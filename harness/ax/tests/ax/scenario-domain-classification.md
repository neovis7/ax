# 도메인 분류기 테스트 케이스

> 10개 경계 케이스로 분류 정확성을 검증합니다.

## 테스트 케이스

### 1. 명확한 단일 도메인
| 입력 | 기대 domain_type | 기대 sub_type |
|------|-----------------|---------------|
| "REST API 서버 개발" | code | api |
| "분기 실적 보고서 작성" | document | report |
| "브랜드 로고 디자인" | creative | null |

### 2. 복합 도메인 (타이브레이크 검증)
| 입력 | 기대 주 도메인 | 기대 부 도메인 | 타이브레이크 근거 |
|------|-------------|-------------|----------------|
| "마케팅 랜딩 페이지 제작" | creative | code | 결과물=시각 디자인물 → creative |
| "데이터 분석 대시보드 구축" | code | research | 결과물=실행 가능한 코드 → code |
| "마케팅 전략 보고서" | document | business | 결과물=HTML/PDF 문서 → document |
| "고객 여정 데이터 시각화 자동화 시스템" | code | research | "시스템"=실행 가능 코드 → code |

### 3. 하위 유형 판별 (code 도메인)
| 입력 | 기대 sub_type | 판별 키워드 |
|------|-------------|-----------|
| "Next.js + FastAPI 풀스택 앱" | fullstack | "풀스택" |
| "Kubernetes 배포 파이프라인" | devops | "Kubernetes" |
| "Airflow ETL 파이프라인" | data-pipeline | "ETL", "Airflow" |

### 4. 영어 입력
| 입력 | 기대 domain_type | 근거 |
|------|-----------------|------|
| "e-commerce SaaS platform" | code | "SaaS" 매핑 |
| "market research report" | research | "research" 매핑 |

### 5. 극도로 짧은 입력
| 입력 | 기대 동작 |
|------|----------|
| "챗봇" | code (기본값: "봇"→코드 구현) |
| "보고서" | document |

## 검증 방법

Phase 6 시나리오 검증에서 이 테스트 케이스를 참조하여:
1. 각 입력에 대한 domain-analysis.json의 domain_type 확인
2. 기대 값과 일치하는지 검증
3. 복합 도메인의 타이브레이크가 규칙대로 적용되었는지 확인
4. 정확도 목표: 10개 중 8개 이상 (80%+)
