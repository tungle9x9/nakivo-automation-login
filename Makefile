.PHONY: help install lint check test test-smoke test-regression test-parallel test-headless report clean

PYTHON ?= python
PYTEST ?= pytest

help:
	@echo "=========================================================="
	@echo "NAKIVO ENTERPRISE TEST AUTOMATION PLATFORM"
	@echo "=========================================================="
	@echo "make install         Install project dependencies and editable package"
	@echo "make lint            Run static analysis and linting checks via ruff"
	@echo "make check           Run static analysis followed by smoke verification"
	@echo "make test            Run all test suites"
	@echo "make test-smoke      Run Smoke test suite"
	@echo "make test-regression Run Regression test suite"
	@echo "make test-parallel   Run tests in parallel (4 workers)"
	@echo "make test-headless   Run tests headlessly"
	@echo "make report          Generate and open Allure report"
	@echo "make clean           Clean caches, logs, and temp reports"
	@echo "=========================================================="

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

lint:
	$(PYTHON) -m ruff check .

check: lint test-smoke

test:
	$(PYTHON) run_platform_tests.py

test-smoke:
	$(PYTHON) run_platform_tests.py -m smoke

test-regression:
	$(PYTHON) run_platform_tests.py -m regression

test-parallel:
	$(PYTHON) run_platform_tests.py -n 4

test-headless:
	$(PYTHON) run_platform_tests.py --headless true

report:
	allure generate reports/allure-results -o reports/allure-report --clean
	allure open reports/allure-report

clean:
	rm -rf reports/allure-results/* reports/screenshots/* reports/report.html reports/junit.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
