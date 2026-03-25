#!/usr/bin/env python3
"""ax 시나리오 검증 실행기.

Usage:
  python3 run_scenario.py <scenario.json>           # 단일 시나리오
  python3 run_scenario.py <scenarios-dir> --all      # 전체 시나리오
"""
import sys, os, json, glob

def deep_get(obj, key_path):
    """중첩 딕셔너리에서 점 표기법으로 값 조회."""
    keys = key_path.split('.')
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return None
    return obj

def run_scenario(scenario_path):
    with open(scenario_path, 'r') as f:
        scenario = json.load(f)

    results = {}
    name = scenario.get('name', os.path.basename(scenario_path))
    expected = scenario.get('expected', {})

    # 프로젝트 디렉토리 결정
    flags = scenario.get('input', {}).get('flags', {})
    if flags.get('here', False):
        project_dir = os.getcwd()
    else:
        desc = scenario.get('input', {}).get('domain_description', '')
        project_name = desc.lower().replace(' ', '-')[:30]
        project_dir = os.path.join('projects', project_name)

    # domain-analysis.json 검증
    da_path = os.path.join(project_dir, '.omc/ax/domain-analysis.json')
    if os.path.exists(da_path):
        with open(da_path, 'r') as f:
            da = json.load(f)
        for key, exp_val in expected.get('domain_analysis', {}).items():
            actual = deep_get(da, key)
            if isinstance(exp_val, list):
                results[f"domain.{key}"] = actual in exp_val
            else:
                results[f"domain.{key}"] = actual == exp_val
    else:
        for key in expected.get('domain_analysis', {}):
            results[f"domain.{key}"] = 'SKIP (no domain-analysis.json)'

    # team-architecture.json 검증
    ta_path = os.path.join(project_dir, '.omc/ax/team-architecture.json')
    if os.path.exists(ta_path):
        with open(ta_path, 'r') as f:
            ta = json.load(f)
        ta_exp = expected.get('team_architecture', {})

        # 패턴 검증
        if 'pattern.primary' in ta_exp:
            valid = ta_exp['pattern.primary']
            actual = deep_get(ta, 'pattern.primary')
            results['pattern'] = actual in valid if isinstance(valid, list) else actual == valid

        # 에이전트 수 검증
        if 'agents_count_range' in ta_exp:
            count = len(ta.get('agents', []))
            r = ta_exp['agents_count_range']
            results['agents_count'] = r[0] <= count <= r[1]

        # 필수 에이전트
        if 'required_agents' in ta_exp:
            agent_names = [a.get('name', '') for a in ta.get('agents', [])]
            for req in ta_exp['required_agents']:
                results[f"agent.{req}"] = req in agent_names
    else:
        results['team_architecture'] = 'SKIP (no team-architecture.json)'

    # 생성 파일 검증
    for fpath in expected.get('generated_files', {}).get('must_include', []):
        full = os.path.join(project_dir, fpath)
        results[f"file.{fpath}"] = os.path.exists(full)

    # 결과 요약
    total = len(results)
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if isinstance(v, str))

    return {
        'scenario': name,
        'project_dir': project_dir,
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'overall': 'PASS' if failed == 0 else 'FAIL',
        'details': {k: str(v) for k, v in results.items()}
    }

def run_all(scenarios_dir):
    reports = []
    for sf in sorted(glob.glob(os.path.join(scenarios_dir, '*.json'))):
        reports.append(run_scenario(sf))
    return reports

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 run_scenario.py <scenario.json|dir> [--all]")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target) or '--all' in sys.argv:
        d = target if os.path.isdir(target) else os.path.dirname(target)
        reports = run_all(d)
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        report = run_scenario(target)
        print(json.dumps(report, indent=2, ensure_ascii=False))
