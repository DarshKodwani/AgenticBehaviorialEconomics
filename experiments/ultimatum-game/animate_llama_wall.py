"""Llama's Wall — 540 dots fill in, one per offer Llama saw as responder.

Green = accepted, red = rejected. The wall completes; ~188 red dots are
scattered through. Caption confirms the count vs the rest of the slate.

Output: output/llama_wall.gif
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

FPS = 25
DOTS_PER_FRAME = 6
HOLD_FRAMES = 50  # final hold


def load_llama_responses():
    """Return list of (offer, accepted_bool, condition) for every Llama responder round."""
    rows = []
    for f in sorted(glob.glob(os.path.join(RESULTS, "*_vs_Llama_31_70B_*.json"))):
        d = json.load(open(f))
        for r in d["runs"]:
            if r.get("responder_parse_ok") and r.get("decision") in ("ACCEPT", "REJECT"):
                rows.append({
                    "offer": r["offer"],
                    "accepted": r["decision"] == "ACCEPT",
                    "condition": d["condition"],
                    "proposer": d["proposer"],
                })
    return rows


def main():
    rows = load_llama_responses()
    n = len(rows)
    assert n == 540, f"expected 540 Llama responder rounds, got {n}"

    n_rejects = sum(1 for r in rows if not r["accepted"])

    # 30 cols × 18 rows = 540 cells
    n_cols, n_rows = 30, 18
    grid_xy = []
    for i in range(n):
        col = i % n_cols
        row = i // n_cols
        grid_xy.append((col, n_rows - 1 - row))  # top-down fill order

    # Order rounds randomly (deterministic)
    rng = np.random.default_rng(7)
    order = rng.permutation(n)
    rounds = [rows[i] for i in order]
    positions = grid_xy  # filled in this fixed order

    reveal_frames = (n + DOTS_PER_FRAME - 1) // DOTS_PER_FRAME
    total_frames = reveal_frames + HOLD_FRAMES

    os.makedirs(OUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 7), dpi=140)
    fig.patch.set_facecolor(BG_TOP)

    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(grad, extent=(-2, n_cols + 1, -2, n_rows + 2), aspect="auto",
              cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("bg", [BG_BOT, BG_TOP]),
              zorder=0)

    ax.set_xlim(-1, n_cols); ax.set_ylim(-1, n_rows)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_facecolor("none")
    ax.set_aspect("equal")

    # One scatter call we'll update each frame.
    sc_xs, sc_ys, sc_colors = [], [], []
    sc = ax.scatter([], [], s=70, c=[], edgecolor="none", zorder=4)

    fig.text(0.06, 0.94, "Llama's Wall", color=TEXT, fontsize=22, weight="bold")
    fig.text(0.06, 0.895,
             "Every offer Llama 3.1 70B saw as responder, across 540 rounds. Green = accepted, red = rejected.",
             color=TEXT_DIM, fontsize=12)

    counter_text = fig.text(0.06, 0.04, "", color=TEXT_DIM, fontsize=11)
    final_text = fig.text(0.5, 0.045, "", color=TEXT, fontsize=14, weight="bold",
                          ha="center", va="center", alpha=0)
    credit_text = fig.text(0.94, 0.04, "Agentic Behavioural Economics · ultimatum-game",
             color=TEXT_DIM, fontsize=9, ha="right")

    plt.subplots_adjust(left=0.06, right=0.94, top=0.85, bottom=0.13)

    def update(frame):
        nonlocal sc_xs, sc_ys, sc_colors
        target = min(n, (frame + 1) * DOTS_PER_FRAME)
        # Add dots up to target.
        while len(sc_xs) < target:
            i = len(sc_xs)
            x, y = positions[i]
            r = rounds[i]
            sc_xs.append(x); sc_ys.append(y)
            sc_colors.append(GREEN if r["accepted"] else RED)
        sc.set_offsets(np.column_stack([sc_xs, sc_ys]))
        sc.set_color(sc_colors)

        n_done = len(sc_xs)
        n_red_so_far = sum(1 for c in sc_colors if c == RED)
        counter_text.set_text(f"{n_done}/{n} rounds shown · {n_red_so_far} rejections so far")

        # After reveal completes, fade in the final tagline.
        if frame >= reveal_frames:
            progress = min(1.0, (frame - reveal_frames + 1) / 20)
            final_text.set_text(
                f"Llama 3.1 70B rejected {n_rejects} of {n} offers.   "
                f"The other five models combined: 16."
            )
            final_text.set_alpha(progress)
            # Fade out the counter and credit so the final text gets the strip.
            counter_text.set_alpha(max(0.0, 1.0 - progress))
            credit_text.set_alpha(max(0.0, 1.0 - progress))

        return [sc, counter_text, final_text, credit_text]

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000 // FPS, blit=False)
    out = os.path.join(OUT_DIR, "llama_wall.gif")
    anim.save(out, writer=PillowWriter(fps=FPS))
    plt.close(fig)
    print(f"wrote {out}")
    print(f"  {n} dots, {n_rejects} red, {total_frames} frames @ {FPS}fps")


if __name__ == "__main__":
    main()
