.DEFAULT_GOAL := help

.PHONY: help install format lint test rules hooks check

help: ## List available targets with their descriptions
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*## "} {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

install: ## Install the project and the git hooks
	uv sync
	uv run prek install

format: ## Format the code (ruff)
	uv run ruff format

lint: ## Lint the code, applying safe fixes (ruff), and audit the workflows (zizmor)
	uv run ruff check
	uv run zizmor --no-progress --config .github/zizmor.yml .github/workflows .github/dependabot.yml

# Each rule file is tested against the fixture at the same path under tests/rules/, with its
# version range ignored: the ranges are what the pytest suite covers.
rules: ## Test every rule against its fixture (semgrep --test)
	@for rules in src/semgrep_odoo/rules/*/*.yaml; do \
		group=$$(basename $$(dirname $$rules)); name=$$(basename $$rules .yaml); \
		uv run semgrep --test --metrics=off --disable-version-check \
			--config $$rules tests/rules/$$group/$$name.* || exit 1; \
	done

test: rules ## Run the rule fixtures and the test suite
	uv run pytest

hooks: ## Run every git hook over every tracked file (prek)
	uv run prek run --all-files

check: ## Full gate: format, lint, workflow audit, rules and tests
	uv run ruff format --check
	uv run ruff check --no-fix
	uv run zizmor --no-progress --config .github/zizmor.yml .github/workflows .github/dependabot.yml
	$(MAKE) --no-print-directory test
