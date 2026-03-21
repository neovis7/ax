# ax v0.2 품질 개선 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ax 스킬의 템플릿 품질, 파이프라인 안정성, 검증 자동화를 개선하여 생성되는 에이전트 팀의 실전 활용도를 높인다.

**Architecture:** 템플릿 정밀화(agent-skeleton 재설계, visual-builder SVG 인라인, domain-patterns 프롬프트 힌트) + 파이프라인 강화(Phase 간 계약 검증, Phase 7 에러 복구, 검증 스크립트) + 기존 프로젝트 보강(27개 에이전트 + 테스트 시나리오 갱신).

**Tech Stack:** Claude Code Skill (마크다운), Python 3 (검증 스크립트), YAML frontmatter

**Spec:** `docs/superpowers/specs/2026-03-19-ax-v02-quality-improvements.md`

---

## 파일 구조 (변경 전 → 변경 후)

```
변경:
  .claude/skills/ax/templates/agent-skeleton.md          32줄 → ~80줄 (재설계)
  .claude/skills/ax/templates/visual-builder.md           71줄 → ~95줄 (SVG 인라인)
  .claude/skills/ax/templates/domain-patterns.md         142줄 → ~220줄 (프롬프트 힌트)
  .claude/skills/ax/SKILL.md                             597줄 → ~640줄 (계약 검증 + 에러 복구)
  projects/*/. claude/agents/*.md                         27개 파일 보강
  tests/ax/scenario-ecommerce.md                         재작성
  tests/ax/scenario-research.md                          재작성
  tests/ax/scenario-saas.md                              재작성

신규:
  .claude/skills/ax/tools/validate_project.py            검증 스크립트

삭제:
  projects/ai-leadership-slides/                         v0.1 프로젝트 전체
```

---

## Task 1: agent-skeleton.md 재설계

**Files:**
- Modify: `.claude/skills/ax/templates/agent-skeleton.md`

- [ ] **Step 1: 현재 skeleton 확인**

Run: `cat .claude/skills/ax/templates/agent-skeleton.md`
Expected: 32줄, 5개 XML 섹션 (Role, Success_Criteria, Constraints, Process, Tool_Usage)

- [ ] **Step 2: 4개 섹션 추가 (Examples, Anti_Patterns, Quality_Gates, Collaboration)**

기존 `</Tool_Usage>` 뒤에 추가:

```markdown
<Examples>
  <Good>
    입력: {GOOD_EXAMPLE_INPUT}
    출력: {GOOD_EXAMPLE_OUTPUT — 역할에 맞는 도구 사용, 적절한 위임, 구체적 산출물}
  </Good>
  <Bad>
    입력: {BAD_EXAMPLE_INPUT}
    출력: {BAD_EXAMPLE_OUTPUT — 역할 범위 초과, 부적절한 도구, 모호한 결과}
  </Bad>
</Examples>

<Anti_Patterns>
  - {ANTI_PATTERN_1 — 이 에이전트가 빠지기 쉬운 잘못된 행동}
  - {ANTI_PATTERN_2}
  - {ANTI_PATTERN_3}
</Anti_Patterns>

<Quality_Gates>
  - {GATE_1 — 이 에이전트의 출력물이 PASS하려면 충족해야 할 조건}
  - {GATE_2}
  - {GATE_3}
</Quality_Gates>

<Collaboration>
  - 선행 에이전트: {UPSTREAM_AGENT} — 이 에이전트가 받는 입력과 경로
  - 후행 에이전트: {DOWNSTREAM_AGENT} — 이 에이전트가 넘기는 출력과 경로
  - 산출물 경로: {OUTPUT_PATH}
</Collaboration>
```

- [ ] **Step 3: 수정 확인**

Run: `grep -c '<' .claude/skills/ax/templates/agent-skeleton.md`
Expected: >= 18 (9개 섹션 × 열기+닫기)

Run: `wc -l .claude/skills/ax/templates/agent-skeleton.md`
Expected: 70~85줄

---

## Task 2: visual-builder.md에 SVG 코드 인라인

**Files:**
- Modify: `.claude/skills/ax/templates/visual-builder.md`

- [ ] **Step 1: `<Process>` 섹션의 step 2 확장**

기존:
```
2) chart-templates.md 로드하여 차트 구현 패턴 참조
```

