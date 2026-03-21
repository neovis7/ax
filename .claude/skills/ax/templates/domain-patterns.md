# 도메인-패턴 매핑 가이드

Phase 1에서 도메인 유형을 분류하고, Phase 2에서 패턴을 선택할 때 참조하는 가이드.

---

## 1. 도메인 분류기

사용자 입력에서 다음 키워드/특성으로 도메인 유형을 자동 분류합니다:

| 도메인 유형 | 키워드/특성 | Phase 1 동작 |
|------------|-------------|-------------|
| **code** | 개발, 코딩, 프론트엔드, 백엔드, API, 앱, SaaS, 풀스택, 마이크로서비스, CLI | 코드베이스 탐색 수행 |
| **document** | 프레젠테이션, 슬라이드, 보고서, 문서, 제안서, 매뉴얼, 가이드, 백서 | 코드 탐색 스킵, 콘텐츠 구조 분석 |
| **creative** | 디자인, 브랜딩, 콘텐츠, 마케팅, 영상, 일러스트, 포스터, 캠페인 | 코드 탐색 스킵, 시각적 결과 강조 |
| **research** | 리서치, 분석, 조사, 데이터 분석, 시장 조사, 논문, 통계 | 코드 탐색 스킵, 데이터 소스 탐색 |
| **business** | 경영, 전략, 기획, 운영, 프로세스, 워크플로우, 자동화 | 코드 탐색 스킵, 프로세스 분석 |

**다국어 키워드 매핑** (영어 입력 지원):

| 도메인 유형 | 영어 키워드 |
|------------|------------|
| **code** | develop, coding, frontend, backend, API, app, SaaS, fullstack, microservice, CLI, chatbot, bot |
| **document** | presentation, slides, report, manual, guide, whitepaper, documentation |
| **creative** | design, branding, marketing, landing page, campaign, poster, newsletter |
| **research** | research, analysis, survey, data analysis, market research, benchmark |
| **business** | management, strategy, planning, operations, workflow, automation |

**복합 도메인 타이브레이크 규칙**:

2개 이상 유형이 동시에 매칭될 때, 다음 우선순위로 주 도메인을 결정합니다:

1. **output_format 기준** (최우선):
   - 결과물이 실행 가능한 코드/앱 → `code` 우선
   - 결과물이 HTML/PDF 문서 → `document` 우선
   - 결과물이 시각 디자인물 → `creative` 우선
2. **핵심 동사 기준**:
   - "개발/구현/빌드" → `code`
   - "작성/문서화" → `document`
   - "디자인/제작" → `creative`
   - "분석/조사" → `research`
   - "기획/관리" → `business`
3. **동점 시**: 더 구체적인(하위 유형이 명확한) 도메인을 주 도메인으로 선택.

나머지 매칭된 유형은 `domain_type_secondary`에 기록.

---

## 2. 도메인별 골든 패턴

각 도메인 유형에 대해 가장 빈번하게 최적인 패턴 조합:

### code 도메인

| 하위 유형 | 권장 패턴 | 근거 |
|----------|----------|------|
| 풀스택 앱 (대규모) | 계층적 위임 + 생성-검증 | 프론트/백/인프라 팀 분리 + 코드 리뷰 |
| 풀스택 앱 (소규모) | 파이프라인 + 생성-검증 | 순차적 빌드 + 검증 |
| API/마이크로서비스 | 전문가 풀 + 생성-검증 | 엔드포인트별 전문가 + 테스트 검증 |
| CLI 도구 | 파이프라인 | 단순 순차 흐름 |
| 데이터 파이프라인 | 파이프라인 + 생성-검증 | ETL 순차 + 데이터 품질 검증 |
| 모바일 앱 | 계층적 위임 | UI/로직/네이티브 레이어 분리 |

### document 도메인

| 하위 유형 | 권장 패턴 | 근거 |
|----------|----------|------|
| 프레젠테이션/슬라이드 | 파이프라인 + 생성-검증 | 리서치→구조→빌드→리뷰 순차 |
| 기술 문서 | 감독자 | 동적 추가 조사, 교차 참조 |
| 제안서/보고서 | 파이프라인 + 생성-검증 | 단계적 구성 + 품질 검증 |
| 매뉴얼/가이드 | 팬아웃/팬인 | 챕터별 병렬 작성 → 통합 |

### creative 도메인

| 하위 유형 | 권장 패턴 | 근거 |
|----------|----------|------|
| 브랜딩/아이덴티티 | 생성-검증 | 반복적 생성 + 품질 검증 루프 |
| 콘텐츠 캠페인 | 팬아웃/팬인 + 생성-검증 | 채널별 병렬 + 품질 통제 |
| 디자인 시스템 | 파이프라인 | 토큰→컴포넌트→문서 순차 |
| 영상/멀티미디어 | 파이프라인 | 기획→촬영→편집→리뷰 순차 |

### research 도메인

