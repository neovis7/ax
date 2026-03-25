# 검증 시나리오: SaaS 풀스택 개발

> v0.2 기준 재작성 (2026-03-19)

## 입력
`/ax "SaaS 풀스택 개발 - Next.js 프론트엔드, FastAPI 백엔드, PostgreSQL"`

## 예상 결과
- 도메인 유형: **code** (주)
- 패턴: **계층적 위임 + 생성-검증**
- 에이전트 수: 8~10개
- 시각화 3인조: 포함 필수
- 모델 라우팅: system-architect에 **Opus** 배정

## 구조 검증 (v0.2)
- [ ] 도메인 분류기: domain_type = "code"
- [ ] Phase 1.3 코드 탐색 실행
- [ ] 에이전트 frontmatter (name, description, model)
- [ ] 모델 ID 유효성 (Opus 포함 확인)
- [ ] XML 태그: `<Role>`, `<Success_Criteria>`, `<Constraints>`
- [ ] `<Examples>` Good/Bad 존재
- [ ] `<Anti_Patterns>` 존재 (code: "하드코딩 시크릿", "테스트 없는 커밋")
- [ ] `<Quality_Gates>` 존재
- [ ] `<Collaboration>` 선행/후행 에이전트 명시
- [ ] 시각화 체인: visual-architect → visual-builder → visual-qa
- [ ] CLAUDE.md "Harness-Generated Team" 섹션
- [ ] 순환 의존성 없음
- [ ] 의미적 검증 통과
- [ ] 출력 계약 검증 (1.6, 2.6, 3.5) 통과
- [ ] code-reviewer에 보안 체크 포함

## 시나리오 검증

### 시나리오 1: "시스템 아키텍처를 설계해주세요"
- 예상 에이전트: system-architect (Opus)
- 위임 규칙 일치: YES

### 시나리오 2: "사용자 인증 API를 구현해주세요"
- 예상 에이전트: manager → backend-lead → backend-developer
- 위임 규칙 일치: YES

### 시나리오 3: "대시보드 UI + 코드 리뷰"
- 예상 에이전트: frontend-developer → code-reviewer + visual-qa
- 위임 규칙 일치: YES