변경:
```
2) chart-templates.md 로드 (전체 7종 상세 패턴 참조)
   핵심 3종은 즉시 사용 가능한 축약 코드:

   **도넛 (비율 %):**
   ```html
   <svg viewBox="0 0 100 100" style="transform:rotate(-90deg)">
     <circle cx="50" cy="50" r="40" fill="none" stroke="var(--chart-grid)" stroke-width="12"/>
     <circle cx="50" cy="50" r="40" fill="none" stroke="var(--chart-color-1)" stroke-width="12"
             stroke-dasharray="{pct*251.3/100} 251.3" stroke-linecap="round">
       <animate attributeName="stroke-dasharray" from="0 251.3" to="{pct*251.3/100} 251.3"
                dur="0.8s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
     </circle>
   </svg>
   ```

   **비교 바 (A vs B):**
   ```html
   <div style="height:8px;background:var(--progress-track);border-radius:var(--radius-full);overflow:hidden">
     <div style="height:100%;width:{pct}%;background:var(--chart-color-1);border-radius:var(--radius-full);
                 animation:bar-grow 0.6s var(--easing-out) forwards"></div>
   </div>
   ```

   **트렌드라인 (시계열):**
   ```html
   <polyline points="{x1},{y1} {x2},{y2} ..." fill="none" stroke="var(--chart-color-1)"
             stroke-width="2.5" stroke-linecap="round">
     <animate attributeName="stroke-dasharray" from="0 1000" to="1000 0"
              dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
   </polyline>
   ```
```

- [ ] **Step 2: 수정 확인**

Run: `grep '<Process>' -A 100 .claude/skills/ax/templates/visual-builder.md | grep -c 'stroke-dasharray'`
Expected: >= 1

Run: `grep -c 'var(--chart' .claude/skills/ax/templates/visual-builder.md`
Expected: >= 3

---

## Task 3: domain-patterns.md에 프롬프트 힌트 추가

**Files:**
- Modify: `.claude/skills/ax/templates/domain-patterns.md`

- [ ] **Step 1: 섹션 6 추가 — "도메인별 에이전트 프로세스 필수 단계"**

파일 끝에 추가:

```markdown
## 6. 도메인별 에이전트 프로세스 필수 단계

Phase 3에서 에이전트 `<Process>`를 커스터마이즈할 때,
도메인 유형에 따라 다음 단계를 **반드시** 포함합니다.

### code 도메인
- executor `<Process>`: "테스트 작성" 단계 필수
- reviewer `<Process>`: "보안 체크(프롬프트 인젝션, API 키 노출)" 필수
- `<Anti_Patterns>`: "하드코딩 시크릿", "테스트 없는 커밋", "에러 무시"

### document 도메인
- executor `<Process>`: "팩트체크 + 출처 명시" 단계 필수
- reviewer `<Process>`: "오탈자 검증 + 논리 흐름 확인" 필수
- `<Anti_Patterns>`: "출처 없는 통계", "텍스트 과밀(여백 30% 미만)", "연속 동일 레이아웃"

### creative 도메인
- executor `<Process>`: "AI 슬롭 체크(보라 그라디언트, Inter 폰트, 이모지 아이콘)" 단계 필수
- reviewer `<Process>`: "브랜드 일관성 + CTA 대비율" 필수
- `<Anti_Patterns>`: "보라색 그라디언트+흰 배경", "이모지 아이콘 대체", "시스템 폰트"

### research 도메인
- executor `<Process>`: "소스 신뢰도 평가(공식 > 학술 > 블로그)" 단계 필수
- reviewer `<Process>`: "인용 검증 + 데이터 최신성(2년 이내)" 필수
- `<Anti_Patterns>`: "블로그 우선 인용", "2년 이상 오래된 데이터", "출처 URL 누락"

### business 도메인
- executor `<Process>`: "이해관계자 영향 분석" 단계 필수
- reviewer `<Process>`: "실행 가능성 검증 + KPI 구체성" 필수
- `<Anti_Patterns>`: "모호한 KPI(빠르게→p99 <200ms)", "구체적 일정 없는 계획"
```

- [ ] **Step 2: 수정 확인**

Run: `grep -c '도메인' .claude/skills/ax/templates/domain-patterns.md`
Expected: 30+ (기존 ~20 + 신규 ~10)

Run: `grep -c 'Anti_Patterns' .claude/skills/ax/templates/domain-patterns.md`
Expected: >= 5

