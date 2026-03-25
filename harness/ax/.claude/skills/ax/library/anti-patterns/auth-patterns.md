# Authentication & Session Anti-Patterns

Phase 3에서 인증이 포함된 프로젝트의 에이전트 `<Anti_Patterns>`에 주입합니다.

## JWT
- ❌ 시크릿 키 하드코딩 → ✅ 환경변수에서 로드, 폴백 없음
- ❌ expiresIn 숫자 (밀리초 혼동) → ✅ 문자열 '15m', '1h', '7d'
- ❌ 토큰에 민감정보(비밀번호) 포함 → ✅ userId + role만 포함
- ❌ 토큰 검증 없이 디코딩만 → ✅ verify() 사용

## 세션 지속성
- ❌ 메모리 전용 저장 (변수) → 새로고침 시 유실 → ✅ localStorage 또는 httpOnly 쿠키
- ❌ localStorage + XSS 취약점 → ✅ httpOnly 쿠키 우선, 불가 시 sanitization 필수
- ❌ refresh 토큰 미구현 → ✅ access(단기) + refresh(장기) 이중 토큰
- ❌ 로그인 상태 복원 미구현 → ✅ 앱 로드 시 토큰 검증 + 사용자 정보 복원

## 보호 라우트
- ❌ 프론트만 라우트 보호 (백엔드 미들웨어 없음) → ✅ BE 미들웨어 + FE 가드 이중 보호
- ❌ 401 응답 시 리다이렉트 없음 → ✅ 인터셉터에서 로그인 페이지로 리다이렉트

## 쿠키 보안
- ❌ Secure 미설정 (HTTP에서 쿠키 전송) → ✅ Secure; SameSite=Strict; HttpOnly
- ❌ 감사 로그에 DELETE/UPDATE 허용 → ✅ INSERT-ONLY 감사 로그
