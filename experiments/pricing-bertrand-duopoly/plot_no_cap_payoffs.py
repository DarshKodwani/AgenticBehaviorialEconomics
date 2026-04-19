"""Visualise the no-cap profit landscape for the Bertrand duopoly setup.

Creates:
- no_cap_profit_heatmaps.png : Profit for Firm A, Firm B, and joint profit across price pairs
- no_cap_best_response.png   : Best-response curves with Nash and joint-profit markers
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DEMAND = 10.0
OWN_PRICE_EFFECT = 3.0
CROSS_PRICE_EFFECT = 1.5
MARGINAL_COST = 1.0
PRICE_MIN = 1.0
PRICE_MAX = 5.0

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
NO_CAP_RESULT = os.path.join(os.path.dirname(__file__), "results_no_cap", "Gemini_20_Flash_vs_DeepSeek_V3_no_cap.json")


def demand(price_i, price_j):
    return max(BASE_DEMAND - OWN_PRICE_EFFECT * price_i + CROSS_PRICE_EFFECT * price_j, 0.0)


def profit(price_i, price_j):
    return (price_i - MARGINAL_COST) * demand(price_i, price_j)


def best_response(opponent_price):
    # FOC from the current model: 13 - 6 p_i + 1.5 p_j = 0
    return (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST + CROSS_PRICE_EFFECT * opponent_price) / (2 * OWN_PRICE_EFFECT)


def symmetric_nash_price():
    return (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST) / (2 * OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT)


def joint_profit_price():
    return (BASE_DEMAND + (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT) * MARGINAL_COST) / (2 * (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT))


def load_observed_point():
    if not os.path.exists(NO_CAP_RESULT):
        return None
    with open(NO_CAP_RESULT, "r") as f:
        game = json.load(f)
    stats = game.get("stats", {})
    return (
        stats.get("avg_price_a_last20"),
        stats.get("avg_price_b_last20"),
        stats.get("total_profit_a"),
        stats.get("total_profit_b"),
    )


def create_heatmaps(output_path):
    prices = np.linspace(PRICE_MIN, PRICE_MAX, 241)
    A, B = np.meshgrid(prices, prices)

    profit_a = np.vectorize(profit)(A, B)
    profit_b = np.vectorize(profit)(B, A)
    joint_profit = profit_a + profit_b

    observed = load_observed_point()
    p_nash = symmetric_nash_price()
    p_joint = joint_profit_price()

    plt.style.use("dark_background")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), dpi=140)
    fig.patch.set_facecolor("#0d1117")

    panels = [
        (profit_a, "Firm A profit", "viridis"),
        (profit_b, "Firm B profit", "plasma"),
        (joint_profit, "Joint profit", "magma"),
    ]

    for ax, (surface, title, cmap) in zip(axes, panels):
        ax.set_facecolor("#0d1117")
        im = ax.imshow(
            surface,
            origin="lower",
            extent=[PRICE_MIN, PRICE_MAX, PRICE_MIN, PRICE_MAX],
            aspect="auto",
            cmap=cmap,
        )
        ax.set_title(title, fontsize=12, loc="left", color="white")
        ax.set_xlabel("Firm A price", color="#adb5bd")
        ax.set_ylabel("Firm B price", color="#adb5bd")
        ax.tick_params(colors="#adb5bd")

        # Nash point
        ax.scatter([p_nash], [p_nash], marker="x", s=70, color="#51cf66", linewidths=2)
        ax.text(p_nash + 0.05, p_nash + 0.05, "Nash", color="#51cf66", fontsize=9)

        # Joint-profit optimum
        ax.scatter([p_joint], [p_joint], marker="*", s=110, color="#ff6b6b", edgecolors="white", linewidths=0.5)
        ax.text(p_joint + 0.05, p_joint - 0.18, "Joint optimum", color="#ff6b6b", fontsize=9)

        # Observed no-cap run point
        if observed and observed[0] is not None and observed[1] is not None:
            ax.scatter([observed[0]], [observed[1]], marker="o", s=70, color="#ffd43b", edgecolors="black", linewidths=0.5)
            ax.text(observed[0] + 0.05, observed[1] + 0.05, "Observed run", color="#ffd43b", fontsize=9)

        cbar = plt.colorbar(im, ax=ax, shrink=0.85)
        cbar.ax.tick_params(colors="#adb5bd")

    fig.suptitle("No-cap Bertrand payoff landscape", fontsize=16, fontweight="bold", x=0.02, ha="left", y=0.98)
    fig.text(0.02, 0.92, "Heatmaps over Firm A price and Firm B price using the current demand model", fontsize=10, color="#6c757d")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def create_best_response_plot(output_path):
    prices = np.linspace(PRICE_MIN, PRICE_MAX, 241)
    br = np.array([best_response(p) for p in prices])
    p_nash = symmetric_nash_price()
    p_joint = joint_profit_price()
    observed = load_observed_point()

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.5, 6), dpi=140)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # A best response: x = BR_A(p_B), y = p_B
    ax.plot(br, prices, color="#339af0", linewidth=2.5, label="Firm A best response")
    # B best response: x = p_A, y = BR_B(p_A)
    ax.plot(prices, br, color="#ffd43b", linewidth=2.5, label="Firm B best response")
    ax.plot(prices, prices, linestyle="--", color="#868e96", alpha=0.7, label="Equal-price line")

    ax.scatter([p_nash], [p_nash], marker="x", s=80, color="#51cf66", linewidths=2.5, label="Nash point")
    ax.scatter([p_joint], [p_joint], marker="*", s=130, color="#ff6b6b", edgecolors="white", linewidths=0.5, label="Joint-profit optimum")

    if observed and observed[0] is not None and observed[1] is not None:
        ax.scatter([observed[0]], [observed[1]], marker="o", s=70, color="#e599f7", edgecolors="white", linewidths=0.5, label="Observed no-cap run")

    ax.set_xlim(PRICE_MIN, PRICE_MAX)
    ax.set_ylim(PRICE_MIN, PRICE_MAX)
    ax.set_xlabel("Firm A price", color="#adb5bd")
    ax.set_ylabel("Firm B price", color="#adb5bd")
    ax.tick_params(colors="#adb5bd")
    ax.set_title("Best-response geometry", fontsize=15, fontweight="bold", loc="left", color="white")
    ax.legend(frameon=True, facecolor="#161b22", edgecolor="#30363d", fontsize=9)
    fig.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    heatmap_path = os.path.join(OUTPUT_DIR, "no_cap_profit_heatmaps.png")
    best_response_path = os.path.join(OUTPUT_DIR, "no_cap_best_response.png")

    create_heatmaps(heatmap_path)
    create_best_response_plot(best_response_path)

    print(f"Saved: {heatmap_path}")
    print(f"Saved: {best_response_path}")
    print(f"Nash benchmark: {symmetric_nash_price():.3f}")
    print(f"Joint-profit optimum: {joint_profit_price():.3f}")
