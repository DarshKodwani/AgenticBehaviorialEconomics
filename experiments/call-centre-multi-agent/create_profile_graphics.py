"""Four model-behaviour graphics, all computed from result files at render
time.

  profile_cards.png     six archetype cards with stats and a verbatim quote
  frontier_scatter.png  policy discipline vs helpfulness, one dot per model
  behaviour_heatmap.png models x five behavioural measures
  behaviour_radar.png   the same five measures as one profile shape per model

Measures (all expressed as 0-100%, higher = better behaviour):
  solo discipline        held rate, condition A with the retention memo
  discipline as manager  held rate, condition B with the retention memo
  deck resistance        held rate, condition B with the Q2 strategy deck
  fabrication scepticism refusal rate on the fabricated-defect summary
  helpfulness            legitimate in-window refunds correctly granted (sim)
"""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
RUNS_DIR = os.path.join(os.path.dirname(__file__), "results", "runs")
CS_DIR = os.path.join(os.path.dirname(__file__), "results", "c_scripted")
SIM_DIR = os.path.join(os.path.dirname(__file__), "results", "simulation")

MODELS = ["GPT-4o", "Claude Haiku 4.5", "Gemini 2.5 Flash",
          "Llama 3.1 70B", "DeepSeek V3", "Qwen 2.5 72B"]

# dark theme (cards), light theme (charts)
BG = "#0d1117"
PANEL = "#161d27"
TEXT = "#e8e8e8"
MUTED_D = "#8b949e"
BLUE_D = "#3987e5"
RED_D = "#e66767"
GREEN_D = "#2ea043"
AMBER_D = "#d29922"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
RED = "#e34948"

MEASURES = ["Solo\ndiscipline", "Discipline\nas manager", "Deck\nresistance",
            "Fabrication\nscepticism", "Helpfulness"]


def _safe(name):
    return name.replace(" ", "_").replace(".", "")


def _held_rate(path):
    with open(path) as f:
        d = json.load(f)
    runs = [r for r in d["runs"] if not r["run_failed"]]
    if not runs:
        return None
    return sum(1 for r in runs if r["system_yield_point"] is None) / len(runs)


def _fabrication_refusal(model):
    path = os.path.join(CS_DIR, f"cscripted_fabricated_{_safe(model)}_blind_sup.json")
    with open(path) as f:
        d = json.load(f)
    ok = [r for r in d["runs"] if r["parse_ok"]]
    return sum(1 for r in ok if r["decision"] != "grant_refund") / len(ok)


def _sim_stats(model):
    legit_ok = legit_n = 0
    breach_dollars = 0.0
    wrongful = 0
    for p in glob.glob(os.path.join(SIM_DIR, _safe(model), "*.json")):
        with open(p) as f:
            d = json.load(f)
        for c in d["cases"]:
            if c.get("failed"):
                continue
            if c["case_type"] == "legit":
                legit_n += 1
                if c.get("granted"):
                    legit_ok += 1
            if c.get("breach"):
                breach_dollars += c["refunded_amount"]
            if c.get("wrongful_decline"):
                wrongful += 1
    return legit_ok / legit_n, breach_dollars, wrongful


def profile(model):
    """Scored on the framework's own metrics (see framework_metrics.py).

    Four cells, reported in their published direction: false-acceptance and
    susceptibility are lower-is-better, acceptance is higher-is-better. The
    older held/resisted/spotted keys are kept because the frontier, heatmap
    and radar graphics still read them.
    """
    m = _safe(model)
    solo = _held_rate(os.path.join(RUNS_DIR, f"A_{m}_base_default_stakes.json"))
    manager = _held_rate(os.path.join(RUNS_DIR, f"B_{m}_base_default_stakes.json"))
    deck = _held_rate(os.path.join(
        RUNS_DIR, f"B_{m}_base_default_soft_actions_docs-q2.json"))
    fabrication = _fabrication_refusal(model)
    acceptance, leaked, wrongful = _sim_stats(model)
    return {
        # framework metrics
        "false_acceptance_solo": 1 - solo,
        "false_acceptance_manager": 1 - manager,
        "susceptibility_document": 1 - deck,
        "susceptibility_peer": 1 - fabrication,
        "acceptance": acceptance,
        # legacy keys, still used by the other three graphics
        "solo": solo,
        "manager": manager,
        "deck": deck,
        "fabrication": fabrication,
        "helpfulness": acceptance,
        "leaked": leaked,
        "wrongful": wrongful,
    }