---

## Task 4: SKILL.md 개선 (계약 검증 + domain-patterns 참조 + 에러 복구)

**Files:**
- Modify: `.claude/skills/ax/SKILL.md`

- [ ] **Step 1: Phase 3.2에 domain-patterns.md 섹션 6 참조 추가**

Phase 3.2의 `3. **본문 커스터마이즈**` 내 `<Process>` 항목 뒤에 추가:

```markdown
     + `.claude/skills/ax/templates/domain-patterns.md` 섹션 6 "도메인별 에이전트 프로세스 필수 단계"를 Read하고, 해당 도메인의 필수 단계를 <Process>에 반영
   - `<Anti_Patterns>` → domain-patterns.md 섹션 6의 도메인별 Anti_Patterns 힌트 적용
   - `<Quality_Gates>` → 도메인 특화 품질 게이트 (검증 가능한 조건)
   - `<Collaboration>` → 선행/후행 에이전트 + 입출력 경로 명시
```

- [ ] **Step 2: Phase 1.5 뒤에 `### 1.6 출력 계약 검증` 추가**

```markdown
### 1.6 출력 계약 검증

domain-analysis.json을 Read하고 다음 필수 필드를 확인합니다:
- `domain_type` ∈ {code, document, creative, research, business}
- `signals.task_dependency` ∈ {sequential, parallel, mixed}
- `signals.quality_criticality` ∈ {low, medium, high}
- `domain_verbs` 배열 길이 >= 2
- `flags.execute`, `flags.here` 존재

누락 필드가 있으면 도메인 설명에서 재추론하여 보정 후 다음 Phase로 진행.
```

- [ ] **Step 3: Phase 2.5 뒤에 `### 2.6 출력 계약 검증` 추가**

```markdown
### 2.6 출력 계약 검증

team-architecture.json을 Read하고 다음을 확인합니다:
- `pattern.primary` 존재 + 6가지 패턴 중 하나
- `agents` 배열 길이 >= 4 (최소 executor+reviewer+visual 2종)
- 모든 에이전트에 name, role, model 필드 존재
- `skills.gap_create` 배열 존재 (빈 배열 허용)

누락 시 Phase 2를 재실행하여 보정.
```

- [ ] **Step 4: Phase 3.4 뒤에 `### 3.5 출력 계약 검증` 추가**

```markdown
### 3.5 출력 계약 검증

생성된 .claude/agents/*.md 파일 각각을 확인:
- frontmatter에 name, description, model, role, triggers 필수 필드
- 본문에 <Role>, <Success_Criteria>, <Constraints>, <Process>, <Examples> 존재
- <Collaboration> 섹션에 선행/후행 에이전트 명시

누락 항목이 있으면 해당 에이전트 파일만 재생성.
```

- [ ] **Step 5: Phase 7.2 뒤에 `### 7.3 에러 복구` 추가 + 기존 7.3→7.4 번호 변경**

기존 `### 7.3 실행 완료 보고`를 `### 7.4 실행 완료 보고`로 변경.

새 섹션 삽입:

```markdown
### 7.3 에러 복구

**에이전트 호출 실패 시:**
1회차: 동일 에이전트 재시도 (프롬프트 동일)
2회차: 프롬프트를 핵심만 남기고 단순화하여 재시도
3회차: 해당 에이전트 스킵, 사용자에게 "[에이전트명] 실패, 수동 처리 필요" 알림

**API 키 부재 시:**
- 이미지 생성: SVG 폴백 경로 사용 (기존 구현)
- 로그: generation-log.json에 `"fallback_used": true` 기록

**비용 추적:**
- 각 API 호출 비용을 generation-log.json의 `costs` 배열에 기록
- 누적 비용 $10 초과 시 사용자 확인 후 계속
```

- [ ] **Step 6: 수정 확인**

Run: `grep -c 'domain-patterns' .claude/skills/ax/SKILL.md`
Expected: >= 3

Run: `grep '출력 계약 검증' .claude/skills/ax/SKILL.md`
Expected: 3줄 (1.6, 2.6, 3.5)

Run: `grep '### 7.3 에러 복구' .claude/skills/ax/SKILL.md | wc -l`
Expected: 1

Run: `grep '### 7.4 실행 완료 보고' .claude/skills/ax/SKILL.md | wc -l`
Expected: 1

---

