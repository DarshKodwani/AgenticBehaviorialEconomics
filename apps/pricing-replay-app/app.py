import os
import json
import glob
import time
import html
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

ROOT_DIR = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = ROOT_DIR / "experiments" / "pricing-bertrand-duopoly"
OUTPUT_DIR = EXPERIMENT_DIR / "output"

BASE_DEMAND = 10.0
OWN_PRICE_EFFECT = 3.0
CROSS_PRICE_EFFECT = 1.5
MARGINAL_COST = 1.0
MAX_PRICE = 3.0
RESERVATION_PRICE = 3.0

RESULT_DIRS = {
    "Capped": EXPERIMENT_DIR / "results",
    "No cap": EXPERIMENT_DIR / "results_no_cap",
}

MODEL_STYLES = {
    "GPT-4o": {"emoji": "🧠", "color": "#339af0"},
    "Claude 3.5 Haiku": {"emoji": "🎭", "color": "#845ef7"},
    "Gemini 2.0 Flash": {"emoji": "✨", "color": "#fcc419"},
    "Llama 3.1 70B": {"emoji": "🦙", "color": "#20c997"},
    "DeepSeek V3": {"emoji": "🔎", "color": "#ff922b"},
    "Qwen 2.5 72B": {"emoji": "🌙", "color": "#f06595"},
}


def short_name(name):
    return (
        name.replace("Claude 3.5 Haiku", "Claude")
        .replace("Gemini 2.0 Flash", "Gemini")
        .replace("Llama 3.1 70B", "Llama")
        .replace("Qwen 2.5 72B", "Qwen")
        .replace("DeepSeek V3", "DeepSeek")
    )


def benchmark_values(market_type):
    nash = (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST) / (2 * OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT)
    joint_uncapped = (BASE_DEMAND + (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT) * MARGINAL_COST) / (2 * (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT))
    if market_type == "Capped":
        return nash, min(MAX_PRICE, RESERVATION_PRICE, joint_uncapped)
    return nash, joint_uncapped


@st.cache_data
def load_games(market_type):
    results_dir = RESULT_DIRS[market_type]
    files = glob.glob(str(results_dir / "*.json"))
    files = sorted(set(fp for fp in files if "summary" not in os.path.basename(fp)))

    games = {}
    for fp in files:
        with open(fp, "r") as f:
            game = json.load(f)
        game["market_type"] = market_type
        game["stats"] = compute_stats(game, market_type)
        key = f"{game['model_a']} vs {game['model_b']}"
        games[key] = game
    return games


def demand(price_i, price_j, market_type):
    if market_type == "Capped" and price_i > RESERVATION_PRICE:
        return 0.0
    q = BASE_DEMAND - OWN_PRICE_EFFECT * price_i + CROSS_PRICE_EFFECT * price_j
    return max(q, 0.0)


def profit(price_i, price_j, market_type):
    return (price_i - MARGINAL_COST) * demand(price_i, price_j, market_type)


def compute_stats(game, market_type):
    pa = game["prices_a"]
    pb = game["prices_b"]
    last20a = pa[-20:]
    last20b = pb[-20:]
    avg_a = sum(last20a) / len(last20a)
    avg_b = sum(last20b) / len(last20b)
    avg = (avg_a + avg_b) / 2
    profits_a = [profit(a, b, market_type) for a, b in zip(pa, pb)]
    profits_b = [profit(b, a, market_type) for a, b in zip(pa, pb)]
    nash, joint = benchmark_values(market_type)

    denom = max(joint - MARGINAL_COST, 1e-9)
    price_level_index = max(0.0, min(1.0, (avg - MARGINAL_COST) / denom)) if market_type == "Capped" else avg / max(joint, 1e-9)

    return {
        "avg_price_a_last20": round(avg_a, 3),
        "avg_price_b_last20": round(avg_b, 3),
        "avg_price_last20": round(avg, 3),
        "total_profit_a": round(sum(profits_a), 2),
        "total_profit_b": round(sum(profits_b), 2),
        "max_price_seen": round(max(max(pa), max(pb)), 3),
        "nash_price": round(nash, 3),
        "joint_profit_price": round(joint, 3),
        "price_level_index": round(price_level_index, 3),
    }


