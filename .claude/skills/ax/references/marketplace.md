# 마켓플레이스 통합 (v1.0 스펙)

## Phase 4.2 외부 스킬 검색

```
1) 도메인 키워드로 외부 마켓플레이스 검색:
   - GitHub: `gh search repos "{domain} claude-code skill" --limit 5`
   - npm: `npm search "claude-code-skill-{domain}" --limit 5`

2) 검색 결과를 평가:
   - 스타 수 / 다운로드 수
   - 최근 업데이트 (6개월 이내)
   - README에 SKILL.md 형식 포함 여부

3) 상위 3개를 사용자에게 추천:
   "외부 마켓플레이스에서 발견된 스킬:
     1. {이름} ⭐{stars} — {설명} (설치: {명령어})
     2. ...
   설치하시겠습니까? (번호/건너뛰기)"

4) 선택 시 설치 + generation-log에 기록
```

## 보안 고려사항

스킬 설치는 코드 실행 권한을 부여하는 것과 같으므로:
- 설치 전 README/SKILL.md 내용을 사용자에게 표시
- `dangerouslyDisableSandbox` 포함 여부 경고
- 신뢰할 수 없는 소스는 설치 전 확인 필수
