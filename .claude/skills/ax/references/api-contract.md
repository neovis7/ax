### 2.4.2 API 계약 생성 (code 도메인 — fullstack/api)

> **적용 조건**: `domain_sub_type`이 `fullstack` 또는 `api`이고, backend + frontend 에이전트가 병렬 실행될 때만.

병렬 에이전트 간 API 응답 구조 불일치를 방지하기 위해, Phase 3(에이전트 생성) 전에 공유 API 계약을 정의합니다.

**절차:**
1. 도메인 분석에서 식별된 API 엔드포인트 목록 도출
2. 각 엔드포인트의 **행동 의도(intent)**, 요청/응답 Zod 스키마, **상태별 응답 변형**을 `src/types/api-contracts.ts`에 정의
3. 에이전트 프롬프트에 `src/types/api-contracts.ts` 참조 의무를 포함

**생성 파일**: `${PROJECT_DIR}/src/types/api-contracts.ts`

```typescript
import { z } from "zod";

// ─── 엔드포인트별 계약: intent(행동 의도) + schema(데이터 구조) + variants(상태별 응답) ───

/**
 * GET /quiz/sessions/:id
 *
 * @intent 퀴즈 세션의 현재 상태에 따른 데이터 반환
 *   - status=active: 풀어야 할 문제 목록(questions[])을 반환 → 프론트엔드가 퀴즈 UI를 렌더링
 *   - status=completed: 결과(score, results[])를 반환 → 프론트엔드가 결과 화면을 렌더링
 *
 * @consumer frontend-developer: 퀴즈 진행 화면 + 결과 화면
 * @producer backend-developer: 세션 상태에 따른 분기 응답
 */
export const GetSessionResponseSchema = z.discriminatedUnion("status", [
  z.object({
    sessionId: z.string().uuid(),
    status: z.literal("active"),
    questions: z.array(QuestionSchema),  // active일 때 필수
    timeLimitMinutes: z.number().optional(),
  }),
  z.object({
    sessionId: z.string().uuid(),
    status: z.literal("completed"),
    score: z.number(),
    results: z.array(QuestionResultSchema),  // completed일 때 필수
  }),
]);
```

**계약 작성 필수 규칙:**

각 엔드포인트 스키마에는 반드시 다음 3가지를 포함합니다:
1. **`@intent` JSDoc**: 이 API가 사용자 관점에서 무엇을 하는지 (CRUD 용어가 아닌 행동 관점)
2. **`@consumer`/`@producer` JSDoc**: 이 API를 호출하는 에이전트와 구현하는 에이전트
3. **상태별 응답 변형**: 리소스 상태(active/completed/draft 등)에 따라 응답이 달라지면 `z.discriminatedUnion`으로 명시

**인증 기반 서비스 필수 계약:**

인증(auth) 엔드포인트가 있는 fullstack 프로젝트에서는 다음을 반드시 정의합니다:

1. **세션 지속성 방식**: 토큰을 어디에 저장하는지 (localStorage / httpOnly cookie / 메모리)
   - localStorage: 페이지 새로고침 시 세션 유지됨. XSS 주의.
   - httpOnly cookie: 새로고침 시 자동 전송. CSRF 주의. 백엔드가 cookie를 설정해야 함.
   - 메모리 전용: **반드시** httpOnly cookie refresh 구현이 동반되어야 함. 그렇지 않으면 새로고침 시 세션 유실.
2. **토큰 갱신 플로우**: refresh token 구현 방식 (cookie 기반 자동 갱신 또는 localStorage 기반 수동 갱신)
3. **로그인 후 상태 복원**: 페이지 새로고침 시 사용자 정보를 어떻게 복원하는지 명시

```typescript
/**
 * 인증 계약 — 세션 지속성
 *
 * @persistence localStorage (accessToken + user JSON)
 *   - 로그인 시: localStorage에 token + user 저장
 *   - 새로고침 시: localStorage에서 token + user 복원
 *   - 로그아웃 시: localStorage에서 삭제
 *
 * @alternative httpOnly cookie (accessToken은 cookie, user는 /auth/me로 복원)
 *   - 이 방식 선택 시 백엔드가 Set-Cookie 헤더를 반드시 설정해야 함
 *   - 프론트엔드는 credentials: 'include' 사용
 */
```

**컬럼명 일치 규칙:**

API 스키마의 필드명은 DB 스키마의 컬럼명과 매핑을 명시합니다:
- snake_case(DB) → camelCase(API) 자동 변환만 허용
- 의미가 다른 이름 사용 금지 (예: DB=`table_name`, API=`resourceType` → 위반)
- 시드 스크립트의 INSERT 컬럼명도 DB 스키마와 반드시 일치

**에이전트 프롬프트 삽입 규칙:**
- backend-developer 프롬프트에: "API 응답은 반드시 `src/types/api-contracts.ts`의 스키마와 **@intent 주석**에 맞춰 구현하라. 스키마 형태만 맞추고 의도가 다르면 계약 위반이다. 인증 계약의 세션 지속성 방식을 반드시 따르라."
- frontend-developer 프롬프트에: "API 호출 결과는 반드시 `src/types/api-contracts.ts`의 스키마로 파싱하라. **@intent 주석**을 읽고 각 상태별 응답 변형을 처리하라. 인증 계약의 세션 복원 방식을 반드시 구현하라."
- 이 규칙은 Phase 3의 `<Constraints>` 및 `<Process>`에 자동 삽입

**team-architecture.json에 추가:**
```json
{
  "api_contract": {
    "enabled": true,
    "file": "src/types/api-contracts.ts",
    "endpoints": ["{식별된 엔드포인트 목록}"],
    "intent_documented": true,
    "column_mapping_enforced": true,
    "auth_persistence": "localStorage|httpOnly|memory+refresh"
  }
}
```
