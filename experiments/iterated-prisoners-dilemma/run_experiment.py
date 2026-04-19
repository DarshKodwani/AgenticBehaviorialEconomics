"""Run the IPD tournament across all model pairs."""
import os
import json
import itertools
from game_engine import MODELS, run_game, compute_stats

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def safe_filename(name):
    return name.replace(" ", "_").replace(".", "")


def progress(r, total, aa, ab):
    label_a = "COOP" if aa == "C" else "DEF "
    label_b = "COOP" if ab == "C" else "DEF "
    if r == 1 or r % 10 == 0 or r == total:
        print(f"  Round {r}/{total}: A={label_a}, B={label_b}")


def main():
    model_names = list(MODELS.keys())

    # all cross-model pairs
    pairs = list(itertools.combinations(model_names, 2))
    # add two same-model pairs for self-play
    pairs.append(("GPT-4o", "GPT-4o"))
    pairs.append(("DeepSeek V3", "DeepSeek V3"))

    total = len(pairs)
    print(f"Running {total} games\n")

    results_summary = []

    for idx, (ma, mb) in enumerate(pairs, 1):
        fname = f"{safe_filename(ma)}_vs_{safe_filename(mb)}.json"
        fpath = os.path.join(RESULTS_DIR, fname)

        # skip if already done
        if os.path.exists(fpath):
            print(f"[{idx}/{total}] Skipping {ma} vs {mb} (already done)")
            with open(fpath) as f:
                game = json.load(f)
            results_summary.append({
                "model_a": ma,
                "model_b": mb,
                "stats": game["stats"],
            })
            continue

        print(f"[{idx}/{total}] Running: {ma} vs {mb}")
        game = run_game(ma, mb, progress_callback=progress)
        stats = compute_stats(game)
        game["stats"] = stats

        with open(fpath, "w") as f:
            json.dump(game, f, indent=2)

        mc = stats["mutual_coop_rate"]
        print(f"  Done. Mutual cooperation: {mc:.1%}\n")

        results_summary.append({
            "model_a": ma,
            "model_b": mb,
            "stats": stats,
        })

    # save summary
    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()
