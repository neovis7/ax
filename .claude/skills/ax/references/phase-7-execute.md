# Phase 7: 실행 (`--execute` 전용)

> `--execute` 플래그가 없으면 이 Phase를 건너뜁니다.

## 7.0 진행 상태 추적

Phase 7 실행 중 각 단계마다 진행 상태를 사용자에게 표시합니다.

**표시 형식:**
```
━━━ Phase 7 실행 진행 ━━━
[1/N] visual-architect — 디자인 토큰 생성 중...
[2/N] {에이전트명} — {작업 설명}...
[3/N] {에이전트명} — {작업 설명}...
...
[N/N] visual-qa — 시각 품질 평가 중... → {score}/60 {PASS/FAIL}
━━━ 완료 ━━━
```

**구현 방법:**
1. team-architecture.json의 `agents` 배열에서 실행 순서 결정
2. 각 에이전트 호출 전에 `[순번/총수] 에이전트명 — 작업 설명...` 출력
3. 에이전트 완료 후 결과 요약 (성공/실패/산출물 경로) 출력
4. 전체 완료 시 요약 보고

**TaskCreate 연동:**
- 각 에이전트 실행을 개별 Task로 등록하여 진행 추적
- `TaskCreate("에이전트명: 작업 설명")` → 실행 시작 시 `in_progress` → 완료 시 `completed`

## 7.05 인프라 사전 점검 (Pre-flight Check)

code 도메인에서 실행 전에 필요한 도구/서비스가 준비되었는지 자동 확인합니다.
실패 항목이 있으면 사용자에게 알리고 해결 방법을 안내합니다.

```
1) 기본 도구 확인
   - node/npm 또는 python3/pip 설치 여부 (Bash: which node, which python3)
   - git 설치 여부 (Bash: git --version)
   - 패키지 매니저 확인 (npm/pnpm/yarn/bun)

2) 배포 플랫폼 확인 (domain_sub_type=fullstack/api 시)
   - Vercel CLI: `vercel --version` → 미설치 시 "npm i -g vercel" 안내
   - Vercel 링크: `vercel whoami` → 미로그인 시 "vercel login" 안내
   - 프로젝트 연결: `vercel link` 상태 확인

3) 데이터베이스 확인 (team-architecture.json에 DB 관련 에이전트 있을 때)
   - Supabase: `supabase --version` → 미설치 시 안내
   - Neon: 환경변수 DATABASE_URL 존재 여부
   - SQLite: 기본 내장, 확인 불필요

4) API 키 확인 (도메인 리서치 또는 AI 기능 포함 시)
   - .env.local 또는 .env 파일 존재 여부
   - 필수 키 목록 (team-architecture.json 기반):
     OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY 등
   - 미설정 시 "해당 기능은 SVG 폴백으로 대체됩니다" 안내

5) 결과 판정
   - 필수(node/git): FAIL 시 실행 중단 + 설치 안내
   - 권장(Vercel/DB): FAIL 시 경고만 표시 + 실행 계속 (로컬 개발 가능)
   - 선택(API 키): FAIL 시 정보만 표시 + 폴백 경로 안내
```

점검 결과를 `.omc/ax/generation-log.json`의 `preflight` 필드에 기록합니다.

## 7.05.5 배포 타겟 프로파일

배포 환경에 따라 기술적 제약을 자동 감지하고 에이전트에 전달합니다:

```
Vercel (서버리스):
  - pg.Pool max = 1 (세션 풀러 한도 방지)
  - prisma generate를 build 스크립트에 포함 필수
  - Cookie: Secure; SameSite=Strict 필수
  - tsconfig.json에 prisma/ 디렉토리 exclude 필수
  - idleTimeoutMillis: 20000, connectionTimeoutMillis: 10000

Docker/전통 서버:
  - pg.Pool max = 10-20
  - 표준 빌드 파이프라인
```

감지 방법: `vercel.json` 또는 `vercel --version` 존재 시 Vercel 프로파일 선택.
프로파일을 `.omc/ax/deployment-profile.json`에 저장하고
backend-developer 에이전트 프롬프트에 제약사항으로 주입합니다.

### 7.0.5 execution-policy 로드

