# 도메인 프레임워크 매핑

> Phase 1.5에서 `domain_type` 감지 후 조건부 Read합니다.
> 필수 프레임워크는 자동 포함, 권장 프레임워크는 사용자 질문 후 선택합니다.

## 1. 프레임워크 매핑 테이블

### 필수 (must) — 자동 포함

| domain_type | 프레임워크 | 설명 | target_roles | process_rule | quality_gate |
|-------------|-----------|------|-------------|-------------|-------------|
| 콘텐츠/creative | AIDA | 주의→관심→욕구→행동 전환 구조 | executor | 모든 콘텐츠를 AIDA 구조(Attention→Interest→Desire→Action)로 설계하라 | AIDA 4단계가 콘텐츠에 명시적으로 반영되어 있는지 확인 |
| 콘텐츠/creative | SEO 키워드 매핑 | 검색 최적화 키워드 전략 | executor | 핵심 키워드를 도출하고 제목/소제목/본문에 자연스럽게 배치하라 | 타겟 키워드가 제목과 첫 문단에 포함되어 있는지 확인 |
| code | SOLID | 객체지향 설계 5원칙 | executor, reviewer | 클래스/모듈 설계 시 단일 책임, 개방-폐쇄, 리스코프 치환, 인터페이스 분리, 의존성 역전 원칙을 적용하라 | SOLID 원칙 위반 여부 확인 — 특히 단일 책임과 의존성 역전 |
| code | OWASP Top 10 | 웹 보안 취약점 상위 10개 | executor, reviewer | 인증, 입력 검증, 세션 관리, 접근 제어에서 OWASP Top 10 가이드라인을 준수하라 | SQL Injection, XSS, CSRF, 인증 우회 등 OWASP Top 10 항목 검증 |
| 데이터/data | Star/Snowflake 스키마 | 분석용 데이터 모델링 패턴 | executor | 데이터 웨어하우스/분석 모델은 Star 또는 Snowflake 스키마로 설계하라 | 팩트/디멘전 테이블 분리가 올바른지 확인 |
| 비즈니스/business | BMC | Business Model Canvas 9블록 | executor | 사업 모델을 BMC 9블록(고객 세그먼트, 가치 제안, 채널, 관계, 수익원, 핵심 자원, 핵심 활동, 파트너, 비용 구조)으로 분석하라 | BMC 9블록이 모두 채워져 있는지 확인 |
| 비즈니스/business | TAM/SAM/SOM | 시장 규모 3단계 산정 | executor | 시장 분석 시 TAM(전체 시장)→SAM(접근 가능 시장)→SOM(실제 획득 가능 시장)을 단계별로 산정하라 | 3단계 시장 규모가 논리적 근거와 함께 산정되어 있는지 확인 |
| 교육/education | Bloom's Taxonomy | 학습 목표 인지 수준 6단계 | specialist, executor | 문제/콘텐츠 난이도를 Bloom의 6단계(기억→이해→적용→분석→평가→창조)로 태깅하라 | 모든 학습 콘텐츠에 Bloom 인지 단계가 태깅되어 있는지 확인. 미태깅 시 FAIL |
| 교육/education | CEFR | 국제 언어 능력 등급 기준 | specialist, executor | 언어 학습 콘텐츠의 등급을 CEFR 레벨(A1~C2)과 매핑하여 국제 기준으로 표현하라 | 등급별 콘텐츠가 대응하는 CEFR 레벨과 일치하는지 확인. 불일치 시 FAIL |
| 법률/legal | IRAC | 법적 논증 구조 | executor | 법률 분석을 IRAC(Issue→Rule→Application→Conclusion) 구조로 작성하라 | IRAC 4단계가 빠짐없이 포함되어 있는지 확인 |
| 법률/legal | GDPR/PIPA | 개인정보 보호 규정 | executor, reviewer | 개인정보 처리 시 GDPR/PIPA 요구사항(수집 동의, 목적 제한, 최소 수집, 보관 기간, 파기)을 준수하라 | 개인정보 처리 항목별 법적 근거가 명시되어 있는지 확인 |
| 라이프/lifestyle | BMR/TDEE | 기초대사량/총에너지소비량 | executor | 건강/영양 서비스에서 BMR(Harris-Benedict 또는 Mifflin-St Jeor)과 TDEE를 기반으로 칼로리를 산정하라 | 칼로리 계산이 과학적 공식에 기반하는지 확인 |
| 라이프/lifestyle | KDRIs | 한국인 영양소 섭취기준 | executor | 영양 정보 제공 시 KDRIs 기준을 참조하라 | 영양소 권장량이 KDRIs 범위 내인지 확인 |
| 문서/document | Diataxis | 문서 4유형 구조화 | executor | 문서를 Diataxis 4유형(튜토리얼, How-to 가이드, 참조, 설명)으로 분류하여 작성하라 | 문서가 4유형 중 하나로 명확히 분류되어 있는지 확인 |
| 운영/operations | SIPOC/RACI | 프로세스 정의 + 책임 매트릭스 | executor | 프로세스를 SIPOC(공급자→입력→프로세스→출력→고객)으로 정의하고, RACI로 역할을 배정하라 | 모든 프로세스에 SIPOC + RACI가 정의되어 있는지 확인 |
| 운영/operations | SMART | 목표 설정 프레임워크 | executor | 목표를 SMART(구체적, 측정 가능, 달성 가능, 관련성, 시간 한정)로 설정하라 | 모든 목표가 SMART 5요소를 충족하는지 확인 |
| 전문/specialized | GHG Protocol | 온실가스 배출량 산정 (탄소) | executor | 탄소 배출 산정 시 GHG Protocol의 Scope 1/2/3 분류를 적용하라 | Scope 분류가 올바른지 확인 |
| 전문/specialized | Cap Rate/IRR | 투자 수익률 지표 (부동산/금융) | executor | 투자 분석 시 Cap Rate와 IRR을 산출하여 의사결정 기준으로 제시하라 | 수익률 계산의 입력값과 공식이 정확한지 확인 |
| 전문/specialized | IMRaD | 과학 논문 구조 | executor | 연구 보고서를 IMRaD(서론→방법→결과→논의) 구조로 작성하라 | IMRaD 4섹션이 모두 존재하는지 확인 |
| 전문/specialized | Georgia-Pacific | 상표 유사성 판단 기준 (지재권) | executor | 상표 분석 시 Georgia-Pacific 요소를 적용하라 | 분석에 해당 요소가 반영되어 있는지 확인 |

