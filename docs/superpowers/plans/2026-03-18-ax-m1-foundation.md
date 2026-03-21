# ax M1: 기반 정비 — 리네이밍, 중복 제거, 경로 통일

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `harness1`을 `ax`로 완전 리네이밍하고, 커맨드-스킬 중복을 제거하고, 모든 경로 참조를 통일하여 깨끗한 코드베이스를 확보한다.

**Architecture:** Claude Code 스킬(순수 마크다운) 구조를 유지. 커맨드 파일은 스킬 호출 래퍼로 축소. 내부 경로는 `${PROJECT_DIR}` 변수 기반으로 통일. `--here` 플래그로 기존 프로젝트 지원 추가.

**Tech Stack:** Claude Code Skill (SKILL.md), YAML frontmatter, 마크다운

**Spec:** `docs/superpowers/specs/2026-03-18-ax-v02-plan.md` M1 섹션

---

## 파일 구조 (변경 전 → 변경 후)

```
변경 전:
  .claude/commands/harness1.md              (407줄, SKILL.md와 중복)
  .claude/skills/harness1/SKILL.md          (418줄)
  .claude/skills/harness1/templates/*.md    (5개)
  tests/harness/*.md                        (3개)
  CLAUDE.md                                 (harness 참조)
  docs/DESIGN-BRIEF.md                      (harness 참조)
  .claude/settings.local.json               (하드코딩 경로)

변경 후:
  .claude/commands/ax.md                    (~10줄, 래퍼만)
  .claude/skills/ax/SKILL.md               (경로 수정, ax 참조)
  .claude/skills/ax/templates/*.md          (5개, ax 참조)
  tests/ax/*.md                             (3개)
  CLAUDE.md                                 (ax 참조)
  docs/DESIGN-BRIEF.md                      (ax 참조)
  .claude/settings.local.json               (정리)
  .gitignore                                (신규)

삭제:
  .claude/commands/harness1.md
  .claude/skills/harness1/                  (전체 디렉토리)
  tests/harness/                            (전체 디렉토리)
```

---

## Task 1: 스킬 디렉토리 이동 (harness1 → ax)

**Files:**
- Create: `.claude/skills/ax/SKILL.md`
- Create: `.claude/skills/ax/templates/agent-skeleton.md`
- Create: `.claude/skills/ax/templates/skill-skeleton.md`
- Create: `.claude/skills/ax/templates/pattern-selection.md`
- Create: `.claude/skills/ax/templates/orchestrator-section.md`
- Create: `.claude/skills/ax/templates/architecture-doc.md`
- Delete: `.claude/skills/harness1/` (전체)

- [ ] **Step 1: ax 디렉토리 생성 및 파일 복사**

```bash
mkdir -p .claude/skills/ax/templates
cp .claude/skills/harness1/SKILL.md .claude/skills/ax/SKILL.md
cp .claude/skills/harness1/templates/*.md .claude/skills/ax/templates/
```

- [ ] **Step 2: 파일 복사 확인**

Run: `ls .claude/skills/ax/templates/`
Expected: 5개 파일 (agent-skeleton.md, architecture-doc.md, orchestrator-section.md, pattern-selection.md, skill-skeleton.md)

- [ ] **Step 3: 이전 디렉토리 삭제**

```bash
rm -rf .claude/skills/harness1
```

- [ ] **Step 4: 삭제 확인**

Run: `ls .claude/skills/harness1/ 2>&1`
Expected: "No such file or directory"

---

## Task 2: SKILL.md 내부 참조 수정

**Files:**
- Modify: `.claude/skills/ax/SKILL.md`

아래의 모든 참조를 일괄 수정:

- [ ] **Step 1: frontmatter name 수정**

```
변경 전: name: harness1
변경 후: name: ax
```

- [ ] **Step 2: description 수정**

```
변경 전: 자동 생성하는 메타 도구. "/harness 도메인설명" 형태로 사용.
변경 후: 자동 생성하는 메타 도구. "/ax 도메인설명" 형태로 사용.
```

- [ ] **Step 3: argument-hint 수정**

