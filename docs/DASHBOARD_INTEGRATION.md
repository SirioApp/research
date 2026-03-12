# Dashboard Integration Guide

## Objective

Map Backed Research Agent output to operational dashboards for IC workflows, risk monitoring, and pipeline triage.

## Integration options

1. CLI batch flow
- Run CLI on schedule or event trigger.
- Save JSON payload to storage.
- Feed dashboard ETL from stored payloads.

2. API flow
- Call `POST /v1/analyze` from backend.
- Persist response envelope and `result` payload.
- Serve dashboard from normalized views and raw JSON snapshots.

## Suggested dashboard layout

### Row 1: Decision overview

- Investment score (`result.score.value`)
- Confidence (`result.score.confidence`)
- Recommendation (`result.recommendation`)
- Market regime (`result.market_snapshot.regime`)

### Row 2: Risk surfaces

- Max risk severity (`result.dashboard.kpis.max_risk_severity`)
- Avg risk severity (`result.dashboard.kpis.avg_risk_severity`)
- Risk register heatmap (`result.risk_register[]`)

### Row 3: Team and fundraising

- Team score (`result.team_assessment.overall_score`)
- Team sub-score radar (`result.team_assessment.*_score`)
- Raising difficulty (`result.fundraising_context.raising_difficulty_score`)
- Raise benchmark ratio (`result.fundraising_context.raise_to_benchmark_ratio`)

### Row 4: Dimension diagnostics

- Table source: `result.dashboard.dimension_rows[]`
- Key columns: score, confidence, risk severity, hit balance, analysis, key questions

### Row 5: Actionability

- Alerts (`result.dashboard.top_alerts[]`)
- Decision gates (`result.dashboard.decision_gates[]`)
- Next checks (`result.project_assessment.next_checks[]`)

## Data model recommendations

For warehouse/BI architecture:

- Keep full raw JSON for auditability and replay.
- Build normalized tables:
  - `analysis_runs`
  - `dimension_findings`
  - `risk_items`
  - `team_metrics`
  - `market_snapshots`
  - `fundraising_snapshots`

## Refresh policy

- Market context refresh: every 4-12h.
- Full underwriting rerun: on new project docs/events or major market dislocations.
- IC freeze snapshot: persist immutable run artifact before committee decisions.

## Quality controls

- Validate against `docs/OUTPUT_SCHEMA.md`.
- Reject payloads missing `risk_register`, `team_assessment`, or `dashboard` blocks.
- Track partial provider failures via notes fields (`market_snapshot.notes`, `fundraising_context.notes`).
- Log API status code, request_id, and source fingerprint for troubleshooting.