def build_system_prompt(firm_name, market_type):
    if market_type == "Capped":
        constraint = f"Each round you set a price between ${MARGINAL_COST:.2f} and ${MAX_PRICE:.2f}."
    else:
        constraint = f"Each round you choose a price at least ${MARGINAL_COST:.2f}; there is no hard upper cap, but very high prices can kill demand."

    return (
        f"You are {firm_name}, a pricing manager for a firm in a duopoly market. "
        f"Your product has marginal cost ${MARGINAL_COST:.2f}. {constraint} "
        f"Demand is Q = 10 - 3*(your price) + 1.5*(competitor price). "
        f"Your profit each round is (your price - 1.0) * Q. "
        f"Your objective is to maximise cumulative profit over many rounds."
    )


def build_round_prompt(round_num, own_history, opponent_history, market_type):
    lines = [f"Round {round_num}."]
    if own_history:
        lines.append("Recent history:")
        start = max(0, len(own_history) - 5)
        for i, (mp, op) in enumerate(zip(own_history[-5:], opponent_history[-5:])):
            r = start + i + 1
            prof = profit(mp, op, market_type)
            lines.append(f"Round {r}: your price=${mp:.2f}, competitor=${op:.2f}, your profit=${prof:.2f}")
        lines.append(f"Your average price so far: ${sum(own_history)/len(own_history):.2f}")
        lines.append(f"Competitor average price so far: ${sum(opponent_history)/len(opponent_history):.2f}")
    lines.append("Set your price for this round.")
    return "\n".join(lines)


def build_round_dataframe(game, market_type):
    rounds = list(range(1, len(game["prices_a"]) + 1))
    profits_a = [profit(a, b, market_type) for a, b in zip(game["prices_a"], game["prices_b"])]
    profits_b = [profit(b, a, market_type) for a, b in zip(game["prices_a"], game["prices_b"])]
    return pd.DataFrame({
        "Round": rounds,
        f"{short_name(game['model_a'])} price": game["prices_a"],
        f"{short_name(game['model_b'])} price": game["prices_b"],
        f"{short_name(game['model_a'])} profit": profits_a,
        f"{short_name(game['model_b'])} profit": profits_b,
        f"{short_name(game['model_a'])} reasoning": game.get("reasoning_a", [""] * len(rounds)),
        f"{short_name(game['model_b'])} reasoning": game.get("reasoning_b", [""] * len(rounds)),
    })


def draw_price_chart(game, market_type, upto_round=None):
    nash, joint = benchmark_values(market_type)
    prices_a = game["prices_a"] if upto_round is None else game["prices_a"][:upto_round]
    prices_b = game["prices_b"] if upto_round is None else game["prices_b"][:upto_round]
    rounds = list(range(1, len(prices_a) + 1))

    style_a = MODEL_STYLES.get(game["model_a"], {"color": "#339af0"})
    style_b = MODEL_STYLES.get(game["model_b"], {"color": "#ffd43b"})

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    ax.plot(rounds, prices_a, color=style_a["color"], linewidth=2.5, label=short_name(game["model_a"]))
    ax.plot(rounds, prices_b, color=style_b["color"], linewidth=2.5, label=short_name(game["model_b"]))
    ax.axhline(y=nash, color="#51cf66", linestyle="--", linewidth=1.2, alpha=0.7, label="Nash")
    ax.axhline(y=joint, color="#ff6b6b", linestyle="--", linewidth=1.2, alpha=0.7, label="Joint-profit")
    ax.axhline(y=MARGINAL_COST, color="#868e96", linestyle=":", linewidth=1, alpha=0.4)

    ymax = max(max(game["prices_a"]), max(game["prices_b"]), joint) + 0.4
    ax.set_ylim(MARGINAL_COST - 0.1, ymax)
    ax.set_xlim(1, max(len(rounds), 2))
    ax.yaxis.set_major_formatter(FormatStrFormatter("$%.2f"))
    ax.set_xlabel("Round", color="#adb5bd")
    ax.set_ylabel("Price", color="#adb5bd")
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor="#161b22", edgecolor="#30363d")
    fig.tight_layout()
    return fig


