# 외부 스킬 추천 카탈로그

Phase 2에서 도메인 유형에 따라 추천할 외부 스킬 목록.
ax가 자동으로 적합한 스킬을 추천하고, 자동 적용 티어 스킬은 Phase 7에서 에이전트 프롬프트에 주입합니다.

---

## 자동 적용 티어 (Auto-Apply Tier)

다음 조건에 따라 해당 스킬을 **자동으로** 적절한 에이전트 프롬프트에 주입합니다:

**디자인 스킬** → frontend-developer/homepage-builder 에이전트에 주입:
- `domain_type` = creative 또는 document + `output_format` = html
- `domain_sub_type` = fullstack (프론트엔드 UI 포함 풀스택 프로젝트)
- 인터뷰에서 사용자가 디자인 스킬 적용을 선택한 경우
- `--design none` 플래그가 **없을** 때

**오피스 스킬** → 도메인 실행 에이전트 (report-writer, slide-builder, data-analyst 등)에 주입:
- `output_format` ∈ {pptx, pdf, xlsx, docx}
- 해당 스킬이 `~/.claude/skills/omc-learned/`에 설치되어 있을 때

디자인 스킬 콘텐츠는 GitHub에서 fetch, 오피스 스킬 콘텐츠는 로컬 경로에서 Read하여 Phase 7 에이전트 프롬프트에 주입합니다.
`--design {skill-name}` 플래그로 명시적으로 다른 스킬을 선택할 수도 있습니다.
`--design none`으로 자동 적용을 비활성화할 수 있습니다.

| 스킬 | GitHub 콘텐츠 URL | 자동 적용 조건 | 티어 |
|------|-------------------|---------------|------|
| supanova-design | `https://raw.githubusercontent.com/uxjoseph/supanova-design-skill/main/taste-skill/SKILL.md` | creative+html (기본) | 자동 |
| deer-flow | `npx skills add bytedance/deer-flow` | document+presentation, 이미지 기반 PPTX (기본) | 자동 |
| frontend-design | Anthropic 공식 플러그인 | `--design frontend-design` 지정 시 | 수동 |
| pptx | `~/.claude/skills/omc-learned/pptx/` | output_format=pptx, 편집 가능한 코드 기반 PPTX | 자동 |
| pdf | `~/.claude/skills/omc-learned/pdf/` | output_format=pdf | 자동 |
| xlsx | `~/.claude/skills/omc-learned/xlsx/` | output_format=xlsx | 자동 |
| docx | `~/.claude/skills/omc-learned/docx/` | output_format=docx | 자동 |

---

## 웹/프론트엔드/디자인 (creative, document 도메인에서 HTML 출력 시)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| supanova-design | `https://github.com/uxjoseph/supanova-design-skill` | UI 중심 구현의 핵심 디자인 스킬 — 시각 품질 최우선 (자동 적용 티어) |
| frontend-design | `claude plugins add anthropics/claude-code/plugins/frontend-design` | Anthropic 공식 프론트엔드 디자인 |
| impeccable | `npx skills add pbakaus/impeccable` | UI 완성도 향상 |
| taste-skill | `claude plugins add Leonxlnx/taste-skill` | 디자인 감각/미적 판단 |
| ui-design-brain | `claude plugins add carmahhawwari/ui-design-brain` | UI 디자인 의사결정 |
| ui-ux-pro-max | `claude plugins add nextlevelbuilder/ui-ux-pro-max-skill` | UI/UX 종합 스킬 |
| designer-skills | `claude plugins add Owl-Listener/designer-skills` | 디자이너 스킬 |
| ui-skills | `npx skills add ibelick/ui-skills` | UI 스킬 모음 |
| design-plugin | `claude plugins add 0xdesign/design-plugin` | 디자인 플러그인 |
| superdesign | `claude plugins add superdesigndev/superdesign` | 슈퍼디자인 |
| make-interfaces-feel-better | `claude plugins add jakubkrehel/make-interfaces-feel-better` | 인터페이스 개선 |

