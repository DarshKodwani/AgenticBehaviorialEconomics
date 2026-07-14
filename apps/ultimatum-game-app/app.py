"""Ultimatum Game Replay & Analysis App.

Five tabs:
  1. The Pivot        – mean offer by prime across models
  2. Round Replay     – step through 30 runs for any proposer × responder × condition
  3. Offer Distribution – histogram per model × condition
  4. Rejection Wall   – accept/reject grid for any responder × condition
  5. Stated vs Revealed – strategy-method thresholds vs revealed behaviour
"""
import json
import glob
import html
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR       = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = ROOT_DIR / "experiments" / "ultimatum-game"
DIRECT_DIR     = EXPERIMENT_DIR / "results" / "direct_play"
STRATEGY_DIR   = EXPERIMENT_DIR / "results" / "strategy_method"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODELS = [
    "GPT-4o",
    "Claude 3.5 Haiku",
    "Gemini 2.0 Flash",
    "Llama 3.1 70B",
    "DeepSeek V3",
    "Qwen 2.5 72B",
]

MODEL_STYLES = {
    "GPT-4o":           {"emoji": "🧠", "color": "#ff5a8a"},
    "Claude 3.5 Haiku": {"emoji": "🎭", "color": "#7eb8f7"},
    "Gemini 2.0 Flash": {"emoji": "✨", "color": "#4ecba0"},
    "Llama 3.1 70B":    {"emoji": "🦙", "color": "#b48af7"},
    "DeepSeek V3":      {"emoji": "🔎", "color": "#ffb347"},
    "Qwen 2.5 72B":     {"emoji": "🌙", "color": "#4ecfd6"},
}

CONDITIONS = ["told_human", "no_prime", "told_llm"]
COND_LABEL = {
    "told_human": "Told: HUMAN",
    "no_prime":   "No Prime",
    "told_llm":   "Told: AI",
}

BG      = "#0d1117"
PANEL   = "#111827"
GRID    = "#2a2e44"
TEXT    = "#e6e9f5"
TEXT_DIM= "#9aa0b8"

ACCEPT_COLOR = "#1ed760"
REJECT_COLOR = "#ff2d55"


def short(name):
    return (
        name.replace("Claude 3.5 Haiku", "Claude")
            .replace("Gemini 2.0 Flash", "Gemini")
            .replace("Llama 3.1 70B",    "Llama")
            .replace("Qwen 2.5 72B",     "Qwen")
            .replace("DeepSeek V3",      "DeepSeek")
    )


def sanitize(text):
    text = html.escape(text or "No reasoning recorded.")
    return text.replace("\n", "<br>")


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
@st.cache_data
def load_direct():
    """Returns dict keyed by (proposer, responder, condition) → list of run dicts."""
    data = {}
    for fp in glob.glob(str(DIRECT_DIR / "*.json")):
        d = json.load(open(fp))
        key = (d["proposer"], d["responder"], d["condition"])
        data[key] = d["runs"]
    return data


@st.cache_data
def load_strategy():
    """Returns dict keyed by (responder, condition) → list of threshold dicts."""
    data = {}
    for fp in glob.glob(str(STRATEGY_DIR / "*.json")):
        d = json.load(open(fp))
        key = (d["responder"], d["condition"])
        data[key] = d["thresholds"]
    return data


@st.cache_data
def pivot_means(direct):
    """Mean offer by (proposer, condition), aggregated over all responders."""
    sums = defaultdict(list)
    for (proposer, responder, cond), runs in direct.items():
        for r in runs:
            sums[(proposer, cond)].append(r["offer"])
    return {k: np.mean(v) for k, v in sums.items()}


