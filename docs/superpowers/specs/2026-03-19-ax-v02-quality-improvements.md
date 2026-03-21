# ax v0.2 품질 개선 — 설계 스펙

> 날짜: 2026-03-19
> 범위: ax 스킬 + 템플릿 + 기존 4개 생성 프로젝트 + 테스트 시나리오
> 방향: 품질 + 확장성 + 안정성 균형 개선
> 접근법: 통합 개선 (템플릿 정밀화 + 파이프라인 강화)

---

## 1. 배경

### 현재 상태

- ax v0.2: SKILL.md 597줄, 11개 템플릿, 8 Phase 파이프라인
- 생성 프로젝트 4개: 슬라이드, 랜딩 페이지, 매뉴얼, 챗봇
- 총 27개 에이전트 생성, 3가지 패턴 자동 선택 작동 확인

### 실전 검증에서 발견된 문제

| 영역 | 문제 | 근본 원인 |
|------|------|----------|
| 에이전트 품질 | 생성된 에이전트가 너무 일반적, 실전 역할 수행 부족 | agent-skeleton.md가 32줄로 빈약, 도메인 특화 힌트 부족 |
| 시각화 품질 | 결과물 디자인이 기대에 못 미침 | visual-builder가 chart-templates.md 참조를 빠뜨림, 코드 패턴 미인라인 |
| 파이프라인 안정성 | 실행 중 에이전트 간 연결 끊김, 에러 복구 없음 | Phase 간 계약 미정의, Phase 7 에러 복구 전략 없음 |

---

## 2. 변경 사항

### 2.1 agent-skeleton.md 재설계

**파일**: `.claude/skills/ax/templates/agent-skeleton.md`
**변경**: 32줄 → ~80줄

추가할 섹션:

```markdown
<Examples>
  <Good>
    입력: {GOOD_EXAMPLE_INPUT}
    출력: {GOOD_EXAMPLE_OUTPUT}
  </Good>
  <Bad>
    입력: {BAD_EXAMPLE_INPUT}
    출력: {BAD_EXAMPLE_OUTPUT}
  </Bad>
</Examples>

<Anti_Patterns>
  {ANTI_PATTERNS_LIST}
</Anti_Patterns>

<Quality_Gates>
  {QUALITY_GATES_LIST}
</Quality_Gates>

<Collaboration>
  - 선행 에이전트: {UPSTREAM_AGENT}
  - 후행 에이전트: {DOWNSTREAM_AGENT}
  - 입력 산출물: {INPUT_PATH}
  - 출력 산출물: {OUTPUT_PATH}
</Collaboration>
```

**수락 기준**:
- skeleton에 6개 XML 섹션 존재 (Role, Success_Criteria, Constraints, Process, Tool_Usage, Examples)
- 추가 3개 섹션 존재 (Anti_Patterns, Quality_Gates, Collaboration)
- `grep -c '<' agent-skeleton.md` >= 18 (열기+닫기 태그)

### 2.2 visual-builder 템플릿에 SVG 코드 인라인

**파일**: `.claude/skills/ax/templates/visual-builder.md`
**변경**: `<Process>` 섹션에 핵심 SVG 패턴 3개(도넛, 비교 바, 트렌드라인)의 축약 코드를 직접 삽입

현재:
```
2) chart-templates.md 로드하여 차트 구현 패턴 참조
```

변경 후:
```
2) chart-templates.md 로드 (상세 패턴)
   아래 핵심 3종은 즉시 사용 가능:

   도넛: <circle cx="50" cy="50" r="40" stroke="var(--chart-color-1)"
          stroke-dasharray="{pct*251.3/100} 251.3" .../>
   비교바: <div style="width:{pct}%;background:var(--chart-color-1);
           animation:bar-grow 0.6s ..."/>
   트렌드: <polyline points="{...}" stroke="var(--chart-color-1)"
           stroke-dasharray="0 1000" .../>
```

