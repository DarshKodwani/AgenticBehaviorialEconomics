"""Iterated Prisoner's Dilemma game engine with LLM agents."""
import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

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

# Classic PD payoff matrix
# (my_payoff, their_payoff) indexed by (my_action, their_action)
PAYOFFS = {
    ("C", "C"): (3, 3),   # mutual cooperation
    ("C", "D"): (0, 5),   # sucker's payoff
    ("D", "C"): (5, 0),   # temptation
    ("D", "D"): (1, 1),   # mutual defection
}

NUM_ROUNDS = 100


def payoff_name(action_self, action_other):
    return PAYOFFS[(action_self, action_other)][0]


def build_system_prompt(player_name):
    return f"""You are {player_name} in an iterated Prisoner's Dilemma game.

Each round you choose: COOPERATE or DEFECT.

Payoff matrix (your points, opponent's points):
  Both COOPERATE:        3, 3
  You COOPERATE, they DEFECT:  0, 5
  You DEFECT, they COOPERATE:  5, 0
  Both DEFECT:           1, 1

Your goal is to maximise your total points over many rounds.

Respond with ONLY a JSON object: {{"action": "C" or "D", "reasoning": "<brief reasoning>"}}
Do not include any other text. Use "C" for cooperate, "D" for defect."""


def build_round_prompt(round_num, own_history, opponent_history, hide_total=False):
    if hide_total:
        prompt = f"Round {round_num}.\n\n"
    else:
        prompt = f"Round {round_num} of {NUM_ROUNDS}.\n\n"

    if len(own_history) > 0:
        # show last 10 rounds
        window = min(10, len(own_history))
        recent_own = own_history[-window:]
        recent_opp = opponent_history[-window:]
        start = len(own_history) - window
        prompt += f"Recent history (last {window} rounds):\n"
        for i, (ma, oa) in enumerate(zip(recent_own, recent_opp)):
            r = start + i + 1
            my_pts = payoff_name(ma, oa)
            label_me = "COOPERATE" if ma == "C" else "DEFECT"
            label_them = "COOPERATE" if oa == "C" else "DEFECT"
            prompt += f"  Round {r}: You={label_me}, Opponent={label_them}, Your points={my_pts}\n"
        prompt += "\n"

        # summary stats
        my_coops = own_history.count("C")
        their_coops = opponent_history.count("C")
        total_pts = sum(payoff_name(m, o) for m, o in zip(own_history, opponent_history))
        prompt += f"Your cooperation rate: {my_coops}/{len(own_history)} ({100*my_coops/len(own_history):.0f}%)\n"
        prompt += f"Opponent's cooperation rate: {their_coops}/{len(opponent_history)} ({100*their_coops/len(opponent_history):.0f}%)\n"
        prompt += f"Your total points so far: {total_pts}\n\n"

    prompt += "Choose your action for this round."
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
        "max_tokens": 150,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            return parse_action(content)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  LLM query failed after {max_retries} attempts: {e}")
                return "C", "fallback"


def parse_action(content):
    """Extract C or D from LLM response."""
    reasoning = ""
    try:
        cleaned = content
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        parsed = json.loads(cleaned)
        action = parsed["action"].upper().strip()
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, KeyError, ValueError):
        # fallback: look for cooperate/defect keywords
        upper = content.upper()
        if "DEFECT" in upper or '"D"' in content or "'D'" in content:
            action = "D"
        else:
            action = "C"
        reasoning = content[:100]

    # normalise
    if action.startswith("C"):
        action = "C"
    elif action.startswith("D"):
        action = "D"
    else:
        action = "C"  # default to cooperate if unclear

    return action, reasoning


def run_game(model_a_name, model_b_name, num_rounds=NUM_ROUNDS, progress_callback=None, hide_total=False):
    """Run a full iterated PD between two models."""
    model_a_id = MODELS[model_a_name]
    model_b_id = MODELS[model_b_name]

    sys_a = build_system_prompt("Player A")
    sys_b = build_system_prompt("Player B")

    actions_a = []
    actions_b = []
    reasoning_a = []
    reasoning_b = []

    for r in range(1, num_rounds + 1):
        prompt_a = build_round_prompt(r, actions_a, actions_b, hide_total=hide_total)
        prompt_b = build_round_prompt(r, actions_b, actions_a, hide_total=hide_total)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(query_llm, model_a_id, sys_a, prompt_a)
            future_b = executor.submit(query_llm, model_b_id, sys_b, prompt_b)
            aa, ra = future_a.result()
            ab, rb = future_b.result()

        actions_a.append(aa)
        actions_b.append(ab)
        reasoning_a.append(ra)
        reasoning_b.append(rb)

        if progress_callback:
            progress_callback(r, num_rounds, aa, ab)

        time.sleep(0.1)

    return {
        "model_a": model_a_name,
        "model_b": model_b_name,
        "actions_a": actions_a,
        "actions_b": actions_b,
        "reasoning_a": reasoning_a,
        "reasoning_b": reasoning_b,
        "num_rounds": num_rounds,
    }


def compute_stats(game_result):
    """Compute summary statistics for a game."""
    aa = game_result["actions_a"]
    ab = game_result["actions_b"]
    n = len(aa)

    # cooperation rates
    coop_rate_a = aa.count("C") / n
    coop_rate_b = ab.count("C") / n

    # last 20 rounds
    last_a = aa[-20:]
    last_b = ab[-20:]
    coop_rate_a_last20 = last_a.count("C") / len(last_a)
    coop_rate_b_last20 = last_b.count("C") / len(last_b)

    # total points
    points_a = sum(payoff_name(a, b) for a, b in zip(aa, ab))
    points_b = sum(payoff_name(b, a) for a, b in zip(aa, ab))

    # mutual cooperation rate
    mutual_coop = sum(1 for a, b in zip(aa, ab) if a == "C" and b == "C") / n
    mutual_defect = sum(1 for a, b in zip(aa, ab) if a == "D" and b == "D") / n
    mutual_coop_last20 = sum(1 for a, b in zip(last_a, last_b) if a == "C" and b == "C") / len(last_a)

    return {
        "coop_rate_a": round(coop_rate_a, 3),
        "coop_rate_b": round(coop_rate_b, 3),
        "coop_rate_a_last20": round(coop_rate_a_last20, 3),
        "coop_rate_b_last20": round(coop_rate_b_last20, 3),
        "mutual_coop_rate": round(mutual_coop, 3),
        "mutual_defect_rate": round(mutual_defect, 3),
        "mutual_coop_last20": round(mutual_coop_last20, 3),
        "points_a": points_a,
        "points_b": points_b,
    }
