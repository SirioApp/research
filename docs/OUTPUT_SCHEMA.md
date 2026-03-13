# Output Schema

The agent returns a single JSON object with these top-level sections.

## 1) score
- `value` (float 0..1)
- `confidence` (float 0..1)
- `rationale` (string)
- `contributions[]`
  - `dimension`
  - `weight`
  - `weighted_score`
  - `weighted_confidence`
  - `rationale`

## 2) executive_summary
- Summary paragraph for committee-level overview.

## 3) recommendation
- Decision label: e.g. `Invest`, `Conditional invest after targeted diligence`, `Do not invest yet`.

## 4) project_profile
- `name`
- `description`
- `website`
- `category`
- `sector_tags[]`
- `stage`
- `token_symbol`
- `chain_focus[]`
- `social_links` (dictionary by platform)
- `key_claims[]`
- `data_quality`
  - `completeness_score`
  - `missing_fields[]`
  - `source_count`

## 5) project_assessment
- `strengths[]`
- `risks[]`
- `next_checks[]`
- `red_flags[]`
- `potential_catalysts[]`

## 6) risk_register[]
For each risk item:
- `dimension`
- `probability` (0..1)
- `impact` (0..1)
- `severity` (0..1)
- `category`
- `rationale`
- `mitigation`
- `owner`
- `timeframe`

## 7) investment_memo
- `summary`
- `bull_case`
- `bear_case`
- `decision_statement`

## 8) team_assessment
- `overall_score`
- `confidence`
- `founder_visibility_score`
- `execution_track_record_score`
- `domain_expertise_score`
- `hiring_signal_score`
- `governance_trust_score`
- `strengths[]`
- `concerns[]`
- `open_questions[]`

## 9) market_snapshot
- `as_of_utc`
- `regime`
- `btc_price_usd`
- `btc_24h_change_pct`
- `eth_price_usd`
- `eth_24h_change_pct`
- `total_market_cap_usd`
- `total_volume_24h_usd`
- `btc_dominance_pct`
- `defi_tvl_usd`
- `stablecoin_mcap_usd`
- `fear_greed_index`
- `fear_greed_label`
- `notes[]`

## 10) fundraising_context
- `defillama_total_funding_rounds`
- `defillama_total_funding_amount_usd`
- `project_detected_raise_usd`
- `project_detected_round_type`
- `benchmark_raise_range_usd`
- `raise_to_benchmark_ratio`
- `raising_difficulty_score`
- `commentary`
- `notes[]`

## 11) dashboard
- `generated_at_utc`
- `kpis` (flat metric dictionary)
- `top_alerts[]`
- `decision_gates[]`
- `dimension_rows[]`
  - `dimension`
  - `score`
  - `confidence`
  - `weight`
  - `positive_hits`
  - `negative_hits`
  - `risk_severity`
  - `analysis`

## 12) findings[]
For each underwriting dimension:
- `dimension`
- `score`
- `confidence`
- `weight`
- `positive_hits`
- `negative_hits`
- `rationale`
- `analysis`
- `key_questions[]`
- `evidence_items[]`
  - `term`
  - `count`
  - `polarity`

## 13) sources[]
- List of source URLs/files used in this run.
