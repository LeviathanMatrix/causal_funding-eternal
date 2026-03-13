# Demo Runbook

This runbook defines the canonical 1-minute demo flow for Eternal updates.

## Goal

Show a complete operator decision loop:

1. Input mint
2. Risk and evidence generation
3. ALLOW / REVIEW / BLOCK decision
4. Governance status (drift closure)

## Demo Inputs

- Primary mint: `DoBAMMqcedjoWV3m7JEU1pAzZjkQqeQzbdLUA2etbonk`
- Optional backup mint: `TODO_BACKUP_MINT`

## Command

```bash
python3 -m onchain_monitor.causal_funding \
  --mint <TOKEN_MINT> \
  --enable-advanced-signals \
  --enable-decision-policy \
  --decision-policy-path data/calibration/causal_decision_policy_v2.json \
  --enable-drift-closure \
  --output data/causal_reports/<TOKEN_MINT>_demo.json
```

## Must-Capture Frames For Video

1. Start command with mint input
2. Auto pool detection and seed discovery
3. Final risk score + confidence
4. Decision action (ALLOW / REVIEW / BLOCK)
5. Evidence highlights and forensic summary

## What To Avoid Showing

- Internal private endpoints
- Sensitive API keys
- Proprietary threshold internals
- Full production architecture details

