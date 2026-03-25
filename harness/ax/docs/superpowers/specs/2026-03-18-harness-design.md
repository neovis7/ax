# Harness 상세 설계 스펙

> 날짜: 2026-03-18
> 상태: Draft
> 접근 방식: Adaptive Agent Factory (접근 2)

## 1. 개요

Harness는 도메인 설명을 입력하면 Claude Code용 에이전트 팀(agents, skills, orchestrator)을 자동 생성하는 메타 도구.
코딩뿐 아니라 리서치, 문서 작성, PDF→PPT 변환 등 일반 업무도 완전 자동화 대상.

### 핵심 차별점

- **골든 템플릿 기반**: OMC/ECC의 검증된 에이전트 구조를 템플릿으로 활용
- **외부 스킬 통합**: Anthropic 공식 스킬, GitHub, 마켓플레이스에서 최적 스킬 검색·설치
- **Skill Resolver**: 런타임에 능력 갭 발견 시 동적으로 스킬 보충
- **6가지 아키텍처 패턴 자동 선택**: 도메인 시그널 기반 점수 매기기

### 사용 형태

```bash
# 기본: 완전 자동
/harness "이커머스 플랫폼 - 상품 관리, 주문 처리, 고객 지원"

# 인터뷰 모드: deep-interview 기반 요구사항 명확화
/harness --interview "데이터 분석 파이프라인"
```

### 생성 결과물

```
.claude/
  agents/*.md          에이전트 정의
  skills/*.md          스킬 정의 (외부 설치 + 커스텀 생성)
  CLAUDE.md            오케스트레이션 규칙 (기존 파일에 merge)
  ARCHITECTURE.md      에이전트 관계도, 데이터 흐름, 패턴 설명
tests/
  harness/*.md         검증 시나리오
```

---

## 2. 에이전트 스키마 (Agent Schema v1)

### 분석 배경

현존하는 3가지 스키마 변형을 통합:

| 출처 | frontmatter | 본문 구조 |
|------|------------|----------|
| ECC 에이전트 | `name, description, tools[], model` | 마크다운 |
| OMC 에이전트 | `name, description, model, disallowedTools` | XML 구조 |
| Anthropic 공식 스킬 | `name, description` | 마크다운 |

### 에이전트 frontmatter

```yaml
---
name: {agent-name}                    # 필수: kebab-case
description: {한 줄 설명}              # 필수: 언제 사용하는지 포함
model: claude-sonnet-4-6              # 필수: 전체 모델 ID (기본: claude-sonnet-4-6)
tools: ["Read", "Grep", "Glob"]      # 선택: 허용 도구 목록 (YAML 배열)
disallowedTools: Write, Edit          # 선택: 금지 도구 (쉼표 구분 문자열, OMC 호환)
role: executor                        # [신규] 선택: 오케스트레이터 위임용
triggers: ["keyword1", "keyword2"]   # [신규] 선택: 자동 활성화 키워드
---
```

**모델 ID 매핑표:**

| 단축명 | 전체 모델 ID | 용도 |
|--------|-------------|------|
| haiku | `claude-haiku-4-5` | 경량 탐색, 빠른 조회 |
| sonnet | `claude-sonnet-4-6` | 일반 구현, 리뷰 (기본값) |
| opus | `claude-opus-4-6` | 아키텍처, 심층 분석 |

> Harness는 생성 시 **전체 모델 ID**를 사용. OMC 환경과 직접 호환.
> ECC 환경(단축명 사용)에서는 단축명으로 자동 변환하는 후처리 옵션 제공.

**필드 규칙:**
- `tools`(YAML 배열)와 `disallowedTools`(쉼표 구분 문자열)는 상호 배타적. 둘 다 없으면 모든 도구 허용.
- `disallowedTools` 포맷: OMC 실제 형식인 쉼표 구분 문자열 채택 (`Write, Edit`), YAML 배열 아님.
- `role`은 **신규 필드** (기존 OMC/ECC에 없음). 오케스트레이터 CLAUDE.md의 위임 규칙에서 참조. Claude Code 로더가 미인식 필드를 무시하므로 호환성 문제 없음.
- `triggers`는 **신규 필드** (기존에 없음). 스킬의 `description` 기반 자동 라우팅을 보완. 명시적 키워드 매칭으로 정확도 향상.
- `role` 허용값: `executor | reviewer | planner | researcher | specialist`

