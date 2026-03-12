# causal_funding Eternal

`causal_funding` is a Solana-native, decision-grade risk intelligence system for listing review, investment screening, and pre-trade gating.

**From raw on-chain noise to an auditable BLOCK / REVIEW / ALLOW decision in minutes.**

## Judge TL;DR

- Not a score-only tool: this demo outputs decision + evidence + governance status.
- Built for Solana speed: designed for real-time listing, investment, and pre-trade workflows.
- Production-minded quality controls: threshold calibration + drift-aware policy tightening.
- Internal replay snapshot: rug catch `0.8857`, safe block `0.05`, block precision `0.9688`.

This is not a toy rug checker. The system runs as a closed loop:

1. Causal funding attribution
2. Multi-dimensional risk scoring
3. Evidence-grade forensic packaging
4. Operator-facing judgment synthesis
5. Calibrated ALLOW / REVIEW / BLOCK policy
6. Drift-aware policy governance

## Why Solana

Solana is one of the best execution environments for real-time products: fast finality, low friction, and high throughput.

That advantage also compresses risk windows. Capital can move fast, narratives can move faster, and manual diligence often arrives too late. `causal_funding` is built for this exact operating reality: make explainable risk decisions at Solana speed.

## What This Demo Proves

The Eternal demo is designed to prove production-minded decision quality, not just dashboard output:

- Input: token mint (pool can be auto-detected)
- Output: structured risk report + evidence package
- Decision layer: ALLOW / REVIEW / BLOCK
- Governance layer: drift-aware threshold control and recalibration signal

## Current Capability Highlights

- Causal path tracing from project-linked seeds to upstream sources
- Multi-dimensional risk engine with cross-signal penalties
- Forensic recovery of execution-root operators and creation anchors
- Agent-ready judgment artifacts for operator review
- Calibrated decision policy from historical replay data
- Drift closure loop with automatic threshold tightening under unstable regimes

## Internal Calibration Snapshot (Current)

From the current internal provisional labeled set:

- Rug catch rate (BLOCK + REVIEW): `0.8857`
- Safe block rate: `0.05`
- Block precision: `0.9688`

This is exactly the direction we want for institutional workflows: high catch quality with controlled false blocks.

## What Is Open vs Private

This repository is intentionally product-facing.

Open in demo:

- Product positioning
- Demo scope
- Roadmap and integration direction
- Public-facing operating narrative

Private by design:

- Full production architecture
- Internal weighting details and threshold internals
- Private data connectors and enrichment logic
- Full model-training pipeline and proprietary evidence transformations

## Who This Is Built For

- Exchange listing and risk teams
- Crypto funds and due-diligence teams
- Market makers and launch platforms
- Security and monitoring operators

## Partnering

We are actively open to:

- Strategic capital partners
- Pilot integration partners (exchange/fund/workflow teams)
- Data partners for enrichment and coverage expansion

Current access is controlled for judges and selected pilot counterparts.

## Repository Guide

- `docs/product-positioning.md`
- `docs/demo-scope.md`
- `docs/roadmap.md`

## Status

Prepared and actively iterated for Colosseum Eternal (March 2026).
