# Demo Shell Architecture

## Purpose

`demo_shell` is a public demo layer for Eternal.

It is intentionally thin:

- Collect input (mint + mode)
- Forward request to private backend API
- Render decision + evidence summary
- Hide core internals

## Layering

1. **Public Demo Shell (Open Source)**
- UI and request forwarding
- Public/Judge display modes
- Redacted fallback sample

2. **Private Production Engine (Not Open Source)**
- Causal attribution internals
- Risk scoring internals
- Policy internals and advanced orchestration

## Why This Design

- Demonstrates real product behavior in public
- Protects proprietary logic and private connectors
- Supports judge/pilot access without leaking core IP

## Environment Variables

- `CF_DEMO_BACKEND_URL`: backend `/api/analyze` endpoint
- `CF_DEMO_API_KEY`: optional bearer key
- `CF_DEMO_JUDGE_TOKEN`: optional judge token for judge mode

## Run

```bash
cd demo_shell
cp .env.example .env
pip install -r requirements.txt
python app.py
```