**오케스트레이터 위임 알고리즘 (role 사용):**
```
1. 사용자 작업 수신
2. 작업 유형 분류: 구현 → executor, 검증 → reviewer, 기획 → planner, 조사 → researcher
3. role이 일치하는 에이전트 후보군 필터링
4. description 유사도로 최종 선택
5. 해당 에이전트에게 SendMessage로 위임
```

### 에이전트 본문 구조

OMC의 XML 구조 채택 (명확한 경계 제공):

```markdown
# {Agent Name}

<Role>
  한 문장 미션 정의.
  - 책임: ...
  - 비책임: ...
</Role>

<Success_Criteria>
  - 완료 조건 1
  - 완료 조건 2
</Success_Criteria>

<Constraints>
  - 제약 1: 설명
  - 제약 2: 설명
</Constraints>

<Process>
  1) 단계 1: 설명
  2) 단계 2: 설명
  3) 단계 3: 설명
</Process>

<Tool_Usage>
  - Read: 용도 설명
  - Bash: 용도 설명
</Tool_Usage>
```

**설계 근거:**
- XML 태그는 LLM이 섹션 경계를 명확히 인식 → 지시 따르기 정확도 향상
- OMC executor, verifier 등에서 이미 검증된 구조
- ECC 마크다운 에이전트보다 구조화된 출력 생성에 유리

### 완성된 에이전트 파일 예시

이커머스 도메인에서 생성된 `content-generator.md`의 완전한 예시:

```markdown
---
name: content-generator
description: >-
  이커머스 상품 설명, 마케팅 카피, SEO 콘텐츠를 생성.
  "상품 설명 작성", "마케팅 카피" 등의 작업에 자동 활성화.
model: claude-sonnet-4-6
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
role: executor
triggers: ["상품 설명", "마케팅 카피", "콘텐츠 생성"]
---

# Content Generator

<Role>
  이커머스 상품의 매력적인 콘텐츠를 생성하는 전문 에이전트.
  - 책임: 상품 설명, 마케팅 카피, SEO 메타 데이터, 카테고리 설명 작성
  - 비책임: 가격 결정, 재고 관리, 이미지 생성, 콘텐츠 품질 검증 (quality-checker 담당)
</Role>

<Success_Criteria>
  - 생성된 콘텐츠가 브랜드 톤앤매너와 일치
  - SEO 키워드가 자연스럽게 포함
  - 상품 특성(스펙, 장점, 사용법)이 정확히 반영
  - quality-checker 에이전트의 검증을 통과
</Success_Criteria>

<Constraints>
  - 허위 또는 과장된 상품 정보 작성 금지
  - 경쟁사 비방 콘텐츠 생성 금지
  - 기존 상품 데이터(스펙, 가격)를 임의로 변경하지 않음
  - 콘텐츠 생성 후 반드시 quality-checker에게 검증 요청
</Constraints>

<Process>
  1) 상품 데이터 수집: 기존 상품 정보, 카테고리, 타겟 고객 분석
  2) 콘텐츠 전략 수립: 톤, 키워드, 강조 포인트 결정
  3) 초안 생성: 상품 설명, 마케팅 카피, SEO 메타 데이터 작성
  4) 자체 검토: 정확성, 톤 일관성, 키워드 밀도 확인
  5) 검증 요청: SendMessage로 quality-checker에게 전달
</Process>

<Tool_Usage>
  - Read: 기존 상품 데이터, 브랜드 가이드라인 참조
  - Write: 새 콘텐츠 파일 생성
  - Edit: 기존 콘텐츠 수정
  - Grep: 기존 콘텐츠에서 패턴, 키워드 사용 분석
  - Glob: 상품 데이터 파일 탐색
</Tool_Usage>
```

---

## 3. 스킬 스키마 (Skill Schema v1)

### 스킬 frontmatter

**호환성 계층:**

| 계층 | 필드 | 대상 환경 |
|------|------|----------|
| Anthropic 호환 | `name`, `description` | 모든 Claude Code 환경 |
| Harness 확장 | + `origin`, `domain`, `dependencies` | Harness 생성 환경 |
| OMC 파이프라인 | + `argument-hint`, `pipeline`, `next-skill`, `next-skill-args`, `handoff` | OMC 체이닝 |

**Anthropic 호환 (최소):**
```yaml
---
name: {skill-name}                    # 필수: kebab-case
description: {언제 사용하고 뭘 하는지}  # 필수
---
```

**Harness 확장:**
```yaml
---
name: {skill-name}                    # 필수: kebab-case
description: {언제 사용하고 뭘 하는지}  # 필수
origin: {harness|anthropic|community|marketplace}  # Harness 전용: 출처 추적
domain: {coding|research|document|business|creative}  # Harness 전용: 도메인 분류
dependencies: ["skill-a", "mcp-b"]   # Harness 전용: 의존 스킬/MCP
---
```

