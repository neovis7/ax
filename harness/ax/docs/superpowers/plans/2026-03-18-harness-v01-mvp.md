# Harness v0.1 MVP 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/harness "도메인 설명"` 스킬을 구현하여 도메인 분석 → 패턴 선택 → 에이전트 생성 → 오케스트레이터 → 검증 파이프라인을 완성한다.

**Architecture:** Claude Code 스킬(순수 마크다운)로 구현. Phase 1-6 전체를 구현하되, Phase 4는 커스텀 스킬 생성만 (외부 스킬 설치는 v0.2). 각 Phase는 SKILL.md 내 섹션으로 정의되며, LLM이 순차 실행. 중간 아티팩트는 `.omc/harness/`에 저장.

**Tech Stack:** Claude Code Skill (SKILL.md), YAML frontmatter, 마크다운, Glob/Grep/Read/Write 도구

**Spec:** `docs/superpowers/specs/2026-03-18-harness-design.md`

---

## 파일 구조

```
.claude/
  skills/
    harness/
      SKILL.md                    # 메인 스킬 — 오케스트레이션 + Phase 1-6 프롬프트
      templates/
        agent-skeleton.md         # 에이전트 본문 스켈레톤 (골든 템플릿 미발견 시 폴백)
        skill-skeleton.md         # 스킬 본문 스켈레톤
        pattern-selection.md      # 패턴 선택 프롬프트 템플릿 + 5개 워크드 예시
        orchestrator-section.md   # CLAUDE.md에 주입할 오케스트레이션 섹션 템플릿
        architecture-doc.md       # ARCHITECTURE.md 템플릿
tests/
  harness/
    scenario-ecommerce.md        # 검증 시나리오: 이커머스
    scenario-research.md         # 검증 시나리오: 리서치 파이프라인
    scenario-saas.md             # 검증 시나리오: SaaS 풀스택
```

---

## Task 1: 프로젝트 초기화 및 디렉토리 구조

**Files:**
- Create: `.claude/skills/harness/SKILL.md` (스텁)
- Create: `.claude/skills/harness/templates/` (디렉토리)

- [ ] **Step 1: 디렉토리 구조 생성**

```bash
mkdir -p .claude/skills/harness/templates
mkdir -p tests/harness
mkdir -p .omc/harness
```

- [ ] **Step 2: SKILL.md 스텁 작성**

```markdown
---
name: harness
description: >-
  도메인 설명을 입력하면 Claude Code용 에이전트 팀(agents, skills, orchestrator)을
  자동 생성하는 메타 도구. "/harness 도메인설명" 형태로 사용.
  코딩, 리서치, 문서 작성 등 모든 도메인에 적용 가능.
argument-hint: '"도메인 설명" 또는 --interview "도메인 설명"'
---

# Harness — Agent Team & Skill Architect

도메인 설명을 분석하여 최적의 에이전트 팀을 자동 생성합니다.

## 사용법

- `/harness "이커머스 플랫폼 - 상품 관리, 주문 처리"` — 완전 자동
- `/harness --interview "데이터 분석"` — 인터뷰 모드 (v1.0)

## 실행 파이프라인

> 이 스킬은 아래 Phase를 순차 실행합니다.
> 각 Phase 산출물은 `.omc/harness/`에 저장됩니다.

(Phase 구현은 후속 Task에서 추가)
```

- [ ] **Step 3: 스킬 파일이 올바른 위치에 생성되었는지 확인**

Run: `cat .claude/skills/harness/SKILL.md | head -5`
Expected: `---` (frontmatter 시작)

- [ ] **Step 4: 커밋 (선택: git repo가 있을 때만)**

```bash
git add .claude/skills/harness/SKILL.md CLAUDE.md docs/
git commit -m "feat: harness 프로젝트 초기화 — 스킬 스텁, 디렉토리 구조"
```

---

## Task 2: 에이전트 스켈레톤 템플릿

**Files:**
- Create: `.claude/skills/harness/templates/agent-skeleton.md`

- [ ] **Step 1: 에이전트 스켈레톤 파일 작성**

골든 템플릿 미발견 시 폴백으로 사용되는 기본 구조.
스펙 섹션 2의 에이전트 스키마를 그대로 반영:

```markdown
---
name: {AGENT_NAME}
description: {AGENT_DESCRIPTION}
model: {AGENT_MODEL}
tools: {AGENT_TOOLS}
role: {AGENT_ROLE}
---

# {AGENT_DISPLAY_NAME}

<Role>
  {ROLE_DESCRIPTION}
  - 책임: {RESPONSIBILITIES}
  - 비책임: {NON_RESPONSIBILITIES}
</Role>

<Success_Criteria>
  {SUCCESS_CRITERIA_LIST}
</Success_Criteria>

<Constraints>
  {CONSTRAINTS_LIST}
</Constraints>

<Process>
  {PROCESS_STEPS}
</Process>

<Tool_Usage>
  {TOOL_USAGE_GUIDELINES}
</Tool_Usage>
```

