# Skills Repository — Management Guide

Este repositório gerencia o catálogo de skills do Hermes Agent via Git.

## ⚠️ Regra absoluta: index.md é território de agente LLM

**É proibido editar `index.md` com scripts** — seja regeneração automática via Python, sed, awk, scripts de shell, ou qualquer outra automação programática que escreva diretamente no arquivo. O `index.md` deve ser mantido **exclusivamente por ferramentas de agente LLM** (`read_file`, `write_file`, `patch`), garantindo que cada decisão editorial (merge de skills, ajuste de descrições, criação de relações) passe por julgamento humano-assistido.

**Scripts são permitidos para tarefas de apoio** — análise de conexões, extração de metadados, estatísticas, geração do grafo HTML, e qualquer processamento que informe o agente sem escrever no `index.md`. O output desses scripts alimenta o raciocínio do agente, que então edita o `index.md` manualmente com as ferramentas apropriadas.

## Estrutura

```
skills/
├── AGENTS.md          ← Este arquivo — regras do repositório
├── index.md           ← Catálogo orientado a conteúdo (sempre atualizado)
├── log.md             ← Diário cronológico append-only de operações
├── reports/           ← Planos e relatórios gerados pela etapa evolve
│   ├── evolve-<YYYY-MM-DD-HHMM>.md        ← plano (pré-execução do evolve)
│   └── evolve-<YYYY-MM-DD>-report.md      ← relatório (pós-execução do evolve)
└── <category>/
    └── <skill-name>/
        ├── SKILL.md
        └── references/
```

---

## index.md — Catálogo Orientado a Conteúdo

**Função:** Lista exaustiva de todas as skills, com metadados e relacionamentos.

Cada skill é registrada com:

| Campo | Descrição |
|-------|-----------|
| **name** | Nome da skill (path relativo) |
| **title** | Título do SKILL.md |
| **file** | Caminho para o SKILL.md |
| **size** | Tamanho em caracteres do SKILL.md |
| **summary** | Resumo de 1 linha (~80 chars) |
| **description** | Parágrafo descritivo (extraído do SKILL.md) |
| **category** | Categoria de diretório |
| **relations** | Outras skills relacionadas (parent, child, similar, uses, used_by) |

**Quando atualizar:** a cada `update` ou `evolve` dentro do ciclo de consolidação. O index.md é a fonte da verdade para o ciclo de consolidação.

---

## log.md — Diário Cronológico

**Função:** Append-only. Cada operação do ciclo de consolidação vira uma entrada.

**Formato padronizado:**

```
## [YYYY-MM-DD] update | Descrição concisa
## [YYYY-MM-DD] evolve | Descrição concisa
```

Cada entrada começa com `## [YYYY-MM-DD]` seguido do prefixo da etapa e uma descrição.

**Prefixos padronizados (etapas do ciclo de consolidação):**

| Prefixo | Etapa |
|---------|-------|
| `update` | Sincronização do index.md com o estado atual das skills |
| `evolve` | Consolidação inteligente — merges, deletes, órfãos, relações, grafo |
| `offload` | Limpeza de memória — remoção de fatos redundantes com skills |

O formato é parseável com Unix tools:
```bash
grep "^## \[" log.md | tail -5   # últimas 5 entradas do ciclo
grep "evolve" log.md              # só etapas evolve
```

---

## Ciclo de Consolidação (macro)

**Não é uma etapa. É o processo que orquestra as etapas.** O ciclo de consolidação é executado periodicamente (a cada N evolves ou sob demanda). Ele inicia os `update` e coordena a sequência completa:

### Sequência do ciclo

```
1. Update          → detecta mudanças, audita descrições, sincroniza index.md
2. Log             → registra o update no log.md
3. Commit          → checkpoint intermediário
4. Evolve          → análise profunda: merges, órfãos, relações, grafo
5. Log             → registra o evolve no log.md
6. Offload         → limpa memória redundante com skills
7. Commit          → checkpoint final
```

### Exemplo de execução

```bash
# --- Etapa: Update ---
# (executa os 6 passos da seção ## update abaixo)

# --- Log do update ---
echo "## [$(date +%F)] update | ..." >> log.md
git commit -m "update: ..."

# --- Etapa: Evolve ---
# (executa os 13 passos da seção ## evolve abaixo)

# --- Log do evolve ---
echo "## [$(date +%F)] evolve | ..." >> log.md
git commit -m "evolve: ..."

# --- Etapa: Offload ---
# (executa os 4 passos da seção ## offload abaixo)

# --- Log do offload ---
echo "## [$(date +%F)] offload | ..." >> log.md
git commit -m "offload: ..."
```

### Diagrama

