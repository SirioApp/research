from __future__ import annotations

from .models import (
    FundraisingContext,
    InvestmentMemo,
    InvestmentScore,
    MarketSnapshot,
    ProjectAssessment,
    ResearchFinding,
    RiskItem,
    TeamAssessment,
)


class NarrativeEngine:
    _labels = {
        "team_execution": "Team & Execution",
        "market_opportunity": "Market Opportunity",
        "product_traction": "Product & Traction",
        "technology_security": "Technology & Security",
        "tokenomics_incentives": "Tokenomics & Incentives",
        "governance_decentralization": "Governance & Decentralization",
        "regulatory_compliance": "Regulatory & Compliance",
        "financial_sustainability": "Financial Sustainability",
        "ecosystem_moat": "Ecosystem & Moat",
    }

    def build_dimension_analysis(self, finding: ResearchFinding) -> str:
        positives = [x for x in finding.evidence_items if x.polarity == "positive"]
        negatives = [x for x in finding.evidence_items if x.polarity == "negative"]
        pos_text = ", ".join(f"{x.term} ({x.count})" for x in positives[:5]) or "none"
        neg_text = ", ".join(f"{x.term} ({x.count})" for x in negatives[:5]) or "none"

        return (
            f"{self._label(finding.dimension)} underwrites at score {finding.score:.3f} (confidence {finding.confidence:.3f}). "
            f"Positive signal cluster: {pos_text}. Negative signal cluster: {neg_text}. "
            f"Dimension weight={finding.weight:.2f}; downside should be treated as material if this score remains below 0.50."
        )

    def build_executive_summary(
        self,
        findings: list[ResearchFinding],
        score: InvestmentScore,
        team: TeamAssessment,
        market: MarketSnapshot,
        funding: FundraisingContext,
    ) -> str:
        weakest = sorted(findings, key=lambda x: x.score)[:3]
        weak_text = ", ".join(self._label(x.dimension) for x in weakest)
        return (
            f"Underwritten score is {score.value:.3f} with confidence {score.confidence:.3f}. "
            f"Team score is {team.overall_score:.3f}. Current market regime is {market.regime}. "
            f"Fundraising difficulty score is {funding.raising_difficulty_score:.3f}. "
            f"Main diligence pressure points are {weak_text}."
        )

    def build_recommendation(
        self,
        score: InvestmentScore,
        risks: list[RiskItem],
        team: TeamAssessment,
        funding: FundraisingContext,
    ) -> str:
        max_risk = max((r.severity for r in risks), default=0.0)
        if score.value >= 0.75 and score.confidence >= 0.60 and max_risk < 0.50 and team.overall_score >= 0.65:
            return "Invest"
        if score.value >= 0.58 and max_risk < 0.72 and team.overall_score >= 0.50:
            return "Conditional invest after targeted diligence"
        if funding.raising_difficulty_score >= 0.75:
            return "Hold; reassess after market/fundraising conditions improve"
        return "Do not invest yet"

    def build_project_assessment(
        self,
        findings: list[ResearchFinding],
        risks: list[RiskItem],
        team: TeamAssessment,
    ) -> ProjectAssessment:
        ordered = sorted(findings, key=lambda x: x.score)
        strengths = [f"{self._label(x.dimension)} score {x.score:.3f}" for x in reversed(ordered[-3:])]
        risk_lines = [f"{self._label(r.dimension)} severity {r.severity:.3f}: {r.rationale}" for r in risks[:4]]
        next_checks = [f"{self._label(r.dimension)}: {r.mitigation}" for r in risks[:5]]

        red_flags = [
            f"{self._label(r.dimension)} unresolved severity {r.severity:.3f}"
            for r in risks
            if r.severity >= 0.70
        ]
        if team.overall_score < 0.5:
            red_flags.append("Team quality confidence is below institutional threshold.")

        catalysts = [
            "Independent audit publication with resolved critical findings.",
            "Sustained user/revenue growth over two consecutive quarters.",
            "Improved governance decentralization and transparency controls.",
            "Demonstrated runway extension or non-dilutive treasury strategy.",
        ]

        return ProjectAssessment(
            strengths=strengths,
            risks=risk_lines,
            next_checks=next_checks,
            red_flags=red_flags,
            potential_catalysts=catalysts,
        )

    def build_investment_memo(
        self,
        findings: list[ResearchFinding],
        score: InvestmentScore,
        recommendation: str,
        risks: list[RiskItem],
        team: TeamAssessment,
        market: MarketSnapshot,
        funding: FundraisingContext,
    ) -> InvestmentMemo:
        top = sorted(findings, key=lambda x: x.score, reverse=True)[:2]
        bottom = sorted(findings, key=lambda x: x.score)[:2]

        top_text = ", ".join(self._label(x.dimension) for x in top) or "no clear strengths"
        bottom_text = ", ".join(self._label(x.dimension) for x in bottom) or "insufficient evidence"

        summary = (
            "Committee-style underwriting across execution, market, security, tokenomics, governance, "
            "regulatory, and financial resilience dimensions."
        )
        bull_case = (
            f"If {top_text} continue to strengthen and execution remains disciplined, the project can compound into "
            "defensible category leadership."
        )
        bear_case = (
            f"If {bottom_text} remain unresolved, downside can materialize through adoption slowdown, governance fragility, "
            "or capital impairment."
        )
        decision = (
            f"Recommendation: {recommendation}. Score={score.value:.3f}, confidence={score.confidence:.3f}, "
            f"team={team.overall_score:.3f}, market_regime={market.regime}, raising_difficulty={funding.raising_difficulty_score:.3f}, "
            f"max_risk={max((r.severity for r in risks), default=0.0):.3f}."
        )

        return InvestmentMemo(
            summary=summary,
            bull_case=bull_case,
            bear_case=bear_case,
            decision_statement=decision,
        )

    def apply_key_questions(self, finding: ResearchFinding) -> list[str]:
        mapping = {
            "team_execution": [
                "What independently verified outcomes has the core team shipped in the last 12 months?",
                "What is the succession plan for key contributors?",
            ],
            "technology_security": [
                "What critical audit findings remain unresolved?",
                "What is the incident-response process and disclosure standard?",
            ],
            "tokenomics_incentives": [
                "How do unlocks impact sell pressure under low-liquidity conditions?",
                "Is value accrual to token holders structurally durable?",
            ],
            "regulatory_compliance": [
                "What jurisdictions materially increase enforcement risk?",
                "Is there legal structuring for token issuance and governance?",
            ],
        }
        return mapping.get(finding.dimension, [
            "What primary data would materially improve confidence in this dimension?",
            "What falsifies the current underwriting assumption?",
        ])

    def _label(self, dimension: str) -> str:
        return self._labels.get(dimension, dimension)
