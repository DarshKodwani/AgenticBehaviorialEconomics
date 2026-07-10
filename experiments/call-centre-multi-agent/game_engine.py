"""Call-centre escalation engine with LLM agents via OpenRouter.

One run = a scripted customer working through the five-level pressure
gradient against a front-line agent (conditions B/C: with per-stage
escalation to a supervisor played by the same model). The customer is a
fixed script, not an LLM.

Per-stage escalation protocol (B/C): at every stage the front-line agent
replies to the customer, then the supervisor makes the binding decision
for that stage. The run stops at the first refund commitment that reaches
the customer (front-line grant or supervisor grant) — that stage is the
system yield point. Supervisor decisions are not relayed into the
front-line agent's context, so front-line behaviour stays comparable
across conditions A/B/C.
"""
import os
import json
import re
import time
import requests
from dotenv import load_dotenv

import prompts
import scripts


load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if not os.getenv("openrouter_api"):
    load_dotenv("/Users/darsh/Documents/Darsh/.env")

OPENROUTER_API_KEY = os.getenv("openrouter_api")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Note: the grid matches the earlier experiments where possible.
# anthropic/claude-3.5-haiku and google/gemini-2.0-flash-001 are no longer
# served on OpenRouter, so the nearest same-tier successors stand in.
MODELS = {
    "GPT-4o": "openai/gpt-4o",
    "Claude Haiku 4.5": "anthropic/claude-haiku-4.5",
    "Gemini 2.5 Flash": "google/gemini-2.5-flash",
    "Llama 3.1 70B": "meta-llama/llama-3.1-70b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat-v3-0324",
    "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
}

TEMPERATURE = 0.7
MAX_TOKENS_FRONTLINE = 400
MAX_TOKENS_FRONTLINE_SUMMARY = 650   # reply + handoff summary
MAX_TOKENS_SUPERVISOR = 300

FRONTLINE_ACTIONS = ("decline", "offer_goodwill_credit", "grant_refund")
SUPERVISOR_DECISIONS = ("uphold_decline", "grant_goodwill_credit", "grant_refund")

JSON_RETRY_REMINDER = (
    "Your previous response was not valid JSON. "
    "Please respond with ONLY a single JSON object in the exact format specified, "
    "and no other text before or after."
)


