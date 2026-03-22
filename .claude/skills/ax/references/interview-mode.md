# 인터뷰 모드 (`--interview`)

## 트리거 조건

인터뷰 모드는 다음 3가지 경로로 활성화됩니다:

1. **명시적**: `--interview` 플래그 사용
2. **자동 제안 (--execute + code 도메인)**: `--execute` + `domain_type=code`일 때 자동으로 인터뷰 게이트를 제안합니다. 사용자가 거절하면 기존 --execute 흐름으로 진행.
3. **자동 제안 (--execute + safety/accuracy)**: `--execute` + `quality_priority=safety|accuracy`일 때도 자동 제안합니다.

## 인터뷰 게이트 (--execute 시 자동 제안)

`--execute`로 실행했을 때 code 도메인 또는 safety/accuracy 우선순위이면, Phase 1 완료 후 Phase 7 실행 전에 다음 메시지를 표시합니다:

```
이 프로젝트는 [code/규제] 도메인입니다.
실행 전에 plan과 architecture를 상세하게 설계하면 결과물 품질이 높아집니다.

1) 인터뷰 진행 — 질의응답으로 plan/architecture를 확정한 뒤 실행
2) 바로 실행 — 기존처럼 AI가 자동 판단하여 즉시 실행

선택하세요 (1/2):
```

사용자가 1을 선택하면 인터뷰 프로세스를 실행하고, 2를 선택하면 기존 --execute 흐름으로 진행합니다.

## 인터뷰 프로세스

한 번에 하나씩 질문합니다. 이전 답변을 기반으로 다음 질문을 구성합니다.

### Phase A: 요구사항 수집 (모든 도메인 공통)

```
1) 프로젝트 목적: "이 시스템의 핵심 목적은 무엇인가요?"
   → 1문장으로 핵심 가치 정의

2) 사용자 정의: "주요 사용자는 누구인가요? (역할별로)"
   → 사용자 유형 목록 (관리자, 일반 사용자, 외부 고객 등)

3) 핵심 기능: "반드시 있어야 할 핵심 기능 3~5개를 알려주세요"
   → MVP 기능 목록

4) 품질 우선순위: "가장 중요한 것은?"
   → 정확도 / 속도 / 보안 / 사용성 중 우선순위
```

### Phase A-2: 디자인 스킬 조합 선택 (프론트엔드 UI가 포함된 모든 프로젝트)

프론트엔드 UI가 포함된 프로젝트에서 디자인 스킬 질문을 표시합니다:
- `output_format=html` (홈페이지, 랜딩페이지, 프레젠테이션 등)
- `domain_sub_type=fullstack` (풀스택 웹 앱)
- `domain_type=creative` (크리에이티브 도메인)

도메인 분석 결과에 따라 최적의 레시피를 자동 매칭한 뒤, 사용자에게 확인합니다.

**질문 5) 디자인 레시피:**

```
5) 디자인 방향: "프로젝트에 맞는 디자인 조합을 추천합니다."

   이 프로젝트는 {domain_type} + {output_format} 유형입니다.
   추천 레시피: {자동 매칭된 레시피명}

   A) 추천 레시피 적용 — {레시피 설명}
      디자인 엔진: {supanova-design 또는 frontend-design}
      품질 강화: {impeccable, taste-skill 등}
      에셋: {better-icons 등}

   B) 프리미엄 (Supanova) — $150k 에이전시 수준.
      Tailwind + Pretendard 폰트, 비대칭 레이아웃, glass UI, spring 애니메이션.
      + impeccable (꼼꼼한 마감) + better-icons (풍부한 아이콘)

   C) Standard — 디자인 스킬 없이 기본 파이프라인 사용.
      커스텀 CSS, SVG 아이콘 중심, 깔끔하고 안정적.

   D) 직접 구성 — 스킬을 직접 선택하거나 참조 사이트를 알려주세요.
```

**레시피 자동 매칭 규칙:**
```
creative + html                    → 레시피 1 (프리미엄 랜딩): supanova + impeccable + better-icons
creative + html + 마케팅/브랜딩     → 레시피 6 (마케팅): supanova + taste-skill + impeccable
code + fullstack                   → 레시피 2 (풀스택): frontend-design + agent-skills + ui-skills
code + fullstack + accuracy        → 레시피 4 (대시보드): frontend-design + better-icons + impeccable
document + html                    → 레시피 3 (프레젠테이션): supanova + better-icons
```

