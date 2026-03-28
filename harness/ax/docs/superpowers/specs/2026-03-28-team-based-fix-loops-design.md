# Team-Based Fix Loops — Phase 7 수정 루프 팀 전환 설계

> **날짜**: 2026-03-28
> **범위**: Phase 7 execution의 CRUD 수정 루프 + Visual QA 피드백 루프
> **방향**: Happy path 변경 없음. 검증 FAIL 시에만 TeamCreate로 전환.

## 배경

현재 Phase 7의 수정 루프는 매 반복마다 새 Agent()를 호출하므로 이전 컨텍스트가 유실됩니다.

**구체적 문제점**:
- CRUD 수정 루프: 매번 5개 파일 재Read + 이전 수정 시도의 맥락 없음 → 같은 수정 반복 위험
- Visual QA 루프: visual-builder가 이전 생성 코드 맥락 잃음 + visual-qa가 이전 점수 비교 불가 → 축 간 트레이드오프 감지 못함

**현재 우회책** (컨텍스트 유실의 증거):
- progress.json을 "재디스패치 시 먼저 Read하라" 지시 (phase-7-execution.md:166-167)
- 디자인 룰을 매 Agent() 프롬프트에 재주입 (phase-7-execution.md:171-187)
- 에이전트 정의에 5개 파일 mandatory Read 지시 (backend-developer.md:36-40)

## 설계 원칙

1. **Happy path 변경 제로**: 첫 실행은 기존 Agent() 그대로. 검증 통과하면 팀 생성 자체가 없음
2. **기존 원칙 존중**: "서브에이전트 분리 필수" 규칙에 예외 조건만 추가
3. **팀 수명 최소화**: FAIL 시 TeamCreate → PASS 또는 max retries 시 즉시 TeamDelete
4. **폴백 보장**: 팀 내 에러 발생 시 기존 3단계 에스컬레이션으로 복귀

## 전체 구조

```
Phase 7 실행 흐름 (⭐ = 변경 부분):

Stage A: backend-developer Agent() → 구현 (변경 없음)
  ↓
Stage B: Layer 1~3 검증
  → PASS → Stage C (변경 없음)
  → FAIL → ⭐ TeamCreate("crud-fix") → 수정 루프 → PASS → TeamDelete → Stage C
  ↓
Stage C: frontend-developer + content Agent() (변경 없음)
  ↓
Stage D: visual-architect Agent() → visual-builder Agent() → visual-qa Agent()
  → PASS (변경 없음)
  → FAIL → ⭐ TeamCreate("visual-fix") → 피드백 루프 → PASS → TeamDelete
```

## CRUD 수정 루프 팀 설계

### 트리거

Layer 1, 2, 또는 3 검증에서 첫 FAIL 발생 시.

### 흐름

```
Layer FAIL
  → TeamCreate("crud-fix")
    멤버: backend-developer (1명)
  → 초기 프롬프트:
    - 실패한 Layer 번호 + 상세 에러
    - 실패 응답 + 기대값 (Layer 2) 또는 스크린샷 + 에러 메시지 (Layer 3)
    - 파일 경로: api-contracts.ts, schema.ts, crud-matrix.md, user-flows.md, crud-checklists.json
    - "위 파일들을 Read한 뒤 수정을 시작하라"
  → SendMessage: 구조화된 수정 지침
  → backend-developer 수정 → 완료 신호
  → 오케스트레이터가 해당 Layer 재검증
  → PASS → TeamDelete("crud-fix")
  → FAIL → SendMessage: 새 실패 상세 (컨텍스트 유지!)
  → max_smoke_test_retries 도달 → TeamDelete + on_smoke_failure 정책
```

### 팀 구성 규칙

- **기본**: backend-developer 1명
- **조건부 추가**: Layer 3 (E2E) 실패이고 에러 메시지에 `src/app/` 또는 `component` 포함 → frontend-developer 추가
- **근거**: Layer 1~2는 API/DB 문제이므로 백엔드만 필요. Layer 3의 프론트엔드 문제만 조건부 추가.

### 컨텍스트 이점

- 2회차: "아까 스키마를 이렇게 고쳤는데 그래도 FAIL" → 다른 접근 가능
- 3회차: 1, 2회차 수정 이력이 모두 컨텍스트에 → 패턴 인식 가능
- 현재: 매번 백지 → 같은 수정 반복 위험

## Visual QA 피드백 루프 팀 설계

### 트리거

visual-qa 평가 점수 < 45/60.

### 흐름

```
visual-qa FAIL
  → TeamCreate("visual-fix")
    멤버:
      - visual-builder (수정 담당)
      - visual-qa (재평가 담당)
  → 초기 프롬프트:
    - 6축 점수 breakdown + weak_axes (점수 < 6인 축)
    - design-tokens.css 경로
    - 생성된 컴포넌트 파일 경로들
    - visual-qa에게: "visual-builder 수정 완료 메시지를 받으면 재평가하라"
  → 오케스트레이터 → SendMessage to visual-builder: 낮은 축부터 순차 수정 지시
  → visual-builder 수정 완료 → SendMessage to visual-qa: 재평가 요청 (팀 내 직접 소통)
  → visual-qa 재평가 → 오케스트레이터에 점수 반환
  → ≥ 45/60 → TeamDelete("visual-fix")
  → < 45/60 → 오케스트레이터 → SendMessage to visual-builder: 새 weak_axes (이전 수정 기억!)
  → max_visual_qa_retries 도달 → TeamDelete + on_visual_qa_failure 정책
```

### visual-qa를 팀에 포함하는 이유