**OMC 파이프라인 (체이닝 필요 시):**
```yaml
---
name: {skill-name}
description: {설명}
origin: harness
domain: business
argument-hint: '"프로젝트 설명"'       # 선택: 사용자에게 인자 힌트
pipeline: true                        # 선택: 다음 스킬로 자동 연결
next-skill: {다음-스킬-이름}           # 선택: 파이프라인 다음 단계
next-skill-args: "--flag value"       # 선택: 다음 스킬에 전달할 인자
handoff: true                         # 선택: 완료 후 다음 스킬에 제어권 이관
---
```

**필드별 설계 근거:**
- `origin`: 스킬 업데이트 시 원본 소스로 추적 가능
- `dependencies`: MCP 서버나 다른 스킬이 필요한 경우 자동 설치
- `domain`: Skill Resolver가 검색 시 필터링에 사용
- `pipeline`/`next-skill`/`handoff`: OMC의 다단계 워크플로우에 필수. `deep-interview → plan`, `plan → execute` 등 체이닝 지원
- 미인식 필드는 vanilla Claude Code에서 무시됨 → 하위 호환성 유지

### 스킬 본문 구조

Anthropic 공식과 동일:

```markdown
# {Skill Name}

## When to Activate
- 트리거 조건 1
- 트리거 조건 2

## Core Rules
1. 규칙 1
2. 규칙 2

## Process
단계별 실행 방법

## Examples
사용 예시
```

---

## 4. 아키텍처 패턴 자동 선택

### 6가지 패턴

| 패턴 | 핵심 특성 | 적합 도메인 |
|------|----------|------------|
| 파이프라인 | 순차 의존성 강함 | CI/CD, 문서 변환 체인 |
| 팬아웃/팬인 | 독립 작업 N개 → 취합 | 다국어 번역, 병렬 리서치 |
| 전문가 풀 | 입력 유형별 다른 처리 | 고객 지원, 멀티포맷 |
| 생성-검증 | 품질 게이트가 핵심 | 코드 생성, 콘텐츠 작성 |
| 감독자 | 동적 작업 할당·재시도 | 프로젝트 관리, 복잡 업무 |
| 계층적 위임 | 다수 하위 팀·도메인 교차 | 엔터프라이즈 시스템 |

### 자동 선택 시그널

Phase 1 도메인 분석에서 5가지 시그널 추출:

```
시그널                  값 범위                       추출 방법
───────────────────── ──────────────────────────── ─────────────────────
task_dependency        sequential|parallel|mixed     작업 간 의존성 분석
input_variety          uniform|varied|highly_varied  입출력 형태 다양성
quality_criticality    low|medium|high               품질 요구 수준
team_size_estimate     small(2-3)|medium(4-6)|large(7+)  필요 역할 수
runtime_dynamism       static|semi_dynamic|highly_dynamic  실행 중 변동성
```

### 판단 방법: 프롬프트 기반 추론 (코드 아님)

패턴 선택은 LLM이 시그널과 예시를 보고 추론하는 방식. 의사코드가 아닌 **구조화된 프롬프트 템플릿**으로 구현.

#### 패턴 선택 프롬프트 템플릿

```
당신은 에이전트 팀 아키텍트입니다. 도메인 분석 시그널을 보고 최적의 아키텍처 패턴을 선택하세요.

## 사용 가능한 패턴

1. **파이프라인**: 작업이 A→B→C 순서로 흘러가며, 각 단계 출력이 다음 단계 입력이 됨
2. **팬아웃/팬인**: N개 독립 작업을 병렬 수행 후 결과를 취합
3. **전문가 풀**: 입력 유형에 따라 서로 다른 전문가에게 라우팅
4. **생성-검증**: 생성물을 만들고 별도 검증 에이전트가 품질 확인
5. **감독자**: 중앙 감독자가 동적으로 작업 분배, 재시도, 우선순위 조정
6. **계층적 위임**: 상위 관리자가 하위 팀 리더에게 위임, 각 팀이 독립 수행

## 도메인 시그널

{signals_json}

## 추론 절차

1. 각 패턴이 이 도메인에 적합한 이유와 부적합한 이유를 한 문장씩 서술
2. 가장 적합한 패턴 1개 선택 (primary)
3. 보조 패턴이 필요한지 판단 — 필요하면 합성 가능한 조합인지 확인
4. 선택 근거를 2-3 문장으로 설명

## 출력 형식

primary_pattern: {패턴명}
secondary_pattern: {패턴명 또는 "없음"}
confidence: {high|medium|low}
rationale: {선택 근거}
```

