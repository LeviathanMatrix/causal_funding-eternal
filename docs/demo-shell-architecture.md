# Demo Shell Architecture

## Purpose

`demo_shell` is a public demo layer for Eternal.

It is intentionally public-safe, but no longer just a thin form wrapper:

- Collect input (mint + mode)
- Forward request to configured analysis endpoint
- Build an evaluator-facing console from the returned report
- Support scenario simulation and review workflows
- Keep the public repo reviewable without exposing core implementation

## Layering

1. **Public Demo Shell (Open Source)**
- UI and request forwarding
- Public/Judge display modes
- Executive decision rendering
- Evidence surfaces
- Hard-evidence brief
- What-if simulation
- Case review / watchlist / recheck
- Redacted fallback sample

2. **Connected Analysis Service**
- Decision output generation
- Evidence packaging
- Evaluator-facing access modes

## Why This Design

- Demonstrates real product behavior in public
- Keeps the public repository focused and understandable
- Supports judge/pilot access without leaking core IP
- Lets the public layer prove workflow value, not only API connectivity

## Environment Variables

- `CF_DEMO_BACKEND_URL`: analysis `/api/analyze` endpoint
- `CF_DEMO_API_KEY`: optional bearer key
- `CF_DEMO_JUDGE_TOKEN`: optional evaluator access token for judge mode

## Run

```bash
cd demo_shell
cp .env.example .env
pip install -r requirements.txt
python app.py
```
