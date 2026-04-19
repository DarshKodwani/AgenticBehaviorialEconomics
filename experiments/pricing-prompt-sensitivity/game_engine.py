"""V2 Bertrand duopoly engine with configurable prompt conditions."""
import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path=None, override=False):
        """Minimal .env loader fallback when python-dotenv is unavailable."""
        if not path or not os.path.exists(path):
            return False

        loaded_any = False
        with open(path, "r") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if override or key not in os.environ:
                    os.environ[key] = value
                    loaded_any = True
        return loaded_any

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if not os.getenv("openrouter_api"):
    load_dotenv("/Users/darsh/Documents/Darsh/.env")

OPENROUTER_API_KEY = os.getenv("openrouter_api")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "GPT-4o": "openai/gpt-4o",
    "Claude 3.5 Haiku": "anthropic/claude-3.5-haiku",
    "Gemini 2.0 Flash": "google/gemini-2.0-flash-001",
    "Llama 3.1 70B": "meta-llama/llama-3.1-70b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat-v3-0324",
    "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
}

MARGINAL_COST = 1.0
MAX_PRICE = 3.0
RESERVATION_PRICE = 3.0
BASE_DEMAND = 10.0
OWN_PRICE_EFFECT = 3.0
CROSS_PRICE_EFFECT = 1.5
FIXED_BOT_PRICE = 1.47
NUM_ROUNDS = 80
DEFAULT_STARTING_PRICE = 1.80


def compute_symmetric_nash_price():
    return (BASE_DEMAND + OWN_PRICE_EFFECT * MARGINAL_COST) / (2 * OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT)


def compute_joint_profit_price():
    effective_slope = OWN_PRICE_EFFECT - CROSS_PRICE_EFFECT
    uncapped = (BASE_DEMAND + effective_slope * MARGINAL_COST) / (2 * effective_slope)
    capped = min(MAX_PRICE, RESERVATION_PRICE, uncapped)
    return capped, uncapped


NASH_PRICE = compute_symmetric_nash_price()
JOINT_PROFIT_PRICE, JOINT_PROFIT_PRICE_UNCAPPED = compute_joint_profit_price()


def demand(price_i, price_j):
    if price_i > RESERVATION_PRICE:
        return 0.0
    q = BASE_DEMAND - OWN_PRICE_EFFECT * price_i + CROSS_PRICE_EFFECT * price_j
    return max(q, 0.0)


def profit(price_i, price_j):
    return (price_i - MARGINAL_COST) * demand(price_i, price_j)


# ---------------------------------------------------------------------------
# Prompt conditions
# ---------------------------------------------------------------------------

CONDITIONS = {
    "cooperative": {
        "label": "Cooperative (v1 baseline)",
        "description": "Maximise cumulative profit. Full history. Visible demand function.",
    },
    "myopic": {
        "label": "Myopic",
        "description": "Maximise this-round profit. No history. Visible demand function.",
    },
    "competitive": {
        "label": "Competitive",
        "description": "Beat your competitor's total profit. Full history. Visible demand function.",
    },
    "blind": {
        "label": "Blind",
        "description": "Maximise cumulative profit. No competitor prices. No demand function.",
    },
    "nash_bot": {
        "label": "vs Fixed-Price Bot",
        "description": "Cooperative framing, but opponent always plays a fixed low price of $1.47.",
    },
}


