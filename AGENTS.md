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
├── reports/           ← Planos de evolução + relatórios pós-evolução
│   ├── evolve-<YYYY-MM-DD-HHMM>.md        ← plano (pré-execução)
│   └── evolve-<YYYY-MM-DD>-report.md      ← relatório (pós-execução)
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

**Quando atualizar:** a cada operação `update` ou `evolve`. O index.md é a fonte da verdade para planejamento de consolidação.

---

## log.md — Diário Cronológico

**Função:** Append-only. Cada operação no repositório vira uma entrada.

**Formato padronizado:**

```
## [YYYY-MM-DD] update | Descrição concisa
## [YYYY-MM-DD] evolve | Descrição concisa
```

Cada entrada começa com `## [YYYY-MM-DD]` seguido de um prefixo de operação e uma descrição.

**Prefixos padronizados:**

| Prefixo | Operação |
|---------|----------|
| `update` | Sincronização do index.md com o estado atual das skills |
| `evolve` | Etapa de consolidação inteligente — merges, deletes, órfãos, relações, grafo |
| `offload` | Limpeza de memória — remoção de fatos redundantes com skills |

O formato é parseável com Unix tools:
```bash
grep "^## \[" log.md | tail -5   # últimas 5 entradas
grep "evolve" log.md               # só etapas evolve
```

---

## Operações

### update

Sincronização do index.md com o estado atual das skills. Executado quando:
- O repositório é inicializado (first seed)
- Skills são adicionadas ou removidas manualmente
- Metadados de skills mudam

**Método:** O index.md evolui commit a commit — nunca é regenerado do zero. O agente usa `git diff` entre o último commit e o estado atual para detectar skills adicionadas, removidas ou com metadados alterados, depois aplica patches cirúrgicos no index.md existente usando ferramentas LLM (`read_file`, `patch`, `write_file`). Cada commit adiciona uma camada ao index.md sem destruir o histórico.

