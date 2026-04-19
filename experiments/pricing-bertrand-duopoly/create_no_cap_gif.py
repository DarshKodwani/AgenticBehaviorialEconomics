"""Generate no-cap GIFs for the Bertrand pricing experiment."""

import os
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

from run_no_cap_pair import MARGINAL_COST, compute_stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_no_cap")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

BASE_DEMAND = 10.0
OWN_PRICE_EFFECT = 3.0
CROSS_PRICE_EFFECT = 1.5
NASH_PRICE = (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST) / (2 * OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT)
JOINT_PROFIT_PRICE_UNCAPPED = (BASE_DEMAND + (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT) * MARGINAL_COST) / (2 * (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT))


def load_game(filepath):
    with open(filepath, "r") as f:
        game = json.load(f)
    game["stats"] = compute_stats(game)
    return game


def short_name(name):
    return (
        name.replace("Claude 3.5 Haiku", "Claude")
        .replace("Gemini 2.0 Flash", "Gemini")
        .replace("Llama 3.1 70B", "Llama")
        .replace("Qwen 2.5 72B", "Qwen")
        .replace("DeepSeek V3", "DeepSeek")
    )


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


def load_all_games():
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = [f for f in files if "summary" not in os.path.basename(f)]
    return [load_game(fp) for fp in sorted(files)]


def find_most_dramatic_game():
    games = load_all_games()
    best = None
    best_score = -1

    for game in games:
        if game["model_a"] == game["model_b"]:
            continue
        pa = np.array(game["prices_a"], dtype=float)
        pb = np.array(game["prices_b"], dtype=float)
        avg_end = game["stats"].get("avg_price_last20", 0)
        volatility = max(pa.std(), pb.std())
        price_range = max(pa.max() - pa.min(), pb.max() - pb.min())
        overshoot = max(game["stats"].get("max_price_seen", 0) - JOINT_PROFIT_PRICE_UNCAPPED, 0)
        score = avg_end + 0.35 * volatility + 0.25 * price_range + 0.2 * overshoot
        if score > best_score:
            best_score = score
            best = game

    return best


