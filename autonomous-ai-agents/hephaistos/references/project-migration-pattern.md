# Project Migration Pattern

> Workflow para migrar projetos existentes para a estrutura padrão Hephaistos v3.1.

## Quando Usar

- Projeto existe mas não segue a estrutura padrão
- Projeto foi criado em outra ferramenta (Figma Make, V0, etc.)
- Projeto precisa ser integrado ao vault Hephaistos

## Estrutura Padrão de Projeto

```
projetos/{nome}/
├── _contexto/
│   ├── estado-atual.md      → Status do projeto
│   ├── fio-do-projeto.md    → Historico
│   ├── decisoes-tomadas.md  → Decisoes tecnicas
│   └── instrucoes-ai.md     → Instrucoes para IAs
│
├── _compact/
│   ├── projeto.md           → Resumo executivo
│   └── tech.md              → Stack tecnico
│
├── visao/
│   ├── visao.md             → Proposito
│   ├── publico.md           → Personas
│   ├── roadmap.md           → Fases
│   └── briefing.md          → Briefing inicial
│
├── arquitetura/
│   ├── stack.md             → Stack escolhido
│   ├── adr.md               → Decisoes tecnicas
│   └── api.md               → API do projeto
│
├── design/
│   ├── research/
│   │   ├── moodboards/      → Moodboards HTML
│   │   └── referencias/     → Referencias visuais
│   ├── specs/
│   │   └── design-system.html
│   └── wireframes/
│       └── prototipo.html
│
├── src/                     → Codigo fonte
├── docs/                    → Documentacao
└── engramas/                → Conhecimento do projeto
```

## Workflow de Migração

### 1. Criar Estrutura de Diretórios

```bash
# Criar todas as pastas necessárias
mkdir -p projetos/{nome}/{_contexto,_compact,visao,arquitetura,design/{research/{moodboards,referencias},specs,wireframes},src,docs,engramas}
```

### 2. Mover Arquivos Existentes

```bash
# Mover arquivos para as pastas corretas
# _contexto/ → _contexto/
# visao/ → visao/
# arquitetura/ → arquitetura/
# design/ → design/
```

### 3. Criar Arquivos Ausentes

Para cada pasta, criar os arquivos padrão se não existirem:

- `_contexto/estado-atual.md` — Status atual
- `_contexto/fio-do-projeto.md` — Historico
- `_compact/projeto.md` — Resumo executivo
- `visao/briefing.md` — Briefing inicial

### 4. Atualizar Wikilinks

Verificar e corrigir wikilinks que referenciam o projeto antigo.

### 5. Verificação Final

```bash
# Verificar estrutura
find projetos/{nome} -type d | sort

# Verificar arquivos
find projetos/{nome} -name "*.md" -type f | wc -l
```

## Exemplo Praticado

**Migração em 2026-06-17:**

| Projeto | Antes | Depois | Arquivos |
|---------|-------|--------|----------|
| hermes-flatpak | Estrutura parcial | Estrutura completa | 13 |
| jogo-da-solidariedade | Estrutura parcial | Estrutura completa | 8 |
| sergipetec | Apenas 1 arquivo | Estrutura completa | 1 |
| peachweb | 3 engramas soltos | Estrutura completa | 3 |

## Regras

1. **NÃO misturar dados de projeto com conhecimento geral** — engramas de projeto ficam em `projetos/{nome}/engramas/`, não em `engramas/`
2. **Manter separação entre projetos** — cada projeto é autônomo
3. **Atualizar `_contexto/estado-atual.md`** — sempre que mudar o status
4. **Documentar decisões** — em `decisoes-tomadas.md`
