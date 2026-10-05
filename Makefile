.PHONY: install test lint refresh refresh-local

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

refresh:
	python scripts/run_pipeline.py refresh

refresh-local:
	python scripts/run_pipeline.py refresh --skip-extract