- [ ] **Step 2: 플레이스홀더가 올바른지 확인**

Run: `grep -c '{' .claude/skills/harness/templates/agent-skeleton.md`
Expected: 11개 이상의 플레이스홀더

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/templates/agent-skeleton.md
git commit -m "feat: 에이전트 스켈레톤 템플릿 추가"
```

---

## Task 3: 스킬 스켈레톤 템플릿

**Files:**
- Create: `.claude/skills/harness/templates/skill-skeleton.md`

- [ ] **Step 1: 스킬 스켈레톤 파일 작성**

스펙 섹션 3의 Harness 확장 계층 스키마 반영:

```markdown
---
name: {SKILL_NAME}
description: {SKILL_DESCRIPTION}
origin: harness
domain: {SKILL_DOMAIN}
---

# {SKILL_DISPLAY_NAME}

## When to Activate
{ACTIVATION_CONDITIONS}

## Core Rules
{CORE_RULES}

## Process
{PROCESS_STEPS}

## Examples
{USAGE_EXAMPLES}
```

- [ ] **Step 2: 확인**

Run: `head -5 .claude/skills/harness/templates/skill-skeleton.md`
Expected: YAML frontmatter 시작

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/templates/skill-skeleton.md
git commit -m "feat: 스킬 스켈레톤 템플릿 추가"
```

---

## Task 4: 패턴 선택 프롬프트 템플릿

**Files:**
- Create: `.claude/skills/harness/templates/pattern-selection.md`

- [ ] **Step 1: 패턴 선택 프롬프트 작성**

스펙 섹션 4의 프롬프트 템플릿 + 5개 워크드 예시를 그대로 포함.
이 파일은 Phase 2에서 LLM에게 제공되는 패턴 선택 가이드:

```markdown
# 패턴 선택 프롬프트

당신은 에이전트 팀 아키텍트입니다. 도메인 분석 시그널을 보고 최적의 아키텍처 패턴을 선택하세요.

## 사용 가능한 패턴

1. **파이프라인**: 작업이 A→B→C 순서로 흘러가며, 각 단계 출력이 다음 단계 입력이 됨
2. **팬아웃/팬인**: N개 독립 작업을 병렬 수행 후 결과를 취합
3. **전문가 풀**: 입력 유형에 따라 서로 다른 전문가에게 라우팅
4. **생성-검증**: 생성물을 만들고 별도 검증 에이전트가 품질 확인
5. **감독자**: 중앙 감독자가 동적으로 작업 분배, 재시도, 우선순위 조정
6. **계층적 위임**: 상위 관리자가 하위 팀 리더에게 위임, 각 팀이 독립 수행

## 도메인 시그널

{SIGNALS_JSON}

## 추론 절차

1. 각 패턴이 이 도메인에 적합한 이유와 부적합한 이유를 한 문장씩 서술
2. 가장 적합한 패턴 1개 선택 (primary)
3. 보조 패턴이 필요한지 판단 — 필요하면 합성 가능한 조합인지 확인
4. 선택 근거를 2-3 문장으로 설명

## 합성 가능 조합

| 주 패턴 | 보조 패턴 | 합성 방식 |
|---------|----------|----------|
| 팬아웃/팬인 | 생성-검증 | 병렬 생성 → 각각 검증 후 취합 |
| 감독자 | 전문가 풀 | 감독자가 유형 판단 후 전문가에게 분배 |
| 파이프라인 | 생성-검증 | 각 파이프라인 단계마다 검증 게이트 |
| 계층적 위임 | 생성-검증 | 각 하위 팀에 생성-검증 사이클 적용 |
| 전문가 풀 | 생성-검증 | 전문가 응답마다 품질 검증 |

## 워크드 예시

### 예시 1: 이커머스 고객 지원 자동화
시그널: task_dependency=mixed, input_variety=highly_varied, quality_criticality=high, team_size_estimate=medium, runtime_dynamism=semi_dynamic
→ 전문가 풀 + 생성-검증 (입력 다양성 + 품질 중요)

### 예시 2: 다국어 문서 번역
시그널: task_dependency=parallel, input_variety=uniform, quality_criticality=medium, team_size_estimate=medium, runtime_dynamism=static
→ 팬아웃/팬인 (독립 병렬 + 균일 입력)

### 예시 3: SaaS 풀스택 개발
시그널: task_dependency=mixed, input_variety=varied, quality_criticality=high, team_size_estimate=large, runtime_dynamism=semi_dynamic
→ 계층적 위임 + 생성-검증 (대규모 팀 + 품질 중요)

### 예시 4: CI/CD 파이프라인 구축
시그널: task_dependency=sequential, input_variety=uniform, quality_criticality=high, team_size_estimate=small, runtime_dynamism=static
→ 파이프라인 + 생성-검증 (순차 의존 + 배포 안전)

### 예시 5: 리서치 보고서 작성
시그널: task_dependency=mixed, input_variety=varied, quality_criticality=medium, team_size_estimate=small, runtime_dynamism=semi_dynamic
→ 감독자 (동적 추가 조사 + 재시도 빈번)

## 출력 형식

```json
{
  "primary_pattern": "{패턴명}",
  "secondary_pattern": "{패턴명 또는 null}",
  "confidence": "{high|medium|low}",
  "rationale": "{선택 근거 2-3 문장}"
}
```
```

