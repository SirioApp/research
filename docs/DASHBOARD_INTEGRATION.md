# Dashboard Integration Guide

## Objective

Map `AgentResult` output to operational dashboards for IC workflows, risk monitoring, and pipeline triage.

## Execution pattern

1. Run CLI with JSON output.
2. Persist payload to storage (blob/db/warehouse).
3. Materialize dashboard views from stable schema paths.

Example:
```bash
backed-research-agent --source "https://project-site.com" --json --output "./out/report.json"
```

## Suggested dashboard layout

### Row 1: Decision overview
- Investment score (`score.value`)
- Confidence (`score.confidence`)
- Recommendation (`recommendation`)
- Market regime (`market_snapshot.regime`)

### Row 2: Risk surfaces
- Max risk severity (`dashboard.kpis.max_risk_severity`)
- Avg risk severity (`dashboard.kpis.avg_risk_severity`)
- Risk register heatmap (`risk_register[]`)

### Row 3: Team + fundraising
- Team overall score (`team_assessment.overall_score`)
- Sub-score radar (`team_assessment.*_score`)
- Raising difficulty (`fundraising_context.raising_difficulty_score`)
- Raise vs benchmark ratio (`fundraising_context.raise_to_benchmark_ratio`)

### Row 4: Dimension diagnostics
- Table source: `dashboard.dimension_rows[]`
- Columns: score, confidence, risk severity, hit counts, analysis

### Row 5: Actionability
- Alerts (`dashboard.top_alerts[]`)
- Decision gates (`dashboard.decision_gates[]`)
- Next checks (`project_assessment.next_checks[]`)

## Data model recommendations

For BI/warehouse ingestion:
- Store full raw JSON for traceability.
- Extract normalized tables:
  - `runs`
  - `risk_items`
  - `dimension_findings`
  - `team_metrics`
  - `market_snapshots`
  - `fundraising_snapshots`

## Refresh policy

- Market context: every 4-12h.
- Full underwriting rerun: when new project documents appear or after major market dislocations.
- IC-ready snapshot: freeze payload with timestamp before committee review.

## Quality controls

- Enforce schema checks against `docs/OUTPUT_SCHEMA.md`.
- Reject payloads missing `risk_register`, `team_assessment`, or `dashboard` sections.
- Log provider notes for partial market/fundraising fetch failures.
