"""Run N public goods games per condition. Resumable: finished games are skipped.

    python run_experiment.py                         # 20 games, np order, visible horizon
    python run_experiment.py --games 40 --horizon hidden
    python run_experiment.py --order pn              # punishment phase first
    PGG_MOCK=1 python run_experiment.py --games 5    # pipeline test, no API calls
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import game_engine as ge
from prompts import HORIZONS, ORDERS

HERE = os.path.dirname(os.path.abspath(__file__))


def results_dir(order, horizon):
    sub = f"{order}_{horizon}" + ("_mock" if ge.MOCK else "")
    path = os.path.join(HERE, "results", sub)
    os.makedirs(path, exist_ok=True)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--order", choices=ORDERS, default="np")
    ap.add_argument("--horizon", choices=HORIZONS, default="visible")
    ap.add_argument("--workers", type=int, default=4, help="games run in parallel")
    args = ap.parse_args()

    if not ge.MOCK and not ge.OPENROUTER_API_KEY:
        raise SystemExit("openrouter_api not found in .env (repo root). Set it, or use PGG_MOCK=1.")

    out = results_dir(args.order, args.horizon)
    todo = [i for i in range(1, args.games + 1)
            if not os.path.exists(os.path.join(out, f"game_{i:03d}.json"))]
    print(f"{len(todo)} games to run -> {out}  (≈{len(todo) * 180} calls)")

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(ge.run_one_game, i, args.order, args.horizon): i for i in todo}
        for n, fut in enumerate(as_completed(futs), 1):
            i = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"  game {i} failed: {e}")
                continue
            with open(os.path.join(out, f"game_{i:03d}.json"), "w") as f:
                json.dump(rec, f, indent=1)
            avg = [sum(r["contributions"].values()) / 6 for r in rec["rounds"]]
            print(f"  [{n}/{len(todo)}] game {i}: mean contribution r1={avg[0]:.1f} "
                  f"r10={avg[9]:.1f} r11={avg[10]:.1f} r20={avg[19]:.1f} "
                  f"failures={rec['parse_failures']}", flush=True)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
