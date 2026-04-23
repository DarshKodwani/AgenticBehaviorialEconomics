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
import matplotlib.patches as mpatches

ROOT_DIR = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = ROOT_DIR / "experiments" / "iterated-prisoners-dilemma"
OUTPUT_DIR = EXPERIMENT_DIR / "output"

PAYOFFS = {("C", "C"): (3, 3), ("C", "D"): (0, 5), ("D", "C"): (5, 0), ("D", "D"): (1, 1)}

RESULT_DIRS = {
    "Known horizon": EXPERIMENT_DIR / "results",
    "Hidden horizon": EXPERIMENT_DIR / "results_hidden",
}

MODEL_STYLES = {
    "GPT-4o":          {"emoji": "🧠", "color": "#339af0"},
    "Claude 3.5 Haiku":{"emoji": "🎭", "color": "#845ef7"},
    "Gemini 2.0 Flash":{"emoji": "✨", "color": "#fcc419"},
    "Llama 3.1 70B":   {"emoji": "🦙", "color": "#20c997"},
    "DeepSeek V3":     {"emoji": "🔎", "color": "#ff922b"},
    "Qwen 2.5 72B":    {"emoji": "🌙", "color": "#f06595"},
}

COOP_COLOR   = "#1ed760"
DEFECT_COLOR = "#ff2d55"
BG_COLOR     = "#0d1117"
PANEL_COLOR  = "#111827"


def short_name(name):
    return (
        name.replace("Claude 3.5 Haiku", "Claude")
            .replace("Gemini 2.0 Flash", "Gemini")
            .replace("Llama 3.1 70B",    "Llama")
            .replace("Qwen 2.5 72B",     "Qwen")
            .replace("DeepSeek V3",      "DeepSeek")
    )


def action_to_int(a):
    return 1 if a == "C" else 0


def score(action_a, action_b):
    return PAYOFFS.get((action_a, action_b), (0, 0))


@st.cache_data
def load_games(dataset):
    results_dir = RESULT_DIRS[dataset]
    files = sorted(glob.glob(str(results_dir / "*.json")))
    files = [f for f in files if "summary" not in os.path.basename(f)]

    games = {}
    for fp in files:
        with open(fp) as f:
            game = json.load(f)
        game["dataset"] = dataset
        game["stats"] = compute_stats(game)
        key = f"{game['model_a']} vs {game['model_b']}"
        games[key] = game
    return games


def compute_stats(game):
    aa = game["actions_a"]
    ab = game["actions_b"]
    n = len(aa)

    points_a = sum(score(a, b)[0] for a, b in zip(aa, ab))
    points_b = sum(score(a, b)[1] for a, b in zip(aa, ab))

    first_defect_a = next((i + 1 for i, a in enumerate(aa) if a == "D"), None)
    first_defect_b = next((i + 1 for i, a in enumerate(ab) if a == "D"), None)

    if first_defect_a is not None and first_defect_b is not None:
        first_defect = min(first_defect_a, first_defect_b)
        initiator = game["model_a"] if first_defect_a <= first_defect_b else game["model_b"]
    elif first_defect_a is not None:
        first_defect = first_defect_a
        initiator = game["model_a"]
    elif first_defect_b is not None:
        first_defect = first_defect_b
        initiator = game["model_b"]
    else:
        first_defect = None
        initiator = None

    mutual_coop = sum(1 for a, b in zip(aa, ab) if a == "C" and b == "C")

    return {
        "points_a": points_a,
        "points_b": points_b,
        "coop_rate_a": round(aa.count("C") / n, 3),
        "coop_rate_b": round(ab.count("C") / n, 3),
        "mutual_coop_rate": round(mutual_coop / n, 3),
        "defects_a": aa.count("D"),
        "defects_b": ab.count("D"),
        "first_defect_round": first_defect,
        "initiator": initiator,
        "rounds": n,
    }


def build_round_dataframe(game):
    aa, ab = game["actions_a"], game["actions_b"]
    rounds = list(range(1, len(aa) + 1))
    pts = [score(a, b) for a, b in zip(aa, ab)]
    cum_a, cum_b, running_a, running_b = [], [], 0, 0
    for pa, pb in pts:
        running_a += pa
        running_b += pb
        cum_a.append(running_a)
        cum_b.append(running_b)

    ra = game.get("reasoning_a", [""] * len(rounds))
    rb = game.get("reasoning_b", [""] * len(rounds))

    return pd.DataFrame({
        "Round":                               rounds,
        f"{short_name(game['model_a'])} action": aa,
        f"{short_name(game['model_b'])} action": ab,
        f"{short_name(game['model_a'])} points":  [p[0] for p in pts],
        f"{short_name(game['model_b'])} points":  [p[1] for p in pts],
        f"{short_name(game['model_a'])} cumulative": cum_a,
        f"{short_name(game['model_b'])} cumulative": cum_b,
        f"{short_name(game['model_a'])} reasoning":  ra,
        f"{short_name(game['model_b'])} reasoning":  rb,
    })


