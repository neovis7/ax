### 1.7 도메인 리서치 (조건부)

> **적용 조건**: 다음 중 하나 이상 충족 시 자동 실행
> - `quality_criticality` = `high`
> - `quality_priority` = `accuracy`
> - 도메인 설명에 규제(FDA, GxP, SOX, HIPAA), 의료, 법률, 금융, 안전 키워드 포함
> - `--execute` 모드이고 콘텐츠 생성이 필요한 도메인

실제 구현/콘텐츠 생성 전에 도메인 전문 지식을 수집하여, 에이전트가 정확한 정보를 기반으로 작업하도록 합니다.

**절차:**

1. **리서치 에이전트 디스패치**: `document-specialist` 에이전트를 사용하여 도메인 핵심 지식 수집
   - 규제 원문, 가이던스 문서, 업계 표준
   - 실사/감사 위반 사례, 흔한 지적 사항
   - 모범 사례, 실무 시나리오
   - 자주 오해되는 개념 (오답 선택지/Anti-Pattern 소재)

2. **지식 베이스 저장**: `${PROJECT_DIR}/docs/research/{domain}-knowledge-base.md`에 구조화된 형태로 저장
   ```markdown
   ## 섹션명
   ### 핵심 개념
   ### 자주 출제되는 포인트
   ### 실무 시나리오
   ### 흔한 오해
   ```

3. **에이전트 프롬프트 연동**: Phase 3(에이전트 생성) 시 콘텐츠 생성 에이전트의 `<Process>`에 다음을 삽입:
   - "작업 전 `docs/research/{domain}-knowledge-base.md`를 반드시 Read하라"
   - "지식 베이스에 없는 내용은 추가 리서치 후 사용하라"

4. **domain-analysis.json 업데이트**:
   ```json
   {
     "research": {
       "enabled": true,
       "knowledge_base": "docs/research/{domain}-knowledge-base.md",
       "topics": ["{리서치 주제 목록}"]
     }
   }
   ```
