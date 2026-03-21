# 검증 시나리오: 시장 리서치 보고서

> v0.2 기준 재작성 (2026-03-19)

## 입력
`/ax "시장 리서치 및 보고서 작성 - 데이터 수집, 분석, 보고서 생성"`

## 예상 결과
- 도메인 유형: **research** (주)
- 패턴: **감독자**
- 에이전트 수: 6~8개
- 시각화 3인조: 포함 필수
- Phase 1.3 코드 탐색: **스킵** (non-code)

## 구조 검증 (v0.2)
- [ ] 도메인 분류기: domain_type = "research"
- [ ] Phase 1.3 스킵 + 콘텐츠 요구사항 분석
- [ ] 에이전트 frontmatter (name, description, model)
- [ ] 모델 ID 유효성
- [ ] XML 태그: `<Role>`, `<Success_Criteria>`, `<Constraints>`
- [ ] `<Examples>` Good/Bad 존재
- [ ] `<Anti_Patterns>` 존재 (research: "블로그 우선 인용", "출처 URL 누락")
- [ ] `<Quality_Gates>` 존재
- [ ] `<Collaboration>` 선행/후행 에이전트 명시
- [ ] 시각화 체인: visual-architect → visual-builder → visual-qa
- [ ] CLAUDE.md "Harness-Generated Team" 섹션
- [ ] 순환 의존성 없음
- [ ] 의미적 검증 통과
- [ ] 출력 계약 검증 (1.6, 2.6, 3.5) 통과

## 시나리오 검증

### 시나리오 1: "경쟁사 시장 점유율을 조사해주세요"
- 예상 에이전트: supervisor → data-collector
- 위임 규칙 일치: YES

### 시나리오 2: "분석 보고서를 작성해주세요"
- 예상 에이전트: supervisor → report-writer → visual-builder
- 위임 규칙 일치: YES

### 시나리오 3: "인용 정확성을 검증해주세요"
- 예상 에이전트: reviewer (인용 검증 + 데이터 최신성)
- 위임 규칙 일치: YES