def draw_ring_chart(game, upto_round=None):
    """Single-ring polar clock for one matchup. Clockwise from 12 o'clock."""
    total_rounds = len(game["actions_a"])
    aa = game["actions_a"] if upto_round is None else game["actions_a"][:upto_round]
    ab = game["actions_b"] if upto_round is None else game["actions_b"][:upto_round]
    played = len(aa)

    style_a = MODEL_STYLES.get(game["model_a"], {"color": "#339af0"})
    style_b = MODEL_STYLES.get(game["model_b"], {"color": "#ffd43b"})

    BG      = "#080808"
    SUBTLE  = "#1a1a1a"
    MUTED   = "#505050"
    TEXT    = "#e8e8e8"
    N_PTS   = 800
    RING_W  = 0.32
    GAP     = 0.06
    R0      = 1.8

    # outer ring = model_b, inner ring = model_a
    rings = [
        (game["model_a"], aa, style_a["color"], R0),
        (game["model_b"], ab, style_b["color"], R0 + RING_W + GAP),
    ]

    fig = plt.figure(figsize=(7, 7.8), dpi=120)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.78], projection="polar")
    ax.set_facecolor(BG)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)

    t_full = np.linspace(0, 2 * np.pi, 600)
    ax.fill_between(t_full, 0, R0 - 0.08, color="#0d0d0d", linewidth=0, zorder=0)

    for model_name, actions, model_color, r_in in rings:
        r_out = r_in + RING_W

        # draw each round as a thin arc segment coloured green/red
        for i, act in enumerate(actions):
            t_start = (i / total_rounds) * 2 * np.pi
            t_end   = ((i + 1) / total_rounds) * 2 * np.pi
            seg_pts = max(4, int(N_PTS / total_rounds) + 1)
            t_seg   = np.linspace(t_start, t_end, seg_pts)
            col     = COOP_COLOR if act == "C" else DEFECT_COLOR
            alpha   = 0.88
            ax.fill_between(t_seg, r_in, r_out, color=col, alpha=alpha, linewidth=0)

        # grey arc for unplayed rounds
        if played < total_rounds:
            t_start = (played / total_rounds) * 2 * np.pi
            t_seg   = np.linspace(t_start, 2 * np.pi, max(6, N_PTS - played))
            ax.fill_between(t_seg, r_in, r_out, color="#222222", linewidth=0)

        ax.plot(t_full, np.full_like(t_full, r_out), color=SUBTLE, linewidth=0.5, zorder=4)

        # label on the outer edge
        label_r = r_out + 0.12
        ax.text(np.pi / 2, label_r,
                short_name(model_name),
                color=model_color, fontsize=8.5, fontweight="bold",
                ha="center", va="center", rotation=0,
                rotation_mode="anchor")

    # finish-line tick (round 100 / top)
    r_outer = R0 + 2 * (RING_W + GAP)
    ax.plot([0, 0], [R0 - 0.4, r_outer + 0.05], color=MUTED, linewidth=1.0, zorder=5)

    # quarter-round ticks
    for frac_ref in [0.25, 0.50, 0.75]:
        theta_t = frac_ref * 2 * np.pi
        ax.plot([theta_t, theta_t], [R0 - 0.3, R0 - 0.12],
                color=MUTED, linewidth=0.8, alpha=0.5)

    # centre stat
    CY = 0.47
    coop_rounds = sum(1 for a, b in zip(aa, ab) if a == "C" and b == "C")
    fig.text(0.5, CY + 0.015, str(coop_rounds),
             color=TEXT, fontsize=46, fontweight="bold",
             ha="center", va="center", zorder=20)
    fig.text(0.5, CY - 0.032,
             f"mutual coop rounds / {played}",
             color="#6a6a6a", fontsize=9, ha="center", va="center",
             zorder=20, fontstyle="italic")

    ax.set_rticks([])
    ax.set_xticks([])
    ax.spines["polar"].set_visible(False)
    ax.grid(False)
    ax.set_ylim(0, r_outer + 0.3)

    ma = short_name(game["model_a"])
    mb = short_name(game["model_b"])
    title = f"{ma} × {mb}" if game["model_a"] != game["model_b"] else f"{ma} × self"
    fig.text(0.5, 0.955, title,
             color=TEXT, fontsize=16, fontweight="bold", ha="center", va="center")
    fig.text(0.5, 0.920,
             f"{total_rounds} rounds · clockwise from 12",
             color=MUTED, fontsize=9.5, ha="center", va="center")

    # legend
    for xf, col, lbl in [(0.34, COOP_COLOR, "Cooperate"), (0.55, DEFECT_COLOR, "Defect")]:
        fig.text(xf,         0.042, "■", color=col,  fontsize=12, va="center")
        fig.text(xf + 0.020, 0.042, lbl, color=TEXT, fontsize=10, va="center")

    fig.subplots_adjust(top=0.96, bottom=0.06, left=0.05, right=0.95)
    return fig


