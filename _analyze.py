import re, os

with open('/opt/data/skills/index.md') as f:
    content = f.read()

sections = content.split('### ')
skill_names = []
orphans = []
with_relations = []

for s in sections[1:]:
    lines = s.split('\n')
    name_line = [l for l in lines if l.startswith('- **Nome:**')]
    if not name_line:
        continue
    name = name_line[0].split('`')[1]
    
    rel_section = False
    has_rel = False
    rel_count = 0
    for l in lines:
        if '**Relações:**' in l:
            rel_section = True
            continue
        if rel_section and l.strip().startswith('- `'):
            has_rel = True
            rel_count += 1
    
    skill_names.append(name)
    if not has_rel:
        orphans.append(name)
    else:
        with_relations.append((name, rel_count))

total = len(skill_names)
orphan_count = len(orphans)

print(f'Total skills: {total}')
print(f'Skills with relations: {len(with_relations)} ({len(with_relations)/total*100:.0f}%)')
print(f'Orphans (no relations): {orphan_count}')
print()
print('--- ORPHANS ---')
for o in orphans:
    print(f'  - {o}')
print()
print('--- SKILLS WITH FEW RELATIONS (1 only) ---')
for name, count in with_relations:
    if count == 1:
        print(f'  - {name} (1 relation)')