## 프레젠테이션/슬라이드 (document 도메인, 발표 자료)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| deer-flow | `npx skills add bytedance/deer-flow` | AI 이미지 기반 PPT 생성 파이프라인 — 편집 불가 이미지 슬라이드 (자동 적용 티어) |
| pptx | `~/.claude/skills/omc-learned/pptx/` | 코드 기반 PPT 생성/편집/읽기 — 편집 가능한 텍스트/도형 슬라이드 (deer-flow와 **충돌**, 택 1) |

> **deer-flow vs pptx 선택 기준:**
> - 비주얼 퀄리티 최우선, 편집 불필요 → deer-flow (Gemini 이미지 생성)
> - 편집 가능한 슬라이드, 템플릿 활용, 기존 .pptx 수정 → pptx (pptxgenjs/python-pptx)

## 문서/오피스 (output_format 기반, 도메인 무관)

| 스킬 | 로컬 경로 | 용도 |
|------|----------|------|
| pptx | `~/.claude/skills/omc-learned/pptx/` | .pptx 생성/편집/읽기 (pptxgenjs, python-pptx, markitdown) |
| pdf | `~/.claude/skills/omc-learned/pdf/` | .pdf 생성/편집/읽기/폼 채우기/OCR (pypdf, pdfplumber, reportlab) |
| xlsx | `~/.claude/skills/omc-learned/xlsx/` | .xlsx/.csv/.tsv 생성/편집/읽기 (openpyxl, pandas, LibreOffice recalc) |
| docx | `~/.claude/skills/omc-learned/docx/` | .docx 생성/편집/읽기/트랙 변경 (python-docx, pandoc) |

## 아이콘/에셋 (시각화가 필요한 모든 도메인)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| better-icons | `claude plugins add better-auth/better-icons` | 아이콘 스킬 |

## 종합/에이전트 (code 도메인, 대규모 프로젝트)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| agent-skills | `claude plugins add vercel-labs/agent-skills` | Vercel 에이전트 스킬 |

---

## visual-architect 추가 제약 (Tailwind v4 프로젝트)

CSS 커스텀 변수 이름은 Tailwind v4 내장 변수와 충돌 금지:

```
금지 접두사: --spacing-*, --color-*, --font-*, --text-*, --shadow-*, --radius-*, --container-*
안전한 접두사: --app-*, --brand-*, --ds-*, 프로젝트명 접두사 (--fda-* 등)
```

Tailwind v4 프로젝트 감지: `tailwind.config.ts` 또는 `@import "tailwindcss"` 패턴 존재 시 자동 적용.
visual-architect 에이전트 프롬프트에 위 블랙리스트를 제약사항으로 주입합니다.

---

## 스킬 역할 분류

각 스킬의 역할을 이해해야 올바른 조합이 가능합니다:

| 역할 | 설명 | 해당 스킬 |
|------|------|----------|
| **디자인 엔진** | 전체 디자인 철학/원칙을 지배. 프로젝트당 1개만 활성화 | supanova-design, frontend-design |
| **품질 강화** | 디자인 엔진 위에 세부 품질 규칙 추가. 엔진과 함께 사용 | impeccable, taste-skill, make-interfaces-feel-better |
| **의사결정** | UI/UX 설계 판단 기준 제공. 설계 단계에 영향 | ui-design-brain, ui-ux-pro-max |
| **컴포넌트** | 구체적 UI 컴포넌트/패턴 라이브러리 제공 | ui-skills, designer-skills, design-plugin, superdesign |
| **에셋** | 아이콘, 이미지 등 시각 에셋 활용 | better-icons |
| **프레젠테이션** | PPT/슬라이드 생성. 프로젝트당 1개만 활성화 (deer-flow ⊗ pptx 충돌). document+presentation 컨텍스트에서만 충돌 적용 | deer-flow (이미지 기반), pptx (코드 기반) |
| **파일 포맷** | 네이티브 오피스 파일 생성/편집/읽기 도구. output_format에 의해 활성화. 비프레젠테이션 컨텍스트에서는 프레젠테이션 역할과 독립 | pptx, pdf, xlsx, docx |
| **인프라** | 개발 도구, 에이전트 워크플로우 | agent-skills |

