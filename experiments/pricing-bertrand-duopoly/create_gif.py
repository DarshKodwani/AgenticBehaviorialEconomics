"""Generate the viral price-race GIF from experiment results."""
import os
import sys
import json
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FormatStrFormatter

try:
    import imageio
except ImportError:
    imageio = None
    from PIL import Image

from game_engine import MARGINAL_COST, NASH_PRICE, JOINT_PROFIT_PRICE, compute_stats


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def load_game(filepath):
    with open(filepath, "r") as f:
        game = json.load(f)
    game["stats"] = compute_stats(game)
    return game


def find_most_dramatic_game():
    """Find the cross-model game with the most dramatic price trajectory."""
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = list(set(f for f in files if "summary" not in f))

    best = None
    best_score = -1

    for fp in files:
        game = load_game(fp)
        # skip same-model pairs
        if game["model_a"] == game["model_b"]:
            continue
        ci = game.get("stats", {}).get("collusion_index", 0)
        # prefer high collusion AND high variance (dynamic trajectory)
        pa = np.array(game["prices_a"])
        pb = np.array(game["prices_b"])
        price_range = max(pa.max() - pa.min(), pb.max() - pb.min())
        # tiebreaker: standard deviation captures interesting dynamics
        volatility = max(pa.std(), pb.std())
        # score: collusion weighted by how dramatic the price movement is
        score = ci * (1 + price_range) + volatility * 0.1
        if score > best_score:
            best_score = score
            best = game

    return best


def smooth(prices, window=5):
    """Simple moving average for smoother lines."""
    kernel = np.ones(window) / window
    return np.convolve(prices, kernel, mode="same")


def save_gif(output_path, frames, fps):
    """Save GIFs with imageio when available, else fall back to Pillow."""
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


