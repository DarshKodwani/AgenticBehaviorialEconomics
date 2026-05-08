# Ultimatum Game between LLMs

One-shot Ultimatum Game played pairwise across a 6-model slate (GPT-4o,
Claude 3.5 Haiku, Gemini 2.0 Flash, Llama 3.1 70B, DeepSeek V3,
Qwen 2.5 72B), with three priming conditions:

- `told_llm` — both parties told the other party is an AI.
- `told_human` — both parties told the other party is a human (deception).
- `no_prime` — no statement about who the other party is.

The prime is symmetric within a pairing: both proposer and responder receive
the same prime sentence.

## Cell map

Direct play: `6 proposers × 6 responders × 3 conditions × 30 runs = 3,240 rounds`
(each round = 2 LLM calls + 2 manipulation-check calls = 4 calls; ≈ 13,000 calls total).

Strategy method: `6 responders × 3 conditions × 30 runs = 540 elicitations`
(each = 1 elicitation + 1 manipulation-check call = 2 calls; ≈ 1,080 calls total).

## Behaviours touched

| Cell | What this experiment measures |
|---|---|
| ABP Reciprocity → Trigger | Responder rejection of unfair offers (canonical elicitation). |
| ABP Altruism → Generosity | Proposer offer (strategically contaminated; not pure dictator). |
| ABP Stability → Steadiness | Delta in offer/threshold across the 3 prime conditions. |
| ABP Stability → Consistency | Variance across the 30 fixed-prompt runs per cell. |
| ASBP A–A → Outcome (Welfare) | Deal rate × prime; total surplus captured. |
| ASBP A–A → Distribution (Inequality) | Cross-pairing offer distribution. |

The headline question this design answers: *does the same model play a
different game when told who is across the table — and what does the
no-prime default reveal about which counterparty it imagines by default?*

## How to run

The harness reads `openrouter_api` from `.env` at the repo root (with
`/Users/darsh/Documents/Darsh/.env` as a fallback). Same auth pattern as
the IPD and pricing experiments.

```bash
cd experiments/ultimatum-game

# Full direct-play matrix
python run_experiment.py

# Strategy-method elicitation
python run_strategy_method.py
```

Both runners are **resumable**: a cell whose JSON file already contains
N runs is skipped on rerun. Per-cell parallelism is 5 concurrent runs;
cells are processed sequentially.

### Restricting to a subset

```bash
# One condition only
python run_experiment.py --condition told_human

# One pairing only
python run_experiment.py --proposer "GPT-4o" --responder "Claude 3.5 Haiku"

# Strategy method for one model
python run_strategy_method.py --responder "GPT-4o"
```

## Output

```
results/
├── direct_play/
│   └── <Proposer>_vs_<Responder>_<condition>.json   # 30 runs per file
└── strategy_method/
    └── <Responder>_<condition>.json                 # 30 elicitations per file
```

Each direct-play run records: `offer`, `decision` (ACCEPT/REJECT), reasoning
strings for both parties, and `mc_*_belief` (`human` | `ai` | `unsure`) from
the follow-up manipulation check on each role.

Each strategy-method run records: `min_acceptable_offer`, reasoning, and
`mc_belief` from the follow-up.

## Design notes

- **Strategy method is the headline elicitation** for responder thresholds —
  no offer-specific noise, no post-hoc rationalisation. The classical
  human-experiments move.
- **Manipulation check on every run** (not subsampled) so the `told_human`
  condition's frame-uptake rate is reported per cell with full precision.
- **Symmetric priming only** for v1. Asymmetric priming (proposer thinks
  human, responder thinks LLM) is a clean v2 follow-up.
- **Temperature 0.7**, matching the IPD harness so the within-cell variance
  is comparable across this experiment and the existing repo data.
- **Offers are not rounded.** Whatever the model returns (subject to a
  `[0, 100]` clamp) is recorded as-is.
