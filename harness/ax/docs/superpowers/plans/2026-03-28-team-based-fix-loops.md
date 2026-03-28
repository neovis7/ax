# Team-Based Fix Loops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 7의 CRUD 수정 루프와 Visual QA 피드백 루프에서, 검증 FAIL 시 TeamCreate 기반 수정 루프로 전환하여 컨텍스트 유실을 방지한다.

**Architecture:** 기존 Agent() 기반 happy path는 그대로 유지. FAIL 발생 시에만 TeamCreate로 전환하고, PASS 또는 max retries 도달 시 TeamDelete. 공통 프로토콜(7.2.1)을 한 번 정의하고 각 루프에서 참조.

**Tech Stack:** Claude Code TeamCreate/SendMessage/TeamDelete API, phase-7-execution.md 마크다운

**Spec:** `docs/superpowers/specs/2026-03-28-team-based-fix-loops-design.md`

---

### File Map

- **Modify:** `.claude/skills/ax/phases/phase-7-execution.md`
  - line 70 부근: 컨텍스트 관리 규칙에 팀 예외 추가
  - line 568 뒤: 7.2.1 신규 섹션 삽입
  - line 570-583: 수정 루프를 팀 기반으로 교체
  - line 585-608: generation-log.json 스키마에 팀 필드 추가
  - line 677-701: 피드백 루프를 팀 기반으로 교체

단일 파일 변경. 각 Task는 독립 섹션을 수정하므로 순서대로 진행.

---

### Task 1: 컨텍스트 관리 규칙에 팀 예외 추가

**Files:**
- Modify: `.claude/skills/ax/phases/phase-7-execution.md:70-76`

- [ ] **Step 1: 서브에이전트 분리 규칙에 예외 조건 추가**

line 76 (`서브에이전트의 결과는 파일로 저장하고, 부모는 파일 경로만 기록`) 뒤에 한 줄 추가:

```markdown
   - **예외 — 검증 실패 수정 루프**: 검증 FAIL 후 수정 루프에서는 `TeamCreate`로 팀을 구성하여 컨텍스트를 유지할 수 있습니다. 팀은 PASS 또는 max retries 도달 시 즉시 `TeamDelete`합니다. 상세: §7.2.1
```

- [ ] **Step 2: 변경 확인**

Read로 수정된 부분을 확인. 예외 조건이 기존 규칙의 마지막 항목 뒤에 추가되었는지 확인.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "docs(ax): 컨텍스트 관리 규칙에 TeamCreate 예외 조건 추가"
```

---

### Task 2: 7.2.1 팀 기반 수정 루프 프로토콜 신규 섹션 추가

**Files:**
- Modify: `.claude/skills/ax/phases/phase-7-execution.md` (line 568 `서버 종료` 뒤, `### 수정 루프` 앞에 삽입)

- [ ] **Step 1: 신규 섹션 삽입**

`5) 정리 - 서버 종료` 코드 블록 종료 뒤, `### 수정 루프` 앞에 아래 내용을 삽입:

````markdown

### 7.2.1 팀 기반 수정 루프 프로토콜

검증 FAIL 후 수정 루프에서 에이전트 컨텍스트를 유지하기 위한 공통 프로토콜입니다.
CRUD 수정 루프(§수정 루프)와 Visual QA 피드백 루프(§7.5)에서 참조합니다.

**트리거**: 첫 Agent() 실행은 성공했으나 검증에서 FAIL이 발생한 경우.

**팀 생성 절차**:
```
검증 FAIL 감지
  → TeamCreate("{loop-name}")
    - 멤버 구성은 각 루프별 규칙을 따름
    - mode: "bypassPermissions"
  → 각 멤버에 초기 프롬프트 전달:
    [공통]
    - 프로젝트 경로, CLAUDE.md 경로
    - progress.json 현재 상태
    - 본인이 첫 Agent()에서 생성한 파일 목록
    [루프별 고유 컨텍스트]
    - 각 루프 섹션에서 정의
```

**팀 내 수정 사이클**:
```
오케스트레이터 → SendMessage to 수정 담당 멤버: 구조화된 수정 지침
  → 멤버 수정 완료 → 완료 신호
  → 검증 재실행 (방법은 각 루프별 정의)
  → PASS → TeamDelete
  → FAIL → SendMessage: 새 실패 상세 (멤버는 이전 수정 맥락 유지)
  → 반복
```

**TeamDelete 조건**:

| 조건 | 동작 |
|------|------|
| 검증 PASS | 즉시 TeamDelete |
| max retries 도달 | TeamDelete + execution-policy.json 정책 적용 |
| 팀 멤버 에러 (크래시) | TeamDelete + §7.3 에러 복구 3단계로 폴백 |

