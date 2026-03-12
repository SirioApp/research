# Integration Guide

## Purpose

This document defines how to integrate Backed Research Agent into a web application and dashboard stack through the HTTP API.

## API service profile

- Service name: `backed-research-agent-api`
- Default host: `127.0.0.1`
- Default port: `8000`
- Versioned base path: `/v1`
- Authentication: API key required for analysis endpoints

## Authentication contract

Use one of the following headers:

- `X-API-Key: <key>`
- `Authorization: Bearer <key>`

Default key is `GIT3PRIVATE` unless overridden by `BACKED_API_KEY`.

## Endpoints

### `GET /v1/health`

Returns service liveness and version metadata.

### `POST /v1/analyze`

Runs a full underwriting cycle and returns dashboard-ready JSON.

Request fields:

- `source` (string, optional): single source URL or local path
- `sources` (array[string], optional): multiple sources
- `mode` (string): `auto`, `ai`, `rules`
- `model` (string): model identifier used in AI mode

Rules:

- Use `source` or `sources`, never both.
- At least one source must be provided.

Response envelope:

- `request_id`: trace identifier for frontend correlation
- `sources`: normalized input list processed by the run
- `mode`: run mode used by the engine
- `model`: model name used by the run
- `result`: full analysis payload (`score`, `risk_register`, `team_assessment`, `market_snapshot`, `dashboard`, etc.)

## Error semantics

- `401`: invalid or missing API key
- `422`: invalid payload or ingestion failure
- `500`: internal execution failure

Frontend should surface non-200 responses with request-level retry controls.

## Dashboard ingestion model

Recommended persistence strategy:

1. Store full response JSON in immutable run storage.
2. Extract normalized tables for analytics and UI queries.
3. Index by `request_id`, source fingerprint, and timestamp.

Suggested table entities:

- `analysis_runs`
- `dimension_findings`
- `risk_items`
- `team_assessments`
- `market_snapshots`
- `fundraising_contexts`
- `dashboard_rows`

Primary UI mappings:

- Header KPIs from `result.dashboard.kpis`
- Risk alerts from `result.dashboard.top_alerts`
- Decision checks from `result.dashboard.decision_gates`
- Dimension table from `result.dashboard.dimension_rows`
- Memo panel from `result.investment_memo`

## CORS and frontend access

Configure allowed browser origins through:

- `BACKED_API_CORS_ORIGINS`

Use comma-separated values for multiple origins.

## Operational recommendations

- Enforce request timeout and retry policy client-side.
- Persist API response and raw source list together for auditability.
- Treat `request_id` as primary troubleshooting key.
- Log API errors with status, source, and mode.
- Run API behind TLS and rotate `BACKED_API_KEY` for production.

## Environment variables

- `OPENAI_API_KEY`: optional, enables AI refinement when mode is `auto` or `ai`
- `BACKED_API_KEY`: API authentication key (`GIT3PRIVATE` default)
- `BACKED_API_HOST`: bind host for API runtime
- `BACKED_API_PORT`: bind port for API runtime
- `BACKED_API_CORS_ORIGINS`: allowed frontend origins

## Run commands

- CLI: `backed-research-agent --source "https://project-site.com" --json`
- API server: `backed-research-agent-api`

## Production hardening checklist

- Place API behind reverse proxy with rate limiting.
- Enable structured request logging and error tracing.
- Add persistent queueing for high-volume ingestion jobs.
- Introduce API key vault management and scheduled rotation.
- Pin dependency versions for reproducible deployments.
