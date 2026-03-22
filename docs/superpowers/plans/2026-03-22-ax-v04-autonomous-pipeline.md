# ax v0.4 — 완전 자율 파이프라인 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ax의 code 도메인 실행 완성도를 높이고, 인터뷰 후 완전 무개입 autopilot을 실현한다.

**Architecture:** execution-policy.json으로 모든 런타임 분기를 사전 결정하고, 3-Layer CRUD 검증으로 완성도를 보장하며, SKILL.md를 Hub-and-Spoke로 분해하여 컨텍스트 효율을 극대화한다.

**Tech Stack:** Python 3 (검증 스크립트), Markdown (스킬/에이전트 정의), JSON (정책/테스트/시나리오)

**Spec:** `docs/superpowers/specs/2026-03-22-ax-v04-autonomous-pipeline-design.md`

---

## File Map

### P0: 무개입 아키텍처
| Action | File | Purpose |
|--------|------|---------|
| Modify | `.claude/skills/ax/SKILL.md` | Phase 1 입력 파싱에 `--skip-interview` 추가, Phase 6.3 에스컬레이션 → execution-policy 참조, Phase 6.7 인터뷰 게이트 → 인터뷰 강제화 |
| Modify | `.claude/skills/ax/references/phase-7-execute.md` | Stage B/스모크/비용/visual-qa의 하드코딩 → execution-policy 참조 |
| Modify | `.claude/skills/ax/references/interview-mode.md` | PPT 스타일 질문을 인터뷰로 통합 (Phase 7에서 질문 제거) |

### P3a: API Fixture (P1 선행 의존)
| Action | File | Purpose |
|--------|------|---------|
| Modify | `.claude/skills/ax/SKILL.md` | Phase 2.4.2 이후 api-fixtures.ts 생성 지시 추가 |

### P1: CRUD 깊이 검증
| Action | File | Purpose |
|--------|------|---------|
| Modify | `.claude/skills/ax/SKILL.md` | Phase 6에 Layer 1 정적 검증 강화, Phase 7에 Layer 2/3 검증 추가 |
| Modify | `.claude/skills/ax/references/phase-7-execute.md` | Stage B를 Layer 2로 대체, Layer 3 E2E 추가, 수정 루프 통합 |
| Modify | `.claude/skills/ax/tools/validate_project.py` | 체크포인트 11-14 추가 |

### P2: SKILL.md 분해
| Action | File | Purpose |
|--------|------|---------|
| Create | `.claude/skills/ax/phases/phase-0-init.md` | Phase 0 추출 |
| Create | `.claude/skills/ax/phases/phase-1-analysis.md` | Phase 1 추출 |
| Create | `.claude/skills/ax/phases/phase-2-architecture.md` | Phase 2 추출 |
| Create | `.claude/skills/ax/phases/phase-3-agents.md` | Phase 3 추출 |
| Create | `.claude/skills/ax/phases/phase-4-skills.md` | Phase 4 추출 |
| Create | `.claude/skills/ax/phases/phase-5-orchestrator.md` | Phase 5 추출 |
| Create | `.claude/skills/ax/phases/phase-6-validation.md` | Phase 6 추출 |
| Create | `.claude/skills/ax/phases/phase-7-execution.md` | Phase 7 추출 (phase-7-execute.md 통합) |
| Rewrite | `.claude/skills/ax/SKILL.md` | 오케스트레이터로 축소 (~150줄) |
| Delete | `.claude/skills/ax/references/phase-7-execute.md` | phase-7-execution.md로 통합됨 |

### P4: 검증 스크립트 강화
| Action | File | Purpose |
|--------|------|---------|
| Create | `tests/ax/tools/validate_ax.py` | ax 스킬 자체 무결성 검증 (Tier 2) |
| Create | `tests/ax/tools/run_scenario.py` | JSON 시나리오 실행기 (Tier 3) |
| Create | `tests/ax/scenarios/fullstack-saas.json` | SaaS 풀스택 시나리오 |
| Create | `tests/ax/scenarios/cli-tool.json` | CLI 도구 시나리오 |
| Create | `tests/ax/scenarios/presentation-slides.json` | 프레젠테이션 시나리오 |
| Create | `tests/ax/scenarios/api-microservice.json` | API 마이크로서비스 시나리오 |
| Create | `tests/ax/scenarios/ecommerce-platform.json` | 이커머스 시나리오 |
| Create | `tests/ax/scenarios/research-analysis.json` | 리서치 분석 시나리오 |
| Create | `Makefile` | 프로젝트 루트 테스트 통합 |
| Modify | `.claude/skills/ax/tools/validate_project.py` | 체크포인트 11-14 (P1에서 구현) |

### P3b: 생성 품질 강화 (나머지)
| Action | File | Purpose |
|--------|------|---------|
| Create | `.claude/skills/ax/library/anti-patterns/backend-common.md` | 범용 백엔드 안티패턴 |
| Create | `.claude/skills/ax/library/anti-patterns/frontend-common.md` | 범용 프론트엔드 안티패턴 |
| Create | `.claude/skills/ax/library/anti-patterns/fullstack-integration.md` | 프론트-백 통합 안티패턴 |
| Create | `.claude/skills/ax/library/anti-patterns/auth-patterns.md` | 인증/세션 안티패턴 |
| Create | `.claude/skills/ax/library/anti-patterns/database-patterns.md` | DB/ORM 안티패턴 |
| Create | `.claude/skills/ax/library/base-agents/backend-developer-base.md` | 백엔드 베이스 에이전트 |
| Create | `.claude/skills/ax/library/base-agents/frontend-developer-base.md` | 프론트엔드 베이스 에이전트 |
| Create | `.claude/skills/ax/library/base-agents/system-architect-base.md` | 시스템 아키텍트 베이스 |
| Create | `.claude/skills/ax/library/base-agents/content-writer-base.md` | 콘텐츠 작성 베이스 |
| Create | `.claude/skills/ax/library/base-agents/data-analyst-base.md` | 데이터 분석 베이스 |
| Modify | `.claude/skills/ax/SKILL.md` (or `phases/phase-3-agents.md`) | Phase 3 안티패턴 하드코딩 → library Read 참조로 교체, base-agent 매칭 우선순위 추가 |

