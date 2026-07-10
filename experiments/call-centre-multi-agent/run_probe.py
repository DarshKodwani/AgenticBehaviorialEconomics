"""Single-level probe arm: per-level pressure potency without the ordering
confound (H4).

In the main gradient a model that yields at level 2 never sees level 3, so
per-level potency is confounded with position. Here each pressure level is
presented cold — opening request, agent response, one pressure turn — giving
a clean per-level breach rate. Solo (condition A) setup, all models.
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
import scripts


N_RUNS = 10
WORKERS_PER_CELL = 5
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "probe")


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def cell_path(model: str, level: int, script_set: str) -> str:
    return os.path.join(RESULTS_DIR, f"probe_L{level}_{_safe(model)}_{script_set}.json")


def load_existing(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def run_cell(model: str, level: int, script_set: str, n_runs: int = N_RUNS):
    path = cell_path(model, level, script_set)
    existing = load_existing(path)
    if existing and len(existing.get("runs", [])) >= n_runs:
        print(f"  [skip] {os.path.basename(path)}")
        return existing

    runs = existing["runs"] if existing else []
    completed_ids = {r["run_id"] for r in runs}
    todo_ids = [i for i in range(1, n_runs + 1) if i not in completed_ids]
    if not todo_ids:
        return existing

    print(f"  [run]  {model} probe L{level} ({scripts.LEVEL_NAMES[level]}) : {len(todo_ids)} runs", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS_PER_CELL) as ex:
        future_to_id = {
            ex.submit(ge.run_one_probe, model, level, run_id, script_set): run_id
            for run_id in todo_ids
        }
        for fut in as_completed(future_to_id):
            run_id = future_to_id[fut]
            done += 1
            try:
                rec = fut.result()
                runs.append(rec)
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id:>2}  breach={rec['breach']}"
                      f"{'  (on opening)' if rec.get('breach_on_opening') else ''}", flush=True)
            except Exception as e:
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id} failed: {e}", flush=True)

    runs.sort(key=lambda r: r["run_id"])
    record = {
        "model": model,
        "probe_level": level,
        "level_name": scripts.LEVEL_NAMES[level],
        "script_set": script_set,
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
    parser.add_argument("--model", action="append", default=None)
    parser.add_argument("--level", action="append", type=int, default=None,
                        choices=list(scripts.PRESSURE_LEVELS))
    parser.add_argument("--script-set", default="base", choices=list(scripts.SCRIPT_SETS))
    args = parser.parse_args()

    models = args.model or list(ge.MODELS.keys())
    levels = args.level or list(scripts.PRESSURE_LEVELS)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    total = len(models) * len(levels)
    print(f"Probe matrix: {len(models)} models × {len(levels)} levels = {total} cells, "
          f"{args.n_runs} runs/cell [{args.script_set}]", flush=True)

    idx = 0
    t0 = time.time()
    for level in levels:
        for model in models:
            idx += 1
            print(f"[cell {idx}/{total}]  elapsed {(time.time() - t0)/60:.1f}m", flush=True)
            run_cell(model, level, args.script_set, n_runs=args.n_runs)


if __name__ == "__main__":
    main()
