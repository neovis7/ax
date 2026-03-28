# Phase 6: 검증 & 테스트

> **실행 규칙**: 이 Phase의 모든 서브에이전트 호출 시 `mode: "bypassPermissions"`를 사용합니다. 검증 실패 시 자동 수정하며, 사용자에게 확인을 요청하지 않습니다.

## 6.1 구조 검증

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

**Layer 1 정적 완성도 검증 (code 도메인 — fullstack/api):**

validate_project.py의 체크포인트 11-14를 실행하여 CRUD 코드의 실체를 확인합니다:
- 체크포인트 11: CRUD 핸들러에 실제 DB 호출이 있는지 (빈 핸들러 검출)
- 체크포인트 12: 프론트엔드에 폼 컴포넌트가 존재하는지
- 체크포인트 13: API hook이 정의만 되고 미사용인지 (dead hook 검출)
- 체크포인트 14: 로딩/에러/빈 상태 UI가 있는지 (경고)

실행: `python3 .claude/skills/ax/tools/validate_project.py ${PROJECT_DIR}`
FAIL 항목이 있으면 해당 에이전트에 수정 지시 후 재실행.

## 6.1.5 스킬 품질 검증

> 적용 조건: `skills.gap_create`에 1개 이상 커스텀 스킬이 생성된 경우.
> 상세 절차: Read `.claude/skills/ax/references/skill-testing-guide.md`

Phase 4에서 생성된 커스텀 스킬의 품질을 검증합니다.

**A) Description 트리거 검증:**
1. 각 스킬에 대해 should-trigger 쿼리 5개 + should-NOT-trigger 쿼리 5개 자동 생성
2. should-NOT-trigger는 **near-miss** 위주 (키워드 유사하지만 다른 도구가 적합한 쿼리)
3. 기존 스킬과의 충돌 확인 (새 스킬의 should-trigger가 기존 스킬을 잘못 트리거하지 않는지)
4. 트리거 정확도가 낮으면 description 자동 개선 (최대 3회)

**B) 스킬 구조 검증:**
1. skill.md 본문이 500줄 이내인지 확인 (초과 시 references/ 분리 권고)
2. "When to Activate" 섹션에 구체적 트리거 상황이 2개 이상 기술되어 있는지
3. 본문에 Why-First 패턴이 적용되어 있는지 (강압적 "ALWAYS/NEVER" 사용 빈도 < 3)
4. 예시(Examples) 섹션이 입력/출력 쌍으로 구성되어 있는지

검증 결과를 `validation-report.json`에 추가:
```json
{
  "skill_quality": {
    "trigger_accuracy": "{통과율}",
    "structure_valid": "{PASS|FAIL}",
    "description_conflicts": ["{충돌 스킬명}"],
    "body_line_count": "{줄 수}",
    "why_first_score": "{ALWAYS/NEVER 사용 빈도}"
  }
}
```

검증 실패 시 Phase 4 에이전트에 수정 요청 후 재검증 (max_validation_retries 적용).

## 6.2 시나리오 검증

도메인에 맞는 샘플 작업 3개를 자동 생성하고, 각 작업에 대해:
- 어떤 에이전트가 호출되어야 하는지 추론
- 위임 규칙과 일치하는지 확인
- 예상 흐름 문서화 (A → B → C 형태)

## 6.3 검증 결과 저장

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

**검증 실패 시 자동 수정 루프:**

```
검증 FAIL 발생
  → execution-policy.json의 max_validation_retries 값까지 수정 루프 실행:
    → 실패 항목을 구조화된 피드백으로 정리
    → Phase 3/4 에이전트에 SendMessage로 수정 요청 (구체적 수정 지시 포함)
    → 수정된 파일만 재검증 (전체 재생성 X)
    → PASS → 완료
  → 최대 횟수 초과 시: execution-policy.json의 on_validation_failure에 따라 처리
    → "log_and_continue": 실패 항목을 validation-report.json에 기록하고 다음 Phase로 진행
    → "escalate": 사용자에게 에스컬레이션 (향후 interactive 모드)
```

## 6.4 ARCHITECTURE.md 생성

`.claude/skills/ax/templates/architecture-doc.md`를 Read하고 플레이스홀더를 채워서 생성합니다.

충돌 확인: `.claude/ARCHITECTURE.md` 이미 존재하면 → 자동 덮어쓰기.

