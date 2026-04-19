"""Generate animated GIF and heatmap for the IPD experiment."""
import os
import sys
import json
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import imageio

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def load_game(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def load_all_games():
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = [f for f in files if "summary" not in f]
    games = []
    for fp in sorted(files):
        games.append(load_game(fp))
    return games


def rolling_coop_rate(actions, window=10):
    """Compute rolling cooperation rate over a window."""
    rates = []
    for i in range(len(actions)):
        start = max(0, i - window + 1)
        chunk = actions[start:i + 1]
        rates.append(chunk.count("C") / len(chunk))
    return np.array(rates)


def cumulative_coop_rate(actions):
    """Cumulative cooperation rate up to each round."""
    rates = []
    coops = 0
    for i, a in enumerate(actions):
        if a == "C":
            coops += 1
        rates.append(coops / (i + 1))
    return np.array(rates)


def find_most_dramatic_game():
    """Find the game with the most interesting cooperation dynamics."""
    games = load_all_games()
    best = None
    best_score = -1

    for game in games:
        if game["model_a"] == game["model_b"]:
            continue
        aa = game["actions_a"]
        ab = game["actions_b"]
        # score = variance in cooperation rate (more dynamic = more interesting)
        coop_a = rolling_coop_rate(aa, 10)
        coop_b = rolling_coop_rate(ab, 10)
        # prefer games where something changes — high variance is interesting
        variance = coop_a.std() + coop_b.std()
        # also prefer games that aren't all-cooperate or all-defect
        overall_rate = (aa.count("C") + ab.count("C")) / (2 * len(aa))
        diversity = 1 - abs(overall_rate - 0.5) * 2  # peaks at 50%, 0 at extremes
        score = variance + diversity * 0.5

        if score > best_score:
            best_score = score
            best = game

    return best


def create_cooperation_gif(game, output_path, fps=20, duration_seconds=12):
    """Create animated GIF showing rolling cooperation rates over time."""
    aa = game["actions_a"]
    ab = game["actions_b"]
    model_a = game["model_a"]
    model_b = game["model_b"]
    num_rounds = len(aa)

    coop_a = rolling_coop_rate(aa, 10)
    coop_b = rolling_coop_rate(ab, 10)

    # also compute mutual outcome per round
    mutual = []
    for a, b in zip(aa, ab):
        if a == "C" and b == "C":
            mutual.append("CC")
        elif a == "D" and b == "D":
            mutual.append("DD")
        else:
            mutual.append("CD")

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # reference lines
    ax.axhline(y=1.0, color="#51cf66", linestyle=":", linewidth=1, alpha=0.3)
    ax.axhline(y=0.0, color="#ff6b6b", linestyle=":", linewidth=1, alpha=0.3)
    ax.axhline(y=0.5, color="#868e96", linestyle=":", linewidth=0.8, alpha=0.3)

    # labels
    ax.text(num_rounds + 1.5, 1.0, "always\ncooperate", fontsize=9, color="#51cf66",
            va="center", fontweight="bold", alpha=0.7)
    ax.text(num_rounds + 1.5, 0.0, "always\ndefect", fontsize=9, color="#ff6b6b",
            va="center", fontweight="bold", alpha=0.7)

    fig.suptitle("do AI agents learn to cooperate?", fontsize=18,
                 fontweight="bold", color="white", x=0.04, ha="left", y=0.98)
    fig.text(0.04, 0.93,
             f"{model_a} vs {model_b} · {num_rounds}-round Prisoner's Dilemma · 10-round rolling window",
             fontsize=10, color="#6c757d", ha="left")

    ax.set_xlabel("round", fontsize=12, color="#adb5bd", labelpad=10)
    ax.set_ylabel("cooperation rate", fontsize=12, color="#adb5bd", labelpad=10)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    ax.set_xlim(0, num_rounds + 12)
    ax.set_ylim(-0.08, 1.12)
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

    # small dots for individual round outcomes — green for CC, red for DD, grey for mixed
    scatter_y = -0.04  # below the main chart area
    outcome_colors = {"CC": "#51cf66", "DD": "#ff6b6b", "CD": "#495057"}

    legend = ax.legend(loc="lower right", fontsize=11, frameon=True,
                       facecolor="#161b22", edgecolor="#30363d", labelcolor="white")
    round_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=13,
                         color="#adb5bd", va="top", fontfamily="monospace")

    # outcome ticker text
    outcome_text = ax.text(0.98, 0.95, "", transform=ax.transAxes, fontsize=11,
                           color="#adb5bd", va="top", ha="right", fontfamily="monospace")

    fig.tight_layout(rect=[0, 0.02, 0.92, 0.90])

    # frame calculation with non-linear pacing
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

        line_a.set_data(x, coop_a[:r + 1])
        line_b.set_data(x, coop_b[:r + 1])

        if len(x) > 0:
            dot_a.set_data([x[-1]], [coop_a[r]])
            dot_b.set_data([x[-1]], [coop_b[r]])

        round_text.set_text(f"round {r + 1}")

        # show current round outcome
        cc = sum(1 for m in mutual[:r+1] if m == "CC")
        dd = sum(1 for m in mutual[:r+1] if m == "DD")
        mixed = r + 1 - cc - dd
        outcome_text.set_text(f"CC:{cc}  DD:{dd}  mixed:{mixed}")

        # draw outcome dots on the bottom edge
        for i in range(r + 1):
            color = outcome_colors[mutual[i]]
            ax.plot(i + 1, scatter_y, "s", color=color, markersize=2, alpha=0.6)

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        image = np.asarray(buf)[:, :, :3].copy()
        frames.append(image)

    plt.close(fig)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    imageio.mimsave(output_path, frames, fps=fps, loop=0)
    print(f"GIF saved to {output_path}")
    print(f"  Frames: {len(frames)}, FPS: {fps}, Duration: {len(frames)/fps:.1f}s")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
    return output_path