- [ ] **Step 2: 6가지 패턴 모두 언급되었는지 확인**

Run: `grep -c '^\d\.' .claude/skills/harness/templates/pattern-selection.md`
Expected: 6

- [ ] **Step 3: 5개 워크드 예시 포함 확인**

Run: `grep -c '### 예시' .claude/skills/harness/templates/pattern-selection.md`
Expected: 5

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/harness/templates/pattern-selection.md
git commit -m "feat: 패턴 선택 프롬프트 템플릿 — 6패턴 + 5예시"
```

---

## Task 5: 오케스트레이터 섹션 템플릿

**Files:**
- Create: `.claude/skills/harness/templates/orchestrator-section.md`

- [ ] **Step 1: CLAUDE.md에 주입할 오케스트레이션 섹션 템플릿 작성**

```markdown
## Harness-Generated Team

> 이 섹션은 `/harness`에 의해 자동 생성되었습니다.
> 생성일: {GENERATION_DATE}
> 도메인: {DOMAIN_DESCRIPTION}
> 패턴: {PRIMARY_PATTERN} {SECONDARY_PATTERN_NOTE}

### 에이전트 카탈로그

| 에이전트 | 역할 | 모델 | 트리거 |
|---------|------|------|--------|
{AGENT_TABLE_ROWS}

### 위임 규칙

{DELEGATION_RULES}

### 실행 프로토콜

- **패턴**: {PATTERN_DESCRIPTION}
- **병렬**: 독립 작업은 팬아웃으로 병렬 실행
- **검증**: {VERIFICATION_POLICY}
- **에스컬레이션**: 3회 실패 시 사용자에게 알림
```

- [ ] **Step 2: 플레이스홀더 확인**

Run: `grep -c '{' .claude/skills/harness/templates/orchestrator-section.md`
Expected: 8개 이상

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/templates/orchestrator-section.md
git commit -m "feat: 오케스트레이터 CLAUDE.md 섹션 템플릿"
```

---

## Task 6: ARCHITECTURE.md 템플릿

**Files:**
- Create: `.claude/skills/harness/templates/architecture-doc.md`

- [ ] **Step 1: ARCHITECTURE.md 템플릿 작성**

```markdown
# {PROJECT_NAME} — 에이전트 팀 아키텍처

> 이 문서는 `/harness`에 의해 자동 생성되었습니다.
> 생성일: {GENERATION_DATE}

## 개요

**도메인**: {DOMAIN_DESCRIPTION}
**선택 패턴**: {PRIMARY_PATTERN} (신뢰도: {CONFIDENCE})
**보조 패턴**: {SECONDARY_PATTERN}

## 패턴 선택 근거

{PATTERN_RATIONALE}

## 에이전트 관계도

```
{AGENT_DIAGRAM}
```

## 에이전트 상세

{AGENT_DETAILS}

## 스킬 목록

| 스킬 | 도메인 | 출처 | 설명 |
|------|--------|------|------|
{SKILL_TABLE_ROWS}

## 데이터 흐름

{DATA_FLOW_DESCRIPTION}

## 설계 결정사항

{DESIGN_DECISIONS}
```

- [ ] **Step 2: 커밋**

```bash
git add .claude/skills/harness/templates/architecture-doc.md
git commit -m "feat: ARCHITECTURE.md 문서 템플릿"
```

---

## Task 7: SKILL.md — Phase 1 (도메인 분석) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

- [ ] **Step 1: Phase 1 프롬프트를 SKILL.md에 추가**

SKILL.md의 `(Phase 구현은 후속 Task에서 추가)` 부분을 아래로 교체:

```markdown
## Phase 1: 도메인 분석

### 입력 파싱

사용자 입력을 파싱합니다:
- `--interview` 플래그 존재 여부 확인 (v1.0 예정, 현재는 무시하고 진행)
- 나머지 텍스트를 도메인 설명으로 사용

### 1.1 프로젝트 탐색 (코드베이스 있을 때)

프로젝트 디렉토리에 코드가 있으면 다음을 탐색:

```bash
# 언어/프레임워크 감지
Glob("package.json") → Node.js/TypeScript
Glob("pyproject.toml") OR Glob("requirements.txt") → Python
Glob("go.mod") → Go
Glob("Cargo.toml") → Rust
Glob("build.gradle*") → Kotlin/Java

# 아키텍처 감지
Glob("src/**") → src 디렉토리 구조 분석
Glob("**/docker-compose*") → 컨테이너화
Glob(".claude/**") → 기존 에이전트/스킬

