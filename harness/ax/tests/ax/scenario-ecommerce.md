# 검증 시나리오: 이커머스 플랫폼

> v0.2 기준 재작성 (2026-03-19)

## 입력
`/ax "이커머스 플랫폼 - 상품 관리, 주문 처리, 고객 지원"`

## 예상 결과
- 도메인 유형: **code** (주), business (부)
- 패턴: **전문가 풀 + 생성-검증**
- 에이전트 수: 8~10개
- 시각화 3인조: 포함 필수

## 구조 검증 (v0.2)
- [ ] 도메인 분류기: domain_type = "code"
- [ ] Phase 1.3 코드 탐색 실행
- [ ] 에이전트 frontmatter (name, description, model)
- [ ] 모델 ID 유효성
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

## 시나리오 검증

### 시나리오 1: "상품 등록 API를 구현해주세요"
- 예상 에이전트: router → product-specialist
- 위임 규칙 일치: YES

### 시나리오 2: "주문 처리 워크플로우를 설계해주세요"
- 예상 에이전트: router → order-specialist
- 위임 규칙 일치: YES

### 시나리오 3: "대시보드 UI를 만들어주세요"
- 예상 에이전트: visual-architect → frontend → visual-builder → visual-qa
- 위임 규칙 일치: YES
