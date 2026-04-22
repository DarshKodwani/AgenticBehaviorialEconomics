"""
Animated single-matchup line plot — actions per round (1 = Cooperate, 0 = Defect).
Default matchup: GPT-4o vs DeepSeek V3 (defections start at round 97).
"""
import json, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MATCHUP_FILE = "GPT-4o_vs_DeepSeek_V3.json"
TOTAL_ROUNDS = 100

# ── palette ───────────────────────────────────────────────────────────────────
BG     = "#080808"
PANEL  = "#0d0d0d"
GRID   = "#1a1a1a"
TEXT   = "#e8e8e8"
MUTED  = "#505050"
COL_A  = "#1ed760"   # green for player A
COL_B  = "#3b9eff"   # blue for player B (we keep red for defect events)
DEFECT = "#ff2d55"

# ── load ──────────────────────────────────────────────────────────────────────
with open(os.path.join(RESULTS_DIR, MATCHUP_FILE)) as f:
    data = json.load(f)

ma = data["model_a"]
mb = data["model_b"]
actions_a = [1 if x == "C" else 0 for x in data["actions_a"]]
actions_b = [1 if x == "C" else 0 for x in data["actions_b"]]
rounds = np.arange(1, TOTAL_ROUNDS + 1)

# ── figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(PANEL)

# grid
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=GRID, linewidth=0.7, linestyle="--")
ax.spines[:].set_visible(False)

# axes
ax.set_xlim(0, TOTAL_ROUNDS + 1)
ax.set_ylim(-0.25, 1.25)
ax.set_yticks([0, 1])
ax.set_yticklabels(["Defect", "Cooperate"], color=TEXT, fontsize=10.5)
ax.set_xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax.tick_params(axis="x", colors=MUTED, labelsize=9, length=0, pad=6)
ax.tick_params(axis="y", length=0, pad=8)
ax.set_xlabel("Round", color=MUTED, fontsize=11, labelpad=10)

# placeholder line objects (start empty, update each frame)
line_a, = ax.step([], [], where="post", color=COL_A, linewidth=2.4, label=ma, solid_capstyle="round")
line_b, = ax.step([], [], where="post", color=COL_B, linewidth=2.4, label=mb,
                  alpha=0.85, linestyle="--", solid_capstyle="round")

# defection markers (red dots) — accumulated across frames
def_scatter_a = ax.scatter([], [], color=DEFECT, s=90, zorder=5, edgecolors=BG, linewidths=1.5)
def_scatter_b = ax.scatter([], [], color=DEFECT, s=90, zorder=5, edgecolors=BG, linewidths=1.5, marker="D")

# ── title block ───────────────────────────────────────────────────────────────
fig.text(0.06, 0.955, f"{ma}  vs  {mb}",
         color=TEXT, fontsize=20, fontweight="bold", va="top")
fig.text(0.06, 0.915, "Actions over 100 rounds of the Prisoner's Dilemma",
         color=MUTED, fontsize=11, va="top")

# legend
leg = ax.legend(loc="lower left", frameon=True, framealpha=0.2,
                edgecolor=MUTED, facecolor=PANEL, labelcolor=TEXT, fontsize=10)

# round counter (top-right)
counter_txt = fig.text(0.94, 0.94, "Round 0 / 100",
                        color=MUTED, fontsize=11, ha="right", va="top",
                        fontfamily="monospace")

plt.tight_layout(rect=[0.04, 0.04, 0.98, 0.88])

# ── animation ─────────────────────────────────────────────────────────────────
def update(frame):
    n = frame  # frame == current round (1..100)
    xa = rounds[:n]
    ya = actions_a[:n]
    yb = actions_b[:n]
    line_a.set_data(xa, ya)
    line_b.set_data(xa, yb)

    # defection markers
    def_x_a = [r for r, v in zip(xa, ya) if v == 0]
    def_y_a = [v for v in ya if v == 0]
    def_x_b = [r for r, v in zip(xa, yb) if v == 0]
    def_y_b = [v for v in yb if v == 0]
    def_scatter_a.set_offsets(np.c_[def_x_a, def_y_a] if def_x_a else np.empty((0, 2)))
    def_scatter_b.set_offsets(np.c_[def_x_b, def_y_b] if def_x_b else np.empty((0, 2)))

    counter_txt.set_text(f"Round {n} / 100")
    return line_a, line_b, def_scatter_a, def_scatter_b, counter_txt

HOLD = 25
FRAMES = list(range(1, TOTAL_ROUNDS + 1)) + [TOTAL_ROUNDS] * HOLD

print(f"Rendering {len(FRAMES)} frames...")
anim = FuncAnimation(fig, update, frames=FRAMES, interval=100, blit=False)

out_path = os.path.join(OUTPUT_DIR, "actions_line_animated.gif")
writer = PillowWriter(fps=10)
anim.save(out_path, writer=writer, dpi=110, savefig_kwargs={"facecolor": BG})

print(f"Saved → {out_path}")
