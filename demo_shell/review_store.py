from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from core_utils import case_id_for_mint, default_priority, utc_now


def ensure_review_store(review_state_dir: Path) -> None:
    review_state_dir.mkdir(parents=True, exist_ok=True)


def load_review_store(review_state_file: Path, review_state_dir: Path) -> dict[str, Any]:
    ensure_review_store(review_state_dir)
    if not review_state_file.exists():
        return {}
    try:
        payload = json.loads(review_state_file.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def save_review_store(payload: dict[str, Any], review_state_file: Path, review_state_dir: Path) -> None:
    ensure_review_store(review_state_dir)
    review_state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_case_review(
    mint: str,
    action: str,
    risk_score: float,
    review_state_file: Path,
    review_state_dir: Path,
) -> dict[str, Any]:
    store = load_review_store(review_state_file, review_state_dir)
    key = str(mint or "").strip()
    current = store.get(key) if isinstance(store.get(key), dict) else {}
    if current:
        return current
    now = utc_now()
    return {
        "case_id": case_id_for_mint(key),
        "status": "NEW",
        "priority": default_priority(action, risk_score),
        "reviewer": "",
        "note": "",
        "updated_at": now,
        "audit": [
            {
                "timestamp": now,
                "status": "NEW",
                "priority": default_priority(action, risk_score),
                "reviewer": "system",
                "note": "Case initialized from current analysis output.",
            }
        ],
    }


def update_case_review(
    mint: str,
    action: str,
    risk_score: float,
    fields: dict[str, Any],
    review_state_file: Path,
    review_state_dir: Path,
) -> dict[str, Any]:
    key = str(mint or "").strip()
    store = load_review_store(review_state_file, review_state_dir)
    current = get_case_review(key, action, risk_score, review_state_file, review_state_dir)
    current["status"] = str(fields.get("status") or current.get("status") or "NEW").strip().upper()
    current["priority"] = str(
        fields.get("priority") or current.get("priority") or default_priority(action, risk_score)
    ).strip().upper()
    current["reviewer"] = str(fields.get("reviewer") or current.get("reviewer") or "").strip()
    current["note"] = str(fields.get("note") or current.get("note") or "").strip()
    current["updated_at"] = utc_now()
    audit = current.get("audit") if isinstance(current.get("audit"), list) else []
    audit.append(
        {
            "timestamp": current["updated_at"],
            "status": current["status"],
            "priority": current["priority"],
            "reviewer": current["reviewer"] or "unassigned",
            "note": current["note"] or "No note recorded.",
        }
    )
    current["audit"] = audit[-25:]
    store[key] = current
    save_review_store(store, review_state_file, review_state_dir)
    return current
