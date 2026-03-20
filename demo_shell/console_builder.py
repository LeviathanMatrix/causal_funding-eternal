from __future__ import annotations

from typing import Any, Callable

from core_utils import clamp, mean, redact_addr, severity, surface_metrics, to_float, to_int

ReviewGetter = Callable[[str, str, float], dict[str, Any]]


def policy_from_report(report: dict[str, Any], action: str) -> dict[str, float]:
    decision = report.get("decision_policy") if isinstance(report.get("decision_policy"), dict) else {}
    thresholds = decision.get("thresholds") if isinstance(decision.get("thresholds"), dict) else {}
    if thresholds:
        return {
            "block_threshold": to_float(thresholds.get("block_threshold"), 70.0),
            "review_threshold": to_float(thresholds.get("review_threshold"), 45.0),
            "min_confidence_for_block": to_float(thresholds.get("min_confidence_for_block"), 0.55),
        }
    return {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55}


def _confidence_penalty(base: float, coverage: float) -> float:
    # Lower coverage means less confidence in hypothetical projection.
    normalized = clamp(coverage, 0.0, 1.0)
    return round(-(base * (1.0 - normalized)), 3)


def _build_hard_evidence_brief(
    funding_chain: dict[str, Any],
    control: dict[str, Any],
    cross_token: dict[str, Any],
    issuer_surface: dict[str, Any],
    attribution: dict[str, Any],
) -> dict[str, Any]:
    path_count = to_int(funding_chain.get("funding_path_count"), 0)
    total_flow = to_float(funding_chain.get("total_traced_flow_sol"), 0.0)
    top_share = to_float((funding_chain.get("top_source") or {}).get("share_pct"), 0.0)
    shared_tokens = to_int(cross_token.get("shared_token_count"), 0)
    shared_wallets = to_int(cross_token.get("max_shared_wallets_per_token"), 0)
    ctrl_conf = to_float(control.get("controller_confidence_pct"), 0.0)
    issuer_risk = to_float(issuer_surface.get("risk_score"), 0.0)
    signals = attribution.get("public_signals") if isinstance(attribution.get("public_signals"), list) else []

    bullets = [
        f"{path_count} traced funding paths with {total_flow:.2f} SOL visible flow.",
        f"Top source concentration currently at {top_share:.1f}%.",
        f"Controller confidence at {ctrl_conf:.1f}% in current snapshot.",
        f"Cross-token reuse context: shared_tokens={shared_tokens}, max_shared_wallets={shared_wallets}.",
        f"Issuer legitimacy risk surface currently at {issuer_risk:.1f}/100.",
    ]

    strongest = signals[:3] if signals else ["No high-intensity public signal in current case."]

    return {
        "evidence_count": path_count,
        "strongest_signals": strongest,
        "cross_token_reuse_summary": f"shared_tokens={shared_tokens}, max_shared_wallets={shared_wallets}",
        "control_highlights": [
            f"primary_controller={str(control.get('primary_controller') or 'N/A')}",
            f"controller_confidence_pct={ctrl_conf:.1f}",
            f"dossier_wallet_count={to_int((control.get('controller_dossier') or {}).get('wallet_count'), 0)}",
        ],
        "issuer_highlights": [
            f"issuer_count={to_int(issuer_surface.get('issuer_count'), 0)}",
            f"related_asset_count={to_int(issuer_surface.get('related_asset_count'), 0)}",
            f"historical_asset_count={to_int(issuer_surface.get('historical_asset_count'), 0)}",
        ],
        "bullets": bullets,
    }


