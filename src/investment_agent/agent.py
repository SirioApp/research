from __future__ import annotations

import os

from .ai_refiner import AIRefinerError, OpenAIInvestmentRefiner
from .dashboard import DashboardBuilder
from .fundraising import FundraisingContextProvider
from .ingestion import SourceIngestor
from .market_data import MarketDataProvider
from .models import AgentResult, FundraisingContext, InvestmentScore, MarketSnapshot, RiskItem, TeamAssessment
from .narrative import NarrativeEngine
from .research import ResearchEngine
from .risk_engine import RiskEngine
from .scoring import InvestmentScorer
from .team_engine import TeamEngine


class InvestmentResearchAgent:
    def __init__(
        self,
        mode: str = "auto",
        model: str = "gpt-4.1-mini",
        api_key: str | None = None,
    ) -> None:
        self._mode = mode
        self._model = model
        self._api_key = api_key

        self._ingestor = SourceIngestor()
        self._research_engine = ResearchEngine()
        self._scorer = InvestmentScorer(self._research_engine.weights)
        self._risk_engine = RiskEngine()
        self._team_engine = TeamEngine()
        self._market_provider = MarketDataProvider()
        self._fundraising_provider = FundraisingContextProvider()
        self._narrative_engine = NarrativeEngine()
        self._dashboard_builder = DashboardBuilder()

    def run(self, sources: list[str]) -> AgentResult:
        documents = self._ingestor.ingest(sources)
        findings = self._research_engine.analyze(documents)

        for finding in findings:
            finding.analysis = self._narrative_engine.build_dimension_analysis(finding)
            finding.key_questions = self._narrative_engine.apply_key_questions(finding)

        market_snapshot = self._market_provider.fetch()
        team_assessment = self._team_engine.evaluate(documents, findings)
        base_score = self._scorer.score(findings)
        risk_register = self._risk_engine.build_risk_register(findings)
        fundraising_context = self._fundraising_provider.build(documents, market_snapshot)

        score = self._apply_context_adjustments(base_score, team_assessment, fundraising_context, market_snapshot, risk_register)

        recommendation = self._narrative_engine.build_recommendation(score, risk_register, team_assessment, fundraising_context)
        executive_summary = self._narrative_engine.build_executive_summary(
            findings,
            score,
            team_assessment,
            market_snapshot,
            fundraising_context,
        )
        project_assessment = self._narrative_engine.build_project_assessment(findings, risk_register, team_assessment)
        investment_memo = self._narrative_engine.build_investment_memo(
            findings,
            score,
            recommendation,
            risk_register,
            team_assessment,
            market_snapshot,
            fundraising_context,
        )

        if self._resolve_ai_mode():
            findings, executive_summary, recommendation, project_assessment, risk_register, investment_memo, team_assessment, fundraising_context = self._run_ai_refinement(
                documents,
                findings,
                risk_register,
                team_assessment,
                market_snapshot,
                fundraising_context,
                fallback=(executive_summary, recommendation, project_assessment, investment_memo),
            )
            base_score = self._scorer.score(findings)
            score = self._apply_context_adjustments(base_score, team_assessment, fundraising_context, market_snapshot, risk_register)

        dashboard = self._dashboard_builder.build(
            score=score,
            findings=findings,
            risk_register=risk_register,
            team=team_assessment,
            fundraising=fundraising_context,
            market_regime=market_snapshot.regime,
            fear_greed_index=market_snapshot.fear_greed_index,
        )

        return AgentResult(
            score=score,
            findings=findings,
            sources=[item.source for item in documents],
            executive_summary=executive_summary,
            recommendation=recommendation,
            project_assessment=project_assessment,
            risk_register=risk_register,
            investment_memo=investment_memo,
            team_assessment=team_assessment,
            market_snapshot=market_snapshot,
            fundraising_context=fundraising_context,
            dashboard=dashboard,
        )

    def _resolve_ai_mode(self) -> bool:
        if self._mode == "rules":
            return False
        if self._mode == "ai":
            return True
        return bool(self._api_key or os.getenv("OPENAI_API_KEY"))

    def _run_ai_refinement(
        self,
        documents,
        findings,
        risk_register,
        team_assessment,
        market_snapshot,
        fundraising_context,
        fallback,
    ):
        fallback_summary, fallback_recommendation, fallback_assessment, fallback_memo = fallback
        try:
            refiner = OpenAIInvestmentRefiner(model=self._model, api_key=self._api_key)
            return refiner.refine(
                documents,
                findings,
                risk_register,
                team_assessment,
                market_snapshot,
                fundraising_context,
            )
        except AIRefinerError as exc:
            if self._mode == "ai":
                raise
            fallback_summary = f"{fallback_summary} AI refinement unavailable ({exc})."
            return (
                findings,
                fallback_summary,
                fallback_recommendation,
                fallback_assessment,
                risk_register,
                fallback_memo,
                team_assessment,
                fundraising_context,
            )

    @staticmethod
    def _apply_context_adjustments(
        base_score: InvestmentScore,
        team: TeamAssessment,
        funding: FundraisingContext,
        market: MarketSnapshot,
        risks: list[RiskItem],
    ) -> InvestmentScore:
        max_risk = max((item.severity for item in risks), default=0.0)
        avg_risk = sum(item.severity for item in risks) / max(1, len(risks))

        team_penalty = max(0.0, 0.60 - team.overall_score) * 0.18
        risk_penalty = max_risk * 0.20 + avg_risk * 0.10
        funding_penalty = max(0.0, funding.raising_difficulty_score - 0.50) * 0.14
        market_penalty = 0.04 if market.regime == "risk_off" else 0.0

        total_penalty = team_penalty + risk_penalty + funding_penalty + market_penalty
        adjusted_value = max(0.0, min(1.0, base_score.value - total_penalty))
        adjusted_conf = max(0.0, min(1.0, min(base_score.confidence, team.confidence + 0.15)))

        rationale = (
            f"Base score {base_score.value:.3f} adjusted by context penalties: team={team_penalty:.3f}, "
            f"risk={risk_penalty:.3f}, funding={funding_penalty:.3f}, market={market_penalty:.3f}; "
            f"final score {adjusted_value:.3f}."
        )

        return InvestmentScore(
            value=adjusted_value,
            confidence=adjusted_conf,
            rationale=rationale,
            contributions=base_score.contributions,
        )
