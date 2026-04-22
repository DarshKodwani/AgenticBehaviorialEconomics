"""
Animated 3x7 grid of cooperation clocks — each clock fills round-by-round
in lock-step, green for mutual cooperation, red for any defection.
"""
import json, glob, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Wedge

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TOTAL_ROUNDS = 100

BG     = "#080808"
COOP   = "#1ed760"
DEFECT = "#ff2d55"
TEXT   = "#e8e8e8"
MUTED  = "#505050"

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

games.sort(key=lambda g: -g["fd"])

# ── grid (use plain cartesian axes + wedges for cheap, crisp rendering) ───────
N_COLS, N_ROWS = 3, 7
fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(12, 16), facecolor=BG)

R_IN, R_OUT = 0.62, 1.0

cell_state = []  # one entry per game: dict with ax, wedges list, centre_text
for ax, g in zip(axes.flat, games):
    ax.set_facecolor(BG)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.35, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(g["label"], color=TEXT, fontsize=10, pad=4)

    # finish-line tick at 12 o'clock
    ax.plot([0, 0], [R_IN - 0.05, R_OUT + 0.08], color="#2a2a2a", linewidth=0.8, zorder=5)

    centre = ax.text(0, 0, "", color=TEXT, fontsize=11, fontweight="bold",
                     ha="center", va="center")
    sub    = ax.text(0, -0.28, "", color=MUTED, fontsize=7.5,
                     ha="center", va="center")
    cell_state.append({"ax": ax, "wedges": [], "centre": centre, "sub": sub, "g": g})

for ax in axes.flat[len(games):]:
    ax.set_visible(False)

# title
fig.text(0.5, 0.978, "21 Cooperation Clocks",
         color=TEXT, fontsize=22, fontweight="bold", ha="center", va="top")
fig.text(0.5, 0.957,
         "One clock per matchup  ·  Green = mutual cooperation  ·  Red = defection",
         color=MUTED, fontsize=10.5, ha="center", va="top")

counter_txt = fig.text(0.95, 0.96, "Round 0 / 100",
                        color=MUTED, fontsize=11, ha="right", va="top",
                        fontfamily="monospace")

plt.tight_layout(rect=[0.02, 0.01, 0.98, 0.93])

# ── animation ─────────────────────────────────────────────────────────────────
# We add one wedge per round, top of clock = round 1, going clockwise.
def angle_for_round(i):
    # matplotlib wedges: theta in degrees, anti-clockwise from +x axis.
    # We want round 1 to start at 12 o'clock (90°) and proceed clockwise.
    # Wedge spanning rounds [i, i+1) maps to:
    start_deg = 90 - (i + 1) * 360 / TOTAL_ROUNDS
    end_deg   = 90 - i * 360 / TOTAL_ROUNDS
    return start_deg, end_deg

def update(n):
    artists = [counter_txt]
    counter_txt.set_text(f"Round {n} / 100")
    for st in cell_state:
        ax = st["ax"]; g = st["g"]; mutual = g["mutual"]
        existing = len(st["wedges"])
        # add wedges for newly arrived rounds
        for i in range(existing, n):
            v = mutual[i]
            s, e = angle_for_round(i)
            color = COOP if v == 1 else DEFECT
            w = Wedge((0, 0), R_OUT, s, e, width=R_OUT - R_IN,
                      facecolor=color, edgecolor="none",
                      alpha=0.92 if v == 1 else 0.95)
            ax.add_patch(w)
            st["wedges"].append(w)
            artists.append(w)
        # update centre label
        if n == 0:
            st["centre"].set_text("")
            st["sub"].set_text("")
        elif g["fd"] > n:
            st["centre"].set_text("100%")
            st["centre"].set_color(COOP)
            st["sub"].set_text("cooperation")
        else:
            st["centre"].set_text(f"R{g['fd']}")
            st["centre"].set_color(DEFECT)
            st["sub"].set_text("first defect")
        artists.extend([st["centre"], st["sub"]])
    return artists

HOLD = 25
FRAMES = list(range(1, TOTAL_ROUNDS + 1)) + [TOTAL_ROUNDS] * HOLD

print(f"Rendering {len(FRAMES)} frames across {len(games)} clocks...")
anim = FuncAnimation(fig, update, frames=FRAMES, interval=100, blit=False)

out_path = os.path.join(OUTPUT_DIR, "clocks_grid_animated.gif")
writer = PillowWriter(fps=10)
anim.save(out_path, writer=writer, dpi=110, savefig_kwargs={"facecolor": BG})
print(f"Saved → {out_path}")