### 권장 (should) — 사용자 선택

| domain_type | 프레임워크 | 설명 | target_roles | process_rule |
|-------------|-----------|------|-------------|-------------|
| 콘텐츠/creative | 패턴 인터럽트 | 주의 환기 기법 | executor | 콘텐츠 도입부에 패턴 인터럽트(예상을 깨는 질문, 통계, 이야기)를 배치하라 |
| 콘텐츠/creative | 플랫폼별 규격 | 채널별 콘텐츠 최적화 | executor | 각 플랫폼(인스타 1080×1080, 유튜브 16:9, 블로그 2000자+)의 규격에 맞게 콘텐츠를 조정하라 |
| code | DDD | Domain-Driven Design | executor | 복잡한 비즈니스 로직은 DDD 패턴(엔티티, 밸류 오브젝트, 애그리거트, 리포지토리)으로 모델링하라 |
| code | 테스트 피라미드 | 단위→통합→E2E 비율 | executor | 테스트를 피라미드 구조(단위 70% : 통합 20% : E2E 10%)로 작성하라 |
| code | DORA 메트릭 | 배포 빈도, 리드타임, MTTR, 변경 실패율 | executor | CI/CD 설계 시 DORA 4대 메트릭을 측정 가능하도록 구성하라 |
| 데이터/data | Great Expectations | 데이터 품질 검증 프레임워크 | executor | 데이터 파이프라인에 Great Expectations 스타일의 기대값 검증을 포함하라 |
| 데이터/data | SHAP/LIME | ML 모델 해석성 도구 | executor | ML 모델 결과에 SHAP 또는 LIME 기반 해석을 제공하라 |
| 비즈니스/business | Porter's 5 Forces | 산업 경쟁 분석 | executor | 시장 분석에 Porter의 5가지 경쟁 요인을 포함하라 |
| 비즈니스/business | RICE | 우선순위 결정 프레임워크 | executor | 기능 우선순위를 RICE(도달 범위×영향×확신/노력)로 산정하라 |
| 비즈니스/business | OKR | 목표-핵심결과 프레임워크 | executor | 전략 목표를 OKR(목표 + 측정 가능한 핵심결과 3~5개)로 설정하라 |
| 교육/education | ADDIE | 학습 콘텐츠 개발 모델 | executor | 콘텐츠 개발 시 ADDIE(분석→설계→개발→구현→평가) 프로세스를 따르라 |
| 교육/education | 에빙하우스 간격 반복 | 망각 곡선 기반 복습 최적화 | executor | 오답 복습 주기를 에빙하우스 곡선 기반으로 설계하라 (1일→3일→7일→14일→30일) |
| 법률/legal | MQM | 번역 품질 평가 메트릭 | executor | 법률 번역 시 MQM 프레임워크로 정확성/유창성/용어를 평가하라 |
| 법률/legal | IPC/CPC 분류 | 특허 국제 분류 | executor | 특허 분석 시 IPC/CPC 분류 체계를 적용하라 |
| 라이프/lifestyle | ACSM 가이드라인 | 미국스포츠의학회 운동 권장 | executor | 운동 프로그램 설계 시 ACSM 가이드라인(유산소 150분/주, 근력 2회/주)을 기준으로 하라 |
| 라이프/lifestyle | Van Westendorp | 가격 민감도 분석 | executor | 가격 책정 시 Van Westendorp PSM(너무 싼/싼/비싼/너무 비싼 4점)으로 최적가를 도출하라 |
| 문서/document | PREP | 결론→이유→예시→결론 구조 | executor | 비즈니스 문서를 PREP(Point→Reason→Example→Point) 구조로 작성하라 |
| 문서/document | STAR | 상황→과제→행동→결과 | executor | 사례/경험 기술 시 STAR(Situation→Task→Action→Result) 구조를 사용하라 |
| 문서/document | MADR | 아키텍처 결정 기록 | executor | 주요 설계 결정을 MADR(제목/상태/맥락/결정/결과) 형식으로 기록하라 |
| 문서/document | SemVer | 시맨틱 버전 관리 | executor | 버전 번호를 SemVer(MAJOR.MINOR.PATCH) 규칙으로 관리하라 |
| 운영/operations | 4C 프레임워크 | 고객/비용/편의/커뮤니케이션 | executor | 마케팅/운영 분석 시 4C(Customer/Cost/Convenience/Communication)를 적용하라 |
| 운영/operations | NPS/CSAT | 고객 만족도 측정 | executor | 서비스 품질 측정에 NPS(추천 의향 0-10)와 CSAT(만족도 1-5)를 설계하라 |
| 전문/specialized | 분야별 보조 프레임워크 | 핵심 외 보완 방법론 | executor | 필수 프레임워크 적용 후, 분야별 보조 분석 도구(탄소: ISO 14064 인증, 투자: DCF/NPV, 논문: 체계적 문헌고찰, 지재권: Hilti 요소)를 권장 적용하라 |

