# Awwwards Research & UI Polish Workflow

> Como pesquisar referências de design em sites premiados, extrair dados da biblioteca de coleções, e traduzir em plano de implementação.

## Quando Usar

- Projeto já existe e precisa de polimento visual
- Usuário pede "melhorar a interface" ou "deixar mais profissional"
- Antes de implementar features visuais novas (animações, transições, data viz)
- **Pesquisa massiva da biblioteca Awwwards Collections** (100+ coleções)
- Extração de padrões, tendências e referências categorizadas

## Fontes

| Fonte | URL | O que Coletar |
|-------|-----|--------------|
| Awwwards Collections | `awwwards.com/collections/` + `?page=N` | Coleções completas com descrição, curador, itens, seguidores |
| Awwwards Websites | `awwwards.com/websites/[categoria]` | Padrões premiados, categorias, scores, tags |
| SiteInspire | `siteinspire.com` | Curadoria limpa, busca por keyword |

Keywords: `dark-mode`, `data-visualization`, `microinteractions`, `animation`, `minimal`, `webgl`, `three-js`, `typography`

---

## Workflow — Extração Massiva de Collections (100+ Coleções)

Quando o objetivo é catalogar a biblioteca completa de coleções do Awwwards para gerar um documento de referência enciclopédico.

### Arquitetura Recomendada

```
Sprint 0: Mapear URLs (pagination: ?page=1..N)
  ↓
Sprint 1-4: Extrair detalhes de cada coleção (25 por sprint)
  ↓
Sprint 5: Compilar documento massivo categorizado
```

### Sprint 0: Mapeamento

A listagem de coleções usa **paginação explícita** (`?page=N`), não scroll infinito. Cada página carrega ~12-13 coleções. O header mostra o total (ex: "Collections132").

```python
# Seletor para extrair nome + URL de cada coleção
selector = "h3 a[href*='collections']"
# Remover sufixo "View Collection" do textContent
```

**Total real:** ~100 coleções únicas (não 132 como o header sugere — diferença inclui coleções privadas ou duplicadas).

### Sprint 1-4: Extração Detalhada

Para cada coleção individual, visitar a URL e extrair:

```markdown
## [Nome da Coleção]
- **URL:** [URL completa]
- **Descrição:** [Texto de descrição da página, se houver]
- **Curador:** [Autor — awwwards.] para oficiais, [username] para comunitárias
- **Itens:** [Número exato do header]
- **Seguidores:** +[Número]
- **Sites exemplares:** [10+ nomes de sites com autor/agência entre parênteses]
- **Recursos principais:** [Lista de capacidades, tecnologias, patterns]
- **Estilo visual:** [Descrição do estilo estético predominante]
```

**Estrutura consistente de cada collection page:**
- Header com título, descrição, curador (avatar + link), botão Follow
- Contagem de itens e seguidores
- Grid de itens (cada um com preview em vídeo ou imagem, título, autor)
- Badges: PRO, SOTD, SOTM, SOTY, DEV, HM
- Paginação/lazy loading para ver mais itens

### Fallback para Coleta (quando delegate_task falha)

**Problema:** Tasks de pesquisa web com 25+ URLs via `delegate_task` podem ser **interrompidas** (exit_reason: "interrupted") devido ao limite de tokens do modelo ou timeout do provider (DeepSeek Flash). AGY CLI via terminal também pode **desviar para outro projeto** se houver contexto residual de sessão anterior.

**Fluxo de fallback comprovado:**

```python
# 1. TENTAR delegate_task com batch pequeno (10-15 URLs máx)
delegate_task(tasks=[{...}])  # pode falhar para modelos limitados

# 2. Se falhar (interrupted), TENTAR AGY via terminal com --print
agy --model="Claude Sonnet 4.6" --print --print-timeout=10m --dangerously-skip-permissions '[INSTRUÇÕES]'

# 3. Se AGY desviar para outro projeto, FALLBACK: navegação direta
#    Visitar cada URL sequencialmente com browser_navigate
browser_navigate(url)
#    Extrair dados manualmente de cada página

# 4. NUNCA fabricar dados de coleções não visitadas
#    Se uma URL falhou, reportar como bloqueada
```

**AGS falha conhecida:** AGY pode usar contexto de workspace de sessão anterior e executar a tarefa no projeto errado (ex: foi solicitar pesquisa Awwwards mas executou no Desconsultor). Sempre verificar o output do AGY antes de confiar.

### Organização dos Dados

```markdown
# Documento Massivo

## Índice
1. Categoria: Design Visual & Estilo
2. Categoria: Animação & Movimento
3. Categoria: Tecnologia & Desenvolvimento
...

## Estatísticas Gerais
- Total de coleções: 100
- Maior coleção: [Nome] — [N] itens
- Coleção mais seguida: [Nome] — [N] seguidores
- Curador principal: awwwards. (~75 coleções)

## Links
- Página 1: ?page=1
- Página N: ?page=N
```

---

## Workflow — Polimento de UI (Projetos Existentes)

1. Visitar o site atual primeiro (entender seções, hierarquia, problemas)
2. Navegar Awwwards por categoria relevante
3. Para cada site, extrair: descrição, paleta, tags, score, padrões úteis
4. Mapear: o que o premiado tem × o que o projeto não tem
5. Priorizar por impacto × esforço
6. Delegar implementação ao agy

## Padrões Comuns Implementáveis

Clip-path reveal, scroll spy com IntersectionObserver, slide-up modal, hover glow que segue o mouse. Ver código no corpo do skill Hephaistos (seção Pitfalls).

## Pitfalls

- **NUNCA implementar design visual diretamente** — delegar ao agy
- **NUNCA criar diretorio separado em `projetos/` para melhorias do Hephaistos** — o vault do Hephaistos e o projeto. Melhorias vao diretamente para `engramas/`, `_contexto/`, e a skill. `projetos/` e apenas para clientes.
- **SEMPRE verificar `_contexto/arquitetura-cognitiva.md` antes de propor trabalho ON Hephaistos** — o plano de fases ja existe (Fases 1-4). Nao invente sprints novas.
- **SEMPRE verificar se artefatos ja existem antes de propor cria-los** — moodboard.html e prototipo.html ja existem em `projetos-test/componentes-design-system/design/html/`.
- **Sites 404 no Awwwards** — slugs mudam, voltar à lista
- **Dribbble/Behance bloqueiam headless** — usar Awwwards + SiteInspire
- **Respeitar o design system do projeto**, não o da referência
- **delegate_task com muitas URLs é frágil** — batch de 25+ URLs via delegate_task pode ser interrompido. Preferir batches de 10-15 URLs máx, ou navegação direta sequencial para tarefas críticas
- **AGY pode desviar de contexto** — quando chamado via `terminal("agy --print 'prompt'")`, o AGY pode herdar contexto de workspace de sessão anterior e executar no projeto errado. Sempre prefixar com `--add-dir <path>` explícito e verificar o output antes de confiar.
- **Contagem do header pode ser imprecisa** — o header "Collections132" não corresponde ao número real de coleções públicas (~100). Algumas coleções podem ser privadas, deletadas ou duplicadas entre páginas.
- **Página 4+ pode falhar** — o site pode rate-limit ou redirecionar para página em branco após muitas requisições. Se página N+ falhar (snapshot <6000 chars), assumir que o total real de coleções foi atingido.
