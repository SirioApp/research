from __future__ import annotations

import re

import requests

from .models import FundraisingContext, MarketSnapshot, SourceDocument


class FundraisingContextProvider:
    _benchmarks = {
        "pre_seed": {"min": 500_000.0, "max": 3_000_000.0},
        "seed": {"min": 2_000_000.0, "max": 8_000_000.0},
        "series_a": {"min": 8_000_000.0, "max": 25_000_000.0},
        "series_b_plus": {"min": 20_000_000.0, "max": 100_000_000.0},
        "token_round": {"min": 3_000_000.0, "max": 30_000_000.0},
    }

    def build(self, documents: list[SourceDocument], market_snapshot: MarketSnapshot) -> FundraisingContext:
        notes: list[str] = []
        rounds_total = None
        amount_total = None

        try:
            response = requests.get("https://defillama.com/raises", timeout=25)
            response.raise_for_status()
            html = response.text.lower()

            rounds_match = re.search(r"total funding rounds\s*(\d[\d,]*)", html)
            amount_match = re.search(r"total funding amount\$\s*([\d.,]+)\s*([mb])", html)

            if rounds_match:
                rounds_total = int(rounds_match.group(1).replace(",", ""))
            if amount_match:
                num = float(amount_match.group(1).replace(",", ""))
                unit = amount_match.group(2)
                amount_total = num * (1_000_000_000.0 if unit == "b" else 1_000_000.0)
        except Exception as exc:
            notes.append(f"DefiLlama raises snapshot unavailable: {exc}")

        project_text = " ".join(doc.text for doc in documents)
        detected_raise = self._extract_raise_amount(project_text)
        detected_round = self._extract_round_type(project_text)

        benchmark = self._benchmarks.get(detected_round or "seed")
        ratio = None
        if detected_raise and benchmark:
            mid = (benchmark["min"] + benchmark["max"]) / 2.0
            ratio = detected_raise / mid if mid > 0 else None

        difficulty = self._raising_difficulty_score(market_snapshot, ratio)
        commentary = self._build_commentary(market_snapshot, detected_raise, detected_round, ratio, difficulty)

        if detected_raise is None:
            notes.append("No explicit project raise amount detected in provided sources.")

        return FundraisingContext(
            defillama_total_funding_rounds=rounds_total,
            defillama_total_funding_amount_usd=amount_total,
            project_detected_raise_usd=detected_raise,
            project_detected_round_type=detected_round,
            benchmark_raise_range_usd=benchmark,
            raise_to_benchmark_ratio=ratio,
            raising_difficulty_score=difficulty,
            commentary=commentary,
            notes=notes,
        )

    @staticmethod
    def _extract_raise_amount(text: str) -> float | None:
        patterns = [
            r"raised\s*\$\s*(\d+(?:\.\d+)?)\s*(m|million|k|thousand|b|bn|billion)",
            r"funding\s*\$\s*(\d+(?:\.\d+)?)\s*(m|million|k|thousand|b|bn|billion)",
            r"\$\s*(\d+(?:\.\d+)?)\s*(m|million|k|thousand|b|bn|billion)\s*(?:round|raise|funding)",
        ]

        lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, lower)
            if not match:
                continue
            value = float(match.group(1))
            unit = match.group(2)
            if unit in {"k", "thousand"}:
                return value * 1_000.0
            if unit in {"m", "million"}:
                return value * 1_000_000.0
            if unit in {"b", "bn", "billion"}:
                return value * 1_000_000_000.0
        return None

    @staticmethod
    def _extract_round_type(text: str) -> str | None:
        lower = text.lower()
        if "pre-seed" in lower or "pre seed" in lower:
            return "pre_seed"
        if "series a" in lower:
            return "series_a"
        if "series b" in lower or "series c" in lower:
            return "series_b_plus"
        if "token sale" in lower or "private sale" in lower or "strategic round" in lower:
            return "token_round"
        if "seed" in lower:
            return "seed"
        return None

    @staticmethod
    def _raising_difficulty_score(market: MarketSnapshot, ratio: float | None) -> float:
        regime_penalty = {"risk_off": 0.35, "neutral": 0.20, "risk_on": 0.08}.get(market.regime, 0.20)
        fear_factor = 0.0
        if market.fear_greed_index is not None:
            fear_factor = max(0.0, (55 - market.fear_greed_index) / 100.0)

        ratio_penalty = 0.0
        if ratio is not None:
            if ratio > 1.5:
                ratio_penalty = 0.20
            elif ratio > 1.2:
                ratio_penalty = 0.12
            elif ratio < 0.7:
                ratio_penalty = -0.05

        return max(0.0, min(1.0, 0.35 + regime_penalty + fear_factor + ratio_penalty))

    @staticmethod
    def _build_commentary(
        market: MarketSnapshot,
        detected_raise: float | None,
        detected_round: str | None,
        ratio: float | None,
        difficulty: float,
    ) -> str:
        raise_text = f"detected raise={detected_raise:,.0f} USD" if detected_raise else "detected raise not found"
        round_text = f"round={detected_round}" if detected_round else "round not identified"
        ratio_text = f"benchmark ratio={ratio:.2f}" if ratio is not None else "benchmark ratio unavailable"

        return (
            f"Current market regime is {market.regime}; {raise_text}; {round_text}; {ratio_text}; "
            f"raising difficulty score={difficulty:.3f} (higher means harder to raise)."
        )
