from __future__ import annotations

import re

from .models import ResearchFinding, SourceDocument, TeamAssessment


class TeamEngine:
    def evaluate(self, documents: list[SourceDocument], findings: list[ResearchFinding]) -> TeamAssessment:
        corpus = " ".join(item.text.lower() for item in documents)

        team_finding = self._find(findings, "team_execution")
        governance_finding = self._find(findings, "governance_decentralization")

        founder_visibility = self._signal_score(corpus, ("founder", "co-founder", "team", "about us", "leadership"))
        execution_track_record = team_finding.score if team_finding else 0.5
        domain_expertise = self._signal_score(corpus, ("ex-", "previously", "phd", "research", "engineer", "core dev"))
        hiring_signal = self._signal_score(corpus, ("hiring", "careers", "job", "recruiting", "open roles"))
        governance_trust = governance_finding.score if governance_finding else 0.5

        confidence = min(1.0, (
            (team_finding.confidence if team_finding else 0.2) * 0.4 +
            (governance_finding.confidence if governance_finding else 0.2) * 0.2 +
            founder_visibility * 0.2 +
            domain_expertise * 0.2
        ))

        overall = min(1.0, max(0.0, (
            founder_visibility * 0.20 +
            execution_track_record * 0.35 +
            domain_expertise * 0.20 +
            hiring_signal * 0.10 +
            governance_trust * 0.15
        )))

        strengths: list[str] = []
        concerns: list[str] = []
        open_questions: list[str] = []

        if founder_visibility >= 0.6:
            strengths.append("Founder and leadership visibility appears acceptable in provided materials.")
        else:
            concerns.append("Limited founder visibility; team transparency should be validated directly.")

        if execution_track_record >= 0.6:
            strengths.append("Execution signal is relatively strong based on delivery-related evidence.")
        else:
            concerns.append("Execution consistency is not yet convincing from available evidence.")

        if domain_expertise >= 0.55:
            strengths.append("Technical/domain expertise references are present.")
        else:
            concerns.append("Domain expertise depth is not sufficiently evidenced.")

        if governance_trust <= 0.45:
            concerns.append("Governance trust and decentralization quality introduce team-related control risk.")

        open_questions.extend([
            "What is the detailed founder-track record with measurable shipped outcomes?",
            "How is key person risk mitigated if core contributors depart?",
            "Which incentives align core team behavior with long-term token/network health?",
        ])

        return TeamAssessment(
            overall_score=overall,
            confidence=confidence,
            founder_visibility_score=founder_visibility,
            execution_track_record_score=execution_track_record,
            domain_expertise_score=domain_expertise,
            hiring_signal_score=hiring_signal,
            governance_trust_score=governance_trust,
            strengths=strengths,
            concerns=concerns,
            open_questions=open_questions,
        )

    @staticmethod
    def _find(findings: list[ResearchFinding], dimension: str) -> ResearchFinding | None:
        for item in findings:
            if item.dimension == dimension:
                return item
        return None

    @staticmethod
    def _signal_score(corpus: str, terms: tuple[str, ...]) -> float:
        hits = 0
        for term in terms:
            hits += len(re.findall(rf"\b{re.escape(term)}\b", corpus))
        return min(1.0, hits / 6.0)
