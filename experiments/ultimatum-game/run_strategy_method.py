"""Strategy-method elicitation: each responder model states its minimum
acceptable offer, before any offer is shown, under each priming condition.

This is the cleanest preference elicitation — no offer-specific noise, no
post-hoc rationalisation. Pairs naturally with the direct-play data: the
delta between stated threshold here and revealed threshold from rejections
in the play data is itself a finding.
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
from prompts import CONDITIONS


N_RUNS = 30
WORKERS_PER_CELL = 5
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "strategy_method")


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def cell_path(responder: str, condition: str) -> str:
    fname = f"{_safe(responder)}_{condition}.json"
    return os.path.join(RESULTS_DIR, fname)


def load_existing(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def run_cell(responder: str, condition: str, n_runs: int = N_RUNS):
    path = cell_path(responder, condition)
    existing = load_existing(path)
    if existing and len(existing.get("thresholds", [])) >= n_runs:
        print(f"  [skip] {os.path.basename(path)} already has {n_runs} runs")
        return existing

    runs = existing["thresholds"] if existing else []
    completed_ids = {r["run_id"] for r in runs}
    todo_ids = [i for i in range(1, n_runs + 1) if i not in completed_ids]

    if not todo_ids:
        return existing

    t0 = time.time()
    print(f"  [run]  {responder} [{condition}] : {len(todo_ids)} runs", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS_PER_CELL) as ex:
        future_to_id = {
            ex.submit(ge.run_one_strategy_method, responder, condition, run_id, True): run_id
            for run_id in todo_ids
        }
        for fut in as_completed(future_to_id):
            run_id = future_to_id[fut]
            done += 1
            try:
                rec = fut.result()
                runs.append(rec)
                t = rec.get("min_acceptable_offer", "?")
                mc = rec.get("mc_belief", "-")
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id:>2}  min_accept={t:>5}  mc={mc}", flush=True)
            except Exception as e:
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id} failed: {e}", flush=True)

    runs.sort(key=lambda r: r["run_id"])
    record = {
        "responder": responder,
        "condition": condition,
        "n_runs": n_runs,
        "completed_runs": len(runs),
        "thresholds": runs,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"         done in {time.time() - t0:.0f}s → {os.path.basename(path)}", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-runs", type=int, default=N_RUNS)
    parser.add_argument("--responder", action="append", default=None,
                        help="restrict to specific responder model(s); repeatable")
    parser.add_argument("--condition", action="append", default=None,
                        choices=list(CONDITIONS), help="restrict to specific condition(s)")
    args = parser.parse_args()

    responders = args.responder or list(ge.MODELS.keys())
    conditions = args.condition or list(CONDITIONS)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_cells = len(responders) * len(conditions)
    print(f"Strategy-method elicitation: {len(responders)} × {len(conditions)} = {total_cells} cells, {args.n_runs} runs/cell", flush=True)

    t_start = time.time()
    idx = 0
    for condition in conditions:
        for responder in responders:
            idx += 1
            elapsed = time.time() - t_start
            print(f"[cell {idx}/{total_cells}]  elapsed {elapsed/60:.1f}m", flush=True)
            run_cell(responder, condition, n_runs=args.n_runs)


if __name__ == "__main__":
    main()
