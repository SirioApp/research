# VC Framework (Web3 Focus)

This project applies a downside-first underwriting workflow inspired by institutional crypto diligence.

## Dimension stack

1. Team & Execution
2. Market Opportunity
3. Product & Traction
4. Technology & Security
5. Tokenomics & Incentives
6. Governance & Decentralization
7. Regulatory & Compliance
8. Financial Sustainability
9. Ecosystem & Moat

Each dimension has:
- quantitative score (0..1)
- confidence score (0..1)
- weighted contribution to final score
- evidence-term breakdown
- analyst questions for deeper diligence

## Risk methodology

For each dimension:
- `probability` from low score + low confidence
- `impact` from dimension criticality
- `severity = probability * impact`

`risk_register` includes category, mitigation, owner, and action timeframe.

## Team underwriting

Team quality is scored separately with sub-scores:
- founder visibility
- execution track record
- domain expertise
- hiring signal
- governance trust

## Market + fundraising context

Live external context is added from:
- CoinGecko (prices + global market stats)
- DefiLlama (DeFi TVL + stablecoin supply + raises page snapshot)
- Fear & Greed index

A dedicated fundraising model estimates:
- detected raise amount
- round type
- benchmark ratio
- raising difficulty score

## Dashboard readiness

The output includes a dedicated `dashboard` section with:
- top KPIs
- top alerts
- decision gates
- dimension table rows

This is designed to feed BI tools or a custom web dashboard directly.
