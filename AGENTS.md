# Agent Notes

Small Python client: public exports/version in `src/getswish/__init__.py`, `SwishClient` in `src/getswish/client.py`.

## Workflow
- Setup: uv 0.13.1 and `uv sync --locked`. See `README.md`.
- Checks: `uv run --locked pytest`, `uv run --locked pytest --cov=src`, `uv run --locked ruff check src`, `uv run --locked ty check src`.
- CI runs on push/PR: Python 3.10-3.15 tests, 3.15 coverage, source-only lint and type checks, build/Twine and isolated installed-certificate checks for wheel and sdist.
- Build with `uv build`; validate with `uv run --locked twine check dist/getswish-*.whl dist/getswish-*.tar.gz`; publish selected artifacts with `uv publish`.
- Bump with `uv version --bump patch` (or minor/major); commit version, lockfile and changelog explicitly. No automatic commit or tag.
- Record user-visible changes in `CHANGELOG.md`.