#### 워크드 예시 (Worked Examples)

**예시 1: 이커머스 고객 지원 자동화**
```
시그널:
  task_dependency: mixed (문의 유형에 따라 다름)
  input_variety: highly_varied (환불, 배송, 상품문의, 기술지원)
  quality_criticality: high (고객 대면)
  team_size_estimate: medium (4-6)
  runtime_dynamism: semi_dynamic

선택: 전문가 풀 + 생성-검증
근거: 입력 유형이 매우 다양하므로 유형별 전문가 라우팅이 핵심.
      고객 대면이라 품질 게이트(생성-검증)를 합성.
```

**예시 2: 다국어 문서 번역 파이프라인**
```
시그널:
  task_dependency: parallel (각 언어 독립)
  input_variety: uniform (모두 같은 원문)
  quality_criticality: medium
  team_size_estimate: medium (4-6)
  runtime_dynamism: static

선택: 팬아웃/팬인
근거: 동일 원문을 N개 언어로 독립 병렬 번역 후 취합.
      순차 의존성 없고 입력이 균일하므로 팬아웃이 최적.
```

**예시 3: SaaS 플랫폼 풀스택 개발**
```
시그널:
  task_dependency: mixed (프론트/백/DB 병렬 가능하나 API 계약 의존)
  input_variety: varied (UI, API, DB, 테스트)
  quality_criticality: high (프로덕션)
  team_size_estimate: large (7+)
  runtime_dynamism: semi_dynamic

선택: 계층적 위임 + 생성-검증
근거: 팀 규모가 크고 도메인이 교차하므로 계층적 위임.
      프로덕션 품질이 필요하므로 생성-검증을 합성.
```

**예시 4: CI/CD 파이프라인 구축**
```
시그널:
  task_dependency: sequential (빌드→테스트→배포)
  input_variety: uniform (코드)
  quality_criticality: high (배포 안전)
  team_size_estimate: small (2-3)
  runtime_dynamism: static

선택: 파이프라인 + 생성-검증
근거: 순차 의존성이 강하므로 파이프라인이 자연스러움.
      배포 안전이 중요하므로 각 단계마다 검증 게이트 합성.
```

**예시 5: 리서치 보고서 작성**
```
시그널:
  task_dependency: mixed (수집은 병렬, 작성은 순차)
  input_variety: varied (웹, 논문, 데이터)
  quality_criticality: medium
  team_size_estimate: small (2-3)
  runtime_dynamism: semi_dynamic

선택: 감독자
근거: 리서치 진행에 따라 동적으로 추가 조사가 필요하고,
      소스 품질에 따라 재시도가 빈번. 감독자가 적응적으로 관리.
```

#### 합성 가능 조합

| 주 패턴 | 보조 패턴 | 합성 방식 |
|---------|----------|----------|
| 팬아웃/팬인 | 생성-검증 | 병렬 생성 → 각각 검증 후 취합 |
| 감독자 | 전문가 풀 | 감독자가 유형 판단 후 전문가에게 분배 |
| 파이프라인 | 생성-검증 | 각 파이프라인 단계마다 검증 게이트 |
| 계층적 위임 | 생성-검증 | 각 하위 팀에 생성-검증 사이클 적용 |
| 전문가 풀 | 생성-검증 | 전문가 응답마다 품질 검증 |

---

## 5. Skill Resolver 아키텍처

### 개요

생성된 에이전트 팀에 자동 포함되는 런타임 에이전트. 작업 중 능력 갭을 감지하면 외부에서 스킬을 검색·평가·설치.

### 아키텍처

```
┌─────────────────────────────────────────────────┐
│              Orchestrator (CLAUDE.md)             │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │       │
│  │ (domain) │  │ (domain) │  │ (verify) │       │
│  └────┬─────┘  └────┬─────┘  └──────────┘       │
│       │              │                            │
│       └──────┬───────┘                            │
│              ▼                                    │
│  ┌────────────────────────────┐                   │
│  │     Skill Resolver         │                   │
│  │                            │                   │
│  │  검색 우선순위:            │                   │
│  │  1. 로컬 .claude/skills/   │                   │
│  │  2. ~/.claude/skills/      │                   │
│  │  3. anthropics/skills repo │                   │
│  │  4. GitHub code search     │                   │
│  │  5. 골든 템플릿 기반 생성  │                   │
│  └────────────────────────────┘                   │
└─────────────────────────────────────────────────┘
```

