from __future__ import annotations

from dataclasses import dataclass
import re

from .models import EvidenceItem, ResearchFinding, SourceDocument


@dataclass(frozen=True, slots=True)
class DimensionProfile:
    name: str
    weight: float
    positive_terms: tuple[str, ...]
    negative_terms: tuple[str, ...]


class ResearchEngine:
    _profiles: tuple[DimensionProfile, ...] = (
        DimensionProfile(
            name="team_execution",
            weight=0.14,
            positive_terms=("founder", "execution", "shipping", "delivered", "experienced", "hiring", "retention", "track record"),
            negative_terms=("anonymous", "turnover", "delay", "missed", "inexperienced", "abandoned", "key person risk"),
        ),
        DimensionProfile(
            name="market_opportunity",
            weight=0.10,
            positive_terms=("large market", "demand", "adoption", "pain point", "growth market", "expansion"),
            negative_terms=("niche", "unclear demand", "no market", "limited users", "stagnation"),
        ),
        DimensionProfile(
            name="product_traction",
            weight=0.13,
            positive_terms=("active users", "revenue", "volume", "partnership", "retention", "engagement", "mainnet", "growth"),
            negative_terms=("low volume", "no users", "declining", "churn", "testnet only", "inactive"),
        ),
        DimensionProfile(
            name="technology_security",
            weight=0.14,
            positive_terms=("audit", "formal verification", "bug bounty", "security review", "reliable", "uptime"),
            negative_terms=("exploit", "hack", "vulnerability", "reentrancy", "outage", "bridge risk", "unaudited"),
        ),
        DimensionProfile(
            name="tokenomics_incentives",
            weight=0.14,
            positive_terms=("utility", "vesting", "sustainable emissions", "aligned incentives", "fee capture", "burn mechanism"),
            negative_terms=("inflationary", "unlock pressure", "mercenary capital", "ponzi", "no utility", "overhang"),
        ),
        DimensionProfile(
            name="governance_decentralization",
            weight=0.09,
            positive_terms=("governance", "dao", "decentralized", "community voting", "multisig transparency"),
            negative_terms=("centralized", "admin key", "opaque governance", "single point of failure"),
        ),
        DimensionProfile(
            name="regulatory_compliance",
            weight=0.10,
            positive_terms=("compliance", "kyc", "legal opinion", "licensed", "jurisdictional clarity"),
            negative_terms=("regulatory risk", "enforcement", "unregistered", "sanctions", "compliance gap"),
        ),
        DimensionProfile(
            name="financial_sustainability",
            weight=0.10,
            positive_terms=("runway", "treasury", "cash flow", "sustainable", "capital efficient"),
            negative_terms=("short runway", "high burn", "insolvent", "dilution", "unsustainable incentives"),
        ),
        DimensionProfile(
            name="ecosystem_moat",
            weight=0.06,
            positive_terms=("network effects", "ecosystem", "developer growth", "integration", "moat", "liquidity depth"),
            negative_terms=("copycat", "fragmented", "weak moat", "dependency", "high competition"),
        ),
    )

    def analyze(self, documents: list[SourceDocument]) -> list[ResearchFinding]:
        corpus = " ".join(doc.text.lower() for doc in documents)
        findings: list[ResearchFinding] = []

        for profile in self._profiles:
            positive_map = self._count_terms(corpus, profile.positive_terms)
            negative_map = self._count_terms(corpus, profile.negative_terms)
            positive_hits = sum(positive_map.values())
            negative_hits = sum(negative_map.values())
            evidence_total = positive_hits + negative_hits

            if evidence_total == 0:
                score = 0.5
                confidence = 0.12
                rationale = f"No explicit {profile.name} evidence found; neutral baseline applied."
            else:
                raw = (positive_hits - negative_hits) / evidence_total
                score = (raw + 1.0) / 2.0
                confidence = min(1.0, evidence_total / 16.0)
                rationale = (
                    f"Derived from {positive_hits} positive and {negative_hits} negative {profile.name} signals."
                )

            evidence_items = self._build_evidence_items(positive_map, negative_map)
            findings.append(
                ResearchFinding(
                    dimension=profile.name,
                    score=self._clamp(score),
                    confidence=self._clamp(confidence),
                    weight=profile.weight,
                    positive_hits=positive_hits,
                    negative_hits=negative_hits,
                    evidence_items=evidence_items,
                    rationale=rationale,
                )
            )

        return findings

    @staticmethod
    def _count_terms(corpus: str, terms: tuple[str, ...]) -> dict[str, int]:
        output: dict[str, int] = {}
        for term in terms:
            count = len(re.findall(rf"\b{re.escape(term.lower())}\b", corpus))
            if count > 0:
                output[term] = count
        return output

    @staticmethod
    def _build_evidence_items(positive_map: dict[str, int], negative_map: dict[str, int]) -> list[EvidenceItem]:
        items: list[EvidenceItem] = []
        for term, count in sorted(positive_map.items(), key=lambda x: x[1], reverse=True):
            items.append(EvidenceItem(term=term, count=count, polarity="positive"))
        for term, count in sorted(negative_map.items(), key=lambda x: x[1], reverse=True):
            items.append(EvidenceItem(term=term, count=count, polarity="negative"))
        return items

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    @property
    def weights(self) -> dict[str, float]:
        return {profile.name: profile.weight for profile in self._profiles}
