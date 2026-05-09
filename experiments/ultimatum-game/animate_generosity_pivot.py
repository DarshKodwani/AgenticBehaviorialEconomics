"""Animated Generosity Pivot — the slope chart, drawing itself.

Lines extend from told_HUMAN -> no_prime (everyone moves), pause, then
extend to told_AI. DeepSeek V3 and GPT-4o curl upward in that final
segment with a glowing trail; the other four stay flat.

Output: output/generosity_pivot.gif
"""
import json
import glob
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


HERE = os.path.dirname(__file__)
RESULTS = os.path.join(HERE, "results", "direct_play")
OUT_DIR = os.path.join(HERE, "output")

CONDITIONS = ["told_human", "no_prime", "told_llm"]
COND_LABEL = {
    "told_human": "told  HUMAN",
    "no_prime": "no  prime",
    "told_llm": "told  AI",
}
MODELS = [
    "DeepSeek V3", "GPT-4o", "Claude 3.5 Haiku",
    "Gemini 2.0 Flash", "Llama 3.1 70B", "Qwen 2.5 72B",
]
HIGHLIGHT = {"DeepSeek V3": "#ffb347", "GPT-4o": "#ff5a8a"}
MUTED = "#6f7891"
BG_TOP, BG_BOT, GRID = "#0d0f1a", "#1a1426", "#2a2e44"
TEXT, TEXT_DIM = "#e6e9f5", "#9aa0b8"

FPS = 20
FRAMES = 160  # 8 sec
P1 = (0, 30)        # frames 0..30: extend told_human -> no_prime
P2 = (30, 50)       # 30..50: hold
P3 = (50, 110)      # 50..110: extend no_prime -> told_llm
P4 = (110, 130)     # 110..130: callouts appear
P5 = (130, FRAMES)  # 130..160: hold for loop


def load_means():
    offers = defaultdict(lambda: defaultdict(list))
    for f in glob.glob(os.path.join(RESULTS, "*.json")):
        d = json.load(open(f))
        for r in d["runs"]:
            if r.get("proposer_parse_ok") and r.get("offer") is not None:
                offers[d["proposer"]][d["condition"]].append(r["offer"])
    means = {}
    for m in MODELS:
        means[m] = [np.mean(offers[m][c]) for c in CONDITIONS]
    return means


def progress_in_segment(frame, seg):
    a, b = seg
    if frame < a: return 0.0
    if frame >= b: return 1.0
    return (frame - a) / (b - a)


