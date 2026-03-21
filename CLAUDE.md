# ax — Agent Team Architect

도메인 설명을 입력하면 최적의 에이전트 팀(agents, skills, orchestrator)을 자동 생성하는 메타 도구.
시각화 품질을 핵심 차별점으로, 멀티 LLM(Claude + OpenAI + Gemini)을 활용한다.

## 프로젝트 개요

- **이름**: ax
- **형태**: Claude Code 스킬 (`/ax "도메인 설명"`)
- **목적**: 프로젝트별 맞춤 에이전트 팀을 8단계 파이프라인으로 자동 생성
- **범위**: 프로젝트 단위 (`.claude/agents/`, `.claude/skills/`)

## 8단계 파이프라인

0. **초기화** — 권한 자동 설정, 진행 추적 초기화
1. **도메인 분석** — 도메인 유형 분류(code/document/creative/research/business), 코드베이스 탐색(code만), 시그널 추출, **도메인 리서치**(규제/의료/법률 등 정확성 중요 도메인 시 자동 실행)
2. **팀 아키텍처 설계** — 6가지 패턴 중 최적 자동 선택, 도메인별 골든 패턴 참조, 시각화 3인조 기본 포함, **API 계약**(fullstack 시 Zod 스키마 사전 정의)
3. **에이전트 정의 생성** — `.claude/agents/*.md` + Good/Bad `<Examples>` 자동 생성
4. **스킬 생성** — `.claude/skills/{name}/SKILL.md` 파일 생성
5. **오케스트레이터 생성** — CLAUDE.md에 오케스트레이션 규칙 주입
6. **검증 & 테스트** — 구조 + 의미적 검증 + 시나리오 + ARCHITECTURE.md 생성
7. **실행** (`--execute` 전용) — 생성된 팀으로 도메인 작업 즉시 수행, 시각화 파이프라인 포함

## 아키텍처 패턴 (자동 선택)

- 파이프라인 (순차 처리)
- 팬아웃/팬인 (병렬 분산 → 취합)
- 전문가 풀 (유형별 라우팅)
- 생성-검증 (Create → Verify)
- 감독자 (Supervisor)
- 계층적 위임 (Hierarchical Delegation)

## 실행 모드

- 기본: 완전 자동 (Phase 0~6)
- `--execute`: Phase 0~7 (팀 생성 + 즉시 실행)
- `--here`: 현재 디렉토리에 에이전트 생성
- `--interview`: deep-interview 기반 요구사항 명확화 (v1.0)

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

## 코딩 규칙

- 한국어 주석, 한국어 문서
- 스킬/에이전트 마크다운은 Claude Code 공식 스키마 준수
- 기존 프로젝트 파일과 충돌 시 자동 덮어쓰기 (무중단 원칙)
