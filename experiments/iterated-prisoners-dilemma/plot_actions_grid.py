"""
Static grid of 21 small line plots — actions per round for every matchup.
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt

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
    games.append({"label": label, "a": a, "b": b, "fd": fd, "ma": ma, "mb": mb})

# sort by first defection (latest first → least dramatic on top-left)
games.sort(key=lambda g: -g["fd"])

# ── grid ──────────────────────────────────────────────────────────────────────
N_COLS = 3
N_ROWS = 7
fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(13, 16), facecolor=BG)
rounds = np.arange(1, TOTAL_ROUNDS + 1)

for ax, g in zip(axes.flat, games):
    ax.set_facecolor(PANEL)
    ax.step(rounds, g["a"], where="post", color=COL_A, linewidth=1.6, alpha=0.95)
    ax.step(rounds, g["b"], where="post", color=COL_B, linewidth=1.4, alpha=0.85, linestyle="--")

    # red markers on defections
    def_x_a = [r for r, v in zip(rounds, g["a"]) if v == 0]
    def_y_a = [0] * len(def_x_a)
    def_x_b = [r for r, v in zip(rounds, g["b"]) if v == 0]
    def_y_b = [0] * len(def_x_b)
    ax.scatter(def_x_a, def_y_a, color=DEFECT, s=22, zorder=5, edgecolors=BG, linewidths=0.8)
    ax.scatter(def_x_b, def_y_b, color=DEFECT, s=22, zorder=5, edgecolors=BG, linewidths=0.8, marker="D")

    # title
    ax.set_title(g["label"], color=TEXT, fontsize=10, pad=6, loc="left")

    # axes formatting
    ax.set_xlim(0, TOTAL_ROUNDS + 1)
    ax.set_ylim(-0.4, 1.4)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["D", "C"], color=MUTED, fontsize=8)
    ax.set_xticks([1, 50, 100])
    ax.tick_params(axis="x", colors=MUTED, labelsize=8, length=0)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, linestyle="--")
    ax.spines[:].set_visible(False)

# hide any unused axes (we have 21 games and 21 cells, but be safe)
for ax in axes.flat[len(games):]:
    ax.set_visible(False)

# ── title ─────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.978, "Every Matchup, Every Round",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="top")
fig.text(0.5, 0.957,
         "Actions per round across 21 LLM matchups  ·  C = Cooperate, D = Defect",
         color=MUTED, fontsize=10.5, ha="center", va="top")

# ── legend ────────────────────────────────────────────────────────────────────
fig.text(0.30, 0.937, "—", color=COL_A, fontsize=14, va="center")
fig.text(0.32, 0.937, "Model A", color=TEXT, fontsize=10, va="center")
fig.text(0.42, 0.937, "- -", color=COL_B, fontsize=12, va="center")
fig.text(0.45, 0.937, "Model B", color=TEXT, fontsize=10, va="center")
fig.text(0.55, 0.937, "●",  color=DEFECT, fontsize=13, va="center")
fig.text(0.57, 0.937, "Defection", color=TEXT, fontsize=10, va="center")

plt.tight_layout(rect=[0.02, 0.01, 0.98, 0.93])

out_path = os.path.join(OUTPUT_DIR, "actions_grid.png")
plt.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out_path}")
