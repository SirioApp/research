from __future__ import annotations

from datetime import datetime, timezone

import requests

from .models import MarketSnapshot


class MarketDataProvider:
    def fetch(self) -> MarketSnapshot:
        notes: list[str] = []

        btc_price = None
        btc_change = None
        eth_price = None
        eth_change = None
        total_market_cap = None
        total_volume = None
        btc_dominance = None
        defi_tvl = None
        stablecoin_mcap = None
        fear_greed_value = None
        fear_greed_label = None

        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "bitcoin,ethereum",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            btc = payload.get("bitcoin", {})
            eth = payload.get("ethereum", {})
            btc_price = self._safe_float(btc.get("usd"))
            btc_change = self._safe_float(btc.get("usd_24h_change"))
            eth_price = self._safe_float(eth.get("usd"))
            eth_change = self._safe_float(eth.get("usd_24h_change"))
        except Exception as exc:
            notes.append(f"CoinGecko price endpoint unavailable: {exc}")

        try:
            response = requests.get("https://api.coingecko.com/api/v3/global", timeout=20)
            response.raise_for_status()
            payload = response.json().get("data", {})
            mcap = payload.get("total_market_cap", {})
            volume = payload.get("total_volume", {})
            market_cap_percent = payload.get("market_cap_percentage", {})
            total_market_cap = self._safe_float(mcap.get("usd"))
            total_volume = self._safe_float(volume.get("usd"))
            btc_dominance = self._safe_float(market_cap_percent.get("btc"))
        except Exception as exc:
            notes.append(f"CoinGecko global endpoint unavailable: {exc}")

        try:
            response = requests.get("https://api.llama.fi/v2/chains", timeout=25)
            response.raise_for_status()
            chains = response.json() if isinstance(response.json(), list) else []
            total = 0.0
            for chain in chains:
                if isinstance(chain, dict):
                    total += float(chain.get("tvl", 0.0) or 0.0)
            defi_tvl = total if total > 0 else None
        except Exception as exc:
            notes.append(f"DefiLlama chains endpoint unavailable: {exc}")

        try:
            response = requests.get("https://stablecoins.llama.fi/stablecoincharts/all", timeout=25)
            response.raise_for_status()
            rows = response.json() if isinstance(response.json(), list) else []
            if rows:
                last = rows[-1]
                stablecoin_mcap = self._safe_float(last.get("totalCirculatingUSD"))
        except Exception as exc:
            notes.append(f"DefiLlama stablecoin endpoint unavailable: {exc}")

        try:
            response = requests.get("https://api.alternative.me/fng/?limit=1&format=json", timeout=20)
            response.raise_for_status()
            data = response.json().get("data", [])
            if data:
                fear_greed_value = int(data[0].get("value"))
                fear_greed_label = str(data[0].get("value_classification"))
        except Exception as exc:
            notes.append(f"Fear & Greed endpoint unavailable: {exc}")

        regime = self._infer_regime(fear_greed_value, btc_change)

        return MarketSnapshot(
            as_of_utc=datetime.now(timezone.utc).isoformat(),
            regime=regime,
            btc_price_usd=btc_price,
            btc_24h_change_pct=btc_change,
            eth_price_usd=eth_price,
            eth_24h_change_pct=eth_change,
            total_market_cap_usd=total_market_cap,
            total_volume_24h_usd=total_volume,
            btc_dominance_pct=btc_dominance,
            defi_tvl_usd=defi_tvl,
            stablecoin_mcap_usd=stablecoin_mcap,
            fear_greed_index=fear_greed_value,
            fear_greed_label=fear_greed_label,
            notes=notes,
        )

    @staticmethod
    def _infer_regime(fear_greed_value: int | None, btc_change: float | None) -> str:
        if fear_greed_value is not None:
            if fear_greed_value >= 70:
                return "risk_on"
            if fear_greed_value <= 35:
                return "risk_off"
        if btc_change is not None:
            if btc_change >= 3:
                return "risk_on"
            if btc_change <= -3:
                return "risk_off"
        return "neutral"

    @staticmethod
    def _safe_float(value) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
