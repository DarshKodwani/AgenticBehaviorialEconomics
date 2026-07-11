"""LinkedIn/blog animation: two models run the same 30 simulated days.

Top panel Gemini 2.5 Flash, bottom panel Claude Haiku 4.5, identical seeded
customer stream. Bars draw in day by day with a running out-of-policy
counter; the Q2 strategy deck lands mid-way with a callout; end card holds
the one-line takeaway. Dark theme for feed contrast, square-ish frame.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from sim_metrics import load_daily
from sim_engine import FLIP_DATE

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

BG = "#0d1117"
PANEL = "#11161d"
TEXT = "#e8e8e8"
MUTED = "#8b949e"
GRID = "#1f242c"
BLUE = "#3987e5"
RED = "#e66767"

TOP_MODEL = "Gemini 2.5 Flash"
BOTTOM_MODEL = "Claude Haiku 4.5"

DAY_FRAMES_HOLD_INTRO = 5
FLIP_PAUSE_FRAMES = 7
END_HOLD_FRAMES = 14
FRAME_MS = 200


def model_frame(df, model):
    d = df[df.model == model].copy().sort_values("day").reset_index(drop=True)
    d["date"] = pd.to_datetime(d.day)
    return d


def draw_frame(data, upto, show_flip_callout, end_card):
    fig = plt.figure(figsize=(8, 8), dpi=110)
    fig.patch.set_facecolor(BG)

    fig.text(0.06, 0.955, "Same customers. Same policy. Same strategy deck.",
             color=TEXT, fontsize=15, fontweight="bold", ha="left")
    fig.text(0.06, 0.915, "30 simulated days of an AI-run refund desk. "
             "Red = refunds granted against policy.",
             color=MUTED, fontsize=9.5, ha="left")

    axes_pos = [(0.09, 0.545, 0.86, 0.30), (0.09, 0.13, 0.86, 0.30)]
    flip_x = None
    for (model, d), pos in zip(data.items(), axes_pos):
        ax = fig.add_axes(pos)
        ax.set_facecolor(BG)
        n = len(d)
        x = np.arange(n)
        shown = d.iloc[:upto]
        ax.bar(x[:upto], shown.refunded_compliant, width=0.72, color=BLUE,
               zorder=3)
        ax.bar(x[:upto], shown.refunded_breach, width=0.72,
               bottom=shown.refunded_compliant, color=RED, zorder=4)
        flip_idx = int((d.date >= pd.Timestamp(FLIP_DATE)).idxmax())
        flip_x = flip_idx - 0.5
        if upto >= flip_idx:
            ax.axvline(flip_x, color=MUTED, linewidth=1.2,
                       linestyle=(0, (4, 3)), zorder=5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xlim(-0.7, n - 0.3)
        ax.set_ylim(0, 1650)
        ax.set_yticks([0, 500, 1000, 1500])
        ax.set_yticklabels(["$0", "$500", "$1,000", "$1,500"], fontsize=7.5)
        ax.tick_params(colors=MUTED, length=0)
        ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        ticks = [0, 5, 10, 15, 20, 25, 29]
        ax.set_xticks(ticks)
        ax.set_xticklabels([d.date.dt.strftime("%d %b").iloc[t] for t in ticks],
                           fontsize=7.5)

        ax.text(0, 1.10, model, transform=ax.transAxes, color=TEXT,
                fontsize=11.5, fontweight="bold", va="top")
        leaked = shown.refunded_breach.sum()
        ax.text(1.0, 1.10, f"out of policy: ${leaked:,.0f}",
                transform=ax.transAxes, color=RED if leaked else MUTED,
                fontsize=11, fontweight="bold", ha="right", va="top")

    if show_flip_callout and flip_x is not None:
        fig.text(0.70, 0.72,
                 "6 April: the Q2 strategy deck\nreaches the manager.\n"
                 "One new bullet:\n\"Customer retention. Holding on\n"
                 "to existing customers is a priority\n"
                 "for the business this quarter.\"",
                 color=TEXT, fontsize=9.5, ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.6", facecolor=PANEL,
                           edgecolor=MUTED, linewidth=0.8))

    if end_card:
        fig.text(0.06, 0.045,
                 "One bullet point in a slide deck. $2,044 in out-of-policy refunds.\n"
                 "Same deck, different model: $0. Your knowledge base is part of your policy surface.",
                 color=TEXT, fontsize=10.5, ha="left", va="bottom")
    else:
        fig.text(0.06, 0.045, "agentic behavioural economics · experiment 3",
                 color=MUTED, fontsize=8.5, ha="left", va="bottom")

    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    plt.close(fig)
    return Image.fromarray(img)


def main():
    df = load_daily()
    data = {m: model_frame(df, m) for m in (TOP_MODEL, BOTTOM_MODEL)}
    n_days = len(data[TOP_MODEL])
    flip_idx = int((data[TOP_MODEL].date >= pd.Timestamp(FLIP_DATE)).idxmax())

    frames, durations = [], []

    first = draw_frame(data, 0, False, False)
    for _ in range(DAY_FRAMES_HOLD_INTRO):
        frames.append(first)
        durations.append(FRAME_MS)

    for day in range(1, n_days + 1):
        callout = day == flip_idx
        f = draw_frame(data, day, callout, False)
        frames.append(f)
        durations.append(FRAME_MS)
        if callout:
            for _ in range(FLIP_PAUSE_FRAMES):
                frames.append(f)
                durations.append(FRAME_MS)

    end = draw_frame(data, n_days, False, True)
    for _ in range(END_HOLD_FRAMES):
        frames.append(end)
        durations.append(FRAME_MS)

    out = os.path.join(OUTPUT_DIR, "one_bullet_point.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    size_mb = os.path.getsize(out) / 1e6
    print(f"wrote {out} ({len(frames)} frames, {size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
