"""Public Goods Game with costly punishment, played by LLM agents via OpenRouter.

One game = one group of six agents (one per model in the slate) playing
two 10-round phases: no deductions, then deductions (or the reverse).
Every call is stateless: the full relevant history is written into the
prompt each round, so context length stays flat and every model sees
exactly the same information.

Set PGG_MOCK=1 to run with a scripted fake agent instead of the API
(used to test the pipeline and plots without spending tokens).
"""
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv

import prompts as P


load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if not os.getenv("openrouter_api"):
    load_dotenv("/Users/darsh/Documents/Darsh/.env")

OPENROUTER_API_KEY = os.getenv("openrouter_api")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MOCK = os.getenv("PGG_MOCK") == "1"

MODELS = {
    "GPT-4o": "openai/gpt-4o",
    "Claude 3.5 Haiku": "anthropic/claude-3.5-haiku",
    "Gemini 2.0 Flash": "google/gemini-2.0-flash-001",
    "Llama 3.1 70B": "meta-llama/llama-3.1-70b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat-v3-0324",
    "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
}

# Game parameters (Fehr & Gaechter 2000 use MPCR 0.4; 2.4 / 6 = 0.4)
ENDOWMENT = 20
MULTIPLIER = 2.4
PHASE_LEN = 10
TOTAL_ROUNDS = 2 * PHASE_LEN
MAX_POINTS = 10
COST = 1
IMPACT = 3

TEMPERATURE = 0.7
MAX_TOKENS = 300
LABELS = "ABCDEF"

JSON_RETRY_REMINDER = (
    "Your previous response was not valid JSON. Respond with ONLY a single "
    "JSON object in the exact format specified, and no other text."
)


# ---------------------------------------------------------------- API layer

def _call_openrouter(model_id, messages, max_retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "response_format": {"type": "json_object"},
    }
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    print(f"  LLM query failed after {max_retries} attempts ({model_id}): {last_err}")
    return ""


def _mock_call(messages):
    """Scripted agent: decays without deductions, cooperates with them."""
    user = messages[-1]["content"]
    rng = random.Random()
    if '"deductions"' in user:
        me = re.search(r"You are Player (\w)", messages[0]["content"]).group(1)
        contribs = dict(re.findall(r"Player (\w): (\d+)", user))
        out = {}
        for lab, c in contribs.items():
            if lab != me:
                out[lab] = max(0, min(MAX_POINTS, int((10 - int(c)) / 3 + rng.gauss(0, 1)))) if int(c) < 10 else 0
        return json.dumps({"deductions": out, "reasoning": "mock"})
    rnd = int(re.search(r"^Round (\d+)(?: of \d+)?\.$", user, re.M).group(1))
    deduction_phase = "Stage 2" in user or "deduction points received" in user
    if deduction_phase:
        mu = 12 + 6 * (1 - 0.6 ** (rnd % PHASE_LEN or PHASE_LEN))
    else:
        mu = 11 - 0.8 * ((rnd - 1) % PHASE_LEN)
    c = 0 if rng.random() < (0.05 if deduction_phase else 0.06 * ((rnd - 1) % PHASE_LEN)) else rng.gauss(mu, 3.5)
    return json.dumps({"contribution": int(max(0, min(ENDOWMENT, round(c)))), "reasoning": "mock"})


def _query(model_id, messages, parser):
    """Call, parse strictly, retry once with a JSON reminder. Returns (parsed|None, raw)."""
    call = (lambda m: _mock_call(m)) if MOCK else (lambda m: _call_openrouter(model_id, m))
    raw = call(messages)
    parsed = parser(raw)
    if parsed is not None:
        return parsed, raw
    raw2 = call(list(messages) + [
        {"role": "assistant", "content": raw or ""},
        {"role": "user", "content": JSON_RETRY_REMINDER},
    ])
    return parser(raw2), raw2 or raw


def _extract_json(content):
    if not content:
        return None
    cleaned = content
    if "```" in cleaned:
        chunks = cleaned.split("```")
        if len(chunks) >= 2:
            cleaned = chunks[1]
            if cleaned.lstrip().lower().startswith("json"):
                cleaned = cleaned.lstrip()[4:]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


def _parse_contribution(content):
    d = _extract_json(content)
    if not d or "contribution" not in d:
        return None
    try:
        c = int(round(float(d["contribution"])))
    except (TypeError, ValueError):
        return None
    return {"contribution": max(0, min(ENDOWMENT, c)), "reasoning": str(d.get("reasoning", ""))}


def _make_deduction_parser(me):
    def parse(content):
        d = _extract_json(content)
        if not d or not isinstance(d.get("deductions"), dict):
            return None
        out = {}
        for lab, v in d["deductions"].items():
            lab = str(lab).strip().replace("Player ", "").upper()
            if lab in LABELS and lab != me:
                try:
                    out[lab] = max(0, min(MAX_POINTS, int(round(float(v)))))
                except (TypeError, ValueError):
                    return None
        return {"deductions": out, "reasoning": str(d.get("reasoning", ""))}
    return parse


# ---------------------------------------------------------------- game logic

def _phase_of(rnd, order):
    first = "none" if order == "np" else "deduction"
    second = "deduction" if order == "np" else "none"
    return (1, first) if rnd <= PHASE_LEN else (2, second)


def _system_prompt(label, horizon):
    labels = ", ".join(LABELS)
    return P.SYSTEM_TEMPLATE.format(
        label=label, n=len(LABELS), labels=labels, endowment=ENDOWMENT,
        multiplier=MULTIPLIER, mpcr=round(MULTIPLIER / len(LABELS), 2),
        horizon_block=P.HORIZON_BLOCK[horizon].format(total_rounds=TOTAL_ROUNDS, phase_len=PHASE_LEN),
    )


