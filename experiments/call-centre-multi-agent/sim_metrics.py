"""Build the daily time-series table from simulation results.

One row per (model, day): compliant vs out-of-policy refund spend, breach
counts, policies-superseded count, credits, over-refusals. Feeds the
timeline charts and the replay app.
"""
import argparse
import glob
import json
import os

import pandas as pd


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "simulation")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def load_daily():
    rows = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*", "*.json"))):
        with open(path) as f:
            d = json.load(f)
        cases = [c for c in d["cases"] if not c.get("failed")]
        breaches = [c for c in cases if c.get("breach")]
        legit_grants = [c for c in cases if c.get("granted") and not c.get("breach")]
        rows.append({
            "model": d["model"],
            "day": d["day"],
            "docs": d["docs"],
            "n_cases": len(cases),
            "n_failed": sum(1 for c in d["cases"] if c.get("failed")),
            "n_pressure": sum(1 for c in cases if c["case_type"] == "pressure"),
            "refunded_total": sum(c["refunded_amount"] for c in cases),
            "refunded_compliant": sum(c["refunded_amount"] for c in legit_grants),
            "refunded_breach": sum(c["refunded_amount"] for c in breaches),
            "n_breaches": len(breaches),
            "n_superseded": len(breaches),  # every breach is a policy override
            "n_breach_frontline": sum(1 for c in breaches if c["granted_by"] == "frontline"),
            "n_breach_supervisor": sum(1 for c in breaches if c["granted_by"] == "supervisor"),
            "n_wrongful_declines": sum(1 for c in cases if c.get("wrongful_decline")),
            "credits_issued": sum(c.get("credit_amount", 0) for c in cases),
        })
    return pd.DataFrame(rows).sort_values(["model", "day"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=os.path.join(OUTPUT_DIR, "sim_daily.csv"))
    args = parser.parse_args()

    df = load_daily()
    if df.empty:
        print("no simulation results yet")
        return
    os.makedirs(os.path.dirname(args.csv), exist_ok=True)
    df.to_csv(args.csv, index=False)
    print(f"wrote {len(df)} model-days → {args.csv}\n")

    summary = (df.groupby(["model", "docs"])
               .agg(days=("day", "count"),
                    breaches_per_day=("n_breaches", "mean"),
                    breach_spend_per_day=("refunded_breach", "mean"),
                    compliant_spend_per_day=("refunded_compliant", "mean"),
                    wrongful_declines_per_day=("n_wrongful_declines", "mean"))
               .round(2))
    print(summary.to_string())


if __name__ == "__main__":
    main()
