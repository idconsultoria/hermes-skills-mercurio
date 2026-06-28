#!/usr/bin/env python3
"""Generate skills_graph.html from all SKILL.md files in the skills repo.

Usage:
  cd /opt/data/skills
  python3 scripts/generate_graph.py          # writes skills_graph.html
  python3 scripts/generate_graph.py --json   # writes graph_data.json only
"""

import os, re, json, sys, argparse

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(SKILLS_DIR, 'index.md')
TEMPLATE_PATH = os.path.join(SKILLS_DIR, 'skills_graph_template.html')
OUTPUT_HTML = os.path.join(SKILLS_DIR, 'skills_graph.html')
OUTPUT_JSON = os.path.join(SKILLS_DIR, 'graph_data.json')

def parse_index_relations():
    """Extract relations from index.md. Falls back to LLM-inferred JSON."""
    if not os.path.exists(INDEX_PATH):
        print(f"Warning: {INDEX_PATH} not found, relations will be empty")
        return {}
    
    with open(INDEX_PATH) as f:
        idx = f.read()
    
    relations = {}
    current_name = ''
    
    for line in idx.split('\n'):
        m = re.search(r'`([^`]+)`', line)
        if line.startswith('- **Nome:**') and m:
            current_name = m.group(1)
            relations[current_name] = []
        elif line.strip().startswith('- `') and '→' in line and current_name:
            rm = re.match(r"- `(\w+)` → `(.+)`", line.strip())
            if rm:
                relations[current_name].append((rm.group(1), rm.group(2)))
    
    # If index.md has no relations, fall back to LLM-inferred JSON
    total = sum(len(v) for v in relations.values())
    if total == 0:
        llm_path = '/opt/data/skills_relations_merged.json'
        if os.path.exists(llm_path):
            print("index.md has no relations — using LLM-inferred JSON fallback")
            with open(llm_path) as f:
                return json.load(f)
    
    return relations

def parse_skills(relations):
    """Walk SKILLS_DIR and extract metadata from every SKILL.md."""
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        # Skip .archive directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if 'SKILL.md' in files:
            path = os.path.join(root, 'SKILL.md')
            name = os.path.relpath(path, SKILLS_DIR).replace('/SKILL.md', '')
            size = os.path.getsize(path)
            cat = name.split('/')[0] if '/' in name else 'uncategorized'
            
            with open(path) as f:
                content = f.read()
            
            # Frontmatter
            fm = {}
            body = content
            fm_m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if fm_m:
                fm_t = fm_m.group(1)
                body = content[fm_m.end():].strip()
                for l in fm_t.split('\n'):
                    if ':' in l:
                        k, v = l.split(':', 1)
                        fm[k.strip()] = v.strip().strip('"\'')
            
            title = fm.get('title', '')
            desc = fm.get('description', '')
            if not title:
                h1 = re.search(r'^# (.+)$', body, re.MULTILINE)
                title = h1.group(1).strip() if h1 else name.split('/')[-1]
            if not desc or desc in ('>-', '>', '>|', '|', ''):
                desc = ''
            desc = desc.replace('>-', '').replace('>|', '').strip()
            
            if not desc:
                paras = [l.strip() for l in body.split('\n') if l.strip()
                         and not l.startswith('#') and not l.startswith('```')
                         and not l.startswith('|') and not l.startswith('>')]
                desc = ' '.join(paras[:3])[:500] if paras else ''
            
            summary = ''
            if desc:
                sent = re.split(r'[.。!?\n]', desc)[0].strip()
                summary = sent[:87] + '...' if len(sent) > 90 else sent
            
            # Extract type from frontmatter
            skill_type = fm.get('type', '')
            
            skills.append({
                'id': name, 'label': name.split('/')[-1], 'title': title,
                'size': size, 'category': cat, 'type': skill_type,
                'summary': summary, 'description': desc
            })
    
    return skills

def build_edges(relations, current_names):
    """Build edges from relations, deduplicating bidirectional pairs."""
    seen_edges = set()
    edges = []
    
    for name, rels in relations.items():
        if name not in current_names:
            continue
        for rtype, target in rels:
            if target not in current_names:
                continue
            if rtype in ('parent', 'uses'):
                key = (name, target, 'directed')
                if key not in seen_edges and (target, name, 'directed') not in seen_edges:
                    seen_edges.add(key)
                    edges.append({'source': name, 'target': target, 'type': rtype})
            elif rtype in ('child', 'used_by'):
                key = (target, name, 'directed')
                if key not in seen_edges and (name, target, 'directed') not in seen_edges:
                    seen_edges.add(key)
                    edges.append({'source': target, 'target': name, 'type': 'parent' if rtype == 'child' else 'uses'})
            elif rtype == 'similar':
                key = (min(name, target), max(name, target), 'similar')
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges.append({'source': name, 'target': target, 'type': 'similar'})
    
    return edges

def main():
    parser = argparse.ArgumentParser(description='Generate skills graph HTML')
    parser.add_argument('--json', action='store_true', help='Write only graph_data.json')
    args = parser.parse_args()
    
    # Parse
    relations = parse_index_relations()
    skills = parse_skills(relations)
    current_names = {s['id'] for s in skills}
    edges = build_edges(relations, current_names)
    
    data = {'nodes': skills, 'edges': edges}
    
    # Write JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"graph_data.json: {len(skills)} nodes, {len(edges)} edges")
    
    if args.json:
        return
    
    # Inject into template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: template not found at {TEMPLATE_PATH}")
        sys.exit(1)
    
    with open(TEMPLATE_PATH) as f:
        template = f.read()
    
    html = template.replace('__DATA_PLACEHOLDER__', json.dumps(data, ensure_ascii=False))
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html)
    
    size = os.path.getsize(OUTPUT_HTML)
    print(f"skills_graph.html: {size:,} bytes")

if __name__ == '__main__':
    main()
