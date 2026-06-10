---
name: cron-newsletter-pipeline
description: "Design and implement automated daily newsletter generation using chained Hermes cron jobs. Covers pipeline architecture (collection → newsletters → synthesis+PDF → ranking delivery), context_from chaining, pre-selection and ranking workflow, minimal-delivery formatting, cron output recovery, and file naming conventions. Use when setting up any cron-based content aggregation and automated newsletter pipeline."
---

# Cron Newsletter Pipeline

Arquitetura e implementação de pipelines automatizados de newsletter diária com Hermes cron jobs encadeados.

## Pipeline Architecture

Uma pipeline típica de newsletter diária usa **3-4 crons encadeados**:

```
04:00 — #1 Coleta de Fontes        (varrer web, Reddit, HN, X, news)
07:30 — #2 Newsletters             (therundown.ai, Superhuman, etc.)
07:50 — #3 Síntese + Ranqueamento + PDF + WhatsApp (entrega principal)
07:55 — #4 Entrega do Ranking      (tabela de ranqueamento .md)
```

### Job #1 — Coleta de Fontes

- **Skills**: `hermes-agent`
- **Deliver**: `local` (output vai para arquivo, não entrega ao usuário)
- **Toolsets**: `terminal`, `web`, `file`
- **Prompt**: Varrer Reddit (RSS), Hacker News (algolia), Google News / web_search, Twitter/X, blogs especializados
- **Output**: salva arquivos .md em `/opt/data/cron/output/`

### Job #2 — Newsletters

- **Skills**: `hermes-agent`
- **Deliver**: `local`
- **Toolsets**: `web`, `file`
- **Prompt**: Extrair conteúdo de newsletters como therundown.ai, Superhuman AI
- **Chaining**: usa `context_from` para receber output do Job #1

### Job #3 — Síntese + PDF

- **Skills**: `newsletter-curation`, `copywriting`, `humanizer`, `html-to-pdf-chromium`
- **Deliver**: `origin` (entrega ao usuário)
- **Toolsets**: `terminal`, `file`
- **Prompt**: Pré-selecionar 20 itens, ranquear, gerar HTML, converter via Chromium, salvar histórico

### Job #4 — Ranking

- **Skills**: nenhuma
- **Deliver**: `origin`
- **Toolsets**: `file`, `terminal`
- **Prompt**: Extrair tabela de ranqueamento do Job #3, salvar como .md, entregar

## Chaining with context_from

Jobs se conectam pelo parâmetro `context_from`:

```python
# Job #2 recebe output do Job #1
cronjob(action='create',
  prompt='...',
  context_from=["b874e9037245"])  # Job ID do Job #1
```

O contexto do job anterior é injetado como "## Output from job 'XXXX'" no início do prompt.

## Minimal Delivery Format

A entrega do cron deve conter APENAS:

1. **Linha 1**: `MEDIA:/caminho/para/arquivo.pdf` (sem texto antes — essencial para anexar no Telegram)
2. **Linha em branco**
3. **Bloco de código WhatsApp** em ```text

```
📰 *IAF — Manhã Aumentada* · (data)

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* [resto normal]

🔥 *Destaques do dia*
• [top 1] — [descrição]
• [top 2] — [descrição]
• [top 3] — [descrição]

🎯 *Aplicação prática:* [1 linha]
```

Sem tabela de ranking, sem metadados extras, sem assinaturas, sem texto adicional.

## File Naming Convention

```
# Arquivos de histórico (salvos no Job #3)
/opt/data/cron/history/iaf_$(date +%Y-%m-%d).html
/opt/data/cron/history/iaf_$(date +%Y-%m-%d).pdf