Phase 7 시작 시 `${PROJECT_DIR}/.omc/ax/execution-policy.json`을 Read합니다.
이 파일이 없으면 기본값으로 런타임 생성합니다.
이후 모든 리트라이/에스컬레이션 분기에서 이 정책의 값을 참조합니다.

## 7.1 실행 준비

Phase 1~6에서 생성된 에이전트 팀으로 도메인 작업을 즉시 수행합니다.

1. `.omc/ax/domain-analysis.json`에서 `domain_description` 확인
2. `.omc/ax/team-architecture.json`에서 에이전트 팀 구성 확인 + 실행 순서 결정
3. `${PROJECT_DIR}/CLAUDE.md`의 위임 규칙 확인
4. 실행할 에이전트 수(N) 산출 → 진행 추적 초기화

## 7.2 시각화 파이프라인 실행

모든 도메인에서 시각화 에이전트 3인조를 순차 실행합니다:

```
1) visual-architect 호출 (Agent, mode: "bypassPermissions", model: "haiku")
   - .claude/skills/ax/templates/design-tokens-template.css를 Read
   - 도메인에 맞게 플레이스홀더를 채워 design-tokens.css 생성
   - 입력: domain-analysis.json의 domain_type, domain_description
   - 출력: ${PROJECT_DIR}/design-tokens.css

2) 도메인 에이전트 실행 (순차 + 병렬 하이브리드)
   - CLAUDE.md의 위임 규칙에 따라 적절한 에이전트에게 작업 위임
   - 각 에이전트는 design-tokens.css를 참조하여 일관된 스타일 유지
   - visual-builder는 .claude/skills/ax/templates/chart-templates.md 참조

   === Stage A: 백엔드 우선 실행 ===
   - backend-developer 에이전트 실행 (API 전체 구현)
   - 완료 후 서버 시작

   === Stage B: 3-Layer CRUD 검증 게이트 (MUST PASS) ===

   **Layer 1: 정적 완성도 검증**
   validate_project.py의 체크포인트 11-14를 실행합니다.
   FAIL 항목이 있으면 백엔드/프론트엔드 에이전트에 수정 지시 후 재실행.

   **Layer 2: API 행동 검증 (기존 Stage B 확장 대체)**
   기존 Zod safeParse 검증을 포함하면서, CRUD 전체 사이클을 순서대로 실행합니다.

   절차:
   a) 시드 데이터 삽입 (npm run db:seed)
   b) 서버 시작 + health check
   c) 로그인하여 인증 토큰 획득
   d) CRUD 매트릭스의 각 엔티티에 대해 전체 사이클 실행:
      1. CREATE — POST → 201 + id 확인 + Zod 스키마 일치
      2. READ(목록) — GET → 200 + 배열 + created_id 포함
      3. READ(상세) — GET/{id} → 200 + id 일치 + 필드값 일치
      4. UPDATE — PUT/{id} → 200 + 재조회 시 수정값 반영
      5. DELETE — DELETE/{id} → 200/204 + 재조회 시 404
      6. 엣지 케이스 — 없는 ID→404, 필수 필드 누락→400
   e) 각 응답을 해당 Zod 스키마로 safeParse
   f) 실제 응답 JSON을 .omc/api-snapshots/{endpoint-name}.json에 저장
   g) 결과 판정:
      - 전체 PASS → Layer 3로 진행 (또는 Playwright 불가 시 Stage C로)
      - FAIL → 해당 에이전트에 구조화된 수정 지시 (실패 응답 + 기대값 첨부)
      - execution-policy.json의 max_smoke_test_retries까지 루프
      - 최대 횟수 초과 → on_smoke_failure에 따라 처리

   payload 자동 생성: api-contracts.ts Zod 스키마 + prisma/seed.ts 참조
   테스트 플랜 저장: .omc/ax/crud-tests.json

   **Layer 3: E2E 사용성 검증 (Playwright 기반, 선택적)**
   Layer 2 PASS 후, 프론트엔드의 실제 사용성을 브라우저 테스트로 확인합니다.

   사전 조건: `npx playwright install chromium` 성공 시에만 실행.

   각 CRUD 작업에 대해:
   1. 네비게이션 — 메뉴 클릭 → 페이지 로드 → JS 에러 0
   2. 목록 페이지 — 시드 데이터 표시 + 빈 상태 EmptyState
   3. 생성 폼 — 버튼→모달 + 유효성 에러 + 성공 피드백 + 목록 반영
   4. 수정 폼 — 프리필 + 수정 + 성공 피드백
   5. 삭제 — 확인 다이얼로그 + 목록에서 제거

   Graceful degradation:
   - Playwright 설치 실패 → Layer 3 전체 스킵, Layer 2까지만 실행
   - 브라우저 실행 실패 (headless 환경) → Layer 3 스킵 + 로그
   - 개별 테스트 타임아웃 (30초) → 해당 테스트 FAIL, 나머지 계속
   - 전체 Layer 3 타임아웃 (5분) → 완료된 테스트까지만 기록

   결과: .omc/ax/e2e-results/ (스크린샷 포함)

   **수정 루프 통합:**
   Layer 1 실패 → "코드가 없다" → 구현 지시
   Layer 2 실패 → "동작이 틀리다" → 실패 응답 + 기대값 첨부
   Layer 3 실패 → "UI가 안 된다" → 스크린샷 + 에러 메시지 첨부
   각 Layer 최대 execution-policy.json의 max_smoke_test_retries회 루프.
   최대 횟수 후 FAIL → 스킵 + 로그 (무개입 정책).

   === Stage C: 프론트엔드 + 콘텐츠 병렬 실행 ===
   계약 검증 게이트 PASS 후:
   - frontend-developer 에이전트 실행 (프롬프트에 다음 필수 포함):
     * ".omc/api-snapshots/ 디렉토리를 Read하여 실제 API 응답 구조를 확인하라"
     * "prisma/seed.ts를 Read하여 테스트 계정을 확인하라 (자체 생성 금지)"
     * "모든 API 데이터 접근에 optional chaining (?.) 필수"
     * "배열 메서드 앞에 (data ?? []) 필수"
   - question-content-specialist 에이전트 병렬 실행 (콘텐츠 생성, 해당 시)

   **[v2] 프론트엔드 에이전트 추가 지침:**
   c) 프론트엔드 에이전트가 `useGet<T>` 사용 시:
      - `useGet`은 `ApiResponse.data`를 추출하므로 반환값은 `T` 직접
      - 페이지네이션 API는 `useGet` 대신 raw `apiFetch` 사용하여 `meta` 접근

3) visual-qa 호출 (Agent, mode: "bypassPermissions")
   - 생성된 결과물의 시각 품질을 60점 루브릭으로 평가
   - 45/60 미만 → visual-builder에 수정 지침과 함께 재작업 요청 (최대 2회)
   - 45/60 이상 → PASS

4) 비용 추적
   - AI 이미지 생성 호출이 있었으면 비용을 generation-log.json에 기록:
     "image_costs": { "openai": N, "gemini": N, "total_usd": N }
```

