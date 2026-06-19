#!/usr/bin/env python3
"""
Audit all SKILL.md descriptions for format compliance + Resumo drift in index.md.

Usage:
    python3 scripts/audit-descriptions.py                # scan all SKILL.md in repo
    python3 scripts/audit-descriptions.py --fix          # fix \n\n escapes in index Resumo
    python3 scripts/audit-descriptions.py --drift-report  # compare index Resumo vs actual summaries

Checks:
1. Format: description uses quoted string ("..."), not block scalar (|, |-, >, >-)
2. Summary length: ≤85 chars, no ... truncation
3. Trigger phrase: has "Load this skill when" or variant
4. Resumo drift: index.md Resumo matches actual SKILL.md summary
"""

import os, re, sys, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def get_skill_descriptions():
    """Walk all SKILL.md files and extract their description frontmatter."""
    skills = {}
    for path in sorted(REPO.rglob('SKILL.md')):
        rel = str(path.relative_to(REPO))
        content = path.read_text()

        # Check format
        fmt_match = re.search(r'^description:\s*([|>-])', content, re.MULTILINE)
        fmt = fmt_match.group(1) if fmt_match else None
        extra = ''
        if fmt_match:
            extra = fmt_match.group(0).strip().split(None, 1)[1] if len(fmt_match.group(0).split(None, 1)) > 1 else ''

        # Extract quoted string content
        idx = content.find('description: "')
        if idx < 0:
            skills[rel] = {'error': 'no description: "..." found', 'format': fmt, 'format_detail': extra}
            continue

        start = idx + len('description: "')
        end = start
        while end < len(content):
            if content[end] == '"' and (end == 0 or content[end-1] != '\\'):
                break
            end += 1

        desc = content[start:end]
        if not desc.strip():
            skills[rel] = {'error': 'empty description', 'format': fmt}
            continue

        # Detect \n\n literal vs real newlines
        has_literal_nl = '\\n\\n' in desc
        has_real_nl = '\n\n' in desc

        # Get summary (first segment)
        if has_real_nl:
            summary = desc.split('\n\n', 1)[0].strip()
        elif has_literal_nl:
            summary = desc.split('\\n\\n', 1)[0].strip()
        else:
            summary = desc.strip()

        # Detect trigger phrase
        trigger = any(t in desc for t in [
            'Load this skill when', 'Load this skill to', 'Load this skill for',
            'Use this skill when', 'Use when the user', 'Activates when',
            'Load this skill during'
        ])

        # Classify issues
        issues = []
        if fmt:
            issues.append(f'YAML {fmt}{"-" if fmt in ">|" and fmt_match and fmt_match.group(0).rstrip().endswith("-") else ""} format')
        if has_literal_nl:
            issues.append('\\n\\n literal escapes (use real newlines)')
        if len(summary) > 85:
            issues.append(f'Summary {len(summary)} chars > 85')
        if summary.rstrip().endswith('...'):
            issues.append('Summary ends with ... (truncation)')
        if not trigger:
            issues.append('Missing trigger phrase')

        skills[rel] = {
            'summary': summary,
            'summary_len': len(summary),
            'trigger': trigger,
            'format': fmt,
            'has_literal_nl': has_literal_nl,
            'has_real_nl': has_real_nl,
            'issues': issues,
            'desc_preview': desc[:80] + '...' if len(desc) > 80 else desc,
        }

    return skills


def check_resumo_drift(index_path, skills):
    """Compare index.md Resumo entries against actual SKILL.md summaries."""
    with open(index_path) as f:
        lines = f.readlines()

    resumo_map = {}
    current_skill = None
    for line in lines:
        if line.startswith('### '):
            current_skill = line.strip('### ').strip()
        if line.strip().startswith('- **Resumo:**'):
            if current_skill:
                resumo = line.split(':**', 1)[1].strip()
                resumo_map[current_skill] = resumo

    drift = []
    for name, index_resumo in resumo_map.items():
        # Find matching skill by path tail
        for sk_path, sk_data in skills.items():
            if sk_path.endswith(name.split('/')[-1] + '/SKILL.md'):
                actual = sk_data.get('summary', '')
                if not actual:
                    continue
                # Check for severe mismatch
                if index_resumo.rstrip().endswith('...'):
                    drift.append((name, index_resumo, actual, 'truncated'))
                elif actual[:len(index_resumo.rstrip())] != index_resumo.rstrip():
                    drift.append((name, index_resumo, actual, 'mismatch'))
                break

    return drift


def main():
    print(f'Scanning SKILL.md files in {REPO}...')
    skills = get_skill_descriptions()
    print(f'  Found {len(skills)} files\n')

    # Section 1: Format & content issues
    with_issues = {k: v for k, v in skills.items() if v.get('issues') and not v.get('error')}
    errors = {k: v for k, v in skills.items() if v.get('error')}

    if errors:
        print(f'=== PARSE ERRORS ({len(errors)}) ===')
        for path, data in errors.items():
            print(f'  {path}: {data["error"]}')
        print()

    if with_issues:
        print(f'=== CONTENT ISSUES ({len(with_issues)} skills) ===')
        for path, data in sorted(with_issues.items()):
            print(f'  {path}')
            for issue in data['issues']:
                print(f'    - {issue}')
            if data['format']:
                print(f'    Format: {data["format"]}')
            if data.get('has_literal_nl'):
                print(f'    Literal \\\\n')
            print(f'    Summary: {data["summary"][:75]}...' if len(data['summary']) > 75 else f'    Summary: {data["summary"]}')
        print()

    # Section 2: Resumo drift
    index_path = REPO / 'index.md'
    if index_path.exists():
        drift = check_resumo_drift(index_path, skills)
        if drift:
            print(f'=== RESUMO DRIFT ({len(drift)} entries) ===')
            for name, index_r, actual_r, kind in drift:
                print(f'  {name}')
                print(f'    Index:  {index_r}')
                print(f'    Actual: {actual_r}')
                print(f'    Kind:   {kind}')
            print()

    # Summary
    clean = len(skills) - len(errors) - len(with_issues)
    print(f'=== SUMMARY ===')
    print(f'  Total SKILL.md: {len(skills)}')
    print(f'  Parse errors:   {len(errors)}')
    print(f'  Issues:         {len(with_issues)}')
    print(f'  Clean:          {clean}')
    print(f'  Resumo drifts:  {len(drift) if index_path.exists() else "N/A (no index.md)"}')

    return 1 if with_issues or errors else 0


if __name__ == '__main__':
    sys.exit(main())
