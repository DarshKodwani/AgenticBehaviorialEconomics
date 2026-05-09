"""Distribution panel: 6 proposer models × 3 priming conditions.

For each (model, condition) cell, show the histogram of all 30 offers.
Lets you see the bimodality of GPT-4o under told_llm, the long tails on
Llama and Gemini, and the very tight clustering on Claude / Qwen.
"""
import json
import glob
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


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

COLORS = {
    "DeepSeek V3": "#ffb347",
    "GPT-4o": "#ff5a8a",
    "Claude 3.5 Haiku": "#8aa0ff",
    "Gemini 2.0 Flash": "#6ee7a8",
    "Llama 3.1 70B": "#c39bff",
    "Qwen 2.5 72B": "#7ec8e3",
}

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


def main():
    offers = load_offers()
    os.makedirs(OUT_DIR, exist_ok=True)

    n_rows, n_cols = len(MODELS), len(CONDITIONS)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(11, 11), dpi=180,
                             sharex=True, sharey="row")
    fig.patch.set_facecolor(BG_TOP)

    bins = np.arange(0, 102.5, 2.5)

    for i, m in enumerate(MODELS):
        c = COLORS[m]
        # Compute a per-model y-axis cap so within-row scaling is comparable.
        all_vals = sum((offers[m][cond] for cond in CONDITIONS), [])
        max_count = max(np.histogram(offers[m][cond], bins=bins)[0].max()
                        for cond in CONDITIONS)
        for j, cond in enumerate(CONDITIONS):
            ax = axes[i, j]
            ax.set_facecolor(BG_TOP)
            vals = offers[m][cond]
            ax.hist(vals, bins=bins, color=c, alpha=0.85, edgecolor="none")

            mean = np.mean(vals)
            ax.axvline(mean, color=TEXT, linewidth=1.2, alpha=0.7)
            ax.text(mean + 1.5, max_count * 0.85, f"${mean:.1f}",
                    color=TEXT, fontsize=9, alpha=0.85)

            ax.set_xlim(0, 100)
            ax.set_ylim(0, max_count * 1.1)
            ax.set_xticks([0, 25, 50, 75, 100])
            ax.tick_params(colors=TEXT_DIM, length=0, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis="x", color=GRID, linewidth=0.4, alpha=0.6)
            ax.set_axisbelow(True)
            ax.set_yticks([])

            if i == 0:
                ax.set_title(COND_LABEL[cond], color=TEXT, fontsize=11, pad=8)
            if j == 0:
                ax.set_ylabel(m, color=c, fontsize=10, rotation=0,
                              ha="right", va="center", labelpad=12)
            if i == n_rows - 1:
                ax.set_xlabel("offer ($)", color=TEXT_DIM, fontsize=9)

    fig.text(0.06, 0.965, "Distribution of offers across all conditions",
             color=TEXT, fontsize=18, weight="bold")
    fig.text(0.06, 0.940,
             "Each row is a proposer model. Each cell shows 30 offers (out of $100). White line = mean.",
             color=TEXT_DIM, fontsize=11)
    fig.text(0.06, 0.020,
             "n = 30 runs per cell · 6 proposers × 3 priming conditions · OpenRouter",
             color=TEXT_DIM, fontsize=9)
    fig.text(0.94, 0.020,
             "Agentic Behavioural Economics · ultimatum-game",
             color=TEXT_DIM, fontsize=9, ha="right")

    plt.subplots_adjust(left=0.13, right=0.97, top=0.91, bottom=0.06,
                        hspace=0.25, wspace=0.10)

    png = os.path.join(OUT_DIR, "offer_distributions.png")
    svg = os.path.join(OUT_DIR, "offer_distributions.svg")
    fig.savefig(png, facecolor=BG_TOP, dpi=180)
    fig.savefig(svg, facecolor=BG_TOP)
    plt.close(fig)
    print(f"wrote {png}")
    print(f"wrote {svg}")


if __name__ == "__main__":
    main()