**수락 기준**:
- `<Process>` 섹션 내에 `stroke-dasharray` 패턴 존재 (`grep '<Process>' -A 100 visual-builder.md | grep -c 'stroke-dasharray'` >= 1)
- `grep -c 'var(--chart' visual-builder.md` >= 3

### 2.3 domain-patterns.md에 프롬프트 힌트 추가

**파일**: `.claude/skills/ax/templates/domain-patterns.md`
**변경**: 섹션 6 "도메인별 에이전트 프로세스 힌트" 신규 추가

```markdown
## 6. 도메인별 에이전트 프로세스 필수 단계

Phase 3에서 에이전트 `<Process>`를 커스터마이즈할 때,
도메인 유형에 따라 다음 단계를 반드시 포함:

### code 도메인
- executor의 <Process>에 "테스트 작성" 단계 필수
- reviewer의 <Process>에 "보안 체크(프롬프트 인젝션, API 키 노출)" 필수
- <Anti_Patterns>에 "하드코딩 시크릿", "테스트 없는 커밋" 포함

### document 도메인
- executor의 <Process>에 "팩트체크 + 출처 명시" 단계 필수
- reviewer의 <Process>에 "오탈자 검증" 필수
- <Anti_Patterns>에 "출처 없는 통계", "텍스트 과밀" 포함

### creative 도메인
- executor의 <Process>에 "AI 슬롭 체크" 단계 필수
- reviewer의 <Process>에 "브랜드 일관성" 필수
- <Anti_Patterns>에 "보라색 그라디언트+흰 배경", "이모지 아이콘" 포함

### research 도메인
- executor의 <Process>에 "소스 신뢰도 평가" 단계 필수
- reviewer의 <Process>에 "인용 검증" 필수
- <Anti_Patterns>에 "블로그 우선 인용", "2년 이상 오래된 데이터" 포함

### business 도메인
- executor의 <Process>에 "이해관계자 영향 분석" 단계 필수
- reviewer의 <Process>에 "실행 가능성 검증" 필수
- <Anti_Patterns>에 "모호한 KPI", "구체적 일정 없는 계획" 포함
```

**수락 기준**:
- domain-patterns.md에 "프로세스 필수 단계" 섹션 존재
- 5개 도메인 유형 모두 커버
- 각 도메인에 executor + reviewer + Anti_Patterns 힌트 존재

### 2.3.1 SKILL.md Phase 3에 domain-patterns 참조 추가

**파일**: `.claude/skills/ax/SKILL.md`
**변경**: Phase 3.2 "골든 템플릿 로드 및 커스터마이즈"의 본문 커스터마이즈 단계에 domain-patterns.md 섹션 6 참조를 추가

기존 `3. **본문 커스터마이즈**` 항목에 추가:
```markdown
   - `<Process>` → 도메인 특화 워크플로우 단계
     + `.claude/skills/ax/templates/domain-patterns.md` 섹션 6 "도메인별 에이전트 프로세스 필수 단계"를 Read하고, 해당 도메인의 필수 단계를 <Process>에 반영
   - `<Anti_Patterns>` → domain-patterns.md 섹션 6의 도메인별 Anti_Patterns 힌트 적용
```

**수락 기준**:
- SKILL.md Phase 3.2에 "domain-patterns.md 섹션 6" 참조가 존재
- `grep -c 'domain-patterns' .claude/skills/ax/SKILL.md` >= 3 (Phase 2.1 + Phase 3.2 + 기존)

### 2.4 SKILL.md Phase 간 출력 계약 검증

**파일**: `.claude/skills/ax/SKILL.md`
**변경**: Phase 1, 2, 3 끝에 각각 1단계 "출력 계약 검증" 추가

Phase 1.5 뒤에 추가:
```markdown
### 1.6 출력 계약 검증

domain-analysis.json을 Read하고 다음 필수 필드를 확인합니다:
- `domain_type` ∈ {code, document, creative, research, business}
- `signals.task_dependency` ∈ {sequential, parallel, mixed}
- `signals.quality_criticality` ∈ {low, medium, high}
- `domain_verbs` 배열 길이 >= 2
- `flags.execute`, `flags.here` 존재

누락 시 즉시 보정 후 다음 Phase로 진행.
```