- 이전 평가 맥락 유지: "이전엔 색상 5점 → 지금 7점, 개선됨. 하지만 레이아웃이 4→3으로 후퇴"
- 축 간 트레이드오프 감지 가능
- 현재는 매번 독립 평가라 개선/후퇴 비교 불가

### visual-architect를 제외하는 이유

- architect는 design-tokens.css 생성 후 역할 종료
- 토큰 자체를 바꾸는 상황은 거의 없음 (builder가 토큰 활용 개선이 대부분)

### 두 루프 비교

| | CRUD 루프 | Visual QA 루프 |
|---|---|---|
| 팀 멤버 수 | 1명 (조건부 +1) | 2명 (고정) |
| 검증 주체 | 오케스트레이터 (Layer 재실행) | 팀 내 visual-qa |
| 소통 패턴 | 오케스트레이터 ↔ developer | builder ↔ qa 직접 |

## 팀 생명주기 관리

### 초기 프롬프트 규칙

팀 생성 시 첫 Agent()의 컨텍스트 유실을 보상하기 위해 구조화된 초기 프롬프트를 제공합니다:

```
[공통]
- 프로젝트 경로, CLAUDE.md 경로
- progress.json 현재 상태
- 본인이 첫 Agent()에서 생성한 파일 목록

[CRUD 팀 - backend-developer]
- 실패한 Layer 번호 + 상세 에러
- api-contracts.ts, schema.ts, crud-matrix.md 경로
- "위 파일들을 Read한 뒤 수정을 시작하라"

[Visual 팀 - visual-builder]
- 6축 점수 breakdown + weak_axes
- design-tokens.css, 컴포넌트 파일 경로들
- "위 파일들을 Read한 뒤 수정을 시작하라"

[Visual 팀 - visual-qa]
- 이전 평가 점수 + 기준 (60점 루브릭)
- "visual-builder 수정 완료 메시지를 받으면 재평가하라"
```

### TeamDelete 조건

| 조건 | 동작 |
|------|------|
| 검증 PASS | 즉시 TeamDelete |
| max retries 도달 | TeamDelete + execution-policy 정책 적용 |
| 팀 멤버 에러 (크래시) | TeamDelete + 기존 에러 복구 3단계로 폴백 |

### 기존 에러 복구와의 관계

7.3의 3단계 에스컬레이션(동일 재시도 → 프롬프트 단순화 → 스킵)은 팀 외부에서만 적용:

```
첫 Agent() 실행 실패?
  → 기존 3단계 에스컬레이션 (변경 없음)

첫 Agent() 성공 → 검증 FAIL?
  → TeamCreate → 팀 내 수정 루프
  → 팀 내에서 멤버 크래시?
    → TeamDelete → 기존 3단계 에스컬레이션으로 폴백
```

### progress.json 연동

팀 활성화 상태를 progress.json에 기록:

```json
{
  "agents": {
    "backend-developer": {
      "status": "in_fix_loop",
      "fix_team": "crud-fix",
      "fix_iteration": 2,
      "fix_trigger": "Layer 2 FAIL: POST /api/quizzes → 500"
    }
  }
}
```

## phase-7-execution.md 변경 범위

### 변경하는 부분

| 위치 | 현재 | 변경 |
|------|------|------|
| 수정 루프 (line 570-583) | Agent() 재호출 기반 | TeamCreate 기반 수정 루프로 교체 |
| 7.5 피드백 루프 (line 677-701) | SendMessage 언급하나 실제는 Agent() 재호출 | 실제 TeamCreate + SendMessage 기반으로 교체 |
| 컨텍스트 관리 (line 66-96) | "반드시 별도 Agent() 호출" | 예외 조건 추가: "검증 FAIL 시 수정 루프는 TeamCreate 허용" |
| generation-log.json 스키마 (line 585-608) | fix_loops 카운트만 | fix_team, fix_iterations 필드 추가 |

### 변경하지 않는 부분

- Stage A (백엔드 첫 실행), Stage C (프론트엔드 + 콘텐츠): Agent() 그대로
- Stage B Layer 1~3 검증 로직 자체: 검증 방법 동일
- Stage D 첫 실행 (visual-architect → builder → qa): Agent() 그대로
- 7.3 에러 복구 3단계: 그대로 (팀 폴백 경로만 추가)
- 7.4 완료 기준, 진행률 표시: 기존 포맷 유지

### 새로 추가하는 부분

**7.2.1 팀 기반 수정 루프 프로토콜 (신규 섹션)**:

수정 루프와 피드백 루프에 공통 적용되는 TeamCreate/TeamDelete 프로토콜을 한 곳에 정의. 기존 수정 루프(570)와 피드백 루프(677)에서 참조.

```
7.2.1 팀 기반 수정 루프 프로토콜 (NEW)
  - 트리거 조건
  - 팀 생성 + 초기 프롬프트 규칙
  - 팀 내 수정 사이클
  - TeamDelete 조건
  - 폴백 규칙
  - progress.json 연동

수정 루프 (기존 570-583) → "7.2.1 프로토콜을 따른다" + CRUD 고유 규칙
피드백 루프 (기존 677-701) → "7.2.1 프로토콜을 따른다" + Visual 고유 규칙
```

## 향후 확장 가능성

이 설계가 검증된 후 고려할 수 있는 확장:

- **code-reviewer cascade**: 리뷰어가 cross-cutting 이슈 발견 시 backend + frontend를 팀으로 묶어 조율 (루프가 아닌 조율 패턴 — 별도 설계 필요)
- **execution-policy.json 옵션**: `"fix_loop_mode": "team" | "subagent"` 선택지 (현재는 YAGNI)
