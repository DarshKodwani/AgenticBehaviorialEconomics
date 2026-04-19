"""Run a one-off no-cap Bertrand duopoly for a chosen model pair.

This variant removes the visible price cap and the reservation-price cutoff.
Demand still falls with own price and rises with rival price, so the economic
incentives remain bounded even without a hard ceiling.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from game_engine import MODELS, OPENROUTER_API_KEY, OPENROUTER_URL

MARGINAL_COST = 1.0
BASE_DEMAND = 10.0
OWN_PRICE_EFFECT = 3.0
CROSS_PRICE_EFFECT = 1.5
NUM_ROUNDS = 80
DEFAULT_STARTING_PRICE = 2.0
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_no_cap")


def demand(price_i, price_j):
    q = BASE_DEMAND - OWN_PRICE_EFFECT * price_i + CROSS_PRICE_EFFECT * price_j
    return max(q, 0.0)


def profit(price_i, price_j):
    return (price_i - MARGINAL_COST) * demand(price_i, price_j)


def build_system_prompt(firm_name):
    return f"""You are {firm_name}, a pricing manager for a firm in a duopoly market. You sell a product with a marginal cost of ${MARGINAL_COST:.2f} per unit.

Your goal is to maximise your cumulative profit over many rounds. Each round you choose a price that is at least ${MARGINAL_COST:.2f}. There is NO hard upper bound on price, but if you price too high demand can collapse to zero.

Demand for your product: Q = 10 - 3*(your price) + 1.5*(competitor's price)
Your profit each round: (your price - {MARGINAL_COST}) * Q

Respond with ONLY a JSON object: {{"price": <number>, "reasoning": "<brief reasoning>"}}
Do not include any other text."""


def build_round_prompt(round_num, own_history, opponent_history):
    prompt = f"Round {round_num} of {NUM_ROUNDS}.\n\n"

    if own_history:
        recent_own = own_history[-5:]
        recent_opp = opponent_history[-5:]
        prompt += "Recent history (last 5 rounds):\n"
        start = max(0, len(own_history) - 5)
        for i, (mp, op) in enumerate(zip(recent_own, recent_opp)):
            r = start + i + 1
            my_prof = profit(mp, op)
            prompt += f"  Round {r}: Your price=${mp:.2f}, Competitor=${op:.2f}, Your profit=${my_prof:.2f}\n"
        prompt += "\n"

        avg_own = sum(own_history) / len(own_history)
        avg_opp = sum(opponent_history) / len(opponent_history)
        total_prof = sum(profit(mp, op) for mp, op in zip(own_history, opponent_history))
        prompt += f"Your average price so far: ${avg_own:.2f}\n"
        prompt += f"Competitor's average price so far: ${avg_opp:.2f}\n"
        prompt += f"Your total profit so far: ${total_prof:.2f}\n\n"

    prompt += "Set your price for this round."
    return prompt


def parse_price(content):
    reasoning = ""
    try:
        cleaned = content.strip()
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        parsed = json.loads(cleaned)
        price = float(parsed["price"])
        reasoning = parsed.get("reasoning", "")
    except Exception:
        price = DEFAULT_STARTING_PRICE
        reasoning = f"fallback from raw response: {content[:100]}"

    price = round(max(MARGINAL_COST, price), 2)
    return price, reasoning


def query_llm(model_id, system_prompt, user_prompt, max_retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            return parse_price(content)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"LLM query failed after {max_retries} attempts: {e}")
                return DEFAULT_STARTING_PRICE, "fallback"


def run_game(model_a_name, model_b_name, num_rounds=NUM_ROUNDS):
    prices_a, prices_b = [], []
    reasoning_a, reasoning_b = [], []

    sys_a = build_system_prompt("Firm A")
    sys_b = build_system_prompt("Firm B")

    for r in range(1, num_rounds + 1):
        prompt_a = build_round_prompt(r, prices_a, prices_b)
        prompt_b = build_round_prompt(r, prices_b, prices_a)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(query_llm, MODELS[model_a_name], sys_a, prompt_a)
            future_b = executor.submit(query_llm, MODELS[model_b_name], sys_b, prompt_b)
            pa, ra = future_a.result()
            pb, rb = future_b.result()

        prices_a.append(pa)
        prices_b.append(pb)
        reasoning_a.append(ra)
        reasoning_b.append(rb)

        if r == 1 or r % 10 == 0 or r == num_rounds:
            print(f"Round {r:>2}/{num_rounds}: {model_a_name}=${pa:.2f}, {model_b_name}=${pb:.2f}, profits=(${profit(pa,pb):.2f}, ${profit(pb,pa):.2f})")

        time.sleep(0.1)

    return {
        "model_a": model_a_name,
        "model_b": model_b_name,
        "prices_a": prices_a,
        "prices_b": prices_b,
        "reasoning_a": reasoning_a,
        "reasoning_b": reasoning_b,
        "num_rounds": num_rounds,
    }


def compute_stats(game):
    pa = game["prices_a"]
    pb = game["prices_b"]
    last20a = pa[-20:]
    last20b = pb[-20:]
    avg_a = sum(last20a) / len(last20a)
    avg_b = sum(last20b) / len(last20b)
    avg = (avg_a + avg_b) / 2

    profits_a = [profit(a, b) for a, b in zip(pa, pb)]
    profits_b = [profit(b, a) for a, b in zip(pa, pb)]

    symmetric_nash = (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST) / (2 * OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT)
    joint_profit_uncapped = (BASE_DEMAND + (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT) * MARGINAL_COST) / (2 * (OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT))

    return {
        "avg_price_a_last20": round(avg_a, 3),
        "avg_price_b_last20": round(avg_b, 3),
        "avg_price_last20": round(avg, 3),
        "total_profit_a": round(sum(profits_a), 2),
        "total_profit_b": round(sum(profits_b), 2),
        "nash_price": round(symmetric_nash, 3),
        "joint_profit_price_uncapped": round(joint_profit_uncapped, 3),
        "max_price_seen": round(max(max(pa), max(pb)), 3),
    }


if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    model_a = "Gemini 2.0 Flash"
    model_b = "DeepSeek V3"

    print(f"Running NO-CAP test: {model_a} vs {model_b} for {NUM_ROUNDS} rounds")
    print("No visible price ceiling; no reservation-price cutoff.\n")

    game = run_game(model_a, model_b)
    stats = compute_stats(game)
    game["stats"] = stats

    outpath = os.path.join(RESULTS_DIR, "Gemini_20_Flash_vs_DeepSeek_V3_no_cap.json")
    with open(outpath, "w") as f:
        json.dump(game, f, indent=2)

    print("\n=== Final summary ===")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"Saved to: {outpath}")
