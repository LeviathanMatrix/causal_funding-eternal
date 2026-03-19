from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
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

BACKEND_URL = os.environ.get("CF_DEMO_BACKEND_URL", "").strip()
BACKEND_API_KEY = os.environ.get("CF_DEMO_API_KEY", "").strip()
JUDGE_TOKEN = os.environ.get("CF_DEMO_JUDGE_TOKEN", "").strip()
TIMEOUT_SEC = float(os.environ.get("CF_DEMO_TIMEOUT_SEC", "90") or 90)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = ROOT / "examples" / "sample_report_redacted.json"
REVIEW_STATE_DIR = ROOT / "demo_shell" / ".local_state"
REVIEW_STATE_FILE = REVIEW_STATE_DIR / "case_reviews.json"

_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>causal_funding Decision Simulation Console</title>
  <style>
    :root {
      --paper: #f3efe6;
      --ink: #142126;
      --muted: #5b6d6f;
      --panel: rgba(255, 252, 245, 0.88);
      --panel-strong: rgba(255, 250, 240, 0.94);
      --border: rgba(15, 74, 80, 0.16);
      --accent: #0f665f;
      --accent-2: #b7802d;
      --accent-3: #7f2438;
      --shadow: 0 18px 52px rgba(18, 28, 34, 0.12);
      --allow: #20744f;
      --review: #b7802d;
      --block: #8b2237;
      --high: #8b2237;
      --medium: #b7802d;
      --low: #20744f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 102, 95, 0.16), transparent 35%),
        radial-gradient(circle at bottom right, rgba(183, 128, 45, 0.18), transparent 28%),
        linear-gradient(160deg, #f5f2e9 0%, #ebe4d5 100%);
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
      min-height: 100vh;
    }
    .wrap {
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px 18px 42px;
    }
    .hero {
      background: linear-gradient(145deg, rgba(255,255,255,0.72), rgba(255,249,237,0.9));
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 26px;
      position: relative;
      overflow: hidden;
    }
    .hero::after {
      content: "";
      position: absolute;
      inset: auto -60px -80px auto;
      width: 260px;
      height: 260px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(15,102,95,0.22), transparent 68%);
      pointer-events: none;
    }
    h1, h2, h3, h4, p { margin: 0; }
    h1 {
      font-size: clamp(34px, 4vw, 52px);
      line-height: 0.95;
      letter-spacing: -0.03em;
      max-width: 700px;
    }
    .sub {
      margin-top: 12px;
      max-width: 760px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.45;
    }
    .notice {
      margin-top: 14px;
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(183, 128, 45, 0.14);
      color: #7b541b;
      font-size: 13px;
      border: 1px solid rgba(183, 128, 45, 0.22);
    }
    .hero-grid {
      margin-top: 22px;
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 18px;
    }
    .hero-form,
    .hero-meta {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
    }
    .eyebrow {
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
    }
    form.main-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 180px 160px;
      gap: 10px;
      align-items: center;
    }
    input, select, textarea, button {
      border-radius: 14px;
      border: 1px solid rgba(16, 58, 61, 0.18);
      padding: 12px 14px;
      background: rgba(255,255,255,0.92);
      color: var(--ink);
      font: inherit;
    }
    input, select, textarea {
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
    }
    button {
      cursor: pointer;
      background: linear-gradient(135deg, #0f665f, #1e847b);
      color: #f8fffd;
      font-weight: 700;
      letter-spacing: 0.01em;
    }
    button.secondary {
      background: linear-gradient(135deg, #87612b, #b7802d);
    }
    .meta-grid,
    .summary-grid,
    .surface-grid,
    .workflow-grid,
    .sim-grid {
      display: grid;
      gap: 14px;
    }
    .meta-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
    .summary-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-top: 18px; }
    .surface-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
    .workflow-grid { grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr); }
    .sim-grid { grid-template-columns: minmax(320px, 0.92fr) minmax(0, 1.08fr); }
    .card {
      background: var(--panel-strong);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 18px;
      box-shadow: var(--shadow);
    }
    .section { margin-top: 20px; }
    .section-head {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 12px;
    }
    .section-head p {
      color: var(--muted);
      max-width: 680px;
      line-height: 1.4;
    }
    .metric-label {
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .metric-value {
      font-size: 30px;
      line-height: 1;
      letter-spacing: -0.04em;
    }
    .metric-foot {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 700;
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #fff;
    }
    .pill.ALLOW { background: var(--allow); }
    .pill.REVIEW { background: var(--review); }
    .pill.BLOCK { background: var(--block); }
    .severity {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #fff;
    }
    .severity.low { background: var(--low); }
    .severity.medium { background: var(--medium); }
    .severity.high { background: var(--high); }
    .surface-top,
    .case-meta-row,
    .sim-result-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }
    .surface-title {
      font-size: 22px;
      letter-spacing: -0.03em;
      margin-bottom: 3px;
    }
    .surface-summary,
    .body-copy,
    .audit-meta,
    .sim-note,
    .hint {
      color: var(--muted);
      line-height: 1.45;
      font-size: 14px;
    }
    ul.clean {
      margin: 12px 0 0;
      padding-left: 18px;
      display: grid;
      gap: 6px;
      color: var(--ink);
    }
    .surface-metrics {
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .surface-metrics .mini {
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid rgba(15, 74, 80, 0.09);
      background: rgba(255,255,255,0.55);
    }
    .surface-metrics .mini .k,
    .sim-k,
    .audit-meta,
    .case-label {
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }
    .surface-metrics .mini .v,
    .sim-v {
      margin-top: 4px;
      font-size: 18px;
      letter-spacing: -0.03em;
    }
    .evidence-brief {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px dashed rgba(15, 74, 80, 0.18);
    }
    .toggle-list {
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }
    .toggle {
      border: 1px solid rgba(15, 74, 80, 0.12);
      background: rgba(255,255,255,0.68);
      border-radius: 16px;
      padding: 12px 14px;
    }
    .toggle-row {
      display: flex;
      gap: 10px;
      align-items: flex-start;
    }
    .toggle input { margin-top: 4px; }
    .toggle-title {
      font-weight: 700;
      font-size: 15px;
      margin-bottom: 4px;
    }
    .toggle-effect {
      margin-top: 8px;
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 12px;
      color: var(--accent);
    }
    .disabled-toggle {
      opacity: 0.45;
      filter: grayscale(0.1);
    }
    .sim-score-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }
    .sim-block {
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid rgba(15,74,80,0.12);
      background: rgba(255,255,255,0.68);
    }
    .sim-list,
    .audit-list {
      margin-top: 14px;
      display: grid;
      gap: 10px;
    }
    .audit-item {
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid rgba(15,74,80,0.12);
      background: rgba(255,255,255,0.7);
    }
    textarea { min-height: 120px; resize: vertical; }
    .workflow-actions {
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .flash {
      margin-top: 10px;
      font-size: 13px;
      color: var(--accent);
      min-height: 18px;
    }
    .code-line {
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 12px;
      color: var(--muted);
      word-break: break-all;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 0 6px rgba(15,102,95,0.08);
      flex: 0 0 auto;
      margin-top: 5px;
    }
    @media (max-width: 940px) {
      .hero-grid,
      .sim-grid,
      .workflow-grid { grid-template-columns: 1fr; }
      form.main-form { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="eyebrow">Decision Simulation & Review Console</div>
      <h1>Institutional-grade token risk review for listing, diligence, and pre-trade control.</h1>
      <p class="sub">This public console exposes decision surfaces, scenario simulation, and review workflow while keeping core attribution and scoring internals private.</p>
      {% if backend_error %}
      <div class="notice">Backend unavailable. Showing controlled sample output: {{ backend_error }}</div>
      {% endif %}
      <div class="hero-grid">
        <div class="hero-form">
          <div class="eyebrow">Run Analysis</div>
          <form class="main-form" method="post" action="/analyze">
            <input type="text" name="mint" required placeholder="Solana mint" value="{{ input_mint }}" />
            <select name="mode">
              <option value="public" {% if not judge_mode %}selected{% endif %}>Public mode</option>
              <option value="judge" {% if judge_mode %}selected{% endif %}>Judge mode</option>
            </select>
            <button type="submit">Analyze</button>
          </form>
          <p class="hint" style="margin-top:12px;">The public console is designed to show decision quality, evidence surfaces, and review workflow without exposing private attribution internals.</p>
        </div>
        <div class="hero-meta">
          <div class="eyebrow">Case Snapshot</div>
          <div class="meta-grid">
            <div>
              <div class="metric-label">Mint</div>
              <div class="code-line">{{ console.meta.mint_masked }}</div>
            </div>
            <div>
              <div class="metric-label">Pool</div>
              <div class="code-line">{{ console.meta.pool_masked }}</div>
            </div>
            <div>
              <div class="metric-label">Symbol</div>
              <div class="code-line">{{ console.meta.symbol }}</div>
            </div>
            <div>
              <div class="metric-label">Source</div>
              <div class="code-line">{{ console.meta.source_label }}</div>
            </div>
          </div>
          <div class="meta-grid" style="margin-top:12px;">
            <div>
              <div class="metric-label">Runtime</div>
              <div class="code-line">{{ console.meta.runtime_label }}</div>
            </div>
            <div>
              <div class="metric-label">Confidence</div>
              <div class="code-line">{{ console.executive_decision.confidence_pct }}%</div>
            </div>
            <div>
              <div class="metric-label">Case ID</div>
              <div class="code-line">{{ console.case_review.case_id }}</div>
            </div>
            <div>
              <div class="metric-label">Mode</div>
              <div class="code-line">{{ 'judge' if judge_mode else 'public' }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <div class="eyebrow">Executive Decision</div>
          <h2>{{ console.executive_decision.headline }}</h2>
        </div>
        <span class="pill {{ console.executive_decision.action }}">{{ console.executive_decision.action }}</span>
      </div>
      <div class="summary-grid">
        <div class="card">
          <div class="metric-label">Risk</div>
          <div class="metric-value">{{ '%.1f'|format(console.executive_decision.risk_score) }}</div>
          <div class="metric-foot">Verdict: {{ console.executive_decision.verdict_label }}</div>
        </div>
        <div class="card">
          <div class="metric-label">Confidence</div>
          <div class="metric-value">{{ console.executive_decision.confidence_pct }}%</div>
          <div class="metric-foot">{{ console.executive_decision.confidence_label }}</div>
        </div>
        <div class="card">
          <div class="metric-label">Decision Memo</div>
          <div class="body-copy">{{ console.executive_decision.decision_memo }}</div>
        </div>
        <div class="card">
          <div class="metric-label">Priority Signal</div>
          <div class="metric-value">{{ console.case_review.priority }}</div>
          <div class="metric-foot">{{ console.executive_decision.action_reason }}</div>
        </div>
      </div>
      <div class="card" style="margin-top:14px;">
        <div class="metric-label">Why this case matters</div>
        <p class="body-copy">{{ console.executive_decision.summary }}</p>
        <ul class="clean">
          {% for flag in console.executive_decision.top_flags %}
          <li>{{ flag }}</li>
          {% endfor %}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <div class="eyebrow">Evidence Surfaces</div>
          <h2>Four operator-facing surfaces, not a single black-box score.</h2>
        </div>
        <p>Each surface is anchored to structured evidence already produced by the analysis engine. The console summarizes the result layer only.</p>
      </div>
      <div class="surface-grid">
        {% for key in surface_order %}
        {% set surface = console.evidence_surfaces[key] %}
        <article class="card">
          <div class="surface-top">
            <div>
              <div class="surface-title">{{ surface.title }}</div>
              <div class="surface-summary">{{ surface.summary }}</div>
            </div>
            <div style="text-align:right;">
              <div class="metric-value" style="font-size:28px;">{{ '%.1f'|format(surface.score) }}</div>
              <span class="severity {{ surface.severity }}">{{ surface.severity }}</span>
            </div>
          </div>
          <div class="surface-metrics">
            {% for metric in surface.metrics %}
            <div class="mini">
              <div class="k">{{ metric.label }}</div>
              <div class="v">{{ metric.value }}</div>
            </div>
            {% endfor %}
          </div>
          <ul class="clean">
            {% for bullet in surface.bullets %}
            <li>{{ bullet }}</li>
            {% endfor %}
          </ul>
          <div class="evidence-brief">
            <div class="metric-label">Evidence Brief</div>
            <ul class="clean">
              {% for bullet in surface.evidence_brief %}
              <li>{{ bullet }}</li>
              {% endfor %}
            </ul>
          </div>
        </article>
        {% endfor %}
      </div>
    </section>

    <section class="section sim-grid">
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">What-If Simulator</div>
            <h2>Scenario testing driven by the current evidence surfaces.</h2>
          </div>
        </div>
        <div class="card">
          <p class="body-copy">This simulator does not pretend to rerun the chain. It applies controlled, surface-level remediations to the current case snapshot and recalculates the decision path using the same policy boundary.</p>
          <div class="toggle-list" id="toggle-list"></div>
        </div>
      </div>
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">Simulation Result</div>
            <h2>Projected decision drift if the selected conditions were actually verified.</h2>
          </div>
        </div>
        <div class="card">
          <div class="sim-result-top">
            <div>
              <div class="metric-label">Projected Action</div>
              <div id="sim-action-pill"></div>
            </div>
            <div class="hint" id="sim-summary-text"></div>
          </div>
          <div class="sim-score-grid">
            <div class="sim-block">
              <div class="sim-k">Current Risk</div>
              <div class="sim-v" id="current-risk"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Projected Risk</div>
              <div class="sim-v" id="sim-risk"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Risk Delta</div>
              <div class="sim-v" id="sim-delta"></div>
            </div>
          </div>
          <div class="sim-score-grid">
            <div class="sim-block">
              <div class="sim-k">Funding Surface</div>
              <div class="sim-v" id="sim-funding"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Control Surface</div>
              <div class="sim-v" id="sim-control"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Permission / Issuer</div>
              <div class="sim-v" id="sim-perm-issuer"></div>
            </div>
          </div>
          <div class="sim-list" id="sim-rationale"></div>
        </div>
      </div>
    </section>

    <section class="section workflow-grid">
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">Case Review Workflow</div>
            <h2>Turn one analysis into a reviewable case record.</h2>
          </div>
        </div>
        <div class="card">
          <div class="case-meta-row">
            <div>
              <div class="metric-label">Current Status</div>
              <div class="metric-value" style="font-size:28px;" id="workflow-status">{{ console.case_review.status }}</div>
            </div>
            <div>
              <div class="metric-label">Priority</div>
              <div class="metric-value" style="font-size:28px;" id="workflow-priority">{{ console.case_review.priority }}</div>
            </div>
          </div>
          <div class="workflow-grid" style="grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 14px;">
            <div>
              <label class="case-label" for="status">Status</label>
              <select id="status">
                {% for option in status_options %}
                <option value="{{ option }}" {% if option == console.case_review.status %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
            <div>
              <label class="case-label" for="priority">Priority</label>
              <select id="priority">
                {% for option in priority_options %}
                <option value="{{ option }}" {% if option == console.case_review.priority %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
          </div>
          <div style="margin-top:10px;">
            <label class="case-label" for="reviewer">Reviewer</label>
            <input id="reviewer" type="text" value="{{ console.case_review.reviewer }}" placeholder="Reviewer or team" />
          </div>
          <div style="margin-top:10px;">
            <label class="case-label" for="note">Decision Note</label>
            <textarea id="note" placeholder="Why was this case blocked, escalated, or cleared?">{{ console.case_review.note }}</textarea>
          </div>
          <div class="workflow-actions">
            <button id="save-review" type="button" class="secondary">Save Review Note</button>
            <div class="hint">Saved notes are stored locally for this demo console only.</div>
          </div>
          <div class="flash" id="review-flash"></div>
        </div>
      </div>
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">Audit Trail</div>
            <h2>Case changes remain inspectable.</h2>
          </div>
        </div>
        <div class="card">
          <p class="sim-note">Every case save appends a local audit row with status, priority, reviewer, and note snapshot. This models the review workflow layer institutions expect.</p>
          <div class="audit-list" id="audit-list"></div>
        </div>
      </div>
    </section>
  </div>

  <script>
    const CONSOLE = {{ console|tojson }};
    const surfaceOrder = {{ surface_order|tojson }};
    const statusOptions = {{ status_options|tojson }};
    const priorityOptions = {{ priority_options|tojson }};

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function formatScore(value) {
      return `${Number(value || 0).toFixed(1)}`;
    }

    function formatDelta(value) {
      const num = Number(value || 0);
      const sign = num > 0 ? '+' : '';
      return `${sign}${num.toFixed(1)}`;
    }

    function renderPill(action) {
      return `<span class="pill ${action}">${action}</span>`;
    }

    function buildToggleList() {
      const wrap = document.getElementById('toggle-list');
      wrap.innerHTML = '';
      for (const toggle of CONSOLE.what_if.toggles) {
        const item = document.createElement('label');
        item.className = `toggle ${toggle.available ? '' : 'disabled-toggle'}`.trim();
        item.innerHTML = `
          <div class="toggle-row">
            <input type="checkbox" data-toggle-id="${toggle.id}" ${toggle.available ? '' : 'disabled'} />
            <div>
              <div class="toggle-title">${toggle.label}</div>
              <div class="sim-note">${toggle.description}</div>
              <div class="toggle-effect">Affects: ${toggle.effect_summary}</div>
            </div>
          </div>
        `;
        wrap.appendChild(item);
      }
      wrap.addEventListener('change', runSimulation);
    }

    function getSelectedToggles() {
      return Array.from(document.querySelectorAll('[data-toggle-id]:checked')).map((el) => el.getAttribute('data-toggle-id'));
    }

    function getPolicy() {
      return CONSOLE.what_if.policy || {block_threshold: 70, review_threshold: 45, min_confidence_for_block: 0.55};
    }

    function actionFromScore(score, confidencePct) {
      const policy = getPolicy();
      const confidence = Number(confidencePct || 0) / 100.0;
      if (score >= Number(policy.block_threshold || 70) && confidence >= Number(policy.min_confidence_for_block || 0.55)) {
        return 'BLOCK';
      }
      if (score >= Number(policy.review_threshold || 45)) {
        return 'REVIEW';
      }
      return 'ALLOW';
    }

    function simulateCase(selectedIds) {
      const base = CONSOLE.what_if.base_surfaces;
      const selected = CONSOLE.what_if.toggles.filter((row) => selectedIds.includes(row.id));
      const reductions = {funding: 0, control: 0, permission: 0, issuer: 0};
      const rationale = [];

      for (const toggle of selected) {
        for (const [key, value] of Object.entries(toggle.reductions || {})) {
          reductions[key] += Number(value || 0);
        }
        rationale.push(toggle.rationale);
      }

      const next = {};
      for (const key of Object.keys(base)) {
        const floor = Number(base[key].floor || 0);
        next[key] = clamp(Number(base[key].score || 0) - Number(reductions[key] || 0), floor, 100);
      }

      const currentAggregate = Number(CONSOLE.what_if.aggregate_score || 1);
      const nextAggregate = Object.values(next).reduce((acc, value) => acc + Number(value || 0), 0);
      const scale = currentAggregate > 0 ? (nextAggregate / currentAggregate) : 1;
      const baseRisk = Number(CONSOLE.executive_decision.risk_score || 0);
      const simulatedRisk = clamp(baseRisk * scale, 0, 100);
      const simulatedAction = actionFromScore(simulatedRisk, CONSOLE.executive_decision.confidence_pct);

      return {
        selectedCount: selected.length,
        risk: simulatedRisk,
        delta: simulatedRisk - baseRisk,
        action: simulatedAction,
        surfaces: next,
        rationale: rationale,
      };
    }

    function renderSimulation() {
      const result = simulateCase(getSelectedToggles());
      document.getElementById('current-risk').textContent = formatScore(CONSOLE.executive_decision.risk_score);
      document.getElementById('sim-risk').textContent = formatScore(result.risk);
      document.getElementById('sim-delta').textContent = formatDelta(result.delta);
      document.getElementById('sim-action-pill').innerHTML = renderPill(result.action);
      document.getElementById('sim-funding').textContent = formatScore(result.surfaces.funding);
      document.getElementById('sim-control').textContent = formatScore(result.surfaces.control);
      document.getElementById('sim-perm-issuer').textContent = `${formatScore(result.surfaces.permission)} / ${formatScore(result.surfaces.issuer)}`;
      document.getElementById('sim-summary-text').textContent = result.selectedCount > 0
        ? `${result.selectedCount} remediation scenario${result.selectedCount > 1 ? 's' : ''} selected.`
        : 'No scenario applied. This is the original case snapshot.';
      const rationaleWrap = document.getElementById('sim-rationale');
      rationaleWrap.innerHTML = '';
      const items = result.rationale.length ? result.rationale : ['No remediation selected. The projected outcome remains the current decision.'];
      for (const text of items) {
        const div = document.createElement('div');
        div.className = 'sim-block';
        div.innerHTML = `<div class="sim-k">Simulation rationale</div><div class="sim-note">${text}</div>`;
        rationaleWrap.appendChild(div);
      }
    }

    function renderAuditTrail(audit) {
      const wrap = document.getElementById('audit-list');
      wrap.innerHTML = '';
      const rows = Array.isArray(audit) && audit.length ? audit : [{timestamp: CONSOLE.case_review.updated_at, status: CONSOLE.case_review.status, priority: CONSOLE.case_review.priority, reviewer: CONSOLE.case_review.reviewer || 'unassigned', note: CONSOLE.case_review.note || 'Case initialized.'}];
      for (const row of rows.slice().reverse()) {
        const item = document.createElement('div');
        item.className = 'audit-item';
        item.innerHTML = `
          <div class="audit-meta">${row.timestamp || 'unknown'} | ${row.status || 'NEW'} | ${row.priority || 'MEDIUM'}</div>
          <div style="margin-top:6px; font-weight:700;">${row.reviewer || 'unassigned'}</div>
          <div class="sim-note" style="margin-top:6px;">${row.note || 'No note recorded.'}</div>
        `;
        wrap.appendChild(item);
      }
    }

    async function saveReview() {
      const flash = document.getElementById('review-flash');
      flash.textContent = 'Saving review note...';
      const body = {
        mint: CONSOLE.meta.mint_raw,
        action: CONSOLE.executive_decision.action,
        risk_score: CONSOLE.executive_decision.risk_score,
        status: document.getElementById('status').value,
        priority: document.getElementById('priority').value,
        reviewer: document.getElementById('reviewer').value,
        note: document.getElementById('note').value,
      };
      try {
        const resp = await fetch('/api/review', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body),
        });
        const payload = await resp.json();
        if (!resp.ok || !payload.ok) {
          throw new Error(payload.error || `review_http_${resp.status}`);
        }
        CONSOLE.case_review = payload.case_review;
        document.getElementById('workflow-status').textContent = payload.case_review.status;
        document.getElementById('workflow-priority').textContent = payload.case_review.priority;
        renderAuditTrail(payload.case_review.audit);
        flash.textContent = 'Review note saved.';
      } catch (err) {
        flash.textContent = `Save failed: ${err}`;
      }
    }

    function runSimulation() {
      renderSimulation();
    }

    document.getElementById('save-review').addEventListener('click', saveReview);
    buildToggleList();
    renderSimulation();
    renderAuditTrail(CONSOLE.case_review.audit || []);
  </script>
</body>
</html>
"""


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _redact_addr(addr: str, keep: int = 4) -> str:
    value = str(addr or "").strip()
    if not value:
        return "N/A"
    if len(value) <= keep * 2:
        return value
    return f"{value[:keep]}****{value[-keep:]}"


def _severity(score: float) -> str:
    if score >= 65.0:
        return "high"
    if score >= 35.0:
        return "medium"
    return "low"


def _mean(values: list[float]) -> float:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return 0.0
    return sum(clean) / float(len(clean))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _case_id_for_mint(mint: str) -> str:
    digest = hashlib.sha1(str(mint or "").encode("utf-8")).hexdigest()[:10]
    return f"CF-{digest.upper()}"


def _default_priority(action: str, risk_score: float) -> str:
    if action == "BLOCK" or risk_score >= 75.0:
        return "HIGH"
    if action == "REVIEW" or risk_score >= 45.0:
        return "MEDIUM"
    return "LOW"


def _ensure_review_store() -> None:
    REVIEW_STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_review_store() -> dict[str, Any]:
    _ensure_review_store()
    if not REVIEW_STATE_FILE.exists():
        return {}
    try:
        payload = json.loads(REVIEW_STATE_FILE.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _save_review_store(payload: dict[str, Any]) -> None:
    _ensure_review_store()
    REVIEW_STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_case_review(mint: str, action: str, risk_score: float) -> dict[str, Any]:
    store = _load_review_store()
    key = str(mint or "").strip()
    current = store.get(key) if isinstance(store.get(key), dict) else {}
    if current:
        return current
    now = _utc_now()
    return {
        "case_id": _case_id_for_mint(key),
        "status": "NEW",
        "priority": _default_priority(action, risk_score),
        "reviewer": "",
        "note": "",
        "updated_at": now,
        "audit": [
            {
                "timestamp": now,
                "status": "NEW",
                "priority": _default_priority(action, risk_score),
                "reviewer": "system",
                "note": "Case initialized from current analysis output.",
            }
        ],
    }


def _update_case_review(mint: str, action: str, risk_score: float, fields: dict[str, Any]) -> dict[str, Any]:
    key = str(mint or "").strip()
    store = _load_review_store()
    current = _get_case_review(key, action, risk_score)
    current["status"] = str(fields.get("status") or current.get("status") or "NEW").strip().upper()
    current["priority"] = str(fields.get("priority") or current.get("priority") or _default_priority(action, risk_score)).strip().upper()
    current["reviewer"] = str(fields.get("reviewer") or current.get("reviewer") or "").strip()
    current["note"] = str(fields.get("note") or current.get("note") or "").strip()
    current["updated_at"] = _utc_now()
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
    _save_review_store(store)
    return current


def _policy_from_report(report: dict[str, Any], action: str) -> dict[str, float]:
    decision = report.get("decision_policy") if isinstance(report.get("decision_policy"), dict) else {}
    thresholds = decision.get("thresholds") if isinstance(decision.get("thresholds"), dict) else {}
    if thresholds:
        return {
            "block_threshold": _to_float(thresholds.get("block_threshold"), 70.0),
            "review_threshold": _to_float(thresholds.get("review_threshold"), 45.0),
            "min_confidence_for_block": _to_float(thresholds.get("min_confidence_for_block"), 0.55),
        }
    if action == "BLOCK":
        return {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55}
    if action == "ALLOW":
        return {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55}
    return {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55}


def _surface_metrics(rows: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"label": k, "value": v} for k, v in rows[:4]]


def _build_console_from_report(report: dict[str, Any], *, mint_hint: str = "", judge_mode: bool = False, source_label: str = "analysis") -> dict[str, Any]:
    public_brief = report.get("public_brief") if isinstance(report.get("public_brief"), dict) else {}
    if not public_brief:
        return _build_console_from_demo_view({}, mint_hint=mint_hint, judge_mode=judge_mode, source_label=source_label)

    meta = report.get("meta") if isinstance(report.get("meta"), dict) else {}
    risk = report.get("risk") if isinstance(report.get("risk"), dict) else {}
    judgement = report.get("judgement") if isinstance(report.get("judgement"), dict) else {}
    decision = report.get("decision_policy") if isinstance(report.get("decision_policy"), dict) else {}
    token_profile = public_brief.get("token_profile") if isinstance(public_brief.get("token_profile"), dict) else {}
    risk_overview = public_brief.get("risk_overview") if isinstance(public_brief.get("risk_overview"), dict) else {}
    funding_chain = public_brief.get("funding_chain") if isinstance(public_brief.get("funding_chain"), dict) else {}
    control = public_brief.get("control_and_permissions") if isinstance(public_brief.get("control_and_permissions"), dict) else {}
    cross_token = public_brief.get("cross_token_intel") if isinstance(public_brief.get("cross_token_intel"), dict) else {}
    hard = public_brief.get("hard_evidence") if isinstance(public_brief.get("hard_evidence"), dict) else {}
    attribution = public_brief.get("attribution") if isinstance(public_brief.get("attribution"), dict) else {}
    lp_surface = public_brief.get("lp_surface") if isinstance(public_brief.get("lp_surface"), dict) else {}

    dims = risk_overview.get("dimension_scores") if isinstance(risk_overview.get("dimension_scores"), dict) else {}
    funding_score = _mean([
        _to_float(dims.get("R2_funding"), 0.0),
        _to_float(dims.get("R3_convergence"), 0.0),
    ])
    hidden_control = attribution.get("risk_surfaces", {}).get("hidden_control", {}) if isinstance(attribution.get("risk_surfaces"), dict) else {}
    recurrence = attribution.get("risk_surfaces", {}).get("recurrence_risk", {}) if isinstance(attribution.get("risk_surfaces"), dict) else {}
    permission_surface = control.get("token_permissions") if isinstance(control.get("token_permissions"), dict) else {}
    issuer_surface = control.get("metadata_legitimacy") if isinstance(control.get("metadata_legitimacy"), dict) else {}
    controller_dossier = control.get("controller_dossier") if isinstance(control.get("controller_dossier"), dict) else {}
    related_assets = control.get("related_assets") if isinstance(control.get("related_assets"), list) else []
    issuer_pattern = control.get("issuer_pattern_summary") if isinstance(control.get("issuer_pattern_summary"), dict) else {}

    control_score = _mean([
        _to_float(dims.get("R1_control"), 0.0),
        _to_float(hidden_control.get("score"), 0.0),
    ])
    permission_score = _to_float(permission_surface.get("score"), 0.0)
    issuer_score = _mean([
        _to_float(issuer_surface.get("risk_score"), 0.0),
        _to_float(recurrence.get("score"), 0.0) * 0.35,
    ])

    top_source = funding_chain.get("top_source") if isinstance(funding_chain.get("top_source"), dict) else {}
    top_source_share = _to_float(top_source.get("share_pct"), 0.0)
    controller_conf = _to_float(control.get("controller_confidence_pct"), 0.0)
    primary_controller = str(control.get("primary_controller") or "")
    current_action = str(decision.get("action") or "REVIEW").upper()
    risk_score = _to_float(risk.get("score"), 0.0)
    confidence = _to_float(risk.get("confidence"), 0.0)
    confidence_pct = round(confidence * 100.0, 2)
    repeat_tokens = _to_int(cross_token.get("shared_token_count"), 0)
    related_asset_count = _to_int(issuer_surface.get("related_asset_count"), 0)
    historical_asset_count = _to_int(issuer_surface.get("historical_asset_count"), 0)

    surfaces = {
        "funding": {
            "title": "Funding Surface",
            "score": round(funding_score, 2),
            "severity": _severity(funding_score),
            "summary": "How concentrated and path-dependent the traced funding footprint looks right now.",
            "metrics": _surface_metrics(
                [
                    ("Paths", str(_to_int(funding_chain.get("funding_path_count"), 0))),
                    ("Total flow", f"{_to_float(funding_chain.get('total_traced_flow_sol'), 0.0):.2f} SOL"),
                    ("Top share", f"{top_source_share:.1f}%"),
                    ("Cycle paths", str(_to_int(funding_chain.get("cycle_path_count"), 0))),
                ]
            ),
            "bullets": [
                f"{_to_int(funding_chain.get('funding_path_count'), 0)} traced paths across the current funding snapshot.",
                f"The dominant traced source accounts for {top_source_share:.1f}% of visible flow.",
                f"Maximum single traced path is {_to_float(funding_chain.get('max_path_flow_sol'), 0.0):.2f} SOL.",
            ],
            "evidence_brief": [
                f"Top source address is masked in public mode and remains available only as a summarized concentration indicator: {_redact_addr(str(top_source.get('address') or ''), 4) if not judge_mode else str(top_source.get('address') or 'N/A') }.",
                f"Funding chain summary tracks total traced flow and path concentration instead of exposing raw path internals.",
                f"Public signal set includes: {', '.join((attribution.get('public_signals') or [])[:2]) or 'No high-intensity anomaly observed'}.",
            ],
        },
        "control": {
            "title": "Control Surface",
            "score": round(control_score, 2),
            "severity": _severity(control_score),
            "summary": "Who appears to control the token surface and how strong the operator-level signals are.",
            "metrics": _surface_metrics(
                [
                    ("Controller", _redact_addr(primary_controller, 4) if not judge_mode else (primary_controller or "N/A")),
                    ("Confidence", f"{controller_conf:.1f}%"),
                    ("Dossier wallets", str(_to_int(controller_dossier.get("wallet_count"), 0))),
                    ("Service-funded", str(_to_int(controller_dossier.get("service_funded_wallet_count"), 0))),
                ]
            ),
            "bullets": [
                f"Primary controller candidate identified with {controller_conf:.1f}% confidence.",
                f"Wallet dossier coverage spans {_to_int(controller_dossier.get('wallet_count'), 0)} control-linked wallets.",
                f"Cross-token reuse signal currently touches {repeat_tokens} related token context(s).",
            ],
            "evidence_brief": [
                f"Primary identity label: {str(controller_dossier.get('primary_identity_name') or controller_dossier.get('primary_identity_type') or 'unknown')}.",
                f"Origin funding label: {str(controller_dossier.get('primary_funder_label') or controller_dossier.get('primary_funder') or 'unknown')}.",
                f"Execution and hidden-control pressure remain summarized through the control surface instead of exposing full attribution internals.",
            ],
        },
        "permission": {
            "title": "Permission Surface",
            "score": round(permission_score, 2),
            "severity": _severity(permission_score),
            "summary": "Token-level control posture, authority exposure, and extension-driven risk complexity.",
            "metrics": _surface_metrics(
                [
                    ("Program", str(permission_surface.get("program_label") or "unknown")),
                    ("Score", f"{permission_score:.1f}"),
                    ("High signals", str(_to_int(len(permission_surface.get("high_risk_signals") or []), 0))),
                    ("Extensions", str(_to_int(len(permission_surface.get("extension_labels") or []), 0))),
                ]
            ),
            "bullets": [
                f"Current token program posture: {str(permission_surface.get('program_label') or 'unknown')}.",
                f"High-risk extension signals observed: {', '.join(permission_surface.get('high_risk_signals') or []) or 'none'}.",
                f"Extensions visible in the public summary: {', '.join(permission_surface.get('extension_labels') or []) or 'none'}.",
            ],
            "evidence_brief": [
                f"Permission summary line: {str(permission_surface.get('summary') or 'not available')}.",
                f"Default account state: {str(permission_surface.get('default_account_state') or 'none') or 'none'}.",
                f"Public mode exposes only authority posture and extension labels, not the underlying parsing logic.",
            ],
        },
        "issuer": {
            "title": "Issuer Surface",
            "score": round(issuer_score, 2),
            "severity": _severity(issuer_score),
            "summary": "How complete the metadata and issuer footprint look, including related-asset context where available.",
            "metrics": _surface_metrics(
                [
                    ("Issuer count", str(_to_int(issuer_surface.get("issuer_count"), 0))),
                    ("Related assets", str(related_asset_count)),
                    ("Historical assets", str(historical_asset_count)),
                    ("Reused symbols", str(_to_int(issuer_surface.get("reused_symbol_count"), 0))),
                ]
            ),
            "bullets": [
                f"Metadata legitimacy score is {_to_float(issuer_surface.get('risk_score'), 0.0):.1f}/100.",
                f"Issuer footprint currently spans {historical_asset_count} historical asset references and {related_asset_count} related asset previews.",
                f"Issuer pattern summary flags {_to_int(issuer_pattern.get('reused_symbol_count'), 0)} reused symbol pattern(s).",
            ],
            "evidence_brief": [
                f"Metadata reasons: {', '.join((issuer_surface.get('reasons') or [])[:2]) or 'no elevated metadata anomalies disclosed'}.",
                f"Related asset preview count exposed in this console: {len(related_assets[:3])}.",
                f"Issuer context is summarized for diligence use without exposing the private enrichment pipeline.",
            ],
        },
    }

    action_reason = str(decision.get("reason") or "policy_decision")
    policy = _policy_from_report(report, current_action)
    base_surfaces = {
        "funding": {"score": surfaces["funding"]["score"], "floor": max(5.0, surfaces["funding"]["score"] * 0.20)},
        "control": {"score": surfaces["control"]["score"], "floor": max(5.0, surfaces["control"]["score"] * 0.20)},
        "permission": {"score": surfaces["permission"]["score"], "floor": max(0.0, surfaces["permission"]["score"] * 0.15)},
        "issuer": {"score": surfaces["issuer"]["score"], "floor": max(0.0, surfaces["issuer"]["score"] * 0.15)},
    }

    funding_exposure = _clamp((top_source_share - 55.0) / 45.0, 0.0, 1.0)
    mint_authority_open = str((control.get("mint_authority") or {}).get("state") or "").strip().lower() == "open"
    update_authority_open = "update_authority=open" in str(permission_surface.get("summary") or "")
    reuse_exposure = _clamp((_to_int(cross_token.get("shared_token_count"), 0) * 0.18) + (_to_int(cross_token.get("max_shared_wallets_per_token"), 0) * 0.12), 0.0, 1.0)
    issuer_exposure = _clamp((historical_asset_count * 0.08) + (related_asset_count * 0.15) + (_to_int(issuer_surface.get("reused_symbol_count"), 0) * 0.12), 0.0, 1.0)
    permission_exposure = _clamp((_to_int(len(permission_surface.get("high_risk_signals") or []), 0) * 0.30) + (_to_int(len(permission_surface.get("extension_labels") or []), 0) * 0.12), 0.0, 1.0)

    toggles = [
        {
            "id": "funding_normalized",
            "label": "Normalize dominant funding concentration",
            "description": "Assume the currently dominant funding concentration is no longer present at the same intensity.",
            "available": top_source_share >= 60.0,
            "reductions": {
                "funding": round(min(18.0, surfaces["funding"]["score"] * (0.20 + (0.18 * funding_exposure))), 2),
                "control": 0.0,
                "permission": 0.0,
                "issuer": 0.0,
            },
            "effect_summary": "funding surface only",
            "rationale": f"Projected risk softens because the currently dominant funding source concentration ({top_source_share:.1f}% of traced flow) is materially reduced.",
        },
        {
            "id": "mint_authority_revoked",
            "label": "Revoke mint authority exposure",
            "description": "Model the case as if active mint authority control is no longer present.",
            "available": mint_authority_open,
            "reductions": {
                "funding": 0.0,
                "control": round(min(8.0, surfaces["control"]["score"] * 0.12), 2),
                "permission": round(min(16.0, max(6.0, surfaces["permission"]["score"] * 0.28)), 2),
                "issuer": 0.0,
            },
            "effect_summary": "control + permission surfaces",
            "rationale": "Projected risk softens because mint-side control exposure is removed from the current token posture.",
        },
        {
            "id": "update_authority_revoked",
            "label": "Revoke update authority exposure",
            "description": "Model the case as if update authority is no longer active on the current token posture.",
            "available": update_authority_open,
            "reductions": {
                "funding": 0.0,
                "control": 0.0,
                "permission": round(min(12.0, max(4.0, surfaces["permission"]["score"] * 0.22)), 2),
                "issuer": 0.0,
            },
            "effect_summary": "permission surface only",
            "rationale": "Projected risk softens because token-level update control is tightened relative to the current observed posture.",
        },
        {
            "id": "reuse_signal_absent",
            "label": "Remove cross-token reuse pressure",
            "description": "Model the case as if the current cross-token reuse context is not present.",
            "available": repeat_tokens > 0,
            "reductions": {
                "funding": 0.0,
                "control": round(min(14.0, surfaces["control"]["score"] * (0.15 + 0.10 * reuse_exposure)), 2),
                "permission": 0.0,
                "issuer": round(min(8.0, surfaces["issuer"]["score"] * (0.10 + 0.12 * reuse_exposure)), 2),
            },
            "effect_summary": "control + issuer surfaces",
            "rationale": f"Projected risk softens because the current cross-token reuse context ({repeat_tokens} related token signal(s)) is removed from the case picture.",
        },
        {
            "id": "issuer_footprint_cleaner",
            "label": "Clean issuer footprint",
            "description": "Model the case as if issuer-side metadata and related-asset context are materially cleaner.",
            "available": historical_asset_count > 0 or related_asset_count > 0 or _to_float(issuer_surface.get("risk_score"), 0.0) > 0.0,
            "reductions": {
                "funding": 0.0,
                "control": 0.0,
                "permission": 0.0,
                "issuer": round(min(18.0, surfaces["issuer"]["score"] * (0.28 + 0.18 * issuer_exposure)), 2),
            },
            "effect_summary": "issuer surface only",
            "rationale": "Projected risk softens because issuer-side metadata legitimacy and related-asset footprint become cleaner than the currently observed case.",
        },
    ]

    aggregate_score = sum(row["score"] for row in base_surfaces.values())
    case_review = _get_case_review(str(report.get("mint") or mint_hint or token_profile.get("mint") or ""), current_action, risk_score)

    return {
        "meta": {
            "mint_raw": str(report.get("mint") or mint_hint or token_profile.get("mint") or ""),
            "mint_masked": _redact_addr(str(report.get("mint") or mint_hint or token_profile.get("mint") or ""), 6),
            "pool_masked": _redact_addr(str(report.get("pool") or token_profile.get("pool") or ""), 6),
            "symbol": str(token_profile.get("token_symbol") or token_profile.get("token_name") or "UNKNOWN"),
            "source_label": source_label,
            "runtime_label": f"{_to_int(meta.get('runtime_ms'), 0)} ms / {_to_int(meta.get('api_calls'), 0)} API calls" if meta else "report artifact",
        },
        "executive_decision": {
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
        },
        "evidence_surfaces": surfaces,
        "what_if": {
            "policy": policy,
            "base_surfaces": base_surfaces,
            "aggregate_score": round(aggregate_score, 4),
            "toggles": toggles,
            "disclaimer": "Scenario outputs are controlled surface-level simulations, not chain replays.",
        },
        "case_review": case_review,
    }


def _build_console_from_demo_view(demo_view: dict[str, Any], *, mint_hint: str = "", judge_mode: bool = False, source_label: str = "demo_view") -> dict[str, Any]:
    decision = demo_view.get("decision") if isinstance(demo_view.get("decision"), dict) else {}
    agent = demo_view.get("agent_judgement") if isinstance(demo_view.get("agent_judgement"), dict) else {}
    drift = demo_view.get("drift_governance") if isinstance(demo_view.get("drift_governance"), dict) else {}
    risk_score = _to_float(decision.get("risk_score"), 0.0)
    confidence_pct = round(_to_float(decision.get("confidence"), 0.0) * 100.0, 2)
    action = str(decision.get("action") or "REVIEW").upper()
    case_review = _get_case_review(str(demo_view.get("mint") or mint_hint or ""), action, risk_score)
    surfaces = {
        "funding": {
            "title": "Funding Surface",
            "score": 58.0 if action == "BLOCK" else 34.0,
            "severity": _severity(58.0 if action == "BLOCK" else 34.0),
            "summary": "Fallback funding summary built from the public demo payload.",
            "metrics": _surface_metrics([("Paths", str(len(demo_view.get("hard_evidence") or []))), ("Drift", str(bool(drift.get("drift_detected")))), ("Mode", str(drift.get("mode") or "unknown")), ("Confidence", f"{confidence_pct:.1f}%")]),
            "bullets": ["Fallback view active because richer report fields were not available.", "The demo still preserves action, confidence, and evidence summary.", "Funding details stay redacted in this public fallback."],
            "evidence_brief": ["Public fallback mode intentionally limits surface detail.", "Judge mode can be backed by a deeper evaluator flow."],
        },
        "control": {
            "title": "Control Surface",
            "score": 52.0 if bool(agent.get("repeat_offender")) else 28.0,
            "severity": _severity(52.0 if bool(agent.get("repeat_offender")) else 28.0),
            "summary": "Fallback control summary built from the public demo payload.",
            "metrics": _surface_metrics([("Controller", str(agent.get("who_controls") or "N/A")), ("Repeat", str(bool(agent.get("repeat_offender")))), ("Can rug", str(bool(agent.get("can_rug")))), ("Verdict", str(agent.get("verdict_level") or ""))]),
            "bullets": ["Controller-level detail is restricted in fallback mode.", "Repeat-offender signal is carried into the visible control surface.", "Deeper wallet dossier data requires full report access."],
            "evidence_brief": ["Fallback mode shows only the visible control outcome and recommendation layer."],
        },
        "permission": {
            "title": "Permission Surface",
            "score": 34.0,
            "severity": _severity(34.0),
            "summary": "Permission surface is limited in fallback mode.",
            "metrics": _surface_metrics([("Program", "redacted"), ("Authorities", "redacted"), ("Signals", "limited"), ("State", "summary only")]),
            "bullets": ["Public fallback mode hides permission parsing detail.", "Full permission posture is available only when the richer report payload is present."],
            "evidence_brief": ["Fallback mode avoids disclosing internal permission parsing behavior."],
        },
        "issuer": {
            "title": "Issuer Surface",
            "score": 26.0,
            "severity": _severity(26.0),
            "summary": "Issuer and metadata context is limited in fallback mode.",
            "metrics": _surface_metrics([("Issuer count", "n/a"), ("Related assets", "n/a"), ("History", "n/a"), ("Metadata", "partial")]),
            "bullets": ["Fallback mode keeps issuer-side context minimal.", "The live backend is expected to fill the richer issuer surface."],
            "evidence_brief": ["No issuer enrichment payload was available in the public fallback."],
        },
    }
    return {
        "meta": {
            "mint_raw": str(demo_view.get("mint") or mint_hint or ""),
            "mint_masked": _redact_addr(str(demo_view.get("mint") or mint_hint or ""), 6),
            "pool_masked": "N/A",
            "symbol": str(demo_view.get("symbol") or "UNKNOWN"),
            "source_label": source_label,
            "runtime_label": "demo fallback",
        },
        "executive_decision": {
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
        },
        "evidence_surfaces": surfaces,
        "what_if": {
            "policy": {"block_threshold": 70.0, "review_threshold": 45.0, "min_confidence_for_block": 0.55},
            "base_surfaces": {
                key: {"score": row["score"], "floor": max(0.0, row["score"] * 0.2)} for key, row in surfaces.items()
            },
            "aggregate_score": round(sum(row["score"] for row in surfaces.values()), 4),
            "toggles": [
                {
                    "id": "fallback_authority_tightened",
                    "label": "Tighten visible control posture",
                    "description": "Fallback scenario that reduces the currently exposed control and permission pressure.",
                    "available": True,
                    "reductions": {"funding": 0.0, "control": 8.0, "permission": 8.0, "issuer": 0.0},
                    "effect_summary": "control + permission surfaces",
                    "rationale": "Projected risk softens because visible control posture is tightened relative to the fallback case.",
                }
            ],
            "disclaimer": "Scenario outputs are controlled surface-level simulations, not chain replays.",
        },
        "case_review": case_review,
    }


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
    payload["ok"] = bool(ok)
    payload["source"] = source
    payload["console_view"] = console
    return payload


def _fallback_payload(mint: str, judge_mode: bool, ok: bool = True) -> dict[str, Any]:
    sample = _safe_json(SAMPLE_FILE)
    payload = _build_payload(sample, mint, judge_mode, ok=ok, source="sample_fallback")
    return payload


def _render_view(payload: dict[str, Any], *, input_mint: str = "", judge_mode: bool = False) -> str:
    console = payload.get("console_view") if isinstance(payload.get("console_view"), dict) else _fallback_payload(input_mint, judge_mode).get("console_view")
    return render_template_string(
        _TEMPLATE,
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

    req_payload = {"mint": mint, "judge_mode": judge_mode, "force": False}
    headers = {"Content-Type": "application/json"}
    if BACKEND_API_KEY:
        headers["Authorization"] = f"Bearer {BACKEND_API_KEY}"
    if JUDGE_TOKEN and judge_mode:
        headers["X-Judge-Token"] = JUDGE_TOKEN

    try:
        if not BACKEND_URL:
            raise RuntimeError("backend_not_configured")
        resp = requests.post(BACKEND_URL, json=req_payload, headers=headers, timeout=TIMEOUT_SEC)
        if resp.status_code >= 300:
            payload = _fallback_payload(mint, judge_mode, ok=False)
            payload["error"] = f"backend_http_{resp.status_code}"
        else:
            body = resp.json()
            payload = _build_payload(body if isinstance(body, dict) else {}, mint, judge_mode, ok=True, source="backend")
            if not isinstance(body, dict):
                payload["error"] = "backend_invalid_payload"
    except Exception:
        payload = _fallback_payload(mint, judge_mode, ok=False)
        payload["error"] = "backend_unreachable"

    return _render_view(payload, input_mint=mint, judge_mode=judge_mode)


@APP.post("/api/analyze")
def analyze_api() -> Any:
    body = request.get_json(silent=True) or {}
    mint = str(body.get("mint") or "").strip()
    judge_mode = bool(body.get("judge_mode"))
    if not mint:
        return jsonify({"ok": False, "error": "missing_mint"}), 400

    req_payload = {"mint": mint, "judge_mode": judge_mode, "force": bool(body.get("force"))}
    headers = {"Content-Type": "application/json"}
    if BACKEND_API_KEY:
        headers["Authorization"] = f"Bearer {BACKEND_API_KEY}"
    if JUDGE_TOKEN and judge_mode:
        headers["X-Judge-Token"] = JUDGE_TOKEN

    try:
        if not BACKEND_URL:
            raise RuntimeError("backend_not_configured")
        resp = requests.post(BACKEND_URL, json=req_payload, headers=headers, timeout=TIMEOUT_SEC)
        if resp.status_code >= 300:
            payload = _fallback_payload(mint, judge_mode, ok=False)
            payload["error"] = f"backend_http_{resp.status_code}"
            payload["upstream_status"] = resp.status_code
            return jsonify(payload), 502
        upstream = resp.json()
        if not isinstance(upstream, dict):
            payload = _fallback_payload(mint, judge_mode, ok=False)
            payload["error"] = "backend_invalid_payload"
            return jsonify(payload), 502
        payload = _build_payload(upstream, mint, judge_mode, ok=True, source="backend")
        return jsonify(payload), 200
    except Exception:
        payload = _fallback_payload(mint, judge_mode, ok=False)
        payload["error"] = "backend_unreachable"
        return jsonify(payload), 503


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
    risk_score = _to_float(body.get("risk_score"), 50.0)
    case_review = _update_case_review(
        mint,
        action,
        risk_score,
        {"status": status, "priority": priority, "reviewer": reviewer, "note": note},
    )
    return jsonify({"ok": True, "case_review": case_review}), 200


if __name__ == "__main__":
    host = os.environ.get("CF_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("CF_DEMO_PORT", "7860") or 7860)
    debug = bool(int(os.environ.get("CF_DEMO_DEBUG", "0") or 0))
    APP.run(host=host, port=port, debug=debug)
