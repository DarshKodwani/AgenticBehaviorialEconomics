"""Streamlit dashboard for the Bertrand duopoly experiment."""
import os
import json
import glob
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from game_engine import MARGINAL_COST, NASH_PRICE, JOINT_PROFIT_PRICE, compute_stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


@st.cache_data
def load_all_results():
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    files = list(set(f for f in files if "summary" not in f))
    games = {}
    for fp in files:
        with open(fp, "r") as f:
            game = json.load(f)
        game["stats"] = compute_stats(game)
        key = f"{game['model_a']} vs {game['model_b']}"
        games[key] = game
    return games


def smooth(prices, window=5):
    kernel = np.ones(window) / window
    return np.convolve(prices, kernel, mode="same")


def plot_price_race(game, show_raw=True, show_smooth=True):
    prices_a = game["prices_a"]
    prices_b = game["prices_b"]
    model_a = game["model_a"]
    model_b = game["model_b"]
    num_rounds = len(prices_a)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    all_prices = prices_a + prices_b
    y_min = min(min(all_prices), MARGINAL_COST) - 0.15
    y_max = max(max(all_prices), JOINT_PROFIT_PRICE) + 0.25

    ax.axhline(y=JOINT_PROFIT_PRICE, color="#ff6b6b", linestyle="--", linewidth=1.5, alpha=0.7, label="joint-profit benchmark")
    ax.axhline(y=NASH_PRICE, color="#51cf66", linestyle="--", linewidth=1.5, alpha=0.7, label="Nash benchmark")
    ax.axhline(y=MARGINAL_COST, color="#868e96", linestyle=":", linewidth=1, alpha=0.3)

    x = list(range(1, num_rounds + 1))
    color_a = "#339af0"
    color_b = "#ffd43b"

    if show_raw:
        ax.plot(x, prices_a, color=color_a, linewidth=0.8, alpha=0.3)
        ax.plot(x, prices_b, color=color_b, linewidth=0.8, alpha=0.3)

    if show_smooth:
        ax.plot(x, smooth(prices_a), color=color_a, linewidth=2.5, label=model_a)
        ax.plot(x, smooth(prices_b), color=color_b, linewidth=2.5, label=model_b)

    ax.set_xlim(0, num_rounds + 1)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("round", fontsize=12, color="#adb5bd")
    ax.set_ylabel("price ($)", fontsize=12, color="#adb5bd")
    ax.yaxis.set_major_formatter(FormatStrFormatter("$%.2f"))
    ax.set_title(f"{model_a} vs {model_b}", fontsize=16, fontweight="bold", color="white", loc="left")
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#495057")
    ax.spines["bottom"].set_color("#495057")
    ax.legend(fontsize=10, frameon=True, facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

    fig.tight_layout()
    return fig


def plot_collusion_heatmap(games):
    models = sorted(set(
        [g["model_a"] for g in games.values()] +
        [g["model_b"] for g in games.values()]
    ))
    n = len(models)
    matrix = np.full((n, n), np.nan)
    model_idx = {m: i for i, m in enumerate(models)}

    for g in games.values():
        i = model_idx[g["model_a"]]
        j = model_idx[g["model_b"]]
        ci = g.get("stats", {}).get("collusion_index", 0)
        matrix[i][j] = ci
        if g["model_a"] != g["model_b"]:
            matrix[j][i] = ci

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    fig.patch.set_facecolor("#0d1117")

    im = ax.imshow(matrix, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(models, fontsize=10)
    ax.set_title("price-level index by model pair", fontsize=16, fontweight="bold", pad=15, loc="left", color="white")

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i][j]):
                val = matrix[i][j]
                color = "white" if val > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9,
                        color=color, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("price-level index (0 = cost floor, 1 = price cap)", fontsize=10, color="#adb5bd")
    cbar.ax.tick_params(colors="#adb5bd")

    fig.tight_layout()
    return fig


def plot_profit_comparison(games):
    data = []
    for g in games.values():
        if g["model_a"] == g["model_b"]:
            continue
        stats = g.get("stats", {})
        data.append({
            "matchup": f"{g['model_a']}\nvs\n{g['model_b']}",
            "price_level_index": stats.get("price_level_index", stats.get("collusion_index", 0)),
            "avg_price": stats.get("avg_price_last20", 0),
        })

    if not data:
        return None

    df = pd.DataFrame(data).sort_values("price_level_index", ascending=True)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    colors = plt.cm.RdYlGn_r(df["price_level_index"].values)
    bars = ax.barh(range(len(df)), df["price_level_index"], color=colors, edgecolor="none", height=0.7)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["matchup"], fontsize=8)
    ax.set_xlabel("price-level index", fontsize=12, color="#adb5bd")
    ax.set_title("which model pairs finish closest to the joint-profit cap?", fontsize=16, fontweight="bold", loc="left", color="white")
    ax.axvline(x=0.5, color="#868e96", linestyle=":", alpha=0.5)
    ax.set_xlim(0, 1)
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#495057")
    ax.spines["bottom"].set_color("#495057")

    fig.tight_layout()
    return fig


