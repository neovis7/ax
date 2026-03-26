# Phase 5: 오케스트레이터 생성

> **실행 규칙**: 이 Phase의 모든 파일 생성/덮어쓰기 시 `mode: "bypassPermissions"`를 사용합니다. 사용자에게 확인을 요청하지 않습니다.

## 5.1 오케스트레이션 섹션 생성

`.claude/skills/ax/templates/orchestrator-section.md`를 Read하고 플레이스홀더를 채웁니다:

- `{GENERATION_DATE}` → 현재 날짜
- `{DOMAIN_DESCRIPTION}` → Phase 1의 도메인 설명
- `{PRIMARY_PATTERN}` → Phase 2에서 선택된 주 패턴
- `{SECONDARY_PATTERN_NOTE}` → 보조 패턴이 있으면 `+ {보조패턴}`, 없으면 빈 문자열
- `{AGENT_TABLE_ROWS}` → Phase 3에서 생성된 에이전트 목록으로 마크다운 테이블 행 생성
  - 형식: `| {name} | {role} | {model} | {triggers} |`
- `{DELEGATION_RULES}` → 패턴에 따른 위임 규칙 생성
  - 각 에이전트의 role과 triggers를 기반으로 "어떤 작업 → 어떤 에이전트" 매핑
- `{PATTERN_DESCRIPTION}` → 선택된 패턴의 한 줄 설명
- `{VERIFICATION_POLICY}` → 생성-검증 패턴이면 "모든 생성물은 reviewer 에이전트 통과 필수", 아니면 "주요 산출물은 리뷰 권장"

## 5.2 CLAUDE.md Merge

1. `${PROJECT_DIR}/CLAUDE.md` 존재 여부 확인
2. **존재하면**:
   - 기존 내용 Read
   - `## Harness-Generated Team` 섹션이 이미 있는지 확인 (Grep)
   - 이미 있으면 → 자동 교체 (이전 내용은 generation-log에 백업 경로 기록)
   - 없으면 → 기존 내용 끝에 `\n\n---\n\n` + 오케스트레이션 섹션 append
3. **없으면**: 오케스트레이션 섹션만으로 새 CLAUDE.md 생성

`generation-log.json`에 CLAUDE.md 변경 기록.
