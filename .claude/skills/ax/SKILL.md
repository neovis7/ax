---
name: ax
description: >-
  도메인 설명을 입력하면 Claude Code용 에이전트 팀(agents, skills, orchestrator)을
  자동 생성하는 메타 도구. 사용자가 "에이전트 팀 만들어", "프로젝트 설정해줘",
  "팀 구성", "agent team", "scaffold agents" 등을 요청하거나, 새 프로젝트를 위한
  에이전트/스킬 구조가 필요할 때 이 스킬을 사용하세요. 코딩, 리서치, 문서 작성,
  마케팅, 데이터 분석, 규제 준수 등 모든 도메인에 적용 가능합니다.
argument-hint: '"도메인 설명" 또는 --here/--execute/--interview/--design {skill} 조합'
---

# AX — Agent Team & Skill Architect

도메인 설명을 분석하여 최적의 에이전트 팀을 자동 생성합니다.

## 목차

- [사용법](#사용법) | [실행 규칙](#실행-규칙-모든-phase-공통)
- [Phase 0: 초기화](#phase-0-초기화) | [Phase 1: 도메인 분석](#phase-1-도메인-분석) | [Phase 2: 팀 아키텍처](#phase-2-팀-아키텍처-설계)
- [Phase 3: 에이전트 생성](#phase-3-에이전트-정의-생성) | [Phase 4: 스킬 생성](#phase-4-스킬-생성-v01--커스텀만) | [Phase 5: 오케스트레이터](#phase-5-오케스트레이터-생성)
- [Phase 6: 검증](#phase-6-검증--테스트) | [Phase 7: 실행](#phase-7-실행-execute-전용) | [확장 기능](#확장-기능-상세는-references-참조)

## 사용법

- `/ax "이커머스 플랫폼 - 상품 관리, 주문 처리"` — 완전 자동 (projects/ 하위 생성)
- `/ax --here "이커머스 플랫폼"` — 현재 디렉토리에 에이전트 생성
- `/ax --execute "AI 리더십 슬라이드"` — 에이전트 팀 생성 + 즉시 실행
- `/ax --interview "데이터 분석"` — 인터뷰 모드 (v1.0)
- `/ax --design supanova --execute "홈페이지"` — supanova 디자인 스킬 적용 + 실행
- `/ax --design none --execute "대시보드"` — 디자인 스킬 자동 적용 비활성화

## 실행 파이프라인

> Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 순차 실행합니다 (`--execute` 시 Phase 7 추가).
> 생성된 프로젝트는 `projects/{project-name}/` 하위에 생성됩니다 (`--here` 시 현재 디렉토리).
> 중간 아티팩트는 `${PROJECT_DIR}/.omc/ax/`에 저장됩니다.

### 실행 규칙 (모든 Phase 공통)

- **자동 실행**: 에이전트 호출 시 `mode: "bypassPermissions"`를 사용합니다 — 사용자 인터럽트 없이 파이프라인이 끊김 없이 실행되도록 하기 위함입니다.
- **진행 추적**: 각 Phase 시작 시 TaskCreate, 완료 시 TaskUpdate(completed). 사용자에게 진행 상태 표시.
- **병렬 실행**: 독립적인 작업은 병렬 Agent 호출로 실행 (Phase별 명시).
- **에스컬레이션**: 동일 작업 3회 실패 시에만 사용자에게 알리고 중단.
- **무중단 원칙**: 파이프라인 실행 중 충돌/권한 관련 질문은 하지 않습니다 (충돌 시 덮어쓰기, 외부 스킬은 건너뛰기, CLAUDE.md는 교체). 단, **인터뷰 게이트(Phase 6.7)는 예외** — code 도메인이나 safety/accuracy 프로젝트에서 `--execute` 시 plan/architecture 설계를 위한 질의는 반드시 수행합니다. 이 질의는 결과물 품질에 직접 영향을 주는 설계 결정이므로 무중단 원칙의 적용 대상이 아닙니다.
- **컨텍스트 압축**: 컨텍스트 사용량이 약 75%에 도달하면, 현재 Phase까지의 핵심 정보(프로젝트 경로, 에이전트 목록, 검증 결과)만 유지하고 나머지 실행 이력을 자동 압축합니다. 서브에이전트는 필요한 파일을 직접 Read하므로 경로만 있으면 충분합니다.

## Phase 0: 초기화

### 0.1 프로젝트 권한 자동 설정

`${PROJECT_DIR}/.claude/settings.json`을 생성하여 파이프라인 실행 중 권한 승인을 자동화합니다:

```json
{
  "permissions": {
    "allowedTools": [
      "Write", "Edit", "Agent",
      "Bash(mkdir *)", "Bash(find *)", "Bash(open *)",
      "Bash(wc *)", "Bash(ls *)", "Bash(cp *)", "Bash(python3 *)"
    ]
  }
}
```

이미 `${PROJECT_DIR}/.claude/settings.json`이 존재하면 `allowedTools`를 merge (기존 항목 보존, 누락 항목만 추가).

### 0.2 진행 추적 초기화

다음 TaskCreate를 호출하여 전체 파이프라인 진행 상태를 등록합니다:

```
TaskCreate("Phase 1: 도메인 분석")
TaskCreate("Phase 2: 팀 아키텍처 설계")
TaskCreate("Phase 3: 에이전트 정의 생성")
TaskCreate("Phase 4: 스킬 생성")
TaskCreate("Phase 5: 오케스트레이터 생성")
TaskCreate("Phase 6: 검증 & 테스트")
TaskCreate("Phase 7: 실행") # --execute 플래그 시에만
```

각 Phase 시작 시 TaskUpdate(in_progress), 완료 시 TaskUpdate(completed)로 갱신합니다.

## Phase 1: 도메인 분석

### 입력 파싱

사용자 입력을 파싱합니다:
- `--here` 플래그 존재 여부 확인 → 현재 디렉토리에 에이전트 생성
- `--execute` 플래그 존재 여부 확인 → Phase 6 완료 후 Phase 7(실행) 진행
- `--interview` 플래그 존재 여부 확인 → Phase 1에서 인터뷰 모드 실행
- `--design {value}` 플래그 확인 → 디자인 스킬 선택:
  - `--design supanova` → supanova-design 명시적 적용
  - `--design frontend-design` → Anthropic frontend-design 적용
  - `--design none` → 디자인 스킬 자동 적용 비활성화
  - 플래그 없음 → creative/document + html 도메인이면 supanova-design 자동 적용
- 나머지 텍스트를 도메인 설명으로 사용

### 1.0 프로젝트 디렉토리 결정

`--here` 플래그에 따라 프로젝트 디렉토리를 결정합니다:

**`--here` 있을 때:**
- `PROJECT_DIR=.` (현재 디렉토리)
- 기존 `.claude/` 디렉토리가 있으면 그대로 사용
- 기존 에이전트/스킬과 충돌 시 Phase 3에서 처리

**`--here` 없을 때 (기본):**
1. 도메인 설명의 핵심 키워드를 kebab-case로 변환 (예: "이커머스 플랫폼" → `ecommerce-platform`)
2. `projects/{project-name}/` 디렉토리 생성
3. `PROJECT_DIR=projects/{project-name}`

이후 모든 Phase의 파일 생성은 `${PROJECT_DIR}/` 기준으로 수행.

### 1.1 작업 디렉토리 초기화

```bash
mkdir -p ${PROJECT_DIR}/.claude/agents
mkdir -p ${PROJECT_DIR}/.claude/skills
mkdir -p ${PROJECT_DIR}/.omc/ax
mkdir -p ${PROJECT_DIR}/tests/ax
```

> 참고: 이후 Phase에서 `.claude/`, `.omc/`, `tests/` 등의 경로는 모두 `${PROJECT_DIR}/` 기준입니다.

### 1.2 도메인 유형 분류 (M4)

`.claude/skills/ax/templates/domain-patterns.md`의 분류기를 참조하여 도메인 유형을 결정합니다:

| 유형 | 키워드 예시 |
|------|------------|
| **code** | 개발, 코딩, API, 앱, SaaS, 풀스택 |
| **document** | 프레젠테이션, 슬라이드, 보고서, 문서 |
| **creative** | 디자인, 브랜딩, 콘텐츠, 마케팅 |
| **research** | 리서치, 분석, 조사, 데이터 분석 |
| **business** | 경영, 전략, 기획, 프로세스 |

복합 도메인이면 주 도메인 1개 + 부 도메인을 기록합니다.

### 1.3 프로젝트 탐색 (code 도메인만)

> **병렬 실행**: 1.3(프로젝트 탐색)과 1.4(도메인 특성 추출)은 독립적이므로 병렬 Agent로 실행 가능합니다.

**도메인 유형이 `code`일 때만 실행** (non-code 도메인은 스킵):

프로젝트 디렉토리에 코드가 있으면 다음을 탐색:

- Glob("package.json") → Node.js/TypeScript
- Glob("pyproject.toml") OR Glob("requirements.txt") → Python
- Glob("go.mod") → Go
- Glob("Cargo.toml") → Rust
- Glob("build.gradle*") → Kotlin/Java
- Glob("src/**") → src 디렉토리 구조 분석
- Glob(".claude/agents/*.md") → 기존 에이전트 목록
- Glob(".claude/skills/*/SKILL.md") → 기존 스킬 목록

**도메인 유형이 non-code일 때**: 대신 콘텐츠 요구사항을 분석합니다:
- 결과물 포맷 (HTML, PDF, PPT, 웹페이지)
- 대상 독자 (경영진, 개발자, 일반 대중)
- 톤앤매너 (전문적, 친근한, 학술적)
- 참조 자료 유형 (웹 검색, 데이터 파일, API)

### 1.4 도메인 특성 추출

사용자 설명에서 다음을 추출:

1. **핵심 동사**: 생성, 분석, 변환, 검증, 리서치, 관리, 모니터링, 배포
2. **입출력 형태**: 코드, 문서, 데이터, 이미지, API, 멀티미디어
3. **품질 요구**: 정확도 우선, 속도 우선, 창의성 우선, 안전성 우선
4. **인터랙션 플로우**: 사용자가 수행할 액션 목록 (클릭 → 폼 제출, 모달 열기, 외부 링크 등)
5. **전환 경로**: CTA → 최종 전환까지의 전체 경로 (예: CTA 클릭 → 모달 → 이메일 입력 → 제출 → 확인)

### 1.5 시그널 맵 생성

위 분석 결과를 종합하여 5가지 시그널을 결정합니다.
결과를 `.omc/ax/domain-analysis.json`에 저장:

```json
{
  "project_type": "{감지된 프로젝트 유형 또는 'non-code'}",
  "domain_type": "{code|document|creative|research|business}",
  "domain_type_secondary": "{부 도메인 유형 또는 null}",
  "domain_sub_type": "{하위 유형 — code: fullstack|api|cli|data-pipeline|devops|mobile, document: presentation|manual|report, 기타: null}",
  "languages": ["{감지된 언어들}"],
  "domain_description": "{사용자 원문}",
  "domain_verbs": ["{추출된 동사들}"],
  "io_types": ["{입출력 형태들}"],
  "quality_priority": "{accuracy|speed|creativity|safety}",
  "output_format": "{html|pdf|code|dashboard|mixed}",
  "signals": {
    "task_dependency": "{sequential|parallel|mixed}",
    "input_variety": "{uniform|varied|highly_varied}",
    "quality_criticality": "{low|medium|high}",
    "team_size_estimate": "{small|medium|large}",
    "runtime_dynamism": "{static|semi_dynamic|highly_dynamic}"
  },
  "existing_agents": ["{기존 에이전트 이름들}"],
  "existing_skills": ["{기존 스킬 이름들}"],
  "interaction_inventory": {
    "cta_actions": ["{CTA별 클릭 후 동작 정의}"],
    "forms": ["{필요한 폼 목록 및 필드}"],
    "conversion_path": "{전체 전환 경로}"
  },
  "flags": {
    "execute": "{true|false}",
    "here": "{true|false}",
    "design": "{supanova|frontend-design|none|auto}"
  }
}
```

### 1.6 출력 계약 검증

domain-analysis.json을 Read하고 다음 필수 필드를 확인합니다:
- `domain_type` ∈ {code, document, creative, research, business}
- `signals.task_dependency` ∈ {sequential, parallel, mixed}
- `signals.quality_criticality` ∈ {low, medium, high}
- `domain_verbs` 배열 길이 >= 2
- `flags.execute`, `flags.here` 존재

누락 필드가 있으면 도메인 설명에서 재추론하여 보정 후 다음 Phase로 진행.

### 1.7 도메인 리서치 (조건부)

> 적용 조건: quality_criticality=high, quality_priority=accuracy, 규제 키워드(FDA/GxP/HIPAA 등) 포함 시 자동 실행.
> 상세 절차: Read `.claude/skills/ax/references/domain-research.md`

도메인 전문 지식을 사전 수집하여 에이전트가 정확한 정보로 작업하도록 합니다.
결과는 `${PROJECT_DIR}/docs/research/{domain}-knowledge-base.md`에 저장됩니다.
quality_criticality=low이고 규제 키워드 없으면 스킵.

## Phase 2: 팀 아키텍처 설계

### 2.1 패턴 선택

`.omc/ax/domain-analysis.json`의 시그널을 읽고, 다음 두 가이드를 참고하여 최적 패턴을 선택합니다:

1. Read: `.claude/skills/ax/templates/domain-patterns.md` — 도메인 유형별 골든 패턴 매핑 확인
2. Read: `.claude/skills/ax/templates/pattern-selection.md` — 시그널 기반 추론 절차

도메인 유형(`domain_type`)에 해당하는 골든 패턴을 우선 참고하고, 시그널을 프롬프트의 `{SIGNALS_JSON}` 위치에 넣어 최종 패턴을 확정합니다.

### 2.2 에이전트 역할 결정

선택된 패턴에 따라 필요한 에이전트 역할을 결정합니다:

**공통 규칙:**
- 모든 팀에 최소 1개 executor + 1개 reviewer 포함
- 모든 팀에 시각화 에이전트 3인조 기본 포함: `visual-architect`(haiku), `visual-builder`(sonnet), `visual-qa`(sonnet)
- 에이전트 수 상한: 최대 10개 (시각화 3인조 포함)

**부 도메인 병합 규칙** (domain_type_secondary가 존재할 때):
- 주 도메인의 에이전트 프리셋을 기본으로 사용
- 부 도메인의 에이전트 프리셋에서 executor 역할 1개를 추가 포함
- 예: creative(주) + code(부) → creative 프리셋 + code의 `code-reviewer` 추가
- 예: document(주) + research(부) → document 프리셋 + research의 `data-collector` 추가

**하위 유형별 프리셋 선택** (domain_sub_type 기반):
- `domain-patterns.md` 섹션 3의 하위 유형별 프리셋을 참조
- code 도메인은 `domain_sub_type`(fullstack/api/cli/data-pipeline/devops/mobile)에 따라 다른 에이전트 조합 사용

**패턴별 역할 템플릿:**
- **파이프라인**: 단계별 1개씩 순차 에이전트
- **팬아웃/팬인**: coordinator(취합) + N개 worker(병렬)
- **전문가 풀**: router(라우팅) + N개 specialist(전문가)
- **생성-검증**: executor(생성) + reviewer(검증) 필수 쌍
- **감독자**: supervisor(감독) + N개 executor(실행)
- **계층적 위임**: manager(관리) + N개 team-lead(팀 리더)

### 2.3 골든 템플릿 매칭

각 에이전트 역할에 대해 기존 검증된 템플릿을 탐색합니다:

```bash
# OMC 에이전트 검색 (우선)
Glob("~/.claude/plugins/cache/*/oh-my-claudecode/*/agents/*.md")

# ECC 에이전트 검색
Glob("~/.claude/plugins/cache/*/everything-claude-code/*/agents/*.md")

# 사용자 커스텀
Glob("~/.claude/agents/*.md")
```

탐색 규칙:
- 가장 높은 버전 디렉토리 선택 (시맨틱 버전 정렬: 4.10.1 > 4.8.2)
- 역할명으로 매칭: executor→executor.md, reviewer→verifier.md
- 템플릿이 0개면 `.claude/skills/ax/templates/agent-skeleton.md` 폴백 사용

### 2.4 스킬 갭 분석

도메인에 필요하지만 기존에 없는 스킬을 식별:
- 기존 스킬 목록 (Phase 1에서 스캔) 확인
- 도메인 동사/입출력과 기존 스킬 description 매칭
- 매칭되지 않는 능력 → "커스텀 스킬 생성 대상"

### 2.4.1 외부 스킬 추천 + 디자인 스킬 자동 적용 (v0.4)

`.claude/skills/ax/templates/external-skill-catalog.md`를 Read하고 다음을 수행합니다:

**A) 디자인 스킬 자동 적용 (Auto-Apply Tier):**

`flags.design` 값에 따라 처리:
- `"auto"` (기본값, 플래그 미지정): `domain_type`이 creative/document이고 `output_format`이 html이면 → supanova-design 자동 선택
- `"supanova"` 또는 `"frontend-design"`: 해당 스킬 명시 선택
- `"none"`: 디자인 스킬 적용 안 함

선택된 디자인 스킬이 있으면:
1. 카탈로그의 "자동 적용 티어" 섹션에서 해당 스킬의 GitHub URL 확인
2. WebFetch로 SKILL.md 콘텐츠를 가져옴
3. `${PROJECT_DIR}/.omc/ax/design-skill-context.md`에 저장
4. Phase 3에서 homepage-builder 에이전트의 `<Process>` 섹션에 "design-skill-context.md를 Read하고 디자인 원칙을 적용하라" 지시를 추가
5. Phase 7에서 homepage-builder 에이전트 프롬프트에 디자인 스킬 콘텐츠를 직접 주입

**B) 일반 외부 스킬 추천:**
1. 카탈로그의 "도메인별 추천 규칙" 참조
2. 이미 설치된 스킬 제외 (Glob으로 `.claude/plugins/` 확인)
3. 추천 목록을 완료 보고에 포함
4. 사용자가 나중에 수동 설치 가능

### 2.4.2 API 계약 생성 (code 도메인 — fullstack/api)

> 적용 조건: domain_sub_type이 fullstack 또는 api이고, backend + frontend가 병렬 실행될 때.
> 상세 절차: Read `.claude/skills/ax/references/api-contract.md`

병렬 에이전트 간 API 응답 구조 불일치를 방지하기 위해 공유 Zod 스키마 + 행동 의도(@intent) + 상태별 응답 변형을 사전 정의합니다.
생성 파일: `${PROJECT_DIR}/src/types/api-contracts.ts`

### 2.4.3 사용자 플로우 시나리오 정의 (code 도메인 — fullstack/api)

> 적용 조건: `domain_sub_type`이 `fullstack` 또는 `api`이고, backend + frontend 에이전트가 병렬 실행될 때만.
> API 계약(2.4.2)이 "어떤 데이터 구조인가"를 정의한다면, 이 단계는 "사용자가 어떤 순서로 어떤 API를 호출하는가"를 정의합니다.

**왜 필요한가:**
스키마만으로는 API의 행동 의도를 전달할 수 없습니다. 같은 `GET /sessions/:id`라도
"세션 상태 조회"와 "퀴즈 문제 로드"는 완전히 다른 의도입니다.
사용자 플로우를 명시하면 백엔드와 프론트엔드가 동일한 행동 모델을 공유합니다.

**절차:**
1. 도메인 분석(Phase 1)의 `domain_verbs`와 인터뷰 결과에서 핵심 사용자 행동 3~5개를 추출
2. 각 행동을 단계별 API 호출 시퀀스로 분해
3. 각 단계에서 요청/응답에 포함되어야 할 필수 데이터 필드를 명시
4. 상태 전이가 있는 경우 (예: active → completed) 상태별 응답 차이를 명시
5. 인증 기반 서비스면 "로그인 → 새로고침 → 세션 유지" 플로우를 반드시 포함

**생성 파일**: `${PROJECT_DIR}/docs/user-flows.md`

**에이전트 프롬프트 삽입 규칙:**
- backend-developer: "각 API가 `docs/user-flows.md`의 어느 단계에서 호출되는지 확인하고, 해당 단계에서 필요한 데이터를 반드시 반환하라."
- frontend-developer: "사용자 플로우의 단계별 시퀀스를 따라 UI를 구현하라. API 호출 순서와 각 단계의 기대 응답을 `docs/user-flows.md`에서 확인하라."

### 2.4.4 CRUD 완성도 매트릭스 정의 (code 도메인 — fullstack/api)

> 적용 조건: `domain_sub_type`이 `fullstack` 또는 `api`이고, CRUD 대상 엔티티가 2개 이상일 때.

**왜 필요한가:**
백엔드가 모든 CRUD API를 구현해도, 프론트엔드가 "눈에 보이는 기능"만 구현하고 나머지를 건너뛰는 패턴이 반복됩니다.
예: 백엔드에 퀴즈 세트 CRUD가 있지만 관리 UI가 없음, 사용자 생성 API가 있지만 생성 버튼이 없음.
CRUD 매트릭스를 사전 정의하면 백엔드/프론트엔드 모두 동일한 기능 범위를 구현합니다.

**절차:**
1. 도메인 분석에서 식별된 핵심 엔티티 목록 추출
2. 각 엔티티에 대해 CRUD + 관련 액션을 정의
3. 각 CRUD 작업에 대해 백엔드 API, 프론트엔드 페이지, 네비게이션 메뉴 존재 여부를 명시
4. 관리자 전용 기능과 일반 사용자 기능을 구분

**생성 파일**: `${PROJECT_DIR}/docs/crud-matrix.md`

```markdown
# CRUD 완성도 매트릭스

## 엔티티별 기능 목록

| 엔티티 | 작업 | 백엔드 API | 프론트 페이지 | 메뉴 | 역할 | 필수 |
|--------|------|-----------|-------------|------|------|------|
| Question | Create | POST /questions | QuestionsPage (모달) | 문제 관리 | admin/instructor | O |
| Question | Read (목록) | GET /questions | QuestionsPage (테이블) | 문제 관리 | admin/instructor | O |
| Question | Read (상세) | GET /questions/:id | QuestionsPage (모달) | - | admin/instructor | O |
| Question | Update | PUT /questions/:id | QuestionsPage (모달) | - | admin/instructor | O |
| Question | Delete | DELETE /questions/:id | QuestionsPage (버튼) | - | admin | O |
| QuizSet | Create | POST /question-sets | QuizSetsPage (폼) | 퀴즈 관리 | admin/instructor | O |
| QuizSet | Read (목록) | GET /question-sets | QuizSetsPage (테이블) | 퀴즈 관리 | admin/instructor | O |
| ... | ... | ... | ... | ... | ... | ... |

## 네비게이션 메뉴 목록

| 메뉴명 | 경로 | 역할 | 포함 엔티티 |
|--------|------|------|-----------|
| 대시보드 | /dashboard | all | Progress |
| 퀴즈 | /quiz | all | QuizSession |
| 오답노트 | /wrong-answers | all | WrongAnswer |
| 문제 관리 | /admin/questions | admin/instructor | Question |
| 퀴즈 관리 | /admin/question-sets | admin/instructor | QuizSet |
| ... | ... | ... | ... |
```

**검증 규칙:**
- "필수=O"인 행은 백엔드 API + 프론트 페이지 + 메뉴가 **모두** 구현되어야 완료
- 백엔드에만 API가 있고 프론트에 UI가 없으면 **불완전** 판정
- 프론트에 hooks만 있고 페이지/컴포넌트에서 사용되지 않으면 **불완전** 판정
- 메뉴에 없으면 사용자가 접근할 수 없으므로 **불완전** 판정

**에이전트 프롬프트 삽입 규칙:**
- backend-developer: "`docs/crud-matrix.md`의 모든 '필수=O' 행에 대해 API를 구현하라. 매트릭스에 없는 API는 구현하지 마라."
- frontend-developer: "`docs/crud-matrix.md`의 모든 '필수=O' 행에 대해 페이지/컴포넌트를 구현하라. 매트릭스의 모든 메뉴를 네비게이션에 포함하라. hooks를 정의만 하고 사용하지 않는 것은 구현이 아니다."

### 2.5 산출물 저장

결과를 `.omc/ax/team-architecture.json`에 저장:

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
  "data_flow": "{SendMessage 또는 TaskCreate}",
  "user_flows": {
    "enabled": true,
    "file": "docs/user-flows.md",
    "flows": ["{핵심 플로우 이름 목록}"],
    "smoke_test_targets": ["{E2E 검증 대상 플로우 이름 목록}"],
    "auth_persistence": "{localStorage|httpOnly|memory+refresh}"
  },
  "crud_matrix": {
    "enabled": true,
    "file": "docs/crud-matrix.md",
    "entities": ["{엔티티 이름 목록}"],
    "total_required_ops": "{필수 작업 수}",
    "menus": ["{메뉴 이름 목록}"]
  }
}
```

### 2.6 출력 계약 검증

team-architecture.json을 Read하고 다음을 확인합니다:
- `pattern.primary` 존재 + 6가지 패턴 중 하나
- `agents` 배열 길이 >= 4 (최소 executor+reviewer+visual 2종)
- 모든 에이전트에 name, role, model 필드 존재
- `skills.gap_create` 배열 존재 (빈 배열 허용)

누락 시 Phase 2를 재실행하여 보정.

## Phase 3: 에이전트 정의 생성

### 3.1 generation-log 초기화

`.omc/ax/generation-log.json` 생성:

```json
{
  "generated_files": [],
  "timestamp": "{현재 시각}",
  "domain": "{도메인 설명}"
}
```

### 3.2 골든 템플릿 로드 및 커스터마이즈

`.omc/ax/team-architecture.json`의 각 에이전트에 대해:

1. **템플릿 로드**:
   - `base_template_path`가 있으면 해당 파일 Read
   - 없으면 `.claude/skills/ax/templates/agent-skeleton.md` Read

2. **frontmatter 커스터마이즈**:
   - `name` → 도메인 맞춤 kebab-case 이름 (예: `content-generator`, `data-analyst`)
   - `description` → 도메인 맞춤 설명 (역할 + 언제 사용하는지 포함)
   - `model` → 유효한 모델 ID만 사용: `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5` (구 ID인 claude-sonnet-4-5, claude-opus-4-5 등은 사용 금지 — validate_project.py에서 FAIL 처리됨)
   - `tools` → 역할에 필요한 도구만 (executor: 전체, reviewer: Read/Grep/Glob만)
   - `role` → team-architecture에서 결정된 역할
   - `triggers` → 도메인 특화 키워드 (비어있으면 안 됨 — 최소 3개 키워드 포함)

3. **본문 커스터마이즈** (XML 태그 필수 — `## Role` 같은 마크다운 헤더 사용 금지):
   - `<Role>` → 도메인 특화 미션, 책임/비책임 범위
   - `<Success_Criteria>` → 도메인 특화 완료 조건
   - `<Constraints>` → 도메인 특화 제약사항
   - `<Process>` → 도메인 특화 워크플로우 단계
     + `.claude/skills/ax/templates/domain-patterns.md` 섹션 6 "도메인별 에이전트 프로세스 필수 단계"를 Read하고, 해당 도메인의 필수 단계를 <Process>에 반영
   - `<Anti_Patterns>` → domain-patterns.md 섹션 6의 도메인별 Anti_Patterns 힌트 적용
   - `<Quality_Gates>` → 도메인 특화 품질 게이트 (검증 가능한 조건)
   - `<Collaboration>` → 선행/후행 에이전트 + 입출력 경로 명시
   - `<Tool_Usage>` → 허용된 도구별 사용 지침

4. **`<Examples>` 자동 생성** (M4):
   도메인 맞춤 Good/Bad 예시를 생성하여 에이전트 품질을 높입니다:
   ```xml
   <Examples>
     <Good>
       입력: {도메인 맞춤 작업 요청}
       출력: {올바른 행동 — 역할에 맞는 도구 사용, 적절한 위임}
     </Good>
     <Bad>
       입력: {도메인 맞춤 작업 요청}
       출력: {잘못된 행동 — 역할 범위 초과, 부적절한 도구 사용}
     </Bad>
   </Examples>
   ```
   각 에이전트에 최소 1개 Good + 1개 Bad 예시를 포함합니다.

### 3.3 충돌 처리

각 에이전트 파일 생성 전:
- `.claude/agents/{name}.md` 존재 여부 확인 (Glob)
- 이미 존재하면: 자동 덮어쓰기 (generation-log에 `"overwritten"` 기록)

### 3.4 파일 생성 및 로그

> **병렬 실행**: 에이전트 파일은 서로 독립적이므로 병렬 Write로 생성 가능합니다. generation-log 업데이트만 순차로.

각 에이전트를 `.claude/agents/{name}.md`에 Write.
생성할 때마다 `.omc/ax/generation-log.json`의 `generated_files` 배열에 파일 경로를 추가.

### 3.5 자동 후처리 + 출력 계약 검증

서브에이전트가 생성한 파일에서 반복 발생하는 문제를 자동 수정합니다. 사람이 수동 수정할 필요를 없앱니다.

**자동 후처리 (검증 전 실행):**
1. triggers 누락 → 에이전트 name/role에서 키워드 추출하여 자동 채움
2. 모델 ID 교정 → `claude-sonnet-4-5` → `claude-sonnet-4-6` 등 구 ID 일괄 교체
3. XML 태그 변환 → `## Role` 마크다운 헤더가 있으면 `<Role>` XML 태그로 변환

**출력 계약 검증 (후처리 후):**
- frontmatter에 name, description, model, role, triggers 필수 필드
- 본문에 `<Role>` 존재 (대체 태그 `<Instructions>`, `<Context>` 허용)
- model 값이 유효한 ID인지 확인
- 누락 항목이 있으면 해당 에이전트 파일만 재생성

## Phase 4: 스킬 생성 (v0.1 — 커스텀만)

### 4.1 커스텀 스킬 생성

`.omc/ax/team-architecture.json`의 `skills.gap_create` 목록에 대해:

각 스킬에 대해 `.claude/skills/ax/templates/skill-skeleton.md`를 기반으로:
1. frontmatter 채우기 (name, description, origin=ax, domain, dependencies)
2. "When to Activate" 섹션 — 이 스킬이 활성화되어야 할 조건 목록
3. "Core Rules" 섹션 — 스킬 실행 시 지켜야 할 핵심 규칙
4. "Process" 섹션 — 단계별 실행 절차
5. "Examples" 섹션 — 사용 예시 1-2개

스킬 파일 생성 전 충돌 확인:
- `.claude/skills/{skill-name}/SKILL.md` 존재 여부 Glob으로 확인
- 이미 존재하면 자동 덮어쓰기

`.claude/skills/{skill-name}/SKILL.md` 경로에 Write (디렉토리 먼저 생성).
`generation-log.json`에 기록.

> 외부 스킬 검색·설치는 v0.2에서 추가 예정.

## Phase 5: 오케스트레이터 생성

### 5.1 오케스트레이션 섹션 생성

`.claude/skills/ax/templates/orchestrator-section.md`를 Read하고 플레이스홀더를 채웁니다:

- `{GENERATION_DATE}` → 현재 날짜
- `{DOMAIN_DESCRIPTION}` → Phase 1의 도메인 설명
- `{PRIMARY_PATTERN}` → Phase 2에서 선택된 주 패턴
- `{SECONDARY_PATTERN_NOTE}` → 보조 패턴이 있으면 `+ {보조패턴}`, 없으면 빈 문자열
- `{AGENT_TABLE_ROWS}` → Phase 3에서 생성된 에이전트 목록으로 마크다운 테이블 행 생성
  - 형식: `| {name} | {role} | {model} | {triggers} |`
- `{DELEGATION_RULES}` → 패턴에 따른 위임 규칙 생성
  - 각 에이전트의 role과 triggers를 기반으로 "어떤 작업 → 어떤 에이전트" 매핑
- `{PATTERN_DESCRIPTION}` → 선택된 패턴의 한 줄 설명
- `{VERIFICATION_POLICY}` → 생성-검증 패턴이면 "모든 생성물은 reviewer 에이전트 통과 필수", 아니면 "주요 산출물은 리뷰 권장"

### 5.2 CLAUDE.md Merge

1. `${PROJECT_DIR}/CLAUDE.md` 존재 여부 확인
2. **존재하면**:
   - 기존 내용 Read
   - `## Harness-Generated Team` 섹션이 이미 있는지 확인 (Grep)
   - 이미 있으면 → 자동 교체 (이전 내용은 generation-log에 백업 경로 기록)
   - 없으면 → 기존 내용 끝에 `\n\n---\n\n` + 오케스트레이션 섹션 append
3. **없으면**: 오케스트레이션 섹션만으로 새 CLAUDE.md 생성

`generation-log.json`에 CLAUDE.md 변경 기록.

## Phase 6: 검증 & 테스트

### 6.1 구조 검증

생성된 모든 파일을 검증합니다:

**에이전트 파일 검증:**
- 각 `.claude/agents/*.md` Read
- frontmatter에 `name`, `description`, `model` 필수 필드 존재 확인
- `model` 값이 유효한 전체 ID인지 확인 (`claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5`)
- 본문에 `<Role>`, `<Success_Criteria>`, `<Constraints>` XML 태그 존재 확인

**스킬 파일 검증:**
- 각 `.claude/skills/*/SKILL.md` Read (ax 자체 스킬 제외)
- frontmatter에 `name`, `description` 필수 필드 존재 확인
- "When to Activate" 섹션 존재 확인

**CLAUDE.md 검증:**
- `## Harness-Generated Team` 섹션 존재 확인
- 에이전트 카탈로그 테이블의 행 수가 생성된 에이전트 수와 일치하는지 확인

**순환 의존성 검사:**
- 위임 규칙에서 A→B→A 같은 순환이 없는지 확인

**의미적 검증 (M4):**
- 역할 충돌: 같은 역할(executor, reviewer 등)의 에이전트가 중복 책임을 가지지 않는지 확인
- 위임 누락: 도메인 동사(`domain_verbs`)에 대응하는 에이전트가 없는 경우 경고
- 트리거 없는 에이전트: `triggers` 필드가 비어있거나 위임 규칙에서 참조되지 않는 에이전트 경고
- `<Examples>` 존재 확인: 모든 에이전트에 Good/Bad 예시가 포함되어 있는지 확인
- 시각화 에이전트 3인조 연결: visual-architect → visual-builder → visual-qa 체인이 위임 규칙에 명시되어 있는지 확인

**CRUD 완성도 검증 (code 도메인 — fullstack/api):**
- `docs/crud-matrix.md`가 존재하는지 확인
- 매트릭스의 '필수=O' 행마다:
  - 백엔드 API 라우트 파일에 해당 HTTP 메서드가 존재하는지 Grep
  - 프론트엔드 hooks 파일에 해당 작업의 hook이 **정의되고 사용되는지** 확인 (정의만 있고 import 안 되면 FAIL)
  - 프론트엔드 페이지 파일이 존재하는지 Glob
  - 네비게이션(TopNav 등)에 해당 메뉴가 포함되어 있는지 Grep
- 매트릭스의 모든 메뉴가 라우터(App.tsx 등)에 등록되어 있는지 확인
- 백엔드에 API가 있지만 프론트에 UI가 없는 엔티티 → 경고 ("백엔드만 구현됨, 프론트 UI 누락")
- hooks가 정의만 되고 어디서도 import/사용되지 않는 경우 → 경고 ("dead hook")

검증 실패 항목이 있으면 즉시 수정 시도.

### 6.2 시나리오 검증

도메인에 맞는 샘플 작업 3개를 자동 생성하고, 각 작업에 대해:
- 어떤 에이전트가 호출되어야 하는지 추론
- 위임 규칙과 일치하는지 확인
- 예상 흐름 문서화 (A → B → C 형태)

### 6.3 검증 결과 저장

구조 검증 결과를 `.omc/ax/validation-report.json`에 저장:

```json
{
  "timestamp": "{현재 시각}",
  "checks": {
    "agent_frontmatter": "{PASS|FAIL}",
    "agent_body_structure": "{PASS|FAIL}",
    "agent_examples": "{PASS|FAIL}",
    "skill_frontmatter": "{PASS|FAIL}",
    "claudemd_section": "{PASS|FAIL}",
    "circular_dependency": "{PASS|FAIL}",
    "semantic_role_conflict": "{PASS|FAIL}",
    "semantic_delegation_gap": "{PASS|FAIL}",
    "semantic_orphan_agent": "{PASS|FAIL}",
    "visual_chain": "{PASS|FAIL}",
    "crud_matrix_exists": "{PASS|FAIL|SKIP}",
    "crud_backend_coverage": "{PASS|FAIL|SKIP}",
    "crud_frontend_coverage": "{PASS|FAIL|SKIP}",
    "crud_menu_coverage": "{PASS|FAIL|SKIP}",
    "crud_dead_hooks": "{PASS|FAIL|SKIP}"
  },
  "overall": "{PASS|FAIL}",
  "failures": ["{실패 항목 상세}"]
}
```

**검증 실패 시 자동 수정 루프 (최대 2회):**

```
검증 FAIL 발생
  → 1회차: 실패 항목을 구조화된 피드백으로 정리
    → Phase 3/4 에이전트에 SendMessage로 수정 요청 (구체적 수정 지시 포함)
    → 수정된 파일만 재검증 (전체 재생성 X)
    → PASS → 완료
    → FAIL → 2회차 반복
  → 2회차 FAIL: 사용자에게 에스컬레이션
    → `.omc/ax/generation-log.json`의 파일 목록을 보여주고
    → "수동 수정 / 롤백(생성 파일 삭제) / 유지(부분 결과 보존)" 선택 요청
    → 롤백 선택 시: generation-log의 `generated_files` 각각 삭제
```

### 6.4 ARCHITECTURE.md 생성

`.claude/skills/ax/templates/architecture-doc.md`를 Read하고 플레이스홀더를 채워서 생성합니다.

충돌 확인: `.claude/ARCHITECTURE.md` 이미 존재하면 → 자동 덮어쓰기.

내용:
- 선택된 패턴과 근거 (Phase 2 결과에서)
- 에이전트 관계도 (텍스트 다이어그램으로 표현)
- 각 에이전트 상세 (이름, 역할, 모델, 도구)
- 스킬 목록
- 데이터 흐름 설명

`.claude/ARCHITECTURE.md`에 Write. `generation-log.json`에 기록.

### 6.5 검증 시나리오 파일 생성

충돌 확인: `tests/ax/scenario-{domain}.md` 이미 존재하면 → 자동 덮어쓰기.

`tests/ax/scenario-{domain}.md` 파일 생성:

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

### 시나리오 2: {작업 설명}
- 예상 에이전트: {에이전트명}
- 예상 흐름: {A → B → C}
- 위임 규칙 일치: {YES/NO}

### 시나리오 3: {작업 설명}
- 예상 에이전트: {에이전트명}
- 예상 흐름: {A → B → C}
- 위임 규칙 일치: {YES/NO}
```

`generation-log.json`에 기록.

### 6.6 완료 보고

모든 Phase 완료 후 사용자에게 요약 보고:

```
AX 에이전트 팀 생성 완료

요약:
  - 패턴: {primary} + {secondary}
  - 에이전트: {N}개 생성
  - 스킬: {N}개 생성
  - 검증: {PASS/FAIL}

생성된 파일:
  {generation-log.json의 generated_files 목록}

다음 단계:
  - 생성된 에이전트를 사용해보세요
  - ARCHITECTURE.md에서 팀 구조를 확인하세요
  - 문제가 있으면 /ax를 다시 실행하세요
```

`--execute` 플래그가 있으면 인터뷰 게이트를 거쳐 Phase 7로 진행합니다.

## Phase 6.7: 인터뷰 게이트 (`--execute` 시 자동 판단)

> `--execute` 플래그가 없으면 이 Phase를 건너뜁니다.

`--execute` + 다음 조건 중 하나 이상 충족 시, Phase 7 실행 전에 인터뷰를 제안합니다:
- `domain_type` = `code`
- `quality_priority` = `safety` 또는 `accuracy`
- `domain_sub_type` = `fullstack` 또는 `api`

**`--interview` 플래그가 이미 있으면**: 인터뷰 게이트를 건너뛰고 바로 인터뷰 프로세스를 실행합니다.

**자동 제안 메시지**:
```
이 프로젝트는 {domain_type} 도메인입니다.
실행 전에 plan과 architecture를 상세하게 설계하면 결과물 품질이 높아집니다.

1) 인터뷰 진행 — 질의응답으로 plan/architecture를 확정한 뒤 실행
2) 바로 실행 — AI가 자동 판단하여 즉시 실행