---

## Task 1: P0 — execution-policy.json 스키마 및 Phase 1 플래그 파싱

**Files:**
- Modify: `.claude/skills/ax/SKILL.md:91-101` (Phase 1 입력 파싱)
- Modify: `.claude/skills/ax/SKILL.md:180-217` (domain-analysis.json flags 스키마)

- [ ] **Step 1: SKILL.md Phase 1 입력 파싱에 `--skip-interview` 추가**

`.claude/skills/ax/SKILL.md`의 Phase 1 입력 파싱 섹션 (~line 91-101)에 다음을 추가:

```markdown
- `--skip-interview` 플래그 존재 여부 확인 → `--execute` 시 인터뷰를 건너뛰고 기본값으로 실행
```

- [ ] **Step 2: domain-analysis.json flags 스키마에 skip_interview 추가**

`.claude/skills/ax/SKILL.md`의 flags JSON 스키마 (~line 208-215)에 추가:

```json
"skip_interview": "{true|false — --skip-interview 플래그 여부}"
```

- [ ] **Step 3: Phase 6.7 이후 execution-policy.json 생성 지시 추가**

SKILL.md의 Phase 6.7 (~line 816-847) 뒤에 다음 섹션을 추가:

```markdown
### Phase 6.8: execution-policy.json 생성

인터뷰 완료 직후 (또는 `--skip-interview` 시 Phase 6.7 직후) 다음 정책 파일을 생성합니다:

파일 위치: `${PROJECT_DIR}/.omc/ax/execution-policy.json`

인터뷰에서 수집된 값(PPT 스타일, 디자인 레시피 등)을 반영하고,
수집되지 않은 값은 기본값을 사용합니다:

{execution-policy.json 스키마 — 스펙 lines 97-112 전체}

Phase 7의 모든 분기에서 이 파일을 Read하여 자동 결정합니다.
```

- [ ] **Step 4: 변경 검증**

SKILL.md에서 `--skip-interview` 문자열을 Grep하여 파싱 섹션 + flags 스키마 + Phase 6.8에 모두 존재하는지 확인.

- [ ] **Step 5: 커밋**

```bash
git add .claude/skills/ax/SKILL.md
git commit -m "feat(ax): --skip-interview 플래그 + execution-policy.json 생성 Phase 추가"
```

---

## Task 2: P0 — SKILL.md 에스컬레이션 → execution-policy 참조로 교체

**Files:**
- Modify: `.claude/skills/ax/SKILL.md:722-737` (Phase 6.3 검증 실패 루프)
- Modify: `.claude/skills/ax/SKILL.md:816-847` (Phase 6.7 인터뷰 게이트)

- [ ] **Step 1: Phase 6.3 검증 실패 시 3지선다 메뉴 삭제 + policy 참조**

SKILL.md ~line 722-737의 검증 실패 수정 루프를 다음으로 교체:

```markdown
**검증 실패 시 자동 수정 루프:**

```
검증 FAIL 발생
  → execution-policy.json의 max_validation_retries 값까지 수정 루프 실행
    → 실패 항목을 구조화된 피드백으로 정리
    → Phase 3/4 에이전트에 SendMessage로 수정 요청
    → 수정된 파일만 재검증
    → PASS → 완료
  → 최대 횟수 초과 시: execution-policy.json의 on_validation_failure에 따라 처리
    → "log_and_continue": 실패 항목을 validation-report.json에 기록하고 다음 Phase로 진행
    → "escalate": 사용자에게 에스컬레이션 (향후 interactive 모드)
```
```

- [ ] **Step 2: Phase 6.7 인터뷰 게이트 → 인터뷰 강제화**

SKILL.md ~line 816-847의 인터뷰 게이트를 다음으로 교체:

```markdown
## Phase 6.7: 인터뷰 (`--execute` 시 자동 실행)

> `--execute` 플래그가 없으면 이 Phase를 건너뜁니다.
> `--skip-interview` 플래그가 있으면 인터뷰를 건너뛰고 기본값으로 execution-policy.json을 생성합니다.

`--execute` 시 인터뷰를 자동으로 실행합니다 (기존: 선택 질문 → 변경: 자동 실행).
사용자가 인터뷰를 원하지 않으면 `--skip-interview`를 명시적으로 사용해야 합니다.

**`--interview` 플래그가 이미 있으면**: 동일하게 인터뷰 프로세스를 실행합니다.
**`--skip-interview` 플래그가 있으면**: 인터뷰 없이 기본값으로 Phase 6.8로 진행합니다.

인터뷰 프로세스: Read `.claude/skills/ax/references/interview-mode.md`
```

- [ ] **Step 3: 변경 검증**

