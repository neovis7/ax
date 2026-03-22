# Phase 3: 에이전트 정의 생성

## 3.1 generation-log 초기화

`.omc/ax/generation-log.json` 생성:

```json
{
  "generated_files": [],
  "timestamp": "{현재 시각}",
  "domain": "{도메인 설명}"
}
```

## 3.2 골든 템플릿 로드 및 커스터마이즈

`.omc/ax/team-architecture.json`의 각 에이전트에 대해:

1. **템플릿 로드**:
   - `base_template_path`가 있으면 해당 파일 Read
   - 없으면 `.claude/skills/ax/templates/agent-skeleton.md` Read

2. **frontmatter 커스터마이즈**:
   - `name` → 도메인 맞춤 kebab-case 이름 (예: `content-generator`, `data-analyst`)
   - `description` → 도메인 맞춤 설명 (역할 + 언제 사용하는지 포함)
   - `model` → 유효한 모델 ID만 사용: `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5` (구 ID인 claude-sonnet-4-5, claude-opus-4-5 등은 사용 금지 — validate_project.py에서 FAIL 처리됨)
   - `tools` → 역할에 필요한 도구만 (executor: 전체, reviewer: Read/Grep/Glob만)
   - `role` → team-architecture에서 결정된 역할
   - `triggers` → 도메인 특화 키워드 (비어있으면 안 됨 — 최소 3개 키워드 포함)

3. **본문 커스터마이즈** (XML 태그 필수 — `## Role` 같은 마크다운 헤더 사용 금지):
   - `<Role>` → 도메인 특화 미션, 책임/비책임 범위
   - `<Success_Criteria>` → 도메인 특화 완료 조건
   - `<Constraints>` → 도메인 특화 제약사항
   - `<Process>` → 도메인 특화 워크플로우 단계
     + `.claude/skills/ax/templates/domain-patterns.md` 섹션 6 "도메인별 에이전트 프로세스 필수 단계"를 Read하고, 해당 도메인의 필수 단계를 <Process>에 반영
   - `<Anti_Patterns>` → domain-patterns.md 섹션 6의 도메인별 Anti_Patterns 힌트 적용
     + backend-developer에 반드시 포함: "req.json() 직접 사용 금지, JWT expiresIn 숫자 사용 금지(문자열 '15m' 형식 사용), 환경변수 폴백값 금지(예: process.env.JWT_SECRET || 'secret'), 유틸리티 인라인 중복 금지, Fisher-Yates 셔플 정확 구현(i > 0 조건), Prisma adapter 패턴 필수"
     + frontend-developer에 반드시 포함: "모든 API 데이터 접근에 ?. 필수, 배열 메서드 앞에 (data ?? []) 필수, useGet 이중 래핑 금지(useGet이 이미 ApiResponse.data를 추출함), 테스트 계정 자체 생성 금지(prisma/seed.ts에서 확인)"
   - `<Quality_Gates>` → 도메인 특화 품질 게이트 (검증 가능한 조건)
   - `<Collaboration>` → 선행/후행 에이전트 + 입출력 경로 명시
   - `<Tool_Usage>` → 허용된 도구별 사용 지침

4. **`<Examples>` 자동 생성** (M4):
   도메인 맞춤 Good/Bad 예시를 생성하여 에이전트 품질을 높입니다:
   ```xml
   <Examples>
     <Good>
       입력: {도메인 맞춤 작업 요청}
       출력: {올바른 행동 — 역할에 맞는 도구 사용, 적절한 위임}
     </Good>
     <Bad>
       입력: {도메인 맞춤 작업 요청}
       출력: {잘못된 행동 — 역할 범위 초과, 부적절한 도구 사용}
     </Bad>
   </Examples>
   ```
   각 에이전트에 최소 1개 Good + 1개 Bad 예시를 포함합니다.

## 3.3 충돌 처리

각 에이전트 파일 생성 전:
- `.claude/agents/{name}.md` 존재 여부 확인 (Glob)
- 이미 존재하면: 자동 덮어쓰기 (generation-log에 `"overwritten"` 기록)

## 3.4 파일 생성 및 로그

> **병렬 실행**: 에이전트 파일은 서로 독립적이므로 병렬 Write로 생성 가능합니다. generation-log 업데이트만 순차로.

각 에이전트를 `.claude/agents/{name}.md`에 Write.
생성할 때마다 `.omc/ax/generation-log.json`의 `generated_files` 배열에 파일 경로를 추가.

## 3.5 자동 후처리 + 출력 계약 검증

서브에이전트가 생성한 파일에서 반복 발생하는 문제를 자동 수정합니다. 사람이 수동 수정할 필요를 없앱니다.

**자동 후처리 (검증 전 실행):**
1. triggers 누락 → 에이전트 name/role에서 키워드 추출하여 자동 채움
2. 모델 ID 교정 → `claude-sonnet-4-5` → `claude-sonnet-4-6` 등 구 ID 일괄 교체
3. XML 태그 변환 → `## Role` 마크다운 헤더가 있으면 `<Role>` XML 태그로 변환

**출력 계약 검증 (후처리 후):**
- frontmatter에 name, description, model, role, triggers 필수 필드
- 본문에 `<Role>` 존재 (대체 태그 `<Instructions>`, `<Context>` 허용)
- model 값이 유효한 ID인지 확인
- 누락 항목이 있으면 해당 에이전트 파일만 재생성
