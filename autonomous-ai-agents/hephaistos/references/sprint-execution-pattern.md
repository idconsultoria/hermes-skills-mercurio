# Sprint Execution Pattern

## Visão Geral

Quando o usuário autoriza "rodar a próxima sprint", execute o trabalho usando **delegate_task em paralelo** (máx 3 subagentes por batch).

## Fluxo

1. **Ler SPRINTS.md** — identificar a sprint pendente e suas tarefas planejadas
2. **Dividir em 2-3 frentes** — cada frente vira um `delegate_task(tasks=[...])`
3. **Cada subagente pesquisa + cria arquivos** — web_search + write_file
4. **Verificar wikilinks** — corrigir links quebrados inventados por subagentes
5. **Atualizar índice** — patch no `engramas/recursos/index.md` (ou equivalente)
6. **Marcar sprint como completa** no SPRINTS.md (tabela + seção detalhada)
7. **Atualizar estado-atual.md**

## Regra de Delegação

```python
# Máximo 3 subagentes por batch
delegate_task(tasks=[
    {"goal": "Pesquisar e criar engramas [lote 1]", "toolsets": ["web", "file", "terminal"]},
    {"goal": "Pesquisar e criar engramas [lote 2]", "toolsets": ["web", "file", "terminal"]},
    {"goal": "Pesquisar e criar engramas [lote 3]", "toolsets": ["web", "file", "terminal"]},
])
```

Se a sprint tem mais de 3 lotes, usar 2 batches sequenciais.

## Contexto para Subagentes

Incluir no `context` de cada subagente:
- Caminho exato do vault: `/home/taciobrito/vaults/hephaistos/engramas/recursos/`
- Formato do engrama: frontmatter YAML, max 100 linhas, wikilinks, "Links Relacionados"
- Tom: técnico, direto, sem emojis
- **Nomes dos wikilinks que existem no vault** (evitar links quebrados)
- Instrução explícita: "Nao crie indices — apenas os arquivos .md"

## Pós-Execução

Após cada batch de delegate_task:
1. Verificar arquivos criados: `ls -1 vault/engramas/recursos/engrama-*`
2. Verificar wikilinks quebrados: `grep -r "engrama-XYZ" vault/engramas/ | wc -l`
3. Corrigir com `patch(replace_all=True)` se necessário
4. Atualizar `index.md` com novas entradas (usar `patch()` para inserir após a entrada anterior)
5. Atualizar contagem no index (ex: "109 engramas" → "121 engramas")

## Atualização do SPRINTS.md

Após concluir a sprint, atualizar **três** locais no SPRINTS.md:

1. **Tabela resumo** (topo do arquivo): marcar status como ✅ Completa + resultado
   ```
   | **Sprint N** | Foco | ✅ Completa | +X engramas |
   ```

2. **Seção detalhada** da sprint: marcar `**Status:** ✅ Completa`

3. **Adicionar seção "Resultado"** antes da próxima sprint:
   ```markdown
   ## Resultado

   X engramas criados em `engramas/recursos/`:

   | Engrama | Foco |
   |---------|------|
   | engrama-foo | Descricao |
   | engrama-bar | Descricao |
   ```

4. **Atualizar `estado-atual.md`** com novo total de .md e sprint atual

## Preferência do Usuário: Perspectiva de Aprendiz

Quando o usuário pede para documentar plataformas/ferramentas/criadores com foco em "aprender", ele quer **cobertura completa**, não resumos superficiais. Para cada item documentado, incluir:

1. **Ferramentas que usa/recomenda** — nomes, como funcionam
2. **Como funciona** — workflow prático, passo a passo
3. **Metodologias que segue** — frameworks, abordagens
4. **Insights e dicas** — o que aprender primeiro, erros comuns
5. **Formatos de trabalho** — como estruturar projetos, apresentar resultados

Exemplo de correção do usuário: "a finalidade é saber quais são as ferramentas que essas plataformas tem, como elas funcionam, as metodologias adotadas, os insights e dicas, referências disponibilizadas... agir como uma pessoa querendo aprender"

## Sprint de Limpeza/Verificação

Quando o vault precisa de limpeza after sprints de criação, usar este workflow:

### Auditoria Inicial

```bash
# 1. Arquivos com espaços no nome
find vault/engramas/ -name "* *" -type f | wc -l

# 2. Arquivos muito curtos (<10 linhas)
find vault/engramas/ -name "*.md" ! -name "index.md" -type f -exec sh -c 'lines=$(wc -l < "$1"); if [ "$lines" -lt 10 ]; then echo "$1"; fi' _ {} \;

# 3. Arquivos muito longos (>200 linhas)
find vault/engramas/ -name "*.md" ! -name "index.md" -type f -exec sh -c 'lines=$(wc -l < "$1"); if [ "$lines" -gt 200 ]; then echo "$1"; fi' _ {} \;

# 4. Wikilinks quebrados
grep -roh '\[\[engrama-[^]]*\]\]' vault/engramas/ 2>/dev/null | sort | uniq -c | sort -rn | while read count link; do
  name=$(echo "$link" | sed 's/\[\[//;s/\]\]//')
  found=$(find vault/ -name "${name}.md" -type f 2>/dev/null | head -1)
  if [ -z "$found" ]; then echo "$link ($count refs)"; fi
done

# 5. MOCs/índices vazios
find vault/ -name "MOC*" -type f -empty
```

### Rename de Arquivos

```bash
# Renomear espaços → hifens, lowercase
find vault/engramas/ -name "* *" -type f | while read file; do
  dir=$(dirname "$file")
  base=$(basename "$file")
  newname=$(echo "$base" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  mv "$file" "$dir/$newname"
done
```

