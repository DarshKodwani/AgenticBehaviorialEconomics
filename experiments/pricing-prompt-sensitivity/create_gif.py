"""Generate v2 prompt-sensitivity visuals."""
import os
import sys
import json
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

try:
    import imageio
except ImportError:
    imageio = None
    from PIL import Image

from game_engine import MARGINAL_COST, NASH_PRICE, JOINT_PROFIT_PRICE, FIXED_BOT_PRICE, compute_stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# also pull v1 cooperative baselines
V1_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "experiment", "results")

# conditions in display order
CONDITION_ORDER = ["cooperative", "myopic", "competitive", "blind", "nash_bot"]
CONDITION_LABELS = {
    "cooperative": "Cooperative\n(v1 baseline)",
    "myopic": "Myopic\n(no history)",
    "competitive": "Competitive\n(beat opponent)",
    "blind": "Blind\n(no competitor info)",
    "nash_bot": f"vs Fixed Bot\n(${FIXED_BOT_PRICE:.2f} always)",
}

# the 3 pairs we test
PAIR_LABELS = {
    ("GPT-4o", "DeepSeek V3"): "GPT-4o vs DeepSeek",
    ("GPT-4o", "Llama 3.1 70B"): "GPT-4o vs Llama 70B",
    ("Gemini 2.0 Flash", "Qwen 2.5 72B"): "Gemini Flash vs Qwen 72B",
}

PAIR_COLORS = {
    ("GPT-4o", "DeepSeek V3"): "#339af0",
    ("GPT-4o", "Llama 3.1 70B"): "#ffd43b",
    ("Gemini 2.0 Flash", "Qwen 2.5 72B"): "#ff6b6b",
}

# which model from each pair plays the fixed-price bot game
PAIR_NASH_MODEL = {
    ("GPT-4o", "DeepSeek V3"): "GPT-4o",
    ("GPT-4o", "Llama 3.1 70B"): "Llama 3.1 70B",
    ("Gemini 2.0 Flash", "Qwen 2.5 72B"): "Gemini 2.0 Flash",
}


def load_game(filepath):
    with open(filepath, "r") as f:
        game = json.load(f)
    game["stats"] = compute_stats(game)
    return game


def safe_filename(name):
    return name.replace(" ", "_").replace(".", "")


def save_gif(output_path, frames, fps):
    if imageio is not None:
        imageio.mimsave(output_path, frames, fps=fps, loop=0)
        return

    pil_frames = [Image.fromarray(frame) for frame in frames]
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=int(1000 / fps),
        loop=0,
    )


def get_v1_cooperative_ci(model_a, model_b):
    """Pull the cooperative CI from the v1 experiment results."""
    # try both orderings
    for ma, mb in [(model_a, model_b), (model_b, model_a)]:
        patterns = [
            os.path.join(V1_RESULTS_DIR, f"{safe_filename(ma)}_vs_{safe_filename(mb)}*.json"),
        ]
        for pat in patterns:
            for fp in glob.glob(pat):
                if "summary" not in fp:
                    game = load_game(fp)
                    stats = compute_stats(game)
                    return stats.get("price_level_index", stats.get("collusion_index", None))
    return None


def collect_results():
    """Collect all v2 results + v1 cooperative baselines into a structured dict."""
    data = {}  # {(pair): {condition: ci}}

    # v2 results
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = [f for f in files if "summary" not in f]

    for fp in files:
        game = load_game(fp)
        ma = game["model_a"]
        mb = game["model_b"]
        cond = game.get("condition", "unknown")
        ci = game.get("stats", {}).get("price_level_index", game.get("stats", {}).get("collusion_index", None))
        if ci is None:
            continue

        # for nash_bot, pair key uses the LLM model
        if cond == "nash_bot":
            pair = (ma, "Fixed Price Bot")
        else:
            pair = (ma, mb)

        if pair not in data:
            data[pair] = {}
        data[pair][cond] = ci

    # pull v1 cooperative baselines for the 3 pairs
    for pair in PAIR_LABELS:
        if pair not in data:
            data[pair] = {}
        if "cooperative" not in data[pair]:
            ci = get_v1_cooperative_ci(pair[0], pair[1])
            if ci is not None:
                data[pair]["cooperative"] = ci

    return data


