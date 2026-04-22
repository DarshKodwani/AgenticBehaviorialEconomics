"""
The Cooperation Clock — 100 rounds as a clock face.
Each ring = one matchup. Green = cooperation, Red = betrayal.
Clockwise from 12 = round 1 → round 100.
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BG      = "#080808"
COOP    = "#1ed760"
DEFECT  = "#ff2d55"
TEXT    = "#e8e8e8"
MUTED   = "#505050"
DIM     = "#303030"
SUBTLE  = "#1a1a1a"

MODEL_SHORT = {
    "GPT-4o": "GPT-4o", "Claude 3.5 Haiku": "Claude",
    "Gemini 2.0 Flash": "Gemini", "Llama 3.1 70B": "Llama",
    "DeepSeek V3": "DeepSeek", "Qwen 2.5 72B": "Qwen",
}

# ── load ──────────────────────────────────────────────────────────────────────
files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
files = [f for f in files if not f.endswith("summary.json")]

matchups = []
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    a, b = d["actions_a"], d["actions_b"]
    fd = next((i + 1 for i, (x, y) in enumerate(zip(a, b)) if not (x == "C" and y == "C")), 101)
    ma = MODEL_SHORT.get(d["model_a"], d["model_a"])
    mb = MODEL_SHORT.get(d["model_b"], d["model_b"])
    label = f"{ma} × {mb}" if ma != mb else f"{ma} × self"
    matchups.append((label, fd))

matchups.sort(key=lambda x: x[1])   # innermost = earliest betrayer

n       = len(matchups)
RING_W  = 0.22
GAP     = 0.045
R0      = 2.6
N_PTS   = 800
STEP    = RING_W + GAP
r_outer = R0 + n * STEP

# ── figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 12))
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0.05, 0.08, 0.9, 0.78], projection="polar")
ax.set_facecolor(BG)
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2)

# ── background disc ───────────────────────────────────────────────────────────
t_full = np.linspace(0, 2 * np.pi, 600)
ax.fill_between(t_full, 0, R0 - 0.05, color="#0d0d0d", linewidth=0, zorder=0)

# ── rings ─────────────────────────────────────────────────────────────────────
for i, (label, fd) in enumerate(matchups):
    r_in  = R0 + i * STEP
    r_out = r_in + RING_W
    frac  = (fd - 1) / 100

    t_g = np.linspace(0, frac * 2 * np.pi, max(6, int(frac * N_PTS)))
    ax.fill_between(t_g, r_in, r_out, color=COOP, alpha=0.82, linewidth=0)

    if fd <= 100:
        t_r = np.linspace(frac * 2 * np.pi, 2 * np.pi, max(6, int((1 - frac) * N_PTS) + 6))
        ax.fill_between(t_r, r_in - 0.05, r_out + 0.05, color=DEFECT, alpha=0.12, linewidth=0)
        ax.fill_between(t_r, r_in, r_out, color=DEFECT, alpha=0.92, linewidth=0)

    ax.plot(t_full, np.full_like(t_full, r_out), color=SUBTLE, linewidth=0.5, zorder=4)

# ── finish-line tick ──────────────────────────────────────────────────────────
ax.plot([0, 0], [R0 - 0.5, r_outer + 0.15], color=DIM, linewidth=1.0, zorder=5)

# ── quarter-round tick marks only (no labels) ─────────────────────────────────
for frac_ref in [0.25, 0.50, 0.75]:
    theta_t = frac_ref * 2 * np.pi
    ax.plot([theta_t, theta_t], [R0 - 0.35, R0 - 0.15], color=MUTED, linewidth=0.8, alpha=0.4)

# ── centre stat (positioned in figure coords at axes centre) ──────────────────
# polar axes centre = (0.5, 0.08 + 0.78/2) = (0.5, 0.47)
CY = 0.47
fig.text(0.5, CY + 0.012, "96",
         color=TEXT, fontsize=58, fontweight="bold",
         ha="center", va="center", zorder=20)
fig.text(0.5, CY - 0.038,
         "rounds of pure cooperation",
         color="#6a6a6a", fontsize=9.5, ha="center", va="center",
         zorder=20, fontstyle="italic")

# ── hide polar chrome ─────────────────────────────────────────────────────────
ax.set_rticks([])
ax.set_xticks([])
ax.spines["polar"].set_visible(False)
ax.grid(False)
ax.set_ylim(0, r_outer + 0.1)

# ── title ─────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.955, "The Cooperation Clock",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="center")
fig.text(
    0.5, 0.918,
    "6 frontier AI models  ·  21 matchups  ·  100 rounds each",
    color=MUTED, fontsize=10.5, ha="center", va="center",
)

# ── legend ────────────────────────────────────────────────────────────────────
for xf, col, lbl in [(0.405, COOP, "Cooperate"), (0.535, DEFECT, "Defect")]:
    fig.text(xf,         0.045, "■", color=col,  fontsize=12, va="center")
    fig.text(xf + 0.018, 0.045, lbl, color=TEXT, fontsize=10, va="center")

out_path = os.path.join(OUTPUT_DIR, "cooperation_clock.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out_path}")
plt.show()