### Skill Resolver 에이전트 정의 (v0.3 이후)

> **중요: v0.1/v0.2에서는 Skill Resolver를 생성된 팀에 포함하지 않음.**
> v0.3에서 명시적 에스컬레이션 프로토콜과 함께 도입.

```yaml
---
name: skill-resolver
description: >-
  다른 에이전트가 SendMessage로 명시적 요청 시 외부 스킬을 검색·평가·설치.
  트리거 키워드 자동 감지가 아닌, 구조화된 요청 메시지로만 호출됨.
model: claude-sonnet-4-6
tools: ["Read", "Write", "Glob", "Grep"]
disallowedTools: WebFetch, WebSearch, Bash
role: specialist
---
```

> v0.3에서 `disallowedTools`를 완화하여 WebFetch, Bash 허용 예정.
> v0.1-v0.2에서는 로컬 스킬 검색만 가능하도록 제한.

### 호출 프로토콜 (v0.3, 키워드 트리거 아님)

다른 에이전트가 능력 갭을 인식하면 **명시적 SendMessage**로 요청:

```
SendMessage(to: "skill-resolver", message: {
  "request": "find_skill",
  "task_description": "PDF를 분석해서 핵심 내용 추출",
  "required_capability": "pdf-extraction",
  "domain": "document",
  "urgency": "blocking"  // blocking: 이 스킬 없이 진행 불가 | nice_to_have
})
```

### 검색·설치 프로세스

```
1. 요청 수신 (SendMessage, 키워드 자동 감지 아님)
   - 구조화된 요청 메시지 파싱
   - urgency에 따라 처리 우선순위 결정

2. 로컬 검색 (v0.1부터 사용 가능)
   - Glob: .claude/skills/**/*.md, ~/.claude/skills/**/*.md
   - 매칭: description + domain 기반 유사도

3. Anthropic 공식 검색 (v0.2부터)
   - WebFetch: raw.githubusercontent.com/anthropics/skills/main/skills/
   - 카테고리 매칭: Creative, Development, Enterprise, Document

4. GitHub 검색 (v0.3부터)
   - Bash: gh search code "SKILL.md" + domain keywords
   - 결과 평가: stars, 최근 업데이트, 설명 관련도

5. 평가 & 설치
   - 후보 스킬 1-3개 선별
   - 평가 기준: 관련도, 품질(구조 완성도), 의존성 부담
   - 선택된 스킬을 .claude/skills/ 에 설치
   - CLAUDE.md 스킬 카탈로그에 추가

6. 생성 폴백
   - 위 단계에서 적합한 스킬이 없으면
   - 골든 템플릿 + 도메인 지식으로 커스텀 스킬 생성
```

---

## 6. Phase별 구현 전략

### Phase 1: 도메인 분석

**입력:** 사용자 설명 (텍스트) + 프로젝트 디렉토리 (선택)

**분석 항목:**

```
A. 프로젝트 유형 감지 (코드베이스 있으면)
   - 언어/프레임워크: package.json, pyproject.toml, go.mod, Cargo.toml
   - 아키텍처: src/ 구조, 설정 파일, 디렉토리 패턴
   - 기존 에이전트/스킬: .claude/ 디렉토리 스캔

B. 도메인 특성 추출 (사용자 설명 기반)
   - 핵심 동사: 분석, 생성, 변환, 검증, 리서치, 관리, 모니터링
   - 입출력 형태: 코드, 문서, 데이터, 이미지, API, 멀티미디어
   - 품질 요구: 정확도 우선, 속도 우선, 창의성 우선, 안전성 우선

C. 시그널 맵 생성
   - 5가지 시그널 점수 산출
   - 패턴 추천 후보 3개 + 각 근거
```

**실행 에이전트:** `explore` (haiku) → `analyst` (opus)

**산출물:** `domain-analysis.json`

```json
{
  "project_type": "web-app",
  "languages": ["typescript", "python"],
  "frameworks": ["nextjs", "fastapi"],
  "domain_verbs": ["generate", "analyze", "convert"],
  "io_types": ["code", "document", "api"],
  "signals": {
    "task_dependency": "mixed",
    "input_variety": "varied",
    "quality_criticality": "high",
    "team_size_estimate": "medium",
    "runtime_dynamism": "semi_dynamic"
  },
  "existing_agents": ["planner.md", "code-reviewer.md"],
  "existing_skills": ["tdd-workflow", "security-review"]
}
```

### Phase 2: 팀 아키텍처 설계

