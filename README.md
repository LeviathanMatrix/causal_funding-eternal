# causal_funding Eternal

`causal_funding` is a Solana-native causal attribution and risk intelligence system built for high-speed decision environments.

It is not a basic rug checker. The product is designed to move from suspicious-signal detection to funding-path attribution, multi-dimensional risk scoring, evidence organization, and agent-supported judgement in a single closed loop. The current system is optimized to produce a first-pass structured result in roughly 1-2 minutes per token while we continue improving speed, stability, and operator usability.

## Why Solana

Solana makes real-time, high-throughput on-chain applications practical at scale. That same execution speed creates a new requirement for risk intelligence: if opportunity and risk both compress into short windows, diligence has to become faster, more structured, and more explainable.

`causal_funding` is being built around that reality. The goal is to give operators a system that can support listing review, investment screening, and pre-trade judgement on a chain where waiting too long often means acting too late.

## What the Product Does

- Traces suspicious token funding paths from project-linked wallets to upstream sources.
- Combines multiple signals into a structured, multi-dimensional risk view.
- Organizes evidence into reviewable outputs instead of a single black-box score.
- Uses an agent layer to turn evidence into readable, decision-oriented conclusions.
- Generates closed-loop output that can later support model training and system improvement.

## Current Product Position

The current Eternal build is aimed at:

- exchange listing and risk teams
- crypto funds and research teams
- market makers and launchpads
- security and monitoring teams

This repository is intentionally product-facing. It documents the external positioning, demo scope, and execution roadmap without exposing sensitive internal implementation details or the full production architecture.

## Access Model

The API is currently in restricted evaluation mode for judges and selected pilot partners only. Public API access is not the immediate priority. The near-term focus is product quality, evidence clarity, and controlled evaluation before broader rollout.

## Repository Guide

- `docs/product-positioning.md`
- `docs/demo-scope.md`
- `docs/roadmap.md`

## Product Direction

The production path is clear:

- improve latency and result consistency
- strengthen evidence-grade reporting
- refine the agent output layer for operator decisions
- prepare controlled API and high-concurrency batch analysis for institutional pilots

## Status

This repository was prepared for Colosseum Eternal on March 12, 2026.
