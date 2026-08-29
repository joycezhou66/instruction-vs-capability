"""Analysis: primary outcome tallies with Wilson CIs, plus a human
transcript reader.

  ./.venv/bin/python analyze.py results/pilot            # tally + CIs
  ./.venv/bin/python analyze.py results/pilot --read baseline 0   # one episode

The primary analysis touches ONLY the mechanically-scored harmful_action
field — no judge output is read here (see CLAUDE.md: judge is for secondary
outcomes, and only after passing the 85% agreement gate).
"""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def wilson_ci(k, n, z=1.96):
    """95% Wilson score interval for a binomial proportion. Chosen over the
    normal approximation because our rates sit near 0 and 1 at small n,
    where the naive interval degenerates."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def load(results_dir):
    recs = [json.loads(p.read_text())
            for p in sorted(Path(results_dir).glob("*.json"))]
    if not recs:
        raise SystemExit(f"no transcripts in {results_dir}")
    return recs


def tally(recs):
    by_cond = defaultdict(list)
    for r in recs:
        by_cond[r["condition"]].append(r)
    print(f"{'condition':<12} {'harmful':>8} {'rate':>6}   95% Wilson CI   stops")
    for cond, rs in by_cond.items():
        k, n = sum(r["harmful_action"] for r in rs), len(rs)
        lo, hi = wilson_ci(k, n)
        stops = defaultdict(int)
        for r in rs:
            stops[r["stop"]] += 1
        print(f"{cond:<12} {k:>4}/{n:<3} {k/n:>6.0%}   "
              f"[{lo:.0%}, {hi:.0%}]   {dict(stops)}")


def read_episode(recs, condition, ep):
    r = next(r for r in recs
             if r["condition"] == condition and r["episode_id"] == ep)
    print(f"=== {r['scenario']} / {r['condition']} / ep{ep} — "
          f"harmful={r['harmful_action']} stop={r['stop']} "
          f"turns={r['turns']} ===\n")
    for msg in r["messages"]:
        blocks = (msg["content"] if isinstance(msg["content"], list)
                  else [{"type": "text", "text": msg["content"]}])
        for b in blocks:
            if isinstance(b, dict) and b.get("type") == "thinking" and b.get("thinking"):
                print(f"  [thinking] {b['thinking'][:600]}\n")
            elif isinstance(b, dict) and b.get("type") == "text":
                print(f"[{msg['role'].upper()}] {b['text']}\n")
            elif isinstance(b, dict) and b.get("type") == "tool_use":
                print(f"  -> TOOL CALL {b['name']}({json.dumps(b['input'])})")
            elif isinstance(b, dict) and b.get("type") == "tool_result":
                content = b["content"]
                print(f"  <- {content}\n" if isinstance(content, str)
                      else f"  <- {content}\n")
    if r["harmful_calls"]:
        print("!! HARMFUL CALLS (model's own logged reasons):")
        for c in r["harmful_calls"]:
            print(f"   - {c}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--read", nargs=2, metavar=("CONDITION", "EP"))
    args = ap.parse_args()
    recs = load(args.results_dir)
    if args.read:
        read_episode(recs, args.read[0], int(args.read[1]))
    else:
        tally(recs)
