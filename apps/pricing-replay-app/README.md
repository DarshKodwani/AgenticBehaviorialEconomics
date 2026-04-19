# Interactive Replay App

This folder contains a standalone Streamlit app for replaying and exploring the saved pricing simulations.

## Features

- round-by-round replay with play, pause, next, previous, and reset
- speed controls for autoplay
- two model avatar cards with prices and reasoning
- prompt view showing what each model was told
- graph explorer for any saved matchup
- tournament overview with grid and comparison visuals

## Run

From the repo root:

streamlit run apps/pricing-replay-app/app.py

The app reads existing saved files from:

- experiments/pricing-bertrand-duopoly/results
- experiments/pricing-bertrand-duopoly/results_no_cap
- experiments/pricing-bertrand-duopoly/output
