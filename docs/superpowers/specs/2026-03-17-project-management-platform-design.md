# ProjectFlow — 프로젝트 관리 SaaS 플랫폼 설계

## 개요

대규모 기업(50명+)을 위한 SaaS 프로젝트 관리 플랫폼. Asana의 직관적 UI와 워크플로우 중심 접근을 벤치마크로, 프로젝트 일정 관리, 리소스 배분, 대시보드/리포팅을 올인원으로 제공한다.

**비즈니스 모델:** SaaS 구독형
**벤치마크:** Asana (직관적 UI, 워크플로우 중심)
**역할 구조:** 관리자 / 멤버 / 뷰어 (3단계)

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 프레임워크 | Next.js 15 (App Router) |
| 언어 | TypeScript |
| DB | PostgreSQL + Prisma ORM |
| 인증 | NextAuth.js (OAuth + 이메일) |
| 상태관리 | Zustand (클라이언트) + Server Components (서버) |
| 스타일링 | Tailwind CSS + shadcn/ui |
| 차트 | Recharts (대시보드) + 커스텀 간트 컴포넌트 |
| 실시간 | MVP 범위 외 — 향후 SSE/WebSocket 확장 |
| 테스트 | Vitest + React Testing Library + Playwright |
| 배포 | Vercel + Supabase (PostgreSQL) |

## 아키텍처

Next.js 풀스택 모놀리스. Server Components 기본, 인터랙션 필요 시 Client Component. API Routes로 CRUD, Server Actions는 폼 제출에만 사용. 모든 DB 접근은 Prisma 경유.

```
src/
├── app/                    # Next.js App Router 페이지
│   ├── (auth)/             # 로그인/회원가입
│   ├── (dashboard)/        # 대시보드 레이아웃
│   │   ├── projects/       # 프로젝트 목록/상세
│   │   ├── board/          # 칸반 보드
│   │   ├── timeline/       # 간트차트
│   │   ├── resources/      # 리소스 관리
│   │   └── reports/        # 리포팅
│   └── api/                # API Route Handlers
├── components/             # 공유 UI 컴포넌트
├── lib/                    # 유틸리티, DB 클라이언트
├── prisma/                 # 스키마 & 마이그레이션
└── types/                  # TypeScript 타입 정의
```

## 데이터 모델

### 엔티티 관계

```
Organization (조직)
 ├── Membership (사용자-조직 연결) → User, role: ADMIN | MEMBER | VIEWER
 ├── Project (프로젝트)
 │    ├── Task (태스크)
 │    │    ├── assignee → User
 │    │    ├── status: TODO | IN_PROGRESS | IN_REVIEW | DONE
 │    │    ├── priority: LOW | MEDIUM | HIGH | URGENT
 │    │    ├── startDate / dueDate (간트차트용)
 │    │    └── estimatedHours / actualHours (리소스 관리용)
 │    ├── TaskDependency (태스크 의존관계)
 │    │    ├── predecessorId → Task
 │    │    └── successorId → Task
 │    ├── Milestone (마일스톤)
 │    │    └── tasks[] → Task
 │    └── Column (칸반 컬럼 — 커스텀 가능)
 └── ResourceAllocation (리소스 배분)
      ├── user → User
      ├── project → Project
      └── allocatedHours (주간 배분 시간)
```

### 주요 모델

| 모델 | 핵심 필드 | 설명 |
|------|-----------|------|
| Organization | name, slug, deletedAt | 멀티테넌시 단위 |
| Membership | userId, orgId, role (ADMIN/MEMBER/VIEWER) | 사용자-조직 연결 (다중 조직 지원) |
| User | email, name, deletedAt | 사용자 (여러 조직 소속 가능) |
| Project | name, description, status (ACTIVE/ARCHIVED/COMPLETED), orgId, deletedAt | 프로젝트 |
| Task | title, description, status, priority, assigneeId, projectId, startDate, dueDate, estimatedHours, actualHours, columnId, order, deletedAt | 핵심 엔티티 |
| Milestone | name, dueDate, projectId | 마일스톤 |
| Column | name, order, projectId, defaultStatus (매핑할 Task.status) | 칸반 컬럼 |
| TaskDependency | predecessorId, successorId, projectId | 태스크 의존관계 (finish-to-start) |
| ResourceAllocation | userId, projectId, allocatedHours, week (ISO 주 시작 월요일 Date) | 주간 리소스 배분 |

### 설계 포인트

