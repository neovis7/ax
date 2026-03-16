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
| 실시간 | Server-Sent Events (SSE) — MVP, 이후 WebSocket 확장 |
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
 ├── User (사용자) — role: ADMIN | MEMBER | VIEWER
 ├── Project (프로젝트)
 │    ├── Task (태스크)
 │    │    ├── assignee → User
 │    │    ├── status: TODO | IN_PROGRESS | IN_REVIEW | DONE
 │    │    ├── priority: LOW | MEDIUM | HIGH | URGENT
 │    │    ├── startDate / dueDate (간트차트용)
 │    │    └── estimatedHours / actualHours (리소스 관리용)
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
| Organization | name, plan, slug | 멀티테넌시 단위 |
| User | email, name, role, orgId | 사용자 |
| Project | name, description, status, orgId | 프로젝트 |
| Task | title, status, priority, assigneeId, projectId, startDate, dueDate, estimatedHours, actualHours, columnId, order | 핵심 엔티티 |
| Milestone | name, dueDate, projectId | 마일스톤 |
| Column | name, order, projectId | 칸반 컬럼 |
| ResourceAllocation | userId, projectId, allocatedHours, week | 주간 리소스 배분 |

### 설계 포인트

- **멀티테넌시:** Organization 기반 데이터 완전 격리
- **칸반 순서:** Task.order 필드로 드래그앤드롭 정렬
- **리소스 추적:** 태스크별 예상/실제 시간 + 주간 배분
- **소프트 삭제:** 중요 엔티티에 deletedAt 필드

## UI/UX 설계

### 레이아웃

사이드바 + 탑바 구조 (Asana 스타일):
- **탑바:** 로고, 검색, 알림, 프로필
- **좌측 사이드바:** 내 작업, 대시보드, 리포트, 리소스, 프로젝트 목록
- **메인 영역:** 프로젝트별 뷰 전환 탭 (보드/타임라인/리스트)

### 칸반 보드

- 드래그앤드롭 태스크 이동 (컬럼 간, 순서 변경)
- 커스텀 컬럼 추가/삭제/이름 변경
- 태스크 카드 클릭 시 사이드 패널로 상세 (페이지 이동 없음)
- 카드에 우선순위 색상, 기한, 담당자 아바타 표시
- 필터: 담당자, 우선순위, 기한 / 정렬: 우선순위, 기한, 생성일

### 간트차트

- 태스크 바 드래그로 기간 조정
- 마일스톤 다이아몬드 표시, 오늘 마커
- 진행률 시각화 (바 내부 색상 채우기)
- 줌 레벨: 일/주/월 전환

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
- 조직 생성 → 초대 링크로 멤버 합류
- 역할별 API 미들웨어로 권한 체크:
  - ADMIN: 모든 CRUD + 조직 설정 + 멤버 관리
  - MEMBER: 태스크/프로젝트 CRUD
  - VIEWER: 읽기 전용

## 에러 처리

- API: 일관된 에러 포맷 `{ error: string, code: string }`
- 클라이언트: React Error Boundary로 페이지별 에러 격리
- 낙관적 업데이트: 칸반 드래그 즉시 반영, 실패 시 롤백
- 유효성 검증: Zod 스키마 서버/클라이언트 공유

## 테스트 전략

- 단위 테스트: Vitest (유틸리티, 비즈니스 로직)
- 컴포넌트 테스트: React Testing Library (핵심 UI)
- E2E: Playwright (로그인, 태스크 생성, 칸반 이동)
- API 테스트: Vitest + Supertest

## MVP 범위

### 포함

1. 프로젝트/태스크 CRUD 및 칸반 보드
2. 간트차트/타임라인 뷰
3. KPI 대시보드/리포팅
4. 리소스/워크로드 관리
5. 인증 (OAuth + 이메일)
6. 3단계 역할 권한

### 향후 확장

- 댓글/알림 시스템
- 팀 멤버 초대 UI (MVP에서는 관리자 직접 추가)
- 실시간 동시 편집
- 모바일 반응형 최적화
- WebSocket 기반 실시간 업데이트