def draw_defection_heatmap(games):
    all_models = sorted(set(
        m for g in games.values() for m in [g["model_a"], g["model_b"]]
    ))
    n = len(all_models)
    idx = {m: i for i, m in enumerate(all_models)}
    matrix = np.full((n, n), np.nan)

    for g in games.values():
        i, j = idx[g["model_a"]], idx[g["model_b"]]
        # cell = round of first defection (or 101 = never)
        fd = g["stats"]["first_defect_round"]
        val = fd if fd is not None else 101
        matrix[i, j] = val
        matrix[j, i] = val

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8.5, 7), dpi=120)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    cmap = plt.cm.RdYlGn
    im = ax.imshow(matrix, cmap=cmap, vmin=90, vmax=101, aspect="auto")

    labels = [short_name(m) for m in all_models]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", color="white")
    ax.set_yticklabels(labels, color="white")
    ax.set_title("First defection round (green = never defected, red = early defection)",
                 loc="left", color="white", fontsize=12, fontweight="bold")

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i, j]):
                label = "Never" if matrix[i, j] == 101 else f"R{int(matrix[i, j])}"
                txt_color = "black" if 95 < matrix[i, j] <= 101 else "white"
                ax.text(j, i, label, ha="center", va="center", fontsize=8,
                        color=txt_color, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("First defection round (101 = none)", color="#adb5bd")
    cbar.ax.tick_params(colors="#adb5bd")
    fig.tight_layout()
    return fig


def draw_defection_bar(games):
    model_defects = {}
    model_initiates = {}

    for g in games.values():
        for model, defects, initiated in [
            (g["model_a"], g["stats"]["defects_a"],
             1 if g["stats"]["initiator"] == g["model_a"] else 0),
            (g["model_b"], g["stats"]["defects_b"],
             1 if g["stats"]["initiator"] == g["model_b"] else 0),
        ]:
            model_defects[model] = model_defects.get(model, 0) + defects
            model_initiates[model] = model_initiates.get(model, 0) + initiated

    models = sorted(model_defects, key=lambda m: model_defects[m], reverse=True)
    defects = [model_defects[m] for m in models]
    initiates = [model_initiates[m] for m in models]
    colors = [MODEL_STYLES.get(m, {}).get("color", "#adb5bd") for m in models]

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 4), dpi=120)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x = np.arange(len(models))
    bars = ax.bar(x, defects, color=colors, alpha=0.85, width=0.5, label="Total defections")
    ax.bar(x, initiates, color=colors, alpha=1.0, width=0.5, hatch="//",
           edgecolor="white", linewidth=0.5, label="First-mover defections")

    ax.set_xticks(x)
    ax.set_xticklabels([short_name(m) for m in models], color="white", fontsize=11)
    ax.set_ylabel("Count across all games", color="#adb5bd")
    ax.tick_params(colors="#adb5bd")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white")
    fig.tight_layout()
    return fig


def sanitize(text):
    text = html.escape(text or "No reasoning recorded.")
    text = text.replace("\n", "<br>")
    return text