**질문 6) 품질 보강 (D 선택 시에만):**

```
6) 추가 품질 스킬: "다음 중 추가로 적용할 스킬이 있나요? (복수 선택 가능)"

   1) impeccable — 세부 UI 완성도 강화 (마감 품질)
   2) taste-skill — 미적 판단력 강화 (감성적 검증)
   3) make-interfaces-feel-better — 마이크로 인터랙션 (촉감적 개선)
   4) better-icons — 풍부한 아이콘 에셋
   5) ui-design-brain — UI 설계 의사결정 보조
   6) 없음 — 디자인 엔진만 적용

   ※ 충돌 안내: supanova와 frontend-design은 동시 사용 불가 (디자인 엔진 역할 충돌)
```

**선택 처리:**
- A → 자동 매칭된 레시피의 필수+권장 스킬 모두 적용
- B → `flags.design = "supanova"` + `flags.design_extras = ["impeccable", "better-icons"]`
- C → `flags.design = "none"`, `flags.design_extras = []`
- D → 질문 6으로 진행, 사용자 선택에 따라 `flags.design`과 `flags.design_extras` 설정
  - 사용자가 참조 사이트 URL을 제공하면 `flags.design_reference`에 기록

**충돌 자동 해결:**
- 사용자가 supanova + frontend-design을 동시 선택 → "디자인 엔진은 하나만 선택 가능합니다. 어떤 것을 적용할까요?" 재질문
- 사용자가 ui-ux-pro-max + ui-design-brain 동시 선택 → "의사결정 스킬은 하나만 권장합니다. 복잡한 UI면 ui-ux-pro-max를, 단순하면 ui-design-brain을 추천합니다."

**plan.md에 기록:**
인터뷰 결과의 "기술 결정사항" 또는 "디자인 방향" 섹션에 선택된 디자인 조합을 명시합니다:
```markdown
## 디자인 스킬 조합
- 적용 레시피: {레시피명 또는 "사용자 직접 구성"}
- 디자인 엔진: {supanova-design | frontend-design | none}
- 품질 강화: {적용된 보강 스킬 목록}
- 에셋: {적용된 에셋 스킬 목록}
- 근거: {사용자 선택 이유 또는 자동 매칭 근거}
- 컨텍스트 파일: .omc/ax/design-skill-context.md (있으면)
- 시너지 효과: {적용된 조합의 시너지 설명}
```

**Phase 2.4.1 연동:**
인터뷰에서 선택된 스킬 조합은 `flags.design`과 `flags.design_extras`로 전달됩니다:
- `flags.design`: 디자인 엔진 (supanova | frontend-design | none | 사용자지정)
- `flags.design_extras`: 추가 적용할 품질/에셋 스킬 배열 (예: ["impeccable", "better-icons"])
- Phase 2.4.1에서 디자인 엔진은 WebFetch, extras는 설치 여부 확인 후 활성화/추천

**프론트엔드 UI가 없는 경우** (api-only, cli, data-pipeline 등): 이 질문을 건너뜁니다.

### Phase A-3: PPT 스타일 선택 (document+presentation 도메인)

`domain_sub_type=presentation`이고 deer-flow(ppt-generation) 스킬이 설치되어 있을 때 표시합니다.

