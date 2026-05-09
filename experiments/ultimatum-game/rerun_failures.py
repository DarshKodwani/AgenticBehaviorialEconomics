"""Re-execute parse-failed runs in place under the hardened engine.

Scans every direct_play and strategy_method JSON file. Identifies runs
where parsing failed (proposer or responder), re-executes the full round
under the new engine (response_format=json_object + one-shot retry +
strict parsing + None-on-total-failure), and replaces the run record
in the file by run_id.

Idempotent: a clean cell is left untouched; a partially-failed cell is
patched only on the broken runs.
"""
import argparse
import json
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge


HERE = os.path.dirname(__file__)
DIRECT_DIR = os.path.join(HERE, "results", "direct_play")
SM_DIR = os.path.join(HERE, "results", "strategy_method")
WORKERS = 5


def _direct_run_failed(r):
    return (
        r.get("responder_parse_ok") is False
        or r.get("proposer_parse_ok") is False
        or r.get("responder_reasoning") == "fallback"
        or r.get("proposer_reasoning") == "fallback"
        or r.get("decision") is None
        or r.get("offer") is None
    )


def _sm_run_failed(t):
    return (
        t.get("parse_ok") is False
        or t.get("min_acceptable_offer") is None
        or t.get("reasoning") == "fallback"
    )


def rerun_direct_play(dry_run=False):
    files = sorted(glob.glob(os.path.join(DIRECT_DIR, "*.json")))
    total_fixed = 0
    for f in files:
        d = json.load(open(f))
        bad = [r for r in d["runs"] if _direct_run_failed(r)]
        if not bad:
            continue
        bad_ids = sorted([r["run_id"] for r in bad])
        print(f"[direct] {os.path.basename(f)}: {len(bad_ids)} broken runs → {bad_ids}")
        if dry_run:
            continue

        new_records = {}
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {
                ex.submit(ge.run_one_round, d["proposer"], d["responder"],
                          d["condition"], rid, True): rid
                for rid in bad_ids
            }
            for fut in as_completed(futures):
                rid = futures[fut]
                rec = fut.result()
                new_records[rid] = rec
                ok = rec.get("proposer_parse_ok") and rec.get("responder_parse_ok")
                print(f"    rerun {rid:>2}: offer={rec.get('offer')} dec={rec.get('decision')}  parse_ok={ok}")

        for i, r in enumerate(d["runs"]):
            if r["run_id"] in new_records:
                d["runs"][i] = new_records[r["run_id"]]

        with open(f, "w") as out:
            json.dump(d, out, indent=2)
        total_fixed += len(new_records)
    print(f"[direct] total reruns: {total_fixed}")
    return total_fixed


def rerun_strategy_method(dry_run=False):
    files = sorted(glob.glob(os.path.join(SM_DIR, "*.json")))
    total_fixed = 0
    for f in files:
        d = json.load(open(f))
        bad = [t for t in d["thresholds"] if _sm_run_failed(t)]
        if not bad:
            continue
        bad_ids = sorted([t["run_id"] for t in bad])
        print(f"[sm] {os.path.basename(f)}: {len(bad_ids)} broken runs → {bad_ids}")
        if dry_run:
            continue

        new_records = {}
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {
                ex.submit(ge.run_one_strategy_method, d["responder"],
                          d["condition"], rid, True): rid
                for rid in bad_ids
            }
            for fut in as_completed(futures):
                rid = futures[fut]
                rec = fut.result()
                new_records[rid] = rec
                print(f"    rerun {rid:>2}: min={rec.get('min_acceptable_offer')}  parse_ok={rec.get('parse_ok')}")

        for i, t in enumerate(d["thresholds"]):
            if t["run_id"] in new_records:
                d["thresholds"][i] = new_records[t["run_id"]]

        with open(f, "w") as out:
            json.dump(d, out, indent=2)
        total_fixed += len(new_records)
    print(f"[sm] total reruns: {total_fixed}")
    return total_fixed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="list broken runs but don't re-execute")
    parser.add_argument("--direct-only", action="store_true")
    parser.add_argument("--strategy-only", action="store_true")
    args = parser.parse_args()

    do_direct = not args.strategy_only
    do_sm = not args.direct_only

    fixed = 0
    if do_direct:
        fixed += rerun_direct_play(dry_run=args.dry_run)
    if do_sm:
        fixed += rerun_strategy_method(dry_run=args.dry_run)
    print(f"\nTotal{'(dry)' if args.dry_run else ''}: {fixed} runs identified")


if __name__ == "__main__":
    main()
