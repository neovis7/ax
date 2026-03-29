# ax — Agent Team Architect (v0.4)

도메인 설명을 입력하면 최적의 에이전트 팀(agents, skills, orchestrator)을 자동 생성하는 메타 도구.
시각화 품질을 핵심 차별점으로, 멀티 LLM(Claude + OpenAI + Gemini)을 활용한다.

## 프로젝트 개요

- **이름**: ax
- **형태**: Claude Code 스킬 (`/ax "도메인 설명"`)
- **목적**: 프로젝트별 맞춤 에이전트 팀을 8단계 파이프라인으로 자동 생성
- **범위**: 프로젝트 단위 (`.claude/agents/`, `.claude/skills/`)

## v0.4 핵심 변경사항

- **무개입 아키텍처**: 인터뷰 후 Phase 2~7은 완전 자율 실행. `execution-policy.json`으로 모든 분기 자동 결정. 사용자 질문 = 0.
- **3-Layer CRUD 검증**: Layer 1(정적 완성도) → Layer 2(API 행동 — 기존 Stage B 대체) → Layer 3(Playwright E2E). 수정 루프 최대 5회.
- **Hub-and-Spoke 분해**: SKILL.md를 ~80줄 오케스트레이터 + `phases/*.md` 8개 파일로 분리. 컨텍스트 효율 극대화.
- **생성 품질 강화**: anti-pattern 라이브러리 5개, base-agent 9개 (기존 4 + 신규 5), API fixture 자동 생성, CRUD 체크리스트 자동 생성.
- **검증 인프라**: `validate_ax.py` (ax 자체 검증), `run_scenario.py` (JSON 시나리오), `Makefile` 통합.

## 파이프라인 (Hub-and-Spoke)

```
SKILL.md (오케스트레이터 ~80줄)
  └→ phases/phase-0-init.md          초기화
  └→ phases/phase-1-analysis.md      도메인 분석
  └→ phases/phase-2-architecture.md  팀 아키텍처 + API 계약 + fixture + CRUD 체크리스트
  └→ phases/phase-3-agents.md        에이전트 생성 (base-agent + anti-pattern 주입)
  └→ phases/phase-4-skills.md        스킬 생성
  └→ phases/phase-5-orchestrator.md  오케스트레이터 생성
  └→ phases/phase-6-validation.md    검증 + 인터뷰 + execution-policy 생성
  └→ phases/phase-7-execution.md     실행 + 3-Layer 검증 + 최종 보고
```

## 실행 모드

- 기본: 완전 자동 (Phase 0~6)
- `--execute`: Phase 0~7 (팀 생성 + 즉시 실행, 인터뷰 자동 포함)
- `--execute --skip-interview`: 인터뷰 없이 기본값으로 즉시 실행
- `--here`: 현재 디렉토리에 에이전트 생성
- `--interview`: deep-interview 기반 요구사항 명확화
- `--design {skill}`: 디자인 스킬 명시 선택 (supanova/frontend-design/none)

## 아키텍처 패턴 (자동 선택)

- 파이프라인 (순차 처리)
- 팬아웃/팬인 (병렬 분산 → 취합)
- 전문가 풀 (유형별 라우팅)
- 생성-검증 (Create → Verify)
- 감독자 (Supervisor)
- 계층적 위임 (Hierarchical Delegation)

## 생성 결과물

```
.claude/
  agents/*.md          에이전트 정의
  skills/*.md          스킬 정의
  CLAUDE.md            오케스트레이션 규칙 (기존 파일에 추가)
  ARCHITECTURE.md      에이전트 관계도, 데이터 흐름, 패턴 설명
tests/
  ax/*.md              검증 시나리오
```

## 테스트

```bash
make test-ax          # Tier 2: ax 스킬 자체 검증
make test-scenarios   # Tier 3: JSON 시나리오 검증
make test-project PROJECT=path  # Tier 1: 생성 프로젝트 검증
```

## 코딩 규칙

- 한국어 주석, 한국어 문서
- 스킬/에이전트 마크다운은 Claude Code 공식 스키마 준수
- 기존 프로젝트 파일과 충돌 시 자동 덮어쓰기 (무중단 원칙)
- 인터뷰 이후 무개입 — 모든 분기는 execution-policy.json으로 자동 결정
- **`harness/` 디렉토리 생성 금지**: ax 코드는 루트 `.claude/skills/ax/`에만 존재. `harness/ax/` 복사본을 절대 만들지 않음
- **Pretendard 폰트 로컬 다운로드 금지**: `~/.claude/fonts/pretendard/` 글로벌 경로 참조. 프로젝트 내 폰트 파일 저장 금지
