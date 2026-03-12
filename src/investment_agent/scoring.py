from __future__ import annotations

from .models import InvestmentScore, ResearchFinding, ScoreContribution


class InvestmentScorer:
    def __init__(self, weights: dict[str, float]):
        self._weights = weights

    def score(self, findings: list[ResearchFinding]) -> InvestmentScore:
        weighted_total = 0.0
        confidence_total = 0.0
        used_weight = 0.0
        contributions: list[ScoreContribution] = []

        for finding in findings:
            weight = self._weights.get(finding.dimension, finding.weight)
            if weight <= 0:
                continue

            weighted_score = finding.score * weight
            weighted_confidence = finding.confidence * weight
            weighted_total += weighted_score
            confidence_total += weighted_confidence
            used_weight += weight

            contributions.append(
                ScoreContribution(
                    dimension=finding.dimension,
                    weight=weight,
                    weighted_score=weighted_score,
                    weighted_confidence=weighted_confidence,
                    rationale=finding.rationale,
                )
            )

        if used_weight == 0:
            return InvestmentScore(
                value=0.5,
                confidence=0.0,
                rationale="No weighted findings available. Assigned neutral fallback score 0.500.",
                contributions=[],
            )

        final_value = max(0.0, min(1.0, weighted_total / used_weight))
        final_confidence = max(0.0, min(1.0, confidence_total / used_weight))
        rationale = (
            f"Final score computed as weighted average across {len(contributions)} dimensions. "
            f"Total weighted score={weighted_total:.3f}, normalized={final_value:.3f}."
        )
        return InvestmentScore(
            value=final_value,
            confidence=final_confidence,
            rationale=rationale,
            contributions=contributions,
        )