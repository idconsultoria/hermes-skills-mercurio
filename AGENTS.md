# Skills Repository — Management Guide

Este repositório gerencia o catálogo de skills do Hermes Agent via Git.

## Estrutura

```
skills/
├── AGENTS.md          ← Este arquivo — regras do repositório
├── index.md           ← Catálogo orientado a conteúdo (sempre atualizado)
├── log.md             ← Diário cronológico append-only de operações
├── reports/           ← Planos de evolução salvos em markdown
│   └── evolve-<YYYY-MM-DD-HHMM>.md
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
| `update` | Criação/edição manual de index.md (first seed, correções) |
| `evolve` | Ciclo completo de consolidação (plano → execução → offload → commit) |
| `offload` | Limpeza de memória — remoção de fatos redundantes com skills |

O formato é parseável com Unix tools:
```bash
grep "^## \[" log.md | tail -5   # últimas 5 entradas
grep "evolve" log.md               # só ciclos de consolidação
```

---

## Operações

### update

Sincronização do index.md com o estado atual das skills. Executado quando:
- O repositório é inicializado (first seed)
- Skills são adicionadas ou removidas manualmente
- Metadados de skills mudam

**Passos:**
1. Escaneia todas as skills no repositório
2. Regera o index.md completo (adiciona, edita, remove entradas)
3. Registra no log.md com prefixo `update`
4. Stage + commit

### evolve

Ciclo de consolidação inteligente. Analisa o portfólio e propõe merges, remoções e spin-offs para manter as skills **MECE** (Mutually Exclusive, Collectively Exhaustive).

**Passos:**
1. **Lista** mudanças de skills desde o último ciclo
2. **Atualiza** o index.md com as mudanças
3. **Registra** no log.md
4. **Stage + commit** (checkpoint pré-plano)
5. **Estuda** o index.md completo e elabora plano de evolução
6. **Salva** o plano em `reports/evolve-<YYYY-MM-DD-HHMM>.md`
7. **Executa** o plano (merges, deletes, consolidação de conteúdo)
8. **Offload** — limpa da memória persistente informações que já estão documentadas em skills; revisa a memória restante para garantir que só contém fatos não cobertos por skills
9. **Atualiza** o index.md pós-transformação
10. **Registra** no log.md com prefixo `evolve`
11. **Stage + commit** final

### offload

Limpeza de memória após um ciclo evolve. Remove entradas da memória persistente que estejam redundantes com skills (ex: configurações de ferramentas, procedimentos, paths de instalação — tudo que deveria viver em skill em vez de memória).

**Regra:** memória guarda preferências do usuário e fatos estáveis do ambiente. Skills guardam procedimentos, receitas e workflows. Tudo que é procedural e está numa skill pode sair da memória.

**Passos:**
1. Lista entradas da memória atual
2. Para cada entrada, verifica se existe skill cobrindo o mesmo assunto
3. Se sim, remove da memória (com confirmação do usuário na primeira vez)
4. Registra no log.md com prefixo `offload`

---

## Ciclo Completo (exemplo)

```bash
# update
python3 scripts/regenerate_index.py
git add index.md
git commit -m "update: sync index.md with current skills"

# evolve
python3 scripts/regenerate_index.py
git add -A
git commit -m "pre-evolve checkpoint"
# elabora reports/evolve-2026-06-10-1200.md
# executa plano
python3 scripts/regenerate_index.py
git add -A
git commit -m "evolve: merged N skills, removed M, spun off K"
```

---

## Convenções de Commit

- `update: <descrição>` — para atualizações de índice
- `evolve: <descrição>` — para ciclos de consolidação
- `init: <descrição>` — para commits iniciais
