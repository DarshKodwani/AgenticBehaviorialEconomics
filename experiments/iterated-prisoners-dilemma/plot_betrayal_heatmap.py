"""
Cooperation heatmap — all matchups × all 100 rounds.
Green = both cooperate, red = at least one defects.
"""
import json
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BG       = "#0a0a0a"
TEXT_COL = "#e0e0e0"
MUTED    = "#555555"
COOP_COL = "#2ecc71"   # emerald green
DEF_COL  = "#e74c3c"   # bright red

# ── load ──────────────────────────────────────────────────────────────────────
files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
files = [f for f in files if not f.endswith("summary.json")]

matrix = []
labels = []
first_defection = []

MODEL_SHORT = {
    "GPT-4o":           "GPT-4o",
    "Claude 3.5 Haiku": "Claude Haiku",
    "Gemini 2.0 Flash": "Gemini Flash",
    "Llama 3.1 70B":    "Llama 70B",
    "DeepSeek V3":      "DeepSeek V3",
    "Qwen 2.5 72B":     "Qwen 72B",
}

for f in files:
    with open(f) as fh:
        data = json.load(fh)
    a = data["actions_a"]
    b = data["actions_b"]
    # 1 = mutual cooperation, 0 = any defection
    row = [1 if x == "C" and y == "C" else 0 for x, y in zip(a, b)]
    matrix.append(row)
    ma = MODEL_SHORT.get(data["model_a"], data["model_a"])
    mb = MODEL_SHORT.get(data["model_b"], data["model_b"])
    label = f"{ma}  ×  {mb}" if ma != mb else f"{ma}  ×  self"
    labels.append(label)
    fd = next((i + 1 for i, v in enumerate(row) if v == 0), None)
    first_defection.append(fd if fd else 101)

# sort by first defection (latest defectors at top)
order = np.argsort(first_defection)[::-1]
matrix  = np.array(matrix)[order]
labels  = [labels[i] for i in order]
first_defection = [first_defection[i] for i in order]

n_games, n_rounds = matrix.shape
rounds = np.arange(1, n_rounds + 1)

# ── colormap: 0 → red, 1 → green ─────────────────────────────────────────────
cmap = mcolors.LinearSegmentedColormap.from_list(
    "coop", [DEF_COL, COOP_COL], N=2
)

# ── figure ────────────────────────────────────────────────────────────────────
fig_h = max(7, 0.46 * n_games + 3)
fig, ax = plt.subplots(figsize=(15, fig_h))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

im = ax.imshow(
    matrix,
    aspect="auto",
    cmap=cmap,
    vmin=0, vmax=1,
    interpolation="nearest",
    extent=[0.5, n_rounds + 0.5, n_games - 0.5, -0.5],
)

# ── y-axis labels ─────────────────────────────────────────────────────────────
ax.set_yticks(range(n_games))
ax.set_yticklabels(labels, color=TEXT_COL, fontsize=9.5, fontfamily="monospace")
ax.tick_params(axis="y", length=0, pad=8)

# ── x-axis ────────────────────────────────────────────────────────────────────
ax.set_xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax.set_xticklabels(
    ["1", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"],
    color=MUTED, fontsize=9,
)
ax.tick_params(axis="x", length=0, pad=6)
ax.set_xlabel("Round", color=MUTED, fontsize=11, labelpad=10)
ax.spines[:].set_visible(False)

# ── "betrayal zone" shaded region ─────────────────────────────────────────────
ax.axvspan(96.5, 100.5, color="#e74c3c", alpha=0.07, zorder=0)
ax.axvline(96.5, color="#e74c3c", linewidth=0.7, alpha=0.35, linestyle="--")
ax.text(97, -1.1, "Betrayal\nzone", color="#e74c3c", fontsize=8,
        ha="center", va="bottom", alpha=0.8)

# ── title block ───────────────────────────────────────────────────────────────
fig.text(
    0.055, 0.995,
    "Betrayal at Round 99",
    color=TEXT_COL, fontsize=21, fontweight="bold", va="top", ha="left",
)
fig.text(
    0.055, 0.955,
    "Every cell = one round between two AI models.  Green = mutual cooperation.  Red = betrayal.\n"
    "6 frontier LLMs cooperated almost perfectly for 96 rounds — then saw the finish line.",
    color=MUTED, fontsize=10.5, va="top", ha="left", linespacing=1.65,
)

# ── legend pills ──────────────────────────────────────────────────────────────
for x_pos, col, lbl in [(0.73, COOP_COL, "Both cooperate"),
                         (0.865, DEF_COL,  "At least one defects")]:
    fig.text(x_pos, 0.967, "■ ", color=col, fontsize=13, va="top", ha="left")
    fig.text(x_pos + 0.018, 0.965, lbl, color=TEXT_COL, fontsize=10, va="top", ha="left")

# ── source tag ────────────────────────────────────────────────────────────────
fig.text(
    0.98, 0.005,
    "GPT-4o · Claude 3.5 Haiku · Gemini 2.0 Flash · Llama 3.1 70B · DeepSeek V3 · Qwen 2.5 72B",
    color="#333333", fontsize=7.5, ha="right", va="bottom",
)

plt.tight_layout(rect=[0, 0.01, 1, 0.91])

out_path = os.path.join(OUTPUT_DIR, "betrayal_heatmap.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out_path}")
plt.show()
