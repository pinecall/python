# What CI runs, and what a commit runs before it lands.

.PHONY: check lint types deps test build

check: lint types deps test ## everything below, in this order

lint: ## ruff: every rule, and the format
	uv run ruff check .
	uv run ruff format --check .

types: ## pyright, strict
	uv run pyright

deps: ## deptry: every import declared, every declaration imported
	uv run deptry src

test: ## the suite, the tree's rules included
	uv run pytest -q

build: ## the wheel and the sdist a tag publishes, into dist/
	uv build --out-dir dist