SKILL.md에서 `선택하세요 (1/2)` 문자열이 사라졌는지 확인 (인터뷰 게이트 선택지 제거).
`execution-policy.json` 문자열이 Phase 6.3 + Phase 6.8에 존재하는지 확인.

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/ax/SKILL.md
git commit -m "feat(ax): Phase 6 에스컬레이션 → execution-policy 참조 + 인터뷰 강제화"
```

---

## Task 3: P0 — phase-7-execute.md 하드코딩 → execution-policy 참조

**Files:**
- Modify: `.claude/skills/ax/references/phase-7-execute.md:116-129` (Stage B)
- Modify: `.claude/skills/ax/references/phase-7-execute.md:229-241` (스모크 테스트)
- Modify: `.claude/skills/ax/references/phase-7-execute.md:271-283` (에러 복구 + 비용)
- Modify: `.claude/skills/ax/references/phase-7-execute.md:324-333` (visual-qa 피드백)

- [ ] **Step 1: Stage B 계약 검증 — 하드코딩 루프 횟수 제거**

phase-7-execute.md ~line 128의 `최대 2회 루프`를:

```markdown
      - FAIL → 백엔드 에이전트에 수정 지시 (execution-policy.json의 max_smoke_test_retries까지 루프)
      - 최대 횟수 초과 후에도 FAIL → execution-policy.json의 on_smoke_failure에 따라 처리
```

- [ ] **Step 2: 스모크 테스트 — 수정 루프 횟수 + 에스컬레이션 교체**

phase-7-execute.md ~line 239-240의 수정 루프를:

```markdown
  → 3) execution-policy.json의 max_smoke_test_retries까지 반복
  → 4) 최대 횟수 후에도 FAIL → on_smoke_failure에 따라 처리
       "log_and_continue": 실패 플로우를 generation-log에 기록하고 완료 처리
```

- [ ] **Step 3: 비용 확인 — 사용자 질문 제거**

phase-7-execute.md ~line 283의 `누적 비용 $10 초과 시 사용자 확인 후 계속`을:

```markdown
비용 추적:
- 각 API 호출 비용을 generation-log.json의 `costs` 배열에 기록
- execution-policy.json의 cost_limit_usd 초과 시: 로그에 경고 기록 + 최종 보고에 포함 (실행은 계속)
```

- [ ] **Step 4: visual-qa 피드백 루프 — 에스컬레이션 교체**

phase-7-execute.md ~line 332의 `최대 2회 반복 후에도 FAIL → 사용자에게 에스컬레이션`을:

```markdown
  → 5) execution-policy.json의 max_visual_qa_retries까지 반복
       최대 횟수 후에도 FAIL → on_visual_qa_failure에 따라 처리
       "skip_and_log": 현재 점수를 기록하고 완료 처리
```

- [ ] **Step 5: Phase 7 시작 부분에 execution-policy.json Read 지시 추가**

phase-7-execute.md의 `## 7.1 실행 준비` (~line 86) 앞에:

```markdown
## 7.0.5 execution-policy 로드

Phase 7 시작 시 `${PROJECT_DIR}/.omc/ax/execution-policy.json`을 Read합니다.
이 파일이 없으면 기본값으로 런타임 생성합니다.
이후 모든 리트라이/에스컬레이션 분기에서 이 정책의 값을 참조합니다.
```

- [ ] **Step 6: 변경 검증**

phase-7-execute.md에서 `사용자에게 에스컬레이션` 또는 `사용자 확인` 문자열이 남아있지 않은지 확인.
`execution-policy.json` 문자열이 5곳 이상 존재하는지 확인.

- [ ] **Step 7: 커밋**

```bash
git add .claude/skills/ax/references/phase-7-execute.md
git commit -m "feat(ax): Phase 7 전체 에스컬레이션 → execution-policy 참조로 교체"
```

---

## Task 4: P0 — PPT 스타일 질문을 인터뷰로 통합

**Files:**
- Modify: `.claude/skills/ax/references/interview-mode.md`
- Modify: `.claude/skills/ax/SKILL.md:899-922` (Phase 7 PPT 스타일 선택)

- [ ] **Step 1: SKILL.md Phase 7의 PPT 스타일 선택 질문 제거**

SKILL.md ~line 899-922의 PPT 스타일 선택 질문 블록을:

```markdown
**PPT 스타일 선택 (인터뷰에서 수집):**

`execution-policy.json`의 `ppt_style` 값을 사용합니다.
인터뷰에서 선택된 스타일이 반영되어 있으며, `--skip-interview` 시 도메인 기본값이 적용됩니다.
도메인 기본값: 테크→glassmorphism, 프리미엄→dark-premium, 스타트업→gradient-modern, 경영진→keynote, 크리에이티브→neo-brutalist, 데이터→minimal-swiss.
```

- [ ] **Step 2: interview-mode.md Phase A-3에 기본값 매핑 추가**

interview-mode.md의 Phase A-3 섹션 (~line 167-180)에 `--skip-interview` 시 자동 선택 로직 추가:

```markdown
**`--skip-interview` 시 자동 선택:**
도메인 키워드에서 자동 매핑:
- "테크/기술/AI/SaaS" → glassmorphism
- "프리미엄/럭셔리/브랜드" → dark-premium
- "스타트업/피치/투자" → gradient-modern
- "경영/임원/보고" → keynote
- "크리에이티브/에이전시/디자인" → neo-brutalist
- "데이터/분석/통계" → minimal-swiss
- 기본값 (매칭 없음) → gradient-modern
```

- [ ] **Step 3: 변경 검증**

