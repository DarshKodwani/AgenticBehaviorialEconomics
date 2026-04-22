"""
The Betrayal Chart — cooperation rate across all matchups, last 20 rounds.
"""
import json
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

WINDOW = 20  # last N rounds to show

# ── colour palette ────────────────────────────────────────────────────────────
BG        = "#0d0d0d"
PANEL_BG  = "#111111"
GRID_COL  = "#1e1e1e"
THIN_COL  = "#c8a96e"        # warm gold for individual lines
AVG_COL   = "#ff4d4d"        # red for average
TEXT_COL  = "#e8e8e8"
MUTED     = "#666666"
ACCENT    = "#c8a96e"

# ── load data ─────────────────────────────────────────────────────────────────
files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
files = [f for f in files if not f.endswith("summary.json")]

all_coop_last20 = []   # shape: (n_games, WINDOW) — 1 = at least one C, 0 = both D
match_labels = []

for f in files:
    with open(f) as fh:
        data = json.load(fh)
    a = data["actions_a"]
    b = data["actions_b"]
    # mutual cooperation rate per round (1 if both cooperate, 0 otherwise)
    mutual = [1 if x == "C" and y == "C" else 0 for x, y in zip(a, b)]
    all_coop_last20.append(mutual[-WINDOW:])
    ma = data["model_a"].replace(" ", "\n")
    mb = data["model_b"].replace(" ", "\n")
    match_labels.append(f"{data['model_a']} vs\n{data['model_b']}")

arr = np.array(all_coop_last20, dtype=float)   # (n_games, WINDOW)
avg = arr.mean(axis=0)
rounds = np.arange(101 - WINDOW, 101)           # round numbers 81–100

# ── figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(PANEL_BG)

# grid
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=GRID_COL, linewidth=0.8, linestyle="--")
ax.xaxis.grid(True, color=GRID_COL, linewidth=0.5, linestyle=":")
ax.spines[:].set_visible(False)

# ── individual matchup lines ──────────────────────────────────────────────────
for i, row in enumerate(arr):
    ax.plot(
        rounds, row,
        color=THIN_COL, alpha=0.18, linewidth=1.1,
        solid_capstyle="round",
    )

# ── average line ──────────────────────────────────────────────────────────────
ax.plot(
    rounds, avg,
    color=AVG_COL, linewidth=3.2,
    solid_capstyle="round", zorder=5,
    path_effects=[
        pe.Stroke(linewidth=5.5, foreground=BG, alpha=0.6),
        pe.Normal(),
    ],
)

# dot at the final round
ax.scatter([100], [avg[-1]], color=AVG_COL, s=80, zorder=6)

# ── annotation: the cliff ─────────────────────────────────────────────────────
cliff_x = rounds[np.argmin(np.diff(avg)) + 1]   # round with steepest drop
ax.annotate(
    "Cooperation collapses\nas the end approaches",
    xy=(cliff_x, avg[np.where(rounds == cliff_x)[0][0]]),
    xytext=(cliff_x - 5.5, 0.35),
    color=TEXT_COL,
    fontsize=10,
    ha="right",
    arrowprops=dict(
        arrowstyle="-|>",
        color=MUTED,
        lw=1.2,
        connectionstyle="arc3,rad=-0.25",
    ),
)

# ── round 100 vertical marker ─────────────────────────────────────────────────
ax.axvline(100, color=MUTED, linewidth=0.8, linestyle="--", alpha=0.6)
ax.text(100.2, 0.04, "Final\nround", color=MUTED, fontsize=8.5, va="bottom")

# ── axes formatting ───────────────────────────────────────────────────────────
ax.set_xlim(rounds[0] - 0.5, 101)
ax.set_ylim(-0.04, 1.08)
ax.set_xticks(range(rounds[0], 101, 2))
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], color=MUTED, fontsize=10)
ax.set_xticklabels(
    [str(r) if r % 5 == 0 else "" for r in range(rounds[0], 101, 2)],
    color=MUTED, fontsize=10,
)
ax.tick_params(axis="both", length=0)
ax.set_xlabel("Round", color=MUTED, fontsize=11, labelpad=10)
ax.set_ylabel("Mutual Cooperation Rate", color=MUTED, fontsize=11, labelpad=12)

# ── legend ────────────────────────────────────────────────────────────────────
legend_elements = [
    Line2D([0], [0], color=THIN_COL, alpha=0.5, linewidth=1.5, label=f"Individual matchup  (n={len(arr)})"),
    Line2D([0], [0], color=AVG_COL,  linewidth=2.5,             label="Average across all matchups"),
]
leg = ax.legend(
    handles=legend_elements,
    loc="lower left",
    frameon=True,
    framealpha=0.15,
    edgecolor=MUTED,
    facecolor=PANEL_BG,
    labelcolor=TEXT_COL,
    fontsize=10,
)

# ── title block ───────────────────────────────────────────────────────────────
fig.text(
    0.055, 0.97,
    "Betrayal at Round 99",
    color=TEXT_COL, fontsize=22, fontweight="bold", va="top", ha="left",
)
fig.text(
    0.055, 0.915,
    "6 frontier LLMs played 100 rounds of the Prisoner's Dilemma against each other.\n"
    "Almost every pair cooperated perfectly — until they could see the end coming.",
    color=MUTED, fontsize=11, va="top", ha="left", linespacing=1.6,
)

# ── subtle source tag ─────────────────────────────────────────────────────────
fig.text(
    0.98, 0.015,
    "Models: GPT-4o · Claude 3.5 Haiku · Gemini 2.0 Flash · Llama 3.1 70B · DeepSeek V3 · Qwen 2.5 72B",
    color="#444444", fontsize=7.5, ha="right", va="bottom",
)

plt.tight_layout(rect=[0, 0.02, 1, 0.88])

out_path = os.path.join(OUTPUT_DIR, "betrayal_chart.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out_path}")
plt.show()
