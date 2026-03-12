from __future__ import annotations

from datetime import datetime, timezone

from .models import DashboardData, FundraisingContext, InvestmentScore, ResearchFinding, RiskItem, TeamAssessment


class DashboardBuilder:
    def build(
        self,
        score: InvestmentScore,
        findings: list[ResearchFinding],
        risk_register: list[RiskItem],
        team: TeamAssessment,
        fundraising: FundraisingContext,
        market_regime: str,
        fear_greed_index: int | None,
    ) -> DashboardData:
        kpis = {
            "investment_score": round(score.value, 4),
            "confidence": round(score.confidence, 4),
            "team_score": round(team.overall_score, 4),
            "max_risk_severity": round(max((r.severity for r in risk_register), default=0.0), 4),
            "avg_risk_severity": round(sum(r.severity for r in risk_register) / max(1, len(risk_register)), 4),
            "market_regime": market_regime,
            "fear_greed_index": fear_greed_index,
            "raising_difficulty_score": round(fundraising.raising_difficulty_score, 4),
            "detected_raise_usd": fundraising.project_detected_raise_usd,
            "detected_round_type": fundraising.project_detected_round_type,
        }

        top_alerts = self._alerts(risk_register, team, fundraising)
        decision_gates = self._decision_gates(risk_register, team)

        risk_map = {item.dimension: item for item in risk_register}
        dimension_rows = [
            {
                "dimension": finding.dimension,
                "score": finding.score,
                "confidence": finding.confidence,
                "weight": finding.weight,
                "positive_hits": finding.positive_hits,
                "negative_hits": finding.negative_hits,
                "risk_severity": risk_map.get(finding.dimension).severity if risk_map.get(finding.dimension) else None,
                "analysis": finding.analysis,
            }
            for finding in findings
        ]

        return DashboardData(
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            kpis=kpis,
            top_alerts=top_alerts,
            decision_gates=decision_gates,
            dimension_rows=dimension_rows,
        )

    @staticmethod
    def _alerts(risk_register: list[RiskItem], team: TeamAssessment, fundraising: FundraisingContext) -> list[str]:
        alerts: list[str] = []

        for risk in risk_register[:5]:
            if risk.severity >= 0.60:
                alerts.append(f"High severity risk in {risk.dimension}: {risk.severity:.3f}")

        if team.overall_score < 0.50:
            alerts.append("Team quality score is below threshold for institutional conviction.")

        if fundraising.raising_difficulty_score > 0.70:
            alerts.append("Fundraising environment appears difficult for this profile.")

        return alerts[:10]

    @staticmethod
    def _decision_gates(risk_register: list[RiskItem], team: TeamAssessment) -> list[str]:
        gates = [
            "No unresolved risk item above severity 0.70.",
            "Independent security review confirms acceptable threat surface.",
            "Team references and founder-track record are verified.",
            "Compliance posture is validated for target jurisdictions.",
        ]

        if team.overall_score < 0.50:
            gates.append("Require founder diligence call before any term-sheet discussion.")

        if any(item.dimension == "tokenomics_incentives" and item.severity >= 0.55 for item in risk_register):
            gates.append("Require token model stress-test and unlock impact scenario analysis.")

        return gates