SKILL.md에서 `선택 (A~H):` 문자열이 사라졌는지 확인.

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/ax/SKILL.md .claude/skills/ax/references/interview-mode.md
git commit -m "feat(ax): PPT 스타일 질문을 인터뷰로 통합 + 도메인 기본값 자동 매핑"
```

---

## Task 5: P0 — 최종 보고서 강화

**Files:**
- Modify: `.claude/skills/ax/SKILL.md:797-814` (Phase 6.6 완료 보고)
- Modify: `.claude/skills/ax/references/phase-7-execute.md:305-320` (Phase 7.4.1 실행 완료 보고)

- [ ] **Step 1: Phase 6.6 완료 보고에 자동 스킵 항목 추가**

SKILL.md ~line 797-814의 완료 보고 템플릿에 "자동 스킵된 항목" 섹션 추가.

- [ ] **Step 2: Phase 7.4.1 실행 완료 보고 강화**

phase-7-execute.md ~line 305-320의 보고 템플릿을 스펙의 최종 보고서 형식(성공/자동스킵/수정루프이력/비용)으로 교체.

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/ax/SKILL.md .claude/skills/ax/references/phase-7-execute.md
git commit -m "feat(ax): 최종 보고서에 자동 스킵 항목 + 수정 루프 이력 + 비용 포함"
```

---

## Task 6: P3a — API Fixture 자동 생성 지시 추가

**Files:**
- Modify: `.claude/skills/ax/SKILL.md:352-372` (Phase 2.4.2 API 계약 생성 직후)

- [ ] **Step 1: Phase 2.4.2 이후 api-fixtures.ts 생성 지시 추가**

SKILL.md Phase 2.4.2 섹션 (~line 372) 뒤에 다음을 추가:

```markdown
### 2.4.2.1 API Fixture 생성

api-contracts.ts 생성 직후, 프론트엔드가 실제 응답 구조를 참조할 수 있도록 응답 예시 파일을 생성합니다:

**생성 파일**: `${PROJECT_DIR}/src/types/api-fixtures.ts`

**포함 내용** (각 Zod 스키마에 대해):
- 목록 응답 예시 (1-2개 항목)
- 생성 요청 예시 (Omit<Schema, 'id' | 'createdAt'>)
- 빈 상태 응답 예시 (빈 배열)
- 유효성 에러 응답 예시 (error + details 배열)

**값 생성 규칙**:
- 시드 데이터(prisma/seed.ts)가 있으면 해당 값 참조
- 없으면 Zod 스키마의 타입/제약에 맞는 예시 값 생성
- 외래 키는 시드 데이터의 실제 ID 사용
- 날짜는 ISO 8601 형식 예시

**에이전트 프롬프트 삽입**:
- frontend-developer: "API 응답 구조를 추측하지 마세요. src/types/api-fixtures.ts를 Read하여 실제 응답 구조를 확인한 뒤 구현하세요."
```

- [ ] **Step 2: 변경 검증**

SKILL.md에서 `api-fixtures.ts` 문자열이 존재하는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/ax/SKILL.md
git commit -m "feat(ax): Phase 2.4.2.1 API fixture 자동 생성 지시 추가"
```

---

## Task 6.5: P3a — CRUD 구현 체크리스트 자동 생성 지시 추가

**Files:**
- Modify: `.claude/skills/ax/SKILL.md:397-447` (Phase 2.4.4 CRUD 매트릭스 직후)

- [ ] **Step 1: Phase 2.4.4 뒤에 CRUD 체크리스트 생성 지시 추가**

SKILL.md Phase 2.4.4 CRUD 매트릭스 섹션 (~line 447) 뒤에 다음을 추가:

```markdown
### 2.4.5 CRUD 구현 체크리스트 자동 생성

CRUD 매트릭스의 각 '필수=O' 행에 대해 에이전트별 구체적 구현 체크리스트를 자동 도출합니다.

**생성 파일**: `${PROJECT_DIR}/.omc/ax/crud-checklists.json`

**구조:**
```json
{
  "entities": [
    {
      "name": "Question",
      "operations": [
        {
          "operation": "Create",
          "backend_checklist": [
            "POST /questions 라우트 핸들러",
            "Zod 스키마로 요청 바디 유효성 검증",
            "유효성 실패 시 400 + 구체적 에러 메시지 반환",
            "DB INSERT 실행",
            "성공 시 201 + 생성된 객체(id 포함) 반환",
            "try-catch로 DB 에러 핸들링"
          ],
          "frontend_checklist": [
            "생성 버튼 → 모달/페이지 열기",
            "폼: 필수 필드 표시 + 클라이언트 유효성 에러",
            "제출 시 로딩 상태 (버튼 비활성화 + 스피너)",
            "성공 시 토스트/알림 + 목록 자동 새로고침",
            "실패 시 서버 에러 메시지 표시",
            "모달 닫기 후 상태 초기화"
          ]
        }
      ]
    }
  ]
}
```

**operation별 체크리스트 템플릿:**
- Create: 라우트 + 유효성 + DB INSERT + 201 응답 / 버튼→모달 + 폼 + 로딩 + 피드백
- Read(목록): 라우트 + 페이지네이션 + 필터링 / 테이블 + 빈 상태 + 로딩
- Read(상세): 라우트 + 404 처리 / 상세 뷰 + 로딩
- Update: 라우트 + 유효성 + 존재 확인 + DB UPDATE / 프리필 폼 + 수정 + 피드백
- Delete: 라우트 + 존재 확인 + DB DELETE / 확인 다이얼로그 + 목록 갱신

