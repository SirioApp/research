from __future__ import annotations

from .models import ResearchFinding, RiskItem


class RiskEngine:
    _impact_map = {
        "team_execution": 0.92,
        "market_opportunity": 0.82,
        "product_traction": 0.88,
        "technology_security": 0.95,
        "tokenomics_incentives": 0.93,
        "governance_decentralization": 0.78,
        "regulatory_compliance": 0.92,
        "financial_sustainability": 0.85,
        "ecosystem_moat": 0.72,
    }

    _category_map = {
        "team_execution": "execution",
        "market_opportunity": "market",
        "product_traction": "product",
        "technology_security": "security",
        "tokenomics_incentives": "tokenomics",
        "governance_decentralization": "governance",
        "regulatory_compliance": "regulatory",
        "financial_sustainability": "finance",
        "ecosystem_moat": "competition",
    }

    _owner_map = {
        "team_execution": "Founders",
        "market_opportunity": "Go-to-market lead",
        "product_traction": "Product lead",
        "technology_security": "CTO / Security lead",
        "tokenomics_incentives": "Token design lead",
        "governance_decentralization": "Governance lead",
        "regulatory_compliance": "Legal / Compliance",
        "financial_sustainability": "CFO / Finance",
        "ecosystem_moat": "Partnerships / Strategy",
    }

    _mitigation_map = {
        "team_execution": "Verify founder-track record, execution cadence, and hiring quality over multiple quarters.",
        "market_opportunity": "Validate TAM and willingness-to-pay with customer interviews and conversion data.",
        "product_traction": "Require retention cohorts and on-chain/off-chain usage consistency.",
        "technology_security": "Require independent audits, bounty evidence, and incident transparency.",
        "tokenomics_incentives": "Stress-test emissions, unlock schedule, and holder concentration.",
        "governance_decentralization": "Review governance rights, upgrade keys, and control concentration.",
        "regulatory_compliance": "Obtain jurisdiction-specific legal memo and compliance controls.",
        "financial_sustainability": "Audit runway assumptions, treasury policy, and burn trajectory.",
        "ecosystem_moat": "Assess defensibility: integrations, switching costs, and distribution advantage.",
    }

    def build_risk_register(self, findings: list[ResearchFinding], top_n: int = 8) -> list[RiskItem]:
        items: list[RiskItem] = []

        for finding in findings:
            probability = self._clamp((1.0 - finding.score) * 0.65 + (1.0 - finding.confidence) * 0.35)
            impact = self._impact_map.get(finding.dimension, 0.75)
            severity = self._clamp(probability * impact)

            negatives = [ev for ev in finding.evidence_items if ev.polarity == "negative"]
            if negatives:
                neg_terms = ", ".join(f"{ev.term} ({ev.count})" for ev in negatives[:3])
                rationale = f"Negative evidence concentration: {neg_terms}."
            else:
                rationale = "Sparse negative evidence, but confidence remains constrained by limited data depth."

            category = self._category_map.get(finding.dimension, "general")
            owner = self._owner_map.get(finding.dimension, "Core team")
            mitigation = self._mitigation_map.get(
                finding.dimension,
                "Collect higher-quality evidence and re-underwrite this dimension.",
            )
            timeframe = "before term sheet" if severity >= 0.60 else "pre-deployment"

            items.append(
                RiskItem(
                    dimension=finding.dimension,
                    probability=probability,
                    impact=impact,
                    severity=severity,
                    category=category,
                    rationale=rationale,
                    mitigation=mitigation,
                    owner=owner,
                    timeframe=timeframe,
                )
            )

        items.sort(key=lambda item: item.severity, reverse=True)
        return items[:top_n]

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
