# Release Checklist

Use this checklist before pushing to GitHub.

## Security
- [ ] `.env` is not present in commit.
- [ ] No API keys or secrets in tracked files.
- [ ] `SECURITY.md` is up to date.

## Quality
- [ ] Tests pass locally.
- [ ] CLI runs successfully on at least one URL and one local file.
- [ ] Output JSON matches `docs/OUTPUT_SCHEMA.md`.

## Documentation
- [ ] `README.md` reflects current behavior.
- [ ] `docs/VC_FRAMEWORK.md` reflects methodology changes.
- [ ] `CHANGELOG.md` updated for current release.

## Packaging
- [ ] `pyproject.toml` version updated.
- [ ] Scripts entry points are correct.
- [ ] `.env.example` contains only placeholders.