def create_grouped_bar_chart(output_path):
    """Key visual: grouped bar chart of CI across conditions."""
    data = collect_results()

    pairs = list(PAIR_LABELS.keys())
    conditions = CONDITION_ORDER

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(14, 7), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    n_conditions = len(conditions)
    n_pairs = len(pairs)
    bar_width = 0.22
    group_width = n_pairs * bar_width + 0.15

    for i, pair in enumerate(pairs):
        xs = []
        ys = []
        for j, cond in enumerate(conditions):
            x = j * group_width + i * bar_width

            # for nash_bot, use the designated model from PAIR_NASH_MODEL
            if cond == "nash_bot":
                nash_model = PAIR_NASH_MODEL.get(pair)
                bot_pair = (nash_model, "Fixed Price Bot") if nash_model else None
                ci = data.get(bot_pair, {}).get("nash_bot", None) if bot_pair else None
            else:
                ci = data.get(pair, {}).get(cond, None)

            if ci is not None:
                xs.append(x)
                ys.append(ci)

        label = PAIR_LABELS[pair]
        color = PAIR_COLORS[pair]
        bars = ax.bar(xs, ys, width=bar_width, color=color, alpha=0.85,
                      label=label, edgecolor="white", linewidth=0.3)

        # annotate bars
        for bx, by in zip(xs, ys):
            ax.text(bx, by + 0.02, f"{by:.2f}", ha="center", va="bottom",
                    fontsize=8, color=color, fontweight="bold")

    # x-axis: condition labels at group centres
    group_centres = [j * group_width + (n_pairs - 1) * bar_width / 2 for j in range(n_conditions)]
    ax.set_xticks(group_centres)
    ax.set_xticklabels([CONDITION_LABELS[c] for c in conditions], fontsize=10, color="#adb5bd")

    # reference lines
    ax.axhline(y=1.0, color="#ff6b6b", linestyle="--", linewidth=1, alpha=0.5)
    ax.axhline(y=0.0, color="#51cf66", linestyle="--", linewidth=1, alpha=0.5)
    ax.text(-0.3, 1.0, "joint-profit cap", fontsize=8, color="#ff6b6b", va="center", alpha=0.7)
    ax.text(-0.3, 0.0, "Nash benchmark", fontsize=8, color="#51cf66", va="center", alpha=0.7)

    ax.set_ylim(-0.15, 1.25)
    ax.set_ylabel("price-level index", fontsize=12, color="#adb5bd", labelpad=10)

    fig.suptitle("how sensitive is AI collusion to prompt design?",
                 fontsize=18, fontweight="bold", color="white", x=0.04, ha="left", y=0.98)
    fig.text(0.04, 0.93,
             "same Bertrand duopoly, 80 rounds · only the prompt framing changes",
             fontsize=10, color="#6c757d", ha="left")

    ax.legend(loc="upper right", fontsize=10, frameon=True,
              facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#495057")
    ax.spines["bottom"].set_color("#495057")

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Grouped bar chart saved to {output_path}")


def create_condition_grid_gif(output_path, fps=20, duration_seconds=12):
    """Grid GIF: 12 v2 games (4 conditions × 3 pairs) animated in sync."""
    data_files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    data_files = [f for f in data_files if "summary" not in f]

    games = []
    for fp in sorted(data_files):
        games.append(load_game(fp))

    if not games:
        print("No v2 results found.")
        return None

    n_games = len(games)
    n_cols = min(4, n_games)
    n_rows = (n_games + n_cols - 1) // n_cols
    num_rounds = len(games[0]["prices_a"])

    plt.style.use("dark_background")
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4.5, n_rows * 3.2), dpi=100)
    fig.patch.set_facecolor("#0d1117")

    if n_rows == 1 and n_cols == 1:
        axes_flat = [axes]
    elif n_rows == 1 or n_cols == 1:
        axes_flat = list(axes.flatten())
    else:
        axes_flat = list(axes.flatten())

    y_min = MARGINAL_COST - 0.1
    y_max = 3.15

    color_a = "#339af0"
    color_b = "#ffd43b"

    lines_a = []
    lines_b = []

    for idx, ax in enumerate(axes_flat):
        ax.set_facecolor("#0d1117")
        if idx >= n_games:
            ax.set_visible(False)
            lines_a.append(None)
            lines_b.append(None)
            continue

        game = games[idx]
        ma = game["model_a"]
        mb = game["model_b"]
        cond = game.get("condition", "?")
        ci = game.get("stats", {}).get("price_level_index", game.get("stats", {}).get("collusion_index", 0))

        ax.axhline(y=JOINT_PROFIT_PRICE, color="#ff6b6b", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=0.8, alpha=0.5)

        short_a = ma.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
        short_b = mb.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
        ax.set_title(f"[{cond}] {short_a} vs {short_b}", fontsize=8, color="#adb5bd", pad=4, loc="left")

        ci_color = "#ff6b6b" if ci >= 0.8 else ("#ffd43b" if ci >= 0.5 else "#51cf66")
        ax.text(0.97, 0.92, f"PI={ci:.2f}", transform=ax.transAxes, fontsize=7,
                color=ci_color, ha="right", va="top", fontfamily="monospace",
                fontweight="bold")

        ax.set_xlim(0, num_rounds + 2)
        ax.set_ylim(y_min, y_max)
        ax.set_yticks([1.0, 1.5, 2.0, 2.5, 3.0])
        ax.tick_params(labelsize=6, colors="#6c757d", length=2)
        ax.yaxis.set_major_formatter(FormatStrFormatter("$%.1f"))

        if idx % n_cols != 0:
            ax.set_yticklabels([])

        for spine in ax.spines.values():
            spine.set_color("#30363d")
            spine.set_linewidth(0.5)

        la, = ax.plot([], [], color=color_a, linewidth=1.5, alpha=0.9)
        lb, = ax.plot([], [], color=color_b, linewidth=1.5, alpha=0.9)
        lines_a.append(la)
        lines_b.append(lb)

    fig.suptitle("prompt sensitivity: same game, different framing",
                 fontsize=16, fontweight="bold", color="white", x=0.02, ha="left", y=0.998)

    round_text_global = fig.text(0.98, 0.99, "", fontsize=14, color="#adb5bd",
                                  ha="right", va="top", fontfamily="monospace",
                                  fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.96], h_pad=2.5, w_pad=1.5)

    all_a = [np.array(g["prices_a"], dtype=float) for g in games]
    all_b = [np.array(g["prices_b"], dtype=float) for g in games]

    total_frames = fps * duration_seconds
    t = np.linspace(0, 1, total_frames)
    round_indices = np.floor(num_rounds * (t ** 1.3)).astype(int)
    round_indices = np.clip(round_indices, 0, num_rounds - 1)
    hold_frames = 40
    round_indices = np.concatenate([round_indices, np.full(hold_frames, num_rounds - 1)])

    frames = []

    for r in round_indices:
        r = int(r)
        x = list(range(1, r + 2))

        for idx in range(n_games):
            y_a = all_a[idx][:r + 1]
            y_b = all_b[idx][:r + 1]
            lines_a[idx].set_data(x, y_a)
            lines_b[idx].set_data(x, y_b)

        round_text_global.set_text(f"round {r + 1}")

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        image = np.asarray(buf)[:, :, :3].copy()
        frames.append(image)

    plt.close(fig)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_gif(output_path, frames, fps)
    print(f"Grid GIF saved to {output_path}")
    print(f"  Frames: {len(frames)}, FPS: {fps}, Duration: {len(frames)/fps:.1f}s")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
    return output_path


if __name__ == "__main__":
    print("=== Grouped bar chart ===")
    bar_path = os.path.join(OUTPUT_DIR, "prompt_sensitivity_bars.png")
    create_grouped_bar_chart(bar_path)

    print("\n=== Condition grid GIF ===")
    grid_path = os.path.join(OUTPUT_DIR, "condition_grid.gif")
    create_condition_grid_gif(grid_path)