def _call_openrouter(model_id, messages, max_tokens, max_retries=5, force_json=True):
    """Call OpenRouter chat completions and return the raw assistant string."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": max_tokens,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    last_err = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    print(f"  LLM query failed after {max_retries} attempts: {last_err}")
    return ""


def _query_with_json_retry(model_id, messages, strict_parser, max_tokens):
    """Call the API, parse strictly; on failure retry once with an explicit
    JSON-only reminder. Returns (parsed_dict_or_None, raw_assistant_str)."""
    raw = _call_openrouter(model_id, messages, max_tokens)
    parsed = strict_parser(raw)
    if parsed is not None:
        return parsed, raw
    retry_messages = list(messages) + [
        {"role": "assistant", "content": raw or ""},
        {"role": "user", "content": JSON_RETRY_REMINDER},
    ]
    raw2 = _call_openrouter(model_id, retry_messages, max_tokens)
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


def _make_frontline_parser(needs_summary: bool):
    def parser(content: str):
        parsed = _extract_json(content)
        if not parsed or "reply" not in parsed or "action" not in parsed:
            return None
        action = str(parsed["action"]).strip().lower()
        if action not in FRONTLINE_ACTIONS:
            return None
        out = {"reply": str(parsed["reply"]), "action": action}
        if needs_summary:
            if "handoff_summary" not in parsed:
                return None
            out["handoff_summary"] = str(parsed["handoff_summary"])
        return out
    return parser


def _make_supervisor_parser(allow_request: bool):
    def parser(content: str):
        parsed = _extract_json(content)
        if not parsed or "decision" not in parsed:
            return None
        decision = str(parsed["decision"]).strip().lower()
        allowed = SUPERVISOR_DECISIONS + (("request_transcript",) if allow_request else ())
        if decision not in allowed:
            return None
        return {"decision": decision, "note": str(parsed.get("note", ""))}
    return parser


# ------------------------------------------------------------------ main run

def run_one_conversation(model_name: str, condition: str, run_id: int,
                         script_set: str = "base", role_frame: str = "default",
                         variant: str = "armored"):
    """Run one full gradient conversation and return a per-run record."""
    model_id = MODELS[model_name]
    has_supervisor = condition in ("B", "C", "C_mitigated")
    summary_channel = condition in ("C", "C_mitigated")

    fl_parser = _make_frontline_parser(needs_summary=summary_channel)
    fl_max_tokens = MAX_TOKENS_FRONTLINE_SUMMARY if summary_channel else MAX_TOKENS_FRONTLINE
    fl_messages = [{"role": "system", "content": prompts.frontline_system(condition, role_frame, variant)}]

    sup_messages = None
    sup_parser = None
    if has_supervisor:
        sup_messages = [{"role": "system", "content": prompts.supervisor_system(condition, role_frame, variant)}]
        sup_parser = _make_supervisor_parser(allow_request=summary_channel)

    turns = []
    yield_frontline = None
    yield_supervisor = None
    run_failed = False
    fail_reason = ""
    # (speaker, text) pairs for building supervisor transcripts (condition B)
    visible_transcript = []
    last_forwarded = 0  # index into visible_transcript already sent to supervisor

    for level in scripts.ALL_LEVELS:
        customer_msg = scripts.customer_turn(script_set, level)
        fl_messages.append({"role": "user", "content": customer_msg})
        visible_transcript.append(("customer", customer_msg))

        parsed, raw = _query_with_json_retry(model_id, fl_messages, fl_parser, fl_max_tokens)
        if parsed is None:
            run_failed = True
            fail_reason = f"frontline parse failure at level {level}"
            turns.append({
                "level": level,
                "level_name": scripts.LEVEL_NAMES[level],
                "customer": customer_msg,
                "frontline_raw": raw,
                "frontline_parse_ok": False,
            })
            break

        fl_messages.append({"role": "assistant", "content": raw})
        visible_transcript.append(("agent", parsed["reply"]))

        turn = {
            "level": level,
            "level_name": scripts.LEVEL_NAMES[level],
            "customer": customer_msg,
            "frontline_reply": parsed["reply"],
            "frontline_action": parsed["action"],
            "frontline_parse_ok": True,
        }
        if summary_channel:
            turn["handoff_summary"] = parsed["handoff_summary"]

        if parsed["action"] == "grant_refund" and yield_frontline is None:
            yield_frontline = level

        # Front-line breach = a refund commitment has reached the customer.
        # The supervisor never gets to weigh in on a promise already made.
        if yield_frontline is not None:
            turns.append(turn)
            break

        if has_supervisor:
            if summary_channel:
                sup_user = prompts.ESCALATION_SUMMARY.format(
                    stage=level, summary=parsed["handoff_summary"])
            else:
                delta = prompts.format_transcript(visible_transcript[last_forwarded:])
                template = (prompts.ESCALATION_TRANSCRIPT_FIRST if last_forwarded == 0
                            else prompts.ESCALATION_TRANSCRIPT_DELTA)
                sup_user = template.format(stage=level, transcript=delta)
                last_forwarded = len(visible_transcript)

            sup_messages.append({"role": "user", "content": sup_user})
            sup_parsed, sup_raw = _query_with_json_retry(
                model_id, sup_messages, sup_parser, MAX_TOKENS_SUPERVISOR)
            if sup_parsed is None:
                run_failed = True
                fail_reason = f"supervisor parse failure at stage {level}"
                turn["supervisor_raw"] = sup_raw
                turn["supervisor_parse_ok"] = False
                turns.append(turn)
                break
            sup_messages.append({"role": "assistant", "content": sup_raw})

            requested_transcript = sup_parsed["decision"] == "request_transcript"
            turn["supervisor_requested_transcript"] = requested_transcript

            if requested_transcript:
                supplied = prompts.TRANSCRIPT_SUPPLIED.format(
                    transcript=prompts.format_transcript(visible_transcript))
                sup_messages.append({"role": "user", "content": supplied})
                final_parser = _make_supervisor_parser(allow_request=False)
                sup_parsed, sup_raw = _query_with_json_retry(
                    model_id, sup_messages, final_parser, MAX_TOKENS_SUPERVISOR)
                if sup_parsed is None:
                    run_failed = True
                    fail_reason = f"supervisor parse failure after transcript at stage {level}"
                    turn["supervisor_raw"] = sup_raw
                    turn["supervisor_parse_ok"] = False
                    turns.append(turn)
                    break
                sup_messages.append({"role": "assistant", "content": sup_raw})

            turn["supervisor_decision"] = sup_parsed["decision"]
            turn["supervisor_note"] = sup_parsed["note"]
            turn["supervisor_parse_ok"] = True

            if sup_parsed["decision"] == "grant_refund" and yield_supervisor is None:
                yield_supervisor = level

        turns.append(turn)

        # Stop once the customer has obtained the refund from the system.
        if yield_supervisor is not None:
            break

    candidates = [y for y in (yield_frontline, yield_supervisor) if y is not None]
    system_yield = min(candidates) if candidates else None

    return {
        "run_id": run_id,
        "model": model_name,
        "condition": condition,
        "script_set": script_set,
        "role_frame": role_frame,
        "variant": variant,
        "turns": turns,
        "yield_point_frontline": yield_frontline,
        "yield_point_supervisor": yield_supervisor,
        "system_yield_point": system_yield,
        "run_failed": run_failed,
        "fail_reason": fail_reason,
    }


# ------------------------------------------------------------------- probe

def run_one_probe(model_name: str, level: int, run_id: int,
                  script_set: str = "base", role_frame: str = "default",
                  variant: str = "armored"):
    """Single-level probe for per-level pressure potency (H4).

    Opening request → agent → ONE pressure level in isolation → agent.
    Solo condition-A setup; removes the ordering confound of the gradient.
    """
    model_id = MODELS[model_name]
    parser = _make_frontline_parser(needs_summary=False)
    messages = [{"role": "system", "content": prompts.frontline_system("A", role_frame, variant)}]

    record = {
        "run_id": run_id,
        "model": model_name,
        "probe_level": level,
        "level_name": scripts.LEVEL_NAMES[level],
        "script_set": script_set,
        "role_frame": role_frame,
        "variant": variant,
        "turns": [],
        "breach": None,          # None = parse failure; else bool
        "breach_on_opening": None,
        "run_failed": False,
    }

    for lvl in (0, level):
        customer_msg = scripts.customer_turn(script_set, lvl)
        messages.append({"role": "user", "content": customer_msg})
        parsed, raw = _query_with_json_retry(model_id, messages, parser, MAX_TOKENS_FRONTLINE)
        if parsed is None:
            record["run_failed"] = True
            record["turns"].append({"level": lvl, "customer": customer_msg,
                                    "frontline_raw": raw, "frontline_parse_ok": False})
            return record
        messages.append({"role": "assistant", "content": raw})
        record["turns"].append({
            "level": lvl,
            "customer": customer_msg,
            "frontline_reply": parsed["reply"],
            "frontline_action": parsed["action"],
            "frontline_parse_ok": True,
        })
        if lvl == 0:
            record["breach_on_opening"] = parsed["action"] == "grant_refund"
            if record["breach_on_opening"]:
                record["breach"] = True
                return record   # caved before the probe level was even shown
        else:
            record["breach"] = parsed["action"] == "grant_refund"
    return record


# --------------------------------------------------------------- C-scripted

def run_one_cscripted(model_name: str, summary_variant: str, run_id: int,
                      role_frame: str = "default", variant: str = "armored"):
    """Single supervisor decision on a fixed summary (neutral vs advocating).

    Facts identical across variants; isolates the causal effect of advocacy
    framing in the handoff channel.
    """
    model_id = MODELS[model_name]
    parser = _make_supervisor_parser(allow_request=False)
    messages = [
        {"role": "system", "content": prompts.supervisor_system("C_scripted", role_frame, variant)},
        {"role": "user", "content": prompts.CSCRIPTED_USER.format(
            summary=prompts.CSCRIPTED_SUMMARIES[summary_variant])},
    ]
    parsed, raw = _query_with_json_retry(model_id, messages, parser, MAX_TOKENS_SUPERVISOR)
    if parsed is None:
        return {
            "run_id": run_id, "model": model_name, "summary_variant": summary_variant,
            "variant": variant, "role_frame": role_frame, "decision": None,
            "note": "", "raw": raw, "parse_ok": False,
        }
    return {
        "run_id": run_id, "model": model_name, "summary_variant": summary_variant,
        "variant": variant, "role_frame": role_frame, "decision": parsed["decision"],
        "note": parsed["note"], "raw": raw, "parse_ok": True,
    }
