"""Run the main matrix: every model × conditions A/B/C (+ C_mitigated).

Each cell = N_RUNS independent conversations against the scripted customer
gradient. Within a cell runs are parallelised; cells are processed
sequentially. Resumable: cells whose JSON file already has N_RUNS completed
runs are skipped.

Stability battery: pass --script-set / --role-frame to rerun cells under
paraphrased customer scripts or retitled roles; results land in the same
directory with self-describing filenames.
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
import prompts
import scripts


N_RUNS = 10
WORKERS_PER_CELL = 5
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "runs")


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def cell_path(model: str, condition: str, script_set: str, role_frame: str,
              variant: str, docs: str = "none") -> str:
    tag = "" if docs == "none" else f"_docs-{docs}"
    fname = f"{condition}_{_safe(model)}_{script_set}_{role_frame}_{variant}{tag}.json"
    return os.path.join(RESULTS_DIR, fname)


def load_existing(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _fmt_yield(y):
    return "never" if y is None else str(y)


def run_cell(model: str, condition: str, script_set: str, role_frame: str,
             variant: str = "armored", docs: str = "none", n_runs: int = N_RUNS):
    path = cell_path(model, condition, script_set, role_frame, variant, docs)
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
    print(f"  [run]  {model} [{condition}] {script_set}/{role_frame}/{variant}/{docs} : {len(todo_ids)} runs", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS_PER_CELL) as ex:
        future_to_id = {
            ex.submit(ge.run_one_conversation, model, condition, run_id, script_set, role_frame, variant, docs): run_id
            for run_id in todo_ids
        }
        for fut in as_completed(future_to_id):
            run_id = future_to_id[fut]
            done += 1
            try:
                rec = fut.result()
                runs.append(rec)
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id:>2}  "
                      f"fl={_fmt_yield(rec['yield_point_frontline']):>5}  "
                      f"sup={_fmt_yield(rec['yield_point_supervisor']):>5}  "
                      f"sys={_fmt_yield(rec['system_yield_point']):>5}"
                      f"{'  FAILED: ' + rec['fail_reason'] if rec['run_failed'] else ''}",
                      flush=True)
            except Exception as e:
                print(f"    [{done:>2}/{len(todo_ids)}] run {run_id} failed: {e}", flush=True)

    runs.sort(key=lambda r: r["run_id"])
    record = {
        "model": model,
        "condition": condition,
        "script_set": script_set,
        "role_frame": role_frame,
        "variant": variant,
        "docs": docs,
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
    parser.add_argument("--model", action="append", default=None,
                        help="restrict to specific model(s); repeatable")
    parser.add_argument("--condition", action="append", default=None,
                        choices=list(prompts.CONDITIONS),
                        help="restrict to specific condition(s); repeatable")
    parser.add_argument("--script-set", default="base", choices=list(scripts.SCRIPT_SETS))
    parser.add_argument("--role-frame", default="default", choices=list(prompts.ROLE_FRAMES))
    parser.add_argument("--variant", default="armored", choices=list(prompts.VARIANTS))
    parser.add_argument("--docs", default="none", choices=list(prompts.DOCS))
    args = parser.parse_args()

    models = args.model or list(ge.MODELS.keys())
    # C_mitigated is the mitigation arm, run explicitly — not part of the default sweep.
    conditions = args.condition or ["A", "B", "C"]

    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_cells = len(models) * len(conditions)
    print(f"Matrix: {len(models)} models × {len(conditions)} conditions = "
          f"{total_cells} cells, {args.n_runs} runs/cell "
          f"[{args.script_set}/{args.role_frame}/{args.variant}/{args.docs}]", flush=True)

    t_start = time.time()
    idx = 0
    for condition in conditions:
        for model in models:
            idx += 1
            print(f"[cell {idx}/{total_cells}]  elapsed {(time.time() - t_start)/60:.1f}m", flush=True)
            run_cell(model, condition, args.script_set, args.role_frame,
                     variant=args.variant, docs=args.docs, n_runs=args.n_runs)


if __name__ == "__main__":
    main()