**입력:** Phase 1 `domain-analysis.json`

**실행:**
1. 패턴 자동 선택 (섹션 4 알고리즘)
2. 에이전트 역할 결정
   - 골든 템플릿 매칭: OMC 에이전트 카탈로그에서 유사 역할 찾기
   - 도메인 특화 에이전트 정의: 골든 템플릿 커스터마이즈
3. 스킬 매칭
   - 로컬 스킬 스캔 → Anthropic 공식 매칭 → GitHub 검색
   - 갭 분석: 필요하지만 없는 스킬 식별
4. 데이터 흐름 설계
   - 에이전트 간 통신: SendMessage (실시간) vs TaskCreate (비동기)
   - 공유 상태: `.omc/state/` 활용

**실행 에이전트:** `planner` (opus)

**산출물:** `team-architecture.json`

```json
{
  "pattern": {
    "primary": "생성-검증",
    "secondary": "팬아웃",
    "confidence": "high",
    "rationale": "품질 중요도 높고 병렬 생성 가능한 작업 구조"
  },
  "agents": [
    {
      "name": "content-generator",
      "base_template": "executor",
      "role": "executor",
      "model": "claude-sonnet-4-6",
      "customization": "도메인 특화 콘텐츠 생성"
    },
    {
      "name": "quality-checker",
      "base_template": "verifier",
      "role": "reviewer",
      "model": "claude-sonnet-4-6",
      "customization": "도메인 기준 품질 검증"
    }
  ],
  "skills": {
    "existing_match": ["article-writing", "market-research"],
    "anthropic_install": ["document-skills/pptx"],
    "gap_create": ["domain-specific-analysis"]
  },
  "data_flow": "SendMessage (실시간 협업)"
}
```

### Phase 3: 에이전트 정의 생성

**입력:** Phase 2 `team-architecture.json`

**골든 템플릿 로딩 메커니즘:**

> 템플릿은 하드코딩된 경로가 아닌 **동적 탐색**으로 로드.
> 플러그인 버전 업데이트에도 안정적으로 동작.

```
탐색 우선순위:
  1. ~/.claude/plugins/cache/omc/oh-my-claudecode/*/agents/*.md  (OMC)
  2. ~/.claude/plugins/cache/*/everything-claude-code/*/agents/*.md  (ECC)
  3. ~/.claude/agents/*.md  (사용자 커스텀)

탐색 방법:
  - Glob("~/.claude/plugins/cache/*/oh-my-claudecode/*/agents/*.md")
  - 결과에서 가장 높은 버전 디렉토리 선택 (시맨틱 버전 정렬: 4.10.1 > 4.8.2)
  - 각 템플릿의 frontmatter에서 name, description, model 추출
  - base_template 필드로 매칭: "executor" → executor.md 로드
  - 폴백: 템플릿이 0개 발견 시 → 섹션 2의 본문 구조 스켈레톤으로 처음부터 생성
```

**실행:**
1. 골든 템플릿 동적 탐색 및 로드
2. 도메인 맞춤 커스터마이즈 (복사 후 수정, 원본 보존)
   - `<Role>` → 도메인 특화 미션으로 교체
   - `<Constraints>` → 도메인 특화 제약 추가
   - `<Process>` → 도메인 특화 워크플로우로 교체
   - `<Tool_Usage>` → 필요 도구만 남기기
   - frontmatter `name`, `description` → 도메인 맞춤 변경
3. `.claude/agents/*.md` 파일 Write
   - **충돌 처리**: 동명 에이전트 파일 존재 시 → 사용자에게 덮어쓰기/건너뛰기 확인
4. v0.1에서는 skill-resolver **미포함** (v0.3 이후 자동 포함)

**실행 에이전트:** `executor` (sonnet, complex → opus)

**산출물:** `.claude/agents/*.md` 파일들

### Phase 4: 스킬 생성 + 외부 설치

**입력:** Phase 2 스킬 매칭 결과

**실행:**
1. 외부 스킬 설치
   - Anthropic 공식: `WebFetch` → raw GitHub → `.claude/skills/`
   - GitHub 검색: `gh search code` → 평가 → 설치
2. 커스텀 스킬 생성
   - 갭 분석 결과 기반
   - Skill Schema v1 준수
3. `.claude/skills/*/SKILL.md` 파일 Write
4. 의존성 확인 (MCP 서버 필요 여부 → 사용자 알림)

**실행 에이전트:** `executor` (sonnet) + `document-specialist` (sonnet)

**산출물:** `.claude/skills/*/SKILL.md` 파일들