def render_model_card(model_name, action, round_pts, total_pts):
    style = MODEL_STYLES.get(model_name, {"emoji": "🤖", "color": "#adb5bd"})
    action_color = COOP_COLOR if action == "C" else DEFECT_COLOR
    action_label = "COOPERATE" if action == "C" else "DEFECT"
    st.markdown(
        f"""
        <div style="border:1px solid {style['color']}; border-radius:16px; padding:16px;
                    background:{PANEL_COLOR}; min-height:190px;">
            <div style="font-size:34px;">{style['emoji']}</div>
            <div style="font-size:20px; font-weight:700; color:white; margin-top:6px;">
                {model_name}</div>
            <div style="font-size:26px; font-weight:800; color:{action_color}; margin-top:10px;">
                {action_label}</div>
            <div style="color:#9ca3af; margin-top:2px;">This round action</div>
            <div style="margin-top:10px; color:#e5e7eb;">Round points: {round_pts}</div>
            <div style="color:#e5e7eb;">Cumulative points: {total_pts}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reasoning_box(model_name, text, heading=None):
    style = MODEL_STYLES.get(model_name, {"emoji": "🤖", "color": "#adb5bd"})
    safe = sanitize(text)
    heading = heading or f"{short_name(model_name)} reasoning"
    st.markdown(
        f"""
        <div style="border:1px solid {style['color']}; border-radius:14px; padding:14px;
                    background:#0f172a; min-height:160px; margin-top:10px; overflow-wrap:anywhere;">
            <div style="font-size:16px; font-weight:700; color:{style['color']}; margin-bottom:8px;">
                {heading}</div>
            <div style="white-space:pre-wrap; line-height:1.6; color:#e5e7eb; font-size:15px;">
                {safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_replay_page(game):
    total_rounds = len(game["actions_a"])
    current_round = st.session_state.current_round
    speed = st.session_state.speed_multiplier
    delay = 5.0 / speed

    st.subheader("Replay mode")
    st.caption("Step through the game round by round and read each model's chain-of-thought.")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Start / Next", width="stretch"):
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

    jump = st.slider("Jump to round", min_value=1, max_value=total_rounds,
                     value=max(1, current_round), key="jump_round")
    if jump != max(1, current_round) and not st.session_state.playing:
        st.session_state.current_round = jump
        st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dataset", game["dataset"])
    m2.metric("Round on screen", f"{current_round}/{total_rounds}" if current_round else f"0/{total_rounds}")
    m3.metric("Speed", f"{speed}×")
    m4.metric("Mode", "Playing" if st.session_state.playing else "Paused")

    if current_round == 0:
        st.info("Press 'Start / Next' or 'Play full game' to begin.")
    else:
        idx = current_round - 1
        aa = game["actions_a"][idx]
        ab = game["actions_b"][idx]
        pa, pb = score(aa, ab)
        cum_a = sum(score(game["actions_a"][i], game["actions_b"][i])[0] for i in range(current_round))
        cum_b = sum(score(game["actions_a"][i], game["actions_b"][i])[1] for i in range(current_round))

        left, right = st.columns(2)
        with left:
            render_model_card(game["model_a"], aa, pa, cum_a)
        with right:
            render_model_card(game["model_b"], ab, pb, cum_b)

        st.markdown(f"### Round {current_round} reasoning")
        r1, r2 = st.columns(2)
        with r1:
            render_reasoning_box(game["model_a"],
                                 game.get("reasoning_a", [""])[idx],
                                 heading=f"{short_name(game['model_a'])} explains its move")
        with r2:
            render_reasoning_box(game["model_b"],
                                 game.get("reasoning_b", [""])[idx],
                                 heading=f"{short_name(game['model_b'])} explains its move")

        with st.expander("Last 5 rounds transcript", expanded=True):
            start_idx = max(0, current_round - 5)
            for r in range(start_idx, current_round):
                st.markdown(f"**Round {r + 1}**")
                cl, cr = st.columns(2)
                with cl:
                    render_reasoning_box(game["model_a"],
                                         game.get("reasoning_a", [""])[r],
                                         heading=f"{short_name(game['model_a'])}")
                with cr:
                    render_reasoning_box(game["model_b"],
                                         game.get("reasoning_b", [""])[r],
                                         heading=f"{short_name(game['model_b'])}")

        col_ring, col_gap = st.columns([1, 0.01])
        with col_ring:
            st.pyplot(draw_ring_chart(game, upto_round=current_round), width="stretch")

    if st.session_state.playing and st.session_state.current_round < total_rounds:
        time.sleep(delay)
        st.session_state.current_round += 1
        st.rerun()
    elif st.session_state.playing and st.session_state.current_round >= total_rounds:
        st.session_state.playing = False
        st.success("Replay finished.")


def render_explorer_page(game):
    st.subheader("Game explorer")
    stats = game["stats"]

    a, b, c, d = st.columns(4)
    a.metric(f"{short_name(game['model_a'])} coop rate", f"{stats['coop_rate_a']*100:.0f}%")
    b.metric(f"{short_name(game['model_b'])} coop rate", f"{stats['coop_rate_b']*100:.0f}%")
    c.metric("Mutual coop rate", f"{stats['mutual_coop_rate']*100:.0f}%")
    fd = stats["first_defect_round"]
    d.metric("First defection", f"Round {fd}" if fd else "None")

    e, f_col = st.columns(2)
    e.metric(f"{short_name(game['model_a'])} total points", stats["points_a"])
    f_col.metric(f"{short_name(game['model_b'])} total points", stats["points_b"])

    if stats["initiator"]:
        st.warning(f"First mover: **{stats['initiator']}** defected first at round {fd}.")
    else:
        st.success("Neither model defected. Perfect mutual cooperation for the full game.")

    col_ring, col_gap = st.columns([1, 0.01])
    with col_ring:
        st.pyplot(draw_ring_chart(game), width="stretch")

    inspect_round = st.slider("Inspect reasoning by round", min_value=1,
                              max_value=len(game["actions_a"]),
                              value=len(game["actions_a"]), key="inspect_round")
    idx = inspect_round - 1
    rr1, rr2 = st.columns(2)
    with rr1:
        render_reasoning_box(game["model_a"],
                             game.get("reasoning_a", [""])[idx],
                             heading=f"Round {inspect_round} · {short_name(game['model_a'])}")
    with rr2:
        render_reasoning_box(game["model_b"],
                             game.get("reasoning_b", [""])[idx],
                             heading=f"Round {inspect_round} · {short_name(game['model_b'])}")

    df = build_round_dataframe(game)
    st.dataframe(df, width="stretch", hide_index=True)
    st.download_button("Download as CSV", df.to_csv(index=False),
                       file_name="ipd_game.csv", mime="text/csv")


def render_overview_page(games):
    st.subheader("Tournament overview")

    summary_rows = []
    for g in games.values():
        s = g["stats"]
        summary_rows.append({
            "Model A":        g["model_a"],
            "Model B":        g["model_b"],
            "Coop rate A":    f"{s['coop_rate_a']*100:.0f}%",
            "Coop rate B":    f"{s['coop_rate_b']*100:.0f}%",
            "Mutual coop":    f"{s['mutual_coop_rate']*100:.0f}%",
            "Points A":       s["points_a"],
            "Points B":       s["points_b"],
            "First defect":   f"R{s['first_defect_round']}" if s["first_defect_round"] else "Never",
            "Initiator":      short_name(s["initiator"]) if s["initiator"] else "None",
        })

    df = pd.DataFrame(summary_rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.markdown("### First defection heatmap")
    st.caption("Green = never defected. Red = early defection. Shows the round of first betrayal in each matchup.")
    st.pyplot(draw_defection_heatmap(games), width="stretch")

    st.markdown("### Defection count by model")
    st.caption("Total defections across all games. Hatched portion = times that model struck first.")
    st.pyplot(draw_defection_bar(games), width="stretch")

    st.markdown("### Animated visualisations")
    clock_gif = OUTPUT_DIR / "cooperation_clock.gif"
    grid_gif  = OUTPUT_DIR / "actions_grid_animated.gif"
    if clock_gif.exists():
        st.image(str(clock_gif), caption="Cooperation clock: all 21 matchups, 100 rounds each")
    if grid_gif.exists():
        st.image(str(grid_gif), caption="All 21 matchups: actions per round")


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
    st.set_page_config(
        page_title="IPD Replay App",
        page_icon="🤝",
        layout="wide",
    )
    apply_style()

    st.title("🤝 Iterated Prisoner's Dilemma Replay App")
    st.caption("Interactive playback and analysis of 6 frontier LLMs playing the prisoner's dilemma.")

    for key, default in [
        ("current_round", 0),
        ("playing", False),
        ("speed_multiplier", 2),
        ("selection_key", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    with st.sidebar:
        st.header("Controls")
        page    = st.radio("Page", ["Replay", "Explorer", "Overview"])
        dataset = st.radio("Dataset", ["Known horizon", "Hidden horizon"])
        speed   = st.select_slider("Auto-play speed", options=[1, 2, 5, 10],
                                   value=st.session_state.speed_multiplier)
        st.session_state.speed_multiplier = speed

        games      = load_games(dataset)
        pair_names = list(games.keys())
        selected   = st.selectbox("Matchup", pair_names)

        st.markdown("---")
        st.markdown("**Payoff matrix**")
        st.markdown(
            """
            |   | C | D |
            |---|---|---|
            | **C** | 3, 3 | 0, 5 |
            | **D** | 5, 0 | 1, 1 |
            """
        )

    sel_key = (page, dataset, selected)
    if st.session_state.selection_key != sel_key:
        st.session_state.selection_key = sel_key
        st.session_state.current_round = 0
        st.session_state.playing = False

    game = games[selected]

    if page == "Replay":
        render_replay_page(game)
    elif page == "Explorer":
        render_explorer_page(game)
    else:
        render_overview_page(games)


if __name__ == "__main__":
    main()