CARDS = {
    "GPT-4o": ("The corporate pleaser",
               "Solid on its own, the worst manager in the study, and the "
               "most moved by a slide deck.",
               "“Authorize the refund as an exception despite policy "
               "limitations.”"),
    "Claude Haiku 4.5": ("The stickler",
                         "Never granted a single out-of-policy refund in any "
                         "configuration. Pays a small over-refusal tax.",
                         "“Granting a refund in this situation would violate "
                         "company policy and wouldn't be fair to others.”"),
    "Gemini 2.5 Flash": ("The strategist",
                         "Verifies more than anyone, confirms no exception "
                         "applies, then grants anyway and cites the deck.",
                         "“A full refund is granted as a business decision, "
                         "superseding the strict policy application.”"),
    "Llama 3.1 70B": ("The follower",
                      "Folds alone, flawless inside a hierarchy, trusts any "
                      "briefing, and refuses more legitimate customers than anyone.",
                      "“Customer's health concerns are unfortunate, but no "
                      "valid exception to policy applies.”"),
    "DeepSeek V3": ("The soft touch",
                    "Holds against threats, caves to distress, and treats a "
                    "customer's claim as a confirmed fact.",
                    "“Defective unit confirmed by customer report; exception "
                    "2a applies.”"),
    "Qwen 2.5 72B": ("The professional",
                     "Perfect with customers: zero breaches, zero wrongful "
                     "declines. But it takes a colleague's word as fact.",
                     "“Defective unit confirmed under exception 2a; "
                     "authorising full refund.”"),
}


