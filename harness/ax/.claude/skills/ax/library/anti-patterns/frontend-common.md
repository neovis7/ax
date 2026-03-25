# Frontend Common Anti-Patterns

Phase 3에서 frontend 역할 에이전트의 `<Anti_Patterns>` 섹션에 주입합니다.

## 방어적 데이터 접근
- ❌ API 응답 데이터 직접 접근 (`data.items.map(...)`) → ✅ optional chaining (`data?.items?.map(...)`)
- ❌ 배열 메서드 직접 호출 (`items.map(...)`) → ✅ 널 병합 (`(items ?? []).map(...)`)
- ❌ `useGet` 반환값을 다시 `.data`로 감싸기 → ✅ `useGet`이 이미 `ApiResponse.data`를 추출함
- ❌ 중첩 객체 접근 시 방어 없음 → ✅ 모든 깊이에서 `?.` 사용

## 상태 관리
- ❌ 로딩 상태 UI 없음 (빈 화면) → ✅ 스켈레톤/스피너 표시
- ❌ 에러 상태 UI 없음 (조용한 실패) → ✅ 에러 메시지 + 재시도 버튼
- ❌ 빈 상태 UI 없음 (빈 테이블) → ✅ EmptyState 컴포넌트 ("데이터가 없습니다")
- ❌ 낙관적 업데이트 없이 느린 피드백 → ✅ 즉시 UI 반영 + 실패 시 롤백

## 폼 처리
- ❌ 폼 제출 시 로딩 표시 없음 → ✅ 버튼 비활성화 + 스피너
- ❌ 서버 에러 메시지 무시 → ✅ 서버 반환 에러를 폼에 표시
- ❌ 성공 후 목록 새로고침 안 함 → ✅ mutation 후 query invalidation
- ❌ 모달 닫기 후 폼 상태 미초기화 → ✅ 닫기 시 reset

## 인증
- ❌ 테스트 계정 자체 생성 (하드코딩) → ✅ `prisma/seed.ts` 시드 데이터 확인 후 사용
- ❌ 로그인 후 리다이렉트 없음 → ✅ 보호된 페이지로 리다이렉트
- ❌ 토큰 만료 시 무한 루프 → ✅ refresh 실패 시 로그아웃 처리
