from __future__ import annotations

from typing import Any

from core_utils import clamp


def action_from_policy(policy: dict[str, Any], score: float, confidence_pct: float) -> str:
    block_threshold = float(policy.get("block_threshold") or 70.0)
    review_threshold = float(policy.get("review_threshold") or 45.0)
    min_conf = float(policy.get("min_confidence_for_block") or 0.55)
    conf = float(confidence_pct or 0.0) / 100.0
    if score >= block_threshold and conf >= min_conf:
        return "BLOCK"
    if score >= review_threshold:
        return "REVIEW"
    return "ALLOW"


def simulate_counterfactual(console: dict[str, Any], selected_ids: list[str]) -> dict[str, Any]:
    what_if = console.get("what_if") if isinstance(console.get("what_if"), dict) else {}
    base_surfaces = what_if.get("base_surfaces") if isinstance(what_if.get("base_surfaces"), dict) else {}
    toggles = what_if.get("toggles") if isinstance(what_if.get("toggles"), list) else []
    policy = what_if.get("policy") if isinstance(what_if.get("policy"), dict) else {}

    selected = [row for row in toggles if isinstance(row, dict) and str(row.get("id") or "") in set(selected_ids)]

    reductions = {"funding": 0.0, "control": 0.0, "permission": 0.0, "issuer": 0.0}
    confidence_shift = 0.0
    rationale: list[str] = []

    for row in selected:
        red = row.get("reductions") if isinstance(row.get("reductions"), dict) else {}
        for key in reductions:
            reductions[key] += float(red.get(key) or 0.0)
        confidence_shift += float(row.get("confidence_delta_pct") or 0.0)
        if str(row.get("rationale") or "").strip():
            rationale.append(str(row.get("rationale") or ""))

    next_surfaces: dict[str, float] = {}
    for key in reductions:
        base = base_surfaces.get(key) if isinstance(base_surfaces.get(key), dict) else {}
        score = float(base.get("score") or 0.0)
        floor = float(base.get("floor") or 0.0)
        next_surfaces[key] = clamp(score - reductions[key], floor, 100.0)

    current_agg = float(what_if.get("aggregate_score") or 1.0)
    next_agg = sum(float(v) for v in next_surfaces.values())
    scale = (next_agg / current_agg) if current_agg > 0 else 1.0

    base_decision = console.get("executive_decision") if isinstance(console.get("executive_decision"), dict) else {}
    base_risk = float(base_decision.get("risk_score") or 0.0)
    base_conf = float(base_decision.get("confidence_pct") or 0.0)

    sim_risk = clamp(base_risk * scale, 0.0, 100.0)
    sim_conf = clamp(base_conf + confidence_shift, 5.0, 99.0)
    sim_action = action_from_policy(policy, sim_risk, sim_conf)

    return {
        "selected_count": len(selected),
        "risk": round(sim_risk, 3),
        "risk_delta": round(sim_risk - base_risk, 3),
        "confidence_pct": round(sim_conf, 3),
        "confidence_delta_pct": round(sim_conf - base_conf, 3),
        "action": sim_action,
        "surfaces": {k: round(v, 3) for k, v in next_surfaces.items()},
        "rationale": rationale,
    }
