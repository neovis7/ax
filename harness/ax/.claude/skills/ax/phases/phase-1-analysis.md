# Phase 1: 도메인 분석

## 입력 파싱

사용자 입력을 파싱합니다:
- `--here` 플래그 존재 여부 확인 → 현재 디렉토리에 에이전트 생성
- `--execute` 플래그 존재 여부 확인 → Phase 6 완료 후 Phase 7(실행) 진행
- `--interview` 플래그 존재 여부 확인 → Phase 1에서 인터뷰 모드 실행
- `--design {value}` 플래그 확인 → 디자인 스킬 선택:
  - `--design supanova` → supanova-design 명시적 적용
  - `--design frontend-design` → Anthropic frontend-design 적용
  - `--design none` → 디자인 스킬 자동 적용 비활성화
  - 플래그 없음 → creative/document + html 도메인이면 supanova-design 자동 적용
- `--skip-interview` 플래그 존재 여부 확인 → `--execute` 시 인터뷰를 건너뛰고 기본값으로 실행
- 나머지 텍스트를 도메인 설명으로 사용

## 1.0 프로젝트 디렉토리 결정

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

## 1.1 작업 디렉토리 초기화

```bash
mkdir -p ${PROJECT_DIR}/.claude/agents
mkdir -p ${PROJECT_DIR}/.claude/skills
mkdir -p ${PROJECT_DIR}/.omc/ax
mkdir -p ${PROJECT_DIR}/tests/ax
```

> 참고: 이후 Phase에서 `.claude/`, `.omc/`, `tests/` 등의 경로는 모두 `${PROJECT_DIR}/` 기준입니다.

## 1.2 도메인 유형 분류 (M4)

`.claude/skills/ax/templates/domain-patterns.md`의 분류기를 참조하여 도메인 유형을 결정합니다:

| 유형 | 키워드 예시 |
|------|------------|
| **code** | 개발, 코딩, API, 앱, SaaS, 풀스택 |
| **document** | 프레젠테이션, 슬라이드, 보고서, 문서 |
| **creative** | 디자인, 브랜딩, 콘텐츠, 마케팅 |
| **research** | 리서치, 분석, 조사, 데이터 분석 |
| **business** | 경영, 전략, 기획, 프로세스 |

복합 도메인이면 주 도메인 1개 + 부 도메인을 기록합니다.

## 1.3 프로젝트 탐색 (code 도메인만)

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

## 1.4 도메인 특성 추출

사용자 설명에서 다음을 추출:

1. **핵심 동사**: 생성, 분석, 변환, 검증, 리서치, 관리, 모니터링, 배포
2. **입출력 형태**: 코드, 문서, 데이터, 이미지, API, 멀티미디어
3. **품질 요구**: 정확도 우선, 속도 우선, 창의성 우선, 안전성 우선
4. **인터랙션 플로우**: 사용자가 수행할 액션 목록 (클릭 → 폼 제출, 모달 열기, 외부 링크 등)
5. **전환 경로**: CTA → 최종 전환까지의 전체 경로 (예: CTA 클릭 → 모달 → 이메일 입력 → 제출 → 확인)

## 1.5 시그널 맵 생성

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
  "output_format": "{html|pdf|pptx|xlsx|docx|code|dashboard|mixed}",
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
    "design": "{supanova|frontend-design|none|auto}",
    "design_extras": ["{impeccable|taste-skill|better-icons|make-interfaces-feel-better|...}"],
    "design_recipe": "{레시피명 또는 null — Phase 2.4.1에서 자동 매칭 또는 인터뷰에서 선택}",
    "ppt_style": "{glassmorphism|dark-premium|gradient-modern|neo-brutalist|3d-isometric|editorial|minimal-swiss|keynote|null}",
    "skip_interview": "{true|false — --skip-interview 플래그 여부}"
  }
}
```

## 1.6 출력 계약 검증

domain-analysis.json을 Read하고 다음 필수 필드를 확인합니다:
- `domain_type` ∈ {code, document, creative, research, business}
- `output_format` ∈ {html, pdf, pptx, xlsx, docx, code, dashboard, mixed}
- `signals.task_dependency` ∈ {sequential, parallel, mixed}
- `signals.quality_criticality` ∈ {low, medium, high}
- `domain_verbs` 배열 길이 >= 2
- `flags.execute`, `flags.here` 존재

누락 필드가 있으면 도메인 설명에서 재추론하여 보정 후 다음 Phase로 진행.

## 1.7 도메인 리서치 (조건부)

> 적용 조건: quality_criticality=high, quality_priority=accuracy, 규제 키워드(FDA/GxP/HIPAA 등) 포함 시 자동 실행.
> 상세 절차: Read `.claude/skills/ax/references/domain-research.md`

도메인 전문 지식을 사전 수집하여 에이전트가 정확한 정보로 작업하도록 합니다.
결과는 `${PROJECT_DIR}/docs/research/{domain}-knowledge-base.md`에 저장됩니다.
quality_criticality=low이고 규제 키워드 없으면 스킵.
