from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from core_utils import utc_now


def ensure_watchlist_store(watchlist_dir: Path) -> None:
    watchlist_dir.mkdir(parents=True, exist_ok=True)


def load_watchlist_store(watchlist_file: Path, watchlist_dir: Path) -> dict[str, Any]:
    ensure_watchlist_store(watchlist_dir)
    if not watchlist_file.exists():
        return {"entries": {}}
    try:
        payload = json.loads(watchlist_file.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {"entries": {}}
    except Exception:
        return {"entries": {}}


def save_watchlist_store(payload: dict[str, Any], watchlist_file: Path, watchlist_dir: Path) -> None:
    ensure_watchlist_store(watchlist_dir)
    watchlist_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_watchlist_entry(mint: str, watchlist_file: Path, watchlist_dir: Path) -> dict[str, Any]:
    key = str(mint or "").strip()
    store = load_watchlist_store(watchlist_file, watchlist_dir)
    entries = store.get("entries") if isinstance(store.get("entries"), dict) else {}
    current = entries.get(key) if isinstance(entries.get(key), dict) else {}
    if current:
        return current
    return {
        "tracked": False,
        "last_recheck_at": "",
        "last_action": "",
        "last_risk_score": 0.0,
        "history": [],
    }


def set_watchlist_tracking(mint: str, tracked: bool, watchlist_file: Path, watchlist_dir: Path) -> dict[str, Any]:
    key = str(mint or "").strip()
    store = load_watchlist_store(watchlist_file, watchlist_dir)
    entries = store.get("entries") if isinstance(store.get("entries"), dict) else {}
    current = entries.get(key) if isinstance(entries.get(key), dict) else {}
    if not current:
        current = get_watchlist_entry(key, watchlist_file, watchlist_dir)
    current["tracked"] = bool(tracked)
    current["updated_at"] = utc_now()
    entries[key] = current
    store["entries"] = entries
    save_watchlist_store(store, watchlist_file, watchlist_dir)
    return current


def append_recheck_snapshot(
    mint: str,
    snapshot: dict[str, Any],
    watchlist_file: Path,
    watchlist_dir: Path,
) -> dict[str, Any]:
    key = str(mint or "").strip()
    store = load_watchlist_store(watchlist_file, watchlist_dir)
    entries = store.get("entries") if isinstance(store.get("entries"), dict) else {}
    current = entries.get(key) if isinstance(entries.get(key), dict) else {}
    if not current:
        current = get_watchlist_entry(key, watchlist_file, watchlist_dir)
    history = current.get("history") if isinstance(current.get("history"), list) else []
    row = {
        "timestamp": utc_now(),
        "action": str(snapshot.get("action") or ""),
        "risk_score": float(snapshot.get("risk_score") or 0.0),
        "confidence_pct": float(snapshot.get("confidence_pct") or 0.0),
        "summary": str(snapshot.get("summary") or ""),
    }
    history.append(row)
    current["history"] = history[-30:]
    current["last_recheck_at"] = row["timestamp"]
    current["last_action"] = row["action"]
    current["last_risk_score"] = row["risk_score"]
    current["last_confidence_pct"] = row["confidence_pct"]
    current["updated_at"] = row["timestamp"]
    entries[key] = current
    store["entries"] = entries
    save_watchlist_store(store, watchlist_file, watchlist_dir)
    return current