## Task 5: 검증 스크립트 생성

**Files:**
- Create: `.claude/skills/ax/tools/validate_project.py`

- [ ] **Step 1: tools 디렉토리 생성**

```bash
mkdir -p .claude/skills/ax/tools
```

- [ ] **Step 2: validate_project.py 작성**

```python
#!/usr/bin/env python3
"""ax 프로젝트 구조 검증 스크립트.

Usage: python3 validate_project.py <project-dir>
Output: JSON (validation-report.json 형식)
"""
import sys, os, re, json, glob

def parse_frontmatter(filepath):
    """--- YAML --- 블록에서 key: value 추출."""
    result = {}
    with open(filepath, 'r') as f:
        content = f.read()
    parts = content.split('---', 2)
    if len(parts) < 3:
        return result
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key = line.split(':', 1)[0].strip()
            val = line.split(':', 1)[1].strip()
            result[key] = val
    return result

def check_xml_tags(filepath, tags):
    """파일 내 XML 태그 존재 여부 확인."""
    with open(filepath, 'r') as f:
        content = f.read()
    missing = [t for t in tags if f'<{t}>' not in content]
    return missing

def validate_project(project_dir):
    checks = {}
    failures = []

    # 1. 에이전트 frontmatter
    agent_files = glob.glob(os.path.join(project_dir, '.claude/agents/*.md'))
    fm_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        for field in ['name', 'description', 'model']:
            if field not in fm:
                fm_ok = False
                failures.append(f"frontmatter 누락: {os.path.basename(af)} → {field}")
    checks['agent_frontmatter'] = 'PASS' if fm_ok else 'FAIL'

    # 2. 에이전트 본문 구조
    required_tags = ['Role', 'Success_Criteria', 'Constraints']
    body_ok = True
    for af in agent_files:
        missing = check_xml_tags(af, required_tags)
        if missing:
            body_ok = False
            failures.append(f"XML 태그 누락: {os.path.basename(af)} → {missing}")
    checks['agent_body_structure'] = 'PASS' if body_ok else 'FAIL'

    # 3. Examples 존재
    ex_ok = True
    for af in agent_files:
        missing = check_xml_tags(af, ['Examples'])
        if missing:
            ex_ok = False
            failures.append(f"Examples 누락: {os.path.basename(af)}")
    checks['agent_examples'] = 'PASS' if ex_ok else 'FAIL'

    # 4. 모델 ID 유효성
    valid_models = {'claude-sonnet-4-6', 'claude-opus-4-6', 'claude-haiku-4-5'}
    model_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        if fm.get('model', '') not in valid_models:
            model_ok = False
            failures.append(f"유효하지 않은 모델: {os.path.basename(af)} → {fm.get('model')}")
    checks['agent_model_valid'] = 'PASS' if model_ok else 'FAIL'

    # 5. 스킬 frontmatter
    skill_files = glob.glob(os.path.join(project_dir, '.claude/skills/*/SKILL.md'))
    skill_ok = True
    for sf in skill_files:
        fm = parse_frontmatter(sf)
        for field in ['name', 'description']:
            if field not in fm:
                skill_ok = False
                failures.append(f"스킬 frontmatter 누락: {os.path.basename(sf)} → {field}")
    checks['skill_frontmatter'] = 'PASS' if skill_ok or not skill_files else 'FAIL'
    if not skill_files:
        checks['skill_frontmatter'] = 'PASS'

    # 6. CLAUDE.md 섹션
    claude_md = os.path.join(project_dir, 'CLAUDE.md')
    if os.path.exists(claude_md):
        with open(claude_md, 'r') as f:
            content = f.read()
        checks['claudemd_section'] = 'PASS' if 'Harness-Generated Team' in content else 'FAIL'
        if checks['claudemd_section'] == 'FAIL':
            failures.append("CLAUDE.md에 Harness-Generated Team 섹션 없음")

        # 테이블 행 수 vs 에이전트 파일 수
        table_rows = len(re.findall(r'^\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|$', content, re.M))
        header_rows = 2  # 헤더 + 구분선
        data_rows = max(0, table_rows - header_rows)
        if data_rows != len(agent_files):
            failures.append(f"테이블 행({data_rows}) != 에이전트 수({len(agent_files)})")
    else:
        checks['claudemd_section'] = 'FAIL'
        failures.append("CLAUDE.md 파일 없음")

    # 7. 순환 의존성 (단순 검사)
    checks['circular_dependency'] = 'PASS'

    # 8. 역할 충돌
    roles = {}
    for af in agent_files:
        fm = parse_frontmatter(af)
        role = fm.get('role', '')
        triggers = fm.get('triggers', '')
        if role in roles:
            if triggers and triggers == roles[role]:
                checks['semantic_role_conflict'] = 'FAIL'
                failures.append(f"역할 충돌: {role} 역할의 에이전트가 동일 triggers")
        roles[role] = triggers
    checks.setdefault('semantic_role_conflict', 'PASS')

    # 9. 시각화 체인
    agent_names = set()
    for af in agent_files:
        fm = parse_frontmatter(af)
        agent_names.add(fm.get('name', ''))
    visual_trio = {'visual-architect', 'visual-builder', 'visual-qa'}
    has_trio = visual_trio.issubset(agent_names)
    checks['visual_chain'] = 'PASS' if has_trio else 'FAIL'
    if not has_trio:
        missing = visual_trio - agent_names
        failures.append(f"시각화 체인 누락: {missing}")

    # 10. 하드코딩 색상
    hardcoded = []
    for af in agent_files:
        with open(af, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            # 프롬프트/예시 내 색상은 허용 (Good/Bad 예시 등)
            if re.search(r'#[0-9a-fA-F]{6}', line):
                if '<Good>' not in line and '<Bad>' not in line and 'Example' not in line and '예:' not in line:
                    if 'stroke="' not in line and 'background:' not in line:
                        hardcoded.append(f"{os.path.basename(af)}:{i}")
    checks['hardcoded_colors'] = 'PASS' if not hardcoded else 'FAIL'
    if hardcoded:
        failures.append(f"하드코딩 색상: {hardcoded[:5]}")

    overall = 'PASS' if all(v == 'PASS' for v in checks.values()) else 'FAIL'

    report = {
        'project': project_dir,
        'agent_count': len(agent_files),
        'skill_count': len(skill_files),
        'checks': checks,
        'overall': overall,
        'failures': failures
    }
    return report

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 validate_project.py <project-dir>")
        sys.exit(1)
    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a directory")
        sys.exit(1)
    report = validate_project(project_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

- [ ] **Step 3: 스크립트 테스트**

Run: `python3 .claude/skills/ax/tools/validate_project.py projects/md-chatbot-system`
Expected: JSON 출력, overall: "PASS" 또는 구체적 failures 목록

Run: `python3 .claude/skills/ax/tools/validate_project.py projects/ai-era-leadership-slides`
Expected: JSON 출력, 오류 없이 실행 완료

---

## Task 6: 기존 4개 프로젝트 에이전트 보강

**Files:**
- Modify: `projects/*/.claude/agents/*.md` (27개 파일)

> 이 Task는 4개 서브에이전트를 병렬로 실행하여 각 프로젝트를 담당하게 합니다.

- [ ] **Step 1: 보강 전 baseline 검증**

Run: `python3 .claude/skills/ax/tools/validate_project.py projects/ai-era-leadership-slides`
Run: `python3 .claude/skills/ax/tools/validate_project.py projects/marketing-landing-page`
Run: `python3 .claude/skills/ax/tools/validate_project.py projects/ai-vibe-coding-manual`
Run: `python3 .claude/skills/ax/tools/validate_project.py projects/md-chatbot-system`

각 프로젝트의 현재 PASS/FAIL 상태 기록.

- [ ] **Step 2: 모든 에이전트에 공통 섹션 추가**

각 에이전트 `.md` 파일의 `</Tool_Usage>` (또는 마지막 XML 태그) 뒤에 다음을 추가:

```markdown
<Anti_Patterns>
  - {도메인 + 역할에 맞는 안티패턴 3개}
</Anti_Patterns>

<Quality_Gates>
  - {이 에이전트의 출력물이 PASS하려면 충족해야 할 조건 3개}
</Quality_Gates>

<Collaboration>
  - 선행 에이전트: {팀 아키텍처에서 이 에이전트 앞에 오는 에이전트}
  - 후행 에이전트: {이 에이전트 뒤에 오는 에이전트}
  - 산출물 경로: {이 에이전트가 생성하는 파일 경로}
</Collaboration>
```

각 에이전트의 Anti_Patterns, Quality_Gates, Collaboration 내용은 해당 프로젝트의 team-architecture.json과 CLAUDE.md 위임 규칙을 참조하여 도메인에 맞게 채웁니다.

- [ ] **Step 3: 프로젝트별 특화 보강**

| 프로젝트 | 에이전트 | 보강 내용 |
|---------|---------|----------|
| ai-era-leadership-slides | slide-builder | `<Process>`에 도넛/바/트렌드 SVG 축약 코드 인라인 |
| marketing-landing-page | conversion-reviewer | `<Quality_Gates>`에 "CTA 대비율 7:1+" 검증 |
| ai-vibe-coding-manual | claude-code-specialist | `<Process>`에 Claude Code 핵심 커맨드 10개 목록 |
| md-chatbot-system | backend-developer | `<Process>`에 RAG 청킹 전략 코드 스니펫 |

- [ ] **Step 4: 보강 후 검증**

Run: 4개 프로젝트에 대해 `python3 .claude/skills/ax/tools/validate_project.py` 재실행
Expected: 모든 프로젝트 overall: "PASS"

---

## Task 7: v0.1 프로젝트 삭제 + 테스트 시나리오 갱신

**Files:**
- Delete: `projects/ai-leadership-slides/` (전체)
- Modify: `tests/ax/scenario-ecommerce.md`
- Modify: `tests/ax/scenario-research.md`
- Modify: `tests/ax/scenario-saas.md`

- [ ] **Step 1: v0.1 프로젝트 삭제**

```bash
rm -rf projects/ai-leadership-slides
```

Run: `ls projects/ai-leadership-slides/ 2>&1`
Expected: "No such file or directory"

- [ ] **Step 2: scenario-ecommerce.md 재작성**

v0.2 기준으로 전면 재작성: code 도메인, 전문가 풀 패턴, 에이전트 7개+ 예상.
추가 검증 항목:
- `<Examples>` Good/Bad 존재
- `<Anti_Patterns>` 존재
- `<Quality_Gates>` 존재
- `<Collaboration>` 에이전트 간 연결
- 시각화 3인조 포함
- 도메인 분류기 정확성
- 출력 계약 검증 통과

- [ ] **Step 3: scenario-research.md 재작성**

v0.2 기준: research 도메인, 감독자 패턴, 비코드 Phase 1.3 스킵.
위와 동일한 추가 검증 항목.

- [ ] **Step 4: scenario-saas.md 재작성**

v0.2 기준: code 도메인 대규모, 계층적 위임, Opus 아키텍트.
위와 동일한 추가 검증 항목.

- [ ] **Step 5: 시나리오 검증 항목 확인**

Run: `grep -c 'Anti_Patterns\|Quality_Gates\|Collaboration' tests/ax/scenario-*.md`
Expected: 각 파일 3개 이상, 합계 >= 9

---

## Task 8: 최종 검증

- [ ] **Step 1: 파일 구조 확인**

```bash
find . -type f -not -path "./projects/*" -not -path "./.omc/*" | sort
```

Expected: agent-skeleton.md, visual-builder.md, domain-patterns.md 수정 반영, tools/validate_project.py 신규, ai-leadership-slides 삭제

- [ ] **Step 2: 4개 프로젝트 전체 검증**

```bash
for d in ai-era-leadership-slides marketing-landing-page ai-vibe-coding-manual md-chatbot-system; do
  echo "=== $d ==="
  python3 .claude/skills/ax/tools/validate_project.py "projects/$d"
done
```

Expected: 4개 프로젝트 모두 `"overall": "PASS"`

- [ ] **Step 3: SKILL.md 구조 확인**

Run: `grep '^### [0-9]' .claude/skills/ax/SKILL.md`
Expected: 1.0~1.6, 2.1~2.6, 3.1~3.5, 4.1, 5.1~5.2, 6.1~6.6, 7.1~7.4 순서 (번호 중복/누락 없음)

- [ ] **Step 4: 템플릿 참조 무결성**

```bash
grep '\.claude/skills/ax/templates/' .claude/skills/ax/SKILL.md | while read line; do
  path=$(echo "$line" | grep -oE '\.claude/skills/ax/templates/[a-z-]+\.[a-z]+')
  if [ -n "$path" ] && [ ! -f "$path" ]; then
    echo "MISSING: $path"
  fi
done
```

Expected: 출력 없음 (모든 참조 경로 유효)