# --- streamlit app ---

st.set_page_config(page_title="AI collusion experiment", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏷️ do AI pricing agents learn to collude?")
st.markdown("*Bertrand duopoly experiment across 7 LLMs · 100 rounds per game · no instruction to collude*")
st.markdown("---")

games = load_all_results()

if not games:
    st.warning("no results found yet. run the experiment first: `python run_experiment.py`")
    st.stop()

# --- tab layout ---
tab1, tab2, tab3, tab4 = st.tabs(["🏁 price race", "🗺️ price-level heatmap", "📊 rankings", "📋 raw data"])

with tab1:
    st.subheader("pick a matchup and watch the price race")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_game = st.selectbox("model pair", list(games.keys()))
    with col2:
        show_raw = st.checkbox("show raw prices", value=True)
    with col3:
        show_smooth = st.checkbox("show smoothed", value=True)

    if selected_game:
        game = games[selected_game]
        fig = plot_price_race(game, show_raw=show_raw, show_smooth=show_smooth)
        st.pyplot(fig)
        plt.close(fig)

        stats = game.get("stats", {})
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("price-level index", f"{stats.get('price_level_index', stats.get('collusion_index', 0)):.2f}",
                     help="0 = at the cost floor, 1 = at the price cap")
        col_b.metric(f"{game['model_a']} avg price (last 20)",
                     f"${stats.get('avg_price_a_last20', 0):.2f}")
        col_c.metric(f"{game['model_b']} avg price (last 20)",
                     f"${stats.get('avg_price_b_last20', 0):.2f}")
        col_d.metric("joint avg price (last 20)",
                     f"${stats.get('avg_price_last20', 0):.2f}")

        # show reasoning in expander
        with st.expander("agent reasoning (last 10 rounds)"):
            reasoning_a = game.get("reasoning_a", [])[-10:]
            reasoning_b = game.get("reasoning_b", [])[-10:]
            prices_a = game["prices_a"][-10:]
            prices_b = game["prices_b"][-10:]
            start_round = len(game["prices_a"]) - 10

            for i, (ra, rb, pa, pb) in enumerate(zip(reasoning_a, reasoning_b, prices_a, prices_b)):
                r = start_round + i + 1
                st.markdown(f"**Round {r}**")
                st.markdown(f"- {game['model_a']} → ${pa:.2f}: _{ra[:200]}_")
                st.markdown(f"- {game['model_b']} → ${pb:.2f}: _{rb[:200]}_")

with tab2:
    st.subheader("price levels across all model pairs")
    fig = plot_collusion_heatmap(games)
    st.pyplot(fig)
    plt.close(fig)

with tab3:
    st.subheader("which pairs finish closest to the joint-profit cap?")
    fig = plot_profit_comparison(games)
    if fig:
        st.pyplot(fig)
        plt.close(fig)

    # summary table
    st.subheader("summary table")
    rows = []
    for g in games.values():
        stats = g.get("stats", {})
        rows.append({
            "model A": g["model_a"],
            "model B": g["model_b"],
            "price-level index": stats.get("price_level_index", stats.get("collusion_index", 0)),
            "avg price (last 20)": stats.get("avg_price_last20", 0),
            "total profit A": stats.get("total_profit_a", 0),
            "total profit B": stats.get("total_profit_b", 0),
        })
    df = pd.DataFrame(rows).sort_values("price-level index", ascending=False)
    st.dataframe(df, width="stretch", hide_index=True)

with tab4:
    st.subheader("raw price data")
    selected = st.selectbox("select game", list(games.keys()), key="raw_select")
    if selected:
        game = games[selected]
        df = pd.DataFrame({
            "round": list(range(1, len(game["prices_a"]) + 1)),
            f"{game['model_a']} price": game["prices_a"],
            f"{game['model_b']} price": game["prices_b"],
        })
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("download CSV", df.to_csv(index=False), f"{selected}.csv", "text/csv")