def _build_decision_trace(
    executive: dict[str, Any],
    surfaces: dict[str, Any],
    hard_evidence_brief: dict[str, Any],
    toggles: list[dict[str, Any]],
    risk: dict[str, Any],
    policy_reason: str,
) -> dict[str, Any]:
    ranked = sorted(
        [
            {"name": key, "score": to_float((row or {}).get("score"), 0.0)}
            for key, row in surfaces.items()
            if isinstance(row, dict)
        ],
        key=lambda x: x["score"],
        reverse=True,
    )
    top = ranked[:2]
    drove = [f"{row['name']} surface score={row['score']:.1f}" for row in top]
    drove.extend([f"policy_reason={policy_reason}"])

    confidence_drivers = [
        f"base_confidence={to_float(risk.get('confidence'), 0.0)*100.0:.1f}%",
        f"evidence_count={to_int(hard_evidence_brief.get('evidence_count'), 0)}",
        f"strong_signals={len(hard_evidence_brief.get('strongest_signals') or [])}",
    ]

    uncertainty = []
    if to_float(executive.get("confidence_pct"), 0.0) < 65.0:
        uncertainty.append("Confidence remains below high-assurance threshold.")
    if to_int(hard_evidence_brief.get("evidence_count"), 0) <= 2:
        uncertainty.append("Limited path evidence density in current snapshot.")
    if not uncertainty:
        uncertainty.append("No dominant uncertainty warning in current public snapshot.")

    change_conditions = [str(row.get("label") or "") for row in toggles if row.get("available")][:5]

    return {
        "what_drove_verdict": drove,
        "what_raised_confidence": confidence_drivers,
        "remaining_uncertainty": uncertainty,
        "what_would_change_decision": change_conditions,
    }


