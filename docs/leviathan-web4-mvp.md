# Leviathan Web4 MVP

## Why Leviathan Exists

As AI agents move toward autonomous on-chain trading and coordination, a hard constraint appears:

**today's crypto execution stack was designed for human operators, not autonomous machine operators.**

That creates a structural Web4 gap in three areas:

- **Boundary gap:** agents lack machine-verifiable constitutional execution boundaries.
- **Decision gap:** most tooling emits raw data or alerts, not pre-trade decisions an agent can act on.
- **Accountability gap:** execution trails are fragmented, making audit and responsibility assignment weak.

## Our Product Response

Leviathan is built as a **constitutional execution layer for Web4 agents on Solana**, not as a wallet utility and not as a score-only scanner.

Leviathan has two core components:

1. **AI Constitution / AEP layer**
   - machine-verifiable execution guardrails
   - accountable permission boundaries for agents
   - auditable decision trace and identity-aware policy hooks

2. **Leviathan MCP layer**
   - converts complex on-chain context into machine-usable decisions
   - returns `ALLOW / REVIEW / BLOCK` with confidence and evidence surfaces
   - supports both autonomous agents and human operators in the same flow

## Why Attribution Is The Core

The attribution engine is the center of Leviathan's practical value.

It gives agents and operators a decision object before execution, so they do not need to consume full raw traces per token every time.

Operationally, this means:

- lower decision latency for autonomous pipelines
- lower token/time burn for repeated risk checks
- stronger downside control before trade/listing actions
- better hit-rate conditions for discovering high-upside opportunities under controlled risk

## Why Solana

Solana is the right execution environment for this system:

- high throughput and low cost fit machine-driven repeated decision loops
- fast finality compresses the time window where pre-trade risk control must work
- agent-native workflows need low-friction decision calls at runtime, not delayed analyst workflows

Leviathan is designed for this exact operating reality: **decision-grade controls at Solana speed**.

## MVP Scope (Public + Controlled)

In current MVP scope:

- public layer demonstrates decision workflow, evidence surfaces, and review context
- controlled evaluator flow demonstrates deeper agent-facing decision integration paths
- core attribution and policy internals remain intentionally sealed

This is an implementation-first MVP direction, not narrative-only positioning.
