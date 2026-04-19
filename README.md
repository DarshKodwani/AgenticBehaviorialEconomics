# AgenticBehaviorialEconomics

This repository explores agentic behavioural economics through a set of experiments with large language models acting as strategic agents.

The current focus is a repeated pricing game in which frontier models compete over 80 rounds, observe each other's past prices, and often drift into tacit coordination or high-price regimes.

## Repository structure

- `blogs/` — the main essay and blog assets
- `experiments/pricing-bertrand-duopoly/` — repeated pricing and no-cap collusion experiments
- `experiments/iterated-prisoners-dilemma/` — iterated Prisoner's Dilemma runs
- `experiments/pricing-prompt-sensitivity/` — prompt framing and behavioural sensitivity tests
- `apps/pricing-replay-app/` — Streamlit app for replaying and exploring saved simulations

## Quick start

### 1. Install dependencies

For the pricing experiment:

```bash
pip install -r experiments/pricing-bertrand-duopoly/requirements.txt
```

For the replay app:

```bash
pip install streamlit pandas matplotlib numpy
```

### 2. Add API credentials

Create a root `.env` file with:

```env
openrouter_api=YOUR_KEY_HERE
```

### 3. Run the replay app

From the repo root:

```bash
python3 -m streamlit run apps/pricing-replay-app/app.py
```

### 4. Run the pricing experiments

Examples:

```bash
python3 experiments/pricing-bertrand-duopoly/run_experiment.py
python3 experiments/pricing-bertrand-duopoly/run_no_cap_all_pairs.py
```

## Main idea

Most AI evaluation still focuses on accuracy and explainability. This project studies something different: behaviour.

Questions include:

- Do agents cooperate or compete?
- Do they converge on stable prices?
- Do prompt changes alter strategic behaviour?
- How close do they get to Nash or joint-profit outcomes?

## Outputs

Saved runs, summaries, and visualisations live inside the relevant experiment folders. The replay app can be used to inspect round-by-round prices, profits, prompts, and model reasoning.
