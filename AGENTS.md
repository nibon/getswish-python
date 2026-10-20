# Agent Notes

Small Python client: public exports/version in `src/getswish/__init__.py`, `SwishClient` in `src/getswish/client.py`.

## Workflow
- Setup: `pip install -e ".[tests]"`; add `deploy` for Flit. See `make help` and `README.md`.
- Checks: `make test`, `make test-all` (Python 3.10-3.15), `make check` (matrix, coverage, lint).
- CI runs on push/PR: all six Python versions, plus 3.15 coverage, source-only Ruff, build/Twine and installed-certificate checks. No blocking typecheck.
- `make build`, `make publish-test`, and `make publish` invoke Flit directly.
- `make bump-patch`, `make bump-minor`, and `make bump-major` commit only the version file.
- Record user-visible changes in `CHANGELOG.md`.
