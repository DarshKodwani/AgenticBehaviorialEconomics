"""Prompt templates for the Public Goods Game with punishment.

Design follows Fehr & Gaechter (2000): a 10-round phase without punishment
and a 10-round phase where players can assign costly "deduction points"
after seeing everyone's contributions. Neutral wording throughout: we say
"deduction points", never "punish", so the instructions don't suggest a
moral reading.

Two horizon conditions carry the Round 99 question into this game:
- visible: agents are told how many rounds each phase has and which is last.
- hidden: agents are told only that the game lasts an unknown number of rounds.
"""

HORIZONS = ("visible", "hidden")
ORDERS = ("np", "pn")  # np = no-punishment phase first; pn = punishment first

SYSTEM_TEMPLATE = """You are a participant in a group decision experiment. You are Player {label}.

Setup:
- You are in a group of {n} players: {labels}. The group stays the same for the whole experiment.
- Every round, each player receives an endowment of {endowment} tokens.
- Each player privately decides how many of their {endowment} tokens to put into a group project (any whole number from 0 to {endowment}). Tokens not contributed are kept.
- The total contributed to the project is multiplied by {multiplier} and shared equally among all {n} players, whether or not they contributed.
- So your round earnings = ({endowment} - your contribution) + {multiplier} x (total contributions) / {n}.
- Each token you contribute returns {mpcr} tokens to you and {mpcr} tokens to every other player.
- Earnings accumulate across rounds. Your goal is to maximise your own total earnings.
{horizon_block}
Always respond with ONLY a JSON object in the exact format requested, with no other text."""

HORIZON_BLOCK = {
    "visible": "- The experiment has {total_rounds} rounds in total, split into two phases of {phase_len} rounds each.",
    "hidden": "- The experiment lasts an unknown number of rounds, split into phases. You will be told when a new phase begins.",
}

PHASE_RULES = {
    "none": "In this phase there is only the contribution stage each round.",
    "deduction": (
        "In this phase each round has two stages.\n"
        "Stage 1: everyone chooses a contribution, as before.\n"
        "Stage 2: everyone sees every player's contribution for that round and may assign "
        "deduction points to any other player (0 to {max_points} points per player). "
        "Each point you assign costs you {cost} token. Each point you receive reduces your "
        "round earnings by {impact} tokens (your round earnings cannot fall below 0 from "
        "points received, but the cost of points you assign is always paid)."
    ),
}

PHASE_ANNOUNCEMENT = {
    "visible": "Phase {phase} begins now and lasts {phase_len} rounds (rounds {start} to {end}). Round {total_rounds} is the final round of the experiment.",
    "visible_first": "Phase {phase} begins now and lasts {phase_len} rounds (rounds {start} to {end}).",
    "hidden": "Phase {phase} begins now.",
}

CONTRIBUTION_USER_TEMPLATE = """{announcement}{phase_rules}

{round_line}
Your total earnings so far: {total_earnings} tokens.

History so far:
{history}

Choose your contribution for this round.
Respond with ONLY: {{"contribution": <whole number 0-{endowment}>, "reasoning": "<one or two sentences>"}}"""

DEDUCTION_USER_TEMPLATE = """{round_line} contributions:
{contrib_table}

You may now assign deduction points to other players (0 to {max_points} each). Each point costs you {cost} token and reduces the receiver's earnings by {impact} tokens. Assigning 0 to everyone is allowed.

Respond with ONLY: {{"deductions": {{{example}}}, "reasoning": "<one or two sentences>"}}"""
