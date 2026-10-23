# Public goods game with punishment between LLMs

A repeated public goods game with costly punishment, after Fehr & Gächter
(2000). Each game is one group of six agents, one per model in the slate
(GPT-4o, Claude 3.5 Haiku, Gemini 2.0 Flash, Llama 3.1 70B, DeepSeek V3,
Qwen 2.5 72B). Seats are shuffled per game, so labels A–F say nothing about
which model is which.

## The game

- Every round each player gets 20 tokens and chooses how many to put into a
  group project. The project total is multiplied by 2.4 and split equally
  across all six, so each token contributed returns 0.4 to the contributor
  (MPCR 0.4, matching Fehr & Gächter).
- Phase 1 (rounds 1–10): contributions only.
- Phase 2 (rounds 11–20): after contributing, everyone sees all contributions
  and can assign 0–10 deduction points to each other player. A point costs
  the sender 1 token and the receiver 3. Round earnings can't go below 0
  from points received.
- Neutral wording: "deduction points", never "punish".
- Partner matching: the same group for all 20 rounds. Each agent sees the
  full contribution history by label, plus the points it personally received
  and assigned (not who sent them).

## Conditions

| Flag | Values | What it tests |
|---|---|---|
| `--order` | `np` (default), `pn` | Order effects: deductions second vs first |
| `--horizon` | `visible` (default), `hidden` | The Round 99 question: does a known last round kill punishment and cooperation near the end? |

## Behaviours touched

| Cell | What this experiment measures |
|---|---|
| ABP Reciprocity | Conditional cooperation; who gets deduction points and for how much |
| ABP Altruism | Contribution level in phase 1 |
| ABP Stability → Consistency | Variance across repeated games of the same cell |
| ASBP A–A → Outcome (Welfare) | Total earnings with vs without deductions (punishment is costly) |
| ASBP A–A → Distribution (Inequality) | Spread of final earnings within each group |

## How to run

Reads `openrouter_api` from `.env` at the repo root, same as the other
experiments.

```bash
cd experiments/public-goods-punishment

python run_experiment.py --games 40                    # headline run
python run_experiment.py --games 40 --horizon hidden   # Round 99 comparison
python run_experiment.py --games 40 --order pn         # order control

python plot_point_cloud.py results/np_visible
python plot_point_cloud.py results/np_visible --by-model
```

Each game is 180 calls (6 contributions × 20 rounds + 6 deduction decisions
× 10 rounds), so 40 games ≈ 7,200 calls. Runs are resumable: finished games
are skipped.

`PGG_MOCK=1` swaps the API for a scripted fake agent so the pipeline and
plots can be tested without spending tokens. Mock results go to
`results/*_mock/` and plots are titled MOCK DATA.

## Output

`results/<order>_<horizon>/game_NNN.json`, one file per game, with seats,
parameters, and for every round: contributions, reasoning, deduction matrix,
deduction reasoning, payoffs and any parse-failure flags. A failed parse
records a contribution of 0 with a flag; the plot excludes flagged decisions.

## Design choices to revisit

- The system prompt tells agents their goal is to maximise their own total
  earnings, mirroring paid human subjects. Dropping that line is a separate
  condition worth running: it probably raises cooperation.
- Agents are told the multiplier arithmetic explicitly (0.4 back per token),
  so the dilemma is transparent rather than something they must work out.
