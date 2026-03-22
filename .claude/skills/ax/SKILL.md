---
name: ax
description: >-
  도메인 설명을 입력하면 Claude Code용 에이전트 팀(agents, skills, orchestrator)을
  자동 생성하는 메타 도구. 사용자가 "에이전트 팀 만들어", "프로젝트 설정해줘",
  "팀 구성", "agent team", "scaffold agents" 등을 요청하거나, 새 프로젝트를 위한
  에이전트/스킬 구조가 필요할 때 이 스킬을 사용하세요. 코딩, 리서치, 문서 작성,
  마케팅, 데이터 분석, 규제 준수 등 모든 도메인에 적용 가능합니다.
argument-hint: '"도메인 설명" 또는 --here/--execute/--interview/--design {skill}/--skip-interview 조합'
---

# AX — Agent Team & Skill Architect

도메인 설명을 분석하여 최적의 에이전트 팀을 자동 생성합니다.

## 사용법

- `/ax "이커머스 플랫폼 - 상품 관리, 주문 처리"` — 완전 자동 (projects/ 하위 생성)
- `/ax --here "이커머스 플랫폼"` — 현재 디렉토리에 에이전트 생성
- `/ax --execute "AI 리더십 슬라이드"` — 에이전트 팀 생성 + 즉시 실행
- `/ax --interview "데이터 분석"` — 인터뷰 모드
- `/ax --execute --skip-interview "대시보드"` — 인터뷰 없이 기본값으로 즉시 실행
- `/ax --design supanova --execute "홈페이지"` — supanova 디자인 스킬 적용 + 실행
- `/ax --design none --execute "대시보드"` — 디자인 스킬 자동 적용 비활성화

## 실행 파이프라인

> Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 6.7(인터뷰) → 6.8(policy) → 7(`--execute` 시)
> 생성된 프로젝트는 `projects/{project-name}/` 하위에 생성됩니다 (`--here` 시 현재 디렉토리).
> 중간 아티팩트는 `${PROJECT_DIR}/.omc/ax/`에 저장됩니다.

### 실행 규칙 (모든 Phase 공통)

- **자동 실행**: 에이전트 호출 시 `mode: "bypassPermissions"`를 사용합니다.
- **진행 추적**: 각 Phase 시작 시 TaskCreate, 완료 시 TaskUpdate(completed).
- **병렬 실행**: 독립적인 작업은 병렬 Agent 호출로 실행 (Phase별 명시).
- **무개입 원칙**: 인터뷰(Phase 6.7) 이후 사용자 질문 = 0. 모든 분기는 `execution-policy.json`을 참조하여 자동 결정.
- **에스컬레이션 정책**: 동일 작업 실패 시 `execution-policy.json`의 `on_*_failure` 정책에 따라 처리 (기본: skip_and_log).
- **컨텍스트 압축**: 사용량이 약 75%에 도달하면 핵심 정보만 유지하고 자동 압축.
- **작동 검증 필수**: 코드를 생성하는 것만으로는 완료가 아닙니다. `--execute` 시 code 도메인에서는 반드시 서버를 실행하고, 핵심 플로우가 실제로 작동하는지 3-Layer 검증으로 확인합니다.

### Phase 실행 프로토콜

각 Phase 실행 시 다음 순서를 따릅니다:
1. Read: `phases/phase-{N}-{name}.md` — 해당 Phase 지시사항 로드
2. Phase 내부에서 필요한 references/templates를 조건부 Read
3. 산출물 생성 + 출력 계약 검증
4. TaskUpdate(completed) → 다음 Phase

### Phase 파일 매핑

| Phase | 파일 | 핵심 산출물 |
|-------|------|-----------|
| 0 | `phases/phase-0-init.md` | settings.json, TaskCreate |
| 1 | `phases/phase-1-analysis.md` | domain-analysis.json |
| 2 | `phases/phase-2-architecture.md` | team-architecture.json, api-contracts.ts, api-fixtures.ts, user-flows.md, crud-matrix.md, crud-checklists.json |
| 3 | `phases/phase-3-agents.md` | .claude/agents/*.md |
| 4 | `phases/phase-4-skills.md` | .claude/skills/*/SKILL.md |
| 5 | `phases/phase-5-orchestrator.md` | CLAUDE.md 오케스트레이션 섹션 |
| 6 | `phases/phase-6-validation.md` | validation-report.json, ARCHITECTURE.md, 시나리오, 인터뷰(--execute), execution-policy.json |
| 7 | `phases/phase-7-execution.md` | 실행 결과물, 3-Layer 검증, 최종 보고 |

### 조건부 참조 로드

Phase 파일 내부에서 필요 시 추가 참조를 Read합니다:
- Phase 1.7: `references/domain-research.md` (규제 도메인일 때만)
- Phase 2.1: `templates/pattern-selection.md` + `templates/domain-patterns.md`
- Phase 2.4.1: `templates/external-skill-catalog.md`
- Phase 2.4.2: `references/api-contract.md` (fullstack/api일 때만)
- Phase 3.2: `library/base-agents/{role}-base.md` + `library/anti-patterns/{role}.md`
- Phase 6.7: `references/interview-mode.md` (--execute 시)

## 확장 기능 (상세는 references/ 참조)

- **인터뷰 모드** (`--interview`): Read `references/interview-mode.md`
- **에이전트 재사용 라이브러리**: Read `references/agent-reuse-library.md`
- **마켓플레이스 통합**: Read `references/marketplace.md`