```
변경 전: argument-hint: '"도메인 설명" 또는 --interview "도메인 설명"'
변경 후: argument-hint: '"도메인 설명" 또는 --here "도메인 설명" 또는 --interview "도메인 설명"'
```

- [ ] **Step 4: 사용법 섹션 수정**

```
변경 전:
- `/harness "이커머스 플랫폼 - 상품 관리, 주문 처리"` — 완전 자동
- `/harness --interview "데이터 분석"` — 인터뷰 모드 (v1.0)

변경 후:
- `/ax "이커머스 플랫폼 - 상품 관리, 주문 처리"` — 완전 자동 (projects/ 하위 생성)
- `/ax --here "이커머스 플랫폼"` — 현재 디렉토리에 에이전트 생성
- `/ax --interview "데이터 분석"` — 인터뷰 모드 (v1.0)
```

- [ ] **Step 5: 중간 아티팩트 경로 수정 (.omc/harness → .omc/ax)**

`replace_all`로 일괄 수정:
```
.omc/harness/ → .omc/ax/
```

- [ ] **Step 6: 템플릿 경로 수정**

`replace_all`로 일괄 수정:
```
.claude/skills/harness/templates/ → .claude/skills/ax/templates/
templates/pattern-selection.md → .claude/skills/ax/templates/pattern-selection.md
templates/agent-skeleton.md → .claude/skills/ax/templates/agent-skeleton.md
templates/skill-skeleton.md → .claude/skills/ax/templates/skill-skeleton.md
templates/orchestrator-section.md → .claude/skills/ax/templates/orchestrator-section.md
templates/architecture-doc.md → .claude/skills/ax/templates/architecture-doc.md
```

- [ ] **Step 7: tests 경로 수정**

```
tests/harness/ → tests/ax/
```

- [ ] **Step 8: mkdir 명령 수정**

```
변경 전: mkdir -p ${PROJECT_DIR}/.omc/harness
변경 후: mkdir -p ${PROJECT_DIR}/.omc/ax
```

```
변경 전: mkdir -p ${PROJECT_DIR}/tests/harness
변경 후: mkdir -p ${PROJECT_DIR}/tests/ax
```

- [ ] **Step 9: origin 필드 수정**

```
변경 전: origin=harness
변경 후: origin=ax
```

- [ ] **Step 10: 완료 보고 수정**

```
변경 전: /harness를 다시 실행하세요
변경 후: /ax를 다시 실행하세요
```

- [ ] **Step 11: harness 자체 스킬 제외 주석 수정**

```
변경 전: (harness 자체 스킬 제외)
변경 후: (ax 자체 스킬 제외)
```

- [ ] **Step 12: 수정 후 잔여 harness 참조 확인**

Run: `grep -n "harness" .claude/skills/ax/SKILL.md`
Expected: 0줄 (harness 참조 완전 제거)

---

## Task 3: --here 플래그 지원 추가

**Files:**
- Modify: `.claude/skills/ax/SKILL.md`

- [ ] **Step 1: 입력 파싱 섹션에 --here 처리 추가**

기존 "입력 파싱" 섹션을 교체:

```markdown
### 입력 파싱

사용자 입력을 파싱합니다:
- `--here` 플래그 존재 여부 확인 → 현재 디렉토리에 에이전트 생성
- `--interview` 플래그 존재 여부 확인 (v1.0 예정, 현재는 무시하고 진행)
- 나머지 텍스트를 도메인 설명으로 사용
```

- [ ] **Step 2: 프로젝트 디렉토리 결정 로직 수정**

기존 "1.0 프로젝트 디렉토리 생성" 섹션을 교체:

```markdown
### 1.0 프로젝트 디렉토리 결정

`--here` 플래그에 따라 프로젝트 디렉토리를 결정합니다:

**`--here` 있을 때:**
- `PROJECT_DIR=.` (현재 디렉토리)
- 기존 `.claude/` 디렉토리가 있으면 그대로 사용
- 기존 에이전트/스킬과 충돌 시 Phase 3에서 처리

**`--here` 없을 때 (기본):**
1. 도메인 설명의 핵심 키워드를 kebab-case로 변환 (예: "이커머스 플랫폼" → `ecommerce-platform`)
2. `projects/{project-name}/` 디렉토리 생성
3. `PROJECT_DIR=projects/{project-name}`

이후 모든 Phase의 파일 생성은 `${PROJECT_DIR}/` 기준으로 수행.
```

