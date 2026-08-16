import sys
sys.path.insert(0, '/usr/local/searxng')
from searx import settings

engines = settings.get('engines', [])
print('total:', len(engines))
for e in engines:
    print(' ', e.get('name'), '| engine:', e.get('engine'),
          '| disabled:', e.get('disabled'), '| weight:', e.get('weight'),
          '| categories:', e.get('categories'))