**progress.json 연동**:

팀 활성화 시 해당 에이전트의 상태를 갱신합니다:
```json
{
  "agents": {
    "{agent-name}": {
      "status": "in_fix_loop",
      "fix_team": "{loop-name}",
      "fix_iteration": 1,
      "fix_trigger": "{실패 원인 요약}"
    }
  }
}
```
TeamDelete 후 status를 `"completed"` 또는 `"skipped"`로 갱신합니다.
````

- [ ] **Step 2: 변경 확인**

Read로 삽입된 섹션이 `5) 정리` 뒤, `### 수정 루프` 앞에 위치하는지 확인.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "docs(ax): 7.2.1 팀 기반 수정 루프 프로토콜 신규 섹션 추가"
```

---

### Task 3: 수정 루프 섹션을 팀 기반으로 교체

**Files:**
- Modify: `.claude/skills/ax/phases/phase-7-execution.md` (`### 수정 루프` 섹션)

- [ ] **Step 1: 기존 수정 루프 섹션 교체**

기존 `### 수정 루프` 코드 블록 전체를 다음으로 교체:

````markdown
### 수정 루프

> §7.2.1 팀 기반 수정 루프 프로토콜을 따릅니다.

```
스모크 테스트 FAIL 발생
  → 1) 실패 원인 분류:
       - 스키마 불일치 → api-contracts.ts 또는 DB 스키마 수정
       - 구현 불일치 → 해당 에이전트에 구체적 수정 지침 전달
       - 환경 설정 오류 → 시드/마이그레이션/dotenv 수정
       - 인증 불일치 → 토큰 저장/복원 로직 수정
  → 2) TeamCreate("crud-fix") — 팀 구성:
       - 기본: backend-developer 1명
       - Layer 3 (E2E) 실패 + 에러에 src/app/ 또는 component 포함 시:
         frontend-developer 추가
  → 3) 초기 프롬프트에 포함:
       - 실패한 Layer 번호 + 상세 에러
       - 실패 응답 + 기대값 (Layer 2) 또는 스크린샷 + 에러 메시지 (Layer 3)
       - 파일 경로: api-contracts.ts, schema.ts, crud-matrix.md, user-flows.md, crud-checklists.json
       - "위 파일들을 Read한 뒤 수정을 시작하라"
  → 4) SendMessage로 구조화된 수정 지침 전달
  → 5) 멤버 수정 완료 → 실패한 플로우만 재테스트
  → 6) PASS → TeamDelete("crud-fix")
       FAIL → SendMessage로 새 실패 상세 전달 (멤버는 이전 수정 맥락 유지)
  → 7) execution-policy.json의 max_smoke_test_retries까지 반복
  → 8) 최대 횟수 후에도 FAIL → TeamDelete("crud-fix") + on_smoke_failure에 따라 처리:
       "log_and_continue": 실패 플로우를 generation-log에 기록하고 완료 처리
```
````

- [ ] **Step 2: 변경 확인**

Read로 교체된 섹션 확인. `TeamCreate("crud-fix")`와 `TeamDelete("crud-fix")`가 짝을 이루는지, `§7.2.1` 참조가 있는지 확인.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "docs(ax): CRUD 수정 루프를 TeamCreate 기반으로 전환"
```

---

### Task 4: generation-log.json 스키마에 팀 필드 추가

**Files:**
- Modify: `.claude/skills/ax/phases/phase-7-execution.md` (`### 스모크 테스트 결과 저장` 섹션의 JSON)

- [ ] **Step 1: smoke_test JSON에 fix_team 필드 추가**

기존:
```json
  "fix_loops": 0,
  "overall": "PASS|FAIL"
```

변경:
```json
  "fix_loops": 0,
  "fix_team": null,
  "fix_iterations": [],
  "overall": "PASS|FAIL"
```

- [ ] **Step 2: JSON 블록 뒤에 필드 설명 추가**

`### 스모크 테스트 결과 저장` 섹션의 JSON 코드 블록 종료 뒤에 추가:

```markdown
팀 수정 루프 필드:
- `fix_team`: 수정 루프에서 사용된 팀 이름 (`"crud-fix"` 또는 `null`)
- `fix_iterations`: 팀 내 수정 반복 기록
  ```json
  [{ "iteration": 1, "layer": "Layer 2", "error": "POST /api/quizzes → 500", "fix_applied": "quiz.ts: params 캐스팅", "result": "PASS" }]
  ```
```

- [ ] **Step 3: 변경 확인**