**주입 시점:**
- Phase 3 에이전트 `<Process>` 섹션에 "crud-checklists.json을 Read하고 해당 엔티티의 체크리스트를 모두 구현하라" 지시 추가
- Phase 7 에이전트 프롬프트에 동적 주입: 해당 에이전트 role의 체크리스트만 발췌
```

- [ ] **Step 2: 변경 검증**

SKILL.md에서 `crud-checklists.json` 문자열이 존재하는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add .claude/skills/ax/SKILL.md
git commit -m "feat(ax): Phase 2.4.5 CRUD 구현 체크리스트 자동 생성 지시 추가"
```

---

## Task 7: P1 — validate_project.py 체크포인트 11-14 추가

**Files:**
- Modify: `.claude/skills/ax/tools/validate_project.py`

- [ ] **Step 1: 체크포인트 11 — CRUD 핸들러 실체 확인**

validate_project.py에 다음 검증 추가 (기존 check 10 뒤):

```python
# 11. CRUD 핸들러 실체 (라우트 파일에 실제 DB 호출이 있는지)
crud_ok = True
route_files = glob.glob(os.path.join(project_dir, 'src/**/routes/**/*.ts'), recursive=True) + \
              glob.glob(os.path.join(project_dir, 'src/**/routes/**/*.js'), recursive=True)
for rf in route_files:
    with open(rf, 'r') as f:
        content = f.read()
    # POST/PUT/DELETE 핸들러가 있는데 DB 호출이 없으면 빈 핸들러 의심
    has_mutation = any(kw in content for kw in ['post(', 'put(', 'delete(', 'POST', 'PUT', 'DELETE'])
    has_db_call = any(kw in content for kw in ['prisma.', 'knex(', 'db.query', 'pool.query', '.create(', '.update(', '.delete(', '.findMany(', '.findUnique('])
    if has_mutation and not has_db_call:
        crud_ok = False
        failures.append(f"빈 핸들러 의심: {os.path.basename(rf)} — mutation 핸들러에 DB 호출 없음")
checks['crud_handler_substance'] = 'PASS' if crud_ok or not route_files else 'PASS'
if route_files and not crud_ok:
    checks['crud_handler_substance'] = 'FAIL'
```

- [ ] **Step 2: 체크포인트 12 — 프론트엔드 폼 컴포넌트**

```python
# 12. 프론트엔드 폼 컴포넌트 (Create/Update용)
form_ok = True
page_files = glob.glob(os.path.join(project_dir, 'src/**/pages/**/*.tsx'), recursive=True) + \
             glob.glob(os.path.join(project_dir, 'src/**/components/**/*.tsx'), recursive=True)
form_keywords = ['<form', 'onSubmit', 'handleSubmit', 'useForm', 'FormData']
has_any_form = False
for pf in page_files:
    with open(pf, 'r') as f:
        content = f.read()
    if any(kw in content for kw in form_keywords):
        has_any_form = True
        break
if page_files and not has_any_form:
    form_ok = False
    failures.append("프론트엔드에 폼 컴포넌트가 하나도 없음 (Create/Update UI 누락 의심)")
checks['frontend_form_components'] = 'PASS' if form_ok or not page_files else 'FAIL'
```

- [ ] **Step 3: 체크포인트 13 — API hook 실제 사용**

```python
# 13. API hook 실제 사용 (정의만 있고 미사용인 dead hook 검출)
hook_ok = True
hook_files = glob.glob(os.path.join(project_dir, 'src/**/hooks/**/*.ts'), recursive=True)
for hf in hook_files:
    with open(hf, 'r') as f:
        hcontent = f.read()
    # export function useSomething 또는 export const useSomething 패턴 추출
    hook_names = re.findall(r'export\s+(?:function|const)\s+(use\w+)', hcontent)
    for hook in hook_names:
        # 이 hook이 다른 파일에서 import되는지 확인
        found = False
        for sf in page_files:
            with open(sf, 'r') as f:
                if hook in f.read():
                    found = True
                    break
        if not found:
            hook_ok = False
            failures.append(f"Dead hook: {hook} ({os.path.basename(hf)}) — 정의만 있고 미사용")
checks['hook_usage'] = 'PASS' if hook_ok else 'FAIL'
```

- [ ] **Step 4: 체크포인트 14 — 에러/로딩/빈 상태 UI**

```python
# 14. 에러/로딩/빈 상태 UI
state_warnings = []
for pf in page_files:
    with open(pf, 'r') as f:
        content = f.read()
    basename = os.path.basename(pf)
    if not any(kw in content for kw in ['isLoading', 'loading', 'Spinner', 'skeleton', 'Skeleton']):
        state_warnings.append(f"로딩 상태 없음: {basename}")
    if not any(kw in content for kw in ['isError', 'error', 'Error', 'catch']):
        state_warnings.append(f"에러 상태 없음: {basename}")
    if not any(kw in content for kw in ['length === 0', '.length === 0', 'empty', 'Empty', '데이터가 없', 'No data']):
        state_warnings.append(f"빈 상태 없음: {basename}")
# 경고만 (FAIL 아님) — 모든 페이지가 해당되진 않으므로
checks['ui_states'] = 'PASS'
if state_warnings:
    failures.extend(state_warnings[:10])  # 상위 10개만
```

- [ ] **Step 5: 스크립트 실행 테스트**

```bash
python3 .claude/skills/ax/tools/validate_project.py .
```

Expected: 에러 없이 JSON 결과 출력 (현재 디렉토리는 ax 자체이므로 agent 파일 없어도 OK).

