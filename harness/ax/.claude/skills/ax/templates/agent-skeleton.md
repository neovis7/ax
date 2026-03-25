---
name: {AGENT_NAME}
description: {AGENT_DESCRIPTION}
model: {AGENT_MODEL}
tools: {AGENT_TOOLS}
role: {AGENT_ROLE}
triggers: {AGENT_TRIGGERS}
---
<!-- 필수 규칙:
  1. model은 반드시 다음 중 하나: claude-sonnet-4-6 | claude-opus-4-6 | claude-haiku-4-5
     (claude-sonnet-4-5, claude-opus-4-5 등 구 ID 사용 금지)
  2. triggers는 반드시 비어있지 않은 값으로 채울 것 (예: "코드 리뷰, 보안 검토")
  3. 본문 섹션은 반드시 XML 태그(<Role>, </Role>)를 사용할 것
     (## Role 같은 마크다운 헤더 사용 금지 — validate_project.py가 XML 태그만 검출)
-->

# {AGENT_DISPLAY_NAME}

<Role>
  {ROLE_DESCRIPTION}
  - 책임: {RESPONSIBILITIES}
  - 비책임: {NON_RESPONSIBILITIES}
</Role>

<Success_Criteria>
  {SUCCESS_CRITERIA_LIST}
</Success_Criteria>

<Constraints>
  {CONSTRAINTS_LIST}
</Constraints>

<Process>
  {PROCESS_STEPS}
</Process>

<Tool_Usage>
  {TOOL_USAGE_GUIDELINES}
</Tool_Usage>

<Examples>
  <Good>
    입력: {GOOD_EXAMPLE_INPUT}
    출력: {GOOD_EXAMPLE_OUTPUT — 역할에 맞는 도구 사용, 적절한 위임, 구체적 산출물}
  </Good>
  <Bad>
    입력: {BAD_EXAMPLE_INPUT}
    출력: {BAD_EXAMPLE_OUTPUT — 역할 범위 초과, 부적절한 도구, 모호한 결과}
  </Bad>
</Examples>

<Anti_Patterns>
  - {ANTI_PATTERN_1 — 이 에이전트가 빠지기 쉬운 잘못된 행동}
  - {ANTI_PATTERN_2}
  - {ANTI_PATTERN_3}
</Anti_Patterns>

<Quality_Gates>
  - {GATE_1 — 이 에이전트의 출력물이 PASS하려면 충족해야 할 조건}
  - {GATE_2}
  - {GATE_3}
</Quality_Gates>

<Collaboration>
  - 선행 에이전트: {UPSTREAM_AGENT} — 이 에이전트가 받는 입력과 경로
  - 후행 에이전트: {DOWNSTREAM_AGENT} — 이 에이전트가 넘기는 출력과 경로
  - 산출물 경로: {OUTPUT_PATH}
</Collaboration>
