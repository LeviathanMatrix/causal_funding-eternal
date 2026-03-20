from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json


def safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def redact_addr(addr: str, keep: int = 4) -> str:
    value = str(addr or "").strip()
    if not value:
        return "N/A"
    if len(value) <= keep * 2:
        return value
    return f"{value[:keep]}****{value[-keep:]}"


def severity(score: float) -> str:
    if score >= 65.0:
        return "high"
    if score >= 35.0:
        return "medium"
    return "low"


def mean(values: list[float]) -> float:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return 0.0
    return sum(clean) / float(len(clean))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def case_id_for_mint(mint: str) -> str:
    digest = hashlib.sha1(str(mint or "").encode("utf-8")).hexdigest()[:10]
    return f"CF-{digest.upper()}"


def default_priority(action: str, risk_score: float) -> str:
    if action == "BLOCK" or risk_score >= 75.0:
        return "HIGH"
    if action == "REVIEW" or risk_score >= 45.0:
        return "MEDIUM"
    return "LOW"


def surface_metrics(rows: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"label": k, "value": v} for k, v in rows[:4]]
