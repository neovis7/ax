# ax v0.4 — 완전 자율 파이프라인 설계

## 배경

ax의 code 도메인 실행 결과물에서 반복적으로 발생하는 3가지 핵심 문제:

1. **CRUD 완성도 부족** — 구현은 되지만 사용성/오류 문제 (빈 상태 미처리, 폼 미구현, dead hook 등)
2. **수동 개입 빈발** — Phase 7에서 에스컬레이션, 스타일 선택, 비용 확인 등으로 자주 끊김
3. **완전 자율 실행 부재** — 인터뷰 후 마무리까지 무개입 autopilot이 안 됨

시간 소요는 무관. 완성도와 자율성이 최우선.
실행 시간이 10x 증가하더라도 완성도를 우선한다.

**적용 범위**: P0(무개입)과 P2(분해)는 모든 도메인에 적용. P1(CRUD 검증)과 P3 대부분은 code 도메인(특히 fullstack/api)에 한정. non-code 도메인의 품질 강화는 별도 스펙에서 다룬다.

## P0-P4 의존성 그래프

```
P0 (무개입) ──────────────────────────────→ 독립 구현 가능
P1 (CRUD 검증) ── P3의 API fixture 필요 ──→ P3 Phase 2.4.2 부분을 먼저 구현
P2 (SKILL.md 분해) ───────────────────────→ 독립 구현 가능 (P4 Tier 2 전제조건)
P3 (생성 품질) ───────────────────────────→ 독립 구현 가능
P4 (검증 스크립트) ── P2의 phases/ 구조 필요 → P2 완료 후 Tier 2 구현
```

**권장 구현 순서**: P0 → P3(api-fixture 부분만) → P1 → P2 → P4 → P3(나머지)

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
| Phase 6 검증 실패 | "수동 수정/롤백/유지" 3지선다 | 3지선다 메뉴 **삭제**. 최대 3회 수정 루프 → 실패 항목 로그 → 파이프라인 계속 |
| Phase 7 스모크 테스트 | "2회 후에도 FAIL → 에스컬레이션" | 최대 5회 수정 루프 → 실패 플로우 로그 → 완료 처리 |

### 현재 대비 변경된 리트라이 횟수

execution-policy.json의 값이 Phase 파일 내 하드코딩 값을 **항상 오버라이드**합니다:

| 항목 | 현재 값 (SKILL.md/phase-7) | 신규 기본값 (execution-policy) | 변경 이유 |
|------|---------------------------|-------------------------------|----------|
| 에이전트 실패 시 재시도 | 3회 (재시도→단순화→스킵) | 3회 (동일, 구조 유지) | 기존과 동일. 3단계 에스컬레이션 유지 |
| Phase 6 검증 수정 루프 | 2회 후 사용자 에스컬레이션 | 3회 후 로그+계속 | 1회 추가 + 에스컬레이션→자동 처리 |
| Phase 7 스모크 테스트 | 2회 후 사용자 에스컬레이션 | 5회 후 로그+계속 | 완성도 우선. 시간 무관 |
| Phase 7 Stage B 계약 검증 | 2회 루프 | 3회 루프 | Layer 2와 통합, 1회 추가 |
| Phase 7 visual-qa 피드백 루프 | 2회 후 사용자 에스컬레이션 | 3회 후 로그+계속 | 무개입 정책 적용 |

**구현 시 필수 수정 대상 파일:**

P0 구현 시, 다음 파일의 하드코딩된 리트라이/에스컬레이션을 `execution-policy.json` 참조로 교체해야 합니다:

