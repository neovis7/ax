# 에이전트 재사용 라이브러리

> Status: IMPLEMENTED — library/base-agents/에 4개 베이스 에이전트 생성 완료 (visual-architect, visual-builder, visual-qa, reviewer).

프로젝트 간 공통 에이전트를 "베이스 + 오버라이드" 패턴으로 공유합니다. 매번 처음부터 생성하면 품질 편차가 생기므로, 검증된 베이스를 공유하고 도메인 특화 부분만 오버라이드합니다.

## 구조

```
.claude/skills/ax/library/
  base-agents/
    visual-architect-base.md
    visual-builder-base.md
    visual-qa-base.md
    reviewer-base.md
```

## Phase 3에서의 활용

```
1) team-architecture.json의 에이전트 역할 확인
2) library/base-agents/ 에서 매칭되는 베이스 에이전트 탐색
3) 베이스가 있으면:
   - 베이스 Read
   - 도메인 특화 오버라이드 적용 (frontmatter, Process, Anti_Patterns, Collaboration)
   - 결합된 에이전트를 .claude/agents/{name}.md에 Write
4) 베이스가 없으면:
   - 기존 방식 (agent-skeleton.md 기반 전체 생성)
```

## 오버라이드 규칙

- **유지**: `<Role>` 기본 미션, `<Tool_Usage>` 기본 도구
- **교체**: `<Process>` 도메인 특화, `<Anti_Patterns>` 도메인 힌트, `<Collaboration>` 프로젝트별
- **추가**: `<Examples>` 도메인 맞춤 Good/Bad, `<Quality_Gates>` 도메인 기준
