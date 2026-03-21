# 외부 스킬 추천 카탈로그

Phase 2에서 도메인 유형에 따라 추천할 외부 스킬 목록.
ax가 자동으로 적합한 스킬을 추천하고, 사용자가 선택하면 설치합니다.

---

## 웹/프론트엔드/디자인 (creative, document 도메인에서 HTML 출력 시)

| 스킬 | 설치 방법 | 용도 |
|------|----------|------|
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
추천 우선순위: frontend-design > impeccable > ui-ux-pro-max > taste-skill
최소 추천: 2개

### document 도메인 (HTML 출력 시)
추천 우선순위: frontend-design > design-plugin > make-interfaces-feel-better
최소 추천: 1개

### code 도메인 (프론트엔드 포함 시)
추천 우선순위: frontend-design > agent-skills > ui-skills
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
4. 사용자에게 추천 목록 제시: "다음 외부 스킬을 설치하면 결과물 품질이 향상됩니다"
5. 사용자가 선택하면 설치 명령 실행
6. 건너뛰기도 가능 (외부 스킬 없이도 기본 기능으로 동작)