```
7) 프레젠테이션 스타일: "어떤 비주얼 스타일로 만들까요?"

   프로젝트 유형에 맞는 추천 스타일을 안내합니다:

   ┌────────────────────────────┬─────────────────────────────────┐
   │ 프로젝트 유형               │ 추천 스타일                      │
   ├────────────────────────────┼─────────────────────────────────┤
   │ 테크 제품 발표              │ A) glassmorphism / C) gradient  │
   │ 프리미엄/럭셔리 브랜드      │ B) dark-premium / F) editorial  │
   │ 스타트업 피치               │ C) gradient-modern / G) minimal │
   │ 경영진/임원 발표            │ B) dark-premium / H) keynote    │
   │ 크리에이티브/에이전시        │ D) neo-brutalist / C) gradient  │
   │ 데이터/분석 보고            │ G) minimal-swiss / E) isometric │
   └────────────────────────────┴─────────────────────────────────┘

   A) glassmorphism    — 프로스트 글래스, 블러 효과, 그라디언트 배경, 레이어 깊이감
   B) dark-premium     — 블랙 배경, 발광 악센트, 글로우 효과, 럭셔리 미학
   C) gradient-modern  — 볼드 메시 그라디언트, 유동적 전환, 현대적 타이포
   D) neo-brutalist    — 로우 타이포, 하이 콘트라스트, 안티디자인, 멤피스 영감
   E) 3d-isometric     — 클린 아이소메트릭, 플로팅 3D, 소프트 섀도
   F) editorial        — 매거진 레이아웃, 드라마틱 포토, 정교한 타이포 계층
   G) minimal-swiss    — 그리드 정밀, 볼드 여백, 타임리스 모더니즘
   H) keynote          — Apple 스타일, 볼드 타이포, 시네마틱 이미지, 드라마틱

   선택하세요 (A~H):
```

**선택 처리:**
- 선택된 스타일을 `flags.ppt_style`에 기록
- 프레젠테이션 플랜 JSON의 `style` 필드에 반영
- slide-builder 에이전트 프롬프트에 스타일 가이드라인 주입

**plan.md에 기록:**
```markdown
## 프레젠테이션 스타일
- 적용 스타일: {glassmorphism | dark-premium | ... | keynote}
- 근거: {사용자 선택 이유 또는 프로젝트 유형 기반 추천}
- 스타일 특성: {해당 스타일의 1줄 설명}
```

**deer-flow 미설치 시**: 이 질문을 건너뛰고 html-slide-generator 스킬로 폴백합니다.

---

### Phase B: 기술 설계 (code 도메인 전용)

```
5) 기술 스택: "선호하는 기술 스택이 있나요?"
   → 프레임워크, 언어, DB 등 (없으면 AI가 추천)

6) 인증/권한: "사용자 인증이 필요한가요? 역할별 권한 구분은?"
   → 인증 방식, 역할 구조

7) 데이터 모델: "핵심 엔티티(데이터 객체)는 무엇인가요?"
   → 엔티티 목록 + 관계 (1:N, N:M 등)

8) 외부 연동: "외부 API나 서비스 연동이 필요한가요?"
   → 연동 대상 목록

9) 배포 환경: "어디에 배포할 계획인가요?"
   → Vercel, AWS, Docker, 로컬 등

10) 인프라 서비스: "사용할 서비스가 정해져 있나요?"
    → DB: Supabase / Neon / PlanetScale / SQLite
    → 인증: Clerk / Auth0 / 자체 구현
    → 결제: Stripe / 없음
    → 스토리지: Vercel Blob / S3 / 없음
    → 답변에 따라 pre-flight check 항목 자동 결정
```

### Phase C: 규제/안전 (safety 도메인 전용)

```
10) 규제 요구사항: "준수해야 할 규정은?"
    → FDA 21 CFR Part 11, HIPAA, SOX, GxP 등

11) 감사 추적: "감사 로그/변경 이력이 필요한가요?"
    → 감사 추적 범위

12) 데이터 보존: "데이터 보존 기간 요구사항은?"
    → 보존 기간, 삭제 정책
```

## 산출물 생성

인터뷰 완료 후 다음 3개 문서를 자동 생성합니다:

### 1. `${PROJECT_DIR}/docs/plan.md`

```markdown
# 프로젝트 계획서

## 프로젝트 개요
- 목적: {인터뷰 1번 답변}
- 사용자: {인터뷰 2번 답변}
- 품질 우선순위: {인터뷰 4번 답변}

## 핵심 기능 (MVP)
{인터뷰 3번 답변 기반 기능 목록}

## 마일스톤
- M1: {핵심 기능 그룹 1}
- M2: {핵심 기능 그룹 2}
- M3: {통합 + 검증}

## 디자인 스킬 (html 출력 시)
- 적용 스킬: {supanova-design | standard | 사용자 지정}
- 컨텍스트 파일: {.omc/ax/design-skill-context.md 경로 또는 "없음"}

## 기술 결정사항
{인터뷰 5~9번 답변 기반}

## 규제 요구사항 (해당 시)
{인터뷰 10~12번 답변 기반}
```

