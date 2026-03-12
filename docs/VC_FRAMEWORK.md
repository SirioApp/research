# VC Framework (Web3 Focus)

This framework implements downside-first underwriting adapted to web3 market structure.

## Dimension model

The engine underwrites nine dimensions:
1. Team & Execution
2. Market Opportunity
3. Product & Traction
4. Technology & Security
5. Tokenomics & Incentives
6. Governance & Decentralization
7. Regulatory & Compliance
8. Financial Sustainability
9. Ecosystem & Moat

Each dimension includes:
- raw signal counts (positive/negative term clusters)
- normalized `score` in `[0,1]`
- normalized `confidence` in `[0,1]`
- portfolio weight contribution
- analyst key questions

## Scoring math

For each dimension `d`:
- `evidence_d = positive_hits_d + negative_hits_d`
- if `evidence_d == 0`: `score_d = 0.5` and low baseline confidence
- else:
  - `raw_d = (positive_hits_d - negative_hits_d) / evidence_d`
  - `score_d = (raw_d + 1) / 2`

Portfolio score:
- `base_score = sum(score_d * weight_d)`
- `base_confidence = sum(confidence_d * weight_d)`

Context-adjusted score then applies penalties for:
- weak team quality
- elevated risk register severities
- harsh fundraising conditions
- risk-off market regime

## Risk model

For each dimension:
- `probability_d = g(1-score_d, 1-confidence_d)`
- `impact_d = static criticality coefficient`
- `severity_d = probability_d * impact_d`

Register entries include:
- category
- rationale
- mitigation
- owner
- action timeframe

## Team underwriting model

The team model is explicit and scored independently:
- founder visibility
- execution track record
- domain expertise
- hiring signal
- governance trust

This prevents the aggregate score from masking team fragility.

## Fundraising model

Fundraising context computes:
- detected raise amount
- detected round type
- benchmark range mapping
- raise-to-benchmark ratio
- raising difficulty score

This is integrated into final decisioning, not treated as cosmetic metadata.

## Decision labels

Recommendation is produced from a rule-based policy over:
- adjusted score
- confidence
- maximum residual risk severity
- team quality
- raising difficulty

Labels:
- `Invest`
- `Conditional invest after targeted diligence`
- `Hold; reassess after market/fundraising conditions improve`
- `Do not invest yet`


## Near-term roadmap note
Protocol-level gating is planned through x402 on MegaETH (see docs/PROTOCOL_INTEGRATIONS.md). This does not change the deterministic underwriting math; it controls execution entitlement for advanced modes.

