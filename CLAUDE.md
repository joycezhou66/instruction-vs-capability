# Instruction vs. Capability: an agentic safety eval

## Research question

This project measures whether a system-prompt rule forbidding a harmful action
reduces that action as much as removing the agent's ability to perform it. We
place an agent (Claude Opus 5) in a simulated data-pipeline scenario with
deadline pressure and measure how often it skips a required validation check
under three conditions: capability present with no rule (baseline), capability
removed (restricted), and capability present but forbidden by a firm
system-prompt rule (instruction). If the instruction condition leaves a
meaningful gap versus capability removal, that is evidence that prompt-level
rules are not a substitute for affordance-level controls in agent deployments.

## Gates (preregistered — do not proceed past a failed gate)

1. **Baseline gate:** the baseline condition must show the harmful behavior in
   a small pilot before any money is spent on the full run. If baseline is
   ~0%, the scenario gets strengthened — the sample size does not get scaled.
2. **Judge gate:** the LLM judge must reach >=85% agreement with Joyce's own
   hand labels on a sample of transcripts before any judge-produced number is
   trusted or reported.

## Standing rules for Claude in this repo

- Explain every change you make, before or as you make it.
- Never accept or make a design decision on Joyce's behalf — present options
  or a diff with reasoning, and she decides.
- Never build more than one component ahead of her demonstrated understanding.
  She must be able to defend every design choice in a live interview with no
  AI help. That is the deliverable.