- [ ] **Step 6: 커밋**

```bash
git add .claude/skills/ax/tools/validate_project.py
git commit -m "feat(ax): validate_project.py 체크포인트 11-14 추가 (CRUD 실체, 폼, hook, UI 상태)"
```

---

## Task 8: P1 — Phase 7에 3-Layer 검증 지시 추가

**Files:**
- Modify: `.claude/skills/ax/references/phase-7-execute.md` (Stage B 대체 + Layer 2/3 추가)
- Modify: `.claude/skills/ax/SKILL.md` (Phase 6 Layer 1 강화)

- [ ] **Step 1: phase-7-execute.md의 Stage B를 Layer 2로 교체**

phase-7-execute.md의 `=== Stage B: 계약 검증 게이트 ===` 섹션 (~line 115-129)을 Layer 2 검증으로 교체. 기존 safeParse + CRUD 시퀀스 검증 + 엣지 케이스 포함.

- [ ] **Step 2: Layer 3 E2E 사용성 검증 추가**

phase-7-execute.md의 `## 7.2.5 통합 E2E 스모크 테스트` 섹션 뒤에 Layer 3 (Playwright 기반) 검증 추가. graceful degradation 4가지 시나리오 포함.

- [ ] **Step 3: 수정 루프 통합 섹션 추가**

Layer 1/2/3 실패 시 구조화된 수정 지시 형식과 루프 정책 추가.

- [ ] **Step 4: SKILL.md Phase 6.1에 Layer 1 강화 지시 추가**

SKILL.md Phase 6.1 구조 검증 (~line 648-686)에 체크포인트 11-14 (validate_project.py) 실행 지시 추가.

- [ ] **Step 5: 커밋**

```bash
git add .claude/skills/ax/references/phase-7-execute.md .claude/skills/ax/SKILL.md
git commit -m "feat(ax): 3-Layer CRUD 검증 — Stage B→Layer 2 대체 + Layer 3 E2E + 수정 루프 통합"
```

---

## Task 9: P2 — 호환성 브릿지 + Phase 7 추출

**Files:**
- Modify: `.claude/skills/ax/SKILL.md` (오케스트레이터 로직 추가)
- Create: `.claude/skills/ax/phases/` (디렉토리)
- Create: `.claude/skills/ax/phases/phase-7-execution.md` (Phase 7 + phase-7-execute.md 통합)

- [ ] **Step 1: git tag로 현재 상태 표시**

```bash
git tag ax-v03-pre-decomposition
```

- [ ] **Step 2: phases/ 디렉토리 생성**

```bash
mkdir -p .claude/skills/ax/phases
```

- [ ] **Step 3: SKILL.md에 호환성 브릿지 로직 추가**

SKILL.md의 `## 실행 파이프라인` 섹션 (~line 32-36)에 Phase 실행 프로토콜 추가:

```markdown
### Phase 실행 프로토콜

각 Phase 실행 시:
1. `phases/phase-{N}-*.md` 파일 존재 확인 (Glob)
2. 존재 → Read(`phases/phase-{N}-*.md`) — 추출된 Phase 지시사항 따라 실행
3. 미존재 → 이 파일 아래의 인라인 Phase 섹션 실행 (기존 동작)
4. 산출물 생성 + 출력 계약 검증
5. TaskUpdate(completed) → 다음 Phase
```

- [ ] **Step 4: Phase 7을 phases/phase-7-execution.md로 추출**

SKILL.md의 Phase 7 섹션 (~line 848-end) + references/phase-7-execute.md 전체를 통합하여 `phases/phase-7-execution.md` 생성. SKILL.md에서 Phase 7 인라인 내용은 유지 (호환성 브릿지가 phases/ 파일 우선).

- [ ] **Step 5: 검증**

```bash
# phases/ 파일 존재 확인
ls .claude/skills/ax/phases/phase-7-execution.md
# SKILL.md에 호환성 브릿지 로직 존재 확인
grep -c "phases/phase-" .claude/skills/ax/SKILL.md
```

- [ ] **Step 6: 커밋**

```bash
git add .claude/skills/ax/phases/phase-7-execution.md .claude/skills/ax/SKILL.md
git commit -m "feat(ax): P2 Phase 7 추출 + 호환성 브릿지 — phase-7-execute.md 통합"
```

---

## Task 10: P2 — Phase 0-6 순차 추출

**Files:**
- Create: `.claude/skills/ax/phases/phase-0-init.md`
- Create: `.claude/skills/ax/phases/phase-1-analysis.md`
- Create: `.claude/skills/ax/phases/phase-2-architecture.md`
- Create: `.claude/skills/ax/phases/phase-3-agents.md`
- Create: `.claude/skills/ax/phases/phase-4-skills.md`
- Create: `.claude/skills/ax/phases/phase-5-orchestrator.md`
- Create: `.claude/skills/ax/phases/phase-6-validation.md`

- [ ] **Step 1: Phase 1-2 추출**

SKILL.md의 Phase 1 (~line 88-237) → `phases/phase-1-analysis.md`
SKILL.md의 Phase 2 (~line 239-504) → `phases/phase-2-architecture.md`

- [ ] **Step 2: 커밋**

```bash
git add .claude/skills/ax/phases/phase-{1,2}-*.md
git commit -m "feat(ax): P2 Phase 1-2 추출 (도메인 분석 + 팀 아키텍처)"
```

- [ ] **Step 3: Phase 3-4 추출**

