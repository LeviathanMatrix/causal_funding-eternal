# Demo Scope

## Demo Goal

Prove that `causal_funding` can support real operator decisions on Solana in minutes, with explainable outputs and policy governance.

## Judge-Facing Flow

1. Input a mint address
2. Auto-discover pool context when available
3. Run causal attribution and forensic synthesis
4. Produce risk report and evidence package
5. Return ALLOW / REVIEW / BLOCK decision
6. Attach drift-governance status (normal vs strict mode)

## What We Intentionally Showcase

- Decision quality over UI cosmetics
- Explainable outputs over black-box scoring
- Operational consistency over one-off anecdotes
- Production-minded controls over unrestricted exposure

## Runtime Expectation

Current first-pass runtime target remains approximately `1-2 minutes` per token under normal conditions, while optimization continues.

## Key Demo Messages

- This is not a basic rug checker.
- The system outputs decisions, evidence, and governance signals.
- Agent-driven interpretation turns raw on-chain evidence into operator-readable conclusions.
- The product is designed for listing, investment, and pre-trade workflows.
- There is a credible path to restricted institutional deployment.

## Current Internal Evaluation Snapshot

From current provisional replay calibration (rounded for public sharing):

- Rug catch rate (BLOCK + REVIEW): `~89%`
- Safe block rate: `~5%`
- Block precision: `~97%`

These values are included to show practical operating posture, not marketing-only claims.

## What Is Not Public In Demo

- Full proprietary architecture and orchestration internals
- Sensitive threshold internals and weighting details
- Private data and enrichment connectors
- Full training pipeline and private operational tuning logic

## Success Criteria

The demo succeeds when a reviewer can clearly see:

- Why the product matters specifically on Solana
- Why decision output is stronger than score-only output
- Why the evidence package is practical for real workflows
- Why the private moat remains intact despite a strong public demo