def _history_text(me, history):
    if not history:
        return "(none yet: this is the first round)"
    lines = []
    for h in history:
        cs = ", ".join(f"{lab}={h['contributions'][lab]}" for lab in LABELS)
        line = f"Round {h['round']}: contributions {cs} | your earnings {h['payoff'][me]}"
        if h["phase_type"] == "deduction":
            got = sum(h["deductions"][src].get(me, 0) for src in LABELS if src != me)
            gave = sum(h["deductions"][me].values())
            line += f" | deduction points received {got}, assigned {gave}"
        lines.append(line)
    return "\n".join(lines)


def _round_line(rnd, horizon):
    return f"Round {rnd} of {TOTAL_ROUNDS}." if horizon == "visible" else f"Round {rnd}."


def _announcement(rnd, order, horizon):
    phase, ptype = _phase_of(rnd, order)
    if rnd not in (1, PHASE_LEN + 1):
        return ""
    start, end = (1, PHASE_LEN) if phase == 1 else (PHASE_LEN + 1, TOTAL_ROUNDS)
    key = "hidden" if horizon == "hidden" else ("visible_first" if phase == 1 else "visible")
    return P.PHASE_ANNOUNCEMENT[key].format(
        phase=phase, phase_len=PHASE_LEN, start=start, end=end, total_rounds=TOTAL_ROUNDS) + "\n"


def _phase_rules(ptype):
    return P.PHASE_RULES[ptype].format(max_points=MAX_POINTS, cost=COST, impact=IMPACT)


def run_one_game(run_id, order="np", horizon="visible", models=None):
    models = models or list(MODELS)
    assert len(models) == len(LABELS), "one model per player"
    rng = random.Random(run_id * 7919 + hash((order, horizon)) % 1000)
    shuffled = models[:]
    rng.shuffle(shuffled)  # labels carry no information about which model is which
    seat = dict(zip(LABELS, shuffled))
    systems = {lab: _system_prompt(lab, horizon) for lab in LABELS}

    history, totals = [], {lab: 0.0 for lab in LABELS}
    failures = 0
    with ThreadPoolExecutor(max_workers=len(LABELS)) as ex:
        for rnd in range(1, TOTAL_ROUNDS + 1):
            phase, ptype = _phase_of(rnd, order)

            def contrib_call(lab):
                user = P.CONTRIBUTION_USER_TEMPLATE.format(
                    announcement=_announcement(rnd, order, horizon),
                    phase_rules=_phase_rules(ptype),
                    round_line=_round_line(rnd, horizon),
                    total_earnings=round(totals[lab], 1),
                    history=_history_text(lab, history),
                    endowment=ENDOWMENT,
                )
                msgs = [{"role": "system", "content": systems[lab]}, {"role": "user", "content": user}]
                return _query(MODELS[seat[lab]], msgs, _parse_contribution)

            res = dict(zip(LABELS, ex.map(contrib_call, LABELS)))
            contributions, reasoning, flags = {}, {}, {}
            for lab, (parsed, raw) in res.items():
                if parsed is None:
                    failures += 1
                    flags[lab] = "parse_failed"
                    contributions[lab], reasoning[lab] = 0, raw[:300]
                else:
                    contributions[lab], reasoning[lab] = parsed["contribution"], parsed["reasoning"]

            share = MULTIPLIER * sum(contributions.values()) / len(LABELS)
            gross = {lab: ENDOWMENT - contributions[lab] + share for lab in LABELS}
            deductions = {lab: {} for lab in LABELS}
            ded_reasoning = {}

            if ptype == "deduction":
                table = "\n".join(f"Player {lab}: {contributions[lab]}" for lab in LABELS)

                def ded_call(lab):
                    others = [o for o in LABELS if o != lab]
                    user = P.DEDUCTION_USER_TEMPLATE.format(
                        round_line=_round_line(rnd, horizon).rstrip("."),
                        contrib_table=table, max_points=MAX_POINTS, cost=COST, impact=IMPACT,
                        example=", ".join(f'"{o}": <0-{MAX_POINTS}>' for o in others),
                    )
                    msgs = [{"role": "system", "content": systems[lab]}, {"role": "user", "content": user}]
                    return _query(MODELS[seat[lab]], msgs, _make_deduction_parser(lab))

                dres = dict(zip(LABELS, ex.map(ded_call, LABELS)))
                for lab, (parsed, raw) in dres.items():
                    if parsed is None:
                        failures += 1
                        flags[lab] = "deduction_parse_failed"
                        ded_reasoning[lab] = raw[:300]
                    else:
                        deductions[lab] = parsed["deductions"]
                        ded_reasoning[lab] = parsed["reasoning"]

            payoff = {}
            for lab in LABELS:
                received = sum(deductions[src].get(lab, 0) for src in LABELS if src != lab)
                spent = COST * sum(deductions[lab].values())
                payoff[lab] = round(max(0.0, gross[lab] - IMPACT * received) - spent, 2)
                totals[lab] += payoff[lab]

            history.append({
                "round": rnd, "phase": phase, "phase_type": ptype,
                "contributions": contributions, "reasoning": reasoning,
                "deductions": deductions, "deduction_reasoning": ded_reasoning,
                "payoff": payoff, "flags": flags,
            })

    return {
        "run_id": run_id, "order": order, "horizon": horizon,
        "seats": seat,
        "params": {"endowment": ENDOWMENT, "multiplier": MULTIPLIER, "phase_len": PHASE_LEN,
                   "max_points": MAX_POINTS, "cost": COST, "impact": IMPACT,
                   "temperature": TEMPERATURE, "mock": MOCK},
        "rounds": history,
        "totals": {lab: round(v, 2) for lab, v in totals.items()},
        "parse_failures": failures,
    }
