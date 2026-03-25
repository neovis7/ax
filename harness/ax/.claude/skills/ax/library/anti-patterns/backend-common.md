# Backend Common Anti-Patterns

Phase 3에서 backend 역할 에이전트의 `<Anti_Patterns>` 섹션에 주입합니다.

## 요청 처리
- ❌ `req.json()` 직접 사용 → ✅ Express `express.json()` 미들웨어 + `req.body`
- ❌ 요청 바디 유효성 검증 없이 사용 → ✅ Zod `safeParse` 후 사용
- ❌ `any` 타입으로 요청/응답 처리 → ✅ Zod 스키마에서 추론된 타입 사용

## 인증
- ❌ JWT `expiresIn`에 숫자(ms) 사용 → ✅ 문자열 형식 `'15m'`, `'7d'`
- ❌ 환경변수 폴백값 (`process.env.JWT_SECRET || 'secret'`) → ✅ 폴백 없이 undefined면 앱 시작 실패
- ❌ 비밀번호 평문 저장 → ✅ bcrypt/argon2 해싱
- ❌ 토큰을 응답 바디에만 반환 (페이지 새로고침 시 유실) → ✅ httpOnly 쿠키 또는 refresh 토큰 구현

## 에러 처리
- ❌ `catch(e) {}` 빈 catch 블록 → ✅ 로깅 + 적절한 에러 응답
- ❌ 500 에러에 스택 트레이스 노출 → ✅ 프로덕션에서 generic 메시지
- ❌ 모든 에러에 200 OK 반환 → ✅ 적절한 HTTP 상태 코드 (400, 401, 404, 500)

## 응답 형식
- ❌ 성공 시 `{message: "Created"}` (id 없음) → ✅ 생성된 객체 전체 반환 (id 포함)
- ❌ 목록 API에서 객체 단일 반환 → ✅ 항상 배열 반환 (빈 배열 포함)

## DB/ORM
- ❌ 유틸리티 함수 인라인 중복 → ✅ 공통 유틸리티 모듈로 분리
- ❌ Fisher-Yates 셔플 구현 오류 (`i >= 0` 대신 `i > 0`) → ✅ 정확한 구현 확인
- ❌ Prisma 없이 raw SQL만 사용 (ORM 프로젝트에서) → ✅ Prisma adapter 패턴 준수
