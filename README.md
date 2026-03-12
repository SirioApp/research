# Backed Research Agent

Backed Research Agent is an analyst-grade web3 diligence engine for venture-style underwriting.
It transforms heterogeneous source material (websites and documents) into a structured investment output for IC workflows, risk teams, and dashboard systems.

## Scope

The engine is designed for early-stage to growth-stage crypto/web3 opportunities where information quality is inconsistent and downside protection is critical.

## Core capabilities

1. Ingestion
- URL fetching with retry/backoff and fallback strategy for `429/5xx` surfaces.
- Local file ingestion (`txt`, `md`, `csv`, `json`, `pdf`, `docx`).

2. Deterministic underwriting
- Multi-dimension scoring with explicit weights and confidence.
- Positive/negative evidence accounting for each analytical dimension.

3. Risk and team evaluation
- Structured risk register (`probability`, `impact`, `severity`, mitigation metadata).
- Team underwriting across founder visibility, execution history, domain fit, hiring signal, governance trust.

4. Market and fundraising context
- Live market signals (BTC/ETH, dominance, TVL, sentiment, regime).
- Raise signal extraction and benchmark comparison with raising difficulty score.

5. Decision output and dashboard payload
- Executive summary and recommendation.
- Project assessment and investment memo.
- Dashboard-native section with KPIs, alerts, gates, and dimension rows.

## Runtime modes

- `rules`: deterministic engine only.
- `auto`: deterministic engine plus AI refinement when `OPENAI_API_KEY` is available.
- `ai`: AI refinement required.

AI refinement improves narrative and advanced analytical fields but does not replace deterministic pipeline structure.

## Installation

```bash
pip install -e .
```

## Configuration

Create `.env` from template.

Unix/macOS:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Supported variables:

- `OPENAI_API_KEY` (optional)
- `BACKED_API_KEY` (default: `GIT3PRIVATE`)
- `BACKED_API_HOST` (default: `127.0.0.1`)
- `BACKED_API_PORT` (default: `8000`)
- `BACKED_API_CORS_ORIGINS` (default: `*`)

## CLI usage

Primary command:
```bash
backed-research-agent --source "https://project-site.com" --json --output "./out/report.json"
```

Compatibility alias:
```bash
investment-agent --source "https://project-site.com" --json --output "./out/report.json"
```

Module entrypoint:
```bash
python -m investment_agent.cli --source "https://project-site.com" --json --output "./out/report.json"
```

CLI options:

- `--source` repeatable URL or local file input
- `--mode` `auto | ai | rules`
- `--model` LLM model for AI mode (default `gpt-4.1-mini`)
- `--json` print full JSON output
- `--output` write full JSON output to file

## API usage

Start API service:
```bash
backed-research-agent-api
```

Available endpoints:

- `GET /v1/health`
- `POST /v1/analyze` (API key required)

API authentication:

- `X-API-Key: <key>`
- or `Authorization: Bearer <key>`

Request payload supports:

- `source` (single source)
- `sources` (multiple sources)
- `mode`
- `model`

Response includes:

- request metadata (`request_id`, `sources`, `mode`, `model`)
- full underwriting result under `result`

## Output contract

Top-level analysis payload sections:

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

Schema reference: [docs/OUTPUT_SCHEMA.md](./docs/OUTPUT_SCHEMA.md)

## Technical documentation

- [Integration.md](./Integration.md)
- [docs/API.md](./docs/API.md)
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- [docs/VC_FRAMEWORK.md](./docs/VC_FRAMEWORK.md)
- [docs/DASHBOARD_INTEGRATION.md](./docs/DASHBOARD_INTEGRATION.md)
- [docs/RESEARCH_BASIS.md](./docs/RESEARCH_BASIS.md)
- [docs/ROADMAP.md](./docs/ROADMAP.md)
- [docs/PROTOCOL_INTEGRATIONS.md](./docs/PROTOCOL_INTEGRATIONS.md)

## Near-term integration roadmap

Planned protocol roadmap includes **x402 on MegaETH** as a payment/authentication primitive for premium research execution paths.
This integration is planned and not active in the current release.

## Development

```bash
python -m unittest discover -s tests -v
```

## Disclaimer

Backed Research Agent is a decision-support system and not financial, legal, or investment advice.