# 기존 에이전트/스킬 스캔
Glob(".claude/agents/*.md") → 기존 에이전트 목록
Glob(".claude/skills/*/SKILL.md") → 기존 스킬 목록
```

### 1.2 도메인 특성 추출

사용자 설명에서 다음을 추출:

1. **핵심 동사**: 생성, 분석, 변환, 검증, 리서치, 관리, 모니터링, 배포
2. **입출력 형태**: 코드, 문서, 데이터, 이미지, API, 멀티미디어
3. **품질 요구**: 정확도 우선, 속도 우선, 창의성 우선, 안전성 우선

### 1.3 시그널 맵 생성

위 분석 결과를 종합하여 5가지 시그널을 결정:

```json
{
  "project_type": "{감지된 프로젝트 유형 또는 'non-code'}",
  "languages": ["{감지된 언어들}"],
  "domain_description": "{사용자 원문}",
  "domain_verbs": ["{추출된 동사들}"],
  "io_types": ["{입출력 형태들}"],
  "signals": {
    "task_dependency": "{sequential|parallel|mixed}",
    "input_variety": "{uniform|varied|highly_varied}",
    "quality_criticality": "{low|medium|high}",
    "team_size_estimate": "{small|medium|large}",
    "runtime_dynamism": "{static|semi_dynamic|highly_dynamic}"
  },
  "existing_agents": ["{기존 에이전트 이름들}"],
  "existing_skills": ["{기존 스킬 이름들}"]
}
```

이 결과를 `.omc/harness/domain-analysis.json`에 저장합니다.
```

- [ ] **Step 2: Phase 1 섹션이 올바르게 추가되었는지 확인**

Run: `grep "## Phase 1" .claude/skills/harness/SKILL.md`
Expected: `## Phase 1: 도메인 분석`

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 1 도메인 분석 프롬프트 구현"
```

---

## Task 8: SKILL.md — Phase 2 (팀 아키텍처 설계) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

- [ ] **Step 1: Phase 2 프롬프트를 SKILL.md에 추가**

Phase 1 섹션 뒤에 추가:

```markdown
## Phase 2: 팀 아키텍처 설계

### 2.1 패턴 선택

`.omc/harness/domain-analysis.json`의 시그널을 읽고, `templates/pattern-selection.md`의 프롬프트를 따라 최적 패턴을 선택합니다.

패턴 선택 시 `templates/pattern-selection.md`의 워크드 예시를 참고하여 추론하세요.

### 2.2 에이전트 역할 결정

선택된 패턴에 따라 필요한 에이전트 역할을 결정합니다:

**역할 결정 규칙:**
- 모든 패턴: 최소 1개 executor + 1개 reviewer 포함
- 생성-검증: executor(생성) + reviewer(검증) 필수 쌍
- 팬아웃/팬인: coordinator(취합) + N개 worker(병렬)
- 전문가 풀: router(라우팅) + N개 specialist(전문가)
- 감독자: supervisor(감독) + N개 executor(실행)
- 계층적 위임: manager(관리) + N개 team-lead(팀 리더)
- 파이프라인: 단계별 1개씩 순차 에이전트

**에이전트 수 제한: 최대 10개**

### 2.3 골든 템플릿 매칭

각 에이전트 역할에 대해 기존 검증된 템플릿을 탐색:

```bash
# OMC 에이전트 검색 (우선)
Glob("~/.claude/plugins/cache/*/oh-my-claudecode/*/agents/*.md")

# ECC 에이전트 검색
Glob("~/.claude/plugins/cache/*/everything-claude-code/*/agents/*.md")

# 사용자 커스텀
Glob("~/.claude/agents/*.md")
```

가장 높은 버전 디렉토리의 에이전트를 선택 (시맨틱 버전 정렬).
매칭: 역할명(executor→executor.md, reviewer→verifier.md 등)으로 대응.
템플릿이 0개면 `templates/agent-skeleton.md` 폴백 사용.

### 2.4 스킬 갭 분석

도메인에 필요하지만 기존에 없는 스킬을 식별:
- 기존 스킬 목록 (Phase 1에서 스캔) 확인
- 도메인 동사/입출력과 기존 스킬 description 매칭
- 매칭되지 않는 능력 → "커스텀 스킬 생성 대상"

### 2.5 산출물 저장

결과를 `.omc/harness/team-architecture.json`에 저장:

```json
{
  "pattern": {
    "primary": "{패턴명}",
    "secondary": "{패턴명 또는 null}",
    "confidence": "{high|medium|low}",
    "rationale": "{근거}"
  },
  "agents": [
    {
      "name": "{에이전트명}",
      "base_template": "{매칭된 골든 템플릿 이름 또는 'skeleton'}",
      "base_template_path": "{골든 템플릿 파일 경로 또는 null}",
      "role": "{역할}",
      "model": "{claude-sonnet-4-6 등}",
      "customization": "{도메인 특화 설명}"
    }
  ],
  "skills": {
    "existing_match": ["{매칭된 기존 스킬}"],
    "gap_create": ["{생성 필요한 스킬}"]
  },
  "data_flow": "{SendMessage 또는 TaskCreate}"
}
```
```

- [ ] **Step 2: Phase 2 섹션 확인**

Run: `grep "## Phase 2" .claude/skills/harness/SKILL.md`
Expected: `## Phase 2: 팀 아키텍처 설계`

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 2 팀 아키텍처 설계 — 패턴 선택, 템플릿 매칭"
```

---

## Task 9: SKILL.md — Phase 3 (에이전트 정의 생성) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

- [ ] **Step 1: Phase 3 프롬프트를 SKILL.md에 추가**

```markdown
## Phase 3: 에이전트 정의 생성

### 3.1 작업 디렉토리 초기화

```bash
mkdir -p .claude/agents
mkdir -p .omc/harness
```

`.omc/harness/generation-log.json` 초기화:
```json
{
  "generated_files": [],
  "timestamp": "{현재 시각}",
  "domain": "{도메인 설명}"
}
```

### 3.2 골든 템플릿 로드 및 커스터마이즈

`.omc/harness/team-architecture.json`의 각 에이전트에 대해:

1. **템플릿 로드**: `base_template_path`가 있으면 해당 파일 Read. 없으면 `templates/agent-skeleton.md` Read.

2. **frontmatter 커스터마이즈**:
   - `name` → 도메인 맞춤 이름 (예: `content-generator`, `data-analyst`)
   - `description` → 도메인 맞춤 설명 (역할 + 트리거 조건 포함)
   - `model` → 아키텍처에서 결정된 모델 ID (전체 ID: `claude-sonnet-4-6`)
   - `tools` → 역할에 필요한 도구만 (executor: 전체, reviewer: Read/Grep/Glob만)
   - `role` → team-architecture에서 결정된 역할
   - `triggers` → 도메인 키워드

3. **본문 커스터마이즈** (복사 후 수정, 원본 보존):
   - `<Role>` → 도메인 특화 미션으로 교체
   - `<Success_Criteria>` → 도메인 특화 완료 조건
   - `<Constraints>` → 도메인 특화 제약 추가
   - `<Process>` → 도메인 특화 워크플로우로 교체
   - `<Tool_Usage>` → 허용된 도구만 남기기

### 3.3 충돌 처리

각 에이전트 파일 생성 전:
- `.claude/agents/{name}.md` 존재 여부 확인 (Glob)
- 이미 존재하면: 사용자에게 "덮어쓰기 / 건너뛰기 / 다른 이름" 옵션 제시
- 건너뛰면 해당 에이전트는 generation-log에 `"skipped"` 기록

### 3.4 파일 생성 및 로그

각 에이전트 `.md` 파일을 Write로 생성.
생성할 때마다 `generation-log.json`의 `generated_files`에 경로 추가.
```

- [ ] **Step 2: Phase 3 섹션 확인**

Run: `grep "## Phase 3" .claude/skills/harness/SKILL.md`
Expected: `## Phase 3: 에이전트 정의 생성`

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 3 에이전트 정의 생성 — 템플릿 로드, 커스터마이즈, 충돌 처리"
```

---

## Task 10: SKILL.md — Phase 4 (커스텀 스킬 생성) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

> Phase 4는 v0.1에서 커스텀 스킬 생성만 구현. 외부 스킬 설치는 v0.2에서 추가.

- [ ] **Step 1: Phase 4 프롬프트를 SKILL.md에 추가**

```markdown
## Phase 4: 스킬 생성 (v0.1 — 커스텀만)

### 4.1 커스텀 스킬 생성

`.omc/harness/team-architecture.json`의 `skills.gap_create` 목록에 대해:

각 스킬에 대해 `templates/skill-skeleton.md`를 기반으로:
1. frontmatter 채우기 (name, description, origin=harness, domain, dependencies)
2. "When to Activate" 섹션 작성
3. "Core Rules" 섹션 작성
4. "Process" 섹션 작성

스킬 파일 생성 전 충돌 확인:
- `.claude/skills/{skill-name}/SKILL.md` 존재 여부 Glob으로 확인
- 이미 존재하면 사용자에게 덮어쓰기/건너뛰기 확인

`.claude/skills/{skill-name}/SKILL.md` 경로에 Write.
generation-log.json에 기록.

> 외부 스킬 검색·설치는 v0.2에서 추가 예정.
```

- [ ] **Step 2: Phase 4 섹션 확인**

Run: `grep "## Phase 4" .claude/skills/harness/SKILL.md`
Expected: `## Phase 4: 스킬 생성 (v0.1 — 커스텀만)`

- [ ] **Step 3: 커밋 (선택: git repo가 있을 때만)**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 4 커스텀 스킬 생성"
```

---

## Task 11: SKILL.md — Phase 5 (오케스트레이터 생성) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

- [ ] **Step 1: Phase 5 프롬프트를 SKILL.md에 추가**

```markdown
## Phase 5: 오케스트레이터 생성

