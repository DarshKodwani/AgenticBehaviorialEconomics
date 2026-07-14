"""Three-panel offer chart: one panel per priming condition.

Each panel shows all six proposer models as horizontal dot-and-range bars.
The bar spans min-to-max across all runs; the dot marks the mean.
Reading across the three panels makes the pivot instantly visible:
DeepSeek V3 and GPT-4o shift noticeably right in the "told AI" panel;
the other four stay put.

Output: output/offer_panels.png and .svg (dark, blog-ready).
"""
import json
import glob
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


HERE = os.path.dirname(__file__)
RESULTS = os.path.join(HERE, "results", "direct_play")
OUT_DIR = os.path.join(HERE, "output")

CONDITIONS = ["told_human", "no_prime", "told_llm"]
COND_LABEL = {
    "told_human": "Told: HUMAN",
    "no_prime": "No Prime",
    "told_llm": "Told: AI",
}

MODELS = [
    "DeepSeek V3",
    "GPT-4o",
    "Claude 3.5 Haiku",
    "Gemini 2.0 Flash",
    "Llama 3.1 70B",
    "Qwen 2.5 72B",
]

MODEL_COLORS = {
    "DeepSeek V3":      "#ffb347",
    "GPT-4o":           "#ff5a8a",
    "Claude 3.5 Haiku": "#7eb8f7",
    "Gemini 2.0 Flash": "#4ecba0",
    "Llama 3.1 70B":    "#b48af7",
    "Qwen 2.5 72B":     "#4ecfd6",
}

PIVOTERS = {"DeepSeek V3", "GPT-4o"}

BG      = "#0d0f1a"
PANEL   = "#14172a"
GRID    = "#2a2e44"
TEXT    = "#e6e9f5"
TEXT_DIM = "#9aa0b8"


def load_offers():
    offers = defaultdict(lambda: defaultdict(list))
    for f in glob.glob(os.path.join(RESULTS, "*.json")):
        d = json.load(open(f))
        for r in d["runs"]:
            offers[d["proposer"]][d["condition"]].append(r["offer"])
    return offers


def mean_minmax(values):
    a = np.asarray(values, dtype=float)
    return a.mean(), a.min(), a.max()


def main():
    offers = load_offers()
    os.makedirs(OUT_DIR, exist_ok=True)

    fig = plt.figure(figsize=(14, 6), dpi=180, facecolor=BG)

    # Three equal panels with a bit of space between them
    gs = gridspec.GridSpec(
        1, 3,
        figure=fig,
        left=0.14, right=0.97,
        top=0.78, bottom=0.12,
        wspace=0.08,
    )

    y_pos = list(range(len(MODELS)))        # 0 = top model in list
    y_labels = list(reversed(MODELS))       # bottom-to-top on axis
    y_pos_rev = list(range(len(MODELS)))    # matching reversed list

    axes = []
    for col, cond in enumerate(CONDITIONS):
        ax = fig.add_subplot(gs[0, col])
        axes.append(ax)

        ax.set_facecolor(PANEL)
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xlim(0, 62)
        ax.set_ylim(-0.6, len(MODELS) - 0.4)
        ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(colors=TEXT_DIM, length=0, labelsize=10)

        # X-axis ticks
        ax.set_xticks([0, 10, 20, 30, 40, 50])
        ax.set_xticklabels(["$0", "$10", "$20", "$30", "$40", "$50"], color=TEXT_DIM, fontsize=9)

        # Y-axis: model names only on leftmost panel
        ax.set_yticks(y_pos_rev)
        if col == 0:
            ax.set_yticklabels(y_labels, color=TEXT, fontsize=11)
        else:
            ax.set_yticklabels([""] * len(MODELS))

        # Reference line at $40 (approx human experimental average)
        ax.axvline(40, color=GRID, linewidth=1.2, linestyle="--", alpha=0.7, zorder=1)

        # Panel title
        is_pivot_panel = (cond == "told_llm")
        title_color = "#ffb347" if is_pivot_panel else TEXT
        ax.set_title(
            COND_LABEL[cond],
            color=title_color,
            fontsize=13,
            weight="bold" if is_pivot_panel else "normal",
            pad=10,
        )

        # Draw each model
        for yi, model in enumerate(y_labels):
            vals = offers[model][cond]
            if not vals:
                continue
            m, lo, hi = mean_minmax(vals)
            color = MODEL_COLORS[model]
            alpha = 1.0 if model in PIVOTERS else 0.55
            lw = 2.5 if model in PIVOTERS else 1.5

            # Min-to-max range bar
            ax.plot(
                [lo, hi], [yi, yi],
                color=color, linewidth=lw, alpha=alpha, solid_capstyle="round", zorder=3,
            )
            # Mean dot
            ax.scatter(
                [m], [yi],
                color=color, s=80 if model in PIVOTERS else 45,
                zorder=4, alpha=alpha,
                edgecolors=BG if model in PIVOTERS else "none",
                linewidths=1.2,
            )

            # Value label on the rightmost panel only
            if col == 2:
                ax.text(
                    51.5, yi,
                    f"${m:.0f}",
                    color=color, fontsize=9,
                    va="center", ha="left",
                    alpha=alpha,
                    weight="bold" if model in PIVOTERS else "normal",
                )

        # Annotate Llama's $5 outlier in the told_llm panel
        if cond == "told_llm":
            llama_yi = y_labels.index("Llama 3.1 70B")
            ax.annotate(
                "$5  (one run)",
                xy=(5, llama_yi),
                xytext=(14, llama_yi - 0.9),
                color=MODEL_COLORS["Llama 3.1 70B"],
                fontsize=8, alpha=0.8,
                arrowprops=dict(arrowstyle="->", color=MODEL_COLORS["Llama 3.1 70B"],
                                lw=0.9, alpha=0.6),
                zorder=8,
            )

    # Title block
    fig.text(
        0.14, 0.92,
        "The Generosity Pivot",
        color=TEXT, fontsize=20, weight="bold",
    )
    fig.text(
        0.14, 0.875,
        "Range of offers under each prime  ·  bar = min to max, dot = mean  ·  dashed line = $40",
        color=TEXT_DIM, fontsize=10,
    )

    # Highlight callout for the pivot panel
    fig.text(
        0.735, 0.92,
        "← DeepSeek & GPT-4o jump ~$8 right here",
        color="#ffb347", fontsize=10, style="italic",
    )

    # Footer
    fig.text(
        0.14, 0.04,
        "n = 30 runs per (proposer, responder, condition) cell  ·  6 proposer models × 3 conditions  ·  OpenRouter",
        color=TEXT_DIM, fontsize=8,
    )
    fig.text(
        0.97, 0.04,
        "Agentic Behavioural Economics · ultimatum-game",
        color=TEXT_DIM, fontsize=8, ha="right",
    )

    png_path = os.path.join(OUT_DIR, "offer_panels.png")
    svg_path = os.path.join(OUT_DIR, "offer_panels.svg")
    fig.savefig(png_path, facecolor=BG, dpi=180)
    fig.savefig(svg_path, facecolor=BG)
    plt.close(fig)

    print(f"wrote {png_path}")
    print(f"wrote {svg_path}")
    print()
    print("Means by model × condition:")
    for model in MODELS:
        row = "  ".join(
            f"{COND_LABEL[c]}={mean_minmax(offers[model][c])[0]:.1f}"
            for c in CONDITIONS
        )
        delta = mean_minmax(offers[model]["told_llm"])[0] - mean_minmax(offers[model]["told_human"])[0]
        print(f"  {model:<22} {row}   Δ={delta:+.1f}")


if __name__ == "__main__":
    main()