def create_price_race_gif(game, output_path, fps=20, duration_seconds=12):
    """Create the animated price race GIF."""
    prices_a = game["prices_a"]
    prices_b = game["prices_b"]
    model_a = game["model_a"]
    model_b = game["model_b"]
    num_rounds = len(prices_a)

    # use raw prices (LLM outputs are clean enough)
    arr_a = np.array(prices_a, dtype=float)
    arr_b = np.array(prices_b, dtype=float)

    # figure setup — dark theme for visual impact
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # price range
    all_prices = prices_a + prices_b
    y_min = min(min(all_prices), MARGINAL_COST) - 0.15
    y_max = max(max(all_prices), JOINT_PROFIT_PRICE) + 0.25

    # reference lines
    ax.axhline(y=JOINT_PROFIT_PRICE, color="#ff6b6b", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axhline(y=MARGINAL_COST, color="#868e96", linestyle=":", linewidth=1, alpha=0.4)

    # labels for reference lines
    ax.text(num_rounds + 1.5, JOINT_PROFIT_PRICE, "joint-profit\nbenchmark", fontsize=9, color="#ff6b6b",
            va="center", fontweight="bold", alpha=0.9)
    ax.text(num_rounds + 1.5, NASH_PRICE, "Nash\nbenchmark", fontsize=9, color="#51cf66",
            va="center", fontweight="bold", alpha=0.9)

    # title and subtitle — use fig-level text to avoid overlap
    fig.suptitle("do AI pricing agents learn to collude?", fontsize=18,
                 fontweight="bold", color="white", x=0.04, ha="left", y=0.97)
    fig.text(0.04, 0.91, f"{model_a} vs {model_b} · {num_rounds}-round Bertrand duopoly · reference lines show the current model-implied benchmarks",
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

    # model name colours
    color_a = "#339af0"  # blue
    color_b = "#ffd43b"  # yellow

    line_a, = ax.plot([], [], color=color_a, linewidth=2.5, alpha=0.9, label=model_a)
    line_b, = ax.plot([], [], color=color_b, linewidth=2.5, alpha=0.9, label=model_b)

    # scatter for current price dot
    dot_a, = ax.plot([], [], "o", color=color_a, markersize=8, zorder=5)
    dot_b, = ax.plot([], [], "o", color=color_b, markersize=8, zorder=5)

    # legend
    legend = ax.legend(loc="lower right", fontsize=11, frameon=True,
                       facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    # round counter text
    round_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=13,
                         color="#adb5bd", va="top", fontfamily="monospace")

    fig.tight_layout(rect=[0, 0.02, 0.92, 0.85])

    # calculate frames — accelerate through boring early rounds
    total_frames = fps * duration_seconds
    # non-linear pacing: start slow, speed up in middle, slow at end
    t = np.linspace(0, 1, total_frames)
    # ease in-out function
    round_indices = np.floor(num_rounds * (t ** 1.3)).astype(int)
    round_indices = np.clip(round_indices, 0, num_rounds - 1)
    # add 30 frames of hold at the end
    hold_frames = 40
    round_indices = np.concatenate([round_indices, np.full(hold_frames, num_rounds - 1)])

    frames = []

    for frame_idx, r in enumerate(round_indices):
        r = int(r)
        x = list(range(1, r + 2))
        y_a = arr_a[:r + 1]
        y_b = arr_b[:r + 1]

        line_a.set_data(x, y_a)
        line_b.set_data(x, y_b)

        if len(x) > 0:
            dot_a.set_data([x[-1]], [y_a[-1]])
            dot_b.set_data([x[-1]], [y_b[-1]])

        round_text.set_text(f"round {r + 1}")

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        image = np.asarray(buf)[:, :, :3].copy()  # RGBA -> RGB
        frames.append(image)

    plt.close(fig)

    # save gif
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_gif(output_path, frames, fps)
    print(f"GIF saved to {output_path}")
    print(f"  Frames: {len(frames)}, FPS: {fps}, Duration: {len(frames)/fps:.1f}s")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")

    return output_path


def load_all_games():
    """Load all game result files."""
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = list(set(f for f in files if "summary" not in f))
    games = []
    for fp in sorted(files):
        games.append(load_game(fp))
    return games


def create_grid_gif(output_path, fps=20, duration_seconds=12):
    """Create a small-multiples grid GIF with all games animating in sync."""
    games = load_all_games()
    if not games:
        print("No results found.")
        return None

    # sort: cross-model pairs first (alphabetical), then same-model pairs
    cross = [g for g in games if g["model_a"] != g["model_b"]]
    same = [g for g in games if g["model_a"] == g["model_b"]]
    cross.sort(key=lambda g: (g["model_a"], g["model_b"]))
    same.sort(key=lambda g: g["model_a"])
    games = cross + same

    n_games = len(games)
    # grid layout: aim for roughly 4:3 aspect or similar
    n_cols = 5
    n_rows = (n_games + n_cols - 1) // n_cols  # ceiling division
    num_rounds = len(games[0]["prices_a"])

    # figure setup
    plt.style.use("dark_background")
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 3.2), dpi=100)
    fig.patch.set_facecolor("#0d1117")

    # flatten axes for easy indexing
    axes_flat = axes.flatten() if n_games > 1 else [axes]

    # global y range across all games
    y_min = MARGINAL_COST - 0.1
    y_max = 3.15

    color_a = "#339af0"  # blue
    color_b = "#ffd43b"  # yellow

    lines_a = []
    lines_b = []
    dots_a = []
    dots_b = []
    round_texts = []

    for idx, ax in enumerate(axes_flat):
        ax.set_facecolor("#0d1117")
        if idx >= n_games:
            ax.set_visible(False)
            lines_a.append(None)
            lines_b.append(None)
            dots_a.append(None)
            dots_b.append(None)
            round_texts.append(None)
            continue

        game = games[idx]
        ma = game["model_a"]
        mb = game["model_b"]
        ci = game["stats"].get("price_level_index", game["stats"].get("collusion_index", 0))

        # reference lines
        ax.axhline(y=JOINT_PROFIT_PRICE, color="#ff6b6b", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=0.8, alpha=0.5)

        # title per cell
        if ma == mb:
            label = f"{ma} vs self"
        else:
            # shorten model names for space
            short_a = ma.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
            short_b = mb.replace("2.0 ", "").replace("3.5 ", "").replace("2.5 ", "").replace("3.1 ", "")
            label = f"{short_a} vs {short_b}"
        ax.set_title(label, fontsize=8, color="#adb5bd", pad=4, loc="left")

        # PI badge in top right
        pi_color = "#ff6b6b" if ci >= 0.8 else ("#ffd43b" if ci >= 0.5 else "#51cf66")
        ax.text(0.97, 0.92, f"PI={ci:.2f}", transform=ax.transAxes, fontsize=7,
                color=pi_color, ha="right", va="top", fontfamily="monospace",
                fontweight="bold")

        # small in-panel legend so viewers can see which line belongs to which model
        ax.text(0.03, 0.92, f"■ {short_a}", transform=ax.transAxes, fontsize=6.5,
                color=color_a, ha="left", va="top", fontweight="bold")
        ax.text(0.03, 0.82, f"■ {short_b}", transform=ax.transAxes, fontsize=6.5,
                color=color_b, ha="left", va="top", fontweight="bold")

        ax.set_xlim(0, num_rounds + 2)
        ax.set_ylim(y_min, y_max)
        ax.set_yticks([1.0, 1.5, 2.0, 2.5, 3.0])
        ax.tick_params(labelsize=6, colors="#6c757d", length=2)
        ax.yaxis.set_major_formatter(FormatStrFormatter("$%.1f"))

        # determine which cells are in the last row that has content in this column
        is_last_row_for_col = (idx >= (n_rows - 1) * n_cols) or (idx + n_cols >= n_games and idx + n_cols < n_rows * n_cols)
        # show y labels only on leftmost column
        if idx % n_cols != 0:
            ax.set_yticklabels([])
        # show x labels on last existing cell per column
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

    # supertitle
    fig.suptitle("do AI pricing agents learn to collude?",
                 fontsize=20, fontweight="bold", color="white", x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.965,
             f"{n_games} LLM matchups · {num_rounds}-round Bertrand duopoly · no instruction to collude",
             fontsize=10, color="#6c757d", ha="left")

    # round counter in top right
    round_text_global = fig.text(0.98, 0.99, "", fontsize=14, color="#adb5bd",
                                  ha="right", va="top", fontfamily="monospace",
                                  fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.94], h_pad=2.5, w_pad=1.5)

    # precompute arrays
    all_a = [np.array(g["prices_a"], dtype=float) for g in games]
    all_b = [np.array(g["prices_b"], dtype=float) for g in games]

    # frames with non-linear pacing
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
            dots_a[idx].set_data([x[-1]], [y_a[-1]])
            dots_b[idx].set_data([x[-1]], [y_b[-1]])

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


