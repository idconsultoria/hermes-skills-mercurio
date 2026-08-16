# Cron de lembrete sobre estado em Google Docs/Sheets (receita validada)

Cron "Zera — Lembrete Demandas Igor" (job `e962f5a06576`, diário 11:00 UTC).
Arquitetura: script coleta estado determinístico → agente lê checkboxes por visão
→ dispara WhatsApp via bridge curl → resposta curta ao origin.

## Problema que resolve

O guia de demandas é um Google Doc com uma tabela sumária onde a coluna "Feito"
tem checkboxes. O usuário quer lembrar o especialista (Igor) por WhatsApp APENAS
na véspera de cada entrega ainda não concluída — nunca no dia nem atrasado.

## Limitação crítica da Docs API

A Google Docs REST API NÃO expõe o estado do checkbox (marcado/vazio). O bullet
retorna `{"listId": "kix.xxx", "textStyle": {...}}` idêntico para ambos estados.
Detalhe: célula com checkbox tem bullet com `glyphType: GLYPH_TYPE_UNSPECIFIED`
na lista — confirma que É checkbox, mas não diz o estado.

## Pipeline validado

### 1. Script de coleta (roda no tick, stdout = JSON pro agente)

```python
# /opt/data/home/.hermes/scripts/cfp_demandas_igor_collect.py
# 1) Token: importlib do md-to-gdoc.py -> get_token()
# 2) Exportar PDF via Drive API:
#    GET https://www.googleapis.com/drive/v3/files/{DOC_ID}/export?mimeType=application/pdf
# 3) Renderizar página 1 com PyMuPDF (fitz — só existe no venv google):
#    /opt/data/venvs/google/bin/python  (system python NÃO tem fitz)
#    page = fitz.open(pdf)[0]; page.get_pixmap(dpi=150).save(png)
# 4) Extrair a tabela sumária via Docs API (estrutura recursiva:
#    body.content[].table.tableRows[].tableCells[].content[].paragraph.elements[].textRun)
# 5) COMPUTAR flags determinísticas em BRT — não deixar o LLM calcular:
#    brt = timezone(timedelta(hours=-3)); hoje = now(brt).date()
#    vence_amanha = prazo == hoje+1; vence_hoje = prazo == hoje; atrasada = prazo < hoje
# 6) stdout: JSON com hoje, amanha_brt_prazo_alvo (DD/MM), png_path,
#    entregas[{numero, nome, prazo, pasta_url, vence_amanha, vence_hoje, atrasada}]
```

Notas de implementação:
- Ordem no `main()`: definir `hoje`/`amanha` ANTES de chamar `extrair_tabela`
  (a função recebe como args — não use globals).
- Server roda UTC; `date.today()` está errado para BRT. Use `datetime.now(brt)`.

### ⚠️ Pitfall: cron runner invoca com o python do SISTEMA (ignora shebang)

Validado 15/08/2026: o runner do cron executa o script com o python do host
(`/usr/bin/python3`, `sys.prefix=/usr`) — **o shebang do venv NÃO é respeitado**.
Resultado: `ModuleNotFoundError: No module named 'fitz'` no tick, mesmo com o
script correto em `~/.hermes/scripts/`.

**Fix self-healing no topo do script** (após os imports, antes de qualquer uso
de fitz):

```python
import json, os, sys, datetime, urllib.request, importlib.util

if importlib.util.find_spec("fitz") is None and os.path.exists("/opt/data/venvs/google/bin/python"):
    os.execv("/opt/data/venvs/google/bin/python", ["/opt/data/venvs/google/bin/python"] + sys.argv)
```

- `os.execv` substitui o processo no lugar — stdout/JSON continuam fluindo pro cron.
- Manter a cópia em `/opt/data/scripts/` e `~/.hermes/scripts/` sincronizadas
  (`cp` após editar) — o runner pode pegar qualquer uma das duas.
- Teste: `/usr/bin/python3 ~/.hermes/scripts/cfp_demandas_igor_collect.py` deve
  re-executar e imprimir o JSON (não o traceback).

### 2. Prompt do cron (regra rígida)

- Agente chama `vision_analyze(png_path)` pedindo: "Liste o estado de cada
  checkbox da coluna 'Feito' (entregas 1 a 7): MARCADO ou VAZIO, um por linha."
- Seleção: `vence_amanha == true` AND checkbox VAZIO. NUNCA `vence_hoje` nem
  `atrasada`. Confiar nas flags do script, não recalcular.
- Envio: curl direto ao bridge (contato fora do channel directory):
  ```bash
  curl -s -X POST http://127.0.0.1:3000/send -H "Content-Type: application/json" \
    -d '{"chatId":"557988677056@s.whatsapp.net","message":"..."}'
  ```
  Verificar retorno `{"success":true,"messageId":"..."}`.
- Falha de visão: responder "⚠️ ... falha de visão" e NÃO enviar (não inventar).
- Resposta final curta (origin): "✅ Lembrete(s) enviado(s)..." ou
  "✅ Sem pendências com prazo amanhã." — o destinatário só vê a mensagem real.

### 3. Entrega two-tier

- `deliver: origin` (Gustavo vê confirmação) + envio real via bridge curl.
- NUNCA `deliver: whatsapp:...` — vazaria status técnico pro destinatário.

## Lição Google Sheets (desta sessão)

Ao atualizar status numa planilha: abas OBJECT (sheetType OBJECT, sem
gridProperties) não são acessíveis via values API — erro `Unable to parse range`
ou `Invalid dataFilter: No grid with id`. Use as abas GRID ('Roadmap em tabela',
'Tarefas em tabela'). Após escrever status, a aba de progresso com fórmulas
COUNTIF/COUNTA recalcula sozinha — leia de volta pra confirmar (ex.: total de
tarefas sobe quando se insere linha nova; % geral muda).

## IDs de referência (projeto Zera)

- Guia de demandas: `1U54ZiMXVcexRzOpXmXEGMoqtlx9SQkAjQYEwXiHp5y0`
- Pasta Demandas para Igor: `16d4j5sqL27jCVDFbGb8Ll3dAH3D02Kl2`
- Planilha Roadmap: `1ePmXCt284hoVAR3Ub_D-MjiT1_MSiVsM5nqebLy_8yI`
  (abas OBJECT: 'Roadmap', 'Tarefas'; abas GRID: 'Progresso', 'Roadmap em
  tabela', 'Tarefas em tabela')
- WhatsApp Igor: `557988677056@s.whatsapp.net` (via bridge curl, não cadastrado)
- Script: `/opt/data/home/.hermes/scripts/cfp_demandas_igor_collect.py`
- Output PNG: `/opt/data/cron/output/cfp_guia_demandas_p1.png`