SKILL.md의 Phase 3 (~line 506-592) → `phases/phase-3-agents.md`
SKILL.md의 Phase 4 (~line 593-613) → `phases/phase-4-skills.md`

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/ax/phases/phase-{3,4}-*.md
git commit -m "feat(ax): P2 Phase 3-4 추출 (에이전트 + 스킬 생성)"
```

- [ ] **Step 5: Phase 5-6 추출**

SKILL.md의 Phase 5 (~line 615-642) → `phases/phase-5-orchestrator.md`
SKILL.md의 Phase 6 (~line 644-815) → `phases/phase-6-validation.md`

- [ ] **Step 6: 커밋**

```bash
git add .claude/skills/ax/phases/phase-{5,6}-*.md
git commit -m "feat(ax): P2 Phase 5-6 추출 (오케스트레이터 + 검증)"
```

- [ ] **Step 7: Phase 0 추출**

SKILL.md의 Phase 0 (~line 48-87) → `phases/phase-0-init.md`

- [ ] **Step 8: 커밋**

```bash
git add .claude/skills/ax/phases/phase-0-init.md
git commit -m "feat(ax): P2 Phase 0 추출 (초기화)"
```

---

## Task 11: P2 — SKILL.md 축소 + phase-7-execute.md 삭제

**Files:**
- Rewrite: `.claude/skills/ax/SKILL.md` (~150줄 오케스트레이터)
- Delete: `.claude/skills/ax/references/phase-7-execute.md`

- [ ] **Step 1: SKILL.md에서 인라인 Phase 내용 삭제**

모든 Phase가 추출 완료되었으므로, SKILL.md에서 Phase 0-7의 인라인 내용을 삭제하고 오케스트레이터만 남김. 유지할 내용:
- frontmatter
- 사용법 + 플래그 설명
- 실행 규칙 (공통)
- Phase 파일 경로 매핑 테이블
- Phase 실행 프로토콜
- 확장 기능 참조 링크

- [ ] **Step 2: phase-7-execute.md 삭제**

```bash
git rm .claude/skills/ax/references/phase-7-execute.md
```

- [ ] **Step 3: 검증 — 모든 Phase 파일 존재 확인**

```bash
ls .claude/skills/ax/phases/phase-*.md | wc -l
# Expected: 8
```

- [ ] **Step 4: 검증 — SKILL.md 줄 수 확인**

```bash
wc -l .claude/skills/ax/SKILL.md
# Expected: ~150 (±30)
```

- [ ] **Step 5: 커밋**

```bash
git add .claude/skills/ax/SKILL.md
git rm .claude/skills/ax/references/phase-7-execute.md
git commit -m "feat(ax): P2 완료 — SKILL.md 오케스트레이터 축소 (~150줄) + phase-7-execute.md 삭제"
```

---

## Task 12: P4 — validate_ax.py (Tier 2)

**Files:**
- Create: `tests/ax/tools/validate_ax.py`

- [ ] **Step 1: validate_ax.py 작성**

6개 체크포인트를 구현하는 Python 스크립트 작성:
1. SKILL.md 파일 참조 무결성
2. Phase 파일 완전성 (phases/ 0-7)
3. 템플릿 플레이스홀더 검증
4. base-agent frontmatter 유효성
5. anti-pattern 라이브러리 존재
6. domain-patterns.md 5개 도메인 정의

- [ ] **Step 2: 실행 테스트**

```bash
python3 tests/ax/tools/validate_ax.py
```

Expected: JSON 결과 출력, Phase 파일 완전성 PASS (Task 10 완료 후).

- [ ] **Step 3: 커밋**

```bash
git add tests/ax/tools/validate_ax.py
git commit -m "feat(ax): validate_ax.py — ax 스킬 자체 무결성 검증 (Tier 2)"
```

---

## Task 13: P4 — run_scenario.py + JSON 시나리오 (Tier 3)

**Files:**
- Create: `tests/ax/tools/run_scenario.py`
- Create: `tests/ax/scenarios/fullstack-saas.json`
- Create: `tests/ax/scenarios/cli-tool.json`
- Create: `Makefile`

- [ ] **Step 1: run_scenario.py 작성**

검증 전용 모드의 시나리오 실행기. 기존 생성 결과물의 domain-analysis.json, team-architecture.json, 생성 파일을 JSON 시나리오의 기대값과 비교.

- [ ] **Step 2: fullstack-saas.json 시나리오 작성**

기존 `tests/ax/scenario-saas.md` 내용을 JSON 형식으로 변환.

- [ ] **Step 3: cli-tool.json 시나리오 작성**

code 도메인, domain_sub_type=cli → 파이프라인 패턴, 에이전트 4-6개, cli-developer 필수.

- [ ] **Step 4: presentation-slides.json 시나리오 작성**

document 도메인, domain_sub_type=presentation → 파이프라인+생성-검증, content-researcher + content-writer + slide-builder 필수.

- [ ] **Step 5: api-microservice.json 시나리오 작성**

code 도메인, domain_sub_type=api → 전문가 풀+생성-검증, api-architect + service-developer 필수.

- [ ] **Step 6: ecommerce-platform.json 시나리오 작성**

기존 `tests/ax/scenario-ecommerce.md` 내용을 JSON 형식으로 변환. code+business 복합 도메인.

- [ ] **Step 7: research-analysis.json 시나리오 작성**

research 도메인 → 감독자 패턴, data-collector + data-analyst 필수.

- [ ] **Step 8: Makefile 작성**

```makefile
.PHONY: test-all test-ax test-scenarios test-project

test-all: test-ax test-scenarios