```
┌───────────────────────────────────────────────────────┐
│                 Ciclo de Consolidação                  │
│                                                       │
│   Update ──→ Log ──→ Commit ──→ Evolve ──→ Log ──→ Offload ──→ Commit
│   (6 passos)           (13 passos)           (4 passos)
│                                                       │
│   As 3 etapas sempre rodam nesta ordem,               │
│   formando um ciclo completo. Cada etapa               │
│   tem seu próprio prefixo no log.md.                   │
└───────────────────────────────────────────────────────┘
```

---

## Etapas do Ciclo

Cada seção abaixo descreve uma das etapas que compõem o ciclo de consolidação.
Elas sempre executam na ordem: **update → evolve → offload**.

### update

Sincronização do index.md com o estado atual das skills. Executado quando:
- O repositório é inicializado (first seed)
- Skills são adicionadas ou removidas manualmente
- Metadados de skills mudam

**Método:** O index.md evolui commit a commit — nunca é regenerado do zero. O agente usa `git diff` entre o último commit e o estado atual para detectar skills adicionadas, removidas ou com metadados alterados, depois aplica patches cirúrgicos no index.md existente usando ferramentas LLM (`read_file`, `patch`, `write_file`). Cada commit adiciona uma camada ao index.md sem destruir o histórico.

**Passos:**
1. **Verifica mudanças no repositório** via `git status` e `git diff` entre o último commit e o estado atual — skills adicionadas, removidas, modificadas ou com metadados alterados. Este diff é o ponto de partida para saber o que precisa ser atualizado no index.md.
2. Escaneia todas as skills no repositório
3. Atualiza o index.md com as mudanças detectadas (adiciona, edita, remove entradas via patches cirúrgicos)
4. **Audita conformidade de descrições** — varre todas as SKILL.md e verifica se cada uma está no formato esperado:
   - **Sumário de uma linha (~80 chars):** descrição concisa do que a skill faz, sem truncamentos (sem `...`). Deve ser auto-contido: quem lê entende na hora se deve carregar a skill ou não.
   - **Parágrafo de resumo:** explica os gatilhos de ativação ("Load this skill when...") e expande a descrição com capacidades específicas, ferramentas que utiliza e o que produz. Não é o corpo inteiro da skill — é um resumo informativo que alimenta o index.md.
   - Lista **todas as skills fora do formato** com o problema específico, edita a SKILL.md original para corrigir, depois atualiza o index.md com as descrições corrigidas.
   - Faz isso para **todas as skills fora do formato**, sem exceção.
5. Registra no log.md com prefixo `update` incluindo o resumo de tudo que foi alterado
6. Stage + commit

---

### evolve

**Esta é uma etapa do ciclo de consolidação.** Ela executa DEPOIS do update e ANTES do offload.

A etapa evolve analisa o portfólio e propõe merges, remoções e spin-offs para manter as skills **MECE** (Mutually Exclusive, Collectively Exhaustive).

**Critério de merge:** Duas skills conectadas (similar/uses) só devem permanecer separadas se descreverem fluxos de trabalho realmente distintos — que não podem ou não faz sentido incorporar um ao outro. Se ambas descrevem o mesmo domínio com padrões de orquestração idênticos, devem ser fundidas. Se operam em níveis de abstração diferentes (receita técnica vs workflow estratégico) ou com toolchains fundamentalmente distintas, devem permanecer separadas. A conexão no grafo (`similar`, `uses`) é evidência, não sentença — o julgamento final é sobre o workflow descrito.

**Passos:**
1. **Estuda** o index.md completo e elabora plano de evolução
2. **Salva** o plano em `reports/evolve-<YYYY-MM-DD-HHMM>.md`
3. **Executa** o plano (merges, deletes, consolidação de conteúdo). Durante a execução:
   - Limpa aprendizados excessivamente específicos das skills — dados de debugging pontual, mensagens de erro de sessões passadas, workarounds temporários, informações transientes que não agregam numa próxima execução do workflow. Mantém o padrão geral, não o caso específico.
   - **⚠️ NÃO remover informações operacionais reutilizáveis entre runs:** números de contato (telefones, WhatsApp JIDs/LIDs, group IDs), IDs de usuário, endereços de email usados para coleta periódica, tokens de acesso a serviços, chaves de API, URLs de webhook, ou qualquer identificador que o workflow precise consultar novamente em execuções futuras. Só remova o que for estritamente inutilizável (ex: estado temporário de uma execução específica, like `session_id` de uma API que expirou, offset/paginação que não se repete). Se um dado pode ser útil em outra run, preserva.
   - **Audita descrições das skills** — verifica se cada SKILL.md tem cabeçalhos de descrição adequados: resumo de uma linha (~80 chars) seguido de parágrafo descritivo completo. Skills com descrições ausentes, truncadas ou genéricas demais devem ser corrigidas para que o conteúdo alimente bem o index.md. O resumo é extraído como `summary` e o parágrafo como `description`. Skills já consolidadas (merges) têm prioridade. Skills não modificadas podem ser corrigidas em lote.
