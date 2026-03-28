# Phase 4: 스킬 생성

> **실행 규칙**: 이 Phase의 모든 파일 생성/덮어쓰기 시 `mode: "bypassPermissions"`를 사용합니다. 사용자에게 확인을 요청하지 않습니다. (v0.1 — 커스텀만)

## 4.1 커스텀 스킬 생성

> 스킬 품질 가이드: Read `.claude/skills/ax/references/skill-writing-guide.md`
> 이 가이드의 원칙을 모든 스킬 생성에 적용합니다.

`.omc/ax/team-architecture.json`의 `skills.gap_create` 목록에 대해:

각 스킬에 대해 `.claude/skills/ax/templates/skill-skeleton.md`를 기반으로:
1. frontmatter 채우기 (name, description, origin=ax, domain, dependencies)

**description 작성 원칙 ("Pushy" 패턴):**
- Claude는 스킬 트리거를 보수적으로 판단하므로, description을 적극적으로 작성
- 스킬이 하는 일 + 구체적 트리거 상황 + 경계 조건을 모두 기술
- 좋은 예: "PDF 파일 읽기, 텍스트/테이블 추출, 병합, 분할... .pdf 파일을 언급하거나 PDF 산출물을 요청하면 반드시 이 스킬을 사용할 것."
- 나쁜 예: "데이터를 처리하는 스킬" — 너무 모호
- 상세: `references/skill-writing-guide.md` §1 참조

2. "When to Activate" 섹션 — 이 스킬이 활성화되어야 할 조건 목록
3. "Core Rules" 섹션 — 스킬 실행 시 지켜야 할 핵심 규칙

**본문 작성 원칙:**
- **Why-First**: 강압적 규칙("ALWAYS do X")보다 이유 설명이 효과적. LLM은 이유를 이해하면 엣지 케이스도 올바르게 판단
- **일반화**: 테스트에서 발견된 문제를 특정 예시에만 맞추지 말고 원리 수준에서 수정
- **컨텍스트 절약**: 모든 문장이 토큰 비용을 정당화하는지 자문. Claude가 이미 아는 내용은 삭제
- **Progressive Disclosure**: skill.md는 500줄 이내. 초과 시 references/로 분리
- 상세: `references/skill-writing-guide.md` §2, §5 참조

4. "Process" 섹션 — 단계별 실행 절차
5. "Examples" 섹션 — 사용 예시 1-2개

**스크립트 번들링 (Phase 7 실행 후 관찰):**
- 3개 이상 테스트에서 동일한 헬퍼 스크립트 생성 → `scripts/`에 번들링
- 매번 같은 pip/npm install → 스킬에 의존성 설치 단계 명시
- 동일 다단계 접근법 반복 → 스킬 본문에 표준 절차로 기술
- 상세: `references/skill-writing-guide.md` §6 참조

스킬 파일 생성 전 충돌 확인:
- `.claude/skills/{skill-name}/SKILL.md` 존재 여부 Glob으로 확인
- 이미 존재하면 자동 덮어쓰기

`.claude/skills/{skill-name}/SKILL.md` 경로에 Write (디렉토리 먼저 생성).
`generation-log.json`에 기록.

> 외부 스킬 검색·설치는 v0.2에서 추가 예정.
