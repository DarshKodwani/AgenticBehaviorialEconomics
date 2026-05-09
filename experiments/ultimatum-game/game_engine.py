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

JSON_RETRY_REMINDER = (
    "Your previous response was not valid JSON. "
    "Please respond with ONLY a single JSON object in the exact format specified, "
    "and no other text before or after."
)


def _call_openrouter(model_id, messages, max_retries=3, force_json=True):
    """Call OpenRouter chat completions and return the raw assistant string.

    `force_json=True` adds response_format={"type": "json_object"}, which is
    honored by all major providers (OpenAI, Anthropic, Google, DeepSeek);
    others ignore it without error.
    """
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
    if force_json:
        payload["response_format"] = {"type": "json_object"}

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


def _query_with_json_retry(model_id, messages, strict_parser):
    """Call the API, try to parse strictly; on failure, retry once with an
    explicit JSON-only reminder. Returns (parsed_dict_or_None, raw_assistant_str).
    """
    raw = _call_openrouter(model_id, messages)
    parsed = strict_parser(raw)
    if parsed is not None:
        return parsed, raw
    retry_messages = list(messages) + [
        {"role": "assistant", "content": raw or ""},
        {"role": "user", "content": JSON_RETRY_REMINDER},
    ]
    raw2 = _call_openrouter(model_id, retry_messages)
    parsed2 = strict_parser(raw2)
    if parsed2 is not None:
        return parsed2, raw2
    return None, raw2 or raw


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


def _strict_parse_offer(content: str):
    """Strict: returns dict on success, None on any failure. No keyword
    fallback — that was masking JSON-format failures as decisions.
    """
    parsed = _extract_json(content)
    if not parsed or "offer_to_responder" not in parsed:
        return None
    try:
        offer = float(parsed["offer_to_responder"])
    except (TypeError, ValueError):
        return None
    offer = max(0.0, min(100.0, offer))
    return {"offer": offer, "reasoning": str(parsed.get("reasoning", ""))}


def _strict_parse_decision(content: str):
    parsed = _extract_json(content)
    if not parsed or "decision" not in parsed:
        return None
    raw = str(parsed["decision"]).strip().upper()
    if raw.startswith("A"):
        return {"decision": "ACCEPT", "reasoning": str(parsed.get("reasoning", ""))}
    if raw.startswith("R"):
        return {"decision": "REJECT", "reasoning": str(parsed.get("reasoning", ""))}
    return None


def _strict_parse_threshold(content: str):
    parsed = _extract_json(content)
    if not parsed or "min_acceptable_offer" not in parsed:
        return None
    try:
        t = float(parsed["min_acceptable_offer"])
    except (TypeError, ValueError):
        return None
    t = max(0.0, min(100.0, t))
    return {"min_acceptable_offer": t, "reasoning": str(parsed.get("reasoning", ""))}


def _strict_parse_belief(content: str):
    parsed = _extract_json(content)
    if not parsed or "counterparty_belief" not in parsed:
        return None
    b = str(parsed["counterparty_belief"]).strip().lower()
    if b in ("human", "ai", "unsure"):
        return {"counterparty_belief": b, "reasoning": str(parsed.get("reasoning", ""))}
    return None


def query_proposer(model_name: str, condition: str):
    system = prompts.proposer_system(condition)
    user = "Make your offer."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    parsed, raw = _query_with_json_retry(MODELS[model_name], messages, _strict_parse_offer)
    if parsed is None:
        return {
            "offer": None,
            "reasoning": (raw or "")[:300],
            "parse_ok": False,
            "raw": raw,
            "messages": messages,
        }
    return {
        "offer": parsed["offer"],
        "reasoning": parsed["reasoning"],
        "parse_ok": True,
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
    parsed, raw = _query_with_json_retry(MODELS[model_name], messages, _strict_parse_decision)
    if parsed is None:
        return {
            "decision": None,
            "reasoning": (raw or "")[:300],
            "parse_ok": False,
            "raw": raw,
            "messages": messages,
        }
    return {
        "decision": parsed["decision"],
        "reasoning": parsed["reasoning"],
        "parse_ok": True,
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
    parsed, raw = _query_with_json_retry(MODELS[model_name], messages, _strict_parse_threshold)
    if parsed is None:
        return {
            "min_acceptable_offer": None,
            "reasoning": (raw or "")[:300],
            "parse_ok": False,
            "raw": raw,
            "messages": messages,
        }
    return {
        "min_acceptable_offer": parsed["min_acceptable_offer"],
        "reasoning": parsed["reasoning"],
        "parse_ok": True,
        "raw": raw,
        "messages": messages,
    }


def query_manipulation_check(model_name: str, prior_messages, prior_assistant_raw: str):
    """Follow-up turn on the same conversation, asking about counterparty belief."""
    messages = list(prior_messages) + [
        {"role": "assistant", "content": prior_assistant_raw or ""},
        {"role": "user", "content": prompts.MANIPULATION_CHECK_USER},
    ]
    parsed, raw = _query_with_json_retry(MODELS[model_name], messages, _strict_parse_belief)
    if parsed is None:
        return {
            "counterparty_belief": None,
            "reasoning": (raw or "")[:300],
            "parse_ok": False,
            "raw": raw,
        }
    return {
        "counterparty_belief": parsed["counterparty_belief"],
        "reasoning": parsed["reasoning"],
        "parse_ok": True,
        "raw": raw,
    }


def run_one_round(proposer_name: str, responder_name: str, condition: str, run_id: int,
                  with_mc: bool = True):
    """Run a single ultimatum-game round end-to-end and return a per-run record."""
    p = query_proposer(proposer_name, condition)

    # If the proposer failed to produce a valid offer even after retry, we
    # can't run the responder (no offer to show). Mark the round failed.
    if p["offer"] is None:
        record = {
            "run_id": run_id,
            "offer": None,
            "proposer_reasoning": p["reasoning"],
            "proposer_parse_ok": False,
            "decision": None,
            "responder_reasoning": "",
            "responder_parse_ok": False,
            "round_failed": True,
        }
        if with_mc:
            record.update({
                "mc_proposer_belief": None, "mc_proposer_reasoning": "",
                "mc_responder_belief": None, "mc_responder_reasoning": "",
            })
        return record

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
