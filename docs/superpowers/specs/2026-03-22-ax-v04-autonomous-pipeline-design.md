# ax v0.4 — 완전 자율 파이프라인 설계

## 배경

ax의 code 도메인 실행 결과물에서 반복적으로 발생하는 3가지 핵심 문제:

1. **CRUD 완성도 부족** — 구현은 되지만 사용성/오류 문제 (빈 상태 미처리, 폼 미구현, dead hook 등)
2. **수동 개입 빈발** — Phase 7에서 에스컬레이션, 스타일 선택, 비용 확인 등으로 자주 끊김
3. **완전 자율 실행 부재** — 인터뷰 후 마무리까지 무개입 autopilot이 안 됨

시간 소요는 무관. 완성도와 자율성이 최우선.

## 접근법: 완전 자율 파이프라인 (Approach C)

생성 품질 강화 + 검증 심화 + 모든 분기에서 수동 개입 제거를 동시에 진행.

## P0: 무개입 아키텍처 (Zero-Intervention Architecture)

### 2-Phase 모델

인터뷰를 "마지막 사용자 접점"으로 확정하고, 이후는 완전 자율로 전환.

```
[Phase 0~1] → [인터뷰 (유일한 사용자 접점)] → [Phase 2~7 완전 자율]
                                                    ↓
                                              중간 질문 = 0
                                              에스컬레이션 = 로그+스킵
                                              최종 보고만 사용자에게
```

### 현재 개입 지점 → 자동 결정 매핑

| 위치 | 현재 동작 | 변경 |
|------|----------|------|
| Phase 6.7 인터뷰 게이트 | "1) 인터뷰 / 2) 바로 실행" 선택 | `--execute` 시 인터뷰 자동 포함. `--skip-interview`로 명시적 스킵만 허용 |
| Phase 7 PPT 스타일 | A~H 스타일 선택 질문 | 인터뷰 Phase A-3으로 통합. 인터뷰 미진행 시 도메인 기본값 자동 적용 |
| Phase 7 에스컬레이션 | "3회 실패, 수동 처리 필요" 중단 | 해당 에이전트 스킵 + 로그 기록 + 다음 에이전트 진행 |
| Phase 7 비용 확인 | "$10 초과, 계속?" 질문 | 확인 제거. 비용은 최종 보고에만 포함 |
| Phase 6 검증 실패 | "수동 수정/롤백/유지" 3지선다 | 최대 3회 수정 루프 → 실패 항목 로그 → 파이프라인 계속 |
| Phase 7 스모크 테스트 | "2회 후에도 FAIL → 에스컬레이션" | 최대 5회 수정 루프 → 실패 플로우 로그 → 완료 처리 |

### execution-policy.json

인터뷰 완료 시 생성되는 정책 객체. Phase 7의 모든 분기를 사전 결정:

```json
{
  "intervention_mode": "zero",
  "max_agent_retries": 3,
  "max_validation_retries": 3,
  "max_smoke_test_retries": 5,
  "on_agent_failure": "skip_and_log",
  "on_validation_failure": "log_and_continue",
  "on_smoke_failure": "log_and_continue",
  "cost_limit_usd": null,
  "ppt_style": "dark-premium",
  "design_recipe": "레시피 1",
  "skip_interview": false
}
```

### 최종 보고서 강화

무개입 대신, 최종 보고서에 모든 결정/스킵/실패를 투명하게 포함:

```markdown
## AX 실행 완료 보고

### 성공 항목
- 에이전트 8/8 실행 완료
- CRUD 매트릭스 12/15 항목 구현

### 자동 스킵된 항목 (수동 확인 필요)
- 항목 + 원인 + 수동 확인 방법

### 수정 루프 이력
- 루프 횟수 + 수정 내용

### 비용
- 이미지 생성 비용 합산
```

## P1: CRUD 깊이 검증 (CRUD Depth Verification)

### 3-Layer 검증 아키텍처

```
Layer 1: 정적 완성도 검증 (Static Completeness)
  "모든 CRUD 코드가 존재하는가?"
         ↓ PASS
Layer 2: API 행동 검증 (Behavioral API Testing)
  "각 CRUD 작업이 올바른 결과를 반환하는가?"
         ↓ PASS
Layer 3: E2E 사용성 검증 (End-to-End Usability)
  "사용자가 실제로 이 기능을 사용할 수 있는가?"
```

### Layer 1: 정적 완성도 검증

Grep 기반 → AST 수준 검증으로 업그레이드:

- 백엔드: 라우트 핸들러 존재 + DB 호출 존재 + 에러 핸들링 존재 + status code 설정
- 프론트엔드: 페이지 파일 + API hook import/호출 + 라우터 등록 + 메뉴 링크 + onSubmit 핸들러(Create/Update)

### Layer 2: API 행동 검증

CRUD 매트릭스에서 실행 가능한 테스트 시퀀스를 자동 생성:

각 엔티티에 대해 CRUD 전체 사이클을 순서대로 실행:
1. CREATE — POST → 201 + id 확인 + Zod 스키마 일치
2. READ(목록) — GET → 200 + 배열 + created_id 포함
3. READ(상세) — GET/{id} → 200 + id 일치 + 필드값 일치
4. UPDATE — PUT/{id} → 200 + 재조회 시 수정값 반영
5. DELETE — DELETE/{id} → 200/204 + 재조회 시 404
6. 엣지 케이스 — 없는 ID→404, 필수 필드 누락→400, 중복→409

payload 자동 생성: api-contracts.ts Zod 스키마 + seed.ts 참조
생성 위치: `.omc/ax/crud-tests.json`

### Layer 3: E2E 사용성 검증

Playwright 기반 브라우저 테스트:

1. 네비게이션 — 메뉴 클릭 → 페이지 로드 → JS 에러 0
2. 목록 페이지 — 시드 데이터 표시 + 빈 상태 EmptyState
3. 생성 폼 — 버튼→모달 + 유효성 에러 + 성공 피드백 + 목록 반영
4. 수정 폼 — 프리필 + 수정 + 성공 피드백
5. 삭제 — 확인 다이얼로그 + 목록에서 제거

Playwright 설치 실패 시 Layer 3 스킵 (graceful degradation).
결과: `.omc/ax/e2e-results/` (스크린샷 포함)

### 수정 루프 통합

```
Layer 1 실패 → "코드가 없다" → 구현 지시
Layer 2 실패 → "동작이 틀리다" → 실패 응답 + 기대값 첨부
Layer 3 실패 → "UI가 안 된다" → 스크린샷 + 에러 메시지 첨부

각 Layer 최대 5회 루프
5회 후 FAIL → 스킵 + 로그 (P0 무개입 정책)
```

## P2: SKILL.md 분해 (Modular Phase Architecture)

### Hub-and-Spoke 구조

```
변경 후:
  SKILL.md (~150줄 — 오케스트레이터)
  phases/
    phase-0-init.md
    phase-1-analysis.md
    phase-2-architecture.md
    phase-3-agents.md
    phase-4-skills.md
    phase-5-orchestrator.md
    phase-6-validation.md
    phase-7-execution.md
  references/         (기존 유지, phase-7-execute.md만 삭제)
  templates/          (변경 없음)
  library/            (변경 없음)
```

### 오케스트레이터 SKILL.md (~150줄)

포함 내용:
- 사용법 (플래그, 예시)
- 모든 Phase 공통 실행 규칙 (무중단, 병렬, execution-policy 참조)
- Phase 파일 경로 매핑 테이블
- Phase 실행 프로토콜: Read → 실행 → 검증 → TaskUpdate → 다음 Phase

### Phase 실행 프로토콜

각 Phase 실행 시:
1. Read: `phases/phase-{N}-{name}.md` — 해당 Phase만 컨텍스트에 로드
2. Phase 내부에서 필요한 references/templates를 조건부 Read
3. 산출물 생성 + 출력 계약 검증
4. TaskUpdate(completed) → 다음 Phase

### 컨텍스트 효율

- 현재: 980줄 전체 투입 (~20K 토큰)
- 변경: 오케스트레이터 150줄 (~3K) + 현재 Phase만 추가 로드
- Phase 7 실행 시 Phase 1-3 상세는 이미 불필요 → 자연스럽게 컨텍스트 절감

### 마이그레이션 순서

1. phases/ 디렉토리 생성
2. Phase 7 추출 (가장 크고 중복 있음, phase-7-execute.md 통합)
3. Phase 1-2 추출
4. Phase 3-4 추출
5. Phase 5-6 추출
6. Phase 0 추출
7. SKILL.md 축소
8. references/phase-7-execute.md 삭제
9. 각 Step 후 회귀 테스트

## P3: 생성 품질 강화 (Generation Quality Enhancement)

### Anti-Pattern 라이브러리 분리

SKILL.md 하드코딩 → 독립 라이브러리로 추출:

```
library/anti-patterns/
  backend-common.md        # 범용 백엔드 (요청 처리, 인증, 에러, DB)
  frontend-common.md       # 범용 프론트엔드 (방어 코딩, 상태 관리, 접근성)
  fullstack-integration.md # 프론트-백 통합 (경로 불일치, 응답 구조, 토큰 저장)
  auth-patterns.md         # 인증/세션 (JWT, 쿠키, refresh, 세션 지속성)
  database-patterns.md     # DB/ORM (마이그레이션, 시드, 컬럼명 일관성)
```

Phase 3에서 에이전트 role 기반으로 관련 파일만 Read → `<Anti_Patterns>` 주입.
프로젝트 실행 후 발견된 새 패턴 추가 → 이후 모든 프로젝트에 자동 반영.