**Passos:**
1. **Verifica mudanças no repositório** via `git status` e `git diff` entre o último commit e o estado atual — skills adicionadas, removidas, modificadas ou com metadados alterados. Este diff é o ponto de partida para saber o que precisa ser atualizado no index.md.
2. Escaneia todas as skills no repositório
3. Regera o index.md completo (adiciona, edita, remove entradas)
4. Registra no log.md com prefixo `update` incluindo o resumo
5. **Audita conformidade de descrições** — varre todas as SKILL.md e verifica se cada uma está no formato esperado:
   - **Sumário de uma linha (~80 chars):** descrição concisa do que a skill faz, sem truncamentos (sem `...`). Deve ser auto-contido: quem lê entende na hora se deve carregar a skill ou não.
   - **Parágrafo de resumo:** explica os gatilhos de ativação (\"Load this skill when...\") e expande a descrição com capacidades específicas, ferramentas que utiliza e o que produz. Não é o corpo inteiro da skill — é um resumo informativo que alimenta o index.md.
   - Lista **todas as skills fora do formato** com o problema específico, edita a SKILL.md original para corrigir, depois atualiza o index.md com as descrições corrigidas.
   - Faz isso para **todas as skills fora do formato**, sem exceção.
6. Stage + commit

### evolve

Etapa de consolidação inteligente do ciclo de consolidação. Analisa o portfólio e propõe merges, remoções e spin-offs para manter as skills **MECE** (Mutually Exclusive, Collectively Exhaustive).

**Critério de merge:** Duas skills conectadas (similar/uses) só devem permanecer separadas se descreverem fluxos de trabalho realmente distintos — que não podem ou não faz sentido incorporar um ao outro. Se ambas descrevem o mesmo domínio com padrões de orquestração idênticos, devem ser fundidas. Se operam em níveis de abstração diferentes (receita técnica vs workflow estratégico) ou com toolchains fundamentalmente distintas, devem permanecer separadas. A conexão no grafo (`similar`, `uses`) é evidência, não sentença — o julgamento final é sobre o workflow descrito.

**Passos:**
1. **Lista** mudanças de skills desde o último ciclo
2. **Atualiza** o index.md com as mudanças
3. **Registra** no log.md
4. **Stage + commit** (checkpoint pré-plano)
5. **Estuda** o index.md completo e elabora plano de evolução
6. **Salva** o plano em `reports/evolve-<YYYY-MM-DD-HHMM>.md`
7. **Executa** o plano (merges, deletes, consolidação de conteúdo). Durante a execução:
   - Limpa aprendizados excessivamente específicos das skills — dados de debugging pontual, mensagens de erro de sessões passadas, workarounds temporários, informações transientes que não agregam numa próxima execução do workflow. Mantém o padrão geral, não o caso específico.
   - **Audita descrições das skills** — verifica se cada SKILL.md tem cabeçalhos de descrição adequados: resumo de uma linha (~80 chars) seguido de parágrafo descritivo completo. Skills com descrições ausentes, truncadas ou genéricas demais devem ser corrigidas para que o conteúdo alimente bem o index.md. O resumo é extraído como `summary` e o parágrafo como `description`. Skills já consolidadas (merges) têm prioridade. Skills não modificadas podem ser corrigidas em lote.
8. **Revisa skills órfãs** — skills sem relações no grafo. Para cada uma:
   - Tenta encontrar conexão semântica com outras skills (lendo ambos os SKILL.md). Se encontrar, adiciona relação.
   - Se não encontrar conexão, avalia se a skill é importante o suficiente para existir isolada. Skills genuinamente de nicho (API de terceiros, CLI específico, data source exótico) podem ficar órfãs com justificativa.
   - Se a skill não tem conexão E não é claramente importante, considera merge com skill genérica ou delete.
9. **Escreve relatório denso** em `reports/evolve-<YYYY-MM-DD>-report.md` com:
   - Estado inicial vs final (skills, memória, disco)
   - Tabela de deleções com motivos
   - Tabela de merges com o que foi absorvido
   - Git diff summary
   - **Lista de skills órfãs** e decisão tomada (relacionada / justificada como nicho / deletada)
10. **Atualiza** o index.md pós-transformação
11. **Registra** no log.md com prefixo `evolve`
12. **Gera grafo HTML interativo** — extrai dados do index.md, constrói grafo D3.js com relações (similar/uses/used_by/parent), salva em `skills_graph.html` na raiz do repositório. Nós coloridos por categoria, arestas tracejadas para similar e sólidas com seta para uses. Modal com summary + description ao clicar no nó. Responsivo para mobile.
13. **Stage + commit** final

### offload

Limpeza de memória após a etapa evolve do ciclo de consolidação. Remove entradas da memória persistente que estejam redundantes com skills (ex: configurações de ferramentas, procedimentos, paths de instalação — tudo que deveria viver em skill em vez de memória).

**Regra:** memória guarda preferências do usuário e fatos estáveis do ambiente. Skills guardam procedimentos, receitas e workflows. Tudo que é procedural e está numa skill pode sair da memória.

**Passos:**
1. Lista entradas da memória atual
2. Para cada entrada, verifica se existe skill cobrindo o mesmo assunto
3. Se sim, remove da memória (com confirmação do usuário na primeira vez)
4. Registra no log.md com prefixo `offload`

---

## Ciclo de Consolidação

**Não é a mesma coisa que `evolve`.** O ciclo de consolidação é o processo macro que orquestra as operações. É executado periodicamente (a cada N evolves ou sob demanda) e é ele quem inicia os `update` normalmente.

### Etapas do ciclo

```
1. Update          → varre mudanças, audita descrições, sincroniza index.md
2. Log do update   → registra no log.md com prefixo `update`
3. Stage + commit  → checkpoint intermediário
4. Evolve          → análise profunda, merges, órfãos, relações, grafo
5. Log do evolve   → registra no log.md com prefixo `evolve`
6. Offload         → limpa memória redundante com skills
7. Stage + commit  → checkpoint final
```

### Diagrama

```
┌─────────────────────────────────────────────────────┐
│              Ciclo de Consolidação                   │
│                                                      │
│   Update → log → commit → Evolve → log → Offload → commit
│   ───────          ──────          ───────
│   (6 passos)       (13 passos)     (4 passos)
│                                                      │
│   Executado periodicamente — inicia os updates       │
└─────────────────────────────────────────────────────┘
```

### Exemplo de execução

```bash
# Update (passos 1-6 do update)
# Log do update
echo "## [$(date +%F)] update | ..." >> log.md
git commit -m "update: ..."

# Evolve (passos 1-13 do evolve)
# Log do evolve  
echo "## [$(date +%F)] evolve | ..." >> log.md
git commit -m "evolve: ..."

# Offload (passos 1-4 do offload)
# Log do offload
echo "## [$(date +%F)] offload | ..." >> log.md
git commit -m "offload: ..."
```

---

## Convenções de Commit

- `update: <descrição>` — para atualizações de índice
- `evolve: <descrição>` — para ciclos de consolidação
- `init: <descrição>` — para commits iniciais
