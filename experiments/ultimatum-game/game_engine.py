"""Ultimatum Game engine with LLM agents via OpenRouter.

One round = a proposer offer, a responder decision, and (optionally) a
manipulation-check follow-up to each role asking who they thought they
were playing.
"""
import os
import json
import re
import time
import requests
from dotenv import load_dotenv

import prompts


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

TEMPERATURE = 0.7
MAX_TOKENS = 250


def _call_openrouter(model_id, messages, max_retries=3):
    """Call OpenRouter chat completions and return the raw assistant string."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    print(f"  LLM query failed after {max_retries} attempts: {last_err}")
    return ""


def _extract_json(content: str):
    """Best-effort JSON extraction from a model response."""
    if not content:
        return None
    cleaned = content
    if "```" in cleaned:
        chunks = cleaned.split("```")
        if len(chunks) >= 2:
            cleaned = chunks[1]
            if cleaned.lstrip().lower().startswith("json"):
                cleaned = cleaned.lstrip()[4:]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _parse_offer(content: str):
    parsed = _extract_json(content)
    if parsed and "offer_to_responder" in parsed:
        try:
            offer = float(parsed["offer_to_responder"])
            offer = max(0.0, min(100.0, offer))
            return offer, parsed.get("reasoning", ""), True
        except (TypeError, ValueError):
            pass
    match = re.search(r"-?\d+(?:\.\d+)?", content or "")
    if match:
        try:
            offer = float(match.group(0))
            offer = max(0.0, min(100.0, offer))
            return offer, content[:200], False
        except ValueError:
            pass
    return 50.0, content[:200] if content else "fallback", False


def _parse_decision(content: str):
    parsed = _extract_json(content)
    if parsed and "decision" in parsed:
        decision = str(parsed["decision"]).strip().upper()
        if decision.startswith("A"):
            return "ACCEPT", parsed.get("reasoning", ""), True
        if decision.startswith("R"):
            return "REJECT", parsed.get("reasoning", ""), True
    upper = (content or "").upper()
    if "REJECT" in upper:
        return "REJECT", content[:200], False
    if "ACCEPT" in upper:
        return "ACCEPT", content[:200], False
    return "REJECT", content[:200] if content else "fallback", False


def _parse_threshold(content: str):
    parsed = _extract_json(content)
    if parsed and "min_acceptable_offer" in parsed:
        try:
            t = float(parsed["min_acceptable_offer"])
            t = max(0.0, min(100.0, t))
            return t, parsed.get("reasoning", ""), True
        except (TypeError, ValueError):
            pass
    match = re.search(r"-?\d+(?:\.\d+)?", content or "")
    if match:
        try:
            t = float(match.group(0))
            t = max(0.0, min(100.0, t))
            return t, content[:200], False
        except ValueError:
            pass
    return 0.0, content[:200] if content else "fallback", False


def _parse_belief(content: str):
    parsed = _extract_json(content)
    if parsed and "counterparty_belief" in parsed:
        b = str(parsed["counterparty_belief"]).strip().lower()
        if b in ("human", "ai", "unsure"):
            return b, parsed.get("reasoning", ""), True
    upper = (content or "").lower()
    if "human" in upper and "ai" not in upper:
        return "human", content[:200], False
    if "ai" in upper and "human" not in upper:
        return "ai", content[:200], False
    return "unsure", content[:200] if content else "fallback", False


def query_proposer(model_name: str, condition: str):
    system = prompts.proposer_system(condition)
    user = "Make your offer."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    raw = _call_openrouter(MODELS[model_name], messages)
    offer, reasoning, parse_ok = _parse_offer(raw)
    return {
        "offer": offer,
        "reasoning": reasoning,
        "parse_ok": parse_ok,
        "raw": raw,
        "messages": messages,
    }


def query_responder(model_name: str, condition: str, offer: float):
    system = prompts.responder_system(condition)
    user = prompts.responder_user(offer)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    raw = _call_openrouter(MODELS[model_name], messages)
    decision, reasoning, parse_ok = _parse_decision(raw)
    return {
        "decision": decision,
        "reasoning": reasoning,
        "parse_ok": parse_ok,
        "raw": raw,
        "messages": messages,
    }


def query_strategy_method(model_name: str, condition: str):
    system = prompts.strategy_method_system(condition)
    user = prompts.STRATEGY_METHOD_USER
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    raw = _call_openrouter(MODELS[model_name], messages)
    threshold, reasoning, parse_ok = _parse_threshold(raw)
    return {
        "min_acceptable_offer": threshold,
        "reasoning": reasoning,
        "parse_ok": parse_ok,
        "raw": raw,
        "messages": messages,
    }


def query_manipulation_check(model_name: str, prior_messages, prior_assistant_raw: str):
    """Follow-up turn on the same conversation, asking about counterparty belief."""
    messages = list(prior_messages) + [
        {"role": "assistant", "content": prior_assistant_raw or ""},
        {"role": "user", "content": prompts.MANIPULATION_CHECK_USER},
    ]
    raw = _call_openrouter(MODELS[model_name], messages)
    belief, reasoning, parse_ok = _parse_belief(raw)
    return {
        "counterparty_belief": belief,
        "reasoning": reasoning,
        "parse_ok": parse_ok,
        "raw": raw,
    }


def run_one_round(proposer_name: str, responder_name: str, condition: str, run_id: int,
                  with_mc: bool = True):
    """Run a single ultimatum-game round end-to-end and return a per-run record."""
    p = query_proposer(proposer_name, condition)
    r = query_responder(responder_name, condition, p["offer"])

    record = {
        "run_id": run_id,
        "offer": p["offer"],
        "proposer_reasoning": p["reasoning"],
        "proposer_parse_ok": p["parse_ok"],
        "decision": r["decision"],
        "responder_reasoning": r["reasoning"],
        "responder_parse_ok": r["parse_ok"],
    }

    if with_mc:
        mc_p = query_manipulation_check(proposer_name, p["messages"], p["raw"])
        mc_r = query_manipulation_check(responder_name, r["messages"], r["raw"])
        record["mc_proposer_belief"] = mc_p["counterparty_belief"]
        record["mc_proposer_reasoning"] = mc_p["reasoning"]
        record["mc_responder_belief"] = mc_r["counterparty_belief"]
        record["mc_responder_reasoning"] = mc_r["reasoning"]

    return record


def run_one_strategy_method(responder_name: str, condition: str, run_id: int,
                            with_mc: bool = True):
    """Run a single strategy-method elicitation and return a per-run record."""
    s = query_strategy_method(responder_name, condition)
    record = {
        "run_id": run_id,
        "min_acceptable_offer": s["min_acceptable_offer"],
        "reasoning": s["reasoning"],
        "parse_ok": s["parse_ok"],
    }
    if with_mc:
        mc = query_manipulation_check(responder_name, s["messages"], s["raw"])
        record["mc_belief"] = mc["counterparty_belief"]
        record["mc_reasoning"] = mc["reasoning"]
    return record
