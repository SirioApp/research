# Research Basis

The framework follows recurring diligence priorities from leading VC/web3 research and is adapted into a deterministic scoring + risk architecture.

## Themes reflected in the model
- Decentralization quality and governance attack surface.
- Token incentive design and long-term alignment.
- Security posture and exploit resilience.
- Regulatory/legal risk management for tokenized networks.
- Team execution quality and transparency.
- Product traction quality, not only top-line growth.
- Treasury discipline and runway resilience.

## Primary references
- a16z crypto decentralization framework:
  https://a16zcrypto.com/posts/article/web3-decentralization-models-framework-principles-how-to/
- a16z token design principles:
  https://a16zcrypto.com/posts/article/designing-tokens-sanity-checks-principles-guidance/
- a16z DAO governance attacks:
  https://a16zcrypto.com/posts/article/dao-governance-attacks-and-how-to-avoid-them/
- a16z state of crypto report:
  https://a16zcrypto.com/posts/article/state-of-crypto-report-2024/
- Paradigm DAO legal options:
  https://www.paradigm.xyz/2022/06/legal-options-for-daos
- Paradigm DAO entity matrix:
  https://daos.paradigm.xyz/
- Sequoia adaptation/capital discipline:
  https://www.sequoiacap.com/article/adapting-to-endure/

## Live market inputs used by the engine
- CoinGecko API (prices + global market data)
- DefiLlama API/pages (TVL, stablecoins, raises snapshot)
- Alternative.me Fear & Greed index

These references and feeds shape methodology; final decisions still require primary diligence and specialist review.

## Scoring robustness controls
- Sentence-level evidence counting (not raw token frequency) to reduce keyword stuffing bias.
- Support-based shrinkage toward neutral when evidence depth is low.
- Conservative baselines on risk-sensitive dimensions (`regulatory_compliance`, `technology_security`, `team_execution`) when explicit evidence is missing.
- Confidence bounded by support strength, term diversity, and source diversity.