## 2. domain_type 매칭 규칙

도메인 분류 키워드와 프레임워크 테이블의 `domain_type`을 매칭합니다:

| domain_type 값 | 매칭되는 테이블 domain_type |
|---------------|--------------------------|
| code | code |
| document | 문서/document |
| creative | 콘텐츠/creative |
| research | 데이터/data |
| business | 비즈니스/business |

추가 키워드 매칭 (domain_description에서 감지):
| 키워드 | 추가 매칭 |
|--------|----------|
| 교육, 학습, 시험, 강의, 튜터, 퀴즈 | 교육/education |
| 법률, 규정, 계약, 특허, 소송 | 법률/legal |
| 건강, 영양, 운동, 다이어트, 피트니스 | 라이프/lifestyle |
| 운영, 프로세스, 워크플로우, KPI | 운영/operations |
| 탄소, 투자, 논문, 상표 | 전문/specialized |

복합 도메인(예: code + 교육)이면 양쪽 프레임워크를 모두 적용합니다.

## 3. 사용자 질문 형식

Phase 1.5.1에서 권장 프레임워크 선택 시 다음 형식을 사용합니다:

```
📋 도메인 프레임워크 선택

필수 프레임워크 (자동 적용):
  ✓ {이름} — {설명}
  ✓ {이름} — {설명}

권장 프레임워크:
  [1] {이름} — {설명}
  [2] {이름} — {설명}
  ...

💡 Opus 추천: [{번호들}]
   이유: {도메인 분석 기반 추천 근거 2-3문장}

선택: [번호] [번호] ... 또는 [전부] [없음]
```

Opus 추천은 domain-analysis.json의 도메인 설명, 동사, 품질 우선순위를 분석하여 생성합니다.
`--skip-interview` 시: 권장 프레임워크를 전부 포함합니다 (기본값).

## 4. Phase 3 주입 규칙

### executor/specialist 에이전트 <Process> 삽입 위치

기존 <Process> 단계의 마지막 번호 + 1에 추가:

```
N. 도메인 프레임워크 적용 (필수):
   - {프레임워크명}: {process_rule}
N+1. 도메인 프레임워크 적용 (권장):
   - {프레임워크명}: {process_rule}
```

### reviewer 에이전트 <Quality_Gates> 삽입 위치

기존 <Quality_Gates> 항목 뒤에 추가:

```
- [필수] {프레임워크명} 준수: {quality_gate}. 미준수 시 FAIL.
- [권장] {프레임워크명}: {process_rule}. 미적용 시 경고.
```

### target_roles 매칭

- `executor` → 해당 팀의 모든 executor 역할 에이전트
- `specialist` → 도메인 전문가 에이전트 (예: topik-content-specialist)
- `reviewer` → 모든 reviewer 역할 에이전트 (code-reviewer, security-reviewer)