def main():
    means = load_means()
    os.makedirs(OUT_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 7), dpi=140)
    fig.patch.set_facecolor(BG_TOP)

    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(grad, extent=(-0.5, 2.5, 15, 65), aspect="auto",
              cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("bg", [BG_BOT, BG_TOP]),
              zorder=0)

    ax.set_xlim(-0.45, 2.45); ax.set_ylim(20, 55)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([COND_LABEL[c] for c in CONDITIONS], color=TEXT, fontsize=13)
    ax.set_ylabel("Mean offer to responder ($ of 100)", color=TEXT, fontsize=12, labelpad=10)
    ax.tick_params(colors=TEXT_DIM, length=0)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=1); ax.set_axisbelow(True)
    ax.set_facecolor("none")
    for x in range(3):
        ax.axvline(x, color=GRID, linewidth=0.5, alpha=0.7, zorder=1)

    # Persistent line + dot + label artists per model
    pivoters = list(HIGHLIGHT.keys())
    flat_models = [m for m in MODELS if m not in pivoters]

    # Stagger flat-line right-side labels.
    ordered = sorted(flat_models, key=lambda m: means[m][2], reverse=True)
    label_y = {}
    min_gap = 1.6
    for i, m in enumerate(ordered):
        y_target = means[m][2]
        if i > 0 and label_y[ordered[i - 1]] - y_target < min_gap:
            y_target = label_y[ordered[i - 1]] - min_gap
        label_y[m] = y_target

    artists = {}
    for m in MODELS:
        c = HIGHLIGHT.get(m, MUTED)
        if m in pivoters:
            glows = []
            for lw, alpha in [(8, 0.18), (5, 0.30), (3, 1.0)]:
                ln, = ax.plot([], [], color=c, linewidth=lw, alpha=alpha,
                              solid_capstyle="round",
                              zorder=5)
                glows.append(ln)
            dots = ax.scatter([], [], color=c, s=110, zorder=6,
                              edgecolor=BG_TOP, linewidth=1.5)
            label = ax.text(2.06, means[m][2], "", color=c, fontsize=12,
                            va="center", weight="bold")
            callout = ax.text(0, 0, "", color=c, fontsize=12, weight="bold",
                              ha="center", va="center", alpha=0)
            artists[m] = {"glows": glows, "dots": dots, "label": label,
                          "callout": callout}
        else:
            ln, = ax.plot([], [], color=c, linewidth=2.0, alpha=0.55, zorder=3)
            dots = ax.scatter([], [], color=c, s=42, alpha=0.65, zorder=3)
            label = ax.text(2.08, label_y[m], "", color=c, fontsize=10,
                            va="center", alpha=0.85)
            artists[m] = {"line": ln, "dots": dots, "label": label}

    fig.text(0.06, 0.94, "The Generosity Pivot", color=TEXT, fontsize=22, weight="bold")
    fig.text(0.06, 0.895, "Same models, same one-shot Ultimatum Game. Tell them who's across the table —",
             color=TEXT_DIM, fontsize=12)
    fig.text(0.06, 0.871, "and watch two of them get $8 more generous to other AIs than to humans.",
             color=TEXT_DIM, fontsize=12)
    fig.text(0.06, 0.04, "n = 30 runs per cell · 6 proposer models × 3 priming conditions · OpenRouter",
             color=TEXT_DIM, fontsize=9)
    fig.text(0.94, 0.04, "Agentic Behavioural Economics · ultimatum-game",
             color=TEXT_DIM, fontsize=9, ha="right")
    plt.subplots_adjust(left=0.08, right=0.84, top=0.80, bottom=0.16)

    def points_for(m, frame):
        """Return xs, ys for the partial line as of this frame."""
        ys = means[m]
        xs_full = [0, 1, 2]

        if frame < P1[0]:  # nothing yet
            return [], []

        # First segment progress
        s1 = progress_in_segment(frame, P1)
        if frame < P2[0]:
            x_end = 0 + s1
            y_end = ys[0] + s1 * (ys[1] - ys[0])
            return [0, x_end], [ys[0], y_end]

        if frame < P3[0]:  # pause at no_prime
            return xs_full[:2], ys[:2]

        # Second segment
        s2 = progress_in_segment(frame, P3)
        x_end = 1 + s2
        y_end = ys[1] + s2 * (ys[2] - ys[1])
        return [0, 1, x_end], [ys[0], ys[1], y_end]

    def update(frame):
        all_artists = []
        for m in MODELS:
            xs, ys = points_for(m, frame)
            a = artists[m]
            if m in pivoters:
                for ln in a["glows"]:
                    ln.set_data(xs, ys)
                    all_artists.append(ln)
                a["dots"].set_offsets(np.column_stack([xs, ys]) if xs else np.empty((0, 2)))
                # label appears once we cross beyond no_prime
                if xs and xs[-1] > 1.5:
                    a["label"].set_text(m)
                    a["label"].set_position((xs[-1] + 0.06, ys[-1]))
                else:
                    a["label"].set_text("")
                # callout fades in during P4
                if frame >= P4[0]:
                    progress = progress_in_segment(frame, P4)
                    delta = means[m][2] - means[m][0]
                    a["callout"].set_text(f"+${delta:.1f}")
                    a["callout"].set_alpha(min(1.0, progress * 1.5))
                    yc = means[m][2] + (3.0 if m == "DeepSeek V3" else -3.0)
                    a["callout"].set_position((1.45, yc))
                else:
                    a["callout"].set_alpha(0)
                all_artists.extend([a["dots"], a["label"], a["callout"]])
            else:
                a["line"].set_data(xs, ys)
                a["dots"].set_offsets(np.column_stack([xs, ys]) if xs else np.empty((0, 2)))
                if xs and xs[-1] > 1.5:
                    a["label"].set_text(m)
                else:
                    a["label"].set_text("")
                all_artists.extend([a["line"], a["dots"], a["label"]])
        return all_artists

    anim = FuncAnimation(fig, update, frames=FRAMES, interval=1000 // FPS, blit=False)
    out = os.path.join(OUT_DIR, "generosity_pivot.gif")
    anim.save(out, writer=PillowWriter(fps=FPS))
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
