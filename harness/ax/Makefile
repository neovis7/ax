.PHONY: test-all test-ax test-scenarios test-project

test-all: test-ax

test-ax:
	@echo "=== Tier 2: ax 스킬 자체 검증 ==="
	python3 tests/ax/tools/validate_ax.py

test-scenarios:
	@echo "=== Tier 3: 시나리오 검증 ==="
	python3 tests/ax/tools/run_scenario.py tests/ax/scenarios/ --all

test-project:
	@echo "=== Tier 1: 프로젝트 검증 ==="
	python3 .claude/skills/ax/tools/validate_project.py $(PROJECT)
