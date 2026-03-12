# Dashboard Integration Guide

## Goal
Use the agent output as a direct data source for dashboards.

## Recommended ingestion
1. Run CLI in JSON mode and write to a file.
2. Load JSON into your data layer (warehouse, API, or frontend state).
3. Bind sections to dashboard widgets.

## Example command
```bash
backed-research-agent \
  --source "https://project-site.com" \
  --json \
  --output "./out/report.json"
```

## Widget mapping
- Score card: `score.value`, `score.confidence`
- Recommendation badge: `recommendation`
- Risk heatmap: `risk_register[]` (severity/probability/impact)
- Team panel: `team_assessment`
- Market panel: `market_snapshot`
- Fundraising panel: `fundraising_context`
- Alerts list: `dashboard.top_alerts[]`
- Decision checklist: `dashboard.decision_gates[]`
- Dimension table: `dashboard.dimension_rows[]`

## Data refresh
- Intraday: refresh market/fundraising context every 4-12 hours.
- Deep diligence refresh: rerun full analysis when new project docs are available.
