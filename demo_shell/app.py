from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from flask import Flask, jsonify, render_template_string, request

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

APP = Flask(__name__)

BACKEND_URL = os.environ.get("CF_DEMO_BACKEND_URL", "http://127.0.0.1:7878/api/analyze").strip()
BACKEND_API_KEY = os.environ.get("CF_DEMO_API_KEY", "").strip()
JUDGE_TOKEN = os.environ.get("CF_DEMO_JUDGE_TOKEN", "").strip()
TIMEOUT_SEC = float(os.environ.get("CF_DEMO_TIMEOUT_SEC", "90") or 90)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = ROOT / "examples" / "sample_report_redacted.json"


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _render_view(payload: dict[str, Any]) -> str:
    demo_view = payload.get("demo_view") if isinstance(payload.get("demo_view"), dict) else {}
    decision = demo_view.get("decision") if isinstance(demo_view.get("decision"), dict) else {}
    agent = demo_view.get("agent_judgement") if isinstance(demo_view.get("agent_judgement"), dict) else {}
    evidence = demo_view.get("hard_evidence") if isinstance(demo_view.get("hard_evidence"), list) else []
    drift = demo_view.get("drift_governance") if isinstance(demo_view.get("drift_governance"), dict) else {}

    status = str(decision.get("action") or "REVIEW").upper()
    if status not in {"ALLOW", "REVIEW", "BLOCK"}:
        status = "REVIEW"

    evidence_items = "".join(
        (
            "<li><b>{seed}</b> -> {term}, flow={flow:.2f} SOL, depth={depth}</li>".format(
                seed=str(row.get("seed_role") or ""),
                term=str(row.get("terminal") or ""),
                flow=float(row.get("flow_sol") or 0.0),
                depth=int(row.get("depth") or 0),
            )
        )
        for row in evidence[:5]
        if isinstance(row, dict)
    ) or "<li>No evidence rows.</li>"

    return render_template_string(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>causal_funding Demo Shell</title>
  <style>
    body { font-family: Arial, sans-serif; background: #0d1418; color: #e8f2ef; margin: 0; }
    .wrap { max-width: 1000px; margin: 0 auto; padding: 20px; }
    .panel { background: #111e24; border: 1px solid #24434e; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 10px; }
    .k { color: #8ab0a2; font-size: 12px; text-transform: uppercase; }
    .v { font-size: 24px; font-weight: 700; }
    .pill { display:inline-block; padding: 5px 10px; border-radius: 999px; font-weight: 700; }
    .ALLOW { background:#3ad18d; color:#052015; }
    .REVIEW { background:#f4c157; color:#231804; }
    .BLOCK { background:#f06274; color:#2a060e; }
    input,select,button { padding: 8px 10px; border-radius: 8px; border: 1px solid #345866; background: #13262f; color: #e8f2ef; }
    button { cursor: pointer; }
    ul { margin: 8px 0 0 18px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h2>causal_funding Demo Shell</h2>
      <p>Open demo layer. Core production logic runs in private backend.</p>
      <form method="post" action="/analyze">
        <input type="text" name="mint" required placeholder="Solana mint" value="{{mint}}" />
        <select name="mode">
          <option value="public" {% if not judge %}selected{% endif %}>Public mode</option>
          <option value="judge" {% if judge %}selected{% endif %}>Judge mode</option>
        </select>
        <button type="submit">Analyze</button>
      </form>
    </div>

    <div class="grid">
      <div class="panel">
        <div class="k">Decision</div>
        <div class="v"><span class="pill {{status}}">{{status}}</span></div>
        <div>risk={{risk_score}} | confidence={{conf}}</div>
      </div>
      <div class="panel">
        <div class="k">Agent Judgement</div>
        <div class="v">{{verdict}}</div>
        <div>{{conclusion}}</div>
      </div>
      <div class="panel">
        <div class="k">Controller</div>
        <div class="v" style="font-size:16px;">{{controller}}</div>
        <div>repeat_offender={{repeat}}</div>
      </div>
      <div class="panel">
        <div class="k">Drift Governance</div>
        <div class="v">{{mode}}</div>
        <div>drift={{drift}} | recalibration={{recal}}</div>
      </div>
    </div>

    <div class="panel">
      <div class="k">Hard Evidence</div>
      <ul>{{ evidence|safe }}</ul>
    </div>
  </div>
</body>
</html>
        """,
        mint=str(demo_view.get("mint") or ""),
        judge=bool(demo_view.get("judge_mode")),
        status=status,
        risk_score=float(decision.get("risk_score") or 0.0),
        conf=float(decision.get("confidence") or 0.0),
        verdict=str(agent.get("verdict_level") or "").upper(),
        conclusion=str(agent.get("risk_conclusion") or ""),
        controller=str(agent.get("who_controls") or ""),
        repeat=bool(agent.get("repeat_offender")),
        mode=str(drift.get("mode") or "unknown"),
        drift=bool(drift.get("drift_detected")),
        recal=bool(drift.get("recalibration_needed")),
        evidence=evidence_items,
    )


def _fallback_payload(mint: str, judge_mode: bool) -> dict[str, Any]:
    sample = _safe_json(SAMPLE_FILE)
    return {
        "ok": True,
        "source": "sample_fallback",
        "demo_view": {
            "mint": mint,
            "symbol": "SAMPLE",
            "judge_mode": judge_mode,
            "decision": {
                "action": (sample.get("decision_policy") or {}).get("action", "REVIEW"),
                "risk_score": float((sample.get("risk") or {}).get("score") or 0.0),
                "confidence": float((sample.get("risk") or {}).get("confidence") or 0.0),
                "confidence_label": str((sample.get("risk") or {}).get("confidence_label") or ""),
                "reason": str(((sample.get("decision_policy") or {}).get("reason") or "fallback_sample")),
            },
            "agent_judgement": {
                "verdict_level": str((sample.get("judgement") or {}).get("verdict_level") or ""),
                "risk_conclusion": str((sample.get("judgement") or {}).get("risk_conclusion") or ""),
                "who_controls": "REDACTED",
                "repeat_offender": True,
            },
            "hard_evidence": [
                {
                    "seed_role": "sample_path",
                    "terminal": "sample_terminal",
                    "flow_sol": 0.0,
                    "depth": 0,
                }
            ],
            "drift_governance": {
                "mode": "normal",
                "drift_detected": False,
                "recalibration_needed": False,
            },
        },
    }


@APP.get("/")
def index() -> str:
    payload = _fallback_payload("", False)
    return _render_view(payload)


@APP.post("/analyze")
def analyze_form() -> Any:
    mint = str(request.form.get("mint") or "").strip()
    mode = str(request.form.get("mode") or "public").strip().lower()
    judge_mode = mode == "judge"

    req_payload = {
        "mint": mint,
        "judge_mode": judge_mode,
        "force": False,
    }
    headers = {"Content-Type": "application/json"}
    if BACKEND_API_KEY:
        headers["Authorization"] = f"Bearer {BACKEND_API_KEY}"
    if JUDGE_TOKEN and judge_mode:
        headers["X-Judge-Token"] = JUDGE_TOKEN

    try:
        resp = requests.post(BACKEND_URL, json=req_payload, headers=headers, timeout=TIMEOUT_SEC)
        if resp.status_code >= 300:
            payload = _fallback_payload(mint, judge_mode)
            payload["error"] = f"backend_http_{resp.status_code}"
        else:
            payload = resp.json()
    except Exception:
        payload = _fallback_payload(mint, judge_mode)
        payload["error"] = "backend_unreachable"

    return _render_view(payload if isinstance(payload, dict) else _fallback_payload(mint, judge_mode))


@APP.post("/api/analyze")
def analyze_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    judge_mode = bool(body.get("judge_mode"))

    req_payload = {
        "mint": mint,
        "judge_mode": judge_mode,
        "force": bool(body.get("force")),
    }
    headers = {"Content-Type": "application/json"}
    if BACKEND_API_KEY:
        headers["Authorization"] = f"Bearer {BACKEND_API_KEY}"
    if JUDGE_TOKEN and judge_mode:
        headers["X-Judge-Token"] = JUDGE_TOKEN

    try:
        resp = requests.post(BACKEND_URL, json=req_payload, headers=headers, timeout=TIMEOUT_SEC)
        if resp.status_code >= 300:
            return jsonify(_fallback_payload(mint, judge_mode)), 200
        return jsonify(resp.json()), 200
    except Exception:
        return jsonify(_fallback_payload(mint, judge_mode)), 200


if __name__ == "__main__":
    host = os.environ.get("CF_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("CF_DEMO_PORT", "7860") or 7860)
    debug = bool(int(os.environ.get("CF_DEMO_DEBUG", "0") or 0))
    APP.run(host=host, port=port, debug=debug)
