"""Point cloud of every contribution decision, with the group average on top.

    python plot_point_cloud.py results/np_visible
    python plot_point_cloud.py results/np_visible --by-model
"""
import argparse
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np

GREY, RED, BLUE, TEAL = "#5F5E5A", "#E24B4A", "#2a78d6", "#0F6E56"
MODEL_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]


def load(folder):
    games = []
    for p in sorted(glob.glob(os.path.join(folder, "game_*.json"))):
        with open(p) as f:
            games.append(json.load(f))
    if not games:
        raise SystemExit(f"no games in {folder}")
    return games


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--by-model", action="store_true")
    args = ap.parse_args()
    games = load(args.folder)
    g0 = games[0]
    phase_len, endow = g0["params"]["phase_len"], g0["params"]["endowment"]
    n_rounds = len(g0["rounds"])
    models = sorted({m for g in games for m in g["seats"].values()})
    rng = np.random.default_rng(0)

    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
    ded_start = 0.5 if g0["order"] == "pn" else phase_len + 0.5
    ded_end = phase_len + 0.5 if g0["order"] == "pn" else n_rounds + 0.5
    ax.axvspan(ded_start, ded_end, color=TEAL, alpha=0.07, lw=0)
    ax.axvline(phase_len + 0.5, color=TEAL, ls="--", lw=1)

    xs, ys, cs = [], [], []
    for g in games:
        for r in g["rounds"]:
            for lab, c in r["contributions"].items():
                if lab in r["flags"]:
                    continue
                xs.append(r["round"] + rng.uniform(-0.33, 0.33))
                ys.append(c + rng.uniform(-0.25, 0.25))
                if args.by_model:
                    cs.append(MODEL_COLOURS[models.index(g["seats"][lab]) % 6])
                else:
                    cs.append(RED if c <= 2 else GREY)
    ax.scatter(xs, ys, s=6, c=cs, alpha=0.35 if not args.by_model else 0.45, lw=0)

    rounds = np.arange(1, n_rounds + 1)
    avg = [np.mean([c for g in games for lab, c in g["rounds"][i]["contributions"].items()
                    if lab not in g["rounds"][i]["flags"]]) for i in range(n_rounds)]
    ax.plot(rounds, avg, color=BLUE, lw=3, solid_capstyle="round", zorder=5)

    top = endow + 2.2
    ax.text((0.5 + phase_len + 0.5) / 2, top - 0.6,
            "No deductions" if g0["order"] == "np" else "Deductions allowed",
            ha="center", color=GREY if g0["order"] == "np" else TEAL, fontsize=11)
    ax.text((phase_len + 0.5 + n_rounds + 0.5) / 2, top - 0.6,
            "Deductions allowed" if g0["order"] == "np" else "No deductions",
            ha="center", color=TEAL if g0["order"] == "np" else GREY, fontsize=11)

    ax.set_xlim(0.4, n_rounds + 0.6)
    ax.set_ylim(-0.8, top)
    ax.set_xticks([1, 5, 10, 15, 20] if n_rounds == 20 else rounds)
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_yticklabels(["0 selfish", "5", "10", "15", "20 all in"])
    ax.set_xlabel("Round")
    ax.set_ylabel(f"Tokens given to the group pot (of {endow})")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", lw=0.8)
    ax.set_axisbelow(True)

    if args.by_model:
        handles = [plt.Line2D([], [], marker="o", ls="", color=MODEL_COLOURS[i], label=m)
                   for i, m in enumerate(models)]
    else:
        handles = [plt.Line2D([], [], marker="o", ls="", color=GREY, label="Contribution"),
                   plt.Line2D([], [], marker="o", ls="", color=RED, label="Free-rider (gave 0-2)")]
    handles.append(plt.Line2D([], [], color=BLUE, lw=3, label="Average"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=len(handles), frameon=False, fontsize=9)
    mock = " (MOCK DATA)" if g0["params"].get("mock") else ""
    ax.set_title(f"{len(games)} games x 6 agents = {len(games) * 6} decisions per round{mock}",
                 loc="left", fontsize=11, color=GREY)

    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out, exist_ok=True)
    name = os.path.basename(os.path.normpath(args.folder)) + ("_by_model" if args.by_model else "")
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(out, f"point_cloud_{name}.{ext}"))
    print(f"saved output/point_cloud_{name}.png/.svg")


if __name__ == "__main__":
    main()