---

## 스킬 시너지/충돌 매트릭스

### 충돌 관계 (동시 사용 금지)

```
supanova-design ⊗ frontend-design
  → 둘 다 "디자인 엔진" 역할. 폰트/컬러/레이아웃 원칙이 서로 다름.
  → supanova: Pretendard 필수, 비대칭 레이아웃, glass UI
  → frontend-design: 프레임워크 기본 폰트, 표준 그리드
  → 해결: --design 플래그로 하나만 선택

ui-ux-pro-max ⊗ ui-design-brain
  → 둘 다 "의사결정" 역할. UI 판단 기준이 중복되어 모순 가능.
  → 해결: 프로젝트 복잡도에 따라 하나만 선택
    (단순 → ui-design-brain, 복잡 → ui-ux-pro-max)

deer-flow ⊗ pptx
  → 둘 다 "프레젠테이션 생성" 역할. 생성 방식이 근본적으로 다름.
  → deer-flow: AI 이미지 기반 — 슬라이드 전체가 이미지, 편집 불가
  → pptx: 코드 기반 (pptxgenjs) — 편집 가능한 텍스트/도형 슬라이드
  → deer-flow 출력물(.pptx)을 pptx 스킬로 편집하는 것은 불가능 (이미지이므로)
  → 해결: 프로젝트 요구에 따라 하나만 선택
    (비주얼 퀄리티 우선 → deer-flow, 편집 가능성 우선 → pptx)
```

### 시너지 관계 (함께 사용 시 효과 증폭)

```
supanova-design + impeccable
  → supanova가 디자인 철학을, impeccable이 세부 완성도를 담당
  → 시너지: 대담한 디자인 + 꼼꼼한 마감

supanova-design + taste-skill
  → supanova가 구현 규칙을, taste가 미적 판단을 보완
  → 시너지: 규칙 기반 구현 + 감성적 검증

supanova-design + better-icons
  → supanova의 디자인 시스템 내에서 better-icons가 에셋 활용을 강화
  → 시너지: 일관된 디자인 + 풍부한 아이콘

frontend-design + agent-skills
  → Anthropic 디자인 + Vercel 인프라
  → 시너지: 공식 디자인 가이드 + 프로덕션 에이전트 패턴

any 디자인 엔진 + make-interfaces-feel-better
  → 인터페이스 감성 개선이 어떤 디자인 엔진과도 호환
  → 시너지: 구조적 디자인 + 촉감적 개선 (마이크로 인터랙션)
```

### 중립 관계 (독립적, 자유 조합)

```
better-icons ↔ 모든 디자인 스킬 (에셋 역할이라 충돌 없음)
agent-skills ↔ 모든 디자인 스킬 (인프라 역할이라 충돌 없음)
designer-skills ↔ ui-skills (컴포넌트 카테고리 내 보완 관계)
pptx ↔ pdf ↔ xlsx ↔ docx (파일 포맷이 다르므로 충돌 없음, 자유 조합)
pptx/pdf/xlsx/docx ↔ 모든 디자인 스킬 (파일 포맷 역할이라 충돌 없음)
```

---

## 프로젝트 유형별 추천 레시피

### 레시피 1: 프리미엄 랜딩 페이지 / 홈페이지
```
필수: supanova-design (자동 적용)
권장: + impeccable + better-icons
선택: + taste-skill (미적 판단 강화)
효과: $150k 에이전시급 시각 품질 + 꼼꼼한 마감 + 풍부한 아이콘
적용: creative 도메인, output_format=html
```

