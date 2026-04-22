"""
Animated Cooperation Clock — GIF.
Frame N shows rounds 1..N painted on each ring (green = both cooperate, red = defection).
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.animation import FuncAnimation, PillowWriter

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BG     = "#080808"
COOP   = "#1ed760"
DEFECT = "#ff2d55"
TEXT   = "#e8e8e8"
MUTED  = "#505050"
DIM    = "#303030"
SUBTLE = "#1a1a1a"

MODEL_SHORT = {
    "GPT-4o": "GPT-4o", "Claude 3.5 Haiku": "Claude",
    "Gemini 2.0 Flash": "Gemini", "Llama 3.1 70B": "Llama",
    "DeepSeek V3": "DeepSeek", "Qwen 2.5 72B": "Qwen",
}

# ── load matchups ─────────────────────────────────────────────────────────────
files = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
files = [f for f in files if not f.endswith("summary.json")]

matchups = []  # list of (label, first_def_round, mutual_array_len100)
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    a, b = d["actions_a"], d["actions_b"]
    mutual = [1 if x == "C" and y == "C" else 0 for x, y in zip(a, b)]
    fd = next((i + 1 for i, m in enumerate(mutual) if m == 0), 101)
    ma = MODEL_SHORT.get(d["model_a"], d["model_a"])
    mb = MODEL_SHORT.get(d["model_b"], d["model_b"])
    label = f"{ma} × {mb}" if ma != mb else f"{ma} × self"
    matchups.append((label, fd, mutual))

matchups.sort(key=lambda x: x[1])  # innermost = earliest betrayer

n       = len(matchups)
RING_W  = 0.22
GAP     = 0.045
R0      = 2.6
N_PTS   = 800
STEP    = RING_W + GAP
r_outer = R0 + n * STEP
TOTAL_ROUNDS = 100

# ── figure setup (matches static version) ─────────────────────────────────────
fig = plt.figure(figsize=(11, 12))
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0.05, 0.08, 0.9, 0.78], projection="polar")
ax.set_facecolor(BG)
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2)

t_full = np.linspace(0, 2 * np.pi, 600)
ax.fill_between(t_full, 0, R0 - 0.05, color="#0d0d0d", linewidth=0, zorder=0)

# finish-line tick
ax.plot([0, 0], [R0 - 0.5, r_outer + 0.15], color=DIM, linewidth=1.0, zorder=5)

# quarter-round tick marks
for frac_ref in [0.25, 0.50, 0.75]:
    theta_t = frac_ref * 2 * np.pi
    ax.plot([theta_t, theta_t], [R0 - 0.35, R0 - 0.15], color=MUTED, linewidth=0.8, alpha=0.4)

# precompute ring radii
ring_radii = [(R0 + i * STEP, R0 + i * STEP + RING_W) for i in range(n)]

# ── chrome ────────────────────────────────────────────────────────────────────
ax.set_rticks([])
ax.set_xticks([])
ax.spines["polar"].set_visible(False)
ax.grid(False)
ax.set_ylim(0, r_outer + 0.1)

# title
fig.text(0.5, 0.955, "The Cooperation Clock",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="center")
fig.text(0.5, 0.918,
         "6 frontier AI models  ·  21 matchups  ·  100 rounds each",
         color=MUTED, fontsize=10.5, ha="center", va="center")

# legend
for xf, col, lbl in [(0.405, COOP, "Cooperate"), (0.535, DEFECT, "Defect")]:
    fig.text(xf,         0.045, "■", color=col,  fontsize=12, va="center")
    fig.text(xf + 0.018, 0.045, lbl, color=TEXT, fontsize=10, va="center")

# centre text (round counter — updates each frame)
CY = 0.47
round_text = fig.text(0.5, CY + 0.012, "0",
                       color=TEXT, fontsize=58, fontweight="bold",
                       ha="center", va="center", zorder=20)
fig.text(0.5, CY - 0.038, "round",
         color="#6a6a6a", fontsize=9.5, ha="center", va="center",
         zorder=20, fontstyle="italic")

# ── ring artists: we keep handles to PolyCollections so we can clear + redraw ─
ring_artists = []  # list of artist lists per ring

def draw_frame(round_idx):
    """round_idx = current round (1..100)"""
    # remove previous ring artists
    for artists in ring_artists:
        for a in artists:
            a.remove()
    ring_artists.clear()

    for i, (label, fd, mutual) in enumerate(matchups):
        r_in, r_out = ring_radii[i]
        artists = []

        # paint segments round-by-round up to round_idx
        # group consecutive rounds with the same colour into a single arc to keep things light
        seg_start = 0
        while seg_start < round_idx:
            colour_val = mutual[seg_start]
            seg_end = seg_start
            while seg_end + 1 < round_idx and mutual[seg_end + 1] == colour_val:
                seg_end += 1
            # arc from seg_start (theta = seg_start/100 * 2π) to seg_end+1
            theta0 = (seg_start / TOTAL_ROUNDS) * 2 * np.pi
            theta1 = ((seg_end + 1) / TOTAL_ROUNDS) * 2 * np.pi
            n_pts = max(6, int((theta1 - theta0) / (2 * np.pi) * N_PTS))
            t = np.linspace(theta0, theta1, n_pts)

            if colour_val == 1:
                pc = ax.fill_between(t, r_in, r_out, color=COOP, alpha=0.82, linewidth=0)
                artists.append(pc)
            else:
                # red glow + core
                pc_glow = ax.fill_between(t, r_in - 0.05, r_out + 0.05, color=DEFECT, alpha=0.12, linewidth=0)
                pc_core = ax.fill_between(t, r_in, r_out, color=DEFECT, alpha=0.92, linewidth=0)
                artists.extend([pc_glow, pc_core])

            seg_start = seg_end + 1

        # subtle outline at outer edge of ring (always full)
        outline, = ax.plot(t_full, np.full_like(t_full, r_out), color=SUBTLE, linewidth=0.5, zorder=4)
        artists.append(outline)

        ring_artists.append(artists)

    round_text.set_text(str(round_idx))

# ── animation ─────────────────────────────────────────────────────────────────
# Frames: 100 rounds + 25 hold frames at the end so the final image lingers
HOLD_FRAMES = 25
FRAMES = list(range(1, TOTAL_ROUNDS + 1)) + [TOTAL_ROUNDS] * HOLD_FRAMES

def update(frame_round):
    draw_frame(frame_round)
    return []

print(f"Rendering {len(FRAMES)} frames...")
anim = FuncAnimation(fig, update, frames=FRAMES, interval=80, blit=False)

out_path = os.path.join(OUTPUT_DIR, "cooperation_clock.gif")
writer = PillowWriter(fps=10)
anim.save(out_path, writer=writer, dpi=110, savefig_kwargs={"facecolor": BG})

print(f"Saved → {out_path}")
