# Fullstack Integration Anti-Patterns

Phase 3에서 fullstack/api 도메인의 모든 에이전트 `<Anti_Patterns>`에 주입합니다.

## API 경로 일치
- ❌ 프론트 hook이 `POST /wrong-path`를 호출하는데 백엔드는 `PUT /correct-path` → ✅ api-contracts.ts를 단일 진실 소스로 사용
- ❌ URL params를 body에 중복 전송 → ✅ `@source params` 필드는 프론트에서 제외

## 응답 구조
- ❌ 프론트가 API 응답 구조를 추측하여 구현 → ✅ api-fixtures.ts를 Read하여 실제 구조 확인
- ❌ 스키마 일치 = 기능 일치 착각 → ✅ Zod 스키마 + @intent 주석 모두 확인
- ❌ DB/API/시드 간 컬럼명 불일치 (resource_type vs table_name) → ✅ snake_case→camelCase 변환 외 차이 불허

## 토큰/세션
- ❌ 메모리 전용 토큰 + refresh 미구현 (새로고침 시 유실) → ✅ 지속성 방식 명시 + BE/FE 일치 확인
- ❌ 인증 persistence 방식이 BE/FE 불일치 → ✅ execution-policy 또는 api-contracts의 @persistence 참조

## CRUD 완성도
- ❌ 백엔드 API만 있고 프론트 UI 없음 → ✅ crud-matrix.md 대조 필수
- ❌ hooks 정의만 하고 미사용 (dead hook) → ✅ 정의한 hook은 반드시 import + 사용
- ❌ 관리 UI 없이 시드/API 직접 호출 의존 → ✅ 모든 '필수' 엔티티에 관리 페이지 구현
