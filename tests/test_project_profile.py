from __future__ import annotations

import unittest

from investment_agent.models import SourceDocument
from investment_agent.project_profile import ProjectProfileBuilder


class ProjectProfileBuilderTests(unittest.TestCase):
    def test_build_extracts_general_project_info(self) -> None:
        doc = SourceDocument(
            source="https://example.org/projects/hurupay/fundraise",
            text=(
                "HuruPay is a payment protocol for cross-border settlements. "
                "Mainnet launched on Ethereum with active users and growing transaction volume. "
                "Join us on https://x.com/hurupay and https://github.com/hurupay/core. "
                "Token symbol: HURU."
            ),
        )

        profile = ProjectProfileBuilder().build([doc])

        self.assertEqual(profile.name, "Hurupay")
        self.assertIsNotNone(profile.description)
        self.assertEqual(profile.category, "payments")
        self.assertEqual(profile.stage, "mainnet")
        self.assertEqual(profile.token_symbol, "HURU")
        self.assertIn("Ethereum", profile.chain_focus)
        self.assertIn("x", profile.social_links)
        self.assertIn("github", profile.social_links)

    def test_build_avoids_mixed_socials_from_other_projects(self) -> None:
        doc = SourceDocument(
            source="https://example.org/projects/hurupay/fundraise",
            text=(
                "HuruPay is a payment protocol. Follow HuruPay at https://x.com/hurupay and https://t.me/hurupay. "
                "Other project Git3 uses https://x.com/TryGit3 and https://t.me/git3io with a separate roadmap."
            ),
        )

        profile = ProjectProfileBuilder().build([doc])

        self.assertEqual(profile.name, "Hurupay")
        self.assertEqual(profile.social_links.get("x"), "https://x.com/hurupay")
        self.assertEqual(profile.social_links.get("telegram"), "https://t.me/hurupay")


if __name__ == "__main__":
    unittest.main()