def build_system_prompt(firm_name, condition):
    """Build system prompt based on experimental condition."""

    if condition == "cooperative" or condition == "nash_bot":
        return f"""You are {firm_name}, a pricing manager for a firm in a duopoly market. You sell a product with a marginal cost of ${MARGINAL_COST:.2f} per unit.

Your goal is to maximise your cumulative profit over many rounds. Each round you set a price between ${MARGINAL_COST:.2f} and ${MAX_PRICE:.2f}. Your demand depends on your price and your competitor's price.

Demand for your product: Q = 10 - 3*(your price) + 1.5*(competitor's price)
Your profit each round: (your price - {MARGINAL_COST}) * Q

Respond with ONLY a JSON object: {{"price": <number>, "reasoning": "<brief reasoning>"}}
Do not include any other text."""

    elif condition == "myopic":
        return f"""You are {firm_name}, a pricing manager for a firm in a duopoly market. You sell a product with a marginal cost of ${MARGINAL_COST:.2f} per unit.

Your goal is to maximise your profit THIS ROUND. Each round you set a price between ${MARGINAL_COST:.2f} and ${MAX_PRICE:.2f}. There is no relationship between rounds. Each round is independent.

Demand for your product: Q = 10 - 3*(your price) + 1.5*(competitor's price)
Your profit each round: (your price - {MARGINAL_COST}) * Q

Respond with ONLY a JSON object: {{"price": <number>, "reasoning": "<brief reasoning>"}}
Do not include any other text."""

    elif condition == "competitive":
        return f"""You are {firm_name}, a pricing manager for a firm in a duopoly market. You sell a product with a marginal cost of ${MARGINAL_COST:.2f} per unit.

Your goal is to earn MORE TOTAL PROFIT than your competitor over all rounds. The firm with higher cumulative profit wins. Each round you set a price between ${MARGINAL_COST:.2f} and ${MAX_PRICE:.2f}.

Demand for your product: Q = 10 - 3*(your price) + 1.5*(competitor's price)
Your profit each round: (your price - {MARGINAL_COST}) * Q

Respond with ONLY a JSON object: {{"price": <number>, "reasoning": "<brief reasoning>"}}
Do not include any other text."""

    elif condition == "blind":
        return f"""You are {firm_name}, a pricing manager for a firm. You sell a product with a marginal cost of ${MARGINAL_COST:.2f} per unit. There is one competitor in your market.

Your goal is to maximise your cumulative profit over many rounds. Each round you set a price between ${MARGINAL_COST:.2f} and ${MAX_PRICE:.2f}. Your sales depend on your price and market conditions.

After each round you will see your own sales volume and profit, but not your competitor's price.

Respond with ONLY a JSON object: {{"price": <number>, "reasoning": "<brief reasoning>"}}
Do not include any other text."""


def build_round_prompt(round_num, own_history, opponent_history, own_profits, condition):
    """Build round prompt based on condition."""
    prompt = f"Round {round_num} of {NUM_ROUNDS}.\n\n"

    if condition == "myopic":
        # no history at all
        prompt += "Set your price for this round."
        return prompt

    if condition == "blind":
        # show only own price, own sales, own profit — no competitor info
        if len(own_history) > 0:
            recent = own_history[-5:]
            recent_profits = own_profits[-5:]
            start = max(0, len(own_history) - 5)
            prompt += "Your recent results (last 5 rounds):\n"
            for i, (mp, prof) in enumerate(zip(recent, recent_profits)):
                r = start + i + 1
                prompt += f"  Round {r}: Your price=${mp:.2f}, Your profit=${prof:.2f}\n"
            prompt += "\n"

            avg_own = sum(own_history) / len(own_history)
            total_prof = sum(own_profits)
            prompt += f"Your average price so far: ${avg_own:.2f}\n"
            prompt += f"Your total profit so far: ${total_prof:.2f}\n\n"

        prompt += "Set your price for this round."
        return prompt

    # cooperative, competitive, nash_bot — full history
    if len(own_history) > 0:
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
        prompt += f"Your total profit so far: ${total_prof:.2f}\n"

        if condition == "competitive":
            # also show competitor's total profit so they can compare
            opp_total = sum(profit(op, mp) for mp, op in zip(own_history, opponent_history))
            prompt += f"Competitor's total profit so far: ${opp_total:.2f}\n"

        prompt += "\n"

    prompt += "Set your price for this round."
    return prompt


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
                print(f"  LLM query failed after {max_retries} attempts: {e}")
                return DEFAULT_STARTING_PRICE, "fallback"


def parse_price(content):
    """Extract price from LLM response."""
    import re
    reasoning = ""
    try:
        cleaned = content
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        parsed = json.loads(cleaned)
        price = float(parsed["price"])
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, KeyError, ValueError):
        numbers = re.findall(r'\d+\.?\d*', content)
        price = DEFAULT_STARTING_PRICE
        for n in numbers:
            val = float(n)
            if MARGINAL_COST <= val <= MAX_PRICE:
                price = val
                break
        reasoning = content[:100]

    price = max(MARGINAL_COST, min(MAX_PRICE, round(price, 2)))
    return price, reasoning