| 파일 | 수정 위치 | 현재 내용 | 변경 |
|------|----------|----------|------|
| SKILL.md | Phase 6.3 (~line 724) | `최대 2회` + 3지선다 메뉴 | `execution-policy.json의 max_validation_retries` 참조 + 메뉴 삭제 |
| SKILL.md | Phase 6.3 (~line 733) | `사용자에게 에스컬레이션` | `on_validation_failure 정책에 따라 처리` |
| phase-7-execute.md | Stage B (~line 128) | `최대 2회 루프` | `max_smoke_test_retries` 참조 |
| phase-7-execute.md | 스모크 테스트 (~line 239) | `최대 2회 반복 → 에스컬레이션` | `max_smoke_test_retries` + `on_smoke_failure` 참조 |
| phase-7-execute.md | 비용 확인 (~line 283) | `$10 초과 시 사용자 확인` | `cost_limit_usd` 참조 + 확인 질문 삭제 |
| phase-7-execute.md | visual-qa 피드백 (~line 332) | `최대 2회 → 에스컬레이션` | `max_visual_qa_retries` + `on_visual_qa_failure` 참조 |

P2(SKILL.md 분해) 이후에는 이 수정 대상이 `phases/phase-6-validation.md`와 `phases/phase-7-execution.md`로 이동합니다.

### `--skip-interview` 플래그 파싱

Phase 1 입력 파싱에 추가:
- `--skip-interview` 플래그 존재 여부 확인
- 존재 시 `flags.skip_interview = true` → Phase 6.7 인터뷰 게이트 및 인터뷰 프로세스 전체 스킵
- `domain-analysis.json`의 `flags` 객체에 `skip_interview` 필드 추가

### execution-policy.json

**생성 시점**: 인터뷰 완료 직후, 또는 `--skip-interview` 시 Phase 6.7 직후에 기본값으로 자동 생성.
**위치**: `${PROJECT_DIR}/.omc/ax/execution-policy.json`
**참조 규칙**: Phase 7의 모든 분기에서 이 파일을 Read하여 자동 결정. 이 파일이 없으면 아래 기본값으로 런타임 생성.

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
  "ppt_style": "dark-premium",
  "design_recipe": "레시피 1",
  "skip_interview": false
}
```

**`intervention_mode` 동작:**
- `"zero"` (기본): 모든 에스컬레이션을 자동 결정으로 대체. Phase 6.3의 3지선다 메뉴 삭제, Phase 7의 모든 사용자 질문 삭제.
- `"interactive"` (향후 확장): 기존 동작 유지 (에스컬레이션 시 사용자에게 질문).

**`cost_limit_usd` 동작:**
- 기본값 $50 (기존 $10에서 상향). 초과 시 중단하지 않고 로그 기록 + 최종 보고에 경고 포함.
- `null`로 설정 시 비용 제한 완전 해제.

**`--design` 플래그와의 우선순위:**
- `--design` 플래그가 명시적으로 지정된 경우 → 플래그 값이 최우선
- 인터뷰에서 선택한 경우 → 인터뷰 결과 적용
- 둘 다 없는 경우 → 도메인 기본값 자동 적용

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

**기존 Stage B와의 관계**: 현재 Phase 7의 Stage B(계약 검증 게이트)는 "모든 엔드포인트를 Zod safeParse"하는 스키마 일치 검증. Layer 2는 Stage B를 **확장 대체**한다 — Stage B의 safeParse 검증을 포함하면서, 추가로 CRUD 시퀀스 검증과 엣지 케이스 검증을 수행. 기존 Stage B 코드는 Layer 2로 통합되어 삭제.

**테스트 실행기**: `.omc/ax/crud-tests.json`에 테스트 플랜을 생성하고, Phase 7에서 curl 명령어로 실행. 각 curl 호출 결과를 JSON으로 파싱하여 기대값과 비교.

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

**Playwright graceful degradation:**
- `npx playwright install chromium` 실패 → Layer 3 전체 스킵, Layer 2까지만 실행
- Playwright 설치 성공했으나 브라우저 실행 실패 (headless 환경 문제) → Layer 3 스킵 + 로그
- 개별 테스트 타임아웃 (30초) → 해당 테스트 FAIL 처리, 나머지 계속 실행
- 전체 Layer 3 타임아웃 (5분) → 완료된 테스트까지만 결과 기록, 나머지 스킵
- Layer 3 스킵 시 최종 보고에 "E2E 사용성 검증 미실행 — Playwright 환경 불가" 명시

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

### 호환성 브릿지

마이그레이션 중 partial state(일부 Phase만 추출된 상태)에서도 ax가 정상 동작해야 합니다:

**오케스트레이터의 Phase 로드 로직:**
```
Phase N 실행 시:
  1. phases/phase-{N}-*.md 파일 존재 확인 (Glob)
  2. 존재 → Read(phases/phase-{N}-*.md) — 추출된 Phase 사용
  3. 미존재 → SKILL.md 내의 inline Phase 섹션 실행 — 기존 동작 유지
