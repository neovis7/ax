#!/usr/bin/env python3
"""ax 스킬 자체 무결성 검증 스크립트.

Usage: python3 validate_ax.py [ax-skill-dir]
Default ax-skill-dir: .claude/skills/ax (from project root)
Output: JSON
"""
import sys, os, re, json, glob

def find_ax_root():
    """프로젝트 루트에서 ax 스킬 디렉토리를 찾습니다."""
    candidates = [
        os.path.join(os.getcwd(), '.claude/skills/ax'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.claude/skills/ax'),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None

def validate_ax(ax_root):
    checks = {}
    failures = []

    # 1. SKILL.md 파일 참조 무결성
    skill_md = os.path.join(ax_root, 'SKILL.md')
    ref_ok = True
    if os.path.exists(skill_md):
        with open(skill_md, 'r') as f:
            content = f.read()
        # phases/phase-*.md 참조 확인
        for ref in re.findall(r'phases/phase-\d+-\w+\.md', content):
            if not os.path.exists(os.path.join(ax_root, ref)):
                ref_ok = False
                failures.append(f"참조 깨짐: {ref}")
        # references/*.md 참조 확인
        for ref in re.findall(r'references/[\w-]+\.md', content):
            if not os.path.exists(os.path.join(ax_root, ref)):
                ref_ok = False
                failures.append(f"참조 깨짐: {ref}")
        # templates/*.md 참조 확인
        for ref in re.findall(r'templates/[\w-]+\.md', content):
            if not os.path.exists(os.path.join(ax_root, ref)):
                ref_ok = False
                failures.append(f"참조 깨짐: {ref}")
    else:
        ref_ok = False
        failures.append("SKILL.md 파일 없음")
    checks['reference_integrity'] = 'PASS' if ref_ok else 'FAIL'

    # 2. Phase 파일 완전성 (phases/ 0-7)
    phase_ok = True
    phases_dir = os.path.join(ax_root, 'phases')
    for i in range(8):
        pattern = os.path.join(phases_dir, f'phase-{i}-*.md')
        matches = glob.glob(pattern)
        if not matches:
            phase_ok = False
            failures.append(f"Phase {i} 파일 없음")
    checks['phase_completeness'] = 'PASS' if phase_ok else 'FAIL'

    # 3. 템플릿 플레이스홀더 검증
    tmpl_ok = True
    known_placeholders = {
        'GENERATION_DATE', 'DOMAIN_DESCRIPTION', 'AGENT_TABLE_ROWS',
        'DELEGATION_RULES', 'PATTERN_DESCRIPTION', 'VERIFICATION_POLICY',
        'PRIMARY_PATTERN', 'SECONDARY_PATTERN_NOTE', 'SIGNALS_JSON',
        'DOMAIN_SPECIFIC_STEPS', 'ADDITIONAL_MIDDLEWARE',
        'BACKEND_ANTI_PATTERNS', 'DOMAIN_ANTI_PATTERNS',
    }
    for tmpl in glob.glob(os.path.join(ax_root, 'templates/*.md')):
        with open(tmpl, 'r') as f:
            tcontent = f.read()
        placeholders = set(re.findall(r'\{([A-Z_]+)\}', tcontent))
        unknown = placeholders - known_placeholders
        if unknown:
            # 경고만 (FAIL 아님)
            failures.append(f"미등록 플레이스홀더: {os.path.basename(tmpl)} → {unknown}")
    checks['template_placeholders'] = 'PASS'  # 경고만

    # 4. base-agent 라이브러리 frontmatter 유효성
    ba_ok = True
    ba_files = glob.glob(os.path.join(ax_root, 'library/base-agents/*.md'))
    for ba in ba_files:
        with open(ba, 'r') as f:
            bcontent = f.read()
        parts = bcontent.split('---', 2)
        if len(parts) >= 3:
            fm = {}
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key = line.split(':', 1)[0].strip()
                    fm[key] = True
            for field in ['name', 'role', 'model']:
                if field not in fm:
                    ba_ok = False
                    failures.append(f"base-agent frontmatter 누락: {os.path.basename(ba)} → {field}")
    checks['base_agents'] = 'PASS' if ba_ok or not ba_files else 'FAIL'
    if not ba_files:
        checks['base_agents'] = 'PASS'  # 아직 없으면 OK

    # 5. anti-pattern 라이브러리 존재
    ap_files = glob.glob(os.path.join(ax_root, 'library/anti-patterns/*.md'))
    checks['anti_patterns'] = 'PASS'
    if not ap_files:
        checks['anti_patterns'] = 'PASS'  # 아직 없으면 OK (P3b에서 생성 예정)
    for apf in ap_files:
        if os.path.getsize(apf) < 50:
            failures.append(f"anti-pattern 파일이 너무 작음: {os.path.basename(apf)}")

    # 6. domain-patterns.md 5개 도메인 정의
    dp_path = os.path.join(ax_root, 'templates/domain-patterns.md')
    dp_ok = True
    if os.path.exists(dp_path):
        with open(dp_path, 'r') as f:
            dp_content = f.read()
        for domain in ['code', 'document', 'creative', 'research', 'business']:
            if f'### {domain}' not in dp_content and f'### {domain} 도메인' not in dp_content:
                dp_ok = False
                failures.append(f"domain-patterns에 {domain} 섹션 없음")
    else:
        dp_ok = False
        failures.append("domain-patterns.md 파일 없음")
    checks['domain_patterns'] = 'PASS' if dp_ok else 'FAIL'

    overall = 'PASS' if all(v == 'PASS' for v in checks.values()) else 'FAIL'
    return {
        'tool': 'validate_ax',
        'ax_root': ax_root,
        'checks': checks,
        'overall': overall,
        'failures': failures
    }

if __name__ == '__main__':
    ax_root = sys.argv[1] if len(sys.argv) > 1 else None
    if ax_root is None:
        ax_root = find_ax_root()
    if ax_root is None or not os.path.isdir(ax_root):
        print(json.dumps({"error": f"ax skill directory not found: {ax_root}"}))
        sys.exit(1)
    report = validate_ax(ax_root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