### 레시피 2: 풀스택 웹앱 (SaaS, 대시보드)
```
필수: frontend-design (표준 UI) 또는 supanova-design (프리미엄 UI)
권장: + agent-skills + ui-skills
선택: + ui-design-brain (복잡한 UI 의사결정)
효과: 일관된 컴포넌트 + Vercel 인프라 최적화
적용: code 도메인, domain_sub_type=fullstack
```

### 레시피 3: 프레젠테이션 / 슬라이드
```
필수: deer-flow 또는 pptx 중 택 1 (충돌 관계)
  deer-flow: AI 이미지 기반, 비주얼 퀄리티 최우선, 편집 불가 → Gemini API 키 필요
  pptx:      코드 기반, 편집 가능, 템플릿 활용, 기존 파일 수정 가능 → pptxgenjs/python-pptx
권장: + supanova-design (프리미엄 비주얼, deer-flow 선택 시) + better-icons
선택: + make-interfaces-feel-better (전환 효과)
효과: 콘텐츠 구조화 + 시각 품질 + 풍부한 아이콘
적용: document 도메인, domain_sub_type=presentation (output_format 무관 — deer-flow vs pptx 선택 기준으로 분기)
선택 기준: deer-flow 설치 + Gemini API 키 존재 → deer-flow 기본 / 미설치 → pptx 폴백
```

### 레시피 4: 데이터 대시보드 / 분석 도구
```
필수: frontend-design (데이터 가독성 우선)
권장: + better-icons + ui-skills
선택: + impeccable (차트/테이블 완성도)
효과: 깔끔한 데이터 표현 + 직관적 네비게이션
적용: code 도메인, domain_sub_type=fullstack, quality_priority=accuracy
```

### 레시피 5: API / CLI / 백엔드 전용
```
필수: 없음 (프론트엔드 UI 없음)
권장: agent-skills (대규모 프로젝트 시)
선택: 없음
효과: 불필요한 디자인 스킬 배제로 컨텍스트 절약
적용: code 도메인, domain_sub_type=api|cli|data-pipeline
```

### 레시피 6: 마케팅 / 브랜딩 콘텐츠
```
필수: supanova-design (자동 적용)
권장: + taste-skill + impeccable
선택: + make-interfaces-feel-better
효과: 브랜드 정체성 강조 + 감성적 디자인 + 마이크로 인터랙션
적용: creative 도메인, output_format=html
```

### 레시피 7: 오피스 문서 생성
```
필수: output_format에 따라 자동 선택 (로컬 경로에서 Read)
  pptx → pptx 스킬 (~/.claude/skills/omc-learned/pptx/)
  pdf  → pdf 스킬 (~/.claude/skills/omc-learned/pdf/)
  xlsx → xlsx 스킬 (~/.claude/skills/omc-learned/xlsx/)
  docx → docx 스킬 (~/.claude/skills/omc-learned/docx/)
권장: 없음 (파일 포맷 도구이므로 디자인 스킬 불필요)
선택: 없음
효과: 네이티브 오피스 파일 직접 생성/편집/읽기
적용: output_format ∈ {pptx, pdf, xlsx, docx} (도메인 무관)
주의: document+presentation에서 pptx 사용 시 deer-flow와 충돌 — 하나만 선택
      스킬 콘텐츠는 office-skill-context.md에 저장 (design-skill-context.md와 별도)
```

---

## 도메인별 추천 규칙

### creative 도메인 (랜딩 페이지, 브랜딩 등)
추천 레시피: 레시피 1 (프리미엄 랜딩) 또는 레시피 6 (마케팅)
추천 우선순위: supanova-design > impeccable > taste-skill > better-icons > make-interfaces-feel-better
최소 추천: 2개 (디자인 엔진 1 + 품질 강화 1)

