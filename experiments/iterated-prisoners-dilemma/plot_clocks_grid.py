"""
Static grid of 21 single-ring "cooperation clocks" — one per matchup.
Each cell is a donut: green arc = mutual cooperation, red arc = defection (any).
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TOTAL_ROUNDS = 100

BG     = "#080808"
COOP   = "#1ed760"
DEFECT = "#ff2d55"
TEXT   = "#e8e8e8"
MUTED  = "#505050"
DIM    = "#1a1a1a"

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
    a, b = d["actions_a"], d["actions_b"]
    mutual = [1 if x == "C" and y == "C" else 0 for x, y in zip(a, b)]
    fd = next((i + 1 for i, m in enumerate(mutual) if m == 0), 101)
    ma = MODEL_SHORT.get(d["model_a"], d["model_a"])
    mb = MODEL_SHORT.get(d["model_b"], d["model_b"])
    label = f"{ma} × {mb}" if ma != mb else f"{ma} × self"
    games.append({"label": label, "mutual": mutual, "fd": fd})

# sort by first defection (latest = cleanest, top-left)
games.sort(key=lambda g: -g["fd"])

# ── grid ──────────────────────────────────────────────────────────────────────
N_COLS = 3
N_ROWS = 7
fig = plt.figure(figsize=(12, 16), facecolor=BG)

R_IN  = 0.65
R_OUT = 1.0
N_PTS = 600

for i, g in enumerate(games):
    ax = fig.add_subplot(N_ROWS, N_COLS, i + 1, projection="polar")
    ax.set_facecolor(BG)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    ax.set_rticks([])
    ax.set_xticks([])
    ax.spines["polar"].set_visible(False)
    ax.grid(False)
    ax.set_ylim(0, R_OUT + 0.18)

    mutual = g["mutual"]
    # paint round-by-round, grouping consecutive same-colour segments
    seg_start = 0
    while seg_start < TOTAL_ROUNDS:
        v = mutual[seg_start]
        seg_end = seg_start
        while seg_end + 1 < TOTAL_ROUNDS and mutual[seg_end + 1] == v:
            seg_end += 1
        theta0 = (seg_start / TOTAL_ROUNDS) * 2 * np.pi
        theta1 = ((seg_end + 1) / TOTAL_ROUNDS) * 2 * np.pi
        n_pts = max(6, int((theta1 - theta0) / (2 * np.pi) * N_PTS))
        t = np.linspace(theta0, theta1, n_pts)
        if v == 1:
            ax.fill_between(t, R_IN, R_OUT, color=COOP, alpha=0.85, linewidth=0)
        else:
            ax.fill_between(t, R_IN - 0.04, R_OUT + 0.04, color=DEFECT, alpha=0.18, linewidth=0)
            ax.fill_between(t, R_IN, R_OUT, color=DEFECT, alpha=0.95, linewidth=0)
        seg_start = seg_end + 1

    # finish-line tick at 12 o'clock
    ax.plot([0, 0], [R_IN - 0.05, R_OUT + 0.08], color="#2a2a2a", linewidth=0.8, zorder=5)

    # title
    ax.set_title(g["label"], color=TEXT, fontsize=10, pad=8)

    # centre annotation: when did first defection happen?
    if g["fd"] > TOTAL_ROUNDS:
        centre_lbl = "100%"
        sub_lbl    = "cooperation"
        col        = COOP
    else:
        centre_lbl = f"R{g['fd']}"
        sub_lbl    = "first defect"
        col        = DEFECT
    ax.text(0, 0, centre_lbl, color=col, fontsize=11, fontweight="bold",
            ha="center", va="center", transform=ax.transData)
    ax.text(0, -0.3, sub_lbl, color=MUTED, fontsize=7.5,
            ha="center", va="center", transform=ax.transData)

# ── title ─────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.978, "21 Cooperation Clocks",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="top")
fig.text(0.5, 0.957,
         "One clock per matchup  ·  Green = mutual cooperation  ·  Red = defection",
         color=MUTED, fontsize=10.5, ha="center", va="top")

plt.tight_layout(rect=[0.02, 0.01, 0.98, 0.93])

out_path = os.path.join(OUTPUT_DIR, "clocks_grid.png")
plt.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out_path}")
