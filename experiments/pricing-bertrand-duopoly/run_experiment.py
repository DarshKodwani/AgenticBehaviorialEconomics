"""Run the Bertrand duopoly experiment across all model pairs and save results."""
import os
import sys
import json
import itertools
import time

sys.path.insert(0, os.path.dirname(__file__))
from game_engine import MODELS, run_game, compute_stats, NUM_ROUNDS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def run_all_pairs(num_rounds=NUM_ROUNDS):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    model_names = list(MODELS.keys())
    pairs = list(itertools.combinations(model_names, 2))
    # run 2 same-model pairs for comparison (GPT-4o vs GPT-4o, DeepSeek V3 vs DeepSeek V3)
    same_pairs = [(model_names[0], model_names[0]), (model_names[4], model_names[4])]
    all_pairs = pairs + same_pairs

    all_results = []

    for i, (ma, mb) in enumerate(all_pairs):
        pair_label = f"{ma} vs {mb}"
        safe_name = f"{ma}_vs_{mb}".replace(" ", "_").replace(".", "")
        filename = f"{safe_name}.json"
        filepath = os.path.join(RESULTS_DIR, filename)

        # skip if already run
        if os.path.exists(filepath):
            print(f"[{i+1}/{len(all_pairs)}] {pair_label} — already done, skipping")
            with open(filepath, "r") as f:
                result = json.load(f)
            all_results.append(result)
            continue

        print(f"\n[{i+1}/{len(all_pairs)}] Running: {pair_label}")

        def progress(r, total, pa, pb):
            if r % 10 == 0 or r == 1:
                print(f"  Round {r}/{total}: {ma}=${pa:.2f}, {mb}=${pb:.2f}")

        try:
            game = run_game(ma, mb, num_rounds=num_rounds, progress_callback=progress)
            stats = compute_stats(game)
            result = {**game, "stats": stats}

            with open(filepath, "w") as f:
                json.dump(result, f, indent=2)

            print(f"  Done. Price-level index: {stats.get('price_level_index', stats['collusion_index']):.3f}")
            all_results.append(result)

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        # pause between games to avoid rate limits
        time.sleep(2)

    # save summary
    summary = []
    for r in all_results:
        summary.append({
            "model_a": r["model_a"],
            "model_b": r["model_b"],
            "stats": r["stats"],
        })

    with open(os.path.join(RESULTS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAll done. {len(all_results)} games completed.")
    print(f"Results saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    num_rounds = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_ROUNDS
    run_all_pairs(num_rounds=num_rounds)
