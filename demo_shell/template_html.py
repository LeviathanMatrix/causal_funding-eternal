from __future__ import annotations

TEMPLATE = """
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
    .watchlist-list {
      margin-top: 12px;
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

    <section class="section workflow-grid">
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">Hard Evidence Brief</div>
            <h2>High-signal evidence digest for decision consumers.</h2>
          </div>
        </div>
        <div class="card">
          <div class="metric-label">Evidence Count</div>
          <div class="metric-value" style="font-size:28px;">{{ console.hard_evidence_brief.evidence_count }}</div>
          <ul class="clean">
            {% for bullet in console.hard_evidence_brief.bullets %}
            <li>{{ bullet }}</li>
            {% endfor %}
          </ul>
          <div class="evidence-brief">
            <div class="metric-label">Strongest Signals</div>
            <ul class="clean">
              {% for row in console.hard_evidence_brief.strongest_signals %}
              <li>{{ row }}</li>
              {% endfor %}
            </ul>
          </div>
        </div>
      </div>
      <div>
        <div class="section-head">
          <div>
            <div class="eyebrow">Decision Trace</div>
            <h2>Why this verdict, what is uncertain, what can change it.</h2>
          </div>
        </div>
        <div class="card">
          <div class="metric-label">What Drove The Verdict</div>
          <ul class="clean">
            {% for row in console.decision_trace.what_drove_verdict %}
            <li>{{ row }}</li>
            {% endfor %}
          </ul>
          <div class="evidence-brief">
            <div class="metric-label">Confidence Drivers</div>
            <ul class="clean">
              {% for row in console.decision_trace.what_raised_confidence %}
              <li>{{ row }}</li>
              {% endfor %}
            </ul>
          </div>
          <div class="evidence-brief">
            <div class="metric-label">Remaining Uncertainty</div>
            <ul class="clean">
              {% for row in console.decision_trace.remaining_uncertainty %}
              <li>{{ row }}</li>
              {% endfor %}
            </ul>
          </div>
        </div>
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
              <div class="sim-k">Current Confidence</div>
              <div class="sim-v" id="current-confidence"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Projected Confidence</div>
              <div class="sim-v" id="sim-confidence"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Confidence Delta</div>
              <div class="sim-v" id="sim-confidence-delta"></div>
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
            <button id="export-case" type="button">Export Brief JSON</button>
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
        <div class="card" style="margin-top:14px;">
          <div class="eyebrow">Watchlist / Recheck</div>
          <p class="sim-note">Track this token for rechecks and retain change snapshots over time.</p>
          <div class="workflow-actions">
            <button id="toggle-watchlist" type="button" class="secondary"></button>
            <button id="run-recheck" type="button">Run Recheck Snapshot</button>
          </div>
          <div class="sim-list">
            <div class="sim-block">
              <div class="sim-k">Tracked</div>
              <div class="sim-v" id="watchlist-tracked"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Last Recheck</div>
              <div class="sim-note" id="watchlist-last-recheck"></div>
            </div>
            <div class="sim-block">
              <div class="sim-k">Last Verdict</div>
              <div class="sim-note" id="watchlist-last-verdict"></div>
            </div>
          </div>
          <div class="watchlist-list" id="watchlist-history"></div>
        </div>
      </div>
    </section>
  </div>

  <script>
    let CONSOLE = {{ console|tojson }};

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

    function getSelectedToggles() {
      return Array.from(document.querySelectorAll('[data-toggle-id]:checked')).map((el) => el.getAttribute('data-toggle-id'));
    }

    function buildToggleList() {
      const wrap = document.getElementById('toggle-list');
      wrap.innerHTML = '';
      for (const toggle of (CONSOLE.what_if?.toggles || [])) {
        const item = document.createElement('label');
        item.className = `toggle ${toggle.available ? '' : 'disabled-toggle'}`.trim();
        item.innerHTML = `
          <div class="toggle-row">
            <input type="checkbox" data-toggle-id="${toggle.id}" ${toggle.available ? '' : 'disabled'} />
            <div>
              <div class="toggle-title">${toggle.label}</div>
              <div class="sim-note">${toggle.description}</div>
              <div class="toggle-effect">Affects: ${toggle.effect_summary} | confidence_delta=${formatDelta(toggle.confidence_delta_pct || 0)}%</div>
            </div>
          </div>
        `;
        wrap.appendChild(item);
      }
      wrap.addEventListener('change', runSimulation);
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

    function renderWatchlist(entry) {
      const watch = entry || {};
      document.getElementById('watchlist-tracked').textContent = watch.tracked ? 'YES' : 'NO';
      document.getElementById('watchlist-last-recheck').textContent = watch.last_recheck_at || 'N/A';
      document.getElementById('watchlist-last-verdict').textContent = watch.last_action ? `${watch.last_action} @ ${formatScore(watch.last_risk_score)}` : 'N/A';
      document.getElementById('toggle-watchlist').textContent = watch.tracked ? 'Untrack' : 'Track';

      const historyWrap = document.getElementById('watchlist-history');
      historyWrap.innerHTML = '';
      const rows = Array.isArray(watch.history) ? watch.history : [];
      if (!rows.length) {
        const row = document.createElement('div');
        row.className = 'sim-note';
        row.textContent = 'No recheck history yet.';
        historyWrap.appendChild(row);
        return;
      }
      for (const row of rows.slice().reverse().slice(0, 8)) {
        const el = document.createElement('div');
        el.className = 'audit-item';
        el.innerHTML = `
          <div class="audit-meta">${row.timestamp || 'unknown'}</div>
          <div style="margin-top:6px; font-weight:700;">${row.action || 'N/A'} | risk=${formatScore(row.risk_score)}</div>
          <div class="sim-note" style="margin-top:6px;">confidence=${formatScore(row.confidence_pct)}% | ${row.summary || ''}</div>
        `;
        historyWrap.appendChild(el);
      }
    }

    async function renderSimulation() {
      const selectedIds = getSelectedToggles();
      const resp = await fetch('/api/simulate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({console: CONSOLE, selected_toggle_ids: selectedIds}),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) {
        return;
      }
      const result = payload.simulation || {};
      document.getElementById('current-risk').textContent = formatScore(CONSOLE.executive_decision.risk_score);
      document.getElementById('sim-risk').textContent = formatScore(result.risk);
      document.getElementById('sim-delta').textContent = formatDelta(result.risk_delta);
      document.getElementById('current-confidence').textContent = `${formatScore(CONSOLE.executive_decision.confidence_pct)}%`;
      document.getElementById('sim-confidence').textContent = `${formatScore(result.confidence_pct)}%`;
      document.getElementById('sim-confidence-delta').textContent = `${formatDelta(result.confidence_delta_pct)}%`;
      document.getElementById('sim-action-pill').innerHTML = renderPill(result.action || CONSOLE.executive_decision.action);
      document.getElementById('sim-funding').textContent = formatScore((result.surfaces || {}).funding);
      document.getElementById('sim-control').textContent = formatScore((result.surfaces || {}).control);
      document.getElementById('sim-perm-issuer').textContent = `${formatScore((result.surfaces || {}).permission)} / ${formatScore((result.surfaces || {}).issuer)}`;
      document.getElementById('sim-summary-text').textContent = (result.selected_count || 0) > 0
        ? `${result.selected_count} remediation scenario${result.selected_count > 1 ? 's' : ''} selected.`
        : 'No scenario applied. This is the original case snapshot.';

      const rationaleWrap = document.getElementById('sim-rationale');
      rationaleWrap.innerHTML = '';
      const items = Array.isArray(result.rationale) && result.rationale.length
        ? result.rationale
        : ['No remediation selected. The projected outcome remains the current decision.'];
      for (const text of items) {
        const div = document.createElement('div');
        div.className = 'sim-block';
        div.innerHTML = `<div class="sim-k">Simulation rationale</div><div class="sim-note">${text}</div>`;
        rationaleWrap.appendChild(div);
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

    async function toggleWatchlist() {
      const watch = CONSOLE.watchlist || {};
      const desired = !Boolean(watch.tracked);
      const resp = await fetch('/api/watchlist', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mint: CONSOLE.meta.mint_raw, tracked: desired}),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) return;
      CONSOLE.watchlist = payload.watchlist || {};
      renderWatchlist(CONSOLE.watchlist);
    }

    async function runRecheck() {
      const resp = await fetch('/api/recheck', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          mint: CONSOLE.meta.mint_raw,
          judge_mode: {{ 'true' if judge_mode else 'false' }},
          refresh: true,
          action: CONSOLE.executive_decision.action,
          risk_score: CONSOLE.executive_decision.risk_score,
          confidence_pct: CONSOLE.executive_decision.confidence_pct,
          summary: CONSOLE.executive_decision.summary,
        }),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) return;
      if (payload.console_view && typeof payload.console_view === 'object') {
        CONSOLE = payload.console_view;
      }
      CONSOLE.watchlist = payload.watchlist || {};
      renderWatchlist(CONSOLE.watchlist);
      renderSimulation();
    }

    async function exportCase() {
      const resp = await fetch('/api/export-case', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({console: CONSOLE}),
      });
      const payload = await resp.json();
      if (!resp.ok || !payload.ok) return;
      const blob = new Blob([JSON.stringify(payload.export || {}, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(CONSOLE.meta?.mint_raw || 'case').slice(0, 16)}_brief.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }

    function runSimulation() {
      renderSimulation();
    }

    document.getElementById('save-review').addEventListener('click', saveReview);
    document.getElementById('toggle-watchlist').addEventListener('click', toggleWatchlist);
    document.getElementById('run-recheck').addEventListener('click', runRecheck);
    document.getElementById('export-case').addEventListener('click', exportCase);

    buildToggleList();
    renderSimulation();
    renderAuditTrail((CONSOLE.case_review || {}).audit || []);
    renderWatchlist(CONSOLE.watchlist || {});
  </script>
</body>
</html>
"""