### 5.1 오케스트레이션 섹션 생성

`templates/orchestrator-section.md`를 읽고 플레이스홀더를 채웁니다:

- `{GENERATION_DATE}` → 현재 날짜
- `{DOMAIN_DESCRIPTION}` → Phase 1 도메인 설명
- `{PRIMARY_PATTERN}` → Phase 2 선택 패턴
- `{AGENT_TABLE_ROWS}` → Phase 3 생성된 에이전트 목록으로 테이블 행 생성
- `{DELEGATION_RULES}` → 패턴에 따른 위임 규칙 생성
- `{VERIFICATION_POLICY}` → 생성-검증 패턴이면 "모든 생성물은 reviewer 통과 필수"

### 5.2 CLAUDE.md Merge

1. 프로젝트 루트에 `CLAUDE.md` 존재 여부 확인
2. **존재하면**: 기존 내용 Read → 끝에 `\n\n---\n\n` + 오케스트레이션 섹션 append
   - 이미 `## Harness-Generated Team` 섹션이 있으면 → 사용자에게 "교체 / 건너뛰기" 확인
3. **없으면**: 오케스트레이션 섹션만으로 새 CLAUDE.md 생성

generation-log.json에 CLAUDE.md 변경 기록.
```

- [ ] **Step 2: Phase 4, 5 섹션 확인**

Run: `grep -E "## Phase [45]" .claude/skills/harness/SKILL.md`
Expected: 2줄 (Phase 4, Phase 5)

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 5 오케스트레이터 생성 — CLAUDE.md merge"
```

---

## Task 12: SKILL.md — Phase 6 (검증 & 테스트) 구현

**Files:**
- Modify: `.claude/skills/harness/SKILL.md`

- [ ] **Step 1: Phase 6 프롬프트를 SKILL.md에 추가**

```markdown
## Phase 6: 검증 & 테스트

### 6.1 구조 검증

생성된 모든 파일을 검증:

1. **에이전트 파일 검증**:
   - 각 `.claude/agents/*.md` Read
   - frontmatter에 `name`, `description`, `model` 필수 필드 존재?
   - `model` 값이 유효한 전체 ID? (`claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5`)
   - 본문에 `<Role>`, `<Success_Criteria>`, `<Constraints>` 태그 존재?

2. **스킬 파일 검증**:
   - 각 `.claude/skills/*/SKILL.md` Read
   - frontmatter에 `name`, `description` 필수 필드 존재?
   - "When to Activate" 섹션 존재?

3. **CLAUDE.md 검증**:
   - `## Harness-Generated Team` 섹션 존재?
   - 에이전트 테이블이 생성된 에이전트 수와 일치?

4. **순환 의존성 검사**:
   - 에이전트 간 위임 규칙에 순환 없는지 확인

검증 실패 항목이 있으면 즉시 수정 시도.

### 6.2 시나리오 검증

도메인에 맞는 샘플 작업 3개를 자동 생성하고, 각 작업에 대해:
- 어떤 에이전트가 호출되어야 하는지 추론
- 위임 규칙과 일치하는지 확인
- 예상 흐름 문서화

### 6.3 검증 결과 저장

구조 검증 결과를 `.omc/harness/validation-report.json`에 저장:

```json
{
  "timestamp": "{현재 시각}",
  "checks": {
    "agent_frontmatter": "{PASS|FAIL}",
    "agent_body_structure": "{PASS|FAIL}",
    "skill_frontmatter": "{PASS|FAIL}",
    "claudemd_section": "{PASS|FAIL}",
    "circular_dependency": "{PASS|FAIL}"
  },
  "overall": "{PASS|FAIL}",
  "failures": ["{실패 항목 상세}"]
}
```

검증 실패 시 (overall == FAIL):
1. 실패 항목을 사용자에게 보여주기
2. 자동 수정 시도
3. 수정 불가하면: `.omc/harness/generation-log.json`의 파일 목록을 보여주고 "롤백(생성 파일 삭제) / 유지(부분 결과 보존)" 선택 요청
4. 롤백 선택 시: generation-log의 generated_files 각각 삭제

### 6.4 ARCHITECTURE.md 생성

`templates/architecture-doc.md`를 읽고 플레이스홀더를 채워서 생성.

충돌 확인: `.claude/ARCHITECTURE.md` 이미 존재하면 → 사용자에게 덮어쓰기/건너뛰기 확인.

`.claude/ARCHITECTURE.md`에 Write.

내용:
- 선택된 패턴과 근거
- 에이전트 관계도 (텍스트 다이어그램)
- 각 에이전트 상세 (이름, 역할, 모델, 도구)
- 스킬 목록
- 데이터 흐름

### 6.5 검증 시나리오 파일 생성

충돌 확인: `tests/harness/scenario-{domain}.md` 이미 존재하면 → 사용자에게 덮어쓰기/건너뛰기 확인.

