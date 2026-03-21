---
name: {SKILL_NAME}
description: >-
  {SKILL_DESCRIPTION — 기능 설명 + 트리거 조건을 함께 작성.
  "무엇을 하는지"와 "언제 사용하는지" 모두 이 필드에 포함.
  사용자가 "{관련 키워드1}", "{관련 키워드2}", "{관련 키워드3}" 등을 요청할 때
  이 스킬을 사용하세요. 명시적으로 스킬 이름을 말하지 않더라도
  관련 작업이면 트리거되도록 pushy하게 작성.}
origin: ax
domain: {SKILL_DOMAIN}
dependencies: {SKILL_DEPENDENCIES}
---

# {SKILL_DISPLAY_NAME}

## When to Activate

> 이 섹션은 description의 트리거 조건을 보완합니다 — description이 1차 트리거이고, 이 섹션은 2차 참조입니다.

{ACTIVATION_CONDITIONS}

## Core Rules

{CORE_RULES}

## Process

{PROCESS_STEPS}

## Examples

**Example 1:**
Input: {사용자 요청 예시}
Output: {기대 결과 요약}

**Example 2:**
Input: {다른 사용자 요청}
Output: {기대 결과 요약}