### Phase 5: 오케스트레이터 생성

**입력:** Phase 3-4 결과물

**실행:**
1. CLAUDE.md 오케스트레이션 섹션 생성

```markdown
# {Project Name} — Agent Team Orchestration

## 에이전트 카탈로그

| 에이전트 | 역할 | 모델 | 트리거 |
|---------|------|------|--------|
| content-generator | executor | claude-sonnet-4-6 | "생성", "작성" |
| quality-checker | reviewer | claude-sonnet-4-6 | 자동 (생성 후) |

## 위임 규칙

- 콘텐츠 생성 작업 → content-generator
- 품질 검증 → quality-checker (생성 완료 후 자동)

## 실행 프로토콜

- 패턴: 생성-검증 + 팬아웃
- 병렬: 독립 작업은 팬아웃으로 병렬 실행
- 검증: 모든 생성물은 quality-checker 통과 필수
```

2. 기존 CLAUDE.md와 merge
   - 새 섹션으로 추가 (`## Harness-Generated Team` 헤더)
   - 기존 내용 보존, 충돌 시 사용자 확인

**실행 에이전트:** `executor` (opus)

**산출물:** CLAUDE.md 업데이트

### Phase 6: 검증 & 테스트

**입력:** Phase 3-5 결과물 전체

**실행:**
1. **구조 검증**
   - 모든 `.md` 파일 frontmatter 파싱 가능 여부
   - 필수 필드 존재 여부
   - 참조된 스킬/에이전트 파일 존재 여부
   - 순환 의존성 검사

2. **시나리오 검증**
   - 도메인별 샘플 작업 3개 자동 생성
   - 각 작업에 대해 에이전트 호출 시뮬레이션
   - 예상 흐름이 패턴과 일치하는지 확인

3. **ARCHITECTURE.md 생성**
   ```markdown
   # 에이전트 팀 아키텍처

   ## 패턴: {선택된 패턴} (신뢰도: {confidence})
   ## 에이전트 관계도
   ## 데이터 흐름
   ## 패턴 선택 근거
   ```

4. **검증 시나리오 파일 생성**
   - `tests/harness/scenario-*.md`
   - 각 시나리오: 입력 → 예상 에이전트 흐름 → 예상 출력

**실행 에이전트:** `verifier` (sonnet) + `critic` (opus)

**산출물:** `ARCHITECTURE.md`, `tests/harness/*.md`

---

## 7. 골든 템플릿 카탈로그

Harness가 에이전트 생성 시 참조하는 검증된 템플릿 목록:

### OMC 에이전트 (XML 구조)

| 템플릿 | 역할 | 용도 |
|--------|------|------|
| executor | 구현 | 코드/콘텐츠 작성, 파일 편집 |
| verifier | 검증 | 증거 기반 완료 확인 |
| planner | 기획 | 요구사항 분석, 구현 계획 |
| architect | 설계 | 시스템 설계, 아키텍처 결정 |
| critic | 비평 | 계획/코드 리뷰 |
| document-specialist | 조사 | 외부 문서 조사, API 레퍼런스 |
| explore | 탐색 | 코드베이스 검색 |
| analyst | 분석 | 요구사항 분석 (pre-planning) |

### ECC 에이전트 (마크다운 구조)

| 템플릿 | 역할 | 용도 |
|--------|------|------|
| code-reviewer | 리뷰 | 코드 품질/보안 리뷰 |
| security-reviewer | 보안 | OWASP Top 10, 시크릿 감지 |
| tdd-guide | TDD | 테스트 주도 개발 가이드 |
| build-error-resolver | 빌드 | 빌드 에러 해결 |

### 커스텀 역할 (Harness 전용)

| 템플릿 | 역할 | 용도 |
|--------|------|------|
| skill-resolver | 스킬 해결 | 런타임 스킬 검색·설치 |
| domain-analyst | 도메인 분석 | Phase 1 도메인 특성 추출 |
| team-architect | 팀 설계 | Phase 2 아키텍처 설계 |

---

## 8. MVP 로드맵

### v0.1 — Core Pipeline (MVP)

**범위:** Phase 1-3 + Phase 5-6 (외부 스킬 없이)
- 도메인 분석 → 패턴 선택 → 에이전트 생성 → 오케스트레이터 → 검증
- 골든 템플릿 기반 에이전트 생성 (동적 탐색으로 로드)
- 커스텀 스킬만 생성 (외부 통합 없음)
- **skill-resolver 미포함** (v0.3에서 도입)
- 기존 파일 충돌 시 사용자 확인 (멱등성)
- 롤백 지원 (generation-log.json 기반)

