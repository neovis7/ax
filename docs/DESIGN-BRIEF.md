# ax 설계 브리프

## 배경

Claude Code의 에이전트 아키텍처(Agent Team & Skill Architect)를 보고,
"도메인을 입력하면 에이전트 팀을 자동 생성하는 메타 도구"를 만들기로 결정.

## 핵심 결정사항

| 항목 | 결정 | 근거 |
|------|------|------|
| 사용 형태 | Claude Code 스킬 (`/ax`) | 프로젝트 컨텍스트와 자연스럽게 통합 |
| 범위 | 프로젝트 단위 | `.claude/` 디렉토리에 생성, 전역 오염 방지 |
| 자동화 수준 | 완전 자동 (옵션: `--interview`) | 기본은 원클릭, 필요시 deep-interview |
| 패턴 선택 | AI 자동 판단 | 도메인 분석 후 최적 패턴 선택 + 근거 제시 |
| 결과물 | 에이전트 + 스킬 + 오케스트레이터 + 테스트 + 아키텍처 문서 | 완결된 에이전트 시스템 |
| 실행 모드 | 에이전트 팀 모드 (Agent + bypassPermissions) | Claude Code 권장 방식 |

## 설계 과제 (v0.1 완료)

- [x] Phase 1 도메인 분석: 코드베이스 탐색 전략, 분류 기준 정의
- [x] 에이전트/스킬 마크다운 표준 스키마 정의
- [x] 6가지 패턴 자동 선택 판단 로직 (프롬프트 엔지니어링)
- [x] 검증 시나리오 포맷: 가이드 문서 (마크다운 체크리스트)
- [x] 기존 `.claude/` 파일 충돌 처리 전략 (존재 확인 → 덮어쓰기/건너뛰기)
- [x] 데이터 프로토콜 선택 기준 (SendMessage 기본)
- [x] 오케스트레이터 규칙의 CLAUDE.md 주입 형식 (append merge)

## v0.2 완료 (시각화 + 도메인 적응)

- [x] M2: 파이프라인 자동화 (bypassPermissions, TaskCreate/Update, 자동 수정 루프)
- [x] M3: 시각화 코어 (시각화 에이전트 3인조, 디자인 토큰 템플릿, SVG 차트 7종, 멀티 LLM 통합)
- [x] M4: 도메인 적응 (5유형 분류기, --execute, Examples 자동 생성, 의미적 검증)

## 남은 과제 (v0.3+)

- [x] 외부 스킬 추천 (external-skill-catalog.md, Phase 2.4.1)
- [x] 에이전트 재사용 라이브러리 (library/base-agents/ 4개 베이스 에이전트)
- [x] `--interview` 모드 (references/interview-mode.md)
- [x] 마켓플레이스 통합 스펙 (references/marketplace.md)
- [x] 도메인 분류 강화 (타이브레이크, 다국어, 하위 유형 프리셋, 부 도메인 병합)
- [x] Anthropic 공식 가이드라인 적용 (Progressive Disclosure, pushy description, eval)

## 참고 이미지

원본 아키텍처 다이어그램: 6 Phase 워크플로우, Core Components (오케스트레이터 + 에이전트 + 스킬),
Two Execution Modes (팀 모드/서브에이전트 모드), 6 Architecture Patterns, 3 Data Protocols

## 산출물

- `docs/superpowers/specs/2026-03-18-ax-design.md` — 상세 설계 스펙
- `docs/superpowers/plans/2026-03-18-ax-v01-mvp.md` — 15-Task 구현 계획
- `.claude/skills/ax/SKILL.md` — 메인 스킬 (Phase 0-7, ~750줄)
- `.claude/skills/ax/templates/*.md` — 12개 템플릿 파일
- `.claude/skills/ax/references/*.md` — 6개 참조 문서 (Progressive Disclosure)
- `.claude/skills/ax/tools/validate_project.py` — 10항목 자동 검증 스크립트
- `tests/ax/scenario-*.md` — 3개 검증 시나리오 (v0.2 기준)
