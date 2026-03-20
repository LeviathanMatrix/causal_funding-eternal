from __future__ import annotations

import os
import sys
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

if __package__ in (None, ""):
    # Allow running as `python app.py` from demo_shell/
    sys.path.append(str(Path(__file__).resolve().parent))

from console_builder import build_console_from_demo_view, build_console_from_report
from core_utils import safe_json, to_float
from review_store import get_case_review, update_case_review
from simulation_engine import simulate_counterfactual
from template_html import TEMPLATE
from watchlist_store import append_recheck_snapshot, get_watchlist_entry, set_watchlist_tracking

APP = Flask(__name__)

BACKEND_URL = os.environ.get("CF_DEMO_BACKEND_URL", "").strip()
BACKEND_API_KEY = os.environ.get("CF_DEMO_API_KEY", "").strip()
JUDGE_TOKEN = os.environ.get("CF_DEMO_JUDGE_TOKEN", "").strip()
TIMEOUT_SEC = float(os.environ.get("CF_DEMO_TIMEOUT_SEC", "90") or 90)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = ROOT / "examples" / "sample_report_redacted.json"
STATE_DIR = ROOT / "demo_shell" / ".local_state"
REVIEW_STATE_FILE = STATE_DIR / "case_reviews.json"
WATCHLIST_STATE_FILE = STATE_DIR / "watchlist_state.json"
REVIEW_STATE_DIR = STATE_DIR


# Backward-compatible wrappers used by local tests.
def _safe_json(path: Path) -> dict[str, Any]:
    return safe_json(path)


def _get_case_review(mint: str, action: str, risk_score: float) -> dict[str, Any]:
    return get_case_review(mint, action, risk_score, REVIEW_STATE_FILE, REVIEW_STATE_DIR)


def _update_case_review(mint: str, action: str, risk_score: float, fields: dict[str, Any]) -> dict[str, Any]:
    return update_case_review(mint, action, risk_score, fields, REVIEW_STATE_FILE, REVIEW_STATE_DIR)


def _get_watchlist(mint: str) -> dict[str, Any]:
    return get_watchlist_entry(mint, WATCHLIST_STATE_FILE, REVIEW_STATE_DIR)


def _set_watchlist(mint: str, tracked: bool) -> dict[str, Any]:
    return set_watchlist_tracking(mint, tracked, WATCHLIST_STATE_FILE, REVIEW_STATE_DIR)


