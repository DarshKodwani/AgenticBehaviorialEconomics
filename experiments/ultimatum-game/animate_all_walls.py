"""All Walls — six dot-fill walls in a 3×2 grid, one per responder model.

Each panel = 540 rounds that responder saw, dots fill in synchronously
across all panels. Green = accepted, red = rejected. Five panels stay
nearly entirely green; Llama's panel speckles with red. Per-panel
rejection counter ticks up live; final tagline drops in.

Output: output/all_walls.gif
"""
import json
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


HERE = os.path.dirname(__file__)
RESULTS = os.path.join(HERE, "results", "direct_play")
OUT_DIR = os.path.join(HERE, "output")

BG_TOP, BG_BOT = "#0d0f1a", "#1a1426"
TEXT, TEXT_DIM = "#e6e9f5", "#9aa0b8"
GREEN = "#6ee7a8"
RED = "#ff5a5a"

MODELS = [
    "DeepSeek V3", "GPT-4o", "Claude 3.5 Haiku",
    "Gemini 2.0 Flash", "Llama 3.1 70B", "Qwen 2.5 72B",
]

FPS = 25
DOTS_PER_FRAME = 8       # synchronously across all panels
HOLD_FRAMES = 125         # final hold (5s) so the tagline has time to land


def load_model_responses(model):
    safe = model.replace(" ", "_").replace(".", "")
    rows = []
    for f in sorted(glob.glob(os.path.join(RESULTS, f"*_vs_{safe}_*.json"))):
        d = json.load(open(f))
        for r in d["runs"]:
            if r.get("responder_parse_ok") and r.get("decision") in ("ACCEPT", "REJECT"):
                rows.append(r["decision"] == "ACCEPT")
    return rows


def main():
    # Per-model: list of accept(True)/reject(False) for each round.
    data = {m: load_model_responses(m) for m in MODELS}
    counts = {m: len(data[m]) for m in MODELS}
    rejects = {m: sum(1 for x in data[m] if not x) for m in MODELS}
    n = max(counts.values())  # 540 per model

    # Order rounds randomly per model (deterministic seed shared so reveal
    # pattern is identical across panels for visual parallelism).
    rng = np.random.default_rng(7)
    perm = rng.permutation(n)
    ordered = {m: [data[m][i] for i in perm[: counts[m]]] for m in MODELS}

    # Grid: 30 cols × 18 rows = 540 cells per panel.
    n_cols, n_rows = 30, 18
    grid_xy = []
    for i in range(n):
        col = i % n_cols
        row = i // n_cols
        grid_xy.append((col, n_rows - 1 - row))

    reveal_frames = (n + DOTS_PER_FRAME - 1) // DOTS_PER_FRAME
    total_frames = reveal_frames + HOLD_FRAMES

    os.makedirs(OUT_DIR, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.5), dpi=140)
    fig.patch.set_facecolor(BG_TOP)

    # Background gradient on the figure.
    bg_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    bg_ax.imshow(grad, extent=(0, 1, 0, 1), aspect="auto",
                 cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("bg", [BG_BOT, BG_TOP]))
    bg_ax.set_xticks([]); bg_ax.set_yticks([]); bg_ax.set_axis_off()

    panels = {}
    for idx, m in enumerate(MODELS):
        ax = axes[idx // 3][idx % 3]
        ax.set_xlim(-1, n_cols); ax.set_ylim(-1.5, n_rows + 0.5)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_facecolor("none")
        ax.set_aspect("equal")
        ax.set_zorder(2)

        title = ax.text(n_cols / 2, n_rows + 0.5, m, color=TEXT,
                        fontsize=12, ha="center", va="bottom", weight="bold")
        counter = ax.text(n_cols / 2, -1.2, "", color=TEXT_DIM,
                          fontsize=10, ha="center", va="top")
        sc = ax.scatter([], [], s=22, c=[], edgecolor="none", zorder=4)

        panels[m] = {
            "ax": ax, "sc": sc, "counter": counter,
            "xs": [], "ys": [], "colors": [],
        }

    fig.text(0.5, 0.965, "Six models, 540 offers each.   Green = accepted, red = rejected.",
             color=TEXT, fontsize=15, weight="bold", ha="center")

    final_text = fig.text(0.5, 0.025, "", color=TEXT, fontsize=14,
                          weight="bold", ha="center", va="center", alpha=0)

    plt.subplots_adjust(left=0.04, right=0.96, top=0.92, bottom=0.06,
                        hspace=0.28, wspace=0.18)

    def update(frame):
        target = min(n, (frame + 1) * DOTS_PER_FRAME)
        artists = []
        for m in MODELS:
            p = panels[m]
            while len(p["xs"]) < target:
                i = len(p["xs"])
                x, y = grid_xy[i]
                accepted = ordered[m][i]
                p["xs"].append(x); p["ys"].append(y)
                p["colors"].append(GREEN if accepted else RED)
            p["sc"].set_offsets(np.column_stack([p["xs"], p["ys"]]))
            p["sc"].set_color(p["colors"])
            n_done = len(p["xs"])
            n_red = sum(1 for c in p["colors"] if c == RED)
            p["counter"].set_text(f"{n_red} rejections / {n_done}")
            artists.extend([p["sc"], p["counter"]])

        if frame >= reveal_frames:
            progress = min(1.0, (frame - reveal_frames + 1) / 30)
            llama = rejects["Llama 3.1 70B"]
            others = sum(rejects[m] for m in MODELS if m != "Llama 3.1 70B")
            final_text.set_text(
                f"Llama 3.1 70B: {llama} rejections.   "
                f"The other five models combined: {others}."
            )
            final_text.set_alpha(progress)
            artists.append(final_text)

        return artists

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000 // FPS, blit=False)
    out = os.path.join(OUT_DIR, "all_walls.gif")
    anim.save(out, writer=PillowWriter(fps=FPS))
    plt.close(fig)
    print(f"wrote {out}")
    print(f"  6 panels × {n} dots = {6*n} dots, {total_frames} frames @ {FPS}fps = {total_frames/FPS:.1f}s")
    for m in MODELS:
        print(f"  {m:<22} {rejects[m]:>3} rejections / {counts[m]}")


if __name__ == "__main__":
    main()
