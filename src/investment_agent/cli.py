from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from .agent import InvestmentResearchAgent
from .ingestion import IngestionError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="investment-agent",
        description="Run a professional web3 VC-style project analysis with full risk and market context.",
    )
    parser.add_argument("--source", action="append", required=True, help="Project source path or URL. Repeat for multiple sources.")
    parser.add_argument("--mode", choices=["auto", "ai", "rules"], default="auto", help="auto=AI if key exists, ai=force AI, rules=framework-only.")
    parser.add_argument("--model", default="gpt-4.1-mini", help="Model name used in AI mode.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    parser.add_argument("--output", help="Write full JSON result to file.")
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()

    agent = InvestmentResearchAgent(mode=args.mode, model=args.model)
    try:
        result = agent.run(args.source)
    except IngestionError as exc:
        raise SystemExit(f"Ingestion failed: {exc}") from exc

    payload = result.to_dict()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return

    print(f"Investment score: {result.score.value:.3f}")
    print(f"Confidence: {result.score.confidence:.3f}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Market regime: {result.market_snapshot.regime}")
    print(f"Team score: {result.team_assessment.overall_score:.3f}")
    print(f"Raising difficulty: {result.fundraising_context.raising_difficulty_score:.3f}")
    print("Executive summary:")
    print(result.executive_summary)

    print("Top risks:")
    for risk in result.risk_register[:5]:
        print(f"- {risk.dimension}: severity={risk.severity:.3f}, probability={risk.probability:.3f}, impact={risk.impact:.3f}")

    print("Investment memo decision:")
    print(result.investment_memo.decision_statement)

    if args.output:
        print(f"JSON exported to: {args.output}")


if __name__ == "__main__":
    main()