def _append_recheck(mint: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return append_recheck_snapshot(mint, snapshot, WATCHLIST_STATE_FILE, REVIEW_STATE_DIR)


def _attach_watchlist(console: dict[str, Any]) -> dict[str, Any]:
    meta = console.get("meta") if isinstance(console.get("meta"), dict) else {}
    mint = str(meta.get("mint_raw") or "").strip()
    entry = _get_watchlist(mint) if mint else {
        "tracked": False,
        "last_recheck_at": "",
        "last_action": "",
        "last_risk_score": 0.0,
        "last_confidence_pct": 0.0,
        "history": [],
    }
    console["watchlist"] = {
        "tracked": bool(entry.get("tracked")),
        "last_recheck_at": str(entry.get("last_recheck_at") or ""),
        "last_action": str(entry.get("last_action") or ""),
        "last_risk_score": float(entry.get("last_risk_score") or 0.0),
        "last_confidence_pct": float(entry.get("last_confidence_pct") or 0.0),
        "history": (entry.get("history") if isinstance(entry.get("history"), list) else [])[-10:],
    }
    return console


def _build_console_from_report(
    report: dict[str, Any],
    *,
    mint_hint: str = "",
    judge_mode: bool = False,
    source_label: str = "analysis",
) -> dict[str, Any]:
    console = build_console_from_report(
        report,
        mint_hint=mint_hint,
        judge_mode=judge_mode,
        source_label=source_label,
        get_case_review=_get_case_review,
    )
    return _attach_watchlist(console)


def _build_console_from_demo_view(
    demo_view: dict[str, Any],
    *,
    mint_hint: str = "",
    judge_mode: bool = False,
    source_label: str = "demo_view",
) -> dict[str, Any]:
    console = build_console_from_demo_view(
        demo_view,
        mint_hint=mint_hint,
        judge_mode=judge_mode,
        source_label=source_label,
        get_case_review=_get_case_review,
    )
    return _attach_watchlist(console)


def _build_payload(raw: dict[str, Any], mint: str, judge_mode: bool, *, ok: bool = True, source: str = "analysis") -> dict[str, Any]:
    payload = dict(raw) if isinstance(raw, dict) else {}
    console = payload.get("console_view") if isinstance(payload.get("console_view"), dict) else None
    if console is None:
        if isinstance(payload.get("public_brief"), dict):
            console = _build_console_from_report(payload, mint_hint=mint, judge_mode=judge_mode, source_label=source)
        elif isinstance(payload.get("report"), dict) and isinstance(payload.get("report", {}).get("public_brief"), dict):
            console = _build_console_from_report(payload.get("report") or {}, mint_hint=mint, judge_mode=judge_mode, source_label=source)
        elif isinstance(payload.get("demo_view"), dict):
            console = _build_console_from_demo_view(payload.get("demo_view") or {}, mint_hint=mint, judge_mode=judge_mode, source_label=source)
        else:
            console = _build_console_from_report(_safe_json(SAMPLE_FILE), mint_hint=mint, judge_mode=judge_mode, source_label="sample_fallback")
    else:
        console = _attach_watchlist(console)
    payload["ok"] = bool(ok)
    payload["source"] = source
    payload["console_view"] = console
    return payload


def _fallback_payload(mint: str, judge_mode: bool, ok: bool = True) -> dict[str, Any]:
    sample = _safe_json(SAMPLE_FILE)
    return _build_payload(sample, mint, judge_mode, ok=ok, source="sample_fallback")


def _fetch_backend_payload(mint: str, judge_mode: bool, force: bool) -> tuple[dict[str, Any], int]:
    req_payload = {"mint": mint, "judge_mode": judge_mode, "force": force}
    headers = {"Content-Type": "application/json"}
    if BACKEND_API_KEY:
        headers["Authorization"] = f"Bearer {BACKEND_API_KEY}"
    if JUDGE_TOKEN and judge_mode:
        headers["X-Judge-Token"] = JUDGE_TOKEN

    if not BACKEND_URL:
        fallback = _fallback_payload(mint, judge_mode, ok=False)
        fallback["error"] = "backend_unreachable"
        return fallback, 503

    try:
        resp = requests.post(BACKEND_URL, json=req_payload, headers=headers, timeout=TIMEOUT_SEC)
        if resp.status_code >= 300:
            fallback = _fallback_payload(mint, judge_mode, ok=False)
            fallback["error"] = f"backend_http_{resp.status_code}"
            fallback["upstream_status"] = resp.status_code
            return fallback, 502
        upstream = resp.json()
        if not isinstance(upstream, dict):
            fallback = _fallback_payload(mint, judge_mode, ok=False)
            fallback["error"] = "backend_invalid_payload"
            return fallback, 502
        return _build_payload(upstream, mint, judge_mode, ok=True, source="backend"), 200
    except Exception:
        fallback = _fallback_payload(mint, judge_mode, ok=False)
        fallback["error"] = "backend_unreachable"
        return fallback, 503


def _render_view(payload: dict[str, Any], *, input_mint: str = "", judge_mode: bool = False) -> str:
    console = payload.get("console_view") if isinstance(payload.get("console_view"), dict) else _fallback_payload(input_mint, judge_mode).get("console_view")
    return render_template_string(
        TEMPLATE,
        console=console,
        input_mint=input_mint,
        judge_mode=judge_mode,
        backend_error=str(payload.get("error") or ""),
        surface_order=["funding", "control", "permission", "issuer"],
        status_options=["NEW", "UNDER_REVIEW", "BLOCKED", "CLEARED", "NEED_MORE_EVIDENCE"],
        priority_options=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )


@APP.get("/")
def index() -> str:
    payload = _fallback_payload("", False)
    return _render_view(payload, input_mint="", judge_mode=False)


@APP.post("/analyze")
def analyze_form() -> Any:
    mint = str(request.form.get("mint") or "").strip()
    mode = str(request.form.get("mode") or "public").strip().lower()
    judge_mode = mode == "judge"
    if not mint:
        payload = _fallback_payload("", judge_mode, ok=False)
        payload["error"] = "missing_mint"
        return _render_view(payload, input_mint="", judge_mode=judge_mode), 400

    payload, _ = _fetch_backend_payload(mint, judge_mode, force=False)
    return _render_view(payload, input_mint=mint, judge_mode=judge_mode)


@APP.post("/api/analyze")
def analyze_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    judge_mode = bool(body.get("judge_mode"))
    if not mint:
        return jsonify({"ok": False, "error": "missing_mint"}), 400

    payload, status = _fetch_backend_payload(mint, judge_mode, force=bool(body.get("force")))
    return jsonify(payload), status


@APP.post("/api/simulate")
def simulate_api() -> Any:
    body = request.get_json(silent=True) or {}
    console = body.get("console") if isinstance(body.get("console"), dict) else {}
    selected = body.get("selected_toggle_ids") if isinstance(body.get("selected_toggle_ids"), list) else []
    if not console:
        return jsonify({"ok": False, "error": "missing_console_payload"}), 400
    result = simulate_counterfactual(console, [str(x) for x in selected])
    return jsonify({"ok": True, "simulation": result}), 200


@APP.post("/api/review")
def review_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    if not mint:
        return jsonify({"ok": False, "error": "missing_mint"}), 400

    status = str(body.get("status") or "NEW").strip().upper()
    priority = str(body.get("priority") or "MEDIUM").strip().upper()
    reviewer = str(body.get("reviewer") or "").strip()
    note = str(body.get("note") or "").strip()
    action = str(body.get("action") or "REVIEW").strip().upper() or "REVIEW"
    risk_score = to_float(body.get("risk_score"), 50.0)

    case_review = _update_case_review(
        mint,
        action,
        risk_score,
        {"status": status, "priority": priority, "reviewer": reviewer, "note": note},
    )
    return jsonify({"ok": True, "case_review": case_review}), 200


@APP.post("/api/watchlist")
def watchlist_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    if not mint:
        return jsonify({"ok": False, "error": "missing_mint"}), 400
    tracked = bool(body.get("tracked"))
    entry = _set_watchlist(mint, tracked)
    return jsonify({"ok": True, "watchlist": entry}), 200


@APP.post("/api/recheck")
def recheck_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    if not mint:
        return jsonify({"ok": False, "error": "missing_mint"}), 400

    judge_mode = bool(body.get("judge_mode"))
    refresh = bool(body.get("refresh", True))
    refreshed_payload = None
    refresh_status = 0
    snapshot = {}
    if refresh:
        refreshed_payload, refresh_status = _fetch_backend_payload(mint, judge_mode, force=True)
        console = refreshed_payload.get("console_view") if isinstance(refreshed_payload.get("console_view"), dict) else {}
        executive = console.get("executive_decision") if isinstance(console.get("executive_decision"), dict) else {}
        if executive:
            snapshot = {
                "action": str(executive.get("action") or "REVIEW"),
                "risk_score": to_float(executive.get("risk_score"), 0.0),
                "confidence_pct": to_float(executive.get("confidence_pct"), 0.0),
                "summary": str(executive.get("summary") or "recheck_refresh"),
            }
    if not snapshot:
        snapshot = {
            "action": str(body.get("action") or "REVIEW"),
            "risk_score": to_float(body.get("risk_score"), 0.0),
            "confidence_pct": to_float(body.get("confidence_pct"), 0.0),
            "summary": str(body.get("summary") or "manual_recheck"),
        }
    entry = _append_recheck(mint, snapshot)
    out = {"ok": True, "watchlist": entry, "refresh_status": refresh_status}
    if isinstance(refreshed_payload, dict):
        out["refresh_source"] = str(refreshed_payload.get("source") or "")
        out["console_view"] = refreshed_payload.get("console_view") if isinstance(refreshed_payload.get("console_view"), dict) else {}
    return jsonify(out), 200


@APP.post("/api/export-case")
def export_case_api() -> Any:
    body = request.get_json(silent=True) or {}
    console = body.get("console") if isinstance(body.get("console"), dict) else {}
    if not console:
        return jsonify({"ok": False, "error": "missing_console_payload"}), 400
    meta = console.get("meta") if isinstance(console.get("meta"), dict) else {}
    executive = console.get("executive_decision") if isinstance(console.get("executive_decision"), dict) else {}
    export = {
        "mint": str(meta.get("mint_raw") or ""),
        "symbol": str(meta.get("symbol") or ""),
        "action": str(executive.get("action") or ""),
        "risk_score": float(executive.get("risk_score") or 0.0),
        "confidence_pct": float(executive.get("confidence_pct") or 0.0),
        "decision_memo": str(executive.get("decision_memo") or ""),
        "hard_evidence_brief": console.get("hard_evidence_brief") if isinstance(console.get("hard_evidence_brief"), dict) else {},
        "decision_trace": console.get("decision_trace") if isinstance(console.get("decision_trace"), dict) else {},
        "case_review": console.get("case_review") if isinstance(console.get("case_review"), dict) else {},
        "watchlist": console.get("watchlist") if isinstance(console.get("watchlist"), dict) else {},
    }
    return jsonify({"ok": True, "export": export}), 200


if __name__ == "__main__":
    host = os.environ.get("CF_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("CF_DEMO_PORT", "7860") or 7860)
    debug = bool(int(os.environ.get("CF_DEMO_DEBUG", "0") or 0))
    APP.run(host=host, port=port, debug=debug)