`tests/harness/scenario-{domain}.md` 파일 생성:

```markdown
# 검증 시나리오: {도메인}

## 생성 정보
- 날짜: {날짜}
- 패턴: {패턴}
- 에이전트 수: {수}
- 스킬 수: {수}

## 구조 검증 결과
- [ ] 에이전트 frontmatter 유효성: {PASS/FAIL}
- [ ] 스킬 frontmatter 유효성: {PASS/FAIL}
- [ ] CLAUDE.md 오케스트레이션 섹션: {PASS/FAIL}
- [ ] 순환 의존성 없음: {PASS/FAIL}

## 시나리오 검증
### 시나리오 1: {작업 설명}
- 예상 에이전트: {에이전트명}
- 예상 흐름: {A → B → C}
- 위임 규칙 일치: {YES/NO}

### 시나리오 2: ...
### 시나리오 3: ...
```

generation-log.json에 기록.

### 6.6 완료 보고

모든 Phase 완료 후 사용자에게 요약 보고:

```
✅ Harness 에이전트 팀 생성 완료

📊 요약:
  - 패턴: {primary} + {secondary}
  - 에이전트: {N}개 생성
  - 스킬: {N}개 생성
  - 검증: {PASS/FAIL}

📁 생성된 파일:
  - .claude/agents/{name1}.md
  - .claude/agents/{name2}.md
  - .claude/skills/{name}/SKILL.md
  - .claude/CLAUDE.md (오케스트레이션 섹션 추가)
  - .claude/ARCHITECTURE.md
  - tests/harness/scenario-{domain}.md

💡 다음 단계:
  - 생성된 에이전트를 사용해보세요
  - ARCHITECTURE.md에서 팀 구조를 확인하세요
  - 문제가 있으면 `/harness`를 다시 실행하세요
```
```

- [ ] **Step 2: Phase 6 섹션 확인**

Run: `grep "## Phase 6" .claude/skills/harness/SKILL.md`
Expected: `## Phase 6: 검증 & 테스트`

- [ ] **Step 3: 전체 Phase 구조 확인**

Run: `grep "^## Phase" .claude/skills/harness/SKILL.md`
Expected: Phase 1, 2, 3, 4, 5, 6 — 총 6줄

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/harness/SKILL.md
git commit -m "feat: Phase 6 검증 & 테스트 — 구조 검증, 시나리오, ARCHITECTURE.md"
```

---

## Task 13: 검증 시나리오 사전 작성

**Files:**
- Create: `tests/harness/scenario-ecommerce.md`
- Create: `tests/harness/scenario-research.md`
- Create: `tests/harness/scenario-saas.md`

- [ ] **Step 1: 이커머스 시나리오 작성**

```markdown
# 검증 시나리오: 이커머스 플랫폼

## 입력
`/harness "이커머스 플랫폼 - 상품 관리, 주문 처리, 고객 지원"`

## 예상 결과

### 도메인 분석 (Phase 1)
- domain_verbs: ["관리", "처리", "지원"]
- io_types: ["데이터", "API"]
- signals.input_variety: "highly_varied"
- signals.quality_criticality: "high"
- signals.team_size_estimate: "medium"

### 패턴 선택 (Phase 2)
- primary: "전문가 풀" (입력 다양성 높음)
- secondary: "생성-검증" (품질 중요)

### 에이전트 (Phase 3) — 예상 4-6개
- product-manager (executor): 상품 관리
- order-processor (executor): 주문 처리
- support-agent (executor): 고객 지원
- router (specialist): 요청 유형별 라우팅
- quality-checker (reviewer): 처리 결과 검증

### 수동 검증 체크리스트
- [ ] 에이전트 파일 5개 이하 생성
- [ ] 각 에이전트에 도메인 특화 <Role> 존재
- [ ] CLAUDE.md에 위임 규칙 존재
- [ ] ARCHITECTURE.md에 전문가 풀 다이어그램
```

- [ ] **Step 2: 리서치 시나리오 작성**

```markdown
# 검증 시나리오: 리서치 보고서 파이프라인

## 입력
`/harness "시장 리서치 및 보고서 작성 - 데이터 수집, 분석, 보고서 생성"`

## 예상 결과

### 도메인 분석 (Phase 1)
- domain_verbs: ["수집", "분석", "생성"]
- io_types: ["데이터", "문서"]
- signals.task_dependency: "mixed"
- signals.runtime_dynamism: "semi_dynamic"
- signals.team_size_estimate: "small"

### 패턴 선택 (Phase 2)
- primary: "감독자" (동적 리서치)

### 에이전트 (Phase 3) — 예상 3-4개
- research-supervisor (supervisor): 리서치 방향 관리
- data-collector (executor): 데이터 수집
- report-writer (executor): 보고서 작성
- fact-checker (reviewer): 사실 확인

