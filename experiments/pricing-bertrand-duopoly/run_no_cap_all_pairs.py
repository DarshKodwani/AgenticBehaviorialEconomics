"""Run the no-cap Bertrand duopoly across all model pairs and save results.

This keeps the original capped experiment results untouched by writing into
experiment/results_no_cap/.
"""

import itertools
import json
import os
import time

from run_no_cap_pair import MODELS, NUM_ROUNDS, run_game, compute_stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_no_cap")


def safe_filename(name):
    return name.replace(" ", "_").replace(".", "")


def main(num_rounds=NUM_ROUNDS):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    model_names = list(MODELS.keys())
    cross_pairs = list(itertools.combinations(model_names, 2))
    same_pairs = [(name, name) for name in model_names]
    all_pairs = cross_pairs + same_pairs

    all_results = []

    print(f"Running {len(all_pairs)} no-cap games for {num_rounds} rounds each\n")

    for idx, (ma, mb) in enumerate(all_pairs, start=1):
        filename = f"{safe_filename(ma)}_vs_{safe_filename(mb)}_no_cap.json"
        filepath = os.path.join(RESULTS_DIR, filename)

        if os.path.exists(filepath):
            print(f"[{idx}/{len(all_pairs)}] Skipping {ma} vs {mb} (already exists)")
            with open(filepath, "r") as f:
                game = json.load(f)
            all_results.append({
                "model_a": game["model_a"],
                "model_b": game["model_b"],
                "stats": game.get("stats", {}),
            })
            continue

        print(f"[{idx}/{len(all_pairs)}] Running: {ma} vs {mb}")
        game = run_game(ma, mb, num_rounds=num_rounds)
        stats = compute_stats(game)
        game["stats"] = stats

        with open(filepath, "w") as f:
            json.dump(game, f, indent=2)

        print(
            f"  Done. avg(last20)=${stats['avg_price_last20']:.3f}, "
            f"max=${stats['max_price_seen']:.3f}, "
            f"uncapped joint optimum=${stats['joint_profit_price_uncapped']:.3f}\n"
        )

        all_results.append({
            "model_a": ma,
            "model_b": mb,
            "stats": stats,
        })

        time.sleep(1)

    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"All done. Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
