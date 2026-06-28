#!/usr/bin/env python3
"""Create OKF-aligned index.md per category directory (v2 — handles root-level skills too)."""
import os, re

SKILLS_DIR = '/opt/data/skills'
SKIP_DIRS = {'scripts', 'reports', '.git', '__pycache__', '.curator_backups', '.archive'}
ROOT_RESERVED = {'AGENTS.md', 'index.md', 'log.md', 'skills_graph.html', 
                  'skills_graph_template.html', 'graph_data.json', '.gitignore'}

CAT_DESC = {
    'autonomous-ai-agents': 'Skills for orchestrating autonomous AI agents, delegation patterns, and multi-agent workflows.',
    'content-production': 'Skills for producing content — newsletters, audio, sound effects, and text-to-speech.',
    'creative': 'Skills for creative work — branding, copywriting, humanization, design systems, and visual assets.',
    'dogfood': 'Skills for exploratory QA testing of web applications.',
    'github': 'Skills for GitHub workflows — PR lifecycle, code review, codebase inspection.',
    'health': 'Skills for fitness coaching and workout planning.',
    'health-fitness': 'Skills for body recomposition metrics and tracking.',
    'infrastructure': 'Skills for infrastructure — SSH, deployment, CI/CD, API safeguards.',
    'media': 'Skills for media production — video, manga conversion, anime research.',
    'productivity': 'Skills for productivity tools — Google Workspace, Notion, TaskFlow, HTML/PDF generation.',
    'read-reddit': 'Skills for reading Reddit communities via RSS feeds.',
    'research': 'Skills for deep research, user interviews, trend discovery, and model benchmarking.',
    'social-media': 'Skills for social media content and brand management.',
    'software-development': 'Skills for software development — planning, architecture, debugging, sprints, TDD.',
    'apple': 'Apple platform skills and utilities.',
    'data-science': 'Data science skills and tools.',
    'email': 'Email automation skills.',
    'mlops': 'MLOps skills — evaluation, inference, model management.',
    'note-taking': 'Note-taking and knowledge management skills.',
    'smart-home': 'Smart home automation skills.',
}

def read_descf(path):
    """Read the SUMMARY or DESCRIPTION from a category."""
    for name in ('SUMMARY.md', 'DESCRIPTION.md', 'README.md'):
        p = os.path.join(path, name)
        if os.path.exists(p):
            with open(p) as f:
                return f.read().strip()
    return ''

def read_skill_info(path):
    """Extract type, timestamp, size, summary, title from a SKILL.md."""
    meta = {'type': '', 'timestamp': '', 'size': 0, 'summary': '', 'title': ''}
    if not os.path.exists(path):
        return meta
    meta['size'] = os.path.getsize(path)
    with open(path) as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    body = content
    fm = {}
    if m:
        fm_t = m.group(1)
        body = content[m.end():].strip()
        for line in fm_t.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip().strip('"\'')
                fm[k] = v
    meta['type'] = fm.get('type', '')
    meta['timestamp'] = fm.get('timestamp', '')
    desc = fm.get('description', '')
    if desc:
        sent = re.split(r'[.。!?\n]', desc)[0].strip()
        meta['summary'] = sent[:85] + ('...' if len(sent) > 85 else sent)
    h1 = re.search(r'^# (.+)$', body, re.MULTILINE)
    meta['title'] = h1.group(1).strip() if h1 else ''
    return meta

def generate(cat, skills, root_skills, has_subdirs):
    lines = [f'# {cat.replace("-", " ").title()}', '']
    desc = CAT_DESC.get(cat, read_descf(os.path.join(SKILLS_DIR, cat)))
    if desc:
        lines.append(desc)
        lines.append('')
    
    total = len(skills) + len(root_skills)
    if total == 0:
        lines.append('*No skills in this category yet.*')
        lines.append('')
        return '\n'.join(lines)
    
    lines.append(f'## Skills')
    lines.append('')
    lines.append(f'*{total} skills*')
    lines.append('')
    
    # Root-level skills first (e.g., dogfood/SKILL.md)
    for sk_name, sk_path in sorted(root_skills):
        meta = read_skill_info(sk_path)
        label = sk_name
        title = meta['title'] or label
        lines.append(f'### [{title}](SKILL.md)')
        if meta['summary']:
            lines.append(f'_{meta["summary"]}_')
        lines.append('')
        parts = []
        if meta['type']: parts.append(f'Type: {meta["type"]}')
        if meta['timestamp']: parts.append(f'Updated: {meta["timestamp"][:10]}')
        if meta['size']: parts.append(f'{meta["size"]:,} chars')
        if parts:
            lines.append(' | '.join(parts))
            lines.append('')
        lines.append('---')
        lines.append('')
    
    # Subdirectory skills
    for sk in skills:
        sk_name = sk.split('/')[-1]
        rel_path = '/'.join(sk.split('/')[1:])
        meta = read_skill_info(os.path.join(SKILLS_DIR, sk, 'SKILL.md'))
        title = meta['title'] or sk_name
        lines.append(f'### [{title}]({rel_path}/SKILL.md)')
        if meta['summary']:
            lines.append(f'_{meta["summary"]}_')
        lines.append('')
        parts = []
        if meta['type']: parts.append(f'Type: {meta["type"]}')
        if meta['timestamp']: parts.append(f'Updated: {meta["timestamp"][:10]}')
        if meta['size']: parts.append(f'{meta["size"]:,} chars')
        if parts:
            lines.append(' | '.join(parts))
            lines.append('')
        lines.append('---')
        lines.append('')
    
    return '\n'.join(lines)

def main():
    # Build categories map
    cats = {}
    root_level_skills = {}
    
    for root, dirs, files in os.walk(SKILLS_DIR):
        # Skip root-level reserved files
        rel = os.path.relpath(root, SKILLS_DIR)
        if rel == '.':
            continue
        
        parts = rel.split(os.sep)
        cat = parts[0]
        
        if cat.startswith('.') or cat in SKIP_DIRS:
            continue
        
        if 'SKILL.md' in files:
            if len(parts) == 1:
                # Root-level skill: e.g., dogfood/SKILL.md
                root_level_skills.setdefault(cat, []).append(rel)
            else:
                cats.setdefault(cat, []).append(rel)
    
    # Sort
    for cat in cats:
        cats[cat].sort()
    for cat in root_level_skills:
        root_level_skills[cat].sort()
    
    # Determine all categories
    all_cats = set(list(cats.keys()) + list(root_level_skills.keys()))
    
    # Also check for empty category dirs
    for d in os.listdir(SKILLS_DIR):
        dpath = os.path.join(SKILLS_DIR, d)
        if os.path.isdir(dpath) and not d.startswith('.') and d not in SKIP_DIRS and d not in ROOT_RESERVED:
            all_cats.add(d)
    
    print(f"Found {len(all_cats)} categories")
    
    for cat in sorted(all_cats):
        cat_dir = os.path.join(SKILLS_DIR, cat)
        if not os.path.isdir(cat_dir):
            continue
        
        skills = cats.get(cat, [])
        root_skills = [(s, os.path.join(SKILLS_DIR, s, 'SKILL.md')) 
                       for s in root_level_skills.get(cat, [])]
        
        content = generate(cat, skills, root_skills, bool(skills))
        
        idx_path = os.path.join(cat_dir, 'index.md')
        with open(idx_path, 'w') as f:
            f.write(content)
        
        total = len(skills) + len(root_skills)
        print(f"  ✓ {cat}/index.md ({total} skills, {len(skills)} subdir + {len(root_skills)} root)")

if __name__ == '__main__':
    main()
