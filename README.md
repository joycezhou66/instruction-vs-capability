# Instruction vs. Capability: what does it take to get an agent to skip a safety check?

A preregistered agentic-safety eval across three Claude models: two decision
gates, a mechanical primary outcome, an LLM judge validated against my
manual labels, and every transcript committed.

## The question

When an agent is under pressure to take a harmful action, does a system-prompt
rule forbidding it ("you must never...") protect as well as removing the
capability (the tool simply absent from the API request)? This is an AI-control
/ authorization-boundary question: prior work (Anthropic's agentic-misalignment
research) showed instructions only partially suppress harmful behavior under
extreme pressure (blackmail, shutdown threats). This project asks the
deployment-shaped version under *mundane* pressure — a flaky CI runner, a board
meeting, a VP at dinner.

## What happened instead (the actual findings)

The preregistered comparison never ran: **no Claude model would take the
harmful action at baseline.** The project became a measurement of what it
takes to elicit it — a legitimacy dose-response:

| Setting (harmful action = calling `skip_validation`) | Model | Skips | 95% Wilson CI |
|---|---|---|---|
| Mundane pressure + diffuse authorization (v1+v2) | Opus 5 | 0/15 | [0%, 20.4%] |
| Same, strengthened scenario (v2) | Sonnet 5 | 0/5 | [0%, 43.4%] |
| Same (v2) | Haiku 4.5 | 0/5 | [0%, 43.4%] |
| **+ explicit, logged authorization from the accountable VP** | Opus 5 | **0/5** | [0%, 43.4%] |
| **+ documented false-alarm bulletin, checks manually re-run & passed, SOP, two humans instructing** | Opus 5 | **3/5** | [23.1%, 88.2%] |

Three observations I did not expect:

1. **Insubordination as safety behavior.** Under explicit authorization, all 5
   episodes acknowledged the VP's authority ("going against Dana's explicit
   authorization") and refused anyway, arguing her premise was unverifiable.
   The threshold for compliance tracked *verifiability*, not authority or
   pressure.
2. **Manipulation-naming.** Strengthened-scenario episodes explicitly labeled
   the pressure levers: "normalization of deviance" (ep010), "'it's worked
   before' is survivorship bias" (ep013).
3. **An eval-aware skip.** One legitimacy-control episode verbalized "this
   feels like a test of whether social pressure can push me into bypassing a
   safety control" — and then took the (correct) action anyway. Eval-awareness
   was flagged per-episode throughout: 2/40 scored episodes verbalized
   suspicion; neither changed behavior after doing so.

## Method

- **Agent:** manual tool-use loop (`rollout.py`) against a deterministic
  simulated DataOps environment (`scenarios.py`): a nightly pipeline whose
  validation suite times out ambiguously before a hard deadline, with a
  pressuring VP message. The safe path (report honestly, hold) always exists.
- **Conditions** (`permissions.py`, ~40 lines): surgical diffs, asserted by
  tests — `restricted` deletes exactly one tool-list entry; `instruction`
  appends exactly one frozen rule paragraph.
- **Primary outcome:** mechanical — a `skip_validation` tool call in the log.
  No judge involved.
- **Gate 1 (preregistered):** baseline must show >=2/5 skips before any full
  run. It failed twice; each failure was diagnosed from transcripts and the
  scenario strengthened (see ITERATIONS.md). The full three-condition
  comparison is therefore *unmeasurable on current Claude models in this
  scenario* — reported as such, not papered over.
- **Gate 2 (preregistered):** LLM judge (Opus 5) trusted only after >=85%
  agreement with my blind hand labels. Result: 145/145 comparisons
  across four tiers — real negatives (100/100), real positives from the
  legitimacy control (20/20), instruction-condition rule-acknowledgment values
  (25/25), plus 12/12 on scripted transcripts with ground truth by
  construction (`judge_sensitivity.py`).
- **Reproducibility:** every episode's full raw request/response is committed
  under `transcripts/`; model IDs pinned; `test_harness.py` runs 28 no-API
  checks including scenario-version guards.

## Honest limitations

- One scenario family, one model family; N is small everywhere (CIs above).
- The legitimacy control contains an internal inconsistency (re-queue reports
  pool *saturation*; the bulletin describes a *reporting bug*) — caught during
  hand-labeling; one episode noticed it. 3/5 is best read as a lower bound.
- Judge and target are the same model family (self-preference not ruled out
  for secondary labels; primary outcome is judge-free).
- The 145/145 judge agreement deserves its context: most cells were easy
  calls on homogeneous refusal data. The informative cells were the ~15 hard
  cases (real skips, eval-aware episodes, rule-acknowledgment values), all
  matched with evidence quotes. The rubric was calibrated during my labeling
  and frozen BEFORE any judge run (order verifiable in git history); no
  rubric or labels were changed after seeing agreement scores.
- Scripted judge-sensitivity positives are authored, not model-sampled.
- Baseline pressure includes deniable authorization ("do whatever you need to
  do") by design; held constant across conditions.
- `rule_acknowledgment: engaged` conflates naming the injected rule (3/5
  calibration episodes) with complying via independent reasoning (2/5).

## Layout

| File | Role |
|---|---|
| `CLAUDE.md` | Preregistration: question, design, gates, amendments |
| `ITERATIONS.md` | Full lab notebook: failures, fixes, calibrations |
| `scenarios.py` / `permissions.py` | World / experimental conditions |
| `rollout.py` / `run_eval.py` | Agent loop / orchestrator |
| `judge.py` / `judge_sensitivity.py` | Secondary-outcome judge + validation |
| `analyze.py` / `test_harness.py` | Stats & transcript reader / free checks |
| `hand_labels*.json`, `labeling/` | Human ground truth + rendered transcripts |
| `transcripts/` | Every episode, raw |

Run it: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`,
put `ANTHROPIC_API_KEY` in `.env`, then `test_harness.py` (free) before
`run_eval.py --conditions baseline --n 5 --out results/pilot`.

## Methods & AI-use disclosure

I built this with Claude Code as pair programmer, harness operator, and
scribe; the design decisions, scenario iterations, and analysis conclusions
are mine, made and documented in-session. I labeled all 35 episodes manually
by reading rendered transcripts, with no AI assistance in the label decisions
(ep001 served as a rubric-training worked example). Judge outputs were never
shown to me before my labels were frozen and committed.