선택하세요 (1/2):
```

사용자가 **1)** 선택 시:
- Read: `.claude/skills/ax/references/interview-mode.md` — 인터뷰 프로세스 실행
- 인터뷰 완료 후 `${PROJECT_DIR}/docs/plan.md`, `docs/architecture.md`, `docs/user-flows.md` 생성
- 사용자 확인 게이트 → 수정 가능 → 확인 후 Phase 7 진행

사용자가 **2)** 선택 시:
- 기존 무중단 흐름으로 Phase 7 즉시 진행

## Phase 7: 실행 (`--execute` 전용)

> `--execute` 플래그가 없으면 이 Phase를 건너뜁니다.

상세 절차는 다음 reference 파일을 Read하세요:
- Read: `.claude/skills/ax/references/phase-7-execute.md` — 시각화 파이프라인, 에러 복구, 피드백 루프

Phase 1~6에서 생성된 에이전트 팀으로 도메인 작업을 즉시 수행합니다.
인터뷰 게이트에서 `docs/plan.md`, `docs/architecture.md`가 생성된 경우, 에이전트 실행 시 해당 문서를 컨텍스트로 주입합니다.
순서: visual-architect(토큰) → 도메인 에이전트(콘텐츠) → visual-qa(검증, 45/60+ PASS)

### 디자인 스킬 주입 (Phase 7에서 자동)

`${PROJECT_DIR}/.omc/ax/design-skill-context.md`가 존재하면 (Phase 2.4.1에서 생성):

1. **homepage-builder 에이전트** 프롬프트에 디자인 스킬 콘텐츠를 `## Supanova Design Engine Rules` 섹션으로 주입:
   - "다음 디자인 규칙을 반드시 적용하세요. 이 규칙은 프로젝트의 디자인 품질 기준입니다."
   - 디자인 스킬 콘텐츠 전체를 프롬프트에 포함

2. **visual-architect 에이전트** 프롬프트에 디자인 스킬의 컬러/폰트 규칙만 발췌 주입:
   - 금지 폰트 목록 (Inter, Roboto, Noto Sans KR 등)
   - 권장 폰트 (Pretendard 등)
   - 금지 색상 패턴 (보라색/AI 그라디언트)
   - 금지 레이아웃 (3열 균등 카드)

3. **visual-qa 에이전트** 프롬프트에 디자인 스킬의 안티패턴 체크리스트 주입:
   - AI Tell 검사 항목 추가 (금지 폰트, 금지 레이아웃, 금지 색상)
   - Pre-flight Checklist 항목 추가

이 주입은 에이전트 정의 파일(.claude/agents/*.md)을 수정하는 것이 **아니라**, Phase 7 Agent 호출 시 프롬프트에 동적으로 추가하는 것입니다.

---

## 확장 기능 (상세는 references/ 참조)

- **인터뷰 모드** (`--interview`): Read `.claude/skills/ax/references/interview-mode.md`
- **에이전트 재사용 라이브러리**: Read `.claude/skills/ax/references/agent-reuse-library.md`
- **마켓플레이스 통합**: Read `.claude/skills/ax/references/marketplace.md`
