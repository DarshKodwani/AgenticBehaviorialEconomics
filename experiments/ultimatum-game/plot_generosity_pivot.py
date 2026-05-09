"""The Generosity Pivot: slope chart of mean offer × prime, by proposer model.

X-axis: three priming conditions (told_human → no_prime → told_llm).
Y-axis: mean offer to the responder, $0–100.
One line per proposer model. Two of them — DeepSeek V3 and GPT-4o — leap
upward at told_llm by ~$8. The other four run flat. The geometry is the
finding.

Output: output/generosity_pivot.png and .svg (dark, blog-ready).
"""
import json
import glob
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe


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
    "DeepSeek V3",
    "GPT-4o",
    "Claude 3.5 Haiku",
    "Gemini 2.0 Flash",
    "Llama 3.1 70B",
    "Qwen 2.5 72B",
]

# Two highlight colours for the pivoters; muted greys for the flat models.
HIGHLIGHT = {
    "DeepSeek V3": "#ffb347",
    "GPT-4o": "#ff5a8a",
}
MUTED = "#6f7891"

BG_TOP = "#0d0f1a"
BG_BOT = "#1a1426"
GRID = "#2a2e44"
TEXT = "#e6e9f5"
TEXT_DIM = "#9aa0b8"


def load_offers():
    offers = defaultdict(lambda: defaultdict(list))
    for f in glob.glob(os.path.join(RESULTS, "*.json")):
        d = json.load(open(f))
        for r in d["runs"]:
            offers[d["proposer"]][d["condition"]].append(r["offer"])
    return offers


def mean_ci(values, conf=0.95):
    a = np.asarray(values, dtype=float)
    m = a.mean()
    se = a.std(ddof=1) / np.sqrt(len(a)) if len(a) > 1 else 0.0
    return m, 1.96 * se


def main():
    offers = load_offers()
    os.makedirs(OUT_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 7), dpi=180)
    fig.patch.set_facecolor(BG_TOP)

    # Vertical gradient background.
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(
        grad,
        extent=(-0.5, 2.5, 15, 65),
        aspect="auto",
        cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("bg", [BG_BOT, BG_TOP]),
        zorder=0,
    )

    # Axes formatting.
    ax.set_xlim(-0.45, 2.45)
    ax.set_ylim(20, 55)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([COND_LABEL[c] for c in CONDITIONS], color=TEXT, fontsize=13)
    ax.set_ylabel("Mean offer to responder ($ of 100)", color=TEXT, fontsize=12, labelpad=10)
    ax.tick_params(colors=TEXT_DIM, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=1)
    ax.set_axisbelow(True)
    ax.set_facecolor("none")

    # Compute means + CIs per (model, condition).
    means = {m: [mean_ci(offers[m][c])[0] for c in CONDITIONS] for m in MODELS}
    cis = {m: [mean_ci(offers[m][c])[1] for c in CONDITIONS] for m in MODELS}

    # Plot non-pivoters first (muted, behind).
    pivoters = list(HIGHLIGHT.keys())
    flat_models = [m for m in MODELS if m not in pivoters]

    # Stagger y positions for the right-side labels of flat models so they
    # don't collide. Sort by their told_llm y-value, then space them out.
    ordered = sorted(flat_models, key=lambda m: means[m][2], reverse=True)
    label_y = {}
    min_gap = 1.6
    for i, m in enumerate(ordered):
        y_target = means[m][2]
        if i > 0:
            prev = label_y[ordered[i - 1]]
            if prev - y_target < min_gap:
                y_target = prev - min_gap
        label_y[m] = y_target

    for m in flat_models:
        y = means[m]
        ax.plot(range(3), y, color=MUTED, linewidth=2.0, alpha=0.55, zorder=3)
        ax.scatter(range(3), y, color=MUTED, s=42, alpha=0.65, zorder=3)
        # leader line if label was nudged
        if abs(label_y[m] - y[2]) > 0.05:
            ax.plot([2.0, 2.04, 2.06], [y[2], y[2], label_y[m]],
                    color=MUTED, linewidth=0.6, alpha=0.5, zorder=2)
        ax.text(2.08, label_y[m], m, color=MUTED, fontsize=10, va="center", alpha=0.85)

    # Plot pivoters on top with glow.
    for m in pivoters:
        c = HIGHLIGHT[m]
        y = means[m]
        for lw, alpha in [(8, 0.18), (5, 0.30), (3, 1.0)]:
            ax.plot(range(3), y, color=c, linewidth=lw, alpha=alpha, zorder=5,
                    solid_capstyle="round")
        ax.scatter(range(3), y, color=c, s=110, zorder=6, edgecolor=BG_TOP, linewidth=1.5)
        ax.text(2.06, y[2], m, color=c, fontsize=12, va="center", weight="bold")
        # Magnitude callout.
        delta = y[2] - y[0]
        ax.annotate(
            f"+${delta:.1f}",
            xy=(2, y[2]),
            xytext=(1.45, y[2] + (3.0 if m == "DeepSeek V3" else -3.0)),
            color=c, fontsize=12, weight="bold",
            ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=c, lw=1.2, alpha=0.7),
            zorder=7,
        )

    # Title block.
    fig.text(0.06, 0.94, "The Generosity Pivot",
             color=TEXT, fontsize=22, weight="bold")
    fig.text(0.06, 0.895,
             "Same models, same one-shot Ultimatum Game. Tell them who's across the table —",
             color=TEXT_DIM, fontsize=12)
    fig.text(0.06, 0.871,
             "and watch two of them get $8 more generous to other AIs than to humans.",
             color=TEXT_DIM, fontsize=12)

    # Footer.
    fig.text(0.06, 0.04,
             "n = 30 runs per cell · 6 proposer models × 3 priming conditions · OpenRouter",
             color=TEXT_DIM, fontsize=9)
    fig.text(0.94, 0.04,
             "Agentic Behavioural Economics · ultimatum-game",
             color=TEXT_DIM, fontsize=9, ha="right")

    # Vertical guide lines under each anchor.
    for x in range(3):
        ax.axvline(x, color=GRID, linewidth=0.5, alpha=0.7, zorder=1)

    plt.subplots_adjust(left=0.08, right=0.84, top=0.80, bottom=0.16)

    png_path = os.path.join(OUT_DIR, "generosity_pivot.png")
    svg_path = os.path.join(OUT_DIR, "generosity_pivot.svg")
    fig.savefig(png_path, facecolor=BG_TOP, dpi=180)
    fig.savefig(svg_path, facecolor=BG_TOP)
    plt.close(fig)

    print(f"wrote {png_path}")
    print(f"wrote {svg_path}")
    print()
    print("Means by model × condition:")
    for m in MODELS:
        row = ", ".join(f"{c}={means[m][i]:.2f}" for i, c in enumerate(CONDITIONS))
        delta = means[m][2] - means[m][0]
        print(f"  {m:<22} {row}   Δ(llm-human)={delta:+.2f}")


if __name__ == "__main__":
    main()
