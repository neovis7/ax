# Phase 0: 초기화

## 0.1 프로젝트 권한 자동 설정

`${PROJECT_DIR}/.claude/settings.json`을 생성하여 파이프라인 실행 중 권한 승인을 자동화합니다:

```json
{
  "permissions": {
    "allowedTools": [
      "Write(*)",
      "Edit(*)",
      "Agent(*)",
      "Bash(*)",
      "Read(*)",
      "Grep(*)",
      "Glob(*)",
      "TaskCreate(*)",
      "TaskUpdate(*)",
      "TaskGet(*)",
      "TaskList(*)",
      "SendMessage(*)",
      "WebFetch(*)",
      "WebSearch(*)"
    ]
  }
}
```

이미 `${PROJECT_DIR}/.claude/settings.json`이 존재하면 `allowedTools`를 merge (기존 항목 보존, 누락 항목만 추가).

`${PROJECT_DIR}/.claude/settings.local.json`도 생성하여 런타임 명령 승인을 자동화합니다:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(node *)",
      "Bash(pip *)",
      "Bash(pip3 *)",
      "Bash(python3 *)",
      "Bash(git *)",
      "Bash(curl *)",
      "Bash(mkdir *)",
      "Bash(cp *)",
      "Bash(mv *)",
      "Bash(rm *)",
      "Bash(cat *)",
      "Bash(which *)",
      "Bash(timeout *)",
      "Bash(ls *)",
      "Bash(cd *)"
    ]
  }
}
```

이미 `${PROJECT_DIR}/.claude/settings.local.json`이 존재하면 `allow`를 merge.

## 0.2 진행 추적 초기화

다음 TaskCreate를 호출하여 전체 파이프라인 진행 상태를 등록합니다:

```
TaskCreate("Phase 1: 도메인 분석")
TaskCreate("Phase 2: 팀 아키텍처 설계")
TaskCreate("Phase 3: 에이전트 정의 생성")
TaskCreate("Phase 4: 스킬 생성")
TaskCreate("Phase 5: 오케스트레이터 생성")
TaskCreate("Phase 6: 검증 & 테스트")
TaskCreate("Phase 7: 실행") # --execute 플래그 시에만
```

각 Phase 시작 시 TaskUpdate(in_progress), 완료 시 TaskUpdate(completed)로 갱신합니다.