| 하위 유형 | 권장 패턴 | 근거 |
|----------|----------|------|
| 시장 조사 | 감독자 | 동적 탐색, 추가 조사 빈번 |
| 데이터 분석 | 파이프라인 | 수집→정제→분석→시각화 순차 |
| 경쟁사 분석 | 팬아웃/팬인 | 경쟁사별 병렬 조사 → 비교 종합 |
| 학술 리서치 | 감독자 + 생성-검증 | 동적 탐색 + 인용 정확성 검증 |

### business 도메인

| 하위 유형 | 권장 패턴 | 근거 |
|----------|----------|------|
| 프로세스 자동화 | 전문가 풀 | 태스크 유형별 전문가 라우팅 |
| 전략 기획 | 감독자 | 동적 분석, 시나리오 탐색 |
| 프로젝트 관리 | 계층적 위임 | 워크스트림별 팀 리더 위임 |
| 고객 지원 | 전문가 풀 + 생성-검증 | 문의 유형 라우팅 + 응답 품질 검증 |

---

## 3. 도메인별 에이전트 프리셋

도메인 유형에 따라 기본적으로 포함되어야 할 에이전트 역할:

### 공통 (모든 도메인)
- executor (최소 1개)
- reviewer (최소 1개)
- visual-architect (haiku)
- visual-builder (sonnet)
- visual-qa (sonnet)

### code 도메인 추가 (하위 유형별 세분화)

**풀스택 앱**:
- `system-architect` (opus) — 시스템 설계, 기술 스택 선정
- `backend-developer` — 서버/API/DB 구현
- `frontend-developer` — UI/UX 구현
- `code-reviewer` — 코드 리뷰 + 보안 체크

**API/마이크로서비스**:
- `api-architect` — 엔드포인트 설계, 프로토콜
- `service-developer` — 서비스 구현
- `code-reviewer` — 코드 리뷰 + 보안 체크

**CLI 도구**:
- `cli-developer` — CLI 인터페이스 + 로직 구현
- `code-reviewer` — 코드 리뷰

**데이터 파이프라인**:
- `data-architect` — 스키마 설계, ETL 전략
- `pipeline-engineer` — 파이프라인 구현, 스케줄링
- `data-quality-checker` — 데이터 품질 규칙 검증

**DevOps/인프라**:
- `infra-architect` — 네트워크/컴퓨팅 토폴로지, IaC
- `pipeline-engineer` — CI/CD 파이프라인
- `security-hardener` — 보안 설정, 시크릿 관리

**모바일 앱**:
- `system-architect` (opus) — 아키텍처 (Clean/MVVM)
- `ui-developer` — UI 구현 (SwiftUI/Compose)
- `logic-developer` — 비즈니스 로직
- `code-reviewer` — 코드 리뷰

> 하위 유형 판별: Phase 1에서 `domain_sub_type` 필드로 결정. 키워드 기반:
> "풀스택/full-stack" → fullstack, "API/REST/GraphQL" → api, "CLI/커맨드라인" → cli,
> "ETL/파이프라인/Airflow/dbt" → data-pipeline, "Kubernetes/Terraform/CI/CD/Docker" → devops,
> "iOS/Android/모바일/KMP" → mobile

### document 도메인 추가
- `content-researcher` — 주제 리서치, 데이터 수집
- `content-writer` — 콘텐츠 구조화, 작성
- `content-reviewer` — 팩트체크, 일관성 검증

### creative 도메인 추가
- `creative-director` — 컨셉 방향, 스타일 가이드
- `asset-creator` — 그래픽, 일러스트, 이미지 생성

### research 도메인 추가
- `data-collector` — 데이터 수집, 소스 탐색
- `data-analyst` — 분석, 통계, 인사이트 추출
- `report-writer` — 분석 결과 문서화

### business 도메인 추가
- `process-analyst` — 프로세스 분석, 개선점 도출
- `strategy-advisor` — 전략 제안, 시나리오 분석

---

## 4. 도메인별 시각화 가이드

visual-architect가 도메인 유형에 따라 참조하는 시각 스타일 힌트:

| 도메인 | 색상 무드 | 레이아웃 스타일 | 차트 선호 |
|--------|----------|---------------|----------|
| code | 다크 + 네온 강조 | 터미널/IDE 느낌, 모노스페이스 | 트렌드라인, 비교바 |
| document | 전문적/절제 | 깔끔한 그리드, 넓은 여백 | 도넛, 비교바, 트렌드라인 |
| creative | 대담/실험적 | 비대칭, 벤토 그리드 | 픽토그램, 와플 |
| research | 데이터 중심 | 정보 밀도 높음, 대시보드 | 레이더, 트렌드라인, 게이지 |
| business | 신뢰/권위 | 구조적, 계층적 | 게이지, 비교바, 도넛 |

---

## 5. 비코드 도메인 Phase 1 동작

도메인 유형이 `code`가 아닌 경우 Phase 1.2(프로젝트 탐색)의 동작을 변경:

```
code 도메인:
  → Phase 1.2 정상 실행 (package.json, pyproject.toml 등 탐색)

non-code 도메인 (document, creative, research, business):
  → Phase 1.2 스킵
  → 대신 "콘텐츠 요구사항 분석" 수행:
    - 결과물 포맷 (HTML, PDF, PPT, 웹페이지)
    - 대상 독자 (경영진, 개발자, 일반 대중)
    - 톤앤매너 (전문적, 친근한, 학술적)
    - 참조 자료 유형 (웹 검색, 데이터 파일, API)
```

## 6. 도메인별 에이전트 프로세스 필수 단계

Phase 3에서 에이전트 `<Process>`를 커스터마이즈할 때,
도메인 유형에 따라 다음 단계를 **반드시** 포함합니다.

### code 도메인
- executor `<Process>`: "테스트 작성" 단계 필수
- executor `<Process>` (fullstack/api): "사용자 플로우 검증" 단계 필수
  - 구현 완료 후 `docs/user-flows.md`의 핵심 플로우를 실제 API 호출로 검증
  - 단위 테스트 커버리지와 별개로, 핵심 플로우의 end-to-end 동작을 확인
- executor `<Process>` (fullstack/api): "API 의도 확인" 단계 필수
  - `api-contracts.ts`의 `@intent` 주석과 실제 구현이 일치하는지 확인
  - 스키마 형태만 일치하고 행동 의도가 다르면 FAIL
- executor `<Process>` (fullstack/api + 인증): "세션 지속성 검증" 단계 필수
  - 로그인 → 보호된 페이지 접근 → 페이지 새로고침 → 세션 유지 확인
  - 토큰 저장 방식(localStorage/cookie/memory)과 복원 로직이 일관되는지 확인
- reviewer `<Process>`: "보안 체크(프롬프트 인젝션, API 키 노출)" 필수
- reviewer `<Process>` (fullstack/api): "컬럼명 일치 검증" 필수
  - DB 스키마 ↔ API 계약 ↔ 시드 스크립트 간 컬럼명이 일관되는지 확인
  - snake_case → camelCase 변환 외의 이름 차이는 FAIL
- `<Anti_Patterns>`:
  - "하드코딩 시크릿", "테스트 없는 커밋", "에러 무시"
  - "단위 테스트만으로 통합 검증 대체" — 97% 커버리지여도 핵심 플로우가 안 되면 무의미
  - "스키마 일치 = 기능 일치 착각" — Zod 스키마가 같아도 API 의도가 다르면 통합 실패
  - "DB/API/시드 간 컬럼명 불일치" — resource_type vs table_name, name vs title 등
  - "메모리 전용 토큰 + refresh 미구현" — 페이지 새로고침 시 세션 유실. 반드시 지속성 방식을 명시하고 양쪽(BE/FE) 구현 일치 확인
  - "백엔드 API만 구현, 프론트 UI 누락" — 백엔드에 CRUD가 있어도 프론트에 페이지/메뉴가 없으면 사용자가 접근 불가. 매트릭스 대조 필수
  - "hooks 정의만 하고 미사용(dead hook)" — useCreateUser를 정의했지만 어디서도 import하지 않으면 기능 미구현과 동일
  - "관리 UI 누락으로 시드/API 직접 호출 의존" — 퀴즈 세트처럼 관리 UI가 없어 시드로만 생성 가능한 엔티티는 운영 불가
  - "프론트-백엔드 API 경로 불일치" — hook이 POST /mark-reviewed를 호출하는데 백엔드는 PUT /review → 런타임 404

### document 도메인
- executor `<Process>`: "팩트체크 + 출처 명시" 단계 필수
- reviewer `<Process>`: "오탈자 검증 + 논리 흐름 확인" 필수
- `<Anti_Patterns>`: "출처 없는 통계", "텍스트 과밀(여백 30% 미만)", "연속 동일 레이아웃"

### creative 도메인
- executor `<Process>`: "AI 슬롭 체크(보라 그라디언트, Inter 폰트, 이모지 아이콘)" 단계 필수
- reviewer `<Process>`: "브랜드 일관성 + CTA 대비율" 필수
- `<Anti_Patterns>`: "보라색 그라디언트+흰 배경", "이모지 아이콘 대체", "시스템 폰트"

### research 도메인
- executor `<Process>`: "소스 신뢰도 평가(공식 > 학술 > 블로그)" 단계 필수
- reviewer `<Process>`: "인용 검증 + 데이터 최신성(2년 이내)" 필수
- `<Anti_Patterns>`: "블로그 우선 인용", "2년 이상 오래된 데이터", "출처 URL 누락"

### business 도메인
- executor `<Process>`: "이해관계자 영향 분석" 단계 필수
- reviewer `<Process>`: "실행 가능성 검증 + KPI 구체성" 필수
- `<Anti_Patterns>`: "모호한 KPI(빠르게→p99 <200ms)", "구체적 일정 없는 계획"