```

이 로직을 오케스트레이터 SKILL.md에 명시하면, Phase 7만 추출하고 나머지는 inline인 중간 상태에서도 정상 동작합니다. 모든 Phase 추출이 완료된 후 inline 내용을 삭제합니다.

**롤백 계획:**
- 각 Step의 커밋은 독립적. 문제 발생 시 해당 커밋만 revert
- 추출 전 SKILL.md의 마지막 정상 상태를 git tag로 표시: `git tag ax-v03-pre-decomposition`

### 마이그레이션 순서

1. phases/ 디렉토리 생성
2. 오케스트레이터 SKILL.md에 호환성 브릿지 로직 추가 (Phase 파일 존재 시 Read, 미존재 시 inline)
3. Phase 7 추출 (가장 크고 중복 있음, phase-7-execute.md 통합)
4. Phase 1-2 추출
5. Phase 3-4 추출
6. Phase 5-6 추출
7. Phase 0 추출
8. SKILL.md에서 inline Phase 내용 삭제 (오케스트레이터만 남김)
9. references/phase-7-execute.md 삭제
10. 각 Step 후 `make test-ax` 회귀 테스트 (P4 Tier 2). P4 미완료 시 수동 검증: `/ax --here "테스트 CLI 도구"` 실행

### 컨텍스트 윈도우 고려

P0의 완전 자율 실행은 기존보다 긴 연속 실행을 만듭니다 (5회 수정 루프 등). 기존 SKILL.md의 75% 컨텍스트 압축 규칙을 유지하되, Phase별 분리(P2)가 자연스러운 완화책:
- 각 Phase는 독립 Read이므로 이전 Phase 상세가 컨텍스트에 남지 않음
- Phase 7 내부에서도 Layer 1→2→3 진행 시 이전 Layer의 상세 로그를 `.omc/ax/` JSON에 기록하고 컨텍스트에서 해제
- 서브에이전트(Agent 호출)는 자체 컨텍스트를 가지므로 메인 컨텍스트 부담 분산

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

**마이그레이션**: SKILL.md Phase 3.2의 하드코딩된 안티패턴(line 543-544의 backend-developer, frontend-developer 목록)을 해당 library 파일로 이동. SKILL.md에는 "Read library/anti-patterns/{role}.md" 지시만 남김.

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
추가:
  backend-developer-base  — API/DB 구현의 필수 프로세스, 유효성 검증, 에러 핸들링 패턴 포함
  frontend-developer-base — 방어적 데이터 접근, 상태 관리(로딩/에러/빈), 폼 패턴 포함
  system-architect-base   — 기술 스택 선정, 디렉토리 구조, 데이터 모델 설계 프로세스 포함
  content-writer-base     — 팩트체크, 출처 명시, 논리 흐름 검증 프로세스 포함
  data-analyst-base       — 소스 신뢰도 평가, 데이터 최신성 검증, 시각화 선택 기준 포함
```

각 base-agent는 skeleton 대비 해당 역할의 **검증된 <Process>, <Anti_Patterns>, <Quality_Gates>**를 포함. <Examples>와 도메인 특화 <Role>은 Phase 3에서 오버라이드.

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
- 실행 모드:
  - **검증 전용** (기본, ~30초): 기존 생성 결과물만 검증. 빠르고 반복 가능.
  - **생성+검증** (`--generate`, 수분~수십분): ax를 실제 실행하여 결과 생성 후 검증. CI/CD나 릴리스 전 사용.
- 통합: 프로젝트 루트 Makefile에서 `make test-all` 실행 (`make -C tests/ax test-all`)

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