def build_console_from_report(
    report: dict[str, Any],
    *,
    mint_hint: str = "",
    judge_mode: bool = False,
    source_label: str = "analysis",
    get_case_review: ReviewGetter,
) -> dict[str, Any]:
    public_brief = report.get("public_brief") if isinstance(report.get("public_brief"), dict) else {}
    if not public_brief:
        return build_console_from_demo_view(
            {},
            mint_hint=mint_hint,
            judge_mode=judge_mode,
            source_label=source_label,
            get_case_review=get_case_review,
        )

    meta = report.get("meta") if isinstance(report.get("meta"), dict) else {}
    risk = report.get("risk") if isinstance(report.get("risk"), dict) else {}
    judgement = report.get("judgement") if isinstance(report.get("judgement"), dict) else {}
    decision = report.get("decision_policy") if isinstance(report.get("decision_policy"), dict) else {}
    token_profile = public_brief.get("token_profile") if isinstance(public_brief.get("token_profile"), dict) else {}
    risk_overview = public_brief.get("risk_overview") if isinstance(public_brief.get("risk_overview"), dict) else {}
    funding_chain = public_brief.get("funding_chain") if isinstance(public_brief.get("funding_chain"), dict) else {}
    control = public_brief.get("control_and_permissions") if isinstance(public_brief.get("control_and_permissions"), dict) else {}
    cross_token = public_brief.get("cross_token_intel") if isinstance(public_brief.get("cross_token_intel"), dict) else {}
    attribution = public_brief.get("attribution") if isinstance(public_brief.get("attribution"), dict) else {}

    dims = risk_overview.get("dimension_scores") if isinstance(risk_overview.get("dimension_scores"), dict) else {}
    permission_surface = control.get("token_permissions") if isinstance(control.get("token_permissions"), dict) else {}
    issuer_surface = control.get("metadata_legitimacy") if isinstance(control.get("metadata_legitimacy"), dict) else {}
    controller_dossier = control.get("controller_dossier") if isinstance(control.get("controller_dossier"), dict) else {}
    issuer_pattern = control.get("issuer_pattern_summary") if isinstance(control.get("issuer_pattern_summary"), dict) else {}

    funding_score = mean([to_float(dims.get("R2_funding"), 0.0), to_float(dims.get("R3_convergence"), 0.0)])
    hidden_control = attribution.get("risk_surfaces", {}).get("hidden_control", {}) if isinstance(attribution.get("risk_surfaces"), dict) else {}
    recurrence = attribution.get("risk_surfaces", {}).get("recurrence_risk", {}) if isinstance(attribution.get("risk_surfaces"), dict) else {}
    control_score = mean([to_float(dims.get("R1_control"), 0.0), to_float(hidden_control.get("score"), 0.0)])
    permission_score = to_float(permission_surface.get("score"), 0.0)
    issuer_score = mean([to_float(issuer_surface.get("risk_score"), 0.0), to_float(recurrence.get("score"), 0.0) * 0.35])

    top_source = funding_chain.get("top_source") if isinstance(funding_chain.get("top_source"), dict) else {}
    top_source_share = to_float(top_source.get("share_pct"), 0.0)
    controller_conf = to_float(control.get("controller_confidence_pct"), 0.0)
    primary_controller = str(control.get("primary_controller") or "")

    current_action = str(decision.get("action") or "REVIEW").upper()
    action_reason = str(decision.get("reason") or "policy_decision")
    risk_score = to_float(risk.get("score"), 0.0)
    confidence = to_float(risk.get("confidence"), 0.0)
    confidence_pct = round(confidence * 100.0, 2)

    repeat_tokens = to_int(cross_token.get("shared_token_count"), 0)
    related_asset_count = to_int(issuer_surface.get("related_asset_count"), 0)
    historical_asset_count = to_int(issuer_surface.get("historical_asset_count"), 0)

    surfaces = {
        "funding": {
            "title": "Funding Surface",
            "score": round(funding_score, 2),
            "severity": severity(funding_score),
            "summary": "How concentrated and path-dependent the traced funding footprint looks right now.",
            "metrics": surface_metrics([
                ("Paths", str(to_int(funding_chain.get("funding_path_count"), 0))),
                ("Total flow", f"{to_float(funding_chain.get('total_traced_flow_sol'), 0.0):.2f} SOL"),
                ("Top share", f"{top_source_share:.1f}%"),
                ("Cycle paths", str(to_int(funding_chain.get("cycle_path_count"), 0))),
            ]),
            "bullets": [
                f"{to_int(funding_chain.get('funding_path_count'), 0)} traced paths across the current funding snapshot.",
                f"The dominant traced source accounts for {top_source_share:.1f}% of visible flow.",
                f"Maximum single traced path is {to_float(funding_chain.get('max_path_flow_sol'), 0.0):.2f} SOL.",
            ],
            "evidence_brief": [
                f"Top source address is masked in public mode and remains available only as a concentration indicator: {redact_addr(str(top_source.get('address') or ''), 4) if not judge_mode else str(top_source.get('address') or 'N/A')}.",
                "Funding chain summary tracks total flow and path concentration instead of exposing raw path internals.",
                f"Public signal set includes: {', '.join((attribution.get('public_signals') or [])[:2]) or 'No high-intensity anomaly observed'}.",
            ],
        },
        "control": {
            "title": "Control Surface",
            "score": round(control_score, 2),
            "severity": severity(control_score),
            "summary": "Who appears to control the token surface and how strong the operator-level signals are.",
            "metrics": surface_metrics([
                ("Controller", redact_addr(primary_controller, 4) if not judge_mode else (primary_controller or "N/A")),
                ("Confidence", f"{controller_conf:.1f}%"),
                ("Dossier wallets", str(to_int(controller_dossier.get("wallet_count"), 0))),
                ("Service-funded", str(to_int(controller_dossier.get("service_funded_wallet_count"), 0))),
            ]),
            "bullets": [
                f"Primary controller candidate identified with {controller_conf:.1f}% confidence.",
                f"Wallet dossier coverage spans {to_int(controller_dossier.get('wallet_count'), 0)} control-linked wallets.",
                f"Cross-token reuse signal currently touches {repeat_tokens} related token context(s).",
            ],
            "evidence_brief": [
                f"Primary identity label: {str(controller_dossier.get('primary_identity_name') or controller_dossier.get('primary_identity_type') or 'unknown')}.",
                f"Origin funding label: {str(controller_dossier.get('primary_funder_label') or controller_dossier.get('primary_funder') or 'unknown')}.",
                "Execution and hidden-control pressure remain summarized through the control surface.",
            ],
        },
        "permission": {
            "title": "Permission Surface",
            "score": round(permission_score, 2),
            "severity": severity(permission_score),
            "summary": "Token-level control posture, authority exposure, and extension-driven risk complexity.",
            "metrics": surface_metrics([
                ("Program", str(permission_surface.get("program_label") or "unknown")),
                ("Score", f"{permission_score:.1f}"),
                ("High signals", str(len(permission_surface.get("high_risk_signals") or []))),
                ("Extensions", str(len(permission_surface.get("extension_labels") or []))),
            ]),
            "bullets": [
                f"Current token program posture: {str(permission_surface.get('program_label') or 'unknown')}.",
                f"High-risk extension signals observed: {', '.join(permission_surface.get('high_risk_signals') or []) or 'none'}.",
                f"Extensions visible in public summary: {', '.join(permission_surface.get('extension_labels') or []) or 'none'}.",
            ],
            "evidence_brief": [
                f"Permission summary line: {str(permission_surface.get('summary') or 'not available')}.",
                f"Default account state: {str(permission_surface.get('default_account_state') or 'none') or 'none'}.",
                "Public mode exposes posture and extension labels, not parsing internals.",
            ],
        },
        "issuer": {
            "title": "Issuer Surface",
            "score": round(issuer_score, 2),
            "severity": severity(issuer_score),
            "summary": "How complete metadata and issuer footprint look, including related-asset context.",
            "metrics": surface_metrics([
                ("Issuer count", str(to_int(issuer_surface.get("issuer_count"), 0))),
                ("Related assets", str(related_asset_count)),
                ("Historical assets", str(historical_asset_count)),
                ("Reused symbols", str(to_int(issuer_surface.get("reused_symbol_count"), 0))),
            ]),
            "bullets": [
                f"Metadata legitimacy score is {to_float(issuer_surface.get('risk_score'), 0.0):.1f}/100.",
                f"Issuer footprint spans {historical_asset_count} historical references and {related_asset_count} related asset previews.",
                f"Issuer pattern summary flags {to_int(issuer_pattern.get('reused_symbol_count'), 0)} reused symbol pattern(s).",
            ],
            "evidence_brief": [
                f"Metadata reasons: {', '.join((issuer_surface.get('reasons') or [])[:2]) or 'no elevated metadata anomalies disclosed'}.",
                "Issuer context is summarized for diligence use without exposing private enrichment internals.",
            ],
        },
    }

    policy = policy_from_report(report, current_action)
    base_surfaces = {
        "funding": {"score": surfaces["funding"]["score"], "floor": max(5.0, surfaces["funding"]["score"] * 0.20)},
        "control": {"score": surfaces["control"]["score"], "floor": max(5.0, surfaces["control"]["score"] * 0.20)},
        "permission": {"score": surfaces["permission"]["score"], "floor": max(0.0, surfaces["permission"]["score"] * 0.15)},
        "issuer": {"score": surfaces["issuer"]["score"], "floor": max(0.0, surfaces["issuer"]["score"] * 0.15)},
    }

    # Exposure terms are derived from current report signals, not arbitrary constants.
    funding_exposure = clamp((top_source_share - 55.0) / 45.0, 0.0, 1.0)
    mint_authority_open = str((control.get("mint_authority") or {}).get("state") or "").strip().lower() == "open"
    update_authority_open = "update_authority=open" in str(permission_surface.get("summary") or "")
    reuse_exposure = clamp((repeat_tokens * 0.18) + (to_int(cross_token.get("max_shared_wallets_per_token"), 0) * 0.12), 0.0, 1.0)
    issuer_exposure = clamp((historical_asset_count * 0.08) + (related_asset_count * 0.15) + (to_int(issuer_surface.get("reused_symbol_count"), 0) * 0.12), 0.0, 1.0)

    toggles = [
        {
            "id": "funding_normalized",
            "label": "Normalize dominant funding concentration",
            "description": "Assume the dominant funding concentration is no longer present at current intensity.",
            "available": top_source_share >= 60.0,
            "reductions": {
                "funding": round(min(18.0, surfaces["funding"]["score"] * (0.20 + (0.18 * funding_exposure))), 2),
                "control": 0.0,
                "permission": 0.0,
                "issuer": 0.0,
            },
            "confidence_delta_pct": _confidence_penalty(3.8, clamp(funding_chain.get("funding_path_count", 0) / 8.0, 0.2, 1.0)),
            "effect_summary": "funding surface",
            "rationale": f"Projected risk softens because dominant source concentration ({top_source_share:.1f}% of traced flow) is reduced.",
        },
        {
            "id": "mint_authority_revoked",
            "label": "Revoke mint authority exposure",
            "description": "Model the case as if active mint authority control is removed.",
            "available": mint_authority_open,
            "reductions": {
                "funding": 0.0,
                "control": round(min(8.0, surfaces["control"]["score"] * 0.12), 2),
                "permission": round(min(16.0, max(6.0, surfaces["permission"]["score"] * 0.28)), 2),
                "issuer": 0.0,
            },
            "confidence_delta_pct": _confidence_penalty(2.6, clamp(controller_conf / 100.0, 0.25, 1.0)),
            "effect_summary": "control + permission surfaces",
            "rationale": "Projected risk softens because mint-side control exposure is removed from current token posture.",
        },
        {
            "id": "update_authority_revoked",
            "label": "Revoke update authority exposure",
            "description": "Model the case as if update authority is no longer active.",
            "available": update_authority_open,
            "reductions": {
                "funding": 0.0,
                "control": 0.0,
                "permission": round(min(12.0, max(4.0, surfaces["permission"]["score"] * 0.22)), 2),
                "issuer": 0.0,
            },
            "confidence_delta_pct": _confidence_penalty(2.2, clamp(len(permission_surface.get("high_risk_signals") or []) / 3.0, 0.2, 1.0)),
            "effect_summary": "permission surface",
            "rationale": "Projected risk softens because token-level update control is tightened.",
        },
        {
            "id": "reuse_signal_absent",
            "label": "Remove cross-token reuse pressure",
            "description": "Model the case as if current cross-token reuse context is absent.",
            "available": repeat_tokens > 0,
            "reductions": {
                "funding": 0.0,
                "control": round(min(14.0, surfaces["control"]["score"] * (0.15 + 0.10 * reuse_exposure)), 2),
                "permission": 0.0,
                "issuer": round(min(8.0, surfaces["issuer"]["score"] * (0.10 + 0.12 * reuse_exposure)), 2),
            },
            "confidence_delta_pct": _confidence_penalty(3.4, clamp(repeat_tokens / 4.0, 0.2, 1.0)),
            "effect_summary": "control + issuer surfaces",
            "rationale": f"Projected risk softens because cross-token reuse context ({repeat_tokens} related token signals) is removed.",
        },
        {
            "id": "issuer_footprint_cleaner",
            "label": "Clean issuer footprint",
            "description": "Model the case as if issuer metadata and related-asset footprint are cleaner.",
            "available": historical_asset_count > 0 or related_asset_count > 0 or to_float(issuer_surface.get("risk_score"), 0.0) > 0.0,
            "reductions": {
                "funding": 0.0,
                "control": 0.0,
                "permission": 0.0,
                "issuer": round(min(18.0, surfaces["issuer"]["score"] * (0.28 + 0.18 * issuer_exposure)), 2),
            },
            "confidence_delta_pct": _confidence_penalty(3.0, clamp((historical_asset_count + related_asset_count) / 8.0, 0.2, 1.0)),
            "effect_summary": "issuer surface",
            "rationale": "Projected risk softens because issuer-side metadata and related-asset footprint become cleaner.",
        },
    ]

    aggregate_score = sum(row["score"] for row in base_surfaces.values())
    mint = str(report.get("mint") or mint_hint or token_profile.get("mint") or "")
    case_review = get_case_review(mint, current_action, risk_score)

    executive = {
        "headline": str(public_brief.get("headline") or "Decision Snapshot"),
        "action": current_action,
        "risk_score": round(risk_score, 2),
        "confidence_pct": confidence_pct,
        "confidence_label": str(risk.get("confidence_label") or risk_overview.get("verdict_level") or ""),
        "verdict_label": str(public_brief.get("verdict") or judgement.get("verdict_level") or current_action),
        "summary": str(public_brief.get("summary") or judgement.get("risk_conclusion") or "Decision-ready risk summary generated."),
        "decision_memo": str(judgement.get("risk_conclusion") or action_reason).strip(),
        "action_reason": action_reason,
        "top_flags": (attribution.get("public_signals") if isinstance(attribution.get("public_signals"), list) else [])[:4] or ["No high-intensity anomaly observed"],
    }

    hard_evidence_brief = _build_hard_evidence_brief(funding_chain, control, cross_token, issuer_surface, attribution)
    decision_trace = _build_decision_trace(executive, surfaces, hard_evidence_brief, toggles, risk, action_reason)

    return {
        "meta": {
            "mint_raw": mint,
            "mint_masked": redact_addr(mint, 6),
            "pool_masked": redact_addr(str(report.get("pool") or token_profile.get("pool") or ""), 6),
            "symbol": str(token_profile.get("token_symbol") or token_profile.get("token_name") or "UNKNOWN"),
            "source_label": source_label,
            "runtime_label": f"{to_int(meta.get('runtime_ms'), 0)} ms / {to_int(meta.get('api_calls'), 0)} API calls" if meta else "report artifact",
        },
        "executive_decision": executive,
        "evidence_surfaces": surfaces,
        "hard_evidence_brief": hard_evidence_brief,
        "decision_trace": decision_trace,
        "what_if": {
            "policy": policy,
            "base_surfaces": base_surfaces,
            "aggregate_score": round(aggregate_score, 4),
            "base_confidence_pct": confidence_pct,
            "toggles": toggles,
            "disclaimer": "Scenario outputs are controlled surface-level simulations, not chain replays.",
        },
        "case_review": case_review,
    }


