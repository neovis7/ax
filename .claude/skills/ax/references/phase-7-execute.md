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

2) 도메인 에이전트 실행 (패턴에 따라 순차 또는 병렬)
   - CLAUDE.md의 위임 규칙에 따라 적절한 에이전트에게 작업 위임
   - 각 에이전트는 design-tokens.css를 참조하여 일관된 스타일 유지
   - visual-builder는 .claude/skills/ax/templates/chart-templates.md 참조

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

3) 결과 판정
   - 모든 플로우 PASS → 스모크 테스트 PASS
   - FAIL → 실패 원인 분류 후 수정 루프

4) 정리
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
  → 3) 최대 2회 반복
  → 4) 2회 후에도 FAIL → 사용자에게 에스컬레이션
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
3회차: 해당 에이전트 스킵, 사용자에게 "[에이전트명] 실패, 수동 처리 필요" 알림

API 키 부재 시:
- 이미지 생성: SVG 폴백 경로 사용 (기존 구현)
- 로그: generation-log.json에 `"fallback_used": true` 기록

비용 추적:
- 각 API 호출 비용을 generation-log.json의 `costs` 배열에 기록
- 누적 비용 $10 초과 시 사용자 확인 후 계속

## 7.4 실행 완료 보고

```
AX 실행 완료

에이전트 팀: {N}개 에이전트
패턴: {primary} + {secondary}
도메인: {domain_description}

시각 품질: {score}/60 ({PASS/FAIL})
통합 스모크 테스트: {PASS/FAIL} ({N}개 플로우 중 {M}개 통과)
생성 비용: ${total_usd} (이미지 {N}장)

결과물:
  {생성된 파일 목록}
```

## 7.5 피드백 루프

visual-qa 점수가 45/60 미만 FAIL일 때, 자동 개선 사이클을 실행합니다. 한 번에 모든 축을 수정하려 하면 오히려 다른 축이 악화될 수 있으므로, 가장 낮은 축부터 순차 개선합니다.

```
visual-qa FAIL (예: 색상 5/10, 레이아웃 4/10)
  → 1) 낮은 축 분석: 점수 6 미만인 축 추출
  → 2) 축별 수정 지침 생성
  → 3) visual-builder에 SendMessage로 수정 지침 전달
  → 4) visual-builder가 수정 후 visual-qa 재평가
  → 5) 최대 2회 반복 후에도 FAIL → 사용자에게 에스컬레이션
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
