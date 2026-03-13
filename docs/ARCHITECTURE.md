# Architecture

## System objective

Produce institutional-quality underwriting artifacts from noisy web3 project data, with deterministic risk decomposition and dashboard-native outputs.

## Runtime pipeline

1. `ingestion.py`
- Reads source URLs/files.
- URL path includes retry strategy for `429/5xx` and fallback fetch strategy.
- Normalizes text into canonical corpus blocks.

2. `research.py`
- Applies weighted dimension profiles.
- Counts positive/negative term clusters per dimension using sentence-level normalization (anti-keyword-stuffing).
- Computes per-dimension:
  - `score` in `[0,1]`
  - `confidence` in `[0,1]`
  - evidence map for explainability

3. `scoring.py`
- Aggregates weighted dimension outputs.
- Computes base portfolio-style score:
  - `weighted_score = sum(score_i * weight_i)`
  - `weighted_confidence = sum(confidence_i * weight_i)`

4. `risk_engine.py`
- Converts dimension outputs into risk vectors.
- For each dimension:
  - `probability = f(low_score, low_confidence)`
  - `impact = dimension criticality constant`
  - `severity = probability * impact`
- Enriches each risk with owner/timeframe/mitigation metadata.

5. `team_engine.py`
- Calculates dedicated team quality model independent from aggregate score.
- Generates strengths, concerns, and diligence questions.

6. `market_data.py`
- Pulls current market state from public providers.
- Computes `regime` classification (`risk_on`, `neutral`, `risk_off`).

7. `fundraising.py`
- Detects raise signals from project corpus.
- Maps detected round type to benchmark range.
- Computes raising difficulty as a function of market regime + sentiment + benchmark ratio.

8. `narrative.py`
- Produces committee-facing textual outputs.
- Builds recommendation logic, project assessment, and memo artifacts.

9. `agent.py`
- Orchestrates full pipeline.
- Applies context adjustments to base score:
  - team penalty
  - risk penalty
  - funding penalty
  - market penalty
- Optional AI refinement pass.

10. `dashboard.py`
- Builds dashboard-native section:
  - KPI dictionary
  - top alerts
  - decision gates
  - normalized dimension rows

11. `api.py`
- Exposes HTTP surface for external clients.
- Enforces API-key authentication.
- Provides `health` and `analyze` endpoints.
- Returns stable envelope with request metadata + full result payload.

## Data model

All output contracts are shaped by dataclasses in `models.py` and serialized via `AgentResult.to_dict()`.
This enforces consistency between CLI, API, and dashboard ingestion.

## AI refinement boundary

AI refinement is optional and bounded by schema parsing/validation.
The deterministic engine remains the source of truth for pipeline completion.

## Failure behavior

- Source unavailable/blocked: deterministic ingestion errors with clear failure semantics.
- Market provider outages: partial market snapshot with notes; no hard-fail.
- AI unavailable in `auto`: fallback to deterministic outputs.
- AI unavailable in `ai`: explicit failure.
- API auth failure: explicit `401` with no pipeline execution.

## Extensibility points

- Add new diligence dimensions in `research.py` + `risk_engine.py` + `narrative.py`.
- Add providers in `market_data.py` and `fundraising.py`.
- Add downstream adapters (REST, Kafka, warehouse) from `AgentResult.to_dict()`.

## Planned protocol integration

See `docs/PROTOCOL_INTEGRATIONS.md` for x402 on MegaETH rollout design and boundaries.

