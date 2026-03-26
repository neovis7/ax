# Phase 2: 팀 아키텍처 설계

> **실행 규칙**: 이 Phase의 모든 서브에이전트 호출 시 `mode: "bypassPermissions"`를 사용합니다. 사용자에게 확인을 요청하지 않습니다.

## 2.1 패턴 선택

`.omc/ax/domain-analysis.json`의 시그널을 읽고, 다음 두 가이드를 참고하여 최적 패턴을 선택합니다:

1. Read: `.claude/skills/ax/templates/domain-patterns.md` — 도메인 유형별 골든 패턴 매핑 확인
2. Read: `.claude/skills/ax/templates/pattern-selection.md` — 시그널 기반 추론 절차

도메인 유형(`domain_type`)에 해당하는 골든 패턴을 우선 참고하고, 시그널을 프롬프트의 `{SIGNALS_JSON}` 위치에 넣어 최종 패턴을 확정합니다.

## 2.2 에이전트 역할 결정

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

## 2.3 골든 템플릿 매칭

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

## 2.4 스킬 갭 분석

도메인에 필요하지만 기존에 없는 스킬을 식별:
- 기존 스킬 목록 (Phase 1에서 스캔) 확인
- 도메인 동사/입출력과 기존 스킬 description 매칭
- 매칭되지 않는 능력 → "커스텀 스킬 생성 대상"

### 2.4.1 외부 스킬 레시피 자동 적용 (v0.5)

`.claude/skills/ax/templates/external-skill-catalog.md`를 Read하고 다음을 수행합니다:

**A) 레시피 자동 매칭:**

도메인 분석 결과(`domain_type`, `output_format`, `domain_sub_type`)로 최적 레시피를 자동 선택합니다:

```
creative + html                    → 레시피 1 (프리미엄 랜딩)
creative + html + 마케팅/브랜딩     → 레시피 6 (마케팅/브랜딩)
code + fullstack                   → 레시피 2 (풀스택 웹앱)
code + fullstack + accuracy        → 레시피 4 (데이터 대시보드)
document + presentation            → 레시피 3 (프레젠테이션 — deer-flow 기본)
document + html (비프레젠테이션)    → 레시피 3 변형 (supanova-design 기본)
code + api|cli|data-pipeline       → 레시피 5 (API/CLI — 디자인 스킬 없음)
```

**B) 디자인 엔진 자동 결정:**

`flags.design` 값에 따라 처리:
- `"auto"` (기본값, 플래그 미지정): 레시피의 "필수" 스킬을 자동 선택
  - creative/document+html → supanova-design
  - code+fullstack → frontend-design
  - 그 외 → 없음
- `"supanova"` 또는 `"frontend-design"`: 해당 스킬 명시 선택
- `"none"`: 디자인 스킬 적용 안 함

**C) 스킬 조합 자동 적용:**

1. 레시피의 "필수" 디자인 엔진: GitHub URL에서 SKILL.md를 WebFetch
2. `${PROJECT_DIR}/.omc/ax/design-skill-context.md`에 저장
3. 레시피의 "권장" 스킬: 설치 여부 확인 (Glob으로 `.claude/plugins/` 확인)
   - 이미 설치됨 → Phase 7에서 해당 스킬 콘텐츠도 에이전트에 주입
   - 미설치 → 완료 보고에 설치 추천 (시너지 효과 설명 포함)
4. 충돌 매트릭스 확인 — 충돌 스킬이 동시 설치되어 있으면 레시피 기준으로 1개만 활성화
5. Phase 3에서 해당 에이전트의 `<Process>` 섹션에 "design-skill-context.md를 Read하고 디자인 원칙을 적용하라" 지시를 추가
6. Phase 7에서 우선순위 규칙에 따라 에이전트 프롬프트에 주입:
   - 1순위: 디자인 엔진 (전체 원칙)
   - 2순위: 품질 강화 스킬 (세부 규칙)
   - 3순위: 에셋 스킬 (리소스 활용)

**D) 완료 보고에 포함할 정보:**
- 적용된 레시피명과 선택 근거
- 자동 적용된 디자인 엔진명
- 추가 설치 추천 스킬 (설치 명령어 + 시너지 효과)
- 충돌로 비활성화된 스킬 (있으면)

### 2.4.2 API 계약 생성 (code 도메인 — fullstack/api)

> 적용 조건: domain_sub_type이 fullstack 또는 api이고, backend + frontend가 병렬 실행될 때.
> 상세 절차: Read `.claude/skills/ax/references/api-contract.md`

병렬 에이전트 간 API 응답 구조 불일치를 방지하기 위해 공유 Zod 스키마 + 행동 의도(@intent) + 상태별 응답 변형을 사전 정의합니다.
생성 파일: `${PROJECT_DIR}/src/types/api-contracts.ts`

