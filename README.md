# Backed Research Agent

Backed Research Agent is an analyst-grade web3 due-diligence engine designed for venture-style underwriting.
It ingests project materials, computes structured risk and scoring outputs, and returns a dashboard-ready JSON payload.

## Why this project
- Build a repeatable, evidence-oriented investment process.
- Standardize downside-first risk evaluation.
- Export dense analytics for dashboards and IC workflows.

## Core features
- Multi-dimension underwriting model (`0..1`) with confidence.
- Extended risk register (probability, impact, severity, owner, timeframe, mitigation).
- Dedicated team assessment model.
- Live market context (CoinGecko, DefiLlama, Fear & Greed).
- Fundraising context with benchmarking and raising difficulty score.
- Dashboard section with KPIs, top alerts, decision gates, and dimension rows.

## Installation
```bash
pip install -e .
```

## Configuration
Create `.env` from example:

Unix/macOS:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Optional for AI refinement:
```bash
OPENAI_API_KEY=your_key
```

## Usage
Primary CLI command:
```bash
backed-research-agent --source "https://project-site.com" --json --output "./out/report.json"
```

Compatibility alias:
```bash
investment-agent --source "https://project-site.com" --json --output "./out/report.json"
```

Python module usage:
```bash
python -m investment_agent.cli --source "https://project-site.com" --json --output "./out/report.json"
```

## CLI options
```text
--source   Repeatable URL or local file input
--mode     auto | ai | rules
--model    LLM model for ai mode (default: gpt-4.1-mini)
--json     Print full JSON payload
--output   Save JSON payload to file
```

## Output sections
- `score`
- `executive_summary`
- `recommendation`
- `project_assessment`
- `risk_register`
- `team_assessment`
- `market_snapshot`
- `fundraising_context`
- `dashboard`
- `findings`
- `sources`

Full schema: [docs/OUTPUT_SCHEMA.md](./docs/OUTPUT_SCHEMA.md)

## Repository documentation
- [docs/VC_FRAMEWORK.md](./docs/VC_FRAMEWORK.md)
- [docs/OUTPUT_SCHEMA.md](./docs/OUTPUT_SCHEMA.md)
- [docs/RESEARCH_BASIS.md](./docs/RESEARCH_BASIS.md)
- [docs/RELEASE_CHECKLIST.md](./docs/RELEASE_CHECKLIST.md)
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- [docs/DASHBOARD_INTEGRATION.md](./docs/DASHBOARD_INTEGRATION.md)

## Development
Run tests:
```bash
python -m unittest discover -s tests -v
```

## Disclaimer
This software is decision support. It is not financial, legal, or investment advice.
