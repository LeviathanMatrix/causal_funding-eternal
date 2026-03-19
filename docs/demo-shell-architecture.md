# Demo Shell Architecture

## Purpose

`demo_shell` is a public demo layer for Eternal.

It is intentionally thin:

- Collect input (mint + mode)
- Forward request to configured analysis endpoint
- Render decision + evidence summary
- Keep the demo surface simple and reviewable

## Layering

1. **Public Demo Shell (Open Source)**
- UI and request forwarding
- Public/Judge display modes
- Redacted fallback sample

2. **Connected Analysis Service**
- Decision output generation
- Evidence packaging
- Evaluator-facing access modes

## Why This Design

- Demonstrates real product behavior in public
- Keeps the public repository focused and understandable
- Supports judge/pilot access without leaking core IP

## Environment Variables

- `CF_DEMO_BACKEND_URL`: analysis `/api/analyze` endpoint
- `CF_DEMO_API_KEY`: optional bearer key
- `CF_DEMO_JUDGE_TOKEN`: optional judge token for judge mode

## Run

```bash
cd demo_shell
cp .env.example .env
pip install -r requirements.txt
python app.py
```