## 7.2.5 통합 E2E 스모크 테스트 (code 도메인 — fullstack/api)

> **적용 조건**: `domain_sub_type`이 `fullstack` 또는 `api`이고, `--execute` 모드일 때만.
> 병렬 에이전트가 각각 성공해도, 통합 시 불일치가 발생할 수 있습니다.

### 사전 검증: 정적 일치성 확인

런타임 테스트 전에 정적 검증을 수행합니다:

```
1) DB 스키마 ↔ API 계약 컬럼명 일치 검증
   - DB 마이그레이션의 컬럼명과 api-contracts.ts의 Zod 필드명 비교
   - snake_case → camelCase 변환 외의 불일치 검출
   - 예: DB=table_name, API=resourceType → FAIL

2) API 계약 ↔ 시드 스크립트 일치 검증
   - 시드 INSERT 컬럼명과 DB 스키마 컬럼명 비교
   - 누락 컬럼, 오타, NOT NULL인데 시드에서 빠진 컬럼 검출

3) 환경 설정 검증
   - 시드 스크립트에 dotenv 로드가 있는지 확인
   - .env.example에 필수 환경변수가 나열되어 있는지 확인

4) 인증 일관성 검증
   - API 계약의 @persistence와 프론트엔드 토큰 저장 방식이 일치하는지 확인
   - 메모리 전용 토큰이면 refresh endpoint + httpOnly cookie 구현 확인

5) CRUD 완성도 검증
   - docs/crud-matrix.md의 '필수=O' 행 전수 검사:
     a) 백엔드: 해당 HTTP 메서드가 라우트 파일에 존재하는지
     b) 프론트엔드: 해당 페이지/컴포넌트 파일이 존재하는지
     c) 프론트엔드: hooks가 정의되고 **실제 import/사용**되는지 (dead hook 검출)
     d) 네비게이션: 메뉴 목록의 모든 항목이 TopNav + 라우터에 등록되어 있는지
     e) API 경로 일치: 프론트 hook의 API 경로와 백엔드 라우트 경로가 일치하는지
        (예: hook이 POST /wrong-answers/mark-reviewed를 호출하는데 백엔드는 PUT /review → FAIL)
   - 검증 결과를 generation-log.json의 smoke_test.crud_coverage에 저장
```