def create_price_race_gif(game, output_path, fps=20, duration_seconds=12):
    prices_a = game["prices_a"]
    prices_b = game["prices_b"]
    model_a = game["model_a"]
    model_b = game["model_b"]
    num_rounds = len(prices_a)

    arr_a = np.array(prices_a, dtype=float)
    arr_b = np.array(prices_b, dtype=float)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    all_prices = prices_a + prices_b
    y_min = MARGINAL_COST - 0.15
    y_max = max(max(all_prices), JOINT_PROFIT_PRICE_UNCAPPED) + 0.4

    ax.axhline(y=JOINT_PROFIT_PRICE_UNCAPPED, color="#ff6b6b", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(y=MARGINAL_COST, color="#868e96", linestyle=":", linewidth=1, alpha=0.4)

    ax.text(num_rounds + 1.5, JOINT_PROFIT_PRICE_UNCAPPED, "uncapped joint-profit\nbenchmark", fontsize=9, color="#ff6b6b",
            va="center", fontweight="bold", alpha=0.9)
    ax.text(num_rounds + 1.5, NASH_PRICE, "Nash\nbenchmark", fontsize=9, color="#51cf66",
            va="center", fontweight="bold", alpha=0.9)

    fig.suptitle("do AI pricing agents push higher without a cap?", fontsize=18,
                 fontweight="bold", color="white", x=0.04, ha="left", y=0.97)
    fig.text(0.04, 0.91, f"{model_a} vs {model_b} · {num_rounds}-round Bertrand duopoly · no hard upper bound on price",
             fontsize=10, color="#6c757d", ha="left")
    ax.set_xlabel("round", fontsize=12, color="#adb5bd", labelpad=10)
    ax.set_ylabel("price ($)", fontsize=12, color="#adb5bd", labelpad=10)
    ax.yaxis.set_major_formatter(FormatStrFormatter("$%.2f"))

    ax.set_xlim(0, num_rounds + 12)
    ax.set_ylim(y_min, y_max)
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#495057")
    ax.spines["bottom"].set_color("#495057")

    color_a = "#339af0"
    color_b = "#ffd43b"

    line_a, = ax.plot([], [], color=color_a, linewidth=2.5, alpha=0.9, label=model_a)
    line_b, = ax.plot([], [], color=color_b, linewidth=2.5, alpha=0.9, label=model_b)
    dot_a, = ax.plot([], [], "o", color=color_a, markersize=8, zorder=5)
    dot_b, = ax.plot([], [], "o", color=color_b, markersize=8, zorder=5)

    ax.legend(loc="lower right", fontsize=11, frameon=True,
              facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    round_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=13,
                         color="#adb5bd", va="top", fontfamily="monospace")

    fig.tight_layout(rect=[0, 0.02, 0.92, 0.85])

    total_frames = fps * duration_seconds
    t = np.linspace(0, 1, total_frames)
    round_indices = np.floor(num_rounds * (t ** 1.3)).astype(int)
    round_indices = np.clip(round_indices, 0, num_rounds - 1)
    round_indices = np.concatenate([round_indices, np.full(40, num_rounds - 1)])

    frames = []
    for r in round_indices:
        r = int(r)
        x = list(range(1, r + 2))
        y_a = arr_a[:r + 1]
        y_b = arr_b[:r + 1]

        line_a.set_data(x, y_a)
        line_b.set_data(x, y_b)
        dot_a.set_data([x[-1]], [y_a[-1]])
        dot_b.set_data([x[-1]], [y_b[-1]])
        round_text.set_text(f"round {r + 1}")

        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())

    plt.close(fig)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_gif(output_path, frames, fps)
    print(f"GIF saved to {output_path}")
    return output_path


