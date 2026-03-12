from __future__ import annotations

import unittest

from fastapi import HTTPException

from investment_agent.api import AnalyzeRequest, _extract_api_key, _resolve_sources


class ApiHelpersTests(unittest.TestCase):
    def test_resolve_sources_from_single_source(self) -> None:
        payload = AnalyzeRequest(source="https://example.com")
        self.assertEqual(_resolve_sources(payload), ["https://example.com"])

    def test_resolve_sources_from_sources_array(self) -> None:
        payload = AnalyzeRequest(sources=["https://a.com", "https://b.com"])
        self.assertEqual(_resolve_sources(payload), ["https://a.com", "https://b.com"])

    def test_resolve_sources_rejects_both_source_fields(self) -> None:
        payload = AnalyzeRequest(source="https://a.com", sources=["https://b.com"])
        with self.assertRaises(HTTPException):
            _resolve_sources(payload)

    def test_extract_api_key_prefers_x_api_key(self) -> None:
        extracted = _extract_api_key(" test-key ", "Bearer ignored")
        self.assertEqual(extracted, "test-key")

    def test_extract_api_key_uses_bearer_token(self) -> None:
        extracted = _extract_api_key(None, "Bearer token-123")
        self.assertEqual(extracted, "token-123")


if __name__ == "__main__":
    unittest.main()