### 런타임 스모크 테스트

정적 검증 통과 후, 실제 서버를 띄워 핵심 플로우를 검증합니다:

```
1) 환경 준비
   - DB 마이그레이션 실행 (있으면)
   - 시드 데이터 삽입 (있으면)
   - 서버 시작 (백그라운드)
   - 서버 health check (최대 30초 대기)

2) 필수 플로우 스모크 테스트
   인증 플로우 (인증 기반 서비스면 반드시 실행):
   a) POST /auth/login → 토큰 + 유저 정보 반환 확인
   b) 토큰으로 보호된 API 호출 → 200 확인
   c) 토큰 없이 보호된 API 호출 → 401 확인

   핵심 도메인 플로우 (docs/user-flows.md 참조):
   - 플로우의 단계별 시퀀스를 curl로 순차 실행
   - 각 단계의 응답에 user-flows.md에서 명시한 필수 필드가 포함되는지 확인
   - 이전 단계 응답 데이터를 다음 단계 요청에 사용

3) 브라우저 렌더링 검증 (v2 추가)
   - 모든 프론트엔드 페이지를 Playwright 또는 curl로 순회
   - 각 페이지에서 JavaScript 런타임 에러 0개 확인
   - "Cannot read properties of undefined" 에러 → 프론트엔드 방어 코드 누락
   - 빈 상태(데이터 0건)에서도 크래시 없이 EmptyState 렌더링 확인

4) 결과 판정
   - 모든 플로우 + 모든 페이지 렌더링 PASS → 스모크 테스트 PASS
   - FAIL → 실패 원인 분류 후 수정 루프

5) 정리
   - 서버 종료
```

### 수정 루프

```
스모크 테스트 FAIL 발생
  → 1) 실패 원인 분류:
       - 스키마 불일치 → api-contracts.ts 또는 DB 스키마 수정
       - 구현 불일치 → 해당 에이전트에 구체적 수정 지침 전달
       - 환경 설정 오류 → 시드/마이그레이션/dotenv 수정
       - 인증 불일치 → 토큰 저장/복원 로직 수정
  → 2) 수정 후 해당 플로우만 재테스트
  → 3) execution-policy.json의 max_smoke_test_retries까지 반복
  → 4) 최대 횟수 후에도 FAIL → on_smoke_failure에 따라 처리:
       "log_and_continue": 실패 플로우를 generation-log에 기록하고 완료 처리
```

### 스모크 테스트 결과 저장 (generation-log.json)

```json
"smoke_test": {
  "executed": true,
  "static_checks": {
    "db_api_column_match": "PASS|FAIL",
    "api_seed_column_match": "PASS|FAIL",
    "env_config": "PASS|FAIL",
    "auth_consistency": "PASS|FAIL"
  },
  "runtime_flows": [
    {
      "flow": "인증",
      "steps": [
        { "step": "login", "status": "PASS|FAIL" },
        { "step": "authenticated_request", "status": "PASS|FAIL" }
      ],
      "overall": "PASS|FAIL"
    }
  ],
  "fix_loops": 0,
  "overall": "PASS|FAIL"
}
```

## 7.3 에러 복구

에이전트 호출 실패 시 3단계 에스컬레이션 — 동일 프롬프트로 재시도하면 같은 이유로 실패할 가능성이 높으므로, 단순화가 핵심입니다.

