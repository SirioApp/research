from __future__ import annotations

from pathlib import Path
import unittest

from investment_agent.agent import InvestmentResearchAgent


class AgentTests(unittest.TestCase):
    def test_agent_returns_dashboard_ready_payload(self) -> None:
        sample_path = Path("tests/sample_report.txt")
        sample_path.write_text(
            "Founders previously built two crypto products and published a security audit. "
            "Mainnet launched with growing active users, but unlock pressure is expected in 12 months. "
            "Treasury runway is uncertain and regulatory exposure remains under review.",
            encoding="utf-8",
        )

        agent = InvestmentResearchAgent(mode="rules")
        result = agent.run([str(sample_path)])
        payload = result.to_dict()

        self.assertGreaterEqual(result.score.value, 0.0)
        self.assertLessEqual(result.score.value, 1.0)
        self.assertIn("team_assessment", payload)
        self.assertIn("market_snapshot", payload)
        self.assertIn("fundraising_context", payload)
        self.assertIn("risk_register", payload)
        self.assertIn("dashboard", payload)
        self.assertGreaterEqual(len(payload["dashboard"]["dimension_rows"]), 5)


if __name__ == "__main__":
    unittest.main()
