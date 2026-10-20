PYTHON ?= python3

.DEFAULT_GOAL := help
.NOTPARALLEL:
.PHONY: help test test-all check build bump-patch bump-minor bump-major publish-test publish

help:
	@echo 'Use an activated virtualenv, or override PYTHON=/path/to/python.'
	@echo 'Install tools: python -m pip install -e ".[tests,deploy]"'
	@echo 'test             Run pytest on the selected Python'
	@echo 'test-all         Run the full Python 3.10-3.15 Nox matrix'
	@echo 'check            Run the matrix, coverage, and source lint'
	@echo 'build            Build wheel and source archive with Flit'
	@echo 'bump-patch       Increment patch and commit the version file only'
	@echo 'bump-minor       Increment minor and commit the version file only'
	@echo 'bump-major       Increment major and commit the version file only'
	@echo 'publish-test     Build and upload to TestPyPI with Flit'
	@echo 'publish          Build and upload to PyPI with Flit'

test:
	$(PYTHON) -m pytest

test-all:
	$(PYTHON) -m nox --error-on-missing-interpreters -s tests-3.10 tests-3.11 tests-3.12 tests-3.13 tests-3.14 tests-3.15

check:
	$(MAKE) test-all
	$(PYTHON) -m pytest --cov=src
	$(PYTHON) -m ruff check src

build:
	$(PYTHON) -m flit build

publish:
	$(PYTHON) -m flit publish

publish-test:
	$(PYTHON) -m flit publish --repository testpypi

bump-patch bump-minor bump-major:
	$(PYTHON) scripts/bump_version.py $(patsubst bump-%,%,$@)
