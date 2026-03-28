# AX 팀 예제 레퍼런스

> Phase 2 아키텍처 패턴 선택 시 참고하는 실전 예제 모음.
> 각 예제는 팀 아키텍처, 에이전트 구성, 오케스트레이터 워크플로우, 에이전트 정의 전문을 포함한다.

---

## 예시 1: 리서치 팀 (에이전트 팀 모드)

### 팀 아키텍처: 팬아웃/팬인
### 실행 모드: 에이전트 팀

```
[리더/오케스트레이터]
    ├── TeamCreate(research-team)
    ├── TaskCreate(4개 조사 작업)
    ├── 팀원들이 자체 조율 (SendMessage)
    ├── 결과 수집 (Read)
    └── 종합 보고서 생성
```

### 에이전트 구성

| 팀원 | 에이전트 타입 | 역할 | 스킬 | 출력 |
|------|-------------|------|------|------|
| official-researcher | general-purpose | 공식 문서/블로그 조사 | WebSearch, Read | research_official.md |
| media-researcher | general-purpose | 미디어/투자 동향 조사 | WebSearch, Read | research_media.md |
| community-researcher | general-purpose | 커뮤니티/SNS 반응 조사 | WebSearch, Read | research_community.md |
| background-researcher | general-purpose | 배경/경쟁/학술 조사 | WebSearch, Read | research_background.md |
| (리더 = 오케스트레이터) | — | 통합 보고서 생성 | Read, Write | 종합보고서.md |

> 리서치 에이전트는 `general-purpose` 빌트인 타입을 사용하되, 반드시 `${PROJECT_DIR}/.claude/agents/{name}.md` 파일로 정의한다.
> 파일에는 역할·조사 범위·팀 통신 프로토콜을 명시하여 재사용성과 협업 품질을 보장한다.

### 오케스트레이터 워크플로우 (에이전트 팀)

```
Phase 1: 준비
  - 사용자 입력 분석 (주제, 조사 모드 파악)
  - _workspace/ 디렉토리 생성

Phase 2: 팀 구성
  - TeamCreate(team_name: "research-team", members: [
      { name: "official",   prompt: "공식 채널 조사..." },
      { name: "media",      prompt: "미디어/투자 동향 조사..." },
      { name: "community",  prompt: "커뮤니티 반응 조사..." },
      { name: "background", prompt: "배경/경쟁 환경 조사..." }
    ])
  - TaskCreate(tasks: [
      { title: "공식 채널 조사",   assignee: "official"   },
      { title: "미디어 동향 조사", assignee: "media"      },
      { title: "커뮤니티 반응 조사", assignee: "community" },
      { title: "배경 환경 조사",   assignee: "background" }
    ])

Phase 3: 조사 수행
  - 4명의 팀원이 독립적으로 조사 수행
  - 흥미로운 발견이 있으면 팀원 간 SendMessage로 공유
    (예: media가 발견한 투자 뉴스를 background에게 전달)
  - 상충 정보 발견 시 팀원 간 직접 토론
  - 각 팀원은 완료 시 파일 저장 + TaskUpdate로 완료 보고

Phase 4: 통합
  - 리더가 4개 산출물 Read
  - 종합 보고서 생성
  - 상충 정보는 출처 병기

Phase 5: 정리
  - TeamDelete로 팀 정리
  - _workspace/ 보존 (사후 검증·감사 추적용)
```

### 팀 통신 패턴

```
official ──SendMessage──→ background  (관련 공식 발표 공유)
media ────SendMessage──→ background  (투자/인수 정보 공유)
community ─SendMessage──→ media      (커뮤니티 반응 중 미디어 관련 정보)
모든 팀원 ──TaskUpdate──→ 공유 작업 목록  (진행률 업데이트)
리더 ←───── 완료 알림 ──── 완료된 팀원   (TaskUpdate 트리거)
```

### 에이전트 정의 파일 전문 예시: `official-researcher.md`

