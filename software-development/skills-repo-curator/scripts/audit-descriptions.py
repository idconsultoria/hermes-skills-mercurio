#!/usr/bin/env python3
"""Audit description format compliance across all SKILL.md files.

Usage:
    cd /opt/data/skills && python3 software-development/skills-repo-curator/scripts/audit-descriptions.py
    cd /opt/data/skills && python3 software-development/skills-repo-curator/scripts/audit-descriptions.py --drift

Checks:
- Quoted string format (no block scalars |, |-, >, >-)
- Summary ≤85 chars and no "..." truncation
- Paragraph with "Load this skill when" activation trigger
- No literal \\n escapes (must use real newlines in quoted strings)
- Resumo drift between index.md and actual SKILL.md summary (--drift only)
"""

import os
import re
import sys

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
INDEX_MD = os.path.join(SKILLS_DIR, 'index.md')


def get_skills():
    for root, dirs, files in os.walk(SKILLS_DIR):
        if '.archive' in root or '.git' in root:
            continue
        if 'SKILL.md' in files:
            path = os.path.join(root, 'SKILL.md')
            rel = os.path.relpath(root, SKILLS_DIR)
            with open(path) as f:
                yield rel, f.read()


def parse_description(content):
    issues = []
    fm = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm:
        return None, '', False, False, ['No frontmatter']
    front = fm.group(1)

    if re.search(r'^description:\s*[|>]', front, re.MULTILINE):
        return None, '', False, False, ['Block scalar format (| or >) — must use quoted string']

    m = re.search(r'^description:\s*(\S)', front, re.MULTILINE)
    if m and m.group(1) != '"':
        return None, '', False, False, [f'Unquoted description (starts with "{m.group(1)}")']

    desc_raw = re.search(r'^description:\s*"(.*)', front, re.MULTILINE)
    if not desc_raw:
        return None, '', False, False, ['No description field found']

    start = desc_raw.start(1)
    idx = start
    while idx < len(front):
        if front[idx] == '"' and (idx == 0 or front[idx-1] != '\\'):
            break
        idx += 1
    description = front[start:idx]

    has_literal_nn = '\\n' in description
    has_real_nl = '\n' in description
    parts = re.split(r'\n\n', description, maxsplit=1)
    summary = parts[0].strip() if parts else description[:80]

    if not summary:
        issues.append('Empty summary')
    if len(summary) > 85:
        issues.append(f'Summary too long ({len(summary)} chars)')
    if '...' in summary:
        issues.append(f'Summary truncated with "..."')
    if has_literal_nn:
        issues.append('Literal \\\\n escapes — must use real newlines')
    if not has_real_nl:
        issues.append('Single-line description — missing paragraph')
    elif 'load this skill' not in description.lower() and 'carregue esta skill' not in description.lower():
        issues.append('Missing "Load this skill when..." trigger')

    return description, summary, has_real_nl, has_literal_nn, issues


def audit():
    all_issues = []
    ok_count = 0
    for rel, content in get_skills():
        desc, summary, has_nl, has_nn, issues = parse_description(content)
        if issues:
            all_issues.append((rel, issues))
        else:
            ok_count += 1

    print(f'SKILL.md files: {ok_count + len(all_issues)}')
    print(f'Compliant: {ok_count}')
    print(f'With issues: {len(all_issues)}')
    for rel, issues in sorted(all_issues):
        print(f'\n  {rel}:')
        for issue in issues:
            print(f'    ❌ {issue}')

    if all_issues:
        sys.exit(1)


def check_drift():
    if not os.path.exists(INDEX_MD):
        print(f'ERROR: index.md not found')
        sys.exit(1)
    with open(INDEX_MD) as f:
        idx = f.read()

    index_resumos = {}
    for block in re.split(r'\n(?=### )', idx):
        m = re.search(r'- \*\*Nome:\*\* `(.+?)`', block)
        r = re.search(r'- \*\*Resumo:\*\* (.+)', block)
        if m and r:
            index_resumos[m.group(1)] = r.group(1).strip()

    drift_count = 0
    for rel, content in get_skills():
        desc, summary, _, _, issues = parse_description(content)
        if not summary:
            continue
        actual = summary[:85] if len(summary) > 85 else summary
        idx_val = index_resumos.get(rel)
        if idx_val and idx_val.rstrip('.') != actual.rstrip('.'):
            print(f'  DRIFT: {rel}')
            print(f'    SKILL.md: "{actual}"')
            print(f'    index.md: "{idx_val}"')
            drift_count += 1

    print(f'\nResumo drift count: {drift_count}')
    if drift_count:
        sys.exit(1)


def main():
    if '--drift' in sys.argv:
        check_drift()
    else:
        audit()


if __name__ == '__main__':
    main()
