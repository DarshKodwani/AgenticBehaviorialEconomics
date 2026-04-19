"""Run the v2 prompt-sensitivity experiment."""
import os
import json
from game_engine import run_game, compute_stats, CONDITIONS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# 3 model pairs that showed different v1 behaviours
LLM_PAIRS = [
    ("GPT-4o", "DeepSeek V3"),        # instant lock-in at $2.00
    ("GPT-4o", "Llama 3.1 70B"),      # gradual ratchet to $3.00
    ("Gemini 2.0 Flash", "Qwen 2.5 72B"),  # low-level lock at $2.05
]

# conditions where both sides are LLMs
LLM_CONDITIONS = ["cooperative", "myopic", "competitive", "blind"]

# fixed-price bot games: one model from each pair
NASH_BOT_MODELS = ["GPT-4o", "Llama 3.1 70B", "Gemini 2.0 Flash"]


def safe_filename(name):
    return name.replace(" ", "_").replace(".", "")


def progress(r, total, pa, pb):
    if r == 1 or r % 10 == 0 or r == total:
        print(f"  Round {r}/{total}: A=${pa:.2f}, B=${pb:.2f}")


def main():
    games = []

    # LLM vs LLM under 4 conditions (but skip cooperative — that's v1 data)
    for ma, mb in LLM_PAIRS:
        for cond in LLM_CONDITIONS:
            if cond == "cooperative":
                continue  # already have this from v1
            games.append((ma, mb, cond))

    # fixed-price bot games
    for model in NASH_BOT_MODELS:
        games.append((model, "Fixed Price Bot", "nash_bot"))

    total = len(games)
    print(f"Running {total} games\n")

    results_summary = []

    for idx, (ma, mb, cond) in enumerate(games, 1):
        fname = f"{safe_filename(ma)}_vs_{safe_filename(mb)}_{cond}.json"
        fpath = os.path.join(RESULTS_DIR, fname)

        if os.path.exists(fpath):
            print(f"[{idx}/{total}] Skipping {ma} vs {mb} [{cond}] (already done)")
            with open(fpath) as f:
                game = json.load(f)
            results_summary.append({
                "model_a": ma, "model_b": mb,
                "condition": cond, "stats": game["stats"],
            })
            continue

        print(f"[{idx}/{total}] Running: {ma} vs {mb} [{cond}]")
        game = run_game(ma, mb, cond, progress_callback=progress)
        stats = compute_stats(game)
        game["stats"] = stats
        ci = stats.get("price_level_index", stats["collusion_index"])

        with open(fpath, "w") as f:
            json.dump(game, f, indent=2)

        print(f"  Done. PI={ci:.3f}, avg price (last 20)=${stats['avg_price_last20']:.2f}\n")

        results_summary.append({
            "model_a": ma, "model_b": mb,
            "condition": cond, "stats": stats,
        })

    # save summary
    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()