def create_heatmap_image(output_path):
    """Create a static benchmark heatmap for all model pairs."""
    games = load_all_games()
    if not games:
        print("No results found yet")
        return None

    models = sorted(set(g["model_a"] for g in games) | set(g["model_b"] for g in games))
    n = len(models)
    matrix = np.full((n, n), np.nan)
    model_idx = {m: i for i, m in enumerate(models)}

    for game in games:
        i = model_idx[game["model_a"]]
        j = model_idx[game["model_b"]]
        bi = game["stats"].get("price_level_index", game["stats"].get("collusion_index", 0))
        matrix[i][j] = bi
        matrix[j][i] = bi

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 8), dpi=120)
    fig.patch.set_facecolor("#0d1117")

    im = ax.imshow(matrix, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(models, fontsize=10)
    ax.set_title("price-level index by model pair", fontsize=16, fontweight="bold", pad=15, loc="left")

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i][j]):
                val = matrix[i][j]
                color = "white" if val > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9,
                        color=color, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("price-level index (0 = cost floor, 1 = price cap)", fontsize=10, color="#adb5bd")
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
    print(f"  Price-level index: {game['stats'].get('price_level_index', game['stats'].get('collusion_index', 0))}")

    gif_path = os.path.join(OUTPUT_DIR, "price_race.gif")
    create_price_race_gif(game, gif_path)

    grid_path = os.path.join(OUTPUT_DIR, "price_race_grid.gif")
    create_grid_gif(grid_path)

    heatmap_path = os.path.join(OUTPUT_DIR, "collusion_heatmap.png")
    create_heatmap_image(heatmap_path)
