"""Create a direct comparison figure for capped vs no-cap Bertrand runs."""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(__file__)
CAPPED_SUMMARY = os.path.join(BASE_DIR, "results", "summary.json")
NO_CAP_SUMMARY = os.path.join(BASE_DIR, "results_no_cap", "summary.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "capped_vs_no_cap_comparison.png")


def load_summary(path):
    with open(path, "r") as f:
        return json.load(f)


def short_name(label):
    return (
        label.replace("Claude 3.5 Haiku", "Claude")
        .replace("Gemini 2.0 Flash", "Gemini")
        .replace("Llama 3.1 70B", "Llama")
        .replace("Qwen 2.5 72B", "Qwen")
        .replace("DeepSeek V3", "DeepSeek")
    )


def main():
    capped = load_summary(CAPPED_SUMMARY)
    no_cap = load_summary(NO_CAP_SUMMARY)

    capped_map = {(r["model_a"], r["model_b"]): r for r in capped}
    no_cap_map = {(r["model_a"], r["model_b"]): r for r in no_cap}

    rows = []
    for pair, c in capped_map.items():
        if pair not in no_cap_map:
            continue
        n = no_cap_map[pair]
        label = f"{short_name(pair[0])} vs {short_name(pair[1])}"
        capped_avg = c["stats"]["avg_price_last20"]
        nocap_avg = n["stats"]["avg_price_last20"]
        rows.append({
            "pair": pair,
            "label": label,
            "capped_avg": capped_avg,
            "nocap_avg": nocap_avg,
            "delta": nocap_avg - capped_avg,
            "nocap_max": n["stats"].get("max_price_seen", nocap_avg),
        })

    rows.sort(key=lambda r: r["delta"], reverse=True)

    x = [r["capped_avg"] for r in rows]
    y = [r["nocap_avg"] for r in rows]
    labels = [r["label"] for r in rows]
    deltas = [r["delta"] for r in rows]

    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=140)
    fig.patch.set_facecolor("#0d1117")
    ax1.set_facecolor("#0d1117")
    ax2.set_facecolor("#0d1117")

    # Scatter comparison
    ax1.scatter(x, y, s=75, color="#339af0", alpha=0.9, edgecolors="white", linewidths=0.5)
    ax1.plot([1.8, 5.8], [1.8, 5.8], linestyle="--", color="#868e96", alpha=0.8)
    ax1.axvline(3.0, linestyle=":", color="#ff6b6b", alpha=0.6)
    ax1.axhline(3.833, linestyle=":", color="#51cf66", alpha=0.6)

    for i, row in enumerate(rows):
        if row["delta"] > 0.6 or row["nocap_avg"] > 3.7 or row["label"] in ["Gemini vs DeepSeek", "GPT-4o vs Llama"]:
            ax1.text(row["capped_avg"] + 0.03, row["nocap_avg"] + 0.03, row["label"], fontsize=8, color="#adb5bd")

    ax1.set_title("Average end-of-game price: capped vs no-cap", loc="left", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Capped run avg price, last 20 rounds", color="#adb5bd")
    ax1.set_ylabel("No-cap run avg price, last 20 rounds", color="#adb5bd")
    ax1.tick_params(colors="#adb5bd")
    ax1.text(3.02, 5.55, "old hard cap", color="#ff6b6b", fontsize=8, rotation=90, va="top")
    ax1.text(1.85, 3.86, "uncapped joint optimum", color="#51cf66", fontsize=8, va="bottom")

    # Delta bar chart
    ypos = np.arange(len(rows))
    colors = ["#ff6b6b" if d > 0.5 else ("#ffd43b" if d > 0.1 else "#51cf66") for d in deltas]
    ax2.barh(ypos, deltas, color=colors, alpha=0.9)
    ax2.set_yticks(ypos)
    ax2.set_yticklabels(labels, fontsize=8)
    ax2.invert_yaxis()
    ax2.axvline(0, color="#868e96", linestyle="--", alpha=0.7)
    ax2.set_title("How much prices rise when the cap is removed", loc="left", fontsize=14, fontweight="bold")
    ax2.set_xlabel("No-cap avg price minus capped avg price", color="#adb5bd")
    ax2.tick_params(colors="#adb5bd")

    for y0, d in zip(ypos, deltas):
        ax2.text(d + (0.03 if d >= 0 else -0.03), y0, f"{d:+.2f}", va="center", ha="left" if d >= 0 else "right", fontsize=8, color="#adb5bd")

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#495057")
        ax.spines["bottom"].set_color("#495057")

    fig.suptitle("Removing the cap changes some pairings a lot — but not all of them", fontsize=17, fontweight="bold", x=0.02, ha="left", y=0.98)
    fig.text(0.02, 0.92, "Same 17 model matchups, comparing the original capped market to the no-cap rerun", fontsize=10, color="#6c757d")

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.savefig(OUTPUT_PATH, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
