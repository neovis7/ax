# 외부 스킬 추천 카탈로그

Phase 2에서 도메인 유형에 따라 추천할 외부 스킬 목록.
ax가 자동으로 적합한 스킬을 추천하고, 자동 적용 티어 스킬은 Phase 7에서 에이전트 프롬프트에 주입합니다.

---

## 자동 적용 티어 (Auto-Apply Tier)

다음 조건이 모두 충족되면 해당 스킬의 핵심 원칙을 **자동으로** homepage-builder 에이전트 프롬프트에 주입합니다:
- `domain_type` = creative 또는 document
- `output_format` = html
- `--design none` 플래그가 **없을** 때

자동 적용 스킬의 콘텐츠는 GitHub에서 fetch하여 Phase 7 에이전트 프롬프트에 주입합니다.
`--design {skill-name}` 플래그로 명시적으로 다른 스킬을 선택할 수도 있습니다.
`--design none`으로 자동 적용을 비활성화할 수 있습니다.

| 스킬 | GitHub 콘텐츠 URL | 자동 적용 조건 | 티어 |
|------|-------------------|---------------|------|
| supanova-design | `https://raw.githubusercontent.com/uxjoseph/supanova-design-skill/main/taste-skill/SKILL.md` | creative+html (기본) | 자동 |
| frontend-design | Anthropic 공식 플러그인 | `--design frontend-design` 지정 시 | 수동 |

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

## 아이콘/에셋 (시각화가 필요한 모든 도메인)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| better-icons | `claude plugins add better-auth/better-icons` | 아이콘 스킬 |

## 종합/에이전트 (code 도메인, 대규모 프로젝트)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
| agent-skills | `claude plugins add vercel-labs/agent-skills` | Vercel 에이전트 스킬 |

---

## 도메인별 추천 규칙

### creative 도메인 (랜딩 페이지, 브랜딩 등)
추천 우선순위: supanova-design > frontend-design > impeccable > ui-ux-pro-max > taste-skill
최소 추천: 2개

### document 도메인 (HTML 출력 시)
추천 우선순위: supanova-design > frontend-design > design-plugin > make-interfaces-feel-better
최소 추천: 1개

### code 도메인 (프론트엔드 포함 시)
추천 우선순위: supanova-design > frontend-design > agent-skills > ui-skills
최소 추천: 1개

### research / business 도메인
추천: better-icons (차트/다이어그램 아이콘 용)
최소 추천: 0개 (선택적)

---

## 추천 프로세스

Phase 2.4 스킬 갭 분석 후:

1. `domain_type`과 `output_format`을 확인
2. 위 추천 규칙에 따라 적합한 외부 스킬 목록 생성
3. 이미 설치된 스킬은 제외 (Glob으로 확인)
4. **자동 적용 티어 확인**: 자동 적용 조건 충족 시, 해당 스킬의 GitHub URL에서 SKILL.md를 WebFetch
5. fetch된 디자인 스킬 콘텐츠를 `${PROJECT_DIR}/.omc/ax/design-skill-context.md`에 저장
6. Phase 7에서 homepage-builder 에이전트 프롬프트에 디자인 스킬 콘텐츠를 주입
7. 완료 보고에 적용된 디자인 스킬명과 추천 목록을 포함

## 자동 적용 흐름 (Phase 2.4.1 → Phase 7)

```
Phase 2.4.1:
  domain_type=creative && output_format=html?
    → YES + --design 없음 → supanova-design 자동 선택
    → YES + --design {name} → 해당 스킬 선택
    → YES + --design none → 스킵
    → NO → 스킵

  선택된 스킬의 GitHub SKILL.md를 WebFetch
  → .omc/ax/design-skill-context.md에 저장

Phase 7:
  .omc/ax/design-skill-context.md 존재 시
  → homepage-builder 에이전트 프롬프트에 "## Design Skill Context" 섹션으로 주입
  → visual-architect 에이전트에도 컬러/폰트 규칙 주입
```