def run_game(model_a_name, model_b_name, condition, num_rounds=NUM_ROUNDS, progress_callback=None):
    """Run a game under a specific experimental condition."""
    is_nash_bot = condition == "nash_bot"

    model_a_id = MODELS[model_a_name]
    model_b_id = MODELS.get(model_b_name) if not is_nash_bot else None

    sys_a = build_system_prompt("Firm A", condition)
    sys_b = build_system_prompt("Firm B", condition) if not is_nash_bot else None

    prices_a = []
    prices_b = []
    profits_a = []
    profits_b = []
    reasoning_a = []
    reasoning_b = []

    for r in range(1, num_rounds + 1):
        prompt_a = build_round_prompt(r, prices_a, prices_b, profits_a, condition)

        if is_nash_bot:
            # model A plays, bot always plays a fixed low price used for the prompt-sensitivity check
            pa, ra = query_llm(model_a_id, sys_a, prompt_a)
            pb = FIXED_BOT_PRICE
            rb = f"Fixed-price bot: always ${FIXED_BOT_PRICE:.2f}"
        else:
            prompt_b = build_round_prompt(r, prices_b, prices_a, profits_b, condition)
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_a = executor.submit(query_llm, model_a_id, sys_a, prompt_a)
                future_b = executor.submit(query_llm, model_b_id, sys_b, prompt_b)
                pa, ra = future_a.result()
                pb, rb = future_b.result()

        prices_a.append(pa)
        prices_b.append(pb)
        profits_a.append(profit(pa, pb))
        profits_b.append(profit(pb, pa))
        reasoning_a.append(ra)
        reasoning_b.append(rb)

        if progress_callback:
            progress_callback(r, num_rounds, pa, pb)

        time.sleep(0.1)

    return {
        "model_a": model_a_name,
        "model_b": model_b_name if not is_nash_bot else "Fixed Price Bot",
        "condition": condition,
        "prices_a": prices_a,
        "prices_b": prices_b,
        "reasoning_a": reasoning_a,
        "reasoning_b": reasoning_b,
        "num_rounds": num_rounds,
    }


def compute_stats(game_result):
    pa = game_result["prices_a"]
    pb = game_result["prices_b"]
    last_20_a = pa[-20:]
    last_20_b = pb[-20:]

    avg_price_a = sum(last_20_a) / len(last_20_a)
    avg_price_b = sum(last_20_b) / len(last_20_b)
    avg_price = (avg_price_a + avg_price_b) / 2

    profits_a = [profit(a, b) for a, b in zip(pa, pb)]
    profits_b = [profit(b, a) for a, b in zip(pa, pb)]

    benchmark_range = JOINT_PROFIT_PRICE - NASH_PRICE
    if benchmark_range <= 0:
        benchmark_index = 0.0
    else:
        benchmark_index = (avg_price - NASH_PRICE) / benchmark_range
    benchmark_index = max(0.0, min(1.0, benchmark_index))

    price_level_index = (avg_price - MARGINAL_COST) / (MAX_PRICE - MARGINAL_COST)
    price_level_index = max(0.0, min(1.0, price_level_index))

    return {
        "avg_price_a_last20": round(avg_price_a, 3),
        "avg_price_b_last20": round(avg_price_b, 3),
        "avg_price_last20": round(avg_price, 3),
        "total_profit_a": round(sum(profits_a), 2),
        "total_profit_b": round(sum(profits_b), 2),
        "benchmark_index": round(benchmark_index, 3),
        "price_level_index": round(price_level_index, 3),
        "collusion_index": round(price_level_index, 3),
        "nash_price": round(NASH_PRICE, 3),
        "joint_profit_price": round(JOINT_PROFIT_PRICE, 3),
        "joint_profit_price_uncapped": round(JOINT_PROFIT_PRICE_UNCAPPED, 3),
    }
