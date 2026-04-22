"""
Animated 3x7 grid of line plots — actions per round across all 21 matchups,
all advancing in lock-step.
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TOTAL_ROUNDS = 100

BG     = "#080808"
PANEL  = "#0d0d0d"
GRID   = "#181818"
TEXT   = "#e8e8e8"
MUTED  = "#505050"
COL_A  = "#1ed760"
COL_B  = "#3b9eff"
DEFECT = "#ff2d55"

MODEL_SHORT = {
    "GPT-4o": "GPT-4o", "Claude 3.5 Haiku": "Claude",
    "Gemini 2.0 Flash": "Gemini", "Llama 3.1 70B": "Llama",
    "DeepSeek V3": "DeepSeek", "Qwen 2.5 72B": "Qwen",
}

# ── load ──────────────────────────────────────────────────────────────────────
files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
files = [f for f in files if not f.endswith("summary.json")]

games = []
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    a = [1 if x == "C" else 0 for x in d["actions_a"]]
    b = [1 if x == "C" else 0 for x in d["actions_b"]]
    fd = next((i + 1 for i, (x, y) in enumerate(zip(d["actions_a"], d["actions_b"]))
               if not (x == "C" and y == "C")), 101)
    ma = MODEL_SHORT.get(d["model_a"], d["model_a"])
    mb = MODEL_SHORT.get(d["model_b"], d["model_b"])
    label = f"{ma} × {mb}" if ma != mb else f"{ma} × self"
    games.append({"label": label, "a": a, "b": b, "fd": fd})

games.sort(key=lambda g: -g["fd"])
rounds = np.arange(1, TOTAL_ROUNDS + 1)

# ── grid ──────────────────────────────────────────────────────────────────────
N_COLS, N_ROWS = 3, 7
fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(13, 16), facecolor=BG)

line_objs = []
for ax, g in zip(axes.flat, games):
    ax.set_facecolor(PANEL)
    la, = ax.step([], [], where="post", color=COL_A, linewidth=1.6, alpha=0.95)
    lb, = ax.step([], [], where="post", color=COL_B, linewidth=1.4, alpha=0.85, linestyle="--")
    sa = ax.scatter([], [], color=DEFECT, s=22, zorder=5, edgecolors=BG, linewidths=0.8)
    sb = ax.scatter([], [], color=DEFECT, s=22, zorder=5, edgecolors=BG, linewidths=0.8, marker="D")
    line_objs.append((la, lb, sa, sb, g))

    ax.set_title(g["label"], color=TEXT, fontsize=10, pad=6, loc="left")
    ax.set_xlim(0, TOTAL_ROUNDS + 1)
    ax.set_ylim(-0.4, 1.4)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["D", "C"], color=MUTED, fontsize=8)
    ax.set_xticks([1, 50, 100])
    ax.tick_params(axis="x", colors=MUTED, labelsize=8, length=0)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, linestyle="--")
    ax.spines[:].set_visible(False)

for ax in axes.flat[len(games):]:
    ax.set_visible(False)

# title
fig.text(0.5, 0.978, "Every Matchup, Every Round",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="top")
fig.text(0.5, 0.957,
         "Actions per round across 21 LLM matchups  ·  C = Cooperate, D = Defect",
         color=MUTED, fontsize=10.5, ha="center", va="top")

# round counter
counter_txt = fig.text(0.95, 0.96, "Round 0 / 100",
                        color=MUTED, fontsize=11, ha="right", va="top",
                        fontfamily="monospace")

plt.tight_layout(rect=[0.02, 0.01, 0.98, 0.93])

# ── animation ─────────────────────────────────────────────────────────────────
def update(n):
    artists = [counter_txt]
    counter_txt.set_text(f"Round {n} / 100")
    for la, lb, sa, sb, g in line_objs:
        xa = rounds[:n]
        ya = g["a"][:n]; yb = g["b"][:n]
        la.set_data(xa, ya)
        lb.set_data(xa, yb)
        dxa = [r for r, v in zip(xa, ya) if v == 0]
        dxb = [r for r, v in zip(xa, yb) if v == 0]
        sa.set_offsets(np.c_[dxa, [0]*len(dxa)] if dxa else np.empty((0, 2)))
        sb.set_offsets(np.c_[dxb, [0]*len(dxb)] if dxb else np.empty((0, 2)))
        artists.extend([la, lb, sa, sb])
    return artists

HOLD = 25
FRAMES = list(range(1, TOTAL_ROUNDS + 1)) + [TOTAL_ROUNDS] * HOLD

print(f"Rendering {len(FRAMES)} frames across {len(games)} panels...")
anim = FuncAnimation(fig, update, frames=FRAMES, interval=100, blit=False)

out_path = os.path.join(OUTPUT_DIR, "actions_grid_animated.gif")
writer = PillowWriter(fps=10)
anim.save(out_path, writer=writer, dpi=110, savefig_kwargs={"facecolor": BG})
print(f"Saved → {out_path}")
