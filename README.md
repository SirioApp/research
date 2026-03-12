# Backed Research Agent

Backed Research Agent is an analyst-grade web3 diligence engine for venture-style underwriting.
It converts heterogeneous project sources (websites + documents) into a structured decision payload for investment committees, risk teams, and dashboard systems.

## Scope

The engine is designed for early-stage to growth-stage web3 opportunities where signal quality is noisy and downside risk dominates the decision surface.

## What the system does

1. Ingests source material
- URL fetching with anti-rate-limit resilience (retry/backoff/fallback).
- Local document ingestion (`txt`, `md`, `csv`, `json`, `pdf`, `docx`).

2. Runs deterministic underwriting
- 9-dimension scoring model with confidence and explicit weights.
- Evidence-term accounting per dimension (positive/negative clusters).

3. Builds multi-factor risk register
- `probability`, `impact`, `severity` decomposition.
- Risk metadata (`category`, `owner`, `timeframe`, `mitigation`).

4. Computes dedicated team underwriting
- Founder visibility.
- Execution track record.
- Domain expertise.
- Hiring signal.
- Governance trust.

5. Adds live market/fundraising context
- CoinGecko, DefiLlama, Fear & Greed sources.
- Detected raise context + benchmark ratio + raising difficulty.

6. Produces decision artifacts
- Executive summary.
- Recommendation.
- Project assessment (strengths, red flags, catalysts, checks).
- Investment memo (summary, bull case, bear case, decision statement).
- Dashboard-first payload (`kpis`, alerts, gates, rows).

## Deterministic core + optional AI refinement

- `--mode rules`: deterministic only.
- `--mode auto`: deterministic + AI refinement when `OPENAI_API_KEY` is present.
- `--mode ai`: force AI refinement.

AI does not replace the deterministic base; it refines narrative quality and can adjust analytical fields within schema constraints.

## Installation

```bash
pip install -e .
```

## Configuration

Create `.env` from template:

Unix/macOS:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Optional:
```bash
OPENAI_API_KEY=your_key
```

## Usage

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

## CLI options

```text
--source   Repeatable URL or local file input
--mode     auto | ai | rules
--model    LLM model for ai mode (default: gpt-4.1-mini)
--json     Print full JSON payload
--output   Save JSON payload to file
```

## Output contract

Top-level sections:
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

## Technical docs

- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- [docs/VC_FRAMEWORK.md](./docs/VC_FRAMEWORK.md)
- [docs/DASHBOARD_INTEGRATION.md](./docs/DASHBOARD_INTEGRATION.md)
- [docs/RESEARCH_BASIS.md](./docs/RESEARCH_BASIS.md)
- [docs/ROADMAP.md](./docs/ROADMAP.md)
- [docs/PROTOCOL_INTEGRATIONS.md](./docs/PROTOCOL_INTEGRATIONS.md)

## Near-term integration roadmap

Planned integration includes **x402 on MegaETH** as a protocol-level payment/authentication primitive for premium research execution paths.
This integration is currently **planned** and not yet enabled in the current release.

## Development

```bash
python -m unittest discover -s tests -v
```

## Disclaimer

Backed Research Agent is a decision-support system and not financial, legal, or investment advice.