4. **Revisa skills órfãs** — skills sem relações no grafo. Para cada uma:
   - Tenta encontrar conexão semântica com outras skills (lendo ambos os SKILL.md). Se encontrar, adiciona relação.
   - Se não encontrar conexão, avalia se a skill é importante o suficiente para existir isolada. Skills genuinamente de nicho (API de terceiros, CLI específico, data source exótico) podem ficar órfãs com justificativa.
   - Se a skill não tem conexão E não é claramente importante, considera merge com skill genérica ou delete.
5. **Escreve relatório denso** em `reports/evolve-<YYYY-MM-DD>-report.md` com:
   - Estado inicial vs final (skills, memória, disco)
   - Tabela de deleções com motivos
   - Tabela de merges com o que foi absorvido
   - Git diff summary
   - **Lista de skills órfãs** e decisão tomada (relacionada / justificada como nicho / deletada)
6. **Atualiza** o index.md pós-transformação
7. **Registra** no log.md com prefixo `evolve`
8. **Gera grafo HTML interativo** — extrai dados do index.md, constrói grafo D3.js com relações (similar/uses/used_by/parent), salva em `skills_graph.html` na raiz do repositório. Nós coloridos por categoria, arestas tracejadas para similar e sólidas com seta para uses. Modal com summary + description ao clicar no nó. Responsivo para mobile.
9. **Stage + commit** final

---

### offload

**Esta é uma etapa do ciclo de consolidação.** Ela executa DEPOIS do evolve.

Remove entradas da memória persistente que estejam redundantes com skills (ex: configurações de ferramentas, procedimentos, paths de instalação — tudo que deveria viver em skill em vez de memória).

**Regra:** memória guarda preferências do usuário e fatos estáveis do ambiente. Skills guardam procedimentos, receitas e workflows. Tudo que é procedural e está numa skill pode sair da memória.

**Passos:**
1. Lista entradas da memória atual
2. Para cada entrada, verifica se existe skill cobrindo o mesmo assunto
3. Se sim, remove da memória (com confirmação do usuário na primeira vez)
4. Registra no log.md com prefixo `offload`

---

## Convenções de Commit

| Prefixo | Uso |
|---------|-----|
| `update: <descrição>` | Para a etapa update do ciclo de consolidação |
| `evolve: <descrição>` | Para a etapa evolve do ciclo de consolidação |
| `offload: <descrição>` | Para a etapa offload do ciclo de consolidação |
| `init: <descrição>` | Para commits iniciais |

---

## Scripts de Apoio

Scripts vivem em `scripts/` na raiz do repositório. São permitidos exclusivamente para tarefas de apoio que **informam** o agente sem escrever no index.md (conforme a regra absoluta).

### `scripts/generate_graph.py` — Grafo Interativo D3.js

Gera o arquivo `skills_graph.html` com um grafo de força (force-directed graph) interativo a partir dos dados do index.md.

```bash
cd /opt/data/skills
python3 scripts/generate_graph.py              # gera skills_graph.html + graph_data.json
python3 scripts/generate_graph.py --json       # só graph_data.json (sem HTML)
```

**O que faz:**
1. Lê o index.md e extrai as relações de cada skill (blocos `**Relações:**` com formato ``- `tipo` → `path` ``)
2. Se o index.md não tiver relações parseáveis, usa fallback para JSON prévio em `/opt/data/skills_relations_merged.json`
3. Varre todos os SKILL.md do repositório extraindo: nome, título, tamanho, categoria, sumário e descrição
4. Constrói a estrutura de nós e arestas, deduplicando relações bidirecionais
5. Injeta os dados no template `skills_graph_template.html` (substitui `__DATA__` pelos dados JSON)
6. Salva `skills_graph.html` (~60KB, auto-contido, sem dependências externas)

**Saída:**
- `skills_graph.html` — visualização interativa com D3.js (83+ nós, coloridos por categoria, modal ao clicar, filtro por nome)
- `graph_data.json` — dados estruturados para consumo por outros scripts

**Dependências:** Python 3 stdlib (os, re, json, sys, argparse). Nenhum pacote externo.

**Template:** `skills_graph_template.html` na raiz — contém todo o código HTML/CSS/JS do D3.js. O script só substitui o placeholder de dados.

### Adicionar novos scripts

Scripts em Python (.py) ou shell (.sh) vão em `scripts/`. Todo script deve:
- Ser chamado via `python3 scripts/<nome>.py` ou `bash scripts/<nome>.sh`
- Ter docstring ou comentário de uso no topo
- Não escrever no index.md ou SKILL.md — apenas ler e produzir relatórios/arquivos auxiliares
- Ser incluído em ````bash```` na seção apropriada acima se for usado pelo ciclo de consolidação