Phase 2.5 뒤에 추가:
```markdown
### 2.6 출력 계약 검증

team-architecture.json을 Read하고 다음을 확인합니다:
- `pattern.primary` 존재 + 6가지 패턴 중 하나
- `agents` 배열 길이 >= 4 (최소 executor+reviewer+visual 2종)
- 모든 에이전트에 name, role, model 필드 존재
- `skills.gap_create` 배열 존재 (빈 배열 허용)
```

Phase 3.4 뒤에 추가:
```markdown
### 3.5 출력 계약 검증

생성된 .claude/agents/*.md 파일 각각을 확인:
- frontmatter에 name, description, model, role, triggers 필수 필드
- 본문에 <Role>, <Success_Criteria>, <Constraints>, <Process>, <Examples> 존재
- <Collaboration> 섹션에 선행/후행 에이전트 명시
```

**수락 기준**:
- SKILL.md에 `### 1.6 출력 계약 검증`, `### 2.6 출력 계약 검증`, `### 3.5 출력 계약 검증` 존재
- 각 검증 단계에 구체적 필드명과 유효값 범위 명시

### 2.5 SKILL.md Phase 7 에러 복구 전략

**파일**: `.claude/skills/ax/SKILL.md`
**변경**: Phase 7.2 뒤에 `### 7.3 에러 복구` 섹션 추가 (기존 7.3 → 7.4로 번호 변경)

```markdown
### 7.3 에러 복구

**에이전트 호출 실패 시:**
1회차: 동일 에이전트 재시도 (프롬프트 동일)
2회차: 프롬프트를 핵심만 남기고 단순화하여 재시도
3회차: 해당 에이전트 스킵, 사용자에게 "[에이전트명] 실패, 수동 처리 필요" 알림

**API 키 부재 시:**
- 이미지 생성: SVG 폴백 경로 사용 (기존 구현)
- 로그: generation-log.json에 "fallback_used": true 기록

**비용 추적:**
- 각 API 호출 비용을 generation-log.json의 `costs` 배열에 기록
- 누적 비용 $10 초과 시 사용자 확인 후 계속
```

**수락 기준**:
- SKILL.md에 `### 7.3 에러 복구` 섹션이 정확히 1개 존재
- SKILL.md에 `### 7.4 실행 완료 보고` 존재 (기존 7.3에서 번호 변경 확인)
- 3단계 에스컬레이션(재시도→단순화→스킵) 명시
- 비용 한도 $10 명시

### 2.6 검증 스크립트 생성

**파일**: `.claude/skills/ax/tools/validate_project.py` (신규)
**목적**: Phase 6 자동화 — 10항목 구조 검증

```python
# 사용법: python3 validate_project.py <project-dir>
# 출력: JSON (validation-report.json 형식)

검증 항목:
1. 에이전트 frontmatter 파싱 (--- YAML --- 추출)
2. 필수 XML 태그 (<Role>, <Success_Criteria>, <Constraints>, <Examples>)
3. 모델 ID 유효성 (claude-sonnet-4-6|claude-opus-4-6|claude-haiku-4-5)
4. 스킬 frontmatter (name, description)
5. CLAUDE.md "Harness-Generated Team" 섹션
6. 에이전트 테이블 행 수 = 에이전트 파일 수
7. 순환 의존성 검사 (위임 규칙 → 방향 그래프 → 사이클 검출)
8. 역할 충돌 (동일 role의 에이전트가 동일 triggers 보유)
9. 시각화 체인 (visual-architect → visual-builder → visual-qa 연결)
10. 하드코딩 색상 (#[0-9a-fA-F]{3,8} 패턴, 프롬프트/예시 영역 제외)
```

**수락 기준**:
- `python3 validate_project.py projects/md-chatbot-system` → 10항목 결과 출력
- 4개 프로젝트 모두 실행 시 오류 없음
- 출력 JSON이 기존 validation-report.json 형식과 호환