**@source 어노테이션 필수**: 각 스키마 필드에 데이터 출처를 명시합니다:
- `@source body` — 요청 바디에서 전달 (email, password 등)
- `@source params` — URL 경로 파라미터 (:id, :sessionId 등)
- `@source query` — URL 쿼리 파라미터 (?page=1 등)
- `@source cookie` — 쿠키에서 추출 (auth_token 등)
- `@source server` — 서버에서 자동 생성 (timestamp, userId from JWT 등)

URL params 필드가 Zod 스키마에 포함된 경우, API 라우트에서 URL params를 body에 자동 주입:
```typescript
const parsed = Schema.safeParse({ ...(body as object), sessionId });
```
프론트엔드는 `@source params` 필드를 요청 바디에 포함하지 않습니다.
상세 규칙: Read `.claude/skills/ax/references/api-contract.md`

### 2.4.2.1 API Fixture 생성

api-contracts.ts 생성 직후, 프론트엔드가 실제 응답 구조를 참조할 수 있도록 응답 예시 파일을 생성합니다:

**생성 파일**: `${PROJECT_DIR}/src/types/api-fixtures.ts`

**포함 내용** (각 Zod 스키마에 대해):
- 목록 응답 예시 (1-2개 항목, 시드 데이터 기반)
- 생성 요청 예시 (`Omit<Schema, 'id' | 'createdAt'>`)
- 빈 상태 응답 예시 (빈 배열 — EmptyState UI 개발용)
- 유효성 에러 응답 예시 (error + details 배열)

**값 생성 규칙**:
- 시드 데이터(`prisma/seed.ts`)가 있으면 해당 값 참조
- 없으면 Zod 스키마의 타입/제약에 맞는 예시 값 생성
- 외래 키는 시드 데이터의 실제 ID 사용
- 날짜는 ISO 8601 형식 예시

**에이전트 프롬프트 삽입**:
- frontend-developer: "API 응답 구조를 추측하지 마세요. `src/types/api-fixtures.ts`를 Read하여 실제 응답 구조를 확인한 뒤 구현하세요. 특히 빈 배열 응답(`emptyListFixture`)으로 EmptyState UI를, 에러 응답(`validationErrorFixture`)으로 에러 UI를 구현하세요."

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

### 2.4.5 CRUD 구현 체크리스트 자동 생성

CRUD 매트릭스의 각 '필수=O' 행에 대해 에이전트별 구체적 구현 체크리스트를 자동 도출합니다.

**생성 파일**: `${PROJECT_DIR}/.omc/ax/crud-checklists.json`

**operation별 체크리스트 템플릿:**

| operation | backend 체크리스트 | frontend 체크리스트 |
|-----------|-------------------|-------------------|
| Create | 라우트 핸들러 + Zod 유효성 검증 + 유효성 실패 400 + DB INSERT + 201+id 응답 + try-catch | 생성 버튼→모달 + 폼 필수필드 + 클라이언트 유효성 + 로딩 상태 + 성공 토스트 + 목록 새로고침 + 실패 에러 표시 |
| Read(목록) | 라우트 핸들러 + 페이지네이션 + 필터링(해당 시) + 200+배열 응답 | 테이블/리스트 + 빈 상태 EmptyState + 로딩 스켈레톤 + 페이지네이션 UI |
| Read(상세) | 라우트 핸들러 + 404 처리 + 200+객체 응답 | 상세 뷰 + 로딩 상태 + 에러/404 상태 |
| Update | 라우트 핸들러 + Zod 유효성 + 존재 확인 404 + DB UPDATE + 200 응답 | 수정 버튼→모달 + 기존값 프리필 + 폼 유효성 + 로딩 + 성공 피드백 |
| Delete | 라우트 핸들러 + 존재 확인 + DB DELETE + 200/204 응답 + cascade(해당 시) | 삭제 버튼 + 확인 다이얼로그 + 목록에서 항목 제거 + 성공 피드백 |

**주입 시점:**
- Phase 3 에이전트 `<Process>` 섹션에 ".omc/ax/crud-checklists.json을 Read하고 해당 엔티티의 체크리스트를 모두 구현하라" 지시 추가
- Phase 7 에이전트 프롬프트에 동적 주입: 해당 에이전트 role의 체크리스트만 발췌하여 포함

## 2.5 산출물 저장

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

## 2.6 출력 계약 검증

team-architecture.json을 Read하고 다음을 확인합니다:
- `pattern.primary` 존재 + 6가지 패턴 중 하나
- `agents` 배열 길이 >= 4 (최소 executor+reviewer+visual 2종)
- 모든 에이전트에 name, role, model 필드 존재
- `skills.gap_create` 배열 존재 (빈 배열 허용)

누락 시 Phase 2를 재실행하여 보정.