```markdown
---
name: official-researcher
description: "공식 채널(홈페이지, 블로그, 보도자료)을 조사하는 리서치 전문가. 리서치 팀에서 공식 정보 담당."
model: claude-sonnet-4-6
tools: WebSearch, Read, Write
role: executor
triggers: 공식 채널, 공식 문서, 블로그, 보도자료, official
---

# Official Researcher — 공식 채널 조사 전문가

<Role>
  공식 채널(공식 홈페이지, 기술 블로그, 보도자료, IR 자료)에서 신뢰 가능한 정보를 수집합니다.
  - 책임: 공식 발표 수집, 기술 문서 요약, 공식 통계·수치 확인
  - 비책임: 미디어/SNS 반응 분석(media-researcher), 경쟁 분석(background-researcher)
</Role>

<Success_Criteria>
  - 공식 출처 URL 명시 (모든 사실에 링크 포함)
  - 발표일 기준으로 최신 정보 우선
  - _workspace/research_official.md에 구조화된 보고서 저장
</Success_Criteria>

<Constraints>
  - 공식 채널이 아닌 2차 출처는 "[비공식]" 태그 부착
  - 추측이나 해석을 사실로 기술 금지
  - 단순 링크 목록이 아닌 요약 포함 필수
</Constraints>

<Process>
  1) 조사 주제 파악 — _workspace/brief.md Read
  2) WebSearch로 공식 홈페이지·블로그·보도자료 탐색
  3) 핵심 발표 내용 Read 및 요약
  4) 수치·통계 확인 (공식 IR, 실적 발표)
  5) _workspace/research_official.md 저장
  6) 주목할 발견이 있으면 background-researcher에게 SendMessage
  7) TaskUpdate로 완료 보고
</Process>

<Anti_Patterns>
  - URL 없이 "공식 자료에 따르면..." 기술
  - 공식 채널 범위를 벗어난 커뮤니티 분석 수행
  - 조사 결과 없이 추정으로 보고서 작성
</Anti_Patterns>

<Quality_Gates>
  - 모든 사실 주장에 출처 URL 포함
  - 보고서에 조사 일시 명시
  - _workspace/research_official.md 저장 완료
</Quality_Gates>

<Collaboration>
  선행: 오케스트레이터 (주제 브리핑 제공)
  후행: 오케스트레이터 (종합 보고서 통합)
  SendMessage 대상: background-researcher (공식 발표 중 경쟁·배경 관련 정보)
  입력: _workspace/brief.md
  출력: _workspace/research_official.md
</Collaboration>

<Examples>
  <Good>
    입력: "OpenAI GPT-5 출시 관련 공식 정보 조사"
    출력: openai.com 블로그 발표문 요약, 공식 API 문서 링크, 가격 정책 공식 페이지 참조.
          background-researcher에게 "GPT-5 기업 파트너십 발표 있음, 경쟁 분석에 반영 요망" SendMessage.
  </Good>
  <Bad>
    입력: "OpenAI GPT-5 출시 관련 공식 정보 조사"
    출력: Reddit 스레드와 트위터 반응을 "공식 채널" 자료로 포함. 출처 URL 없음.
  </Bad>
</Examples>
```

### 에러 핸들링

```
- 공식 사이트 접근 불가 → 캐시된 버전(web.archive.org) 시도 후 "[접근 불가]" 태그
- 정보가 상충하는 공식 발표 → 두 버전 모두 기재, 날짜 기준 최신 우선
- 조사 결과 없음 → "정보 없음" 명시, 리더에게 알림
```

---

## 예시 2: SF 소설 집필 팀 (에이전트 팀 모드)

### 팀 아키텍처: 파이프라인 + 팬아웃
### 실행 모드: 에이전트 팀

```
Phase 1 (병렬 — 에이전트 팀): worldbuilder + character-designer + plot-architect
  → 서로 SendMessage로 일관성 조율
  → worldbuilder가 사회 구조 완성 시 character-designer에게 SendMessage
  → character-designer가 주인공 설정 시 plot-architect에게 SendMessage

Phase 2 (순차): prose-stylist (집필)
  → Phase 1 팀 정리 후 서브 에이전트로 단독 호출

Phase 3 (병렬 — 에이전트 팀): science-consultant + continuity-manager (리뷰)
  → 서로 발견을 공유 (SendMessage)
  → 팀 정리

Phase 4 (순차): prose-stylist (리뷰 반영 수정)
```

### 에이전트 구성

| 팀원 | 에이전트 타입 | 역할 | 스킬 | 출력 |
|------|-------------|------|------|------|
| worldbuilder | 커스텀 | 세계관 구축 | Read, Write | 01_worldbuilder_setting.md |
| character-designer | 커스텀 | 캐릭터 설계 | Read, Write | 01_character_profiles.md |
| plot-architect | 커스텀 | 플롯 구조 | Read, Write | 01_plot_outline.md |
| prose-stylist | 커스텀 | 집필 + 수정 | Read, Write | 02_prose_draft.md |
| science-consultant | 커스텀 | 과학 검증 | Read, Grep | 03_science_review.md |
| continuity-manager | 커스텀 | 일관성 검증 | Read, Grep | 03_continuity_review.md |

### 팀 워크플로우 상세

```
Phase 1: TeamCreate(team_name: "creation-team", members: [worldbuilder, character-designer, plot-architect])
         TaskCreate([세계관 구축, 캐릭터 설계, 플롯 구조])
         → 팀원들이 자체 조율하며 병렬 작업
         → worldbuilder가 사회 구조 완성 시 character-designer에게 SendMessage
         → character-designer가 주인공 설정 시 plot-architect에게 SendMessage
         → 모두 완료 → TeamDelete

Phase 2: prose-stylist를 서브 에이전트로 호출 (단독 집필이므로 팀 불필요)
         _workspace/의 3개 산출물을 Read하여 집필
         → _workspace/02_prose_draft.md 저장

Phase 3: TeamCreate(team_name: "review-team", members: [science-consultant, continuity-manager])
         (Phase 1 팀을 정리했으므로 새 팀 생성 가능 — 세션당 한 팀만 활성)
         → 두 리뷰어가 draft를 검토, 서로 발견을 공유
         → science-consultant가 물리 오류 발견 시 continuity-manager에게도 알림
         → 리뷰 완료 후 TeamDelete

Phase 4: prose-stylist를 서브 에이전트로 재호출, 리뷰 결과 반영하여 최종 수정
```

