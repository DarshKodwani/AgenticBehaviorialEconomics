import json, os, glob

results_dir = os.path.join(os.path.dirname(__file__), "results")
files = glob.glob(os.path.join(results_dir, "*.json"))
files = [f for f in files if "summary" not in f]

total_games = len(files)
rounds = 80
total_calls = total_games * rounds * 2

model_calls = {}
for f in files:
    game = json.load(open(f))
    ma, mb = game["model_a"], game["model_b"]
    model_calls[ma] = model_calls.get(ma, 0) + rounds
    model_calls[mb] = model_calls.get(mb, 0) + rounds

# Estimate: system ~200 tok, user prompt grows with history
# Round N: ~30 + N*25 tokens for price history
# Average across 80 rounds: ~30 + 40*25 = 1030
# Total input per call: ~200 + 1030 = 1230
# Output: ~50 tokens
avg_in = 1230
avg_out = 50

# OpenRouter per-1M-token pricing (approximate, May 2025)
prices = {
    "GPT-4o": (2.50, 10.00),
    "Claude 3.5 Haiku": (0.80, 4.00),
    "Gemini 2.0 Flash": (0.10, 0.40),
    "Llama 3.1 70B": (0.40, 0.40),
    "DeepSeek V3": (0.30, 0.88),
    "Qwen 2.5 72B": (0.30, 0.30),
}

print(f"Games: {total_games}")
print(f"Total API calls: {total_calls:,}")
print(f"Est. total input tokens: {total_calls * avg_in:,}")
print(f"Est. total output tokens: {total_calls * avg_out:,}")
print(f"Est. total tokens: {total_calls * (avg_in + avg_out):,}")
print()

total_cost = 0
for m in sorted(model_calls):
    c = model_calls[m]
    inp = c * avg_in
    out = c * avg_out
    pin, pout = prices.get(m, (0, 0))
    cost = (inp / 1e6) * pin + (out / 1e6) * pout
    total_cost += cost
    print(f"  {m:25s} {c:5d} calls  ~{inp:>10,} in  ~{out:>7,} out  ${cost:.3f}")

print(f"\nEstimated total cost: ${total_cost:.2f}")