# ---------------------------------------------------------------------------
# Shared styling
# ---------------------------------------------------------------------------
def apply_style():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0d1117; }
        h1,h2,h3,h4,p,label { color: white !important; }
        [data-testid="stMetricValue"] { color: white; }
        [data-testid="stSidebar"] { background-color: #111827; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def model_card(model, offer, decision, proposer_reasoning, responder_reasoning, run_id, n_runs):
    style   = MODEL_STYLES.get(model, {"emoji": "🤖", "color": "#adb5bd"})
    dec_col = ACCEPT_COLOR if decision == "ACCEPT" else REJECT_COLOR
    payoff  = offer if decision == "ACCEPT" else 0
    kept    = (100 - offer) if decision == "ACCEPT" else 0
    safe_pr = sanitize(proposer_reasoning)
    safe_rr = sanitize(responder_reasoning)
    st.markdown(
        f"""
        <div style="border:1px solid {style['color']}33; border-radius:14px;
                    padding:18px; background:{PANEL}; margin-bottom:12px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <span style="font-size:28px;">{style['emoji']}</span>
            <span style="font-size:18px; font-weight:700; color:white;">{model}</span>
            <span style="margin-left:auto; color:{TEXT_DIM}; font-size:12px;">
              run {run_id} / {n_runs}</span>
          </div>
          <div style="display:flex; gap:24px; flex-wrap:wrap; margin-bottom:14px;">
            <div>
              <div style="color:{TEXT_DIM}; font-size:11px; text-transform:uppercase;">Offer</div>
              <div style="color:white; font-size:22px; font-weight:700;">${offer:.0f}</div>
            </div>
            <div>
              <div style="color:{TEXT_DIM}; font-size:11px; text-transform:uppercase;">Decision</div>
              <div style="color:{dec_col}; font-size:22px; font-weight:700;">{decision}</div>
            </div>
            <div>
              <div style="color:{TEXT_DIM}; font-size:11px; text-transform:uppercase;">Proposer gets</div>
              <div style="color:white; font-size:22px; font-weight:700;">${kept:.0f}</div>
            </div>
            <div>
              <div style="color:{TEXT_DIM}; font-size:11px; text-transform:uppercase;">Responder gets</div>
              <div style="color:white; font-size:22px; font-weight:700;">${payoff:.0f}</div>
            </div>
          </div>
          <div style="border-top:1px solid {GRID}; padding-top:10px; margin-top:4px;">
            <div style="color:{style['color']}; font-size:12px; font-weight:600;
                        margin-bottom:4px;">Proposer reasoning</div>
            <div style="color:#e5e7eb; font-size:14px; line-height:1.6;">{safe_pr}</div>
          </div>
          <div style="border-top:1px solid {GRID}; padding-top:10px; margin-top:10px;">
            <div style="color:{dec_col}; font-size:12px; font-weight:600;
                        margin-bottom:4px;">Responder reasoning</div>
            <div style="color:#e5e7eb; font-size:14px; line-height:1.6;">{safe_rr}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab 1 – The Pivot
# ---------------------------------------------------------------------------
def tab_pivot(direct):
    st.subheader("The Pivot")
    st.caption(
        "Mean offer to the responder, aggregated over all responders and 30 runs per pairing. "
        "DeepSeek V3 and GPT-4o offer ~$8 more when told the counterparty is an AI."
    )

    means = pivot_means(direct)

    # Build figure
    fig = plt.figure(figsize=(13, 5.5), dpi=150, facecolor=BG)
    gs  = gridspec.GridSpec(1, 3, figure=fig,
                            left=0.13, right=0.96, top=0.78, bottom=0.14, wspace=0.08)
    y_labels = list(reversed(MODELS))
    pivoters = {"DeepSeek V3", "GPT-4o"}

    for col, cond in enumerate(CONDITIONS):
        ax = fig.add_subplot(gs[0, col])
        ax.set_facecolor(PANEL)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_xlim(20, 58)
        ax.set_ylim(-0.6, len(MODELS) - 0.4)
        ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(colors=TEXT_DIM, length=0, labelsize=9)
        ax.set_xticks([20, 30, 40, 50])
        ax.set_xticklabels(["$20", "$30", "$40", "$50"], color=TEXT_DIM, fontsize=9)
        ax.set_yticks(range(len(MODELS)))
        if col == 0:
            ax.set_yticklabels(y_labels, color=TEXT, fontsize=10)
        else:
            ax.set_yticklabels([""] * len(MODELS))
        ax.axvline(40, color=GRID, linewidth=1.2, linestyle="--", alpha=0.7)
        tc = MODEL_STYLES["DeepSeek V3"]["color"] if cond == "told_llm" else TEXT
        ax.set_title(COND_LABEL[cond], color=tc,
                     fontsize=12, weight="bold" if cond == "told_llm" else "normal", pad=8)

        for yi, model in enumerate(y_labels):
            m = means.get((model, cond))
            if m is None:
                continue
            color = MODEL_STYLES[model]["color"]
            alpha = 1.0 if model in pivoters else 0.55
            ax.barh(yi, m - 20, left=20, height=0.45,
                    color=color, alpha=alpha, zorder=3)
            if col == 2:
                ax.text(m + 0.6, yi, f"${m:.0f}",
                        color=color, fontsize=9, va="center",
                        weight="bold" if model in pivoters else "normal")

    fig.text(0.13, 0.91, "Mean offer by priming condition",
             color=TEXT, fontsize=16, weight="bold")
    fig.text(0.13, 0.87,
             "Bar ends at mean offer · dashed line = $40 · aggregated over all responders, 30 runs each",
             color=TEXT_DIM, fontsize=9)
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    # Slope chart overlay
    st.markdown("#### Slope view: told_human → told_AI")
    fig2, ax2 = plt.subplots(figsize=(7, 4.5), dpi=150, facecolor=BG)
    ax2.set_facecolor(PANEL)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.set_xlim(-0.3, 2.3)
    ax2.set_ylim(25, 55)
    ax2.yaxis.grid(True, color=GRID, linewidth=0.5)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels([COND_LABEL[c] for c in CONDITIONS], color=TEXT, fontsize=11)
    ax2.tick_params(colors=TEXT_DIM, length=0)
    ax2.set_ylabel("Mean offer ($)", color=TEXT_DIM, fontsize=10)

    for model in MODELS:
        ys = [means.get((model, c), np.nan) for c in CONDITIONS]
        color = MODEL_STYLES[model]["color"]
        alpha = 1.0 if model in pivoters else 0.4
        lw    = 2.5 if model in pivoters else 1.2
        ax2.plot([0, 1, 2], ys, color=color, linewidth=lw, alpha=alpha,
                 marker="o", markersize=5 if model in pivoters else 3)
        ax2.text(2.05, ys[2], short(model), color=color,
                 fontsize=9 if model in pivoters else 8,
                 va="center", alpha=alpha,
                 weight="bold" if model in pivoters else "normal")

    fig2.tight_layout()
    st.pyplot(fig2, width="stretch")
    plt.close(fig2)


# ---------------------------------------------------------------------------
# Tab 2 – Round Replay
# ---------------------------------------------------------------------------
def tab_replay(direct):
    st.subheader("Round Replay")
    st.caption("Step through 30 runs for any proposer × responder × condition pairing.")

    col1, col2, col3 = st.columns(3)
    with col1:
        proposer = st.selectbox("Proposer", MODELS, key="rp_proposer")
    with col2:
        responder = st.selectbox("Responder", MODELS, key="rp_responder")
    with col3:
        cond = st.selectbox("Condition", CONDITIONS, format_func=lambda c: COND_LABEL[c],
                            key="rp_cond")

    runs = direct.get((proposer, responder, cond), [])
    if not runs:
        st.warning("No data found for this combination.")
        return

    n = len(runs)
    run_idx = st.slider("Run", min_value=1, max_value=n, value=1, key="rp_run") - 1
    r = runs[run_idx]

    model_card(
        model=proposer,
        offer=r["offer"],
        decision=r["decision"],
        proposer_reasoning=r.get("proposer_reasoning", ""),
        responder_reasoning=r.get("responder_reasoning", ""),
        run_id=run_idx + 1,
        n_runs=n,
    )

    # Manipulation check
    with st.expander("Manipulation check — what did each model think it was playing?"):
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown(f"**Proposer belief:** `{r.get('mc_proposer_belief', '—')}`")
            st.markdown(f"*{r.get('mc_proposer_reasoning', '')}*")
        with mc2:
            st.markdown(f"**Responder belief:** `{r.get('mc_responder_belief', '—')}`")
            st.markdown(f"*{r.get('mc_responder_reasoning', '')}*")

    # Summary stats for this pairing
    st.markdown("#### All 30 runs at a glance")
    offers    = [x["offer"] for x in runs]
    decisions = [x["decision"] for x in runs]
    n_accept  = decisions.count("ACCEPT")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mean offer",    f"${np.mean(offers):.1f}")
    m2.metric("Median offer",  f"${np.median(offers):.1f}")
    m3.metric("Acceptance rate", f"{n_accept}/{n}")
    m4.metric("Min → Max offer", f"${min(offers):.0f} → ${max(offers):.0f}")

    fig, ax = plt.subplots(figsize=(8, 2.5), dpi=140, facecolor=BG)
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values():
        sp.set_visible(False)
    colors = [ACCEPT_COLOR if d == "ACCEPT" else REJECT_COLOR for d in decisions]
    ax.bar(range(1, n + 1), offers, color=colors, width=0.7, alpha=0.85)
    ax.axhline(np.mean(offers), color=TEXT_DIM, linewidth=1, linestyle="--")
    ax.set_xlabel("Run", color=TEXT_DIM, fontsize=9)
    ax.set_ylabel("Offer ($)", color=TEXT_DIM, fontsize=9)
    ax.tick_params(colors=TEXT_DIM, labelsize=8)
    ax.set_ylim(0, 105)
    # Legend
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=ACCEPT_COLOR, label="Accept"),
                        Patch(color=REJECT_COLOR, label="Reject")],
              facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=8)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Tab 3 – Offer Distributions
# ---------------------------------------------------------------------------
def tab_distributions(direct):
    st.subheader("Offer Distributions")
    st.caption("Histogram of offers for a selected proposer across all conditions. "
               "DeepSeek flips from a $40 spike to a $50 spike under the AI prime.")

    proposer = st.selectbox("Proposer model", MODELS, key="dist_proposer")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), dpi=140, facecolor=BG,
                              sharey=True, sharex=True)
    color = MODEL_STYLES[proposer]["color"]
    bins  = np.arange(0, 105, 5)

    for ax, cond in zip(axes, CONDITIONS):
        all_offers = []
        for (prop, resp, c), runs in direct.items():
            if prop == proposer and c == cond:
                all_offers.extend(r["offer"] for r in runs)

        ax.set_facecolor(PANEL)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.hist(all_offers, bins=bins, color=color, alpha=0.8, edgecolor=BG)
        ax.axvline(np.mean(all_offers) if all_offers else 40,
                   color=TEXT_DIM, linewidth=1.2, linestyle="--")
        ax.set_title(COND_LABEL[cond], color=TEXT, fontsize=11,
                     weight="bold" if cond == "told_llm" else "normal")
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        ax.set_xlabel("Offer ($)", color=TEXT_DIM, fontsize=9)
        ax.xaxis.grid(True, color=GRID, linewidth=0.4)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("Count", color=TEXT_DIM, fontsize=9)
    fig.suptitle(f"{proposer} — offer distribution by condition",
                 color=TEXT, fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Tab 4 – Rejection Wall
# ---------------------------------------------------------------------------
def tab_wall(direct):
    st.subheader("Rejection Wall")
    st.caption(
        "Every offer received by a responder model, coloured green (ACCEPT) or red (REJECT). "
        "Llama's wall is speckled with red even on fair offers."
    )

    col1, col2 = st.columns(2)
    with col1:
        responder = st.selectbox("Responder model", MODELS, key="wall_responder")
    with col2:
        cond = st.selectbox("Condition", CONDITIONS, format_func=lambda c: COND_LABEL[c],
                            key="wall_cond")

    # Gather all runs where this model is responder
    runs_all = []
    for (prop, resp, c), runs in direct.items():
        if resp == responder and c == cond:
            for r in runs:
                runs_all.append({
                    "proposer": prop,
                    "offer":    r["offer"],
                    "decision": r["decision"],
                    "reasoning": r.get("responder_reasoning", ""),
                })

    if not runs_all:
        st.warning("No data for this combination.")
        return

    n_accept = sum(1 for r in runs_all if r["decision"] == "ACCEPT")
    n_reject = sum(1 for r in runs_all if r["decision"] == "REJECT")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total offers", len(runs_all))
    m2.metric("Accepted", n_accept)
    m3.metric("Rejected", n_reject)

    # Sort by offer value descending
    runs_all.sort(key=lambda x: x["offer"], reverse=True)
    n = len(runs_all)
    ncols = 30
    nrows = (n + ncols - 1) // ncols

    fig, ax = plt.subplots(figsize=(13, max(3, nrows * 0.55 + 1.2)), dpi=140, facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")

    for i, run in enumerate(runs_all):
        row = i // ncols
        col = i % ncols
        color = ACCEPT_COLOR if run["decision"] == "ACCEPT" else REJECT_COLOR
        rect = plt.Rectangle([col, nrows - row - 1], 0.88, 0.88,
                              color=color, alpha=0.85)
        ax.add_patch(rect)
        ax.text(col + 0.44, nrows - row - 0.56,
                f"${run['offer']:.0f}",
                ha="center", va="center", fontsize=5.5, color="white", fontweight="bold")

    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    fig.suptitle(
        f"{responder} as responder · {COND_LABEL[cond]} · sorted by offer (high→low)",
        color=TEXT, fontsize=11, fontweight="bold"
    )
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=ACCEPT_COLOR, label="Accept"),
                         Patch(color=REJECT_COLOR, label="Reject")],
               loc="lower right", facecolor=PANEL, edgecolor=GRID,
               labelcolor=TEXT, fontsize=9)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    # Show rejection reasoning
    rejections = [r for r in runs_all if r["decision"] == "REJECT"]
    if rejections:
        with st.expander(f"Rejection reasoning ({len(rejections)} rejections)"):
            for r in rejections:
                st.markdown(
                    f"**Offer: ${r['offer']:.0f}** from *{short(r['proposer'])}*  \n"
                    f"{r['reasoning']}"
                )
                st.divider()


# ---------------------------------------------------------------------------
# Tab 5 – Stated vs Revealed
# ---------------------------------------------------------------------------
def tab_thresholds(direct, strategy):
    st.subheader("Stated vs Revealed Thresholds")
    st.caption(
        "Stated minimum: what each model said it would accept (strategy method). "
        "Revealed minimum: the lowest offer it actually accepted in direct play. "
        "Gemini's stated threshold collapses under the AI prime; Llama's rises."
    )

    cond = st.selectbox("Condition", CONDITIONS, format_func=lambda c: COND_LABEL[c],
                        key="thresh_cond")

    rows = []
    for model in MODELS:
        # Stated threshold
        thresh_runs = strategy.get((model, cond), [])
        stated = np.mean([t["min_acceptable_offer"] for t in thresh_runs]) if thresh_runs else None

        # Revealed: lowest offer actually accepted
        accepted_offers = []
        rejected_offers = []
        for (prop, resp, c), runs in direct.items():
            if resp == model and c == cond:
                for r in runs:
                    if r["decision"] == "ACCEPT":
                        accepted_offers.append(r["offer"])
                    else:
                        rejected_offers.append(r["offer"])
        revealed = min(accepted_offers) if accepted_offers else None
        n_rej    = len(rejected_offers)

        rows.append({
            "Model":           model,
            "Stated min (avg)": f"${stated:.1f}" if stated is not None else "—",
            "Lowest accepted":  f"${revealed:.0f}" if revealed is not None else "—",
            "Rejections":       n_rej,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, width="stretch")

    # Chart: stated vs revealed side by side
    stated_vals   = []
    revealed_vals = []
    labels        = []
    colors        = []
    for model in MODELS:
        thresh_runs = strategy.get((model, cond), [])
        stated = np.mean([t["min_acceptable_offer"] for t in thresh_runs]) if thresh_runs else 0
        accepted = []
        for (prop, resp, c), runs in direct.items():
            if resp == model and c == cond:
                accepted.extend(r["offer"] for r in runs if r["decision"] == "ACCEPT")
        revealed = min(accepted) if accepted else 0
        stated_vals.append(stated)
        revealed_vals.append(revealed)
        labels.append(short(model))
        colors.append(MODEL_STYLES[model]["color"])

    x   = np.arange(len(MODELS))
    w   = 0.35
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=140, facecolor=BG)
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values():
        sp.set_visible(False)

    b1 = ax.bar(x - w / 2, stated_vals,   w, color=colors, alpha=0.9,  label="Stated min")
    b2 = ax.bar(x + w / 2, revealed_vals, w, color=colors, alpha=0.45, label="Lowest accepted",
                hatch="//", edgecolor=BG)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=TEXT, fontsize=10)
    ax.set_ylabel("Offer ($)", color=TEXT_DIM, fontsize=10)
    ax.tick_params(colors=TEXT_DIM)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 55)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=9)
    fig.suptitle(f"Stated vs revealed minimum acceptable offer — {COND_LABEL[cond]}",
                 color=TEXT, fontsize=12, fontweight="bold")
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    # Strategy method reasoning explorer
    st.markdown("#### Strategy method reasoning")
    model_sel = st.selectbox("Model", MODELS, key="thresh_model")
    thresh_runs = strategy.get((model_sel, cond), [])
    if thresh_runs:
        run_idx = st.slider("Run", 1, len(thresh_runs), 1, key="thresh_run") - 1
        t = thresh_runs[run_idx]
        color = MODEL_STYLES[model_sel]["color"]
        st.markdown(
            f"""
            <div style="border:1px solid {color}33; border-radius:12px; padding:16px;
                        background:{PANEL}; margin-top:8px;">
              <div style="color:{color}; font-weight:700; margin-bottom:6px;">
                {model_sel} · stated minimum: <span style="font-size:20px;">${t['min_acceptable_offer']:.0f}</span>
              </div>
              <div style="color:#e5e7eb; line-height:1.6; font-size:14px;">{sanitize(t['reasoning'])}</div>
              <div style="color:{TEXT_DIM}; font-size:11px; margin-top:10px;">
                Manipulation check: believed counterparty was
                <strong style="color:white;">{t.get('mc_belief','—')}</strong> —
                {sanitize(t.get('mc_reasoning',''))}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No strategy method data for this combination.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Ultimatum Game — LLM Analysis",
        page_icon="⚖️",
        layout="wide",
    )
    apply_style()

    st.title("⚖️ Ultimatum Game: Frontier LLMs")
    st.caption(
        "Six frontier models · 3,240 direct-play rounds · 540 strategy-method rounds · "
        "three priming conditions: told human, no prime, told AI."
    )

    direct   = load_direct()
    strategy = load_strategy()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 The Pivot",
        "▶️ Round Replay",
        "📈 Offer Distributions",
        "🧱 Rejection Wall",
        "🎯 Stated vs Revealed",
    ])

    with tab1:
        tab_pivot(direct)
    with tab2:
        tab_replay(direct)
    with tab3:
        tab_distributions(direct)
    with tab4:
        tab_wall(direct)
    with tab5:
        tab_thresholds(direct, strategy)


if __name__ == "__main__":
    main()