### Correção de Wikilinks

Mapear links quebrados para seus destinos corretos:

```python
# Exemplo de mapeamento
fixes = {
    "engrama-shadcn-ui": "shadcn-ui",
    "engrama-claude-designers": "claude-para-designers",
    "engrama-radix-ui": "radix-ui",
    "engrama-vibe-coding": "vibe-coding",
}

for old, new in fixes.items():
    grep -rl "[[$old]]" vault/engramas/ | while read file; do
        sed -i "s/\[\[$old\]\]/[[$new]]/g" "$file"
    done
```

Para wikilinks sem correspondência, remover a linha inteira:

```bash
grep -rl "\[\[engrama-nonexistent\]\]" vault/engramas/ | while read file; do
    sed -i "/\[\[engrama-nonexistent\]\]/d" "$file"
done
```

### Condensação de Arquivos Longos

Para arquivos >200 linhas (ex: Pesquisa_lovable.md com 660 linhas):

1. **Ler o arquivo completo** — identificar seções principais
2. **Delegar criação de engramas atômicos** — cada seção vira 1 engrama (max 100 linhas)
3. **Deletar o arquivo original** — substituído pelos engramas atômicos
4. **Atualizar índice** — adicionar novos engramas ao index.md

```python
# Exemplo: 660 linhas → 3 engramas
delegate_task(tasks=[{
    "goal": "Ler Pesquisa_lovable.md e criar 3 engramas atômicos",
    "context": "Arquivo tem 660 linhas sobre Lovable. Criar: engrama-lovable-architecture.md, engrama-lovable-design-system.md, engrama-lovable-visual-edits.md. Deletar original.",
    "toolsets": ["file", "terminal"]
}])
```

### Pós-Limpeza

Verificação final:

```bash
# Todos os checks devem retornar 0
echo "Arquivos com espaços: $(find vault/engramas/ -name '* *' -type f | wc -l)"
echo "Wikilinks quebrados: $(grep -roh '\[\[engrama-[^]]*\]\]' vault/engramas/ 2>/dev/null | sort | uniq -c | ... | wc -l)"
echo "Arquivos vazios: $(find vault/ -name "MOC*" -type f -empty | wc -l)"
echo "Total .md: $(find vault/ -name '*.md' -type f | wc -l)"
```

## Separação de Dados: Projeto vs Arquitetura

**Regra fundamental:** Dados de projeto (briefing, design, código, deploy) NÃO se misturam com dados de arquitetura/memoria (engramas, skills, metodologias).

### Estrutura Correta

```
hephaistos/
├── _contexto/           → META-FRAMEWORK (estado, decisoes, instrucoes)
├── _compact/            → RESUMOS COMPACTOS (para contexto de IA)
├── visao/               → VISAO ESTRATEGICA
├── arquitetura/         → ARQUITETURA TECNICA
├── projetos/            → PROJETOS (autonomos)
│   ├── projeto-a/
│   │   ├── _contexto/
│   │   ├── visao/
│   │   ├── arquitetura/
│   │   ├── design/
│   │   ├── src/
│   │   └── engramas/    → Conhecimento ESPECIFICO do projeto
│   └── projeto-b/
└── engramas/            → CONHECIMENTO GERAL (nao-projeto)
    ├── design/
    ├── infraestrutura/
    ├── orquestracao/
    ├── ia-agentes/
    └── recursos/
```

### O que vai em cada lugar

| Tipo de dado | Onde vai | Exemplo |
|--------------|----------|---------|
| Briefing do projeto | `projetos/{nome}/visao/briefing.md` | Briefing do Jogo da Solidariedade |
| Design system do projeto | `projetos/{nome}/design/specs/` | Design system HTML do projeto |
| Metodologia de design | `engramas/design/` | `engrama-design-tokens.md` |
| Ferramenta específica | `engramas/recursos/` | `engrama-security-owasp-top-10.md` |
| Decisão arquitetural | `projetos/{nome}/arquitetura/adr.md` | ADR do projeto |
| Decisão do framework | `_contexto/decisoes-tomadas.md` | Decisão sobre pipeline |

### Quando mover engrama de projeto para engramas gerais

Um engrama que começou em `projetos/{nome}/engramas/` pode ser promovido para `engramas/` quando:
1. **Múltiplos projetos o utilizam** — se 2+ projetos referenciam o mesmo engrama
2. **É conhecimento genérico** — não depende de dados específicos do projeto
3. **Outros usuários se beneficiariam** — é relevante para qualquer projeto similar

### Quando manter engrama no projeto

Mantenha em `projetos/{nome}/engramas/` quando:
1. **Dados específicos do projeto** — briefing, personas, decisões de design
2. **Referências visuais do projeto** — moodboards, screenshots, assets
3. **Configurações técnicas do projeto** — stack, deploy, variáveis de ambiente

## Preferência do Usuário: Dados Irrelevantes

**Dados de pricing/preços são irrelevantes** para o vault de conhecimento. O usuário corrigiu explicitamente quando engramas continham tabelas de preços ($12-75/seat, $499/mes, etc.).

### O que NÃO documentar

- Tabelas de preços de ferramentas/SaaS
- Comparativos de custo entre soluções
- Informações de assinatura/mensalidade
- Descontos, promoções, planos

### O que documentar (mesmo sendo "preço")

- **Modelo de negócio** — como a ferramenta monetiza (freemium, open-source, enterprise)
- **Tier gratuito** — o que está disponível sem pagar
- **Diferencial vs concorrência** — por que escolher esta ferramenta

**Razão:** O vault é um repositório de conhecimento técnico, não um catálogo de compras. Informações de preço mudam frequentemente e não agregam valor ao conhecimento de como usar a ferramenta.
