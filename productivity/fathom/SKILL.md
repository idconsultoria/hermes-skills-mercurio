---
name: fathom
description: "Cliente da API REST do Fathom - reuniões, resumos e transcrições.

Carregue esta skill quando precisar puxar reuniões do Fathom (gravações, resumos, transcrições, action items) por script, quando um consumidor quebrar em `from fathom_api import FathomClient`, ou quando for mexer em `productivity/fathom/scripts/fathom_api.py`. Cobre autenticação (chave em `.secrets/fathom.env`), endpoints `/meetings` e `/meetings/{id}`, paginação por cursor, retry com backoff e o contrato mínimo que o pipeline da Phronesis consome."

type: ToolIntegration
timestamp: 2026-11-02T00:00:00Z
category: productivity
---

# Fathom — cliente mínimo da API de reuniões

## Quando usar

- O pipeline semanal da Phronesis (`phronesis_weekly.py` e afins) precisa das reuniões gravadas
  no Fathom da ID para montar pauta, encaminhamentos ou métricas de relacionamento.
- Algum consumidor quebra em `from fathom_api import FathomClient`.
- É preciso entender o que a API externa devolve antes de decidir se vale um resumo manual.

Não é substituto de `reunioes-diarizadas` (diarização/transcrição de áudio local) nem de
`meeting-action-items` (transformar notas em decisões, donos e tickets). Esta skill é só o
**transporte**: buscar do Fathom o que já foi gravado lá.

## Autenticação

- Chave: `FATHOM_API_KEY` em `<HERMES_HOME>/.secrets/fathom.env`
  (`HERMES_HOME` default `/data/data/com.termux/files/home/capitolium`), com fallback para a
  variável de ambiente `FATHOM_API_KEY`.
- Header: `X-Api-Key: <chave>`. Sem chave, o cliente levanta `RuntimeError` com o caminho
  esperado do arquivo — leia a mensagem antes de suspeitar de rede.

## Endpoints usados

| Chamada | Uso |
|---|---|
| `GET /meetings` | listar por janela (`created_after`), paginado por `cursor` |
| `GET /meetings/{recording_id}` | uma reunião com resumo e transcrição |

Base: `https://api.fathom.ai/external/v1`.

Flags de peso em `list_meetings(limit, include_summary, include_transcript, include_action_items,
created_after, cursor, recorded_by)`:

- `include_transcript=true` é o que domina o tamanho da resposta — peça só quando for usar.
- `created_after` aceita ISO 8601 (`2026-10-19T00:00:00Z`) e é o filtro barato para janela semanal.
- `recorded_by` vira `recorded_by[]` na query.
- Paginação: repetir com o `cursor` devolvido até vir vazio; não assumir que `limit=50` traz tudo.

## Robustez

- `_get` tenta até 4 vezes com backoff exponencial (2, 4, 8… s, teto 20 s).
- `401`, `403` e `404` **não** são retentados: levantam na hora (chave errada, sem permissão,
  id inexistente). Retentar esses casos só atrasa o diagnóstico.
- Timeout por requisição: 90 s.

## Montagem num script consumidor

```python
import sys
sys.path.insert(0, "<HERMES_HOME>/skills/productivity/fathom/scripts")
from fathom_api import FathomClient

c = FathomClient()
page = c.list_meetings(limit=50, include_summary=True, include_transcript=True,
                       include_action_items=True, created_after="2026-10-26T00:00:00Z")
for m in page.get("items", page.get("meetings", [])):
    print(m.get("recording_id"), m.get("title"), m.get("created_at"))
```

O formato exato da lista muda entre versões da API externa: inspecione a chave que veio
(`items` × `meetings`) em vez de assumir, e nunca invente campos ausentes.

## Pitfalls

- **Não recriar o módulo em outro path.** O import dos consumidores é
  `from fathom_api import FathomClient` com o diretório `scripts/` no `sys.path`; um segundo shim
  em outro lugar cria duas verdades e o pipeline passa a ler de um cliente desatualizado.
- **`__pycache__/` fica fora do git** (já no `.gitignore`); se aparecer no `git status`, apague.
- **Chave não vai para skill nem para log.** Fica só em `.secrets/fathom.env`.
- **Não transformar resumo do Fathom em ata final sem revisão** — resumo automático erra nome
  próprio e atribuição de dono; use como insumo, não como entrega.