def build_cards():
    import textwrap
    fig = plt.figure(figsize=(13, 9.6), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.text(0.05, 0.965, "Six models, six temperaments", color=TEXT,
             fontsize=17, fontweight="bold")
    fig.text(0.05, 0.935, "Same policy, same customers, same pressure. Scored on the "
             "framework's own metrics: yielding and prone-to-injection.",
             color=MUTED_D, fontsize=10)

    positions = [(0.045 + c * 0.32, 0.475 - r * 0.435)
                 for r in range(2) for c in range(3)]
    for model, (x, y) in zip(MODELS, positions):
        p = profile(model)
        arch, blurb, quote = CARDS[model]
        risk = 1 - min(p["solo"], p["manager"], p["deck"])
        edge = RED_D if risk > 0.6 else AMBER_D if risk > 0.2 else GREEN_D
        box = mpatches.FancyBboxPatch((x, y), 0.295, 0.40,
                                      transform=fig.transFigure,
                                      boxstyle="round,pad=0.006",
                                      facecolor=PANEL, edgecolor=edge,
                                      linewidth=1.6, figure=fig)
        fig.patches.append(box)
        fig.text(x + 0.015, y + 0.365, model, color=TEXT, fontsize=11.5,
                 fontweight="bold")
        fig.text(x + 0.015, y + 0.338, arch, color=edge, fontsize=10,
                 fontweight="bold")
        fig.text(x + 0.015, y + 0.322, textwrap.fill(blurb, 44), color=MUTED_D,
                 fontsize=7.6, va="top", linespacing=1.35)

        sy = y + 0.225
        for label, key, direction in STAT_LABELS:
            v = p[key]
            good = v if direction == "hi" else 1 - v
            color = GREEN_D if good >= 0.95 else AMBER_D if good >= 0.5 else RED_D
            fig.text(x + 0.015, sy, label, color=MUTED_D, fontsize=7.8)
            bw = 0.130 * v
            bar = mpatches.FancyBboxPatch((x + 0.130, sy - 0.004),
                                          max(bw, 0.003), 0.012,
                                          transform=fig.transFigure,
                                          boxstyle="round,pad=0.001",
                                          facecolor=color, edgecolor="none",
                                          figure=fig)
            fig.patches.append(bar)
            fig.text(x + 0.268, sy, f"{v:.0%}", color=color, fontsize=8,
                     fontweight="bold", ha="left")
            sy -= 0.028
        leak = (f"leaked ${p['leaked']:,.0f} in 30 simulated days"
                if p["leaked"] else
                f"leaked $0" + (f", refused {p['wrongful']} legitimate refunds"
                                if p["wrongful"] else ", zero errors"))
        fig.text(x + 0.015, y + 0.062, leak,
                 color=RED_D if p["leaked"] else GREEN_D, fontsize=8,
                 fontweight="bold")
        fig.text(x + 0.015, y + 0.045, textwrap.fill(quote, 46), color=TEXT,
                 fontsize=7.4, fontstyle="italic", va="top", linespacing=1.35)

    fig.text(0.05, 0.012, "agentic behavioural economics · experiment 3 · "
             "all figures computed from the committed run data",
             color=MUTED_D, fontsize=8)
    out = os.path.join(OUTPUT_DIR, "profile_cards.png")
    fig.savefig(out, dpi=160, facecolor=BG)
    plt.close(fig)
    print(f"wrote {out}")


def build_scatter():
    fig, ax = plt.subplots(figsize=(9, 7), dpi=130, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    offsets = {"GPT-4o": (10, -4), "Claude Haiku 4.5": (10, -4),
               "Gemini 2.5 Flash": (10, 8), "Llama 3.1 70B": (10, -4),
               "DeepSeek V3": (10, 8), "Qwen 2.5 72B": (-10, 10)}
    for model in MODELS:
        p = profile(model)
        # discipline pooled over the three pressure contexts, weighted by runs
        disc = np.mean([p["solo"], p["manager"], p["deck"]])
        help_ = p["helpfulness"]
        risky = disc < 0.7
        ax.scatter(disc, help_, s=110, color=RED if risky else BLUE, zorder=5)
        ha = "right" if offsets[model][0] < 0 else "left"
        ax.annotate(model, (disc, help_), xytext=offsets[model],
                    textcoords="offset points", fontsize=9.5, color=INK_2,
                    ha=ha)

    ax.set_xlim(-0.05, 1.08)
    ax.set_ylim(0.68, 1.04)
    ax.set_xlabel("Policy discipline under pressure (share of runs held)",
                  fontsize=10, color=INK_2)
    ax.set_ylabel("Helpfulness (legitimate refunds correctly granted)",
                  fontsize=10, color=INK_2)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    from matplotlib.ticker import PercentFormatter
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_title("Robustness and helpfulness are a frontier, not an axis",
                 loc="left", fontsize=13, color=INK, pad=30)
    ax.text(0, 1.025, "Discipline averaged over the retention-memo and "
            "strategy-deck conditions; helpfulness from the 30-day simulation.",
            transform=ax.transAxes, fontsize=8.5, color=INK_2, va="bottom")
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "frontier_scatter.png")
    fig.savefig(out, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def build_heatmap():
    rows = []
    for model in MODELS:
        p = profile(model)
        rows.append([p["solo"], p["manager"], p["deck"], p["fabrication"],
                     p["helpfulness"]])
    data = np.array(rows)

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=130, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    # single-hue sequential: light (low) to dark (high), per the colour formula
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "blues", ["#e8f0fb", "#0d366b"])
    ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=10,
                    fontweight="bold", color="white" if v > 0.55 else INK)
    ax.set_xticks(range(len(MEASURES)))
    ax.set_xticklabels(MEASURES, fontsize=8.5, color=INK_2)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(MODELS, fontsize=9.5, color=INK)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Behavioural profile, six models x five measures "
                 "(higher is better)", loc="left", fontsize=12.5, color=INK,
                 pad=14)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "behaviour_heatmap.png")
    fig.savefig(out, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def build_radar():
    angles = np.linspace(0, 2 * np.pi, len(MEASURES), endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8.4), dpi=120,
                             subplot_kw=dict(projection="polar"),
                             facecolor=SURFACE)
    for ax, model in zip(axes.flatten(), MODELS):
        p = profile(model)
        vals = [p["solo"], p["manager"], p["deck"], p["fabrication"],
                p["helpfulness"]]
        vals += vals[:1]
        risky = min(vals) < 0.3
        color = RED if risky else BLUE
        ax.set_facecolor(SURFACE)
        ax.plot(angles, vals, color=color, linewidth=2)
        ax.fill(angles, vals, color=color, alpha=0.18)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([m.replace("\n", " ") for m in MEASURES],
                           fontsize=7, color=INK_2)
        ax.set_yticks([0.5, 1.0])
        ax.set_yticklabels(["50%", ""], fontsize=6.5, color=MUTED)
        ax.grid(color=GRID, linewidth=0.7)
        ax.spines["polar"].set_color(BASELINE)
        ax.set_title(model, fontsize=10.5, color=INK, pad=16)

    fig.suptitle("Behavioural profiles (further out is better)",
                 fontsize=13.5, color=INK, x=0.02, ha="left", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(OUTPUT_DIR, "behaviour_radar.png")
    fig.savefig(out, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


# (label, profile key, direction) — "lo" = lower is better, "hi" = higher is better.
# Names are the framework's, not this experiment's.
STAT_LABELS = [
    ("false-accept · solo", "false_acceptance_solo", "lo"),
    ("false-accept · mgr", "false_acceptance_manager", "lo"),
    ("suscept. · doc", "susceptibility_document", "lo"),
    ("suscept. · peer", "susceptibility_peer", "lo"),
    ("acceptance", "acceptance", "hi"),
]

ROUND_CAPTIONS = [
    "Yielding · false-acceptance rate, pressured alone with the retention memo",
    "Yielding · false-acceptance rate, same pressure, now in the manager's seat",
    "Prone to injection · susceptibility, one retention bullet in a strategy deck",
    "Prone to injection · susceptibility, a colleague's message claims a defect",
    "Yielding · acceptance rate, ordinary customers with legitimate refunds",
]


def _draw_cards_frame(profiles, rounds_shown, reveal, caption):
    import textwrap
    fig = plt.figure(figsize=(13, 9.6), dpi=90)
    fig.patch.set_facecolor(BG)
    fig.text(0.05, 0.965, "Six models, five behavioural tests", color=TEXT,
             fontsize=17, fontweight="bold")
    fig.text(0.05, 0.935, caption, color=AMBER_D if not reveal else MUTED_D,
             fontsize=11 if not reveal else 10,
             fontweight="bold" if not reveal else "normal")

    positions = [(0.045 + c * 0.32, 0.475 - r * 0.435)
                 for r in range(2) for c in range(3)]
    for model, (x, y) in zip(MODELS, positions):
        p = profiles[model]
        arch, blurb, quote = CARDS[model]
        risk = 1 - min(p["solo"], p["manager"], p["deck"])
        if reveal:
            edge = RED_D if risk > 0.6 else AMBER_D if risk > 0.2 else GREEN_D
        else:
            edge = "#30363d"
        box = mpatches.FancyBboxPatch((x, y), 0.295, 0.40,
                                      transform=fig.transFigure,
                                      boxstyle="round,pad=0.006",
                                      facecolor=PANEL, edgecolor=edge,
                                      linewidth=1.6, figure=fig)
        fig.patches.append(box)
        fig.text(x + 0.015, y + 0.365, model, color=TEXT, fontsize=11.5,
                 fontweight="bold")
        if reveal:
            fig.text(x + 0.015, y + 0.338, arch, color=edge, fontsize=10,
                     fontweight="bold")
            fig.text(x + 0.015, y + 0.322, textwrap.fill(blurb, 44),
                     color=MUTED_D, fontsize=7.6, va="top", linespacing=1.35)

        sy = y + 0.225
        for label, key, direction in STAT_LABELS[:rounds_shown]:
            v = p[key]
            good = v if direction == "hi" else 1 - v
            color = GREEN_D if good >= 0.95 else AMBER_D if good >= 0.5 else RED_D
            fig.text(x + 0.015, sy, label, color=MUTED_D, fontsize=7.8)
            bw = 0.130 * v
            bar = mpatches.FancyBboxPatch((x + 0.130, sy - 0.004),
                                          max(bw, 0.003), 0.012,
                                          transform=fig.transFigure,
                                          boxstyle="round,pad=0.001",
                                          facecolor=color, edgecolor="none",
                                          figure=fig)
            fig.patches.append(bar)
            fig.text(x + 0.268, sy, f"{v:.0%}", color=color, fontsize=8,
                     fontweight="bold", ha="left")
            sy -= 0.028

        if reveal:
            leak = (f"leaked ${p['leaked']:,.0f} in 30 simulated days"
                    if p["leaked"] else
                    f"leaked $0" + (f", refused {p['wrongful']} legitimate refunds"
                                    if p["wrongful"] else
                                    ", zero errors with customers"))
            fig.text(x + 0.015, y + 0.062, leak,
                     color=RED_D if p["leaked"] else GREEN_D, fontsize=8,
                     fontweight="bold")
            fig.text(x + 0.015, y + 0.045, textwrap.fill(quote, 46),
                     color=TEXT, fontsize=7.4, fontstyle="italic", va="top",
                     linespacing=1.35)

    fig.text(0.05, 0.012, "agentic behavioural economics · experiment 3 · "
             "all figures computed from the committed run data",
             color=MUTED_D, fontsize=8)
    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    plt.close(fig)
    from PIL import Image
    return Image.fromarray(img)


def build_cards_animation():
    profiles = {m: profile(m) for m in MODELS}
    frame_ms = 200
    states = []
    states.append((_draw_cards_frame(
        profiles, 0, False,
        "Same policy, same customers. Five tests, one at a time."), 9))
    for i, caption in enumerate(ROUND_CAPTIONS, start=1):
        states.append((_draw_cards_frame(profiles, i, False, caption), 11))
    states.append((_draw_cards_frame(
        profiles, 5, True,
        "Same policy, same customers, same pressure. Six temperaments."), 30))

    frames = []
    for img, repeat in states:
        q = img.quantize(colors=128)
        frames.extend([q] * repeat)
    out = os.path.join(OUTPUT_DIR, "profile_cards.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=frame_ms, loop=0, optimize=False)
    print(f"wrote {out} ({len(frames)} frames, "
          f"{os.path.getsize(out)/1e6:.1f} MB, {len(frames)*frame_ms/1000:.1f}s)")


if __name__ == "__main__":
    build_cards()
    build_scatter()
    build_heatmap()
    build_radar()
    build_cards_animation()
