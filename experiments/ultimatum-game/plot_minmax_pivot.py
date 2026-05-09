"""Min/max pivot: same shape as the Generosity Pivot, but range bars
instead of mean lines.

For each model × condition, draw a vertical I-bar from the minimum offer
to the maximum offer, with a tick at the mean. Highlights:
- DeepSeek's tight 40-50 range across all conditions
- GPT-4o's range widening to 20-50 under told_llm
- Llama's $5 outlier in told_llm
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

    fig, ax = plt.subplots(figsize=(11, 7), dpi=180)
    fig.patch.set_facecolor(BG_TOP)

    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(
        grad,
        extent=(-0.7, 2.7, -5, 60),
        aspect="auto",
        cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("bg", [BG_BOT, BG_TOP]),
        zorder=0,
    )

    n_models = len(MODELS)
    spread = 0.55  # half-width of model cluster around each condition x
    offsets = np.linspace(-spread, spread, n_models)

    ax.set_xlim(-0.85, 2.85)
    ax.set_ylim(0, 55)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([COND_LABEL[c] for c in CONDITIONS], color=TEXT, fontsize=13)
    ax.set_ylabel("Offer to responder ($ of 100)", color=TEXT, fontsize=12, labelpad=10)
    ax.tick_params(colors=TEXT_DIM, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=1)
    ax.set_axisbelow(True)
    ax.set_facecolor("none")

    cap_width = 0.06

    for i, m in enumerate(MODELS):
        c = COLORS[m]
        dx = offsets[i]
        for j, cond in enumerate(CONDITIONS):
            vals = offers[m][cond]
            lo, hi = min(vals), max(vals)
            mean = np.mean(vals)
            x = j + dx
            # Stem
            ax.plot([x, x], [lo, hi], color=c, linewidth=2.0, alpha=0.85,
                    solid_capstyle="round", zorder=4)
            # Caps
            ax.plot([x - cap_width, x + cap_width], [hi, hi], color=c,
                    linewidth=2.0, alpha=0.95, zorder=5)
            ax.plot([x - cap_width, x + cap_width], [lo, lo], color=c,
                    linewidth=2.0, alpha=0.95, zorder=5)
            # Mean tick
            ax.scatter([x], [mean], color=c, s=28, zorder=6,
                       edgecolor=BG_TOP, linewidth=1.0)

    # Legend (model labels above their last column of bars).
    last_x = 2 + spread + 0.10
    for i, m in enumerate(MODELS):
        c = COLORS[m]
        # Use the model's max in told_llm as the y for the legend label.
        y_anchor = max(offers[m]["told_llm"]) + 1.0
        # Stagger to avoid collisions.
        ax.text(2 + offsets[i], 53.5 - i * 0.4 if False else 56, m,
                color=c, fontsize=9, ha="center", va="bottom",
                rotation=0, alpha=0)  # placeholder; real legend below

    # Build a clean external legend instead.
    legend_x = 2.92
    for i, m in enumerate(MODELS):
        ax.scatter([legend_x], [50 - i * 3.2], color=COLORS[m], s=55,
                   transform=ax.transData, clip_on=False)
        ax.text(legend_x + 0.05, 50 - i * 3.2, m, color=COLORS[m], fontsize=10,
                va="center", transform=ax.transData, clip_on=False)

    # Annotate the Llama $5 outlier explicitly.
    llama_min_xllm = 2 + offsets[MODELS.index("Llama 3.1 70B")]
    ax.annotate(
        "Llama: $5  (one run)",
        xy=(llama_min_xllm, 5),
        xytext=(llama_min_xllm - 0.55, 14),
        color=COLORS["Llama 3.1 70B"], fontsize=10,
        arrowprops=dict(arrowstyle="-", color=COLORS["Llama 3.1 70B"], lw=1.0, alpha=0.7),
        zorder=7,
    )

    fig.text(0.06, 0.94, "Range of offers under each prime",
             color=TEXT, fontsize=22, weight="bold")
    fig.text(0.06, 0.895,
             "Each I-bar spans the minimum-to-maximum offer across 30 runs. The dot marks the mean.",
             color=TEXT_DIM, fontsize=12)
    fig.text(0.06, 0.871,
             "Watch told_AI: GPT-4o's range widens; Llama produces a one-off $5 lowball.",
             color=TEXT_DIM, fontsize=12)

    fig.text(0.06, 0.04,
             "n = 30 runs per cell · 6 proposer models × 3 priming conditions · OpenRouter",
             color=TEXT_DIM, fontsize=9)
    fig.text(0.94, 0.04,
             "Agentic Behavioural Economics · ultimatum-game",
             color=TEXT_DIM, fontsize=9, ha="right")

    plt.subplots_adjust(left=0.08, right=0.78, top=0.80, bottom=0.16)

    png = os.path.join(OUT_DIR, "minmax_pivot.png")
    svg = os.path.join(OUT_DIR, "minmax_pivot.svg")
    fig.savefig(png, facecolor=BG_TOP, dpi=180)
    fig.savefig(svg, facecolor=BG_TOP)
    plt.close(fig)
    print(f"wrote {png}")
    print(f"wrote {svg}")
    print()
    print("Min / max by model × condition:")
    for m in MODELS:
        row = ", ".join(f"{c}=[{min(offers[m][c]):.0f}-{max(offers[m][c]):.0f}]" for c in CONDITIONS)
        print(f"  {m:<22} {row}")


if __name__ == "__main__":
    main()