### 에이전트 정의 파일 전문 예시: `worldbuilder.md`

```markdown
---
name: worldbuilder
description: "SF 소설의 세계관을 구축하는 전문가. 물리 법칙, 사회 구조, 기술 수준, 역사를 설계한다."
model: claude-opus-4-6
tools: Read, Write
role: executor
triggers: 세계관, 설정, SF 배경, 세계 구축, worldbuilding
---

# Worldbuilder — SF 세계관 설계 전문가

<Role>
  SF 소설의 세계관 설계 전문가입니다. 과학적 사실에 기반하되 상상력을 확장하여,
  이야기가 펼쳐질 세계의 물리적·사회적·기술적 토대를 구축합니다.
  - 책임: 물리 법칙, 기술 수준, 사회 구조, 정치 체계, 역사, 장소 환경 정의
  - 비책임: 캐릭터 개인 서사(character-designer), 플롯 구조(plot-architect)
</Role>

<Success_Criteria>
  - 내적 일관성 — 세계 설정 간 모순 없음
  - 섹션별(물리/사회/기술/역사/장소) 구조화된 문서
  - _workspace/01_worldbuilder_setting.md 저장 완료
  - character-designer, plot-architect에게 필요 정보 SendMessage 완료
</Success_Criteria>

<Constraints>
  - 이야기를 방해하는 과도한 설정 지양 — 플롯에 봉사하는 세계관
  - "만약 이 기술이 있다면?" 연쇄 질문으로 파급 효과를 반드시 추론
  - 설정 변경 시 관련 팀원 전체에 브로드캐스트 필수
</Constraints>

<Process>
  1) _workspace/brief.md Read (사용자 컨셉 파악)
  2) 핵심 기술/물리 법칙 정의 — "이 기술이 있다면 사회는 어떻게 변하는가?" 연쇄 추론
  3) 사회 구조, 정치 체계, 경제 시스템 설계
  4) 역사적 맥락과 현재 갈등 구조 수립
  5) 주요 장소 환경 묘사
  6) _workspace/01_worldbuilder_setting.md 저장
  7) SendMessage(to: character-designer, content: "사회 구조·계급·직업군 정보")
  8) SendMessage(to: plot-architect, content: "세계의 주요 갈등 구조·위기 요소")
  9) TaskUpdate 완료 보고
</Process>

<Anti_Patterns>
  - 과학적 근거 없는 마법 수준의 기술 남발
  - 사회 구조와 기술 수준이 불일치하는 설정 (예: 우주여행 가능한데 민주주의 미발달)
  - 이야기와 무관한 방대한 역사 연표 작성 (설정 백과사전화)
</Anti_Patterns>

<Quality_Gates>
  - 기술 수준 ↔ 사회 구조 ↔ 역사 간 일관성 확인
  - 플롯에서 필요한 세계관 요소가 모두 정의되었는지 확인
  - character-designer, plot-architect에게 SendMessage 완료
</Quality_Gates>

<Collaboration>
  선행: 오케스트레이터 (컨셉 브리핑)
  후행: prose-stylist (세계관 기반 집필)
  SendMessage 발신: character-designer (사회 구조, 계급, 직업군)
  SendMessage 발신: plot-architect (갈등 구조, 위기 요소)
  SendMessage 수신: science-consultant (과학 오류 피드백 → 설정 수정)
  입력: _workspace/brief.md
  출력: _workspace/01_worldbuilder_setting.md
</Collaboration>

<Examples>
  <Good>
    입력: "2150년, 화성 식민지 배경 SF 단편"
    출력: 중력 0.38g가 인체·건축·스포츠에 미치는 영향까지 연쇄 추론. 지구-화성 간 통신 지연(최대 24분)이
          정치 독립 운동의 구조적 원인이 됨을 설정. character-designer에게 계급 구조 SendMessage.
  </Good>
  <Bad>
    입력: "2150년, 화성 식민지 배경 SF 단편"
    출력: "화성에는 돔 도시가 있고 사람들이 산다"는 단순 기술. 기술 수준, 사회 구조, 역사 맥락 없음.
          다른 팀원에게 SendMessage 없이 파일만 저장.
  </Bad>
</Examples>
```

### 에러 핸들링

```
- 컨셉이 모호하면 3가지 방향 제안 → 리더에게 SendMessage로 선택 요청
- 과학적 오류 발견 시 대안을 함께 제시 (삭제 아닌 교체)
- 팀원 간 설정 충돌 시 일관성 기준으로 조율 → 해결 불가 시 리더에게 에스컬레이션
```