### 2.7 기존 4개 프로젝트 에이전트 보강

**파일**: `projects/*/.claude/agents/*.md` (약 27개 파일)
**변경**: 모든 에이전트에 `<Anti_Patterns>`, `<Quality_Gates>`, `<Collaboration>` 추가

각 프로젝트 특화 보강:

| 프로젝트 | 특화 보강 |
|---------|----------|
| ai-era-leadership-slides | slide-builder `<Process>`에 chart-templates.md SVG 패턴 3개 인라인 |
| marketing-landing-page | conversion-reviewer `<Quality_Gates>`에 CTA 대비율 7:1+ 검증 로직 |
| ai-vibe-coding-manual | claude-code-specialist `<Process>`에 Claude Code 핵심 커맨드 10개 인라인 |
| md-chatbot-system | backend-developer `<Process>`에 RAG 청킹 전략(512토큰 overlap-128) 코드 스니펫 |

**수락 기준**:
- 27개 에이전트 모두 `<Anti_Patterns>`, `<Quality_Gates>`, `<Collaboration>` 보유
- `validate_project.py` 실행 시 4개 프로젝트 전체 PASS

### 2.8 v0.1 프로젝트 삭제

**파일**: `projects/ai-leadership-slides/` (전체 디렉토리)
**변경**: 삭제 (v0.1 형식, harness 참조, 시각화 3인조 없음 — ai-era-leadership-slides로 대체)

**수락 기준**:
- `ls projects/ai-leadership-slides/ 2>&1` → "No such file or directory"

### 2.9 제네릭 테스트 시나리오 갱신

**파일**: `tests/ax/scenario-ecommerce.md`, `scenario-research.md`, `scenario-saas.md`
**변경**: v0.2 기준으로 전면 재작성

추가할 검증 항목 (3개 시나리오 공통):
- 도메인 분류기 정확성 (domain_type 일치)
- `<Examples>` Good/Bad 존재
- `<Anti_Patterns>` 존재
- `<Collaboration>` 에이전트 간 연결
- 시각화 3인조 포함 여부
- 의미적 검증 10항목

**수락 기준**:
- 3개 시나리오 모두 v0.2 검증 항목 10개+ 포함
- `grep -c 'Anti_Patterns\|Quality_Gates\|Collaboration' tests/ax/scenario-*.md` >= 9

---

## 3. 리스크

| 리스크 | 영향 | 확률 | 완화 |
|--------|------|------|------|
| agent-skeleton이 너무 커지면 LLM이 플레이스홀더를 제대로 채우지 못함 | 생성 품질 저하 | 중 | 80줄 이내로 제한, 각 섹션 주석으로 가이드 |
| 기존 프로젝트 27개 에이전트 수정 중 실수 | 기존 작동하던 에이전트 깨짐 | 중 | validate_project.py로 수정 전후 비교 검증 |
| validate_project.py 마크다운 파싱 취약 | 잘못된 PASS/FAIL | 중 | YAML frontmatter는 `---` 구분자 기반 단순 파싱, XML 태그는 정규식 |
| Phase 간 계약 검증이 파이프라인 속도 저하 | 실행 시간 증가 | 저 | 각 검증은 JSON Read + 필드 존재 확인만 (< 1초) |

---

## 4. 구현 순서

```
Step 1: agent-skeleton.md 재설계 (2.1)
Step 2: visual-builder.md SVG 인라인 (2.2)
Step 3: domain-patterns.md 프롬프트 힌트 (2.3)
Step 4: SKILL.md 출력 계약 검증 (2.4) + 에러 복구 (2.5)
Step 5: validate_project.py 생성 (2.6)
Step 6: 기존 프로젝트 에이전트 보강 (2.7)
Step 7: v0.1 프로젝트 삭제 (2.8) + 테스트 시나리오 갱신 (2.9)
Step 8: 최종 검증 — validate_project.py로 4개 프로젝트 전체 PASS 확인
```
