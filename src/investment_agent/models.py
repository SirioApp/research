from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SourceDocument:
    source: str
    text: str


@dataclass(slots=True)
class EvidenceItem:
    term: str
    count: int
    polarity: str


@dataclass(slots=True)
class ResearchFinding:
    dimension: str
    score: float
    confidence: float
    weight: float
    positive_hits: int
    negative_hits: int
    evidence_items: list[EvidenceItem]
    rationale: str
    analysis: str = ""
    key_questions: list[str] | None = None


@dataclass(slots=True)
class ScoreContribution:
    dimension: str
    weight: float
    weighted_score: float
    weighted_confidence: float
    rationale: str


@dataclass(slots=True)
class InvestmentScore:
    value: float
    confidence: float
    rationale: str
    contributions: list[ScoreContribution]


@dataclass(slots=True)
class RiskItem:
    dimension: str
    probability: float
    impact: float
    severity: float
    category: str
    rationale: str
    mitigation: str
    owner: str
    timeframe: str


@dataclass(slots=True)
class TeamAssessment:
    overall_score: float
    confidence: float
    founder_visibility_score: float
    execution_track_record_score: float
    domain_expertise_score: float
    hiring_signal_score: float
    governance_trust_score: float
    strengths: list[str]
    concerns: list[str]
    open_questions: list[str]


@dataclass(slots=True)
class MarketSnapshot:
    as_of_utc: str
    regime: str
    btc_price_usd: float | None
    btc_24h_change_pct: float | None
    eth_price_usd: float | None
    eth_24h_change_pct: float | None
    total_market_cap_usd: float | None
    total_volume_24h_usd: float | None
    btc_dominance_pct: float | None
    defi_tvl_usd: float | None
    stablecoin_mcap_usd: float | None
    fear_greed_index: int | None
    fear_greed_label: str | None
    notes: list[str]


@dataclass(slots=True)
class FundraisingContext:
    defillama_total_funding_rounds: int | None
    defillama_total_funding_amount_usd: float | None
    project_detected_raise_usd: float | None
    project_detected_round_type: str | None
    benchmark_raise_range_usd: dict[str, float] | None
    raise_to_benchmark_ratio: float | None
    raising_difficulty_score: float
    commentary: str
    notes: list[str]


@dataclass(slots=True)
class ProjectAssessment:
    strengths: list[str]
    risks: list[str]
    next_checks: list[str]
    red_flags: list[str]
    potential_catalysts: list[str]


@dataclass(slots=True)
class InvestmentMemo:
    summary: str
    bull_case: str
    bear_case: str
    decision_statement: str


@dataclass(slots=True)
class DashboardData:
    generated_at_utc: str
    kpis: dict[str, Any]
    top_alerts: list[str]
    decision_gates: list[str]
    dimension_rows: list[dict[str, Any]]