test-ax:
	python3 tests/ax/tools/validate_ax.py

test-scenarios:
	python3 tests/ax/tools/run_scenario.py tests/ax/scenarios/ --all

test-project:
	python3 .claude/skills/ax/tools/validate_project.py $(PROJECT)
```

- [ ] **Step 5: 실행 테스트**

```bash
make test-ax
```

Expected: Tier 2 검증 PASS.

- [ ] **Step 6: 커밋**

```bash
git add tests/ax/tools/run_scenario.py tests/ax/scenarios/ Makefile
git commit -m "feat(ax): P4 완료 — run_scenario.py + JSON 시나리오 + Makefile"
```

---

## Task 14: P3b — Anti-Pattern 라이브러리

**Files:**
- Create: `.claude/skills/ax/library/anti-patterns/backend-common.md`
- Create: `.claude/skills/ax/library/anti-patterns/frontend-common.md`
- Create: `.claude/skills/ax/library/anti-patterns/fullstack-integration.md`
- Create: `.claude/skills/ax/library/anti-patterns/auth-patterns.md`
- Create: `.claude/skills/ax/library/anti-patterns/database-patterns.md`

- [ ] **Step 1: SKILL.md (또는 phases/phase-3-agents.md)에서 하드코딩된 안티패턴 추출**

Phase 3.2의 backend-developer/frontend-developer 안티패턴 목록을 각 파일로 이동.

- [ ] **Step 2: backend-common.md 작성**

카테고리별: 요청 처리, 인증, 에러 처리, 응답 형식. ❌/✅ 형식.

- [ ] **Step 3: frontend-common.md 작성**

카테고리별: 방어적 데이터 접근, 상태 관리, 폼 처리, 접근성.

- [ ] **Step 4: fullstack-integration.md 작성**

카테고리별: API 경로 일치, 응답 구조, 토큰 저장, CRUD 완성도.

- [ ] **Step 5: auth-patterns.md 작성**

카테고리별: JWT, 쿠키, refresh 토큰, 세션 지속성.

- [ ] **Step 6: database-patterns.md 작성**

카테고리별: 마이그레이션, 시드, 컬럼명 일관성, ORM 패턴.

- [ ] **Step 7: Phase 3에 "Read library/anti-patterns/{role}.md" 지시 추가**

phases/phase-3-agents.md에서 하드코딩 안티패턴을 라이브러리 Read 참조로 교체.

- [ ] **Step 8: 커밋**

```bash
git add .claude/skills/ax/library/anti-patterns/ .claude/skills/ax/phases/phase-3-agents.md
git commit -m "feat(ax): anti-pattern 라이브러리 5개 파일 + Phase 3 참조 교체"
```

---

## Task 15: P3b — Base Agent 라이브러리 확장

**Files:**
- Create: `.claude/skills/ax/library/base-agents/backend-developer-base.md`
- Create: `.claude/skills/ax/library/base-agents/frontend-developer-base.md`
- Create: `.claude/skills/ax/library/base-agents/system-architect-base.md`
- Modify: `.claude/skills/ax/phases/phase-3-agents.md` (골든 템플릿 매칭 우선순위)

- [ ] **Step 1: backend-developer-base.md 작성**

frontmatter(name, role, model) + `<Role>`, `<Process>` (필수 7단계), `<Anti_Patterns>` (backend-common.md 참조 지시), `<Quality_Gates>`, `<Collaboration>`.

- [ ] **Step 2: frontend-developer-base.md 작성**

방어적 데이터 접근, 3가지 상태(로딩/에러/빈), 폼 패턴 포함.

- [ ] **Step 3: system-architect-base.md 작성**

기술 스택 선정, 디렉토리 구조, 데이터 모델 설계 프로세스 포함.

- [ ] **Step 4: content-writer-base.md 작성**

팩트체크, 출처 명시, 논리 흐름 검증 프로세스 포함. document/creative 도메인용.

- [ ] **Step 5: data-analyst-base.md 작성**

소스 신뢰도 평가, 데이터 최신성 검증, 시각화 선택 기준 포함. research 도메인용.

- [ ] **Step 6: Phase 3 골든 템플릿 매칭 우선순위 업데이트**

phases/phase-3-agents.md의 골든 템플릿 매칭 섹션에:
```
1순위: OMC/ECC 에이전트 (기존)
2순위: library/base-agents/{role}-base.md (신규)
3순위: templates/agent-skeleton.md (폴백)
```

- [ ] **Step 5: validate_ax.py 실행하여 base-agent frontmatter 검증**

```bash
python3 tests/ax/tools/validate_ax.py
```

Expected: base_agents 체크 PASS.

- [ ] **Step 6: 커밋**

```bash
git add .claude/skills/ax/library/base-agents/ .claude/skills/ax/phases/phase-3-agents.md
git commit -m "feat(ax): base-agent 3개 추가 (backend/frontend/system-architect) + 매칭 우선순위"
```

---

## Task 16: 최종 검증 + CLAUDE.md 업데이트

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: make test-all 실행**

```bash
make test-all
```

Expected: Tier 2 (validate_ax) PASS, Tier 3 (시나리오) 가용한 만큼 PASS.

- [ ] **Step 2: CLAUDE.md 업데이트**

버전 정보, 새 기능(execution-policy, 3-Layer 검증, phases/ 구조) 반영.

- [ ] **Step 3: 최종 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md v0.4 업데이트 — 무개입 아키텍처, 3-Layer 검증, Hub-and-Spoke 분해"
```
