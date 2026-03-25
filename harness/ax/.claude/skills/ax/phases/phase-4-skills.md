# Phase 4: 스킬 생성 (v0.1 — 커스텀만)

## 4.1 커스텀 스킬 생성

`.omc/ax/team-architecture.json`의 `skills.gap_create` 목록에 대해:

각 스킬에 대해 `.claude/skills/ax/templates/skill-skeleton.md`를 기반으로:
1. frontmatter 채우기 (name, description, origin=ax, domain, dependencies)
2. "When to Activate" 섹션 — 이 스킬이 활성화되어야 할 조건 목록
3. "Core Rules" 섹션 — 스킬 실행 시 지켜야 할 핵심 규칙
4. "Process" 섹션 — 단계별 실행 절차
5. "Examples" 섹션 — 사용 예시 1-2개

스킬 파일 생성 전 충돌 확인:
- `.claude/skills/{skill-name}/SKILL.md` 존재 여부 Glob으로 확인
- 이미 존재하면 자동 덮어쓰기

`.claude/skills/{skill-name}/SKILL.md` 경로에 Write (디렉토리 먼저 생성).
`generation-log.json`에 기록.

> 외부 스킬 검색·설치는 v0.2에서 추가 예정.