**구현 형태:** Claude Code 스킬 (`/harness`)

**예상 결과:**
- `.claude/agents/*.md` 3-7개 (상한 10개)
- `.claude/skills/*.md` 2-5개
- `CLAUDE.md` 오케스트레이션 섹션 (merge 방식: 새 섹션 append)
- `ARCHITECTURE.md`
- `.omc/harness/` 중간 아티팩트

### v0.2 — External Skill Integration

**추가 범위:** Phase 4 (외부 스킬)
- Anthropic 공식 스킬 검색·설치
- GitHub 스킬 검색
- 스킬 의존성 자동 해결

### v0.3 — Runtime Skill Resolver

**추가 범위:** Skill Resolver 런타임 에이전트
- 실행 중 능력 갭 감지
- 동적 스킬 검색·설치·활성화
- 스킬 캐시 및 재사용

### v1.0 — Full Adaptive Agent Factory

**추가 범위:**
- 마켓플레이스 통합 (skillsmp.com 등)
- 패턴 합성 (복합 패턴)
- 팀 성능 피드백 루프 (실행 결과 → 팀 최적화)
- `--interview` 모드 deep-interview 통합

---

## 9. 기술적 제약 및 결정사항

### 제약

1. **Claude Code 스킬 형태**: 순수 마크다운, 외부 런타임 없음
2. **파일 시스템 기반**: 모든 결과물은 `.claude/` 디렉토리에 파일로 생성
3. **기존 파일 보존**: CLAUDE.md merge 시 기존 내용 덮어쓰기 금지
4. **한국어 문서**: 주석, 문서 모두 한국어
5. **에이전트 수 상한**: 생성되는 에이전트 최대 10개 (대규모 팀도 10개 이내로 합성)
6. **멱등성**: 동일 프로젝트에 `/harness` 재실행 시 기존 파일 덮어쓰기 않음. 충돌 시 사용자 선택 (덮어쓰기/건너뛰기/merge)

### 중간 아티팩트 경로

Phase 간 전달되는 중간 데이터의 저장 위치:

```
.omc/harness/                        # Harness 전용 작업 디렉토리
  domain-analysis.json               # Phase 1 산출물
  team-architecture.json             # Phase 2 산출물
  generation-log.json                # Phase 3-4 생성 이력 (롤백용)
  validation-report.json             # Phase 6 검증 결과
```

> `.omc/` 디렉토리는 OMC 상태 관리 표준 경로.
> Harness 전용 하위 디렉토리로 격리.

### 롤백 전략

Phase 실패 시 부분 생성물 처리:

```
1. Phase 3-5는 generation-log.json에 생성한 파일 목록 기록
2. 실패 감지 시:
   a. generation-log.json 읽기
   b. 생성된 파일 목록을 사용자에게 제시
   c. 사용자가 "롤백" 선택 시 생성된 파일 삭제
   d. 사용자가 "유지" 선택 시 부분 결과물 보존
3. CLAUDE.md 변경은 마지막 Phase(5)에서만 수행 → 중간 실패 시 CLAUDE.md 무사
```

### 결정사항

| 항목 | 결정 | 근거 |
|------|------|------|
| 에이전트 본문 | XML 구조 (OMC 방식) | LLM 경계 인식 정확도 |
| 스킬 본문 | 마크다운 (Anthropic 방식) | 공식 호환성 |
| 패턴 선택 | 프롬프트 기반 점수 매기기 | 코드 없이 LLM 판단 활용 |
| 외부 스킬 | 빌드타임 + 런타임 하이브리드 | 안정성 + 유연성 |
| 실행 모드 | 에이전트 팀 (TeamCreate/SendMessage) | Claude Code 권장 |
| 골든 템플릿 | OMC + ECC 혼합 | 둘 다 검증된 구조 |

---

## 10. 리스크 및 완화

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 외부 스킬 품질 불확실 | 생성된 팀 신뢰도 저하 | 평가 기준 (구조, stars, 업데이트) 적용 |
| 패턴 자동 선택 오류 | 비효율적 팀 구성 | 선택 근거 제시 + 사용자 오버라이드 옵션 |
| CLAUDE.md merge 충돌 | 기존 설정 손상 | diff 기반 merge + 사용자 확인 |
| Skill Resolver 남용 | 불필요한 외부 의존성 | 로컬 우선 정책 + 설치 한도 |
| 도메인 분석 부정확 | 잘못된 팀 설계 | `--interview` 모드로 정밀화 |