def create_grid_gif(output_path, fps=20, duration_seconds=12):
    """Small-multiples grid GIF with all games animating in sync."""
    games = load_all_games()
    if not games:
        print("No results found.")
        return None

    cross = [g for g in games if g["model_a"] != g["model_b"]]
    same = [g for g in games if g["model_a"] == g["model_b"]]
    cross.sort(key=lambda g: (g["model_a"], g["model_b"]))
    same.sort(key=lambda g: g["model_a"])
    games = cross + same

    n_games = len(games)
    n_cols = 5
    n_rows = (n_games + n_cols - 1) // n_cols
    num_rounds = len(games[0]["actions_a"])

    plt.style.use("dark_background")
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 3.2), dpi=100)
    fig.patch.set_facecolor("#0d1117")
    axes_flat = axes.flatten()

    color_a = "#339af0"
    color_b = "#ffd43b"

    lines_a = []
    lines_b = []
    dots_a = []
    dots_b = []

    # precompute rolling coop rates
    all_coop_a = []
    all_coop_b = []

    for idx, ax in enumerate(axes_flat):
        ax.set_facecolor("#0d1117")
        if idx >= n_games:
            ax.set_visible(False)
            lines_a.append(None)
            lines_b.append(None)
            dots_a.append(None)
            dots_b.append(None)
            all_coop_a.append(None)
            all_coop_b.append(None)
            continue

        game = games[idx]
        ma = game["model_a"]
        mb = game["model_b"]
        stats = game.get("stats", {})
        mc = stats.get("mutual_coop_rate", 0)

        coop_a = rolling_coop_rate(game["actions_a"], 10)
        coop_b = rolling_coop_rate(game["actions_b"], 10)
        all_coop_a.append(coop_a)
        all_coop_b.append(coop_b)

        # reference lines
        ax.axhline(y=1.0, color="#51cf66", linestyle=":", linewidth=0.6, alpha=0.3)
        ax.axhline(y=0.0, color="#ff6b6b", linestyle=":", linewidth=0.6, alpha=0.3)

        # title per cell
        if ma == mb:
            label = f"{ma} vs self"
        else:
            short_a = ma.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
            short_b = mb.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
            label = f"{short_a} vs {short_b}"
        ax.set_title(label, fontsize=8, color="#adb5bd", pad=4, loc="left")

        # mutual coop badge
        mc_pct = f"{mc:.0%}"
        mc_color = "#51cf66" if mc >= 0.6 else ("#ffd43b" if mc >= 0.3 else "#ff6b6b")
        ax.text(0.97, 0.92, f"MC={mc_pct}", transform=ax.transAxes, fontsize=7,
                color=mc_color, ha="right", va="top", fontfamily="monospace",
                fontweight="bold")

        ax.set_xlim(0, num_rounds + 2)
        ax.set_ylim(-0.05, 1.08)
        ax.set_yticks([0, 0.5, 1.0])
        ax.tick_params(labelsize=6, colors="#6c757d", length=2)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))

        if idx % n_cols != 0:
            ax.set_yticklabels([])
        is_last_row_for_col = (idx >= (n_rows - 1) * n_cols) or (idx + n_cols >= n_games and idx + n_cols < n_rows * n_cols)
        if not is_last_row_for_col:
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

    fig.suptitle("do AI agents learn to cooperate?",
                 fontsize=20, fontweight="bold", color="white", x=0.02, ha="left", y=0.998)
    fig.text(0.02, 0.973,
             f"{n_games} LLM matchups · {num_rounds}-round Prisoner's Dilemma · 10-round rolling cooperation rate",
             fontsize=10, color="#6c757d", ha="left")

    round_text_global = fig.text(0.98, 0.99, "", fontsize=14, color="#adb5bd",
                                  ha="right", va="top", fontfamily="monospace",
                                  fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.96], h_pad=2.5, w_pad=1.5)

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
            if lines_a[idx] is None:
                continue
            lines_a[idx].set_data(x, all_coop_a[idx][:r + 1])
            lines_b[idx].set_data(x, all_coop_b[idx][:r + 1])
            dots_a[idx].set_data([x[-1]], [all_coop_a[idx][r]])
            dots_b[idx].set_data([x[-1]], [all_coop_b[idx][r]])

        round_text_global.set_text(f"round {r + 1}")

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        image = np.asarray(buf)[:, :, :3].copy()
        frames.append(image)

    plt.close(fig)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    imageio.mimsave(output_path, frames, fps=fps, loop=0)
    print(f"Grid GIF saved to {output_path}")
    print(f"  Frames: {len(frames)}, FPS: {fps}, Duration: {len(frames)/fps:.1f}s")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
    return output_path