@dataclass(slots=True)
class AgentResult:
    score: InvestmentScore
    findings: list[ResearchFinding]
    sources: list[str]
    executive_summary: str
    recommendation: str
    project_assessment: ProjectAssessment
    risk_register: list[RiskItem]
    investment_memo: InvestmentMemo
    team_assessment: TeamAssessment
    market_snapshot: MarketSnapshot
    fundraising_context: FundraisingContext
    dashboard: DashboardData

    def to_dict(self) -> dict:
        return {
            "score": {
                "value": self.score.value,
                "confidence": self.score.confidence,
                "rationale": self.score.rationale,
                "contributions": [
                    {
                        "dimension": item.dimension,
                        "weight": item.weight,
                        "weighted_score": item.weighted_score,
                        "weighted_confidence": item.weighted_confidence,
                        "rationale": item.rationale,
                    }
                    for item in self.score.contributions
                ],
            },
            "executive_summary": self.executive_summary,
            "recommendation": self.recommendation,
            "project_assessment": {
                "strengths": self.project_assessment.strengths,
                "risks": self.project_assessment.risks,
                "next_checks": self.project_assessment.next_checks,
                "red_flags": self.project_assessment.red_flags,
                "potential_catalysts": self.project_assessment.potential_catalysts,
            },
            "risk_register": [
                {
                    "dimension": risk.dimension,
                    "probability": risk.probability,
                    "impact": risk.impact,
                    "severity": risk.severity,
                    "category": risk.category,
                    "rationale": risk.rationale,
                    "mitigation": risk.mitigation,
                    "owner": risk.owner,
                    "timeframe": risk.timeframe,
                }
                for risk in self.risk_register
            ],
            "investment_memo": {
                "summary": self.investment_memo.summary,
                "bull_case": self.investment_memo.bull_case,
                "bear_case": self.investment_memo.bear_case,
                "decision_statement": self.investment_memo.decision_statement,
            },
            "team_assessment": {
                "overall_score": self.team_assessment.overall_score,
                "confidence": self.team_assessment.confidence,
                "founder_visibility_score": self.team_assessment.founder_visibility_score,
                "execution_track_record_score": self.team_assessment.execution_track_record_score,
                "domain_expertise_score": self.team_assessment.domain_expertise_score,
                "hiring_signal_score": self.team_assessment.hiring_signal_score,
                "governance_trust_score": self.team_assessment.governance_trust_score,
                "strengths": self.team_assessment.strengths,
                "concerns": self.team_assessment.concerns,
                "open_questions": self.team_assessment.open_questions,
            },
            "market_snapshot": {
                "as_of_utc": self.market_snapshot.as_of_utc,
                "regime": self.market_snapshot.regime,
                "btc_price_usd": self.market_snapshot.btc_price_usd,
                "btc_24h_change_pct": self.market_snapshot.btc_24h_change_pct,
                "eth_price_usd": self.market_snapshot.eth_price_usd,
                "eth_24h_change_pct": self.market_snapshot.eth_24h_change_pct,
                "total_market_cap_usd": self.market_snapshot.total_market_cap_usd,
                "total_volume_24h_usd": self.market_snapshot.total_volume_24h_usd,
                "btc_dominance_pct": self.market_snapshot.btc_dominance_pct,
                "defi_tvl_usd": self.market_snapshot.defi_tvl_usd,
                "stablecoin_mcap_usd": self.market_snapshot.stablecoin_mcap_usd,
                "fear_greed_index": self.market_snapshot.fear_greed_index,
                "fear_greed_label": self.market_snapshot.fear_greed_label,
                "notes": self.market_snapshot.notes,
            },
            "fundraising_context": {
                "defillama_total_funding_rounds": self.fundraising_context.defillama_total_funding_rounds,
                "defillama_total_funding_amount_usd": self.fundraising_context.defillama_total_funding_amount_usd,
                "project_detected_raise_usd": self.fundraising_context.project_detected_raise_usd,
                "project_detected_round_type": self.fundraising_context.project_detected_round_type,
                "benchmark_raise_range_usd": self.fundraising_context.benchmark_raise_range_usd,
                "raise_to_benchmark_ratio": self.fundraising_context.raise_to_benchmark_ratio,
                "raising_difficulty_score": self.fundraising_context.raising_difficulty_score,
                "commentary": self.fundraising_context.commentary,
                "notes": self.fundraising_context.notes,
            },
            "dashboard": {
                "generated_at_utc": self.dashboard.generated_at_utc,
                "kpis": self.dashboard.kpis,
                "top_alerts": self.dashboard.top_alerts,
                "decision_gates": self.dashboard.decision_gates,
                "dimension_rows": self.dashboard.dimension_rows,
            },
            "findings": [
                {
                    "dimension": item.dimension,
                    "score": item.score,
                    "confidence": item.confidence,
                    "weight": item.weight,
                    "positive_hits": item.positive_hits,
                    "negative_hits": item.negative_hits,
                    "rationale": item.rationale,
                    "analysis": item.analysis,
                    "key_questions": item.key_questions or [],
                    "evidence_items": [
                        {
                            "term": evidence.term,
                            "count": evidence.count,
                            "polarity": evidence.polarity,
                        }
                        for evidence in item.evidence_items
                    ],
                }
                for item in self.findings
            ],
            "sources": self.sources,
        }
