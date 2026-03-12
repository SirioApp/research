# Release Checklist

Use this checklist before pushing to GitHub.

## Security
- [ ] `.env` is not present in commit.
- [ ] No sensitive secrets in tracked files.
- [ ] `SECURITY.md` is up to date.
- [ ] `BACKED_API_KEY` production value is not hardcoded in repository files.

## Quality
- [ ] Tests pass locally.
- [ ] CLI runs successfully on at least one URL and one local file.
- [ ] API `GET /v1/health` and `POST /v1/analyze` work with auth.
- [ ] Output JSON matches `docs/OUTPUT_SCHEMA.md`.

## Documentation
- [ ] `README.md` reflects current behavior.
- [ ] `Integration.md` reflects API and dashboard integration flow.
- [ ] `docs/VC_FRAMEWORK.md` reflects methodology changes.
- [ ] `CHANGELOG.md` updated for current release.

## Packaging
- [ ] `pyproject.toml` version updated.
- [ ] Scripts entry points are correct.
- [ ] `.env.example` contains only non-sensitive defaults/placeholders.
