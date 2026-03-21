# ax — Agent Team Architect

도메인 설명을 분석하여 최적의 에이전트 팀을 자동 생성합니다.

**도메인 입력:** $ARGUMENTS

## 실행

> 이 커맨드는 SKILL.md의 Phase 1-6을 순차 실행합니다.
> 생성 결과는 `projects/{project-name}/` 하위에 생성됩니다 (`--here` 시 현재 디렉토리).
> 중간 아티팩트는 `${PROJECT_DIR}/.omc/ax/`에 저장됩니다.
> 템플릿: `.claude/skills/ax/templates/`

스킬 파일을 읽고 Phase 1부터 순차 실행하세요:

Read: .claude/skills/ax/SKILL.md

ARGUMENTS: $ARGUMENTS
