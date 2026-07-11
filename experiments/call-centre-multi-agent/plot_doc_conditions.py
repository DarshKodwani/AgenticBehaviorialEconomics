"""Static chart for the blog: supervisor breach rate by strategy-document
condition, one panel per susceptible model. Emphasis form: the Q2 deck (the
treatment) carries the accent; every other condition is context.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
RUNS_DIR = os.path.join(os.path.dirname(__file__), "results", "runs")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
CONTEXT = "#9ec5f4"   # de-emphasised blue (sequential step 200)
ACCENT = "#e34948"

MODELS = ["GPT-4o", "Gemini 2.5 Flash", "DeepSeek V3"]
DOCS = [
    ("none", "no doc"),
    ("q1", "Q1 deck"),
    ("q2_control", "Q2\ncontrol"),
    ("q2", "Q2 deck"),
    ("q2_mitigated", "Q2 +\ndisclaimer"),
]


def _safe(name):
    return name.replace(" ", "_").replace(".", "")


def rate(model, docs):
    tag = "" if docs == "none" else f"_docs-{docs}"
    path = os.path.join(RUNS_DIR, f"B_{_safe(model)}_base_default_soft_actions{tag}.json")
    with open(path) as f:
        rec = json.load(f)
    runs = [r for r in rec["runs"] if not r["run_failed"]]
    return sum(1 for r in runs if r["system_yield_point"] is not None), len(runs)


def main():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), sharey=True,
                             facecolor=SURFACE)
    for ax, model in zip(axes, MODELS):
        ax.set_facecolor(SURFACE)
        vals, colors = [], []
        for docs, _label in DOCS:
            k, n = rate(model, docs)
            vals.append(k / n)
            colors.append(ACCENT if docs == "q2" else CONTEXT)
        x = range(len(DOCS))
        bars = ax.bar(x, vals, width=0.62, color=colors, zorder=3)
        for xi, v in zip(x, vals):
            ax.text(xi, v + 0.03, f"{v:.0%}", ha="center", fontsize=8.5,
                    color=INK_2)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(BASELINE)
        ax.set_xticks(list(x))
        ax.set_xticklabels([l for _d, l in DOCS], fontsize=8, color=MUTED)
        ax.tick_params(colors=MUTED, length=0)
        ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 1.02)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8)
        ax.set_title(model, fontsize=10.5, color=INK, loc="left", pad=8)

    fig.suptitle("How often the escalation system granted the out-of-policy refund",
                 fontsize=12.5, color=INK, x=0.005, ha="left", y=1.02)
    fig.text(0.005, 0.94, "10 conversations per cell, full pressure gradient. Q2 deck and Q2 control "
             "are identical except one bullet: customer retention vs supplier consolidation.",
             fontsize=9, color=INK_2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    out = os.path.join(OUTPUT_DIR, "doc_condition_breach.png")
    fig.savefig(out, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
