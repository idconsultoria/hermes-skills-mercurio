#!/usr/bin/env python3
"""Checa os limites de chars de MEMORY.md/USER.md de um HERMES_HOME.

Instancia o MemoryStore REAL do Hermes — a contagem, as entradas e o bloqueio são
exatamente os que o agente verá no próximo turno. O sucesso é NÃO aparecer o aviso
"exceeds its char limit on load".

Uso (usa o venv da instalação, com PYTHONPATH apontando para ela):

  HERMES_HOME=/data/data/com.termux/files/home/capitolium PYTHONPATH=/usr/local/lib/hermes-agent \\
    /usr/local/lib/hermes-agent/venv/bin/python check_memory_limits.py

  # ou passando o home como argumento:
  PYTHONPATH=/usr/local/lib/hermes-agent \\
    /usr/local/lib/hermes-agent/venv/bin/python check_memory_limits.py /data/data/com.termux/files/home/capitolium

Saída: para cada alvo (memory, user) chars/limite, nº de entradas, folga ou bloqueio,
e o caminho do arquivo. Exit 1 se algum alvo estiver estourado (adds bloqueados).
Ajuste MEMORY_LIMIT/USER_LIMIT se o config.yaml da instalação usar outros valores.
"""

import logging
import os
import sys

MEMORY_LIMIT = 2200
USER_LIMIT = 1375
INSTALL = os.environ.get("HERMES_INSTALL", "/usr/local/lib/hermes-agent")

logging.basicConfig(level=logging.WARNING, format="LOG %(levelname)s: %(message)s")

if len(sys.argv) > 1:
    os.environ["HERMES_HOME"] = sys.argv[1]
home = os.environ.get("HERMES_HOME")
if not home:
    sys.exit("defina HERMES_HOME (argumento ou variável de ambiente)")

if INSTALL not in sys.path:
    sys.path.insert(0, INSTALL)
import tools.memory_tool as mt  # noqa: E402

store = mt.MemoryStore(MEMORY_LIMIT, USER_LIMIT)
store.load_from_disk()

over = False
for target in ("memory", "user"):
    used = store._char_count(target)
    limit = store._char_limit(target)
    entries = store.memory_entries if target == "memory" else store.user_entries
    path = store._path_for(target)
    state = ("ESTOURADO — adds bloqueados" if used > limit
             else f"ok (folga {limit - used} chars)")
    print(f"{target:>6}: {used:>5}/{limit} chars | {len(entries)} entradas | {state} | {path}")
    over = over or used > limit

print("HERMES_HOME:", home)
sys.exit(1 if over else 0)