- [ ] **Step 3: 수정 확인**

Run: `grep -c "\-\-here" .claude/skills/ax/SKILL.md`
Expected: 3 이상

---

## Task 4: 템플릿 파일 참조 수정

**Files:**
- Modify: `.claude/skills/ax/templates/orchestrator-section.md`
- Modify: `.claude/skills/ax/templates/architecture-doc.md`
- Modify: `.claude/skills/ax/templates/skill-skeleton.md`

- [ ] **Step 1: orchestrator-section.md 수정**

```
변경 전: > 이 섹션은 `/harness`에 의해 자동 생성되었습니다.
변경 후: > 이 섹션은 `/ax`에 의해 자동 생성되었습니다.
```

- [ ] **Step 2: architecture-doc.md 수정**

```
변경 전: > 이 문서는 `/harness`에 의해 자동 생성되었습니다.
변경 후: > 이 문서는 `/ax`에 의해 자동 생성되었습니다.
```

- [ ] **Step 3: skill-skeleton.md 수정**

```
변경 전: origin: harness
변경 후: origin: ax
```

- [ ] **Step 4: 모든 템플릿에서 잔여 harness 확인**

Run: `grep -rn "harness" .claude/skills/ax/templates/`
Expected: 0줄

---

## Task 5: 커맨드 파일 교체 (중복 제거)

**Files:**
- Create: `.claude/commands/ax.md`
- Delete: `.claude/commands/harness1.md`

- [ ] **Step 1: 새 커맨드 파일 생성 (래퍼)**

`.claude/commands/ax.md`:

```markdown
# ax — Agent Team Architect

도메인 설명을 분석하여 최적의 에이전트 팀을 자동 생성합니다.

**도메인 입력:** $ARGUMENTS

## 실행 파이프라인

> 이 스킬은 아래 Phase를 순차 실행합니다.
> 생성된 프로젝트는 `projects/{project-name}/` 하위에 생성됩니다 (`--here` 시 현재 디렉토리).
> 중간 아티팩트는 `${PROJECT_DIR}/.omc/ax/`에 저장됩니다.
> 템플릿 파일 경로: `.claude/skills/ax/templates/`
```

이 커맨드는 SKILL.md의 Phase 1-6 전체를 참조합니다. SKILL.md를 Read하여 지시를 따르세요:

```
Read: .claude/skills/ax/SKILL.md
```

ARGUMENTS: $ARGUMENTS

- [ ] **Step 2: 이전 커맨드 파일 삭제**

```bash
rm .claude/commands/harness1.md
```

- [ ] **Step 3: 확인**

Run: `ls .claude/commands/`
Expected: `ax.md`만 존재

Run: `wc -l .claude/commands/ax.md`
Expected: ~20줄 (407줄에서 대폭 축소)

---

## Task 6: 테스트 시나리오 이동

**Files:**
- Create: `tests/ax/scenario-ecommerce.md`
- Create: `tests/ax/scenario-research.md`
- Create: `tests/ax/scenario-saas.md`
- Delete: `tests/harness/` (전체)

- [ ] **Step 1: 디렉토리 생성 및 파일 이동**

```bash
mkdir -p tests/ax
cp tests/harness/*.md tests/ax/
rm -rf tests/harness
```

- [ ] **Step 2: 시나리오 파일 내부 참조 수정**

각 파일에서:
```
/harness → /ax
```

- [ ] **Step 3: 확인**

Run: `ls tests/ax/`
Expected: 3개 파일

Run: `grep -rn "harness" tests/ax/`
Expected: 0줄

---

## Task 7: CLAUDE.md 갱신

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 프로젝트 헤더 교체**

