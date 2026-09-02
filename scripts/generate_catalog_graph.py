#!/usr/bin/env python3
"""Generate the skills graph (HTML + JSON) scoped to the INDEXED CATALOG (82 skills),
reading skills and relations from index.md, not from disk (which has ~140 untracked).
Writes only skills_graph.html and graph_data.json — never the index.md.
"""
import os, re, json, sys
os.chdir('/opt/mercurio-data/skills')

INDEX = 'index.md'
TEMPLATE = 'software-development/skills-repo-curator/templates/graph.html'
OUT_HTML = 'skills_graph.html'
OUT_JSON = 'graph_data.json'

idx = open(INDEX).read()

# 1. skills catalogadas: linhas de tabela '| `skill` | Type | desc |', capturando a categoria da seção ## corrente
skills = []
current_cat = ""
for line in idx.split('\n'):
    hm = re.match(r'^## ([a-z0-9_\-]+)', line.strip())
    if hm:
        current_cat = hm.group(1)
        continue
    m = re.match(r'\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|', line)
    if m:
        name, typ = m.group(1), m.group(2)
        skills.append({'name': name, 'type': typ, 'category': current_cat})
allnames = {s['name'] for s in skills}
print(f"skills catalogadas: {len(skills)}")

# 2. relações do apêndice '## Relações entre skills'
rels = []
sim_section = False
uses_section = False
for line in idx.split('\n'):
    t = line.strip()
    if t.startswith('## Relações'):
        sim_section = uses_section = False
        continue
    if t.startswith('Similar:'):
        sim_section, uses_section = True, False; continue
    if t.startswith('Uses:'):
        sim_section, uses_section = False, True; continue
    m = re.match(r'^- `([^`]+)` → `([^`]+)`$', t)
    if m and (sim_section or uses_section):
        a, b = m.group(1).strip(), m.group(2).strip()
        rtype = 'similar' if sim_section else 'uses'
        # só inclui se AMBOS estão no catálogo
        if a in allnames and b in allnames:
            rels.append({'source': a, 'target': b, 'type': rtype})
print(f"relações do apêndice: {len(rels)}")

# valida: nenhuma relação apontando p/ skill fora do catálogo
edges_ok = 0; edges_dropped = 0
kept = []
for r in rels:
    if r['source'] in allnames and r['target'] in allnames:
        kept.append(r); edges_ok += 1
    else:
        edges_dropped += 1
print(f"  arestas válidas (ambos no catálogo): {edges_ok}; descartadas: {edges_dropped}")

# nós
nodes = []
for s in skills:
    # caminho real: <categoria>/<nome>/SKILL.md (o index lista só o nome curto)
    sk = os.path.join(s['category'], s['name'], 'SKILL.md')
    if not os.path.exists(sk):
        # fallback: relativo p/ skill raiz
        alt = os.path.join(s['name'], 'SKILL.md')
        sk = alt if os.path.exists(alt) else sk
    size = os.path.getsize(sk) if os.path.exists(sk) else 0
    # summary (1ª linha do description) e description do frontmatter
    summary = ""
    description = ""
    if os.path.exists(sk):
        c = open(sk).read()
        fm = re.search(r'^---\n(.*?)\n---', c, re.DOTALL)
        if fm:
            d = re.search(r'^description:\s*"((?:[^"\\]|\\.)*)', fm.group(1), re.MULTILINE)
            if d:
                description = d.group(1).strip()
                summary = description.split('\n')[0].strip()[:87]
    nodes.append({
        'id': s['name'], 'label': s['name'].split('/')[-1],
        'category': s['category'], 'type': s['type'],
        'size': size, 'summary': summary, 'description': description
    })

data = {'nodes': nodes, 'edges': kept}

with open(OUT_JSON, 'w') as f:
    json.dump(data, f, ensure_ascii=False)
print(f"graph_data.json: {len(nodes)} nós, {len(kept)} arestas")

if os.path.exists(TEMPLATE):
    tpl = open(TEMPLATE).read()
    html = tpl.replace('__DATA_PLACEHOLDER__', json.dumps(data, ensure_ascii=False))
    open(OUT_HTML, 'w').write(html)
    print(f"skills_graph.html: {os.path.getsize(OUT_HTML):,} bytes")
else:
    print("WARN: template não encontrado; HTML não gerado")
    sys.exit(1)

# auditoria de órfãos (skills sem nenhuma aresta) e dangling (alvos fora do catálogo)
deg = {}
for r in kept:
    deg[r['source']] = deg.get(r['source'],0)+1
    deg[r['target']] = deg.get(r['target'],0)+1
orphans = [s['name'] for s in skills if s['name'] not in deg]
print(f"\nÓRFÃOS (0 arestas) no catálogo: {len(orphans)}")
for o in orphans: print("   -", o)