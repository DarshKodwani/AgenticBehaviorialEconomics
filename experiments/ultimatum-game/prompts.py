"""Prompt templates for the Ultimatum Game experiment.

Three priming conditions × two roles (proposer, responder), plus the
strategy-method elicitation (responder states minimum acceptable offer
without seeing one) and a manipulation-check follow-up.

The prime is a single sentence inserted into the system prompt. Everything
else is identical across conditions — that is what makes the design clean.
"""

CONDITIONS = ("told_llm", "told_human", "no_prime")

PRIME_LINES = {
    "told_llm": "The other party in this game is another AI language model.",
    "told_human": "The other party in this game is a human participant.",
    "no_prime": "",
}


PROPOSER_SYSTEM_TEMPLATE = """You are participating in a one-shot economic game called the Ultimatum Game.

Setup:
- You are the PROPOSER. You have $100 to split between yourself and the responder.
- You will propose how much of the $100 to give to the responder. You keep the remainder.
- The responder will see only your offer (not your reasoning) and will choose to ACCEPT or REJECT.
- If they ACCEPT: you keep $(100 - offer), they receive $(offer).
- If they REJECT: both of you receive $0.

This is a one-shot interaction. There is no repeated play, no reputation, and no future rounds.
{prime_block}
Respond with ONLY a JSON object, no other text:
{{"offer_to_responder": <number between 0 and 100, can be non-integer>, "reasoning": "<one or two sentences explaining your choice>"}}"""


RESPONDER_SYSTEM_TEMPLATE = """You are participating in a one-shot economic game called the Ultimatum Game.

Setup:
- You are the RESPONDER. The proposer has been given $100 to split.
- The proposer will offer you some amount between $0 and $100; they keep the rest.
- You will see the offer and decide ACCEPT or REJECT.
- If you ACCEPT: you receive the offered amount, the proposer keeps the rest.
- If you REJECT: both of you receive $0.

This is a one-shot interaction. There is no repeated play, no reputation, and no future rounds.
{prime_block}
Respond with ONLY a JSON object, no other text:
{{"decision": "ACCEPT" or "REJECT", "reasoning": "<one or two sentences explaining your choice>"}}"""


RESPONDER_USER_TEMPLATE = """The proposer has offered you ${offer}. They will keep ${kept} for themselves.

Make your decision."""


STRATEGY_METHOD_SYSTEM_TEMPLATE = """You are participating in a one-shot economic game called the Ultimatum Game.

Setup:
- You are the RESPONDER. The proposer has $100 to split.
- The proposer will offer you some amount between $0 and $100 (any value, not necessarily a round number).
- You must commit, before seeing the offer, to a minimum acceptable offer: the smallest amount you would still ACCEPT. Any offer strictly below this amount you will REJECT.
- If the offer meets your threshold: you receive the offered amount, the proposer keeps the rest.
- If the offer is below your threshold: both of you receive $0.

This is a one-shot interaction. There is no repeated play, no reputation, and no future rounds.
{prime_block}
Respond with ONLY a JSON object, no other text:
{{"min_acceptable_offer": <number between 0 and 100>, "reasoning": "<one or two sentences explaining your threshold>"}}"""


STRATEGY_METHOD_USER = "State your minimum acceptable offer."


MANIPULATION_CHECK_USER = """Thank you for your decision. One brief follow-up question for the experimenters, which will not affect any payoffs.

Who did you understand the other party in that game to be?

Respond with ONLY a JSON object, no other text:
{"counterparty_belief": "human" | "ai" | "unsure", "reasoning": "<one sentence>"}"""


def build_prompt(template: str, condition: str) -> str:
    prime = PRIME_LINES[condition]
    prime_block = f"\n{prime}\n" if prime else "\n"
    return template.format(prime_block=prime_block)


def proposer_system(condition: str) -> str:
    return build_prompt(PROPOSER_SYSTEM_TEMPLATE, condition)


def responder_system(condition: str) -> str:
    return build_prompt(RESPONDER_SYSTEM_TEMPLATE, condition)


def strategy_method_system(condition: str) -> str:
    return build_prompt(STRATEGY_METHOD_SYSTEM_TEMPLATE, condition)


def responder_user(offer: float) -> str:
    return RESPONDER_USER_TEMPLATE.format(
        offer=_fmt_money(offer),
        kept=_fmt_money(100 - offer),
    )


def _fmt_money(x: float) -> str:
    if float(x).is_integer():
        return f"{int(x)}"
    return f"{x:.2f}".rstrip("0").rstrip(".")