def build_console_from_demo_view(
    demo_view: dict[str, Any],
    *,
    mint_hint: str = "",
    judge_mode: bool = False,
    source_label: str = "demo_view",
    get_case_review: ReviewGetter,
) -> dict[str, Any]:
    decision = demo_view.get("decision") if isinstance(demo_view.get("decision"), dict) else {}
    agent = demo_view.get("agent_judgement") if isinstance(demo_view.get("agent_judgement"), dict) else {}
    drift = demo_view.get("drift_governance") if isinstance(demo_view.get("drift_governance"), dict) else {}
    risk_score = to_float(decision.get("risk_score"), 0.0)
    confidence_pct = round(to_float(decision.get("confidence"), 0.0) * 100.0, 2)
    action = str(decision.get("action") or "REVIEW").upper()
    mint = str(demo_view.get("mint") or mint_hint or "")
    case_review = get_case_review(mint, action, risk_score)

    surfaces = {
        "funding": {
            "title": "Funding Surface",
            "score": 58.0 if action == "BLOCK" else 34.0,
            "severity": severity(58.0 if action == "BLOCK" else 34.0),
            "summary": "Fallback funding summary built from the public demo payload.",
            "metrics": surface_metrics([
                ("Paths", str(len(demo_view.get("hard_evidence") or []))),
                ("Drift", str(bool(drift.get("drift_detected")))),
                ("Mode", str(drift.get("mode") or "unknown")),
                ("Confidence", f"{confidence_pct:.1f}%"),
            ]),
            "bullets": [
                "Fallback view active because richer report fields were not available.",
                "The demo still preserves action, confidence, and evidence summary.",
            ],
            "evidence_brief": ["Fallback mode intentionally limits surface detail."],
        },
        "control": {
            "title": "Control Surface",
            "score": 52.0 if bool(agent.get("repeat_offender")) else 28.0,
            "severity": severity(52.0 if bool(agent.get("repeat_offender")) else 28.0),
            "summary": "Fallback control summary built from the public demo payload.",
            "metrics": surface_metrics([
                ("Controller", str(agent.get("who_controls") or "N/A")),
                ("Repeat", str(bool(agent.get("repeat_offender")))),
                ("Verdict", str(agent.get("verdict_level") or "")),
                ("Source", source_label),
            ]),
            "bullets": [
                "Controller-level detail is restricted in fallback mode.",
                "Repeat-offender signal is carried into the visible control surface.",
            ],
            "evidence_brief": ["Fallback mode shows only visible outcome and recommendation layers."],
        },
        "permission": {
            "title": "Permission Surface",
            "score": 34.0,
            "severity": severity(34.0),
            "summary": "Permission surface is limited in fallback mode.",
            "metrics": surface_metrics([("Program", "redacted"), ("Authorities", "redacted"), ("Signals", "limited"), ("State", "summary")]),
            "bullets": ["Public fallback mode hides permission parsing detail."],
            "evidence_brief": ["Fallback mode avoids disclosing internal permission parsing behavior."],
        },
        "issuer": {
            "title": "Issuer Surface",
            "score": 26.0,
            "severity": severity(26.0),
            "summary": "Issuer and metadata context is limited in fallback mode.",
            "metrics": surface_metrics([("Issuer count", "n/a"), ("Related assets", "n/a"), ("History", "n/a"), ("Metadata", "partial")]),
            "bullets": ["Fallback mode keeps issuer-side context minimal."],
            "evidence_brief": ["No issuer enrichment payload was available in fallback."],
        },
    }

    executive = {
        "headline": "Decision Snapshot",
        "action": action,
        "risk_score": round(risk_score, 2),
        "confidence_pct": confidence_pct,
        "confidence_label": str(decision.get("confidence_label") or ""),
        "verdict_label": str(agent.get("verdict_level") or action),
        "summary": str(agent.get("risk_conclusion") or "Fallback decision summary generated."),
        "decision_memo": str(agent.get("risk_conclusion") or decision.get("reason") or "fallback decision summary"),
        "action_reason": str(decision.get("reason") or "fallback_policy"),
        "top_flags": ["Fallback sample active", "Backend unavailable or reduced payload mode"],
    }

    toggles = [
        {
            "id": "fallback_authority_tightened",
            "label": "Tighten visible control posture",
            "description": "Fallback scenario reducing exposed control and permission pressure.",
            "available": True,
            "reductions": {"funding": 0.0, "control": 8.0, "permission": 8.0, "issuer": 0.0},
            "confidence_delta_pct": -2.0,
            "effect_summary": "control + permission surfaces",
            "rationale": "Projected risk softens because visible control posture is tightened in fallback case.",
        }
    ]

    hard_evidence_brief = {
        "evidence_count": len(demo_view.get("hard_evidence") or []),
        "strongest_signals": ["Fallback sample active"],
        "cross_token_reuse_summary": "not available in fallback",
        "control_highlights": ["fallback_control_surface"],
        "issuer_highlights": ["fallback_issuer_surface"],
        "bullets": ["Fallback mode keeps evidence concise and non-sensitive."],
    }

    decision_trace = {
        "what_drove_verdict": [f"action={action}", f"fallback_reason={executive['action_reason']}"] ,
        "what_raised_confidence": [f"confidence={confidence_pct:.1f}%"],
        "remaining_uncertainty": ["Fallback payload does not include full evidence graph."],
        "what_would_change_decision": [row["label"] for row in toggles],
    }

    return {
        "meta": {
            "mint_raw": mint,
            "mint_masked": redact_addr(mint, 6),
            "pool_masked": "N/A",
            "symbol": str(demo_view.get("symbol") or "UNKNOWN"),
            "source_label": source_label,
            "runtime_label": "demo fallback",
        },
        "executive_decision": executive,
        "evidence_surfaces": surfaces,
        "hard_evidence_brief": hard_evidence_brief,
        "decision_trace": decision_trace,
        "what_if": {
            "policy": {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55},
            "base_surfaces": {key: {"score": row["score"], "floor": max(0.0, row["score"] * 0.2)} for key, row in surfaces.items()},
            "aggregate_score": round(sum(row["score"] for row in surfaces.values()), 4),
            "base_confidence_pct": confidence_pct,
            "toggles": toggles,
            "disclaimer": "Scenario outputs are controlled surface-level simulations, not chain replays.",
        },
        "case_review": case_review,
    }