1회차: 동일 에이전트 재시도 (프롬프트 동일)
2회차: 프롬프트를 핵심만 남기고 단순화하여 재시도
3회차: 해당 에이전트 스킵, execution-policy.json의 on_agent_failure에 따라 처리 (기본: skip_and_log)

API 키 부재 시:
- 이미지 생성: SVG 폴백 경로 사용 (기존 구현)
- 로그: generation-log.json에 `"fallback_used": true` 기록

비용 추적:
- 각 API 호출 비용을 generation-log.json의 `costs` 배열에 기록
- execution-policy.json의 cost_limit_usd 초과 시: 로그에 경고 기록 + 최종 보고에 포함 (실행은 계속)

## 7.4 Phase 7 완료 기준 (모두 충족 시)

다음 기준을 **모두** 충족해야 Phase 7 완료로 간주합니다:

1. **빌드 성공**: `npm run build` 에러 0
2. **타입 체크**: `npx tsc --noEmit` 에러 0
3. **API 계약 검증**: 모든 엔드포인트 Zod safeParse 성공 (Stage B 결과)
4. **스모크 테스트**: 인증 + 핵심 플로우 PASS
5. **브라우저 렌더링 검증**: 모든 페이지 접속 시 JS 런타임 에러 0
   - 빈 상태(데이터 0건)에서도 크래시 없이 EmptyState 렌더링 확인
6. **CRUD 매트릭스**: `docs/crud-matrix.md`의 필수=O 행 전수 검사
7. **시각 품질**: visual-qa 45/60 이상 (해당 시)
8. **보안 체크리스트**:
   - 하드코딩된 시크릿 0개 (grep으로 확인)
   - JWT 시크릿 폴백값 없음
   - 쿠키 Secure + SameSite=Strict
   - 감사 로그 INSERT-ONLY (DELETE/UPDATE 없음)
9. **Layer 1 정적 검증**: validate_project.py 체크포인트 11-14 PASS (code 도메인)

하나라도 미충족 시 Phase 7 완료로 간주하지 않습니다.

## 7.4.1 실행 완료 보고

```
AX 실행 완료

에이전트 팀: {N}개 에이전트
패턴: {primary} + {secondary}
도메인: {domain_description}

### 성공 항목
- 에이전트: {성공}/{전체} 실행 완료
- CRUD 매트릭스: {구현된 수}/{전체 필수} 항목 구현
- 시각 품질: {score}/60 ({PASS/FAIL})
- 스모크 테스트: {PASS/FAIL} ({N}개 플로우 중 {M}개 통과)

### 자동 스킵된 항목 (수동 확인 필요)
{각 항목: 에이전트명/기능명 + 실패 원인 + 수동 확인 방법}
없으면 "모든 항목 성공"

### 수정 루프 이력
- 검증 수정: {N}회 (수정 내용 요약)
- 스모크 테스트 수정: {N}회 (수정 내용 요약)
- Visual-QA 수정: {N}회 (수정 내용 요약)

### 비용
- 이미지 생성: ${total_usd} ({API별 장수})
- cost_limit_usd 초과 여부: {예/아니오}
```

## 7.5 피드백 루프

visual-qa 점수가 45/60 미만 FAIL일 때, 자동 개선 사이클을 실행합니다. 한 번에 모든 축을 수정하려 하면 오히려 다른 축이 악화될 수 있으므로, 가장 낮은 축부터 순차 개선합니다.

```
visual-qa FAIL (예: 색상 5/10, 레이아웃 4/10)
  → 1) 낮은 축 분석: 점수 6 미만인 축 추출
  → 2) 축별 수정 지침 생성
  → 3) visual-builder에 SendMessage로 수정 지침 전달
  → 4) visual-builder가 수정 후 visual-qa 재평가
  → 5) execution-policy.json의 max_visual_qa_retries까지 반복
  → 6) 최대 횟수 후에도 FAIL → on_visual_qa_failure에 따라 처리 (기본: skip_and_log — 현재 점수 기록하고 완료)
```

피드백 데이터 저장 (generation-log.json):
```json
"feedback_loops": [
  {
    "iteration": 1,
    "score_before": 38,
    "weak_axes": ["색상", "레이아웃"],
    "fixes_applied": ["CSS 변수 교체", "여백 확보"],
    "score_after": 47
  }
]
```
