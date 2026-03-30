# Week 3 Update

## Summary

Week 3 turned Leviathan from a decision-intelligence product into a clearer constitutional execution stack for Web4 agent workflows.

This cycle focused on one core objective: connect attribution, policy, execution lanes, and review state into a single operator- and agent-facing workflow.

## What We Shipped

### 1) AEP Constitution Kernel Expansion

- Expanded AEP from a narrow authorization concept into a framework-agnostic constitutional kernel.
- Added a clearer case lifecycle across authorization, execution, and review.
- Formalized Leviathan as execution infrastructure rather than analytics-only infrastructure.

What this means in practice:

- each action is now bound to a stable `case_id`
- constitutional approval sits in front of execution
- execution results and retrospective review are written back into the same case state
- the audit and liability trail is preserved across the full local workflow

### 2) Multi-Action AEP Workflow

- Extended AEP workflow coverage beyond trade-only handling.
- Added support for structured action flows across:
  - trade
  - payment
  - approve
  - contract call

Current execution semantics are explicit:

- `trade` and `payment` can run through the controlled devnet / paper execution path
- `approve` and `contract_call` are currently constrained to paper-mode execution

This matters because the product is now closer to a real constitutional execution kernel, not just a token-risk gate.

### 3) Live Attribution Routing for Devnet Trade Requests

- Added a routing layer that prefers live causal attribution for devnet trade requests.
- Added fail-closed fallback to provided paper risk input when live attribution is unavailable.
- Recorded the selected attribution route in the case itself for later audit and review.

This improves the relationship between Leviathan MCP / AEP and the attribution engine:

- when live attribution is available, AEP can bind execution to fresher runtime evidence
- when live attribution fails, the kernel still behaves deterministically and records the fallback instead of silently degrading

### 4) Controlled Devnet Execution Lane Hardening

- Continued hardening the controlled devnet lane for approved cases.
- Preserved execution-lane separation between:
  - constitutional approval
  - prepared devnet bundle execution
  - reconciliation and local writeback
- Improved retry behavior around bundle preparation / fresh-bundle recovery.

This is important for evaluator credibility: devnet execution is no longer treated as a disconnected demo artifact, but as part of the constitutional case lifecycle.

### 5) Attribution Runtime Quality Upgrades

- Fixed cross-token reuse overlap logic that could under-report recurrence signals.
- Removed stale inbound conversion fallback behavior when reliable pricing is unavailable.
- Parallelized top-source convergence probing to reduce waiting time in the tracing stage.
- Preserved cacheable report delivery while keeping live refresh available when deeper validation is needed.

## Quality Improvements

- Repaired kernel and CLI regressions identified during validation.
- Re-ran the AEP kernel test suite after the latest state-machine changes.
- Re-ran attribution-side validation for report, analytics, and compliance tracks.
- Preserved controlled public-output boundaries while continuing to improve machine-facing delivery.

## Demo/Review Impact

- Clearer explanation of Leviathan as Web4 constitutional execution infrastructure.
- Stronger bridge from attribution evidence to executable `ALLOW / REVIEW / BLOCK` decisions.
- Better evaluator visibility into how attribution, policy, execution, and review connect inside a single workflow.
- Stronger MCP / agent story: the system is moving from “risk output” toward “machine-consumable execution control.”

## Next Focus

- Throughput and latency upgrades for larger batch analysis scenarios.
- Additional visualization polish for evaluator readability.
- Continued refinement of the case workflow and operator-facing displays.
- More execution-surface hardening for live agent and evaluator demonstrations.