- **멀티테넌시:** Organization 기반 데이터 완전 격리
- **칸반 순서:** Task.order 필드 (정수, gap-based: 1000 간격 배치, 공간 소진 시 re-index)
- **리소스 추적:** 태스크별 예상/실제 시간 + 주간 배분
- **소프트 삭제:** Organization, User, Project, Task에 deletedAt 필드
- **태스크 의존관계:** TaskDependency로 finish-to-start 관계 표현, 간트차트에서 화살표 렌더링. 순환 의존 방지: 의존관계 생성 시 DFS로 사이클 탐지, 순환 발견 시 400 에러 반환
- **다중 조직:** User ↔ Organization은 Membership 조인 테이블로 N:M 관계
- **컬럼-상태 관계:** Column은 순수 칸반 UI용 그룹핑이며 Task.status와 독립적. 프로젝트 생성 시 기본 4컬럼(할 일/진행 중/리뷰/완료) 자동 생성되고 각각 기본 status 매핑 보유. 커스텀 컬럼 추가 시 status 매핑을 선택. 태스크를 컬럼 간 이동하면 매핑된 status도 자동 변경
- **칸반 re-index:** 컬럼 단위로 수행 (프로젝트 전체가 아닌 해당 컬럼의 태스크만 재정렬)

## API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 권한 |
|-----------|--------|------|------|
| `/api/auth/*` | * | NextAuth.js 핸들러 | 공개 |
| `/api/users/me/organizations` | GET | 내 조직 목록 조회 | 인증 |
| `/api/organizations` | POST | 조직 생성 | 인증 |
| `/api/organizations/[orgId]` | GET, PATCH | 조직 조회/수정 | ADMIN |
| `/api/organizations/[orgId]/members` | GET, POST, DELETE | 멤버 관리 | ADMIN |
| `/api/projects` | GET, POST | 프로젝트 목록/생성 | MEMBER+ |
| `/api/projects/[id]` | GET, PATCH, DELETE | 프로젝트 상세/수정/삭제 | MEMBER+(삭제는 ADMIN) |
| `/api/projects/[id]/columns` | GET, POST, PATCH, DELETE | 칸반 컬럼 CRUD | MEMBER+ |
| `/api/projects/[id]/tasks` | GET, POST | 태스크 목록/생성 | MEMBER+ (GET은 VIEWER+) |
| `/api/tasks/[id]` | GET, PATCH, DELETE | 태스크 상세/수정/삭제 | MEMBER+ (PATCH/DELETE은 담당자 또는 생성자만, GET은 VIEWER+) |
| `/api/tasks/[id]/dependencies` | GET, POST, DELETE | 태스크 의존관계 관리 | MEMBER+ |
| `/api/tasks/reorder` | PATCH | 칸반 순서 변경 (columnId, order) | MEMBER+ |
| `/api/projects/[id]/milestones` | GET, POST | 프로젝트 마일스톤 목록/생성 | MEMBER+ |
| `/api/milestones/[id]` | GET, PATCH, DELETE | 마일스톤 상세/수정/삭제 | MEMBER+ |
| `/api/projects/[id]/resources` | GET, POST, PATCH | 프로젝트 리소스 배분 관리 | MEMBER+ |
| `/api/resources/workload?week=YYYY-MM-DD` | GET | 주간 팀 워크로드 조회 (전체 프로젝트 합산) | VIEWER+ |
| `/api/dashboard/stats` | GET | KPI 집계 데이터 | VIEWER+ |
| `/api/dashboard/charts` | GET | 차트 데이터 (진행률, 상태 분포) | VIEWER+ |

모든 응답: `{ data: T }` 성공 / `{ error: string, code: string }` 실패. 목록 API는 커서 기반 페이지네이션 지원 (`?cursor=&limit=20`).

## UI/UX 설계

### 레이아웃

사이드바 + 탑바 구조 (Asana 스타일):
- **탑바:** 로고, 조직 전환 드롭다운, 프로필
- **좌측 사이드바:** 내 작업, 대시보드, 리포트, 리소스, 프로젝트 목록
- **메인 영역:** 프로젝트별 뷰 전환 탭 (보드/타임라인/리스트)

### 칸반 보드

- 드래그앤드롭 태스크 이동 (컬럼 간, 순서 변경)
- 커스텀 컬럼 추가/삭제/이름 변경
- 태스크 카드 클릭 시 사이드 패널로 상세 (페이지 이동 없음)
  - 사이드 패널 내용: 제목, 설명(마크다운), 상태, 우선순위, 담당자, 기한, 예상/실제 시간 편집
- 카드에 우선순위 색상, 기한, 담당자 아바타 표시
- 필터: 담당자, 우선순위, 기한 / 정렬: 우선순위, 기한, 생성일

### 간트차트

- 태스크 바 드래그로 기간 조정
- 태스크 의존관계 화살표 표시 (finish-to-start)
- 의존관계 생성: 태스크 바 우측 끝 핸들을 드래그하여 다른 태스크에 연결. 삭제: 화살표 클릭 후 삭제 버튼
- 마일스톤 다이아몬드 표시, 오늘 마커
- 진행률 시각화 (바 내부 색상 채우기)
- 줌 레벨: 일/주/월 전환
- 프로젝트당 최대 200개 태스크. 초과 시 태스크 생성 API에서 제한 (400 에러)