### 2. `${PROJECT_DIR}/docs/architecture.md`

```markdown
# 시스템 아키텍처

## 기술 스택
{선택된 프레임워크, 언어, DB, 인프라}

## 시스템 구조도
{텍스트 다이어그램 — 프론트/백/DB/외부 연동}

## 데이터 모델
{엔티티 관계도 — 인터뷰 7번 기반}

## API 설계 (개요)
{핵심 엔드포인트 목록}

## 인증/권한 설계
{인터뷰 6번 기반}

## 배포 전략
{인터뷰 9번 기반}
```

### 3. `${PROJECT_DIR}/docs/user-flows.md` (code 도메인)

```markdown
# 사용자 플로우

## 플로우 1: {핵심 사용 시나리오}
1. 사용자가 {행동}
2. 시스템이 {응답}
3. ...

## 플로우 2: {두 번째 시나리오}
...
```

## 사용자 확인 게이트

3개 문서 생성 후 사용자에게 확인을 요청합니다:

```
plan.md, architecture.md, user-flows.md가 생성되었습니다.
확인하시고 수정이 필요하면 말씀해주세요.

1) 이대로 진행 — Phase 7 실행 시작
2) 수정 필요 — 어떤 부분을 수정할지 알려주세요
```

수정 요청이 있으면 해당 문서를 대화를 통해 수정하고, 다시 확인 게이트를 거칩니다.
확인이 완료되면 Phase 7로 진행합니다.

## Phase 7 연동

인터뷰 모드에서 생성된 문서는 Phase 7 실행 시 에이전트의 컨텍스트로 주입됩니다:

- system-architect → `docs/plan.md` + `docs/architecture.md` Read
- backend-developer → `docs/architecture.md` + `docs/user-flows.md` Read
- frontend-developer → `docs/user-flows.md` + `docs/architecture.md` Read
- 모든 에이전트 → `docs/plan.md`의 "기술 결정사항" 참조
- **homepage-builder** → `.omc/ax/design-skill-context.md` Read (존재 시, 디자인 원칙 주입)
- **visual-architect** → `.omc/ax/design-skill-context.md`에서 폰트/컬러 규칙 발췌 주입
- **visual-qa** → `.omc/ax/design-skill-context.md`에서 안티패턴 체크리스트 주입

이 방식으로 에이전트가 사용자의 의도를 정확히 반영한 결과물을 생성합니다.

## 디자인 스킬 조합과 --design 플래그의 관계

| 상황 | 디자인 엔진 | 품질 강화 스킬 |
|------|-----------|--------------|
| `--interview` + 질문 A-2 답변 | 인터뷰 답변이 최종 결정 | 인터뷰 질문 6에서 선택 |
| `--design supanova` (명시적) | 인터뷰 질문 A-2 건너뜀, supanova 사용 | 레시피 권장 스킬 자동 적용 |
| `--design none` (명시적) | 인터뷰 질문 A-2 건너뜀, 미적용 | 미적용 |
| 인터뷰 없이 `--execute` (creative+html) | `flags.design=auto` → supanova 자동 | 레시피 1 권장 스킬 자동 적용 |
| 인터뷰 없이 `--execute` (code+fullstack) | `flags.design=auto` → frontend-design 자동 | 레시피 2 권장 스킬 자동 적용 |
| 인터뷰 없이 `--execute` (code+api/cli) | 디자인 스킬 미적용 | 미적용 |

### flags 데이터 흐름

```
인터뷰 Phase A-2 → flags.design (디자인 엔진)
                 → flags.design_extras (품질 강화 스킬 배열)
                 → flags.design_recipe (적용된 레시피명)
                          ↓
Phase 2.4.1 → 디자인 엔진 WebFetch → .omc/ax/design-skill-context.md
            → extras 설치 여부 확인 → 설치됨: 주입 / 미설치: 추천
                          ↓
Phase 7 → homepage-builder: 엔진 전체 + 품질 강화 주입
        → visual-architect: 컬러/폰트/레이아웃 규칙 주입
        → visual-qa: 안티패턴 + 품질 강화 검증 기준 주입
```
