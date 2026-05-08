"""Run the full direct-play matrix: every model × every model × 3 conditions.

Each cell = N_RUNS independent one-shot ultimatum games. Within a cell runs
are parallelised; cells are processed sequentially. Resumable: cells whose
JSON file already exists with N_RUNS completed runs are skipped.
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
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "direct_play")


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def cell_path(proposer: str, responder: str, condition: str) -> str:
    fname = f"{_safe(proposer)}_vs_{_safe(responder)}_{condition}.json"
    return os.path.join(RESULTS_DIR, fname)


def load_existing(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def run_cell(proposer: str, responder: str, condition: str, n_runs: int = N_RUNS):
    path = cell_path(proposer, responder, condition)
    existing = load_existing(path)
    if existing and len(existing.get("runs", [])) >= n_runs:
        print(f"  [skip] {os.path.basename(path)} already has {n_runs} runs")
        return existing

    runs = existing["runs"] if existing else []
    completed_ids = {r["run_id"] for r in runs}
    todo_ids = [i for i in range(1, n_runs + 1) if i not in completed_ids]

    if not todo_ids:
        return existing

    t0 = time.time()
    print(f"  [run]  {proposer} → {responder} [{condition}] : {len(todo_ids)} runs", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS_PER_CELL) as ex:
        future_to_id = {
            ex.submit(ge.run_one_round, proposer, responder, condition, run_id, True): run_id
            for run_id in todo_ids
        }
        for fut in as_completed(future_to_id):
            run_id = future_to_id[fut]
            done += 1
            try:
                rec = fut.result()
                runs.append(rec)
                offer = rec.get("offer", "?")
                decision = rec.get("decision", "?")
                mc_p = rec.get("mc_proposer_belief", "-")
                mc_r = rec.get("mc_responder_belief", "-")
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id:>2}  offer={offer:>5}  → {decision:<6}  mc(p/r)={mc_p}/{mc_r}", flush=True)
            except Exception as e:
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id} failed: {e}", flush=True)

    runs.sort(key=lambda r: r["run_id"])
    record = {
        "proposer": proposer,
        "responder": responder,
        "condition": condition,
        "n_runs": n_runs,
        "completed_runs": len(runs),
        "runs": runs,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"         done in {time.time() - t0:.0f}s → {os.path.basename(path)}", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-runs", type=int, default=N_RUNS)
    parser.add_argument("--proposer", action="append", default=None,
                        help="restrict to specific proposer model(s); repeatable")
    parser.add_argument("--responder", action="append", default=None,
                        help="restrict to specific responder model(s); repeatable")
    parser.add_argument("--condition", action="append", default=None,
                        choices=list(CONDITIONS), help="restrict to specific condition(s)")
    args = parser.parse_args()

    proposers = args.proposer or list(ge.MODELS.keys())
    responders = args.responder or list(ge.MODELS.keys())
    conditions = args.condition or list(CONDITIONS)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_cells = len(proposers) * len(responders) * len(conditions)
    print(f"Direct-play matrix: {len(proposers)} × {len(responders)} × {len(conditions)} = {total_cells} cells, {args.n_runs} runs/cell", flush=True)

    t_start = time.time()
    idx = 0
    for condition in conditions:
        for proposer in proposers:
            for responder in responders:
                idx += 1
                elapsed = time.time() - t_start
                print(f"[cell {idx}/{total_cells}]  elapsed {elapsed/60:.1f}m", flush=True)
                run_cell(proposer, responder, condition, n_runs=args.n_runs)


if __name__ == "__main__":
    main()