### CRUD 구현 체크리스트 자동 생성

CRUD 매트릭스의 각 행에서 에이전트별 구체적 구현 지시를 자동 도출:

백엔드: 라우트 + Zod 유효성 + DB 호출 + 에러 핸들링 + status code
프론트엔드: 버튼 → 모달/페이지 + 폼 유효성 + 로딩 상태 + 성공/실패 피드백 + 목록 새로고침

생성 시점: Phase 2.4.4 직후 → `.omc/ax/crud-checklists.json`
주입 시점: Phase 3 에이전트 `<Process>` + Phase 7 에이전트 프롬프트

### API Fixture 자동 생성

프론트-백 불일치 원천 차단:

```
api-contracts.ts (스키마) + seed.ts (데이터) → api-fixtures.ts (응답 예시)
```

포함 내용: 목록 응답, 생성 요청, 빈 상태 응답, 에러 응답 예시.
프론트엔드 에이전트에 "api-fixtures.ts를 Read하여 실제 응답 구조 확인 후 구현" 지시.
생성 시점: Phase 2.4.2 직후.

### Base Agent 라이브러리 확장

현재 4개 → 9개로 확장:

```
기존: visual-architect-base, visual-builder-base, visual-qa-base, reviewer-base
추가: backend-developer-base, frontend-developer-base, system-architect-base,
      content-writer-base, data-analyst-base
```

Phase 3 골든 템플릿 매칭 우선순위:
1. OMC/ECC 에이전트 (기존)
2. library/base-agents/{role}-base.md (신규)
3. templates/agent-skeleton.md (폴백)

## P4: 검증 스크립트 강화 (Verification Infrastructure)

### 3-Tier 테스트 아키텍처

```
Tier 1: validate_project.py 확장 — 생성 프로젝트 구조+실체 검증 (~2초)
Tier 2: validate_ax.py 신규 — ax 스킬 자체 무결성 검증 (~3초)
Tier 3: run_scenario.py 신규 — JSON 시나리오 기반 회귀 테스트 (~30초)
```

### Tier 1: validate_project.py 확장

기존 10개 + 신규 4개 체크포인트:
- 11: CRUD 핸들러 실체 (빈 핸들러 검출 — DB 호출 존재 확인)
- 12: 프론트엔드 폼 컴포넌트 (Create/Update용 폼/모달 존재)
- 13: API hook 실제 사용 (import + 호출 확인, dead hook 검출)
- 14: 에러/로딩/빈 상태 UI (3가지 상태 처리 존재 확인)

### Tier 2: validate_ax.py

ax 스킬 자체 검증:
1. SKILL.md 파일 참조 무결성 (Read로 참조하는 파일 존재 확인)
2. Phase 파일 완전성 (phases/ 디렉토리에 0-7 모두 존재)
3. 템플릿 플레이스홀더 검증 (미등록 플레이스홀더 경고)
4. base-agent 라이브러리 frontmatter 유효성
5. anti-pattern 라이브러리 존재 + 비어있지 않음
6. domain-patterns.md 5개 도메인 모두 정의 확인

### Tier 3: JSON 시나리오 프레임워크

마크다운 체크리스트 → 실행 가능한 JSON 시나리오:
- 입력: domain_description + flags
- 기대값: domain_analysis 필드, 패턴, 에이전트 수/필수 에이전트, 생성 파일, 검증 결과
- 실행: 기존 생성 결과물 검증 또는 `--generate`로 새로 생성 후 검증
- 통합: `make test-all` = test-ax + test-scenarios

### 테스트 파일 구조

```
tests/ax/
  scenarios/
    fullstack-saas.json
    ecommerce-platform.json
    presentation-slides.json
    cli-tool.json
    research-analysis.json
    api-microservice.json
  tools/
    validate_project.py     (기존 확장)
    validate_ax.py          (신규)
    run_scenario.py         (신규)
  Makefile                  (신규)
```

## 구현 우선순위

| 순위 | 항목 | 이유 |
|------|------|------|
| P0 | 무개입 아키텍처 | 사용자 최우선 요구. 비교적 빠르게 적용 가능 |
| P1 | CRUD 깊이 검증 | 완성도 문제의 직접적 해결 |
| P2 | SKILL.md 분해 | 이후 모든 작업의 효율 기반 |
| P3 | 생성 품질 강화 | 근본 원인 해결. 반복 실험 필요 |
| P4 | 검증 스크립트 강화 | ax 자체 안정성. 장기적 필수 |

## 제약사항

- 모든 변경은 기존 ax 파이프라인과 호환 유지 (breaking change 최소화)
- P2 마이그레이션은 Phase별 순차 추출 + 매 Step 회귀 테스트
- P3 base-agent은 최소 backend + frontend부터 시작, 나머지는 점진적 추가
- P4 시나리오는 기존 scenario-*.md에서 JSON으로 마이그레이션
