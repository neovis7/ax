# 도메인 프레임워크 자동 주입 설계

> **날짜**: 2026-03-28
> **범위**: Phase 1 + Phase 3 + 신규 참조 파일
> **목적**: 도메인별 업계 표준 프레임워크를 에이전트에 자동 주입하여 전문가 수준 산출물 보장

## 배경

현재 ax 파이프라인은 도메인 유형(code, document, creative 등)을 감지하지만, 해당 도메인의 업계 표준 프레임워크/방법론은 활용하지 않습니다. 교육 프로젝트에서 Bloom's Taxonomy 없이, 개발 프로젝트에서 OWASP Top 10 없이 에이전트가 작업하면 "그럴듯하지만 얕은" 결과물이 됩니다.

## 프레임워크 매핑

### 필수 (must) — 자동 포함, 질문 없음

| 도메인 | 필수 프레임워크 |
|--------|---------------|
| 콘텐츠 | AIDA, SEO 키워드 매핑 |
| 개발 | SOLID, OWASP Top 10 |
| 데이터 | Star/Snowflake 스키마 |
| 비즈니스 | BMC, TAM/SAM/SOM |
| 교육 | Bloom's Taxonomy, CEFR |
| 법률 | IRAC, GDPR/PIPA |
| 라이프 | BMR/TDEE, KDRIs |
| 문서 | Diataxis |
| 운영 | SIPOC/RACI, SMART |
| 전문 | 분야별 핵심 1개 (GHG Protocol / Cap Rate·IRR / IMRaD / Georgia-Pacific) |

### 권장 (should) — 사용자에게 질문 후 선택

| 도메인 | 권장 프레임워크 |
|--------|---------------|
| 콘텐츠 | 패턴 인터럽트, 플랫폼별 규격 |
| 개발 | DDD, 테스트 피라미드, DORA 메트릭 |
| 데이터 | Great Expectations, SHAP/LIME |
| 비즈니스 | Porter's 5 Forces, RICE, OKR |
| 교육 | ADDIE, 에빙하우스 간격 반복 |
| 법률 | MQM, IPC/CPC 분류 |
| 라이프 | ACSM 가이드라인, Van Westendorp |
| 문서 | PREP, STAR, MADR, SemVer |
| 운영 | 4C 프레임워크, NPS/CSAT |
| 전문 | 분야별 나머지 |

## 흐름

```
Phase 1.2: domain_type 감지 (기존)
  ↓
Phase 1.5: references/domain-frameworks.md 조건부 Read
  → domain_type으로 필수 프레임워크 자동 선택
  → 권장 프레임워크 목록 추출
  ↓
Phase 1.5.1: 권장 프레임워크 사용자 질문 (1회)
  → Opus 모델로 도메인 분석 결과 기반 추천 생성
  → 추천 이유와 함께 다중선택 질문 표시
  → 사용자 선택 반영
  → --skip-interview 시: 권장 전부 포함 (기본값)
  ↓
Phase 1.5.2: domain-analysis.json에 frameworks 필드 저장
  ↓
Phase 3.2: 에이전트 커스터마이즈 시
  → executor: <Process>에 프레임워크 적용 단계 삽입
  → reviewer: <Quality_Gates>에 필수 프레임워크 준수 검증 조건 삽입
  ↓
Phase 6.4: ARCHITECTURE.md에 "적용된 프레임워크" 섹션 추가
Phase 6.6: 완료 보고에 프레임워크 목록 포함
```

## 사용자 질문 형식 (Phase 1.5.1)

```
📋 도메인 프레임워크 선택

필수 프레임워크 (자동 적용):
  ✓ Bloom's Taxonomy — 학습 목표 난이도 6단계 설계
  ✓ CEFR — 국제 언어 능력 등급 기준

권장 프레임워크:
  [1] ADDIE — 학습 콘텐츠 개발 프로세스 (분석→설계→개발→구현→평가)
  [2] 에빙하우스 간격 반복 — 복습 주기 최적화로 장기 기억 강화

💡 Opus 추천: [1, 2] 전부 적용
   이유: TOPIK은 장기 학습이 필요한 시험이므로 ADDIE로 체계적 콘텐츠를
   설계하고, 에빙하우스로 오답 복습 주기를 최적화하면 학습 효과가 극대화됩니다.

선택: [1] [2] [3=전부] [4=없음]
```

## domain-analysis.json 확장

```json
{
  "frameworks": {
    "must": [
      {
        "name": "Bloom's Taxonomy",
        "description": "학습 목표 난이도 6단계 설계",
        "injection": {
          "target_roles": ["specialist", "executor"],
          "process_rule": "문제/콘텐츠 난이도를 Bloom의 6단계(기억→이해→적용→분석→평가→창조)로 태깅하라",
          "quality_gate": "모든 학습 콘텐츠에 Bloom 단계가 명시되어 있는지 확인"
        }
      }
    ],
    "should": [
      {
        "name": "에빙하우스 간격 반복",
        "description": "복습 주기 최적화로 장기 기억 강화",
        "selected": true,
        "injection": {
          "target_roles": ["executor"],
          "process_rule": "오답 복습 주기를 에빙하우스 곡선 기반으로 설계하라 (1일→3일→7일→14일→30일)",
          "quality_gate": null
        }
      }
    ]
  }
}
```

## Phase 3 에이전트 주입 규칙

### executor 에이전트 <Process>에 삽입

```xml
<Process>
  ...기존 단계...
  N. 도메인 프레임워크 적용 (필수):
     - Bloom's Taxonomy: 문제/콘텐츠 난이도를 6단계로 태깅하라
     - CEFR: TOPIK 등급을 CEFR 레벨과 매핑하여 국제 기준으로 표현하라
  N+1. 도메인 프레임워크 적용 (권장):
     - ADDIE: 콘텐츠 개발 시 분석→설계→개발→구현→평가 프로세스를 따르라
     - 에빙하우스 간격 반복: 오답 복습 주기를 1일→3일→7일→14일→30일로 설계하라
</Process>
```

### reviewer 에이전트 <Quality_Gates>에 삽입

```xml
<Quality_Gates>
  ...기존 게이트...
  - [필수] Bloom's Taxonomy 준수: 모든 학습 콘텐츠에 인지 수준 단계가 태깅되어 있는지 확인. 미태깅 시 FAIL.
  - [필수] CEFR 매핑: 등급별 콘텐츠가 대응하는 CEFR 레벨과 일치하는지 확인. 불일치 시 FAIL.
  - [권장] ADDIE 프로세스: 콘텐츠가 체계적 개발 프로세스를 거쳤는지 확인. 미준수 시 경고.
</Quality_Gates>
```

## 가시성 (적용 표시)

1. **domain-analysis.json**: `frameworks.must` + `frameworks.should` 필드
2. **ARCHITECTURE.md**: "적용된 프레임워크" 섹션 (이름, 설명, 적용 대상 에이전트)
3. **Phase 6.6 완료 보고**: 프레임워크 목록 + 필수/권장 구분 표시

## 변경 파일 목록

| 파일 | 변경 유형 |
|------|----------|
| `references/domain-frameworks.md` | 신규 생성 |
| `phases/phase-1-analysis.md` | 수정 (1.5 뒤에 1.5.1~1.5.2 추가) |
| `phases/phase-3-agents.md` | 수정 (3.2에 프레임워크 주입 규칙 추가) |
| `SKILL.md` | 수정 (조건부 참조 로드에 domain-frameworks.md 추가) |
