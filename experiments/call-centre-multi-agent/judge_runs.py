"""Judging pass: annotate saved runs with judge classifications.

Separate from the run pass so it can be rerun (e.g. with a different judge
model) without repeating the expensive conversations. Idempotent: runs that
already carry a successful judgement are skipped unless --rejudge is set.
Writes the judgement and the keyword backstop into each run record in place.
"""
import argparse
import glob
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import judge


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "runs")
WORKERS = 4


def needs_judging(run: dict, rejudge: bool) -> bool:
    if run.get("run_failed"):
        return False
    if rejudge:
        return True
    j = run.get("judge")
    return j is None or j.get("judge_failed")


def judge_file(path: str, rejudge: bool):
    with open(path) as f:
        record = json.load(f)

    todo = [r for r in record.get("runs", []) if needs_judging(r, rejudge)]
    if not todo:
        print(f"  [skip] {os.path.basename(path)}")
        return

    print(f"  [judge] {os.path.basename(path)} : {len(todo)} runs", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        future_to_run = {ex.submit(judge.judge_run, r): r for r in todo}
        for fut in as_completed(future_to_run):
            run = future_to_run[fut]
            try:
                run["judge"] = fut.result()
            except Exception as e:
                run["judge"] = {"judge_failed": True, "raw": f"exception: {e}",
                                "judge_model": judge.JUDGE_MODEL}
            run["keyword_backstop_level"] = judge.keyword_backstop(run)
            failed = run["judge"].get("judge_failed", False)
            print(f"    run {run['run_id']:>2}  "
                  f"{'JUDGE FAILED' if failed else 'ok'}  "
                  f"backstop={run['keyword_backstop_level']}", flush=True)

    with open(path, "w") as f:
        json.dump(record, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="*.json",
                        help="glob over results/runs/, e.g. 'C_*_base_default.json'")
    parser.add_argument("--rejudge", action="store_true",
                        help="rejudge runs that already have a judgement")
    args = parser.parse_args()

    paths = sorted(glob.glob(os.path.join(RESULTS_DIR, args.pattern)))
    if not paths:
        print(f"no result files match {args.pattern}")
        return
    print(f"Judging {len(paths)} files with {judge.JUDGE_MODEL}")
    for path in paths:
        judge_file(path, args.rejudge)


if __name__ == "__main__":
    main()
