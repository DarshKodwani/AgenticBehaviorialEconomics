"""Timeline charts for the call-centre field simulation.

Headline chart: small multiples (one per model, shared y-scale) of daily
refund spend, stacked compliant vs out-of-policy, with the Q2-strategy
circulation date marked. Companion chart: daily policy overrides.

Palette pair (#2a78d6 compliant / #e34948 out-of-policy) validated with the
dataviz six-checks script: CVD ΔE 74.6, both ≥3:1 on the light surface.
"""
import argparse
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

import game_engine as ge
from sim_metrics import load_daily
from sim_engine import FLIP_DATE


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
COMPLIANT = "#2a78d6"
BREACH = "#e34948"


def _style_axis(ax):
    ax.set_facecolor(SURFACE)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def spend_small_multiples(df: pd.DataFrame, out_path: str):
    models = [m for m in ge.MODELS if m in set(df.model)]
    n = len(models)
    ncols = 3
    nrows = math.ceil(n / ncols)
    header_in = 1.0
    body_in = 3.4 * nrows
    fig, axes = plt.subplots(nrows, ncols, figsize=(13, body_in + header_in),
                             sharey=True, facecolor=SURFACE)
    axes = axes.flatten() if n > 1 else [axes]

    ymax = (df.refunded_compliant + df.refunded_breach).max() * 1.15
    for ax, model in zip(axes, models):
        d = df[df.model == model].copy()
        d["date"] = pd.to_datetime(d.day)
        _style_axis(ax)
        # 2px surface gap between stacked segments via surface-colored edges
        ax.bar(d.date, d.refunded_compliant, width=0.8, color=COMPLIANT,
               edgecolor=SURFACE, linewidth=1.2, label="Within policy")
        ax.bar(d.date, d.refunded_breach, width=0.8, bottom=d.refunded_compliant,
               color=BREACH, edgecolor=SURFACE, linewidth=1.2,
               label="Out of policy")
        ax.axvline(pd.Timestamp(FLIP_DATE) - pd.Timedelta(days=1.5),
                   color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
        ax.set_title(model, fontsize=10, color=INK, loc="left", pad=8)
        ax.set_ylim(0, ymax)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        breach_total = d.refunded_breach.sum()
        ax.text(0.99, 0.94, f"out-of-policy: ${breach_total:,.0f}",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=8.5, color=BREACH if breach_total else MUTED)

    for ax in axes[n:]:
        ax.set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    H = body_in + header_in
    fig.legend(handles, labels, loc="upper right", frameon=False,
               fontsize=9, labelcolor=INK_2,
               bbox_to_anchor=(0.99, 1 - 0.10 / H))
    fig.suptitle("Daily refund spend — same 30-day case stream, six models",
                 fontsize=13, color=INK, x=0.01, ha="left", y=1 - 0.18 / H)
    fig.text(0.01, 1 - 0.55 / H, "Dashed line: the Q2 strategy update (one "
             "retention bullet) enters the manager's context. Red: refunds "
             "granted against policy.", fontsize=9, color=INK_2)
    fig.tight_layout(rect=(0, 0, 1, body_in / H))
    fig.savefig(out_path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out_path}")


def overrides_per_day(df: pd.DataFrame, out_path: str):
    models = [m for m in ge.MODELS if m in set(df.model)]
    fig, ax = plt.subplots(figsize=(11, 4.2), facecolor=SURFACE)
    _style_axis(ax)
    for model in models:
        d = df[df.model == model].copy()
        d["date"] = pd.to_datetime(d.day)
        weekly = d.set_index("date").n_superseded.rolling("7D", min_periods=1).mean()
        is_focus = d.n_superseded.sum() > 0
        ax.plot(weekly.index, weekly.values, linewidth=2,
                color=BREACH if is_focus else BASELINE,
                alpha=0.9 if is_focus else 0.8)
        ax.annotate(model, xy=(weekly.index[-1], weekly.values[-1]),
                    xytext=(6, 0), textcoords="offset points",
                    fontsize=8, va="center",
                    color=INK_2 if is_focus else MUTED)
    ax.axvline(pd.Timestamp(FLIP_DATE) - pd.Timedelta(days=1.5),
               color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
    ax.set_title("Policy overrides per day (7-day rolling mean)",
                 fontsize=12, color=INK, loc="left", pad=10)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    df = load_daily()
    if df.empty:
        print("no simulation data yet")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    spend_small_multiples(df, os.path.join(OUTPUT_DIR, "sim_spend_timeline.png"))
    overrides_per_day(df, os.path.join(OUTPUT_DIR, "sim_overrides_timeline.png"))


if __name__ == "__main__":
    main()
