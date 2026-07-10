"""C-scripted causal arm: supervisor decides on a fixed summary we wrote.

Two variants with identical facts — "neutral" and "advocating" (the latter
appends two sentences of advocacy framing). The difference in supervisor
breach rate between variants is the causal effect of advocacy in the
handoff channel (H3). Single supervisor call per run, so runs are cheap;
default N is higher than the conversation cells.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
import prompts


N_RUNS = 30
WORKERS_PER_CELL = 8
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "c_scripted")

# Provider-diverse 3-model subset for the causal arm.
DEFAULT_SUBSET = ["GPT-4o", "Claude Haiku 4.5", "DeepSeek V3"]

VARIANTS = ("neutral", "advocating")


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def cell_path(model: str, variant: str) -> str:
    return os.path.join(RESULTS_DIR, f"cscripted_{variant}_{_safe(model)}.json")


def load_existing(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def run_cell(model: str, variant: str, n_runs: int = N_RUNS):
    path = cell_path(model, variant)
    existing = load_existing(path)
    if existing and len(existing.get("runs", [])) >= n_runs:
        print(f"  [skip] {os.path.basename(path)}")
        return existing

    runs = existing["runs"] if existing else []
    completed_ids = {r["run_id"] for r in runs}
    todo_ids = [i for i in range(1, n_runs + 1) if i not in completed_ids]
    if not todo_ids:
        return existing

    print(f"  [run]  {model} [{variant}] : {len(todo_ids)} runs", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS_PER_CELL) as ex:
        future_to_id = {
            ex.submit(ge.run_one_cscripted, model, variant, run_id): run_id
            for run_id in todo_ids
        }
        for fut in as_completed(future_to_id):
            run_id = future_to_id[fut]
            done += 1
            try:
                rec = fut.result()
                runs.append(rec)
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id:>2}  decision={rec['decision']}", flush=True)
            except Exception as e:
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id} failed: {e}", flush=True)

    runs.sort(key=lambda r: r["run_id"])
    record = {
        "model": model,
        "variant": variant,
        "n_runs": n_runs,
        "completed_runs": len(runs),
        "runs": runs,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-runs", type=int, default=N_RUNS)
    parser.add_argument("--model", action="append", default=None,
                        help=f"default subset: {DEFAULT_SUBSET}")
    args = parser.parse_args()

    models = args.model or DEFAULT_SUBSET
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"C-scripted: {len(models)} models × {len(VARIANTS)} variants, {args.n_runs} runs/cell", flush=True)
    for variant in VARIANTS:
        for model in models:
            run_cell(model, variant, n_runs=args.n_runs)

    # Quick summary of breach rates per cell.
    print("\nBreach rates (grant_refund):")
    for variant in VARIANTS:
        for model in models:
            rec = load_existing(cell_path(model, variant))
            if not rec:
                continue
            ok = [r for r in rec["runs"] if r["parse_ok"]]
            breaches = sum(1 for r in ok if r["decision"] == "grant_refund")
            if ok:
                print(f"  {model:<18} {variant:<11} {breaches}/{len(ok)} = {breaches/len(ok):.0%}")


if __name__ == "__main__":
    main()