### 수동 검증 체크리스트
- [ ] 에이전트 4개 이하
- [ ] supervisor 역할 에이전트 존재
- [ ] ARCHITECTURE.md에 감독자 패턴 설명
```

- [ ] **Step 3: SaaS 시나리오 작성**

```markdown
# 검증 시나리오: SaaS 풀스택 개발

## 입력
`/harness "SaaS 풀스택 개발 - Next.js 프론트엔드, FastAPI 백엔드, PostgreSQL"`

## 예상 결과

### 도메인 분석 (Phase 1)
- project_type: "web-app"
- languages: ["typescript", "python"]
- signals.task_dependency: "mixed"
- signals.team_size_estimate: "large"
- signals.quality_criticality: "high"

### 패턴 선택 (Phase 2)
- primary: "계층적 위임"
- secondary: "생성-검증"

### 에이전트 (Phase 3) — 예상 6-8개
- project-lead (manager): 전체 조율
- frontend-lead (executor): 프론트엔드
- backend-lead (executor): 백엔드
- db-specialist (executor): DB 설계
- code-reviewer (reviewer): 코드 리뷰
- test-engineer (executor): 테스트 작성

### 수동 검증 체크리스트
- [ ] 에이전트 10개 이하
- [ ] 계층적 구조 (manager → team-lead) 존재
- [ ] ARCHITECTURE.md에 계층 다이어그램
```

- [ ] **Step 4: 커밋**

```bash
git add tests/harness/
git commit -m "feat: 3개 검증 시나리오 — 이커머스, 리서치, SaaS"
```

---

## Task 14: 통합 테스트 — 이커머스 시나리오

**Files:**
- 모든 기존 파일 활용

- [ ] **Step 1: 스킬 실행 테스트**

```bash
# 프로젝트 디렉토리에서 harness 스킬 실행
/harness "이커머스 플랫폼 - 상품 관리, 주문 처리, 고객 지원"
```

- [ ] **Step 2: 생성 결과 확인**

```bash
# 에이전트 파일 존재 확인
ls .claude/agents/*.md

# 스킬 파일 존재 확인
ls .claude/skills/*/SKILL.md

# CLAUDE.md 오케스트레이션 섹션 확인
grep "Harness-Generated Team" .claude/CLAUDE.md

# ARCHITECTURE.md 존재 확인
cat .claude/ARCHITECTURE.md | head -10

# 검증 시나리오 존재 확인
ls tests/harness/
```

- [ ] **Step 3: 에이전트 파일 품질 확인**

생성된 각 에이전트 파일에 대해:
- frontmatter에 `name`, `description`, `model` 존재?
- `model` 값이 전체 ID?
- `<Role>`, `<Success_Criteria>`, `<Constraints>` 태그 존재?
- 도메인 특화 내용이 포함?

- [ ] **Step 4: 문제 수정 후 재테스트**

문제 발견 시 SKILL.md 수정 → 재실행 → 확인

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "test: 이커머스 시나리오 통합 테스트 통과"
```

---

## Task 15: 최종 검증 및 문서 정리

**Files:**
- Modify: `CLAUDE.md` (프로젝트 루트)
- Modify: `docs/DESIGN-BRIEF.md`

- [ ] **Step 1: DESIGN-BRIEF.md 남은 과제 체크**

`docs/DESIGN-BRIEF.md`의 체크리스트를 업데이트하여 완료된 항목 표시.

- [ ] **Step 2: 프로젝트 루트 CLAUDE.md 업데이트**

```markdown
## 구현 상태

### v0.1 (MVP) — 완료
- [x] Phase 1: 도메인 분석
- [x] Phase 2: 팀 아키텍처 설계 (패턴 자동 선택)
- [x] Phase 3: 에이전트 정의 생성 (골든 템플릿 기반)
- [x] Phase 4: 커스텀 스킬 생성
- [x] Phase 5: 오케스트레이터 생성 (CLAUDE.md merge)
- [x] Phase 6: 검증 & 테스트

### v0.2 — 예정
- [ ] 외부 스킬 통합 (Anthropic 공식, GitHub)
- [ ] 스킬 의존성 자동 해결

### v0.3 — 예정
- [ ] Skill Resolver 런타임 에이전트
- [ ] 동적 스킬 검색·설치
```

- [ ] **Step 3: 전체 파일 구조 최종 확인**

```bash
find .claude/skills/harness -type f | sort
find tests/harness -type f | sort
```

Expected:
```
.claude/skills/harness/SKILL.md
.claude/skills/harness/templates/agent-skeleton.md
.claude/skills/harness/templates/architecture-doc.md
.claude/skills/harness/templates/orchestrator-section.md
.claude/skills/harness/templates/pattern-selection.md
.claude/skills/harness/templates/skill-skeleton.md
tests/harness/scenario-ecommerce.md
tests/harness/scenario-research.md
tests/harness/scenario-saas.md
```

- [ ] **Step 4: 최종 커밋**

```bash
git add -A
git commit -m "feat: Harness v0.1 MVP 완성 — 6단계 파이프라인 에이전트 팀 자동 생성"
```
