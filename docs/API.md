# API Reference

## Service

Backed Research Agent exposes an HTTP API intended for backend services and dashboard frontends.

- Base URL: `http://<host>:<port>`
- Version prefix: `/v1`

## Authentication

`POST /v1/analyze` requires an API key.

Accepted headers:

- `X-API-Key: <key>`
- `Authorization: Bearer <key>`

Default key is `GIT3PRIVATE` unless replaced by `BACKED_API_KEY`.

## Endpoints

### GET `/v1/health`

Response:

- `status`
- `service`
- `version`

### POST `/v1/analyze`

Request body:

- `source` (`string`, optional)
- `sources` (`string[]`, optional)
- `mode` (`auto | ai | rules`, default `auto`)
- `model` (`string`, default `gpt-4.1-mini`)

Validation rules:

- `source` and `sources` are mutually exclusive.
- One of them must be present.

Response body:

- `request_id` (`string`)
- `sources` (`string[]`)
- `mode` (`string`)
- `model` (`string`)
- `result` (`object`) full structured analysis payload

The `result` object shape is defined in [docs/OUTPUT_SCHEMA.md](./OUTPUT_SCHEMA.md).

## Status codes

- `200`: analysis completed
- `401`: authentication failure
- `422`: bad request or ingestion failure
- `500`: internal failure

## Runtime configuration

- `BACKED_API_KEY`: API authentication key
- `BACKED_API_HOST`: bind host
- `BACKED_API_PORT`: bind port
- `BACKED_API_CORS_ORIGINS`: comma-separated allowed origins

## Launch

Run API with project script:

- `backed-research-agent-api`
