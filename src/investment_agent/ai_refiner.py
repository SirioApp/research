from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

from .models import (
    FundraisingContext,
    InvestmentMemo,
    MarketSnapshot,
    ProjectAssessment,
    ResearchFinding,
    RiskItem,
    SourceDocument,
    TeamAssessment,
)


class AIRefinerError(RuntimeError):
    pass


class OpenAIInvestmentRefiner:
    def __init__(self, model: str = "gpt-4.1-mini", api_key: str | None = None) -> None:
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise AIRefinerError("OPENAI_API_KEY is required for AI mode.")

    def refine(
        self,
        documents: list[SourceDocument],
        findings: list[ResearchFinding],
        risk_register: list[RiskItem],
        team_assessment: TeamAssessment,
        market_snapshot: MarketSnapshot,
        fundraising_context: FundraisingContext,
    ) -> tuple[
        list[ResearchFinding],
        str,
        str,
        ProjectAssessment,
        list[RiskItem],
        InvestmentMemo,
        TeamAssessment,
        FundraisingContext,
    ]:
        payload = self._build_payload(
            documents,
            findings,
            risk_register,
            team_assessment,
            market_snapshot,
            fundraising_context,
        )
        response = self._call_openai(payload)
        parsed = self._parse_response_to_json(response)

        by_dimension = {
            item.get("dimension", "").strip().lower(): item
            for item in parsed.get("dimensions", [])
            if isinstance(item, dict)
        }

        for finding in findings:
            item = by_dimension.get(finding.dimension.lower())
            if not item:
                continue
            finding.score = self._bounded_float(item.get("score"), finding.score)
            finding.confidence = self._bounded_float(item.get("confidence"), finding.confidence)
            if isinstance(item.get("rationale"), str) and item["rationale"].strip():
                finding.rationale = item["rationale"].strip()
            if isinstance(item.get("analysis"), str) and item["analysis"].strip():
                finding.analysis = item["analysis"].strip()
            if isinstance(item.get("key_questions"), list):
                finding.key_questions = [str(x) for x in item["key_questions"] if isinstance(x, str)]

        summary = self._safe_text(parsed.get("executive_summary"), "AI summary unavailable.")
        recommendation = self._safe_text(parsed.get("recommendation"), "Conditional invest after targeted diligence")
        assessment = self._parse_assessment(parsed.get("project_assessment"))
        risks = self._parse_risks(parsed.get("risk_register"), fallback=risk_register)
        memo = self._parse_memo(parsed.get("investment_memo"), recommendation)
        team = self._parse_team(parsed.get("team_assessment"), fallback=team_assessment)
        funding = self._parse_funding(parsed.get("fundraising_context"), fallback=fundraising_context)

        return findings, summary, recommendation, assessment, risks, memo, team, funding

    def _call_openai(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=90,
        )
        if response.status_code >= 400:
            raise AIRefinerError(f"OpenAI API error {response.status_code}: {response.text[:400]}")
        return response.json()

    def _build_payload(
        self,
        documents: list[SourceDocument],
        findings: list[ResearchFinding],
        risk_register: list[RiskItem],
        team_assessment: TeamAssessment,
        market_snapshot: MarketSnapshot,
        fundraising_context: FundraisingContext,
    ) -> dict[str, Any]:
        system_prompt = (
            "You are a partner-level web3 VC analyst. "
            "Write critical, evidence-based underwriting suitable for an investment committee. "
            "Avoid generic language and prioritize downside risk clarity."
        )

        source_inventory = [doc.source for doc in documents]
        findings_payload = [
            {
                "dimension": f.dimension,
                "score": f.score,
                "confidence": f.confidence,
                "weight": f.weight,
                "positive_hits": f.positive_hits,
                "negative_hits": f.negative_hits,
                "evidence_terms": [
                    {"term": e.term, "count": e.count, "polarity": e.polarity}
                    for e in f.evidence_items
                ],
            }
            for f in findings
        ]

        risk_payload = [
            {
                "dimension": r.dimension,
                "probability": r.probability,
                "impact": r.impact,
                "severity": r.severity,
                "category": r.category,
                "rationale": r.rationale,
                "mitigation": r.mitigation,
                "owner": r.owner,
                "timeframe": r.timeframe,
            }
            for r in risk_register
        ]

        team_payload = {
            "overall_score": team_assessment.overall_score,
            "confidence": team_assessment.confidence,
            "founder_visibility_score": team_assessment.founder_visibility_score,
            "execution_track_record_score": team_assessment.execution_track_record_score,
            "domain_expertise_score": team_assessment.domain_expertise_score,
            "hiring_signal_score": team_assessment.hiring_signal_score,
            "governance_trust_score": team_assessment.governance_trust_score,
            "strengths": team_assessment.strengths,
            "concerns": team_assessment.concerns,
            "open_questions": team_assessment.open_questions,
        }

        market_payload = {
            "regime": market_snapshot.regime,
            "btc_price_usd": market_snapshot.btc_price_usd,
            "btc_24h_change_pct": market_snapshot.btc_24h_change_pct,
            "eth_price_usd": market_snapshot.eth_price_usd,
            "eth_24h_change_pct": market_snapshot.eth_24h_change_pct,
            "total_market_cap_usd": market_snapshot.total_market_cap_usd,
            "total_volume_24h_usd": market_snapshot.total_volume_24h_usd,
            "btc_dominance_pct": market_snapshot.btc_dominance_pct,
            "defi_tvl_usd": market_snapshot.defi_tvl_usd,
            "stablecoin_mcap_usd": market_snapshot.stablecoin_mcap_usd,
            "fear_greed_index": market_snapshot.fear_greed_index,
            "fear_greed_label": market_snapshot.fear_greed_label,
        }

        funding_payload = {
            "defillama_total_funding_rounds": fundraising_context.defillama_total_funding_rounds,
            "defillama_total_funding_amount_usd": fundraising_context.defillama_total_funding_amount_usd,
            "project_detected_raise_usd": fundraising_context.project_detected_raise_usd,
            "project_detected_round_type": fundraising_context.project_detected_round_type,
            "benchmark_raise_range_usd": fundraising_context.benchmark_raise_range_usd,
            "raise_to_benchmark_ratio": fundraising_context.raise_to_benchmark_ratio,
            "raising_difficulty_score": fundraising_context.raising_difficulty_score,
            "commentary": fundraising_context.commentary,
        }

        schema = {
            "executive_summary": "string",
            "recommendation": "string",
            "project_assessment": {
                "strengths": ["string"],
                "risks": ["string"],
                "next_checks": ["string"],
                "red_flags": ["string"],
                "potential_catalysts": ["string"],
            },
            "team_assessment": {
                "overall_score": "number 0..1",
                "confidence": "number 0..1",
                "founder_visibility_score": "number 0..1",
                "execution_track_record_score": "number 0..1",
                "domain_expertise_score": "number 0..1",
                "hiring_signal_score": "number 0..1",
                "governance_trust_score": "number 0..1",
                "strengths": ["string"],
                "concerns": ["string"],
                "open_questions": ["string"],
            },
            "fundraising_context": {
                "raising_difficulty_score": "number 0..1",
                "commentary": "string",
                "notes": ["string"],
            },
            "risk_register": [
                {
                    "dimension": "string",
                    "probability": "number 0..1",
                    "impact": "number 0..1",
                    "severity": "number 0..1",
                    "category": "string",
                    "rationale": "string",
                    "mitigation": "string",
                    "owner": "string",
                    "timeframe": "string",
                }
            ],
            "investment_memo": {
                "summary": "string",
                "bull_case": "string",
                "bear_case": "string",
                "decision_statement": "string",
            },
            "dimensions": [
                {
                    "dimension": "string",
                    "score": "number 0..1",
                    "confidence": "number 0..1",
                    "rationale": "string",
                    "analysis": "string",
                    "key_questions": ["string"],
                }
            ],
        }

        user_prompt = (
            "Task: produce an analyst-grade web3 investment underwriting package.\n"
            "Rules:\n"
            "1) Prioritize downside clarity and risk realism.\n"
            "2) Be project-specific and grounded in source evidence and provided data.\n"
            "3) Keep all quantitative fields in [0,1] where requested.\n"
            f"Sources: {json.dumps(source_inventory, ensure_ascii=True)}\n"
            f"Dimension findings: {json.dumps(findings_payload, ensure_ascii=True)}\n"
            f"Risk register baseline: {json.dumps(risk_payload, ensure_ascii=True)}\n"
            f"Team baseline: {json.dumps(team_payload, ensure_ascii=True)}\n"
            f"Market snapshot: {json.dumps(market_payload, ensure_ascii=True)}\n"
            f"Fundraising context: {json.dumps(funding_payload, ensure_ascii=True)}\n"
            f"Return strict JSON only with this shape: {json.dumps(schema, ensure_ascii=True)}"
        )

        return {
            "model": self._model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

    def _parse_response_to_json(self, response: dict[str, Any]) -> dict[str, Any]:
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIRefinerError("Unexpected OpenAI response format.") from exc

        text = content if isinstance(content, str) else ""
        if not text:
            raise AIRefinerError("AI output is empty.")

        parsed = self._try_parse_json(text)
        if parsed is not None:
            return parsed

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise AIRefinerError("AI output is not valid JSON.")

        parsed = self._try_parse_json(match.group(0))
        if parsed is None:
            raise AIRefinerError("AI output is not valid JSON.")

        return parsed

    @staticmethod
    def _try_parse_json(text: str) -> dict[str, Any] | None:
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return None
        return obj if isinstance(obj, dict) else None

    @staticmethod
    def _parse_assessment(value: Any) -> ProjectAssessment:
        if not isinstance(value, dict):
            return ProjectAssessment(strengths=[], risks=[], next_checks=[], red_flags=[], potential_catalysts=[])
        return ProjectAssessment(
            strengths=[str(x) for x in value.get("strengths", []) if isinstance(x, str)],
            risks=[str(x) for x in value.get("risks", []) if isinstance(x, str)],
            next_checks=[str(x) for x in value.get("next_checks", []) if isinstance(x, str)],
            red_flags=[str(x) for x in value.get("red_flags", []) if isinstance(x, str)],
            potential_catalysts=[str(x) for x in value.get("potential_catalysts", []) if isinstance(x, str)],
        )

    @staticmethod
    def _parse_risks(value: Any, fallback: list[RiskItem]) -> list[RiskItem]:
        if not isinstance(value, list):
            return fallback

        out: list[RiskItem] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            dimension = item.get("dimension")
            if not isinstance(dimension, str):
                continue
            out.append(
                RiskItem(
                    dimension=dimension,
                    probability=OpenAIInvestmentRefiner._bounded_float(item.get("probability"), 0.5),
                    impact=OpenAIInvestmentRefiner._bounded_float(item.get("impact"), 0.5),
                    severity=OpenAIInvestmentRefiner._bounded_float(item.get("severity"), 0.5),
                    category=str(item.get("category") or "general"),
                    rationale=str(item.get("rationale") or ""),
                    mitigation=str(item.get("mitigation") or ""),
                    owner=str(item.get("owner") or "Core team"),
                    timeframe=str(item.get("timeframe") or "pre-deployment"),
                )
            )
        return out or fallback

    @staticmethod
    def _parse_team(value: Any, fallback: TeamAssessment) -> TeamAssessment:
        if not isinstance(value, dict):
            return fallback
        return TeamAssessment(
            overall_score=OpenAIInvestmentRefiner._bounded_float(value.get("overall_score"), fallback.overall_score),
            confidence=OpenAIInvestmentRefiner._bounded_float(value.get("confidence"), fallback.confidence),
            founder_visibility_score=OpenAIInvestmentRefiner._bounded_float(value.get("founder_visibility_score"), fallback.founder_visibility_score),
            execution_track_record_score=OpenAIInvestmentRefiner._bounded_float(value.get("execution_track_record_score"), fallback.execution_track_record_score),
            domain_expertise_score=OpenAIInvestmentRefiner._bounded_float(value.get("domain_expertise_score"), fallback.domain_expertise_score),
            hiring_signal_score=OpenAIInvestmentRefiner._bounded_float(value.get("hiring_signal_score"), fallback.hiring_signal_score),
            governance_trust_score=OpenAIInvestmentRefiner._bounded_float(value.get("governance_trust_score"), fallback.governance_trust_score),
            strengths=[str(x) for x in value.get("strengths", []) if isinstance(x, str)] or fallback.strengths,
            concerns=[str(x) for x in value.get("concerns", []) if isinstance(x, str)] or fallback.concerns,
            open_questions=[str(x) for x in value.get("open_questions", []) if isinstance(x, str)] or fallback.open_questions,
        )

    @staticmethod
    def _parse_funding(value: Any, fallback: FundraisingContext) -> FundraisingContext:
        if not isinstance(value, dict):
            return fallback

        score = OpenAIInvestmentRefiner._bounded_float(
            value.get("raising_difficulty_score"),
            fallback.raising_difficulty_score,
        )
        commentary = str(value.get("commentary") or fallback.commentary)
        notes = [str(x) for x in value.get("notes", []) if isinstance(x, str)]

        return FundraisingContext(
            defillama_total_funding_rounds=fallback.defillama_total_funding_rounds,
            defillama_total_funding_amount_usd=fallback.defillama_total_funding_amount_usd,
            project_detected_raise_usd=fallback.project_detected_raise_usd,
            project_detected_round_type=fallback.project_detected_round_type,
            benchmark_raise_range_usd=fallback.benchmark_raise_range_usd,
            raise_to_benchmark_ratio=fallback.raise_to_benchmark_ratio,
            raising_difficulty_score=score,
            commentary=commentary,
            notes=notes or fallback.notes,
        )

    @staticmethod
    def _parse_memo(value: Any, recommendation: str) -> InvestmentMemo:
        if not isinstance(value, dict):
            return InvestmentMemo(
                summary="AI memo unavailable.",
                bull_case="Not available.",
                bear_case="Not available.",
                decision_statement=f"Recommendation: {recommendation}",
            )
        return InvestmentMemo(
            summary=str(value.get("summary") or "AI memo unavailable."),
            bull_case=str(value.get("bull_case") or "Not available."),
            bear_case=str(value.get("bear_case") or "Not available."),
            decision_statement=str(value.get("decision_statement") or f"Recommendation: {recommendation}"),
        )

    @staticmethod
    def _safe_text(value: Any, fallback: str) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return fallback

    @staticmethod
    def _bounded_float(value: Any, fallback: float) -> float:
        try:
            n = float(value)
        except (TypeError, ValueError):
            return fallback
        return max(0.0, min(1.0, n))