### 대시보드

카드 그리드 레이아웃:
- KPI 카드 4개: 전체 프로젝트 수, 진행 태스크, 완료율, 지연 태스크
- 프로젝트별 진행률 바 차트
- 태스크 상태 도넛 차트
- 기간 필터 (이번 주 / 이번 달 / 전체)

### 리소스 관리

- 팀원별 주간 워크로드 스택 바
- 과부하(>100%) 빨간색 경고
- 프로젝트별 배분 시간 시각화
- 주간 단위 네비게이션

## 인증 & 권한

- NextAuth.js: OAuth (Google, GitHub) + 이메일/패스워드
- 조직 생성 후 ADMIN이 멤버를 직접 추가 (초대 링크는 향후 확장)
- 사용자는 여러 조직에 소속 가능 (Membership 조인 테이블)
- 조직 생성 시 생성자가 자동으로 ADMIN
- 역할별 API 미들웨어로 권한 체크:
  - ADMIN: 모든 CRUD + 조직 설정 + 멤버 관리 + 프로젝트 삭제
  - MEMBER: 태스크 읽기(전체) + 태스크 생성 + 태스크 수정/삭제(본인 담당 또는 본인 생성분) + 담당자 변경(본인을 담당자로 지정 가능) + 프로젝트 생성/수정 (삭제 불가)
  - VIEWER: 읽기 전용

## 에러 처리

- API: 일관된 에러 포맷 `{ error: string, code: string }`
- 클라이언트: React Error Boundary로 페이지별 에러 격리
- 낙관적 업데이트: 칸반 드래그 즉시 반영, 실패 시 롤백 (last-write-wins, MVP에서는 동시 편집 충돌 미처리)
- 유효성 검증: Zod 스키마 서버/클라이언트 공유

## 테스트 전략

- **단위 테스트 (Vitest):** 권한 미들웨어, 의존관계 사이클 탐지, 칸반 순서 계산, Zod 유효성 검증
- **API 테스트 (Vitest + Supertest):** 모든 엔드포인트 CRUD + 권한 검증 (역할별 접근 제어 테스트 필수)
- **컴포넌트 테스트 (React Testing Library):** 칸반 카드, 태스크 사이드 패널, 대시보드 카드
- **E2E (Playwright):** 회원가입→조직생성→프로젝트생성→태스크생성→칸반이동 플로우, 간트차트 드래그 조정

**필수 테스트 불변식:**
- VIEWER는 어떤 데이터도 생성/수정/삭제 불가
- MEMBER는 타인의 태스크를 삭제 불가
- 태스크 의존관계에 사이클이 존재하면 안 됨
- 프로젝트당 태스크 200개 제한 준수

## MVP 범위 & 구현 단계

MVP는 5개 독립 모듈로 구성되며, 아래 순서로 단계적 구현한다. **각 Phase는 별도의 구현 계획(plan)으로 작성한다.** 이 스펙은 전체 시스템의 설계 문서이며, 실제 구현은 Phase별 plan을 통해 진행한다.

### Phase 1: 기반 (인증 + 데이터 모델)
- Prisma 스키마 정의 및 마이그레이션
- NextAuth.js 인증 (OAuth + 이메일)
- 조직/멤버 관리 API
- 역할 기반 권한 미들웨어
- 기본 레이아웃 (사이드바 + 탑바)

### Phase 2: 태스크 관리 (칸반 보드)
- 프로젝트/태스크 CRUD API
- 칸반 보드 UI (드래그앤드롭, 컬럼 관리)
- 태스크 사이드 패널
- 필터/정렬

### Phase 3: 간트차트
- 커스텀 간트 컴포넌트 (SVG 기반, Canvas 아님 — 접근성/인터랙션 용이)
- 태스크 바 드래그 기간 조정
- 의존관계 화살표
- 마일스톤, 줌 레벨
- 성능: 프로젝트당 최대 200개 태스크 기준 설계, 가상화 미적용 (MVP)

### Phase 4: 리소스 관리
- 리소스 배분 CRUD API
- 주간 워크로드 스택 바 UI
- 과부하 경고

### Phase 5: 대시보드 & 리포팅
- KPI 집계 API
- 카드 그리드 대시보드
- Recharts 차트 (진행률 바, 도넛)
- 기간 필터

### 향후 확장 (MVP 이후)

- 검색 (프로젝트/태스크 전문 검색)
- 알림 시스템
- 댓글 기능
- 초대 링크로 멤버 합류
- 실시간 동시 편집 (SSE/WebSocket)
- 동시 편집 충돌 해결
- 모바일 반응형 최적화
