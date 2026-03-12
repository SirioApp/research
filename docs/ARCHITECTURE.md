# Architecture

## High-level flow
1. Ingestion
   - Reads URLs and local files.
   - Handles rate-limit scenarios with retry/backoff/fallback.
2. Research scoring
   - Applies deterministic multi-dimension signal engine.
3. Risk modeling
   - Builds risk register with severity decomposition.
4. Team analysis
   - Computes team quality sub-scores and open questions.
5. Market context
   - Pulls live market and macro-crypto metrics.
6. Fundraising context
   - Detects raise signals and benchmarks difficulty.
7. Narrative + memo
   - Produces IC-style summary and recommendation.
8. Dashboard payload
   - Exports KPI and table-oriented structures.

## Main modules
- `ingestion.py`
- `research.py`
- `scoring.py`
- `risk_engine.py`
- `team_engine.py`
- `market_data.py`
- `fundraising.py`
- `narrative.py`
- `dashboard.py`
- `agent.py`
- `cli.py`

## Design principles
- Deterministic core logic first.
- AI as optional refinement layer.
- Explicit risk ownership and actionability.
- Output model optimized for downstream systems.
