# 패턴 선택 프롬프트

당신은 에이전트 팀 아키텍트입니다. 도메인 분석 시그널을 보고 최적의 아키텍처 패턴을 선택하세요.

## 사용 가능한 패턴

1. **파이프라인**: 작업이 A→B→C 순서로 흘러가며, 각 단계 출력이 다음 단계 입력이 됨
2. **팬아웃/팬인**: N개 독립 작업을 병렬 수행 후 결과를 취합
3. **전문가 풀**: 입력 유형에 따라 서로 다른 전문가에게 라우팅
4. **생성-검증**: 생성물을 만들고 별도 검증 에이전트가 품질 확인
5. **감독자**: 중앙 감독자가 동적으로 작업 분배, 재시도, 우선순위 조정
6. **계층적 위임**: 상위 관리자가 하위 팀 리더에게 위임, 각 팀이 독립 수행

## 도메인 시그널

{SIGNALS_JSON}

## 추론 절차

1. 각 패턴이 이 도메인에 적합한 이유와 부적합한 이유를 한 문장씩 서술
2. 가장 적합한 패턴 1개 선택 (primary)
3. 보조 패턴이 필요한지 판단 — 필요하면 합성 가능한 조합인지 확인
4. 선택 근거를 2-3 문장으로 설명

## 합성 가능 조합

| 주 패턴 | 보조 패턴 | 합성 방식 |
|---------|----------|----------|
| 팬아웃/팬인 | 생성-검증 | 병렬 생성 → 각각 검증 후 취합 |
| 감독자 | 전문가 풀 | 감독자가 유형 판단 후 전문가에게 분배 |
| 파이프라인 | 생성-검증 | 각 파이프라인 단계마다 검증 게이트 |
| 계층적 위임 | 생성-검증 | 각 하위 팀에 생성-검증 사이클 적용 |
| 전문가 풀 | 생성-검증 | 전문가 응답마다 품질 검증 |

## 워크드 예시

### 예시 1: 이커머스 고객 지원 자동화
시그널: task_dependency=mixed, input_variety=highly_varied, quality_criticality=high, team_size_estimate=medium, runtime_dynamism=semi_dynamic
→ 전문가 풀 + 생성-검증 (입력 다양성 + 품질 중요)

### 예시 2: 다국어 문서 번역
시그널: task_dependency=parallel, input_variety=uniform, quality_criticality=medium, team_size_estimate=medium, runtime_dynamism=static
→ 팬아웃/팬인 (독립 병렬 + 균일 입력)

### 예시 3: SaaS 풀스택 개발
시그널: task_dependency=mixed, input_variety=varied, quality_criticality=high, team_size_estimate=large, runtime_dynamism=semi_dynamic
→ 계층적 위임 + 생성-검증 (대규모 팀 + 품질 중요)

### 예시 4: CI/CD 파이프라인 구축
시그널: task_dependency=sequential, input_variety=uniform, quality_criticality=high, team_size_estimate=small, runtime_dynamism=static
→ 파이프라인 + 생성-검증 (순차 의존 + 배포 안전)

### 예시 5: 리서치 보고서 작성
시그널: task_dependency=mixed, input_variety=varied, quality_criticality=medium, team_size_estimate=small, runtime_dynamism=semi_dynamic
→ 감독자 (동적 추가 조사 + 재시도 빈번)

## 출력 형식

```json
{
  "primary_pattern": "{패턴명}",
  "secondary_pattern": "{패턴명 또는 null}",
  "confidence": "{high|medium|low}",
  "rationale": "{선택 근거 2-3 문장}"
}
```