def create_grid_gif(output_path, fps=20, duration_seconds=12):
    games = load_all_games()
    if not games:
        print("No no-cap results found.")
        return None

    cross = [g for g in games if g["model_a"] != g["model_b"]]
    same = [g for g in games if g["model_a"] == g["model_b"]]
    cross.sort(key=lambda g: (g["model_a"], g["model_b"]))
    same.sort(key=lambda g: g["model_a"])
    games = cross + same

    n_games = len(games)
    n_cols = 5
    n_rows = (n_games + n_cols - 1) // n_cols
    num_rounds = len(games[0]["prices_a"])

    plt.style.use("dark_background")
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 3.2), dpi=100)
    fig.patch.set_facecolor("#0d1117")
    axes_flat = axes.flatten() if n_games > 1 else [axes]

    global_max = max(max(max(g["prices_a"]), max(g["prices_b"])) for g in games)
    y_min = MARGINAL_COST - 0.1
    y_max = max(global_max, JOINT_PROFIT_PRICE_UNCAPPED) + 0.25

    color_a = "#339af0"
    color_b = "#ffd43b"

    lines_a, lines_b, dots_a, dots_b = [], [], [], []

    for idx, ax in enumerate(axes_flat):
        ax.set_facecolor("#0d1117")
        if idx >= n_games:
            ax.set_visible(False)
            lines_a.append(None)
            lines_b.append(None)
            dots_a.append(None)
            dots_b.append(None)
            continue

        game = games[idx]
        ma = short_name(game["model_a"])
        mb = short_name(game["model_b"])
        avg_price = game["stats"].get("avg_price_last20", 0)

        ax.axhline(y=JOINT_PROFIT_PRICE_UNCAPPED, color="#ff6b6b", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=0.8, alpha=0.5)

        ax.set_title(f"{ma} vs {mb}", fontsize=8, color="#adb5bd", pad=4, loc="left")

        badge_color = "#ff6b6b" if avg_price > JOINT_PROFIT_PRICE_UNCAPPED else ("#ffd43b" if avg_price > NASH_PRICE else "#51cf66")
        ax.text(0.97, 0.92, f"P={avg_price:.2f}", transform=ax.transAxes, fontsize=7,
                color=badge_color, ha="right", va="top", fontfamily="monospace", fontweight="bold")

        # small in-panel legend so viewers can identify the blue and yellow lines
        ax.text(0.03, 0.92, f"■ {ma}", transform=ax.transAxes, fontsize=6.5,
                color=color_a, ha="left", va="top", fontweight="bold")
        ax.text(0.03, 0.82, f"■ {mb}", transform=ax.transAxes, fontsize=6.5,
                color=color_b, ha="left", va="top", fontweight="bold")

        ax.set_xlim(0, num_rounds + 2)
        ax.set_ylim(y_min, y_max)
        ax.tick_params(labelsize=6, colors="#6c757d", length=2)
        ax.yaxis.set_major_formatter(FormatStrFormatter("$%.1f"))

        if idx % n_cols != 0:
            ax.set_yticklabels([])
        if idx < (n_rows - 1) * n_cols:
            ax.set_xticklabels([])

        for spine in ax.spines.values():
            spine.set_color("#30363d")
            spine.set_linewidth(0.5)

        la, = ax.plot([], [], color=color_a, linewidth=1.5, alpha=0.9)
        lb, = ax.plot([], [], color=color_b, linewidth=1.5, alpha=0.9)
        da, = ax.plot([], [], "o", color=color_a, markersize=4, zorder=5)
        db, = ax.plot([], [], "o", color=color_b, markersize=4, zorder=5)
        lines_a.append(la)
        lines_b.append(lb)
        dots_a.append(da)
        dots_b.append(db)

    fig.suptitle("no-cap Bertrand tournament", fontsize=20, fontweight="bold", color="white", x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.965,
             f"{n_games} LLM matchups · {num_rounds} rounds · no hard upper bound on price",
             fontsize=10, color="#6c757d", ha="left")
    round_text_global = fig.text(0.98, 0.99, "", fontsize=14, color="#adb5bd",
                                 ha="right", va="top", fontfamily="monospace", fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.94], h_pad=2.5, w_pad=1.5)

    all_a = [np.array(g["prices_a"], dtype=float) for g in games]
    all_b = [np.array(g["prices_b"], dtype=float) for g in games]

    total_frames = fps * duration_seconds
    t = np.linspace(0, 1, total_frames)
    round_indices = np.floor(num_rounds * (t ** 1.3)).astype(int)
    round_indices = np.clip(round_indices, 0, num_rounds - 1)
    round_indices = np.concatenate([round_indices, np.full(40, num_rounds - 1)])

    frames = []
    for r in round_indices:
        r = int(r)
        x = list(range(1, r + 2))
        for idx in range(n_games):
            y_a = all_a[idx][:r + 1]
            y_b = all_b[idx][:r + 1]
            lines_a[idx].set_data(x, y_a)
            lines_b[idx].set_data(x, y_b)
            dots_a[idx].set_data([x[-1]], [y_a[-1]])
            dots_b[idx].set_data([x[-1]], [y_b[-1]])

        round_text_global.set_text(f"round {r + 1}")
        fig.canvas.draw()
        frames.append(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())

    plt.close(fig)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_gif(output_path, frames, fps)
    print(f"Grid GIF saved to {output_path}")
    return output_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dramatic_game = find_most_dramatic_game()
    if dramatic_game is None:
        print("No no-cap results found.")
        return

    single_out = os.path.join(OUTPUT_DIR, "no_cap_price_race.gif")
    grid_out = os.path.join(OUTPUT_DIR, "no_cap_price_race_grid.gif")

    print(f"Selected highlight matchup: {dramatic_game['model_a']} vs {dramatic_game['model_b']}")
    create_price_race_gif(dramatic_game, single_out)
    create_grid_gif(grid_out)
    print("Done.")


if __name__ == "__main__":
    main()
