# Cron Provider-Outage Triage & Rerun

## Real case (2026-08-08)

Três agent-driven crons falharam na MESMA janela (10:10–10:50 UTC) com o MESMO erro:

```
ERROR cron.scheduler: Job '<name>' idle for 600s (inactivity limit 600s) | last_activity=waiting for non-streaming API response | iteration=1/150 | tool=none
TimeoutError: Cron job '<name>' idle for 600s (limit 600s) — last activity: waiting for non-streaming API response
```

Jobs afetados (todos `tool=none`, `iteration=1/150` — nenhuma ferramenta chegou a rodar):
- Panorama Diário TaskFlow (10:10 UTC)
- IAF — Newsletters (10:40 UTC)
- IAF — Síntese + PDF (10:50 UTC)

**Causa raiz:** a API do provider LLM (`opencode-go` / deepseek-v4-flash) ficou sem
responder entre ~10:00–10:50 UTC. A primeira chamada de modelo pendurou; o scheduler
matou cada job após 600s de inatividade. NÃO eram bugs dos jobs.

**Confirmação:** jobs que rodaram ANTES (05:00, 07:00) e DEPOIS (12:10 Moodle) da
janela terminaram com `ok`. A janela de falha bate exatamente com a indisponibilidade
do provider.

## Triage (multi-job failure na mesma janela)

1. `cronjob(action='list')` — compare `last_run_at`. Mesma janela = causa compartilhada.
2. Grep no errors.log filtrando ruído MCP conhecido:
   ```bash
   grep -n "2026-08-08 1[01]:" /opt/data/logs/errors.log | grep -v "vulcano\|open-design"
   ```
   As linhas `cron.scheduler: Job ... idle for 600s` confirmam os kills.
3. Cross-check jobs OK antes/depois da janela → provider recuperou; era transitório.
4. **Ruído MCP NÃO é a causa:** warnings contínuos de `MCP server 'X' failed initial
   connection` (ex: vulcano DNS failure, open-design connection closed) e OAuth token
   refresh (`mcp.client.auth.oauth2: Token refresh failed: 400`) estão presentes o dia
   todo, inclusive quando jobs rodam bem. Não persiga esses warnings durante o triage.

## Rerun dos crons falhados

- `cronjob(action='run', job_id=...)` → `execution_success: true` significa
  **despachado**, não concluído. Verifique por artefatos reais depois.
- **Respeite dependências de pipeline:** se o job B consome output do job A, rode A
  primeiro, espere o artefato aparecer (ex: `ls cron/output/<producer>/` com arquivo
  de hoje), depois rode B. Disparar tudo em paralelo = consumidor lê input stale.
  Exemplo IAF: rodar Newsletters (#2) ANTES da Síntese (#3), que lê os arquivos
  `iaf_newsletters_*.md` gerados.
- **Verificação independente (self-report do job não conta):**
  - `ls` no output dir → arquivo de hoje existe
  - `curl -o /dev/null -w "%{http_code}" https://iaf-newsletter.vercel.app/{SLUG}` → 200
  - grep `messageId` no output `.md` → entrega WhatsApp confirmada

## Lição transversal

Quando vários crons agent-driven falham na mesma janela com `idle for 600s — waiting
for non-streaming API response`, o padrão é: **provider outage**, não bugs independentes.
Triagem = janela de tempo compartilhada + jobs OK fora da janela + ignorar ruído MCP.
