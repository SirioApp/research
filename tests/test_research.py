from __future__ import annotations

import unittest

from investment_agent.models import SourceDocument
from investment_agent.research import ResearchEngine


class ResearchEngineTests(unittest.TestCase):
    def test_scoring_is_not_overconfident_with_sparse_positive_signals(self) -> None:
        docs = [
            SourceDocument(
                source="https://example.org/project",
                text=(
                    "Project has execution and roadmap references. "
                    "It mentions growth and integration repeatedly. "
                    "There is no explicit compliance section and no explicit audit details."
                ),
            )
        ]

        findings = ResearchEngine().analyze(docs)
        by_dimension = {item.dimension: item for item in findings}

        self.assertLess(by_dimension["team_execution"].score, 0.90)
        self.assertLess(by_dimension["technology_security"].score, 0.85)
        self.assertLess(by_dimension["regulatory_compliance"].score, 0.60)


if __name__ == "__main__":
    unittest.main()
