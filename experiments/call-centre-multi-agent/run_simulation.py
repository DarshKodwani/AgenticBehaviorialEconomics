"""Run the call-centre field simulation for one or more models.

Every model faces the identical seeded 30-day case schedule (same-world
design); the Q2 strategy doc enters the manager's context from 6 April.
Resumable per (model, day): a day file with all its cases completed is
skipped. Within a day, cases run in parallel; days run in order.

  python3 run_simulation.py --model "GPT-4o"
  python3 run_simulation.py                    # all six models, sequential
  python3 run_simulation.py --days 3           # shakedown: first N days only
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
import sim_engine


WORKERS = 5
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "simulation")

# Endpoints that 429 at higher concurrency.
LOW_CONCURRENCY_MODELS = {"Llama 3.1 70B": 2, "Qwen 2.5 72B": 2}


def _safe(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def day_path(model: str, day: str) -> str:
    return os.path.join(RESULTS_DIR, _safe(model), f"{day}.json")


def run_day(model: str, day_sched: dict):
    path = day_path(model, day_sched["day"])
    if os.path.exists(path):
        try:
            with open(path) as f:
                existing = json.load(f)
            done_ids = {c["case_id"] for c in existing.get("cases", [])
                        if not c.get("failed")}
        except (OSError, json.JSONDecodeError):
            existing, done_ids = None, set()
    else:
        existing, done_ids = None, set()

    todo = [c for c in day_sched["cases"] if c["case_id"] not in done_ids]
    kept = [c for c in (existing or {}).get("cases", [])
            if c["case_id"] in done_ids]
    if not todo:
        print(f"  [skip] {day_sched['day']}")
        return

    workers = LOW_CONCURRENCY_MODELS.get(model, WORKERS)
    t0 = time.time()
    results = list(kept)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(sim_engine.run_case, model, c, day_sched["docs"]): c
                for c in todo}
        for fut in as_completed(futs):
            c = futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:
                results.append({**c, "docs": day_sched["docs"], "model": model,
                                "failed": True, "error": str(e), "turns": []})

    results.sort(key=lambda r: r["case_id"])
    n_breach = sum(1 for r in results if r.get("breach"))
    refunded = sum(r.get("refunded_amount", 0) for r in results)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"model": model, "day": day_sched["day"],
                   "docs": day_sched["docs"], "cases": results}, f, indent=2)
    print(f"  [{day_sched['day']}] {day_sched['docs']:>2} doc  "
          f"{len(results):>2} cases  ${refunded:>7.2f} refunded  "
          f"{n_breach} breach{'es' if n_breach != 1 else ''}  "
          f"({time.time()-t0:.0f}s)", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="append", default=None)
    parser.add_argument("--days", type=int, default=None,
                        help="run only the first N business days (shakedown)")
    args = parser.parse_args()

    models = args.model or list(ge.MODELS.keys())
    schedule = sim_engine.build_schedule()
    if args.days:
        schedule = schedule[:args.days]

    total_cases = sum(len(d["cases"]) for d in schedule)
    for model in models:
        print(f"=== {model}: {len(schedule)} days, {total_cases} cases ===", flush=True)
        for day_sched in schedule:
            run_day(model, day_sched)


if __name__ == "__main__":
    main()