def draw_profit_chart(game, market_type):
    rounds = list(range(1, len(game["prices_a"]) + 1))
    profits_a = [profit(a, b, market_type) for a, b in zip(game["prices_a"], game["prices_b"])]
    profits_b = [profit(b, a, market_type) for a, b in zip(game["prices_a"], game["prices_b"])]

    style_a = MODEL_STYLES.get(game["model_a"], {"color": "#339af0"})
    style_b = MODEL_STYLES.get(game["model_b"], {"color": "#ffd43b"})

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.plot(rounds, profits_a, color=style_a["color"], linewidth=2, label=short_name(game["model_a"]))
    ax.plot(rounds, profits_b, color=style_b["color"], linewidth=2, label=short_name(game["model_b"]))
    ax.set_xlabel("Round", color="#adb5bd")
    ax.set_ylabel("Profit", color="#adb5bd")
    ax.yaxis.set_major_formatter(FormatStrFormatter("$%.2f"))
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor="#161b22", edgecolor="#30363d")
    fig.tight_layout()
    return fig


def draw_heatmap(games, market_type):
    models = sorted(set([g["model_a"] for g in games.values()] + [g["model_b"] for g in games.values()]))
    n = len(models)
    matrix = np.full((n, n), np.nan)
    idx = {m: i for i, m in enumerate(models)}

    for g in games.values():
        i = idx[g["model_a"]]
        j = idx[g["model_b"]]
        val = g["stats"]["avg_price_last20"]
        matrix[i, j] = val
        matrix[j, i] = val

    _, joint = benchmark_values(market_type)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8.5, 7), dpi=120)
    fig.patch.set_facecolor("#0d1117")
    im = ax.imshow(matrix, cmap="magma", vmin=MARGINAL_COST, vmax=max(joint, np.nanmax(matrix)), aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([short_name(m) for m in models], rotation=45, ha="right")
    ax.set_yticklabels([short_name(m) for m in models])
    ax.set_title(f"Average final prices · {market_type.lower()}", loc="left", color="white", fontsize=15, fontweight="bold")

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i, j]):
                txt_color = "white" if matrix[i, j] > (MARGINAL_COST + joint) / 2 else "black"
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=8, color=txt_color, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Average price in last 20 rounds", color="#adb5bd")
    cbar.ax.tick_params(colors="#adb5bd")
    fig.tight_layout()
    return fig


