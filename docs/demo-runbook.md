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
- Optional backup mint: `So11111111111111111111111111111111111111112` (wSOL)

## Public Demo Command

```bash
cd demo_shell
cp .env.example .env
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:7860` and run the mint in public/judge display mode.

For controlled evaluators, the same shell can forward to a configured analysis endpoint through environment configuration.

## Must-Capture Frames For Video

1. Start command with mint input
2. Auto pool detection and seed discovery
3. Final risk score + confidence
4. Decision action (ALLOW / REVIEW / BLOCK)
5. Evidence highlights and forensic summary

## What To Avoid Showing

- Non-public endpoints
- Sensitive API keys
- Internal configuration details
- Non-public implementation details