### document 도메인
추천 레시피:
  - domain_sub_type=presentation → 레시피 3 (deer-flow 또는 pptx 택 1)
  - output_format ∈ {pptx,pdf,xlsx,docx} → 레시피 7 (오피스 문서)
  - output_format=html → 레시피 3 변형 (supanova-design)
추천 우선순위 (프레젠테이션): deer-flow(기본) 또는 pptx(폴백) > supanova-design > better-icons
추천 우선순위 (오피스 문서): 해당 포맷 스킬 1개 (디자인 스킬 불필요)
최소 추천: 1개
참고: deer-flow와 pptx는 충돌 관계 — 동시 활성화 금지

### code 도메인 (프론트엔드 포함 시)
추천 레시피: 레시피 2 (풀스택) 또는 레시피 4 (대시보드)
추천 우선순위: frontend-design > agent-skills > ui-skills > impeccable
최소 추천: 1개 (디자인 엔진 또는 인프라)
주의: domain_sub_type=api|cli|data-pipeline이면 디자인 스킬 추천하지 않음

### research / business 도메인
추천: better-icons (차트/다이어그램 아이콘 용)
최소 추천: 0개 (선택적)

---

## 우선순위 규칙 (충돌 해결)

여러 스킬이 동시에 활성화될 때의 우선순위:

### 1. 디자인 엔진 충돌
```
--design {name} 명시 지정 → 해당 스킬만 활성화, 다른 디자인 엔진 무시
--design 미지정 (auto) → 도메인 기본값 사용:
  creative+html → supanova-design
  code+fullstack → frontend-design
  document+html → supanova-design
```

### 2. 동일 역할 충돌
```
의사결정 역할 충돌 (ui-design-brain vs ui-ux-pro-max):
  → domain_sub_type=fullstack 이상 복잡도 → ui-ux-pro-max 우선
  → 단순 페이지/컴포넌트 → ui-design-brain 우선

컴포넌트 역할 중복 (ui-skills vs designer-skills vs design-plugin):
  → 모두 설치되어도 충돌 없음 (보완 관계)
  → 단, 컨텍스트 절약을 위해 최대 2개 권장
```

### 3. 프롬프트 주입 우선순위 (Phase 7)
```
에이전트 프롬프트에 주입할 때의 순서:
  1순위: 디자인 엔진 (supanova/frontend-design) — 전체 원칙
  2순위: 품질 강화 (impeccable/taste-skill) — 세부 규칙
  3순위: 에셋 (better-icons) — 리소스 활용

주입 대상 에이전트:
  homepage-builder/frontend-developer → 디자인 엔진 전체 + 품질 강화
  visual-architect → 디자인 엔진의 컬러/폰트/레이아웃 규칙만
  visual-qa → 디자인 엔진의 안티패턴 체크리스트 + 품질 강화의 검증 기준
```

---

## 설치 후 활용 가이드

### ax 자동 적용 스킬 (설치 불필요)
```
supanova-design:
  → ax가 GitHub에서 자동 fetch → .omc/ax/design-skill-context.md에 저장
  → Phase 7에서 에이전트 프롬프트에 자동 주입
  → 사용자 액션 없음 (--design none으로 비활성화 가능)
```

### 수동 설치 스킬 (설치 후 자동 감지)
```
설치 방법:
  claude plugins add {repo}  또는  npx skills add {repo}

설치 후 동작:
  1. ax Phase 2.4에서 다음 경로를 Glob으로 스킬 설치 여부 자동 감지:
     - Glob(".claude/plugins/")  — 플러그인으로 설치된 스킬
     - Glob("~/.claude/skills/omc-learned/*/SKILL.md")  — 수동 설치된 Anthropic 공식 스킬
  2. 이미 설치된 스킬은 추천 목록에서 제외
  3. 설치된 스킬은 Claude Code가 자동으로 활성화 (별도 설정 불필요)
  4. 스킬의 SKILL.md에 정의된 트리거 조건에 따라 자동 실행

확인 방법:
  claude plugins list  → 플러그인 설치 스킬 확인
  ls ~/.claude/skills/omc-learned/  → 수동 설치 스킬 확인
```