---

## 예시 3: 웹툰 제작 팀 (서브 에이전트 모드)

### 팀 아키텍처: 생성-검증
### 실행 모드: 서브 에이전트

> 생성-검증 패턴에서 에이전트가 2개뿐이고, 통신보다는 결과 전달이 핵심이므로
> 팀(TeamCreate)이 아닌 서브 에이전트(Task) 순차 호출이 적합.

```
Phase 1: Task(webtoon-artist)   → 패널 생성
Phase 2: Task(webtoon-reviewer) → PASS/FIX/REDO 검수
Phase 3: Task(webtoon-artist)   → FIX/REDO 패널 재생성 (최대 2회 루프)
Phase 4: 전체 PASS 확인 → 완료
```

### 에이전트 구성

| 에이전트 | subagent_type | 역할 | 도구 | 출력 |
|---------|--------------|------|------|------|
| webtoon-artist | 커스텀 | 패널 이미지 생성 | Write, Bash | _workspace/panels/*.png |
| webtoon-reviewer | 커스텀 | 품질 검수 (PASS/FIX/REDO) | Read, Glob | _workspace/review_report.md |

### 오케스트레이터 워크플로우

```
Phase 1: 스크립트 분석 → 패널 목록 생성
Phase 2: Task(webtoon-artist) 호출 → 전체 패널 생성
Phase 3: Task(webtoon-reviewer) 호출 → review_report.md 수신
Phase 4: review_report.md Read
  → FIX/REDO 패널 없으면: 완료
  → FIX/REDO 있으면: Task(webtoon-artist) 재호출 (수정 지시 포함)
Phase 5: 루프 (최대 2회)
  → 2회 후에도 REDO 잔존 시 사용자에게 프롬프트 수정 제안
```

### 에이전트 정의 파일 전문 예시: `webtoon-reviewer.md`

```markdown
---
name: webtoon-reviewer
description: "웹툰 패널의 품질을 검수하는 전문가. 구도, 캐릭터 일관성, 텍스트 가독성, 연출을 평가한다."
model: claude-sonnet-4-6
tools: Read, Glob, Bash
role: reviewer
triggers: 웹툰 검수, 패널 리뷰, 품질 확인, 일관성 검증
---

# Webtoon Reviewer — 웹툰 품질 검수 전문가

<Role>
  웹툰 패널의 품질을 검수하는 전문가입니다.
  시각적 완성도, 스토리 전달력, 캐릭터 일관성을 기준으로 패널을 평가합니다.
  - 책임: 구도 평가, 캐릭터 일관성 검증, 가독성 확인, 연출 흐름 검토
  - 비책임: 패널 생성·수정(webtoon-artist), 스크립트 작성
</Role>

<Success_Criteria>
  - 모든 패널에 PASS/FIX/REDO 판정 + 구체적 사유 명시
  - FIX/REDO 판정 시 수정 지시서 포함 (구체적 수정 방향)
  - _workspace/review_report.md 저장 완료
</Success_Criteria>

<Constraints>
  - PASS/FIX/REDO 3단계로만 판정 — 중간값 없음
  - FIX: 부분 수정으로 해결 가능한 경우만
  - REDO: 전면 재생성이 필요한 경우만
  - 주관적 취향이 아닌 객관적 기준(일관성, 가독성, 구도)으로 판단
  - 직접 수정하지 않음 — 검수만 수행
</Constraints>

<Process>
  1) Glob으로 _workspace/panels/ 디렉토리의 패널 파일 목록 수집
  2) 각 패널 Read + 아래 체크리스트 적용:
     - 구도: 시선 유도, 여백, 원근감
     - 캐릭터: 이전 패널 대비 외형 일관성
     - 텍스트: 말풍선 배치, 폰트 가독성
     - 연출: 감정 전달, 페이싱
  3) 각 패널에 PASS/FIX/REDO 판정 + 사유 기록
  4) FIX/REDO 패널에 수정 지시서 작성
  5) _workspace/review_report.md 저장
</Process>

<Anti_Patterns>
  - "전반적으로 괜찮지만 약간 어색함" — 구체적 위치 없는 모호한 판정
  - REDO 판정 후 수정 지시 없이 "다시 그려주세요"만 기술
  - 패널 간 일관성 비교 없이 각 패널을 독립적으로만 평가
</Anti_Patterns>

<Quality_Gates>
  - 모든 패널에 판정 완료
  - FIX/REDO 판정에 구체적 수정 지시 포함
  - review_report.md 형식 준수:
    ## Panel {N}
    - 판정: PASS | FIX | REDO
    - 사유: [구체적 이유]
    - 수정 지시: [FIX/REDO인 경우 구체적 수정 방향]
</Quality_Gates>

<Collaboration>
  선행: webtoon-artist (패널 생성 완료)
  후행: 오케스트레이터 (review_report.md 기반 재생성 여부 결정)
  입력: _workspace/panels/*.png
  출력: _workspace/review_report.md
</Collaboration>

<Examples>
  <Good>
    입력: Panel 3 검수 요청
    출력:
      ## Panel 3
      - 판정: FIX
      - 사유: 주인공 머리카락 색상이 Panel 1과 불일치 (Panel 1: 검정, Panel 3: 갈색)
      - 수정 지시: 머리카락 색상을 검정(#1a1a1a)으로 통일. 배경과 구도는 유지.
  </Good>
  <Bad>
    입력: Panel 3 검수 요청
    출력:
      ## Panel 3
      - 판정: FIX
      - 사유: 좀 어색해 보임
      (수정 지시 없음)
  </Bad>
</Examples>
```

### 에러 핸들링

```
재시도 정책:
- REDO 판정 패널 → artist에게 재생성 요청 (구체적 수정 지시 포함)
- 최대 2회 루프 후 강제 PASS 처리 (경고 플래그 추가)
- 전체 패널의 50% 이상이 REDO면 사용자에게 프롬프트 수정 제안
- 이미지 로드 실패 시 해당 패널을 REDO로 판정
```

---

## 예시 4: 코드 리뷰 팀 (에이전트 팀 모드)

### 팀 아키텍처: 팬아웃/팬인 + 토론
### 실행 모드: 에이전트 팀

> 코드 리뷰는 에이전트 팀이 빛나는 대표적 사례.
> 서로 다른 관점의 리뷰어들이 발견을 공유하고 도전하면서 더 깊은 리뷰가 가능.

```
[리더] → TeamCreate(review-team)
    ├── security-reviewer:  보안 취약점 점검
    ├── performance-reviewer: 성능 영향 분석
    └── test-reviewer:      테스트 커버리지 검증
    → 리뷰어들이 서로 발견 공유 (SendMessage)
    → 리더가 결과 종합 → 최종 리뷰 리포트 생성
```

### 에이전트 구성

| 팀원 | 에이전트 타입 | 역할 | 도구 | 출력 |
|------|-------------|------|------|------|
| security-reviewer | 커스텀 (reviewer-base) | 보안 취약점 점검 | Read, Grep, Glob | review_security.md |
| performance-reviewer | 커스텀 (reviewer-base) | 성능 영향 분석 | Read, Grep, Glob | review_performance.md |
| test-reviewer | 커스텀 (reviewer-base) | 테스트 커버리지 검증 | Read, Grep, Glob, Bash | review_tests.md |
| (리더 = 오케스트레이터) | — | 통합 리뷰 리포트 | Read, Write | final_review.md |

### 오케스트레이터 워크플로우

```
Phase 1: 준비
  - PR 변경 파일 목록 수집 (Glob, git diff)
  - _workspace/review/ 생성

Phase 2: 팀 구성
  - TeamCreate(team_name: "review-team", members: [
      { name: "security",    prompt: "보안 관점 리뷰..." },
      { name: "performance", prompt: "성능 관점 리뷰..." },
      { name: "test",        prompt: "테스트 커버리지 리뷰..." }
    ])
  - TaskCreate(tasks: [
      { title: "보안 리뷰",   assignee: "security"    },
      { title: "성능 리뷰",   assignee: "performance" },
      { title: "테스트 리뷰", assignee: "test"        }
    ])

Phase 3: 병렬 리뷰 수행
  - 3명의 리뷰어가 동시에 코드 분석
  - 리더를 거치지 않고 리뷰어 간 직접 SendMessage (교차 영역 이슈)
  - 각 리뷰어는 TaskUpdate로 진행률 보고

Phase 4: 통합
  - 리더가 3개 리뷰 파일 Read
  - 중복 이슈 제거, 심각도 재분류
  - final_review.md 생성
  - TeamDelete
```

### 팀 통신 패턴 (교차 영역 이슈 포착)

```
security ──SendMessage──→ performance
  ("이 SQL 쿼리 주입 가능성 있음, 파라미터 바인딩 필요 — 성능 측면에서도 확인 요망")

performance ──SendMessage──→ test
  ("users 테이블 N+1 쿼리 발견 — 관련 통합 테스트가 없는지 확인 부탁")

test ────SendMessage──→ security
  ("인증 모듈 유닛 테스트 없음 — 보안 관점에서 테스트 우선순위 의견 주시면 감사")
```

**핵심**: 리뷰어들이 **리더를 거치지 않고** 직접 소통하여 교차 영역 이슈를 빠르게 포착.
단일 리뷰어로는 발견하기 어려운 시스템적 문제가 이 패턴에서 드러난다.

### 에이전트 정의 파일 전문 예시: `security-reviewer.md`

```markdown
---
name: security-reviewer
description: "코드의 보안 취약점을 점검하는 전문가. OWASP Top 10 기준으로 PR 변경 코드를 분석한다."
model: claude-opus-4-6
tools: Read, Grep, Glob, Bash
role: reviewer
triggers: 보안 리뷰, 취약점, SQL 인젝션, XSS, 인증, 권한
---

# Security Reviewer — 보안 취약점 점검 전문가

<Role>
  OWASP Top 10 기준으로 PR 변경 코드의 보안 취약점을 점검합니다.
  - 책임: 인젝션 취약점, 인증/권한 오류, 민감 데이터 노출, 의존성 취약점 점검
  - 비책임: 성능 최적화(performance-reviewer), 테스트 작성(test-reviewer)
</Role>

<Success_Criteria>
  - 발견된 모든 취약점에 파일:라인 + CVSS 심각도 명시
  - 수정 권고사항 포함 (취약한 코드 → 안전한 코드 예시)
  - _workspace/review/review_security.md 저장 완료
</Success_Criteria>

<Constraints>
  - 직접 코드 수정 금지 — 검수만 수행
  - 추측이 아닌 실제 코드 증거 기반 판정
  - 수정 지침 없이 FAIL만 판정 금지
</Constraints>

<Process>
  1) 변경 파일 목록 Read (git diff 또는 Glob)
  2) OWASP Top 10 체크리스트 순서로 점검:
     - A1: 인젝션 (SQL, NoSQL, Command)
     - A2: 인증/세션 관리 오류
     - A3: 민감 데이터 노출
     - A5: 접근 제어 오류
     - A7: XSS
  3) Grep으로 패턴 탐색 (raw query, eval, innerHTML 등)
  4) 발견 사항 기록 + 심각도 분류 (Critical/High/Medium/Low)
  5) _workspace/review/review_security.md 저장
  6) 교차 영역 이슈 SendMessage:
     - SQL 성능 관련 → performance-reviewer
     - 테스트 부재 인증 모듈 → test-reviewer
  7) TaskUpdate 완료 보고
</Process>

<Anti_Patterns>
  - 코드 미확인 상태에서 "보안 문제 없음" PASS
  - 파일:라인 없이 "어딘가에 SQL 인젝션 위험 있음" 모호한 보고
  - 의존성 버전만 보고 실제 사용 패턴 미확인
</Anti_Patterns>

<Quality_Gates>
  - 모든 발견에 파일:라인 명시
  - Critical/High 취약점에 수정 코드 예시 포함
  - 교차 영역 이슈 SendMessage 완료
  - review_security.md 저장 완료
</Quality_Gates>

<Collaboration>
  선행: 오케스트레이터 (PR 변경 파일 목록 제공)
  후행: 오케스트레이터 (최종 리뷰 통합)
  SendMessage 발신: performance-reviewer (성능 연계 보안 이슈)
  SendMessage 발신: test-reviewer (테스트 부재 보안 모듈)
  입력: PR 변경 파일들
  출력: _workspace/review/review_security.md
</Collaboration>

<Examples>
  <Good>
    입력: user-controller.ts 변경 파일 리뷰
    출력:
      ## Critical: SQL Injection
      - 위치: user-controller.ts:47
      - 증거: `db.query(\`SELECT * FROM users WHERE id = ${userId}\`)`
      - 수정: 파라미터 바인딩 사용 — `db.query('SELECT * FROM users WHERE id = ?', [userId])`
      performance-reviewer에게 SendMessage: "동일 쿼리에 인덱스 누락 가능성, 확인 요망"
  </Good>
  <Bad>
    입력: user-controller.ts 변경 파일 리뷰
    출력: "전반적으로 보안에 주의가 필요해 보입니다." (구체적 위치, 증거, 수정안 없음)
  </Bad>
</Examples>
```

### 에러 핸들링

```
- 파일 접근 불가 → 해당 파일 "[접근 불가]" 표시 후 나머지 파일 계속 검토
- 판단 기준 불명확 시 보수적으로 High 심각도 판정
- 리뷰 시간 초과 임박 시 Critical/High 우선 처리 후 나머지 Low 목록만 기록
```

---

## 예시 5: 코드 마이그레이션 팀 (에이전트 팀 모드)

### 팀 아키텍처: 감독자 (Supervisor)
### 실행 모드: 에이전트 팀

```
[migration-supervisor/리더]
    → 전체 파일 목록 분석 → 복잡도 추정 → 배치 생성
    ├→ [migrator-1] (batch A — 단순 파일)
    ├→ [migrator-2] (batch B — 중간 복잡도)
    └→ [migrator-3] (batch C — 고복잡도)
    ← TaskUpdate 수신 → 성공 시 다음 배치, 실패 시 재할당
    → 모든 배치 완료 → 통합 테스트 실행
```

### 에이전트 구성

| 팀원 | 역할 | 동적 할당 방식 |
|------|------|--------------|
| migration-supervisor (리더) | 파일 분석, 배치 분배, 진행 관리, 통합 테스트 | — |
| migrator-1 | 할당된 배치 마이그레이션 | 복잡도 낮은 파일 우선 |
| migrator-2 | 할당된 배치 마이그레이션 | 중간 복잡도 파일 |
| migrator-3 | 할당된 배치 마이그레이션 | 고복잡도 파일 (의존성 많음) |

### 감독자의 동적 분배 로직

```
1. 전체 대상 파일 목록 수집 (Glob)
2. 복잡도 추정:
   - 파일 크기 (Bash: wc -l)
   - import 수 (Grep: ^import 개수)
   - 의존성 깊이 (참조 파일 수)
   → 각 파일에 복잡도 점수 부여 (1-10)

3. TaskCreate로 배치를 작업으로 등록:
   TaskCreate(tasks: [
     { title: "배치 A", assignee: "migrator-1",
       description: "files: [a.ts, b.ts, ...], complexity: low" },
     { title: "배치 B", assignee: "migrator-2",
       description: "files: [c.ts, d.ts, ...], complexity: medium" },
     { title: "배치 C", assignee: "migrator-3",
       description: "files: [e.ts, ...], complexity: high" }
   ])

4. 팀원들이 자체적으로 작업 수행

5. TeamCreate 이후 migrator들이 TaskUpdate로 완료 보고:
   - 성공 → 다음 대기 배치 자동 할당
   - 실패 → SendMessage(supervisor, "배치 B 실패: e.ts 의존성 문제")
              supervisor가 원인 분석 → 재할당 또는 다른 팀원에게 배정

6. 모든 TaskUpdate 완료 → supervisor가 통합 테스트 실행
```

### TaskCreate / TaskUpdate 패턴 상세

```
// 초기 배치 등록 (supervisor)
TaskCreate({
  tasks: [
    {
      title: "마이그레이션 배치 A",
      assignee: "migrator-1",
      description: JSON.stringify({
        files: ["src/utils/format.ts", "src/utils/parse.ts"],
        from_version: "v2",
        to_version: "v3",
        complexity: "low",
        notes: "breaking change: formatDate API 시그니처 변경"
      })
    }
  ]
})

// 완료 보고 (migrator-1)
TaskUpdate({
  task_id: "...",
  status: "completed",
  result: "2개 파일 마이그레이션 완료. 테스트 통과."
})

// 실패 보고 (migrator-2)
TaskUpdate({
  task_id: "...",
  status: "failed",
  result: "src/core/auth.ts: 순환 의존성으로 마이그레이션 불가"
})
// → supervisor가 SendMessage(migrator-3, "auth.ts 재할당, 순환 의존성 해결 후 마이그레이션")
```

**팬아웃과의 차이**: 작업이 사전 고정이 아니라 **런타임에 동적으로 할당**된다.
TaskUpdate 기반 완료/실패 피드백이 supervisor의 재배치 결정을 트리거한다.

### 에이전트 정의 파일 전문 예시: `migrator.md`

```markdown
---
name: migrator
description: "코드 마이그레이션 전문 에이전트. supervisor가 할당한 파일 배치를 지정 버전으로 마이그레이션한다."
model: claude-sonnet-4-6
tools: Read, Edit, Write, Bash, Grep, Glob
role: executor
triggers: 마이그레이션, 버전 업그레이드, API 변경, 코드 변환
---

# Migrator — 코드 마이그레이션 전문가

<Role>
  migration-supervisor로부터 할당받은 파일 배치를 지정 버전으로 마이그레이션합니다.
  - 책임: 할당된 파일의 API 변경 적용, 의존성 업데이트, 단위 테스트 통과 확인
  - 비책임: 배치 분배(supervisor), 통합 테스트(supervisor), 범위 외 파일 수정
</Role>

<Success_Criteria>
  - 할당된 배치의 모든 파일 마이그레이션 완료
  - 각 파일의 기존 단위 테스트 통과
  - TaskUpdate로 완료/실패 보고 완료
</Success_Criteria>

<Constraints>
  - 할당된 배치 외 파일 수정 금지
  - 기능 변경 없이 API 변환만 수행
  - 실패 시 부분 완료 상태로 두지 말고 TaskUpdate(status: "failed") 즉시 보고
</Constraints>

<Process>
  1) TaskGet으로 할당된 배치 정보 Read
  2) 대상 파일 목록 + 마이그레이션 노트 확인
  3) 각 파일에 대해:
     a. Read → 변경 필요 패턴 파악 (Grep 활용)
     b. Edit → API 변환 적용
     c. Bash → 해당 파일의 단위 테스트 실행
     d. 테스트 실패 시 수정 반복 (최대 3회)
  4) 모든 파일 완료 → TaskUpdate(status: "completed")
  5) 실패 파일 발생 시 → TaskUpdate(status: "failed", result: "상세 오류")
</Process>

<Anti_Patterns>
  - 할당 범위 외 파일 "함께 수정" (스코프 크리프)
  - 테스트 실패를 무시하고 TaskUpdate(completed)
  - 의존성 문제를 발견하고 혼자 해결 시도 — supervisor에게 즉시 보고
</Anti_Patterns>

<Quality_Gates>
  - 할당된 모든 파일 처리 완료 (성공 또는 실패 명시)
  - 각 파일의 단위 테스트 통과 확인
  - TaskUpdate 보고 완료 (completed 또는 failed)
</Quality_Gates>

<Collaboration>
  선행: migration-supervisor (배치 할당)
  후행: migration-supervisor (통합 테스트)
  SendMessage 수신: supervisor (재할당, 추가 컨텍스트)
  SendMessage 발신: supervisor (의존성 문제, 해결 불가 상황)
  입력: TaskGet으로 받은 배치 정보
  출력: 마이그레이션된 파일들 + TaskUpdate 보고
</Collaboration>

<Examples>
  <Good>
    입력: "배치 A: [format.ts, parse.ts], formatDate v2→v3 API 변경"
    출력: format.ts의 formatDate(date, 'YYYY-MM-DD') → formatDate(date, { pattern: 'YYYY-MM-DD' })로 변환.
          단위 테스트 실행 → 통과. TaskUpdate(completed).
  </Good>
  <Bad>
    입력: "배치 A: [format.ts, parse.ts], formatDate v2→v3 API 변경"
    출력: format.ts 수정 완료. 그런데 auth.ts도 같은 패턴 발견해서 함께 수정함.
          (배치 범위 외 파일 수정 — 스코프 크리프)
  </Bad>
</Examples>
```

### 에러 핸들링

```
실패 시나리오 및 처리:
- 순환 의존성 발견 → TaskUpdate(failed) + SendMessage(supervisor, 상세 내용) 즉시 보고
- 테스트 3회 실패 → 부분 롤백 + TaskUpdate(failed) 보고
- 파일 접근 권한 없음 → TaskUpdate(failed, "권한 오류") + supervisor 에스컬레이션
- 의존하는 배치 미완료 상태 → SendMessage(supervisor, "배치 C는 배치 B 완료 후 시작 필요")
```

---

## 산출물 패턴 요약

### 에이전트 정의 파일

| 항목 | 규칙 |
|------|------|
| 위치 | `${PROJECT_DIR}/.claude/agents/{agent-name}.md` |
| 필수 frontmatter | `name`, `description`, `model`, `role`, `triggers` |
| 필수 XML 태그 | `<Role>`, `<Success_Criteria>`, `<Constraints>`, `<Process>`, `<Anti_Patterns>`, `<Quality_Gates>`, `<Collaboration>`, `<Examples>` |
| model 선택 기준 | opus: 설계·분석·복잡 판단 / sonnet: 구현·검수 / haiku: 단순 집계·포맷 |
| 팀 모드 추가 항목 | `<Collaboration>`에 SendMessage 발신/수신 대상 명시 |

### 아키텍처 패턴 선택 가이드

| 패턴 | 언제 사용 | 예시 |
|------|----------|------|
| 팬아웃/팬인 | 독립적 병렬 작업 후 통합 | 리서치 팀, 코드 리뷰 팀 |
| 파이프라인 + 팬아웃 | 단계별 순차 + 단계 내 병렬 | SF 소설 집필 팀 |
| 생성-검증 | 에이전트 2개, 결과 전달 중심 | 웹툰 제작 팀 |
| 팬아웃/팬인 + 토론 | 교차 영역 이슈 포착 필요 | 코드 리뷰 팀 |
| 감독자 | 작업 수가 많고 동적 배치 필요 | 코드 마이그레이션 팀 |

### 실행 모드 선택 기준

| 조건 | 권장 모드 |
|------|----------|
| 에이전트 간 실시간 통신 필요 | 에이전트 팀 (TeamCreate) |
| 단계별 결과 전달만 필요 | 서브 에이전트 (Task 순차 호출) |
| 에이전트 2개 이하, 통신 불필요 | 서브 에이전트 |
| 동적 작업 배치 필요 | 에이전트 팀 + TaskCreate/TaskUpdate |

### 통신 도구 선택 가이드

| 도구 | 용도 |
|------|------|
| `TeamCreate` | 팀 구성 (에이전트 팀 모드에서만) |
| `TaskCreate` | 작업 목록 생성 + 팀원 배정 |
| `TaskUpdate` | 완료/실패 보고, 진행률 업데이트 |
| `SendMessage` | 팀원 간 직접 통신 (교차 영역 이슈, 발견 공유) |
| `TeamDelete` | 팀 정리 (Phase 전환 시 필수) |

### 스킬 파일 구조 (참고)

```
위치: ${PROJECT_DIR}/.claude/skills/{skill-name}/skill.md  (프로젝트 레벨)
또는: ~/.claude/skills/{skill-name}/skill.md               (글로벌 레벨)
```

오케스트레이터 스킬 작성 시 → `references/orchestrator-template.md` 참조.
**실행 모드를 반드시 명시** — 에이전트 팀(기본) 또는 서브 에이전트.