Read로 스키마가 올바르게 확장되었는지 확인.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "docs(ax): generation-log.json 스키마에 fix_team/fix_iterations 추가"
```

---

### Task 5: Visual QA 피드백 루프를 팀 기반으로 교체

**Files:**
- Modify: `.claude/skills/ax/phases/phase-7-execution.md` (`## 7.5 피드백 루프` 섹션)

- [ ] **Step 1: 기존 피드백 루프 섹션 교체**

`## 7.5 피드백 루프` 전체를 다음으로 교체:

````markdown
## 7.5 피드백 루프

> §7.2.1 팀 기반 수정 루프 프로토콜을 따릅니다.

visual-qa 점수가 45/60 미만 FAIL일 때, 자동 개선 사이클을 실행합니다. 한 번에 모든 축을 수정하려 하면 오히려 다른 축이 악화될 수 있으므로, 가장 낮은 축부터 순차 개선합니다.

```
visual-qa FAIL (예: 색상 5/10, 레이아웃 4/10)
  → 1) 낮은 축 분석: 점수 6 미만인 축 추출
  → 2) 축별 수정 지침 생성
  → 3) TeamCreate("visual-fix") — 팀 구성:
       - visual-builder (수정 담당)
       - visual-qa (재평가 담당)
  → 4) 초기 프롬프트에 포함:
       - visual-builder: 6축 점수 breakdown, weak_axes, design-tokens.css 경로, 컴포넌트 파일 경로
       - visual-qa: 이전 평가 점수 + 60점 루브릭, "visual-builder 수정 완료 메시지를 받으면 재평가하라"
  → 5) 오케스트레이터 → SendMessage to visual-builder: 낮은 축부터 순차 수정 지시
  → 6) visual-builder 수정 완료 → SendMessage to visual-qa: 재평가 요청 (팀 내 직접 소통)
  → 7) visual-qa 재평가 → 오케스트레이터에 점수 반환
  → 8) ≥ 45/60 → TeamDelete("visual-fix")
       < 45/60 → 오케스트레이터 → SendMessage to visual-builder: 새 weak_axes (이전 수정 기억!)
  → 9) execution-policy.json의 max_visual_qa_retries까지 반복
  → 10) 최대 횟수 후에도 FAIL → TeamDelete("visual-fix") + on_visual_qa_failure에 따라 처리 (기본: skip_and_log — 현재 점수 기록하고 완료)
```

피드백 데이터 저장 (generation-log.json):
```json
"feedback_loops": [
  {
    "iteration": 1,
    "fix_team": "visual-fix",
    "score_before": 38,
    "weak_axes": ["색상", "레이아웃"],
    "fixes_applied": ["CSS 변수 교체", "여백 확보"],
    "score_after": 47
  }
]
```
````

- [ ] **Step 2: 변경 확인**

Read로 교체된 섹션 확인. `TeamCreate("visual-fix")`와 `TeamDelete("visual-fix")`가 짝을 이루는지, builder → qa 직접 소통이 명시되었는지, `§7.2.1` 참조가 있는지 확인.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "docs(ax): Visual QA 피드백 루프를 TeamCreate 기반으로 전환"
```

---

### Task 6: 전체 일관성 검증

**Files:**
- Read: `.claude/skills/ax/phases/phase-7-execution.md` (전체)

- [ ] **Step 1: 섹션 참조 일관성 확인**

phase-7-execution.md를 Read하여 확인:
- `§7.2.1` 참조가 수정 루프와 7.5 피드백 루프 양쪽에 있는지
- 7.2.1 섹션이 `5) 정리` 뒤, `### 수정 루프` 앞에 위치하는지
- 컨텍스트 관리 규칙에 예외 조건이 추가되었는지

- [ ] **Step 2: TeamCreate/TeamDelete 짝 확인**

Grep으로 출현 횟수 확인:
```
grep "TeamCreate" .claude/skills/ax/phases/phase-7-execution.md
grep "TeamDelete" .claude/skills/ax/phases/phase-7-execution.md
```
Expected: TeamCreate 출현마다 대응하는 TeamDelete가 존재

- [ ] **Step 3: generation-log.json 스키마 일관성**

`fix_team` 필드가 smoke_test 섹션과 feedback_loops 섹션 양쪽에 있는지 확인.

- [ ] **Step 4: 기존 ax 테스트 실행**

```bash
cd /Users/james/Claude/harness/ax && make test-ax 2>&1 | head -50
```
Expected: 기존 테스트 PASS

- [ ] **Step 5: 최종 Commit (필요 시)**

테스트 실패로 수정이 있었다면:
```bash
git add .claude/skills/ax/phases/phase-7-execution.md
git commit -m "fix(ax): 팀 기반 수정 루프 일관성 수정"
```
