"""Orchestrate an eval run: N episodes per condition, resumable, budgeted.

Usage:
  source .env && ./.venv/bin/python run_eval.py --conditions baseline --n 5 \
      --out results/pilot            # Gate-1 pilot
  source .env && ./.venv/bin/python run_eval.py --n 20 --out results/full

Episodes already on disk are skipped, so a crashed or interrupted run is
resumed by re-running the same command. Order is condition-major and
deterministic, purely so resume bookkeeping stays simple — each episode is
an independent API conversation either way.
"""

import argparse
import json
from pathlib import Path

import anthropic

from permissions import CONDITIONS
from rollout import run_episode
from scenarios import SCENARIOS

# Opus 5 pricing, USD per million tokens (checked 2026-08-28).
PRICE_IN, PRICE_OUT = 5.00, 25.00


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="pipeline_integrity")
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS))
    ap.add_argument("--n", type=int, required=True, help="episodes per condition")
    ap.add_argument("--out", required=True, help="output dir, e.g. results/pilot")
    ap.add_argument("--model", default="claude-opus-5")
    args = ap.parse_args()

    scenario = SCENARIOS[args.scenario]
    client = anthropic.Anthropic()
    cost = 0.0

    for condition in args.conditions:
        tally = {"done": 0, "harmful": 0}
        for ep in range(args.n):
            path = (Path(args.out) /
                    f"{scenario.name}__{condition}__ep{ep:03d}.json")
            if path.exists():
                rec = json.loads(path.read_text())
                print(f"  [skip] {path.name} (already on disk)")
            else:
                rec = run_episode(client, scenario, condition, ep,
                                  model=args.model, out_dir=args.out)
            tally["done"] += 1
            tally["harmful"] += rec["harmful_action"]
            u = rec["usage"]
            cost += (u["input_tokens"] * PRICE_IN
                     + u["output_tokens"] * PRICE_OUT) / 1e6
            print(f"  {condition} ep{ep:03d}: harmful={rec['harmful_action']} "
                  f"stop={rec['stop']} turns={rec['turns']} "
                  f"(run total ~${cost:.2f})")
        print(f"== {condition}: {tally['harmful']}/{tally['done']} harmful ==\n")

    print(f"TOTAL estimated cost this invocation: ~${cost:.2f}")


if __name__ == "__main__":
    main()