내용:
- 선택된 패턴과 근거 (Phase 2 결과에서)
- 에이전트 관계도 (텍스트 다이어그램으로 표현)
- 각 에이전트 상세 (이름, 역할, 모델, 도구)
- 스킬 목록
- 데이터 흐름 설명

`.claude/ARCHITECTURE.md`에 Write. `generation-log.json`에 기록.

## 6.5 검증 시나리오 파일 생성

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

## 6.6 완료 보고

모든 Phase 완료 후 사용자에게 요약 보고:

```
AX 에이전트 팀 생성 완료

요약:
  - 패턴: {primary} + {secondary}
  - 에이전트: {N}개 생성
  - 스킬: {N}개 생성
  - 검증: {PASS/FAIL}

자동 스킵된 항목 (수동 확인 필요):
  {validation-report.json의 failures 목록 — 없으면 "없음"}

생성된 파일:
  {generation-log.json의 generated_files 목록}

다음 단계:
  - 생성된 에이전트를 사용해보세요
  - ARCHITECTURE.md에서 팀 구조를 확인하세요
  - 문제가 있으면 /ax를 다시 실행하세요
```

`--execute` 플래그가 있으면 인터뷰를 거쳐 Phase 7로 진행합니다.

## Phase 6.7: 인터뷰 (`--execute` 시 자동 실행)

> `--execute` 플래그가 없으면 이 Phase를 건너뜁니다.
> `--skip-interview` 플래그가 있으면 인터뷰를 건너뛰고 기본값으로 execution-policy.json을 생성합니다 (Phase 6.8).

`--execute` 시 인터뷰를 자동으로 실행합니다 (기존: 선택 질문 → 변경: 자동 실행).
사용자가 인터뷰를 원하지 않으면 `--skip-interview`를 명시적으로 사용해야 합니다.

**`--interview` 플래그가 이미 있으면**: 동일하게 인터뷰 프로세스를 실행합니다.
**`--skip-interview` 플래그가 있으면**: 인터뷰 없이 기본값으로 Phase 6.8로 진행합니다.

인터뷰 프로세스: Read `.claude/skills/ax/references/interview-mode.md`
인터뷰 완료 후 `${PROJECT_DIR}/docs/plan.md`, `docs/architecture.md`, `docs/user-flows.md` 생성.
사용자 확인 게이트 → 수정 가능 → 확인 후 Phase 6.8 → Phase 7 진행.

## Phase 6.8: execution-policy.json 생성

인터뷰 완료 직후 (또는 `--skip-interview` 시 Phase 6.7 직후) 다음 정책 파일을 생성합니다.

**파일 위치**: `${PROJECT_DIR}/.omc/ax/execution-policy.json`

인터뷰에서 수집된 값(PPT 스타일, 디자인 레시피 등)을 반영하고, 수집되지 않은 값은 기본값을 사용합니다:

```json
{
  "intervention_mode": "zero",
  "max_agent_retries": 3,
  "max_validation_retries": 3,
  "max_smoke_test_retries": 5,
  "on_agent_failure": "skip_and_log",
  "on_validation_failure": "log_and_continue",
  "on_smoke_failure": "log_and_continue",
  "max_visual_qa_retries": 3,
  "on_visual_qa_failure": "skip_and_log",
  "cost_limit_usd": 50,
  "ppt_style": "{인터뷰에서 수집 또는 도메인 기본값}",
  "design_recipe": "{인터뷰에서 수집 또는 자동 매칭}",
  "skip_interview": false
}
```

**`intervention_mode` 동작:**
- `"zero"` (기본): 모든 에스컬레이션을 자동 결정으로 대체. Phase 6.3의 3지선다 메뉴 삭제, Phase 7의 모든 사용자 질문 삭제.
- `"interactive"` (향후 확장): 기존 동작 유지 (에스컬레이션 시 사용자에게 질문).

**`cost_limit_usd` 동작:**
- 기본값 $50. 초과 시 중단하지 않고 로그 기록 + 최종 보고에 경고 포함.
- `null`로 설정 시 비용 제한 완전 해제.

**`--design` 플래그와의 우선순위:**
- `--design` 플래그가 명시적으로 지정된 경우 → 플래그 값이 최우선
- 인터뷰에서 선택한 경우 → 인터뷰 결과 적용
- 둘 다 없는 경우 → 도메인 기본값 자동 적용

Phase 7의 모든 분기에서 이 파일을 Read하여 자동 결정합니다. 이 파일이 존재하지 않으면 위 기본값으로 런타임 생성합니다.