```markdown
변경 전:
# Harness — Agent Team & Skill Architect
도메인 설명을 입력하면 Claude Code용 에이전트 팀(agents, skills, orchestrator)을 자동 생성하는 메타 도구.

변경 후:
# ax — Agent Team Architect
도메인 설명을 입력하면 최적의 에이전트 팀(agents, skills, orchestrator)을 자동 생성하는 메타 도구.
시각화 품질을 핵심 차별점으로, 멀티 LLM(Claude + OpenAI + Gemini)을 활용한다.
```

- [ ] **Step 2: 스킬 참조 수정**

```
/harness → /ax
harness/*.md → ax/*.md
```

- [ ] **Step 3: 확인**

Run: `grep -n "harness" CLAUDE.md`
Expected: 0줄

---

## Task 8: .gitignore 및 설정 정리

**Files:**
- Create: `.gitignore`
- Modify: `.claude/settings.local.json`

- [ ] **Step 1: .gitignore 생성**

```
projects/
.omc/
*.output
```

- [ ] **Step 2: settings.local.json 정리**

하드코딩된 프로젝트 경로를 제거하고 범용 패턴으로 교체:

```json
{
  "permissions": {
    "allow": [
      "Bash(mkdir -p *)",
      "Bash(ls *)",
      "Bash(find *)",
      "Bash(cp *)",
      "Bash(rm -rf projects/*)",
      "Bash(rm -rf tests/ax/*)",
      "Bash(python3 *)",
      "mcp__exa__web_search_exa"
    ]
  }
}
```

- [ ] **Step 3: 확인**

Run: `grep -c "harness" .claude/settings.local.json`
Expected: 0

---

## Task 9: 설계 문서 갱신

**Files:**
- Modify: `docs/DESIGN-BRIEF.md`

- [ ] **Step 1: DESIGN-BRIEF.md 수정**

모든 `harness` → `ax`, `/harness` → `/ax` 교체.

- [ ] **Step 2: 확인**

Run: `grep -rn "harness" docs/DESIGN-BRIEF.md`
Expected: 0줄

---

## Task 10: 최종 검증

- [ ] **Step 1: 전체 프로젝트에서 잔여 harness 참조 검색**

```bash
grep -rn "harness" --include="*.md" --include="*.json" . | grep -v "projects/" | grep -v ".omc/" | grep -v "node_modules/"
```

Expected: `docs/superpowers/` 내 히스토리 문서(specs, plans)만 남음 — 이것은 의도적 보존 (설계 히스토리)

- [ ] **Step 2: 파일 구조 최종 확인**

```bash
find . -type f -not -path "./projects/*" -not -path "./.omc/*" -not -path "./node_modules/*" | sort
```

Expected:
```
./.claude/commands/ax.md
./.claude/settings.local.json
./.claude/skills/ax/SKILL.md
./.claude/skills/ax/templates/agent-skeleton.md
./.claude/skills/ax/templates/architecture-doc.md
./.claude/skills/ax/templates/orchestrator-section.md
./.claude/skills/ax/templates/pattern-selection.md
./.claude/skills/ax/templates/skill-skeleton.md
./.gitignore
./CLAUDE.md
./docs/DESIGN-BRIEF.md
./docs/superpowers/plans/2026-03-18-ax-m1-foundation.md
./docs/superpowers/plans/2026-03-18-harness-v01-mvp.md
./docs/superpowers/specs/2026-03-18-ax-v02-plan.md
./docs/superpowers/specs/2026-03-18-harness-design.md
./tests/ax/scenario-ecommerce.md
./tests/ax/scenario-research.md
./tests/ax/scenario-saas.md
```

- [ ] **Step 3: SKILL.md 경로 참조 테스트**

```bash
# SKILL.md가 참조하는 모든 템플릿 경로가 실제 존재하는지 확인
grep "\.claude/skills/ax/templates/" .claude/skills/ax/SKILL.md | while read line; do
  path=$(echo "$line" | grep -oE '\.claude/skills/ax/templates/[a-z-]+\.md')
  if [ -n "$path" ] && [ ! -f "$path" ]; then
    echo "MISSING: $path"
  fi
done
```

Expected: 출력 없음 (모든 경로 유효)
