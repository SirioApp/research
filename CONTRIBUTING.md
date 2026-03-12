# Contributing

Thank you for improving Backed Research Agent.

## Development setup
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -e .`
3. Run tests:
   `python -m unittest discover -s tests -v`

## Contribution standards
- Keep modules cohesive and testable.
- Preserve deterministic behavior in core risk/scoring logic.
- Add type hints for new public functions.
- Keep comments minimal and high-value.
- Update docs when output schema or methodology changes.

## Pull request checklist
- Short summary of the problem and solution.
- Behavior impact (before/after) for scoring, risk, or memo logic.
- Tests added/updated for changed logic.
- No secrets in code, docs, or commits.

## Commit hygiene
- Small, focused commits.
- Clear commit messages.
- Avoid unrelated refactors in the same PR.
