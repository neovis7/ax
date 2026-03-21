#!/usr/bin/env python3
"""ax 프로젝트 구조 검증 스크립트.

Usage: python3 validate_project.py <project-dir>
Output: JSON (validation-report.json 형식)
"""
import sys, os, re, json, glob

def parse_frontmatter(filepath):
    """--- YAML --- 블록에서 key: value 추출."""
    result = {}
    with open(filepath, 'r') as f:
        content = f.read()
    parts = content.split('---', 2)
    if len(parts) < 3:
        return result
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key = line.split(':', 1)[0].strip()
            val = line.split(':', 1)[1].strip()
            result[key] = val
    return result

def check_xml_tags(filepath, tags):
    """파일 내 XML 태그 존재 여부 확인."""
    with open(filepath, 'r') as f:
        content = f.read()
    return [t for t in tags if f'<{t}>' not in content]

def validate_project(project_dir):
    checks = {}
    failures = []
    agent_files = glob.glob(os.path.join(project_dir, '.claude/agents/*.md'))

    # 1. 에이전트 frontmatter
    fm_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        for field in ['name', 'description', 'model']:
            if field not in fm:
                fm_ok = False
                failures.append(f"frontmatter 누락: {os.path.basename(af)} -> {field}")
    checks['agent_frontmatter'] = 'PASS' if fm_ok else 'FAIL'

    # 2. 에이전트 본문 구조
    body_ok = True
    for af in agent_files:
        missing = check_xml_tags(af, ['Role', 'Success_Criteria', 'Constraints'])
        if missing:
            body_ok = False
            failures.append(f"XML 태그 누락: {os.path.basename(af)} -> {missing}")
    checks['agent_body_structure'] = 'PASS' if body_ok else 'FAIL'

    # 3. Examples 존재
    ex_ok = True
    for af in agent_files:
        if check_xml_tags(af, ['Examples']):
            ex_ok = False
            failures.append(f"Examples 누락: {os.path.basename(af)}")
    checks['agent_examples'] = 'PASS' if ex_ok else 'FAIL'

    # 4. 모델 ID 유효성
    valid_models = {'claude-sonnet-4-6', 'claude-opus-4-6', 'claude-haiku-4-5'}
    model_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        if fm.get('model', '') not in valid_models:
            model_ok = False
            failures.append(f"유효하지 않은 모델: {os.path.basename(af)} -> {fm.get('model')}")
    checks['agent_model_valid'] = 'PASS' if model_ok else 'FAIL'

    # 5. 스킬 frontmatter
    skill_files = glob.glob(os.path.join(project_dir, '.claude/skills/*/SKILL.md'))
    skill_ok = True
    for sf in skill_files:
        fm = parse_frontmatter(sf)
        for field in ['name', 'description']:
            if field not in fm:
                skill_ok = False
                failures.append(f"스킬 frontmatter 누락: {os.path.basename(os.path.dirname(sf))} -> {field}")
    checks['skill_frontmatter'] = 'PASS' if skill_ok or not skill_files else 'FAIL'
    if not skill_files:
        checks['skill_frontmatter'] = 'PASS'

    # 6. CLAUDE.md 섹션
    claude_md = os.path.join(project_dir, 'CLAUDE.md')
    if os.path.exists(claude_md):
        with open(claude_md, 'r') as f:
            content = f.read()
        checks['claudemd_section'] = 'PASS' if 'Harness-Generated Team' in content else 'FAIL'
        if checks['claudemd_section'] == 'FAIL':
            failures.append("CLAUDE.md에 Harness-Generated Team 섹션 없음")
    else:
        checks['claudemd_section'] = 'FAIL'
        failures.append("CLAUDE.md 파일 없음")

    # 7. 순환 의존성 검사
    circ_ok = True
    if os.path.exists(claude_md):
        with open(claude_md, 'r') as f:
            cm_content = f.read()
        # 위임 규칙에서 "→ agent_name" 패턴으로 방향 그래프 구축
        edges = {}
        for line in cm_content.split('\n'):
            if '→' in line and '`' in line:
                parts = line.split('→')
                if len(parts) >= 2:
                    # 백틱 안의 에이전트 이름 추출
                    src_matches = re.findall(r'`([a-z-]+)`', parts[0])
                    dst_matches = re.findall(r'`([a-z-]+)`', parts[1])
                    for s in src_matches:
                        for d in dst_matches:
                            if s != d:
                                edges.setdefault(s, set()).add(d)
        # DFS로 사이클 검출
        visited = set()
        rec_stack = set()
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in edges.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False
        for node in list(edges.keys()):
            if node not in visited:
                if has_cycle(node):
                    circ_ok = False
                    failures.append(f"순환 의존성 발견: {node} 관련 사이클")
                    break
    checks['circular_dependency'] = 'PASS' if circ_ok else 'FAIL'

    # 8. 역할 충돌
    roles = {}
    role_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        role = fm.get('role', '')
        triggers = fm.get('triggers', '')
        if role in roles and triggers and triggers == roles[role]:
            role_ok = False
            failures.append(f"역할 충돌: {role} 역할의 에이전트가 동일 triggers")
        roles[role] = triggers
    checks['semantic_role_conflict'] = 'PASS' if role_ok else 'FAIL'

    # 8b. 위임 누락 (delegation gap) — CLAUDE.md 위임 규칙에 에이전트가 참조되는지
    deleg_ok = True
    if os.path.exists(claude_md):
        with open(claude_md, 'r') as f:
            cm = f.read()
        for af in agent_files:
            aname = parse_frontmatter(af).get('name', '')
            if aname and aname not in cm and aname not in ('visual-architect', 'visual-builder', 'visual-qa'):
                deleg_ok = False
                failures.append(f"위임 누락: {aname}이 CLAUDE.md 위임 규칙에 없음")
    checks['semantic_delegation_gap'] = 'PASS' if deleg_ok else 'FAIL'

    # 8c. 고아 에이전트 (orphan agent) — triggers 비어있는 에이전트
    orphan_ok = True
    for af in agent_files:
        fm = parse_frontmatter(af)
        triggers = fm.get('triggers', '').strip()
        if not triggers:
            orphan_ok = False
            failures.append(f"고아 에이전트: {fm.get('name', os.path.basename(af))} triggers 비어있음")
    checks['semantic_orphan_agent'] = 'PASS' if orphan_ok else 'FAIL'

    # 9. 시각화 체인 (소규모 팀 5개 이하는 visual-builder 없어도 PASS)
    agent_names = {parse_frontmatter(af).get('name', '') for af in agent_files}
    visual_trio = {'visual-architect', 'visual-builder', 'visual-qa'}
    if len(agent_files) <= 5:
        visual_min = {'visual-architect', 'visual-qa'}
        has_min = visual_min.issubset(agent_names)
        checks['visual_chain'] = 'PASS' if has_min else 'FAIL'
        if not has_min:
            failures.append(f"시각화 체인 누락: {visual_min - agent_names}")
    else:
        has_trio = visual_trio.issubset(agent_names)
        checks['visual_chain'] = 'PASS' if has_trio else 'FAIL'
        if not has_trio:
            failures.append(f"시각화 체인 누락: {visual_trio - agent_names}")

    # 10. 하드코딩 색상 (Example/Anti_Patterns 블록 내부는 허용)
    hardcoded = []
    for af in agent_files:
        with open(af, 'r') as f:
            content_full = f.read()
        lines = content_full.split('\n')
        in_exempt_block = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if any(tag in stripped for tag in ['<Good>', '<Bad>', '<Anti_Patterns>', '<Examples>']):
                in_exempt_block = True
            if any(tag in stripped for tag in ['</Good>', '</Bad>', '</Anti_Patterns>', '</Examples>']):
                in_exempt_block = False
                continue
            if in_exempt_block:
                continue
            if re.search(r'#[0-9a-fA-F]{6}', line):
                in_line_exempt = any(kw in line for kw in ['예:', '출력:', '대비', '미달', '하드코딩', '--color', 'style=', '부적합', '//', 'Example'])
                if not in_line_exempt:
                    hardcoded.append(f"{os.path.basename(af)}:{i}")
    checks['hardcoded_colors'] = 'PASS' if not hardcoded else 'FAIL'
    if hardcoded:
        failures.append(f"하드코딩 색상: {hardcoded[:5]}")

    overall = 'PASS' if all(v == 'PASS' for v in checks.values()) else 'FAIL'
    return {
        'project': os.path.basename(project_dir),
        'agent_count': len(agent_files),
        'skill_count': len(skill_files),
        'checks': checks,
        'overall': overall,
        'failures': failures
    }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 validate_project.py <project-dir>")
        sys.exit(1)
    project_dir = sys.argv[1].rstrip('/')
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a directory")
        sys.exit(1)
    report = validate_project(project_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