# Output do cron (salvo automaticamente)
/opt/data/cron/output/<job_id>/<timestamp>.md
```

Usar SEMPRE o formato `iaf_YYYY-MM-DD.pdf` — é o padrão que o usuário aprovou.

## Pre-selection and Ranking Workflow

1. **Ler coletas**: todos os .md em `/opt/data/cron/output/`
2. **Histórico 14 dias**: ler `/opt/data/cron/history/` para deduplicação
3. **Pré-seleção**: 20 itens mais interessantes (não 10-15 que era o padrão antigo)
4. **Ranqueamento**: scores 1-10 em Impacto, Utilidade, Intriga → média simples
5. **Tags**: cada item como `notícia` (news) ou `discussão` (discussion/opinion)
6. **Ordenar**: decrescente por total
7. **Alocar**:
   - Top 3 → Deep Dive (análise expandida)
   - Demais notícias → Radar (compacto)
   - Demais discussões → Pulso da Comunidade (2 expandidos + restante compacto)
   - Nenhum tópico repetido entre seções

## Prompt Recovery (Accidental Overwrite)

Se você sobrescrever acidentalmente o prompt de um cron:

1. Liste os outputs: `ls /opt/data/cron/output/<job_id>/`
2. Leia o arquivo mais recente: contém o prompt original antes da seção `## Response`
3. Reconstrua o prompt a partir do output salvo
4. Restaure com `cronjob(action='update', job_id='...', prompt='...')`

**Importante**: O arquivo de output contém o prompt COMPLETO incluindo skills carregadas. Extraia APENAS a parte da instrução customizada (após as skills), não o conteúdo das skills.

## Verification — WhatsApp Companion Format

**Problema conhecido**: o agente autônomo do cron frequentemente *droppa* elementos do formato WhatsApp, mesmo com a especificação explícita no prompt. Verificar manualmente o delivery real após cada execução nos primeiros dias.

### Checklist de verificação do formato entregue

| Elemento | Padrão | Verificar |
|----------|--------|-----------|
| 📰 emoji | Antes do título `📰 *IAF — Manhã Aumentada*` | Presente? |
| Editorial | `*FRASE* texto normal` (negrito só na primeira frase) | Formato correto? |
| 🔥 header | `🔥 *Destaques do dia*` antes das bullets | Presente? |
| 3 bullets | `• [título] — [descrição]` | Formato correto? |
| 🎯 header | `🎯 *Aplicação prática de hoje*` | Presente? |
| Sem extras | Sem ranking, sem assinatura, sem metadata | Limpo? |

### Como auditar o último delivery

```bash
# Última sessão do cron #3
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
rows = conn.execute('''
    SELECT id FROM sessions
    WHERE source = 'cron' AND id LIKE 'cron_e418042f0c99%'
    ORDER BY started_at DESC LIMIT 1
''').fetchall()
if rows:
    print(f'Session: {rows[0][0]}')
    print('Use session_search(session_id=...) to see the final delivery message')
"
```

## Pitfalls

- **MEDIA: deve ser a primeira linha** da resposta do cron. Nada antes — nem espaço, nem quebra de linha.
- **Sobrescrita acidental**: `cronjob(action='update', prompt='...')` SEM o prompt correto substitui o prompt inteiro. Sempre usar output files como backup.
- **Fuso horário**: agendamento cron é em UTC. Converter GMT-3 → UTC ao criar (`0 7 * * *` = 04:00 GMT-3).
- **Skills content não é parte do prompt**: o sistema carrega skills automaticamente. Não incluir conteúdo de skills no campo `prompt` do cron.
- **Nomes de arquivo estéticos**: usar formato limpo `iaf_YYYY-MM-DD.pdf`, nunca genérico como `output.pdf`.
- **Entrega mínima**: o cron NÃO deve incluir tabela de ranking, comentários, análises ou qualquer texto extra além do PDF + WhatsApp.
- **Formato WhatsApp degrada em execução autônoma**: o agente do cron #3 tende a simplificar o formato — pula 📰, pula 🔥 *Destaques do dia*, deixa bullets soltas. A especificação explícita no prompt **não é suficiente**. Sempre verificar o delivery real contra o checklist acima nos primeiros dias de operação.
- **Permissão explícita**: não implementar/executar nada sem o usuário dar ordem explícita ("SÓ IMPLEMENTE QUANDO EU DER A ORDEM EXPLÍCITA").