### 스킬 비활성화
```
전체 비활성화:
  /ax --design none "프로젝트 설명"  → 디자인 스킬 자동 적용 안 함

개별 비활성화:
  claude plugins remove {skill-name}  → 특정 스킬 제거

일시적 비활성화:
  .claude/settings.json의 disabledPlugins에 스킬명 추가
```

---

## 추천 프로세스

Phase 2.4 스킬 갭 분석 후:

1. `domain_type`, `output_format`, `domain_sub_type`을 확인
2. 위 "프로젝트 유형별 추천 레시피"에서 적합한 레시피 선택
3. 레시피의 필수/권장/선택 스킬 목록 생성
4. 이미 설치된 스킬은 제외 (Glob으로 `.claude/plugins/` + `~/.claude/skills/omc-learned/*/SKILL.md` 확인)
5. 충돌 매트릭스 확인 — 충돌 스킬은 하나만 추천 (특히 deer-flow ⊗ pptx)
6. **자동 적용 티어 확인**:
   - 디자인 스킬: 자동 적용 조건 충족 시, GitHub URL에서 SKILL.md를 WebFetch → `design-skill-context.md`에 저장
   - 오피스 스킬: output_format ∈ {pptx,pdf,xlsx,docx} 시, 로컬 경로에서 Read → `office-skill-context.md`에 저장
7. Phase 7에서 대상 에이전트에 주입:
   - design-skill-context.md → 시각 관련 에이전트 (homepage-builder, visual-architect, visual-qa)
   - office-skill-context.md → 도메인 실행 에이전트 (report-writer, slide-builder, data-analyst 등)
8. 완료 보고에 다음을 포함:
   - 적용된 레시피명
   - 자동 적용된 디자인/오피스 스킬명
   - 추가 설치 추천 스킬 (설치 명령어 포함)
   - 충돌로 비활성화된 스킬 (deer-flow/pptx 중 선택되지 않은 쪽 등)

## 자동 적용 흐름 (Phase 2.4.1 → Phase 7)

```
Phase 2.4.1:
  1) 프로젝트 유형 → 추천 레시피 매칭
  2) 디자인 엔진 결정:
     --design {name} → 해당 스킬
     --design none → 스킵
     --design 없음 (auto):
       creative+html → supanova-design
       code+fullstack → frontend-design
       document+html → supanova-design
       그 외 → 스킵
  3) 디자인 엔진의 GitHub SKILL.md를 WebFetch
     → .omc/ax/design-skill-context.md에 저장
  4) 오피스 스킬 결정 (output_format 기반):
     output_format ∈ {pptx,pdf,xlsx,docx} →
       해당 스킬의 SKILL.md를 로컬 Read (~/.claude/skills/omc-learned/{format}/SKILL.md)
       → .omc/ax/office-skill-context.md에 저장
     document+presentation → deer-flow 또는 pptx 중 택 1 (충돌 매트릭스 참조)
       deer-flow 설치 + Gemini API 키 → deer-flow 기본
       deer-flow 미설치 → pptx 폴백
  5) 추천 레시피의 권장/선택 스킬 → 완료 보고에 포함

Phase 7:
  .omc/ax/design-skill-context.md 존재 시:
  → homepage-builder 에이전트: 디자인 원칙 전체 주입
  → visual-architect 에이전트: 컬러/폰트/레이아웃 규칙 주입
  → visual-qa 에이전트: 안티패턴 체크리스트 주입
  주입 순서: 디자인 엔진 → 품질 강화 → 에셋 (우선순위 규칙 참조)

  .omc/ax/office-skill-context.md 존재 시:
  → 도메인 실행 에이전트: "도구 참조" 섹션으로 주입
  → visual-architect/visual-qa에는 주입하지 않음
  → design-skill-context.md와 독립 (둘 다 존재 가능)
```