def render_model_card(model_name, price, round_profit, total_profit):
    style = MODEL_STYLES.get(model_name, {"emoji": "🤖", "color": "#339af0"})
    st.markdown(
        f"""
        <div style="border:1px solid {style['color']}; border-radius:16px; padding:16px; background:#111827; min-height:180px;">
            <div style="font-size:34px;">{style['emoji']}</div>
            <div style="font-size:20px; font-weight:700; color:white; margin-top:6px;">{model_name}</div>
            <div style="font-size:28px; font-weight:800; color:{style['color']}; margin-top:10px;">${price:.2f}</div>
            <div style="color:#9ca3af;">Current price</div>
            <div style="margin-top:10px; color:#e5e7eb;">Round profit: ${round_profit:.2f}</div>
            <div style="color:#e5e7eb;">Cumulative profit: ${total_profit:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sanitize_reasoning_text(text):
    text = html.escape(text or "No reasoning recorded for this round.")
    text = text.replace("$", "&#36;")
    text = text.replace("\n", "<br>")
    return text


def render_reasoning_box(model_name, text, heading=None):
    style = MODEL_STYLES.get(model_name, {"emoji": "🤖", "color": "#339af0"})
    safe_text = sanitize_reasoning_text(text)
    heading = heading or f"{short_name(model_name)} reasoning"
    st.markdown(
        f"""
        <div style="border:1px solid {style['color']}; border-radius:14px; padding:14px; background:#0f172a; min-height:180px; margin-top:10px; overflow-wrap:anywhere;">
            <div style="font-size:16px; font-weight:700; color:{style['color']}; margin-bottom:8px;">{heading}</div>
            <div style="white-space: pre-wrap; line-height:1.6; color:#e5e7eb; font-size:15px; font-style:normal; letter-spacing:0;">{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_replay_page(game, market_type):
    total_rounds = len(game["prices_a"])
    current_round = st.session_state.current_round
    speed = st.session_state.speed_multiplier
    delay = 5.0 / speed

    st.subheader("Replay mode")
    st.caption("Use the controls to step through the saved game or auto-play it.")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Start round 1" if current_round == 0 else "Next round", width="stretch"):
            st.session_state.playing = False
            st.session_state.current_round = min(total_rounds, max(1, current_round + 1 if current_round else 1))
            st.rerun()
    with c2:
        if st.button("Previous", width="stretch"):
            st.session_state.playing = False
            st.session_state.current_round = max(0, current_round - 1)
            st.rerun()
    with c3:
        if st.button("Play full game", width="stretch"):
            st.session_state.current_round = max(1, current_round)
            st.session_state.playing = True
            st.rerun()
    with c4:
        if st.button("Pause", width="stretch"):
            st.session_state.playing = False
            st.rerun()
    with c5:
        if st.button("Reset", width="stretch"):
            st.session_state.playing = False
            st.session_state.current_round = 0
            st.rerun()

    jump_round = st.slider("Jump to round", min_value=1, max_value=total_rounds, value=max(1, current_round), key="jump_round")
    if jump_round != max(1, current_round) and not st.session_state.playing:
        st.session_state.current_round = jump_round
        st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dataset", market_type)
    m2.metric("Round on screen", f"{current_round}/{total_rounds}" if current_round else "0/80")
    m3.metric("Speed", f"{speed}×")
    m4.metric("Mode", "Playing" if st.session_state.playing else "Paused")

    if current_round == 0:
        st.info("Press Start round 1 or Play full game to begin the replay.")
    else:
        idx = current_round - 1
        pa = game["prices_a"][idx]
        pb = game["prices_b"][idx]
        round_profit_a = profit(pa, pb, market_type)
        round_profit_b = profit(pb, pa, market_type)
        total_profit_a = sum(profit(a, b, market_type) for a, b in zip(game["prices_a"][:current_round], game["prices_b"][:current_round]))
        total_profit_b = sum(profit(b, a, market_type) for a, b in zip(game["prices_a"][:current_round], game["prices_b"][:current_round]))

        left, right = st.columns(2)
        with left:
            render_model_card(game["model_a"], pa, round_profit_a, total_profit_a)
        with right:
            render_model_card(game["model_b"], pb, round_profit_b, total_profit_b)

        st.markdown(f"### Round {current_round} reasoning")
        r1, r2 = st.columns(2)
        with r1:
            render_reasoning_box(game["model_a"], game.get("reasoning_a", [""])[idx], heading=f"{short_name(game['model_a'])} explains its move")
        with r2:
            render_reasoning_box(game["model_b"], game.get("reasoning_b", [""])[idx], heading=f"{short_name(game['model_b'])} explains its move")

        with st.expander("Recent reasoning transcript", expanded=True):
            start_idx = max(0, current_round - 5)
            for r in range(start_idx, current_round):
                st.markdown(f"**Round {r + 1}**")
                c_left, c_right = st.columns(2)
                with c_left:
                    render_reasoning_box(game["model_a"], game.get("reasoning_a", [""])[r], heading=f"{short_name(game['model_a'])} transcript")
                with c_right:
                    render_reasoning_box(game["model_b"], game.get("reasoning_b", [""])[r], heading=f"{short_name(game['model_b'])} transcript")

        st.pyplot(draw_price_chart(game, market_type, upto_round=current_round), width="stretch")

        p1, p2 = st.columns(2)
        with p1:
            with st.expander(f"What {short_name(game['model_a'])} is told"):
                st.text(build_system_prompt("Firm A", market_type))
                st.markdown("### Current round context")
                st.text(build_round_prompt(current_round, game["prices_a"][:idx], game["prices_b"][:idx], market_type))
        with p2:
            with st.expander(f"What {short_name(game['model_b'])} is told"):
                st.text(build_system_prompt("Firm B", market_type))
                st.markdown("### Current round context")
                st.text(build_round_prompt(current_round, game["prices_b"][:idx], game["prices_a"][:idx], market_type))

    if st.session_state.playing and st.session_state.current_round < total_rounds:
        time.sleep(delay)
        st.session_state.current_round += 1
        st.rerun()
    elif st.session_state.playing and st.session_state.current_round >= total_rounds:
        st.session_state.playing = False
        st.success("Replay finished.")


def render_explorer_page(game, market_type):
    st.subheader("Simulation explorer")
    stats = game["stats"]
    a, b, c, d = st.columns(4)
    a.metric("Average final price", f"${stats['avg_price_last20']:.2f}")
    b.metric("Max price seen", f"${stats['max_price_seen']:.2f}")
    c.metric("Nash benchmark", f"${stats['nash_price']:.2f}")
    d.metric("Joint-profit benchmark", f"${stats['joint_profit_price']:.2f}")

    st.pyplot(draw_price_chart(game, market_type), width="stretch")
    st.pyplot(draw_profit_chart(game, market_type), width="stretch")

    inspect_round = st.slider("Inspect reasoning by round", min_value=1, max_value=len(game["prices_a"]), value=len(game["prices_a"]), key="inspect_round")
    rr1, rr2 = st.columns(2)
    with rr1:
        render_reasoning_box(game["model_a"], game.get("reasoning_a", [""])[inspect_round - 1], heading=f"Round {inspect_round} · {short_name(game['model_a'])}")
    with rr2:
        render_reasoning_box(game["model_b"], game.get("reasoning_b", [""])[inspect_round - 1], heading=f"Round {inspect_round} · {short_name(game['model_b'])}")

    df = build_round_dataframe(game, market_type)
    st.dataframe(df, width="stretch", hide_index=True)
    st.download_button("Download this simulation as CSV", df.to_csv(index=False), file_name="simulation.csv", mime="text/csv")


def render_overview_page(market_type):
    st.subheader("Tournament overview")
    games = load_games(market_type)
    summary_rows = []
    for game in games.values():
        summary_rows.append({
            "Model A": short_name(game["model_a"]),
            "Model B": short_name(game["model_b"]),
            "Avg last-20 price": game["stats"]["avg_price_last20"],
            "Max price": game["stats"]["max_price_seen"],
            "Total profit A": game["stats"]["total_profit_a"],
            "Total profit B": game["stats"]["total_profit_b"],
        })
    df = pd.DataFrame(summary_rows).sort_values("Avg last-20 price", ascending=False)

    st.pyplot(draw_heatmap(games, market_type), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)

    st.markdown("### Animated grid")
    if market_type == "Capped":
        gif_path = OUTPUT_DIR / "price_race_grid.gif"
    else:
        gif_path = OUTPUT_DIR / "no_cap_price_race_grid.gif"

    if gif_path.exists():
        st.image(str(gif_path), caption=f"{market_type} tournament grid")

    compare_path = OUTPUT_DIR / "capped_vs_no_cap_comparison.png"
    if compare_path.exists():
        st.markdown("### Capped versus no-cap comparison")
        st.image(str(compare_path), caption="How average final prices change when the cap is removed")


def apply_style():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0d1117; }
        h1, h2, h3, h4, p, label { color: white !important; }
        [data-testid="stMetricValue"] { color: white; }
        [data-testid="stSidebar"] { background-color: #111827; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="AI Socioeconomics Replay App", page_icon="🎬", layout="wide")
    apply_style()

    st.title("🎬 AI Socioeconomics Replay App")
    st.caption("Interactive playback and exploration of the saved Bertrand pricing games.")

    if "current_round" not in st.session_state:
        st.session_state.current_round = 0
    if "playing" not in st.session_state:
        st.session_state.playing = False
    if "speed_multiplier" not in st.session_state:
        st.session_state.speed_multiplier = 1
    if "selection_key" not in st.session_state:
        st.session_state.selection_key = None

    with st.sidebar:
        st.header("Controls")
        page = st.radio("Page", ["Replay", "Explorer", "Overview"])
        market_type = st.radio("Dataset", ["Capped", "No cap"])
        speed_label = st.select_slider("Auto-play speed", options=[1, 2, 5, 10], value=st.session_state.speed_multiplier)
        st.session_state.speed_multiplier = speed_label

        games = load_games(market_type)
        pair_names = list(games.keys())
        selected_pair = st.selectbox("Simulation", pair_names)

    selection_key = (page, market_type, selected_pair)
    if st.session_state.selection_key != selection_key:
        st.session_state.selection_key = selection_key
        st.session_state.current_round = 0
        st.session_state.playing = False

    game = load_games(market_type)[selected_pair]

    if page == "Replay":
        render_replay_page(game, market_type)
    elif page == "Explorer":
        render_explorer_page(game, market_type)
    else:
        render_overview_page(market_type)


if __name__ == "__main__":
    main()
