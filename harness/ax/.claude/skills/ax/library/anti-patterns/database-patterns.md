# Database & ORM Anti-Patterns

Phase 3에서 DB를 사용하는 에이전트의 `<Anti_Patterns>`에 주입합니다.

## 마이그레이션
- ❌ 마이그레이션 없이 DB 스키마 변경 → ✅ 마이그레이션 파일로 버전 관리
- ❌ 마이그레이션에 데이터 삭제 포함 (DROP TABLE) → ✅ 가역적 마이그레이션 우선

## 시드 데이터
- ❌ 시드 스크립트에 dotenv 로드 누락 → ✅ 시드 시작부에 dotenv.config()
- ❌ NOT NULL 컬럼을 시드에서 누락 → ✅ DB 스키마의 모든 NOT NULL 컬럼 포함
- ❌ 시드 컬럼명과 DB 스키마 불일치 → ✅ 마이그레이션 파일의 정확한 컬럼명 사용

## 컬럼명 일관성
- ❌ DB=snake_case, API=camelCase, 시드=또 다른 이름 → ✅ 단일 변환 규칙 (snake→camel만 허용)
- ❌ resource_type(DB) vs tableName(API) vs name(시드) → ✅ 같은 의미면 같은 이름

## 커넥션
- ❌ 서버리스에서 pg.Pool max=10 → 커넥션 고갈 → ✅ Vercel 등 서버리스: max=1
- ❌ 커넥션 타임아웃 미설정 → ✅ idleTimeoutMillis: 20000, connectionTimeoutMillis: 10000
- ❌ prisma generate를 빌드에서 누락 → ✅ build 스크립트에 `prisma generate && ...` 포함