def create_heatmap_image(output_path):
    """Create mutual cooperation heatmap."""
    summary_file = os.path.join(RESULTS_DIR, "summary.json")
    if not os.path.exists(summary_file):
        print("No summary.json found yet")
        return None

    with open(summary_file, "r") as f:
        summary = json.load(f)

    models = sorted(set(s["model_a"] for s in summary) | set(s["model_b"] for s in summary))
    n = len(models)
    matrix = np.full((n, n), np.nan)
    model_idx = {m: i for i, m in enumerate(models)}

    for s in summary:
        i = model_idx[s["model_a"]]
        j = model_idx[s["model_b"]]
        mc = s["stats"]["mutual_coop_rate"]
        matrix[i][j] = mc
        matrix[j][i] = mc

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 8), dpi=120)
    fig.patch.set_facecolor("#0d1117")

    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(models, fontsize=10)
    ax.set_title("mutual cooperation rate by model pair", fontsize=16, fontweight="bold", pad=15, loc="left")

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i][j]):
                val = matrix[i][j]
                color = "white" if val < 0.5 else "black"
                ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=10,
                        color=color, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("mutual cooperation rate (0%=always defect, 100%=always cooperate)", fontsize=10, color="#adb5bd")
    cbar.ax.tick_params(colors="#adb5bd")

    fig.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Heatmap saved to {output_path}")


if __name__ == "__main__":
    game = find_most_dramatic_game()
    if game is None:
        print("No results found yet. Run the experiment first.")
        sys.exit(1)

    print(f"Most dramatic game: {game['model_a']} vs {game['model_b']}")
    mc = game.get("stats", {}).get("mutual_coop_rate", "?")
    print(f"  Mutual cooperation rate: {mc}")

    gif_path = os.path.join(OUTPUT_DIR, "cooperation_race.gif")
    create_cooperation_gif(game, gif_path)

    grid_path = os.path.join(OUTPUT_DIR, "cooperation_grid.gif")
    create_grid_gif(grid_path)

    heatmap_path = os.path.join(OUTPUT_DIR, "cooperation_heatmap.png")
    create_heatmap_image(heatmap_path)
