---
name: hermes-session-forensics
description: "Use ao buscar histórico de sessões fora do perfil atual."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [sessions, state.db, sqlite, histórico, forense, multi-perfil, projetos]
    scopes: [id]
type: Orchestrator
timestamp: 2026-10-12T00:00:00Z
---

# Forense do histórico de sessões do Hermes

A tool `session_search` procura **só no store do perfil atual**. Quando a pergunta é
"onde foi que fizemos X?" e o trabalho aconteceu **em outro perfil, em outra instalação
(Termux nativo, host Oracle) ou antes de uma migração**, a resposta está no próprio
arquivo do store: consultar `state.db` direto, read-only.

## Quando usar

- "Encontre o histórico de sessões em que fizemos X" / "em que pé ficou o projeto Y".
- `session_search` volta vazio ou raso e o operador lembra que foi feito em outro
  perfil/máquina.
- Reconstruir **datas, decisões, artefatos e caminhos** de um projeto antigo: o que foi
  entregue, para quem, quando, e onde o material está hoje.

## Onde estão os arquivos

| Store | Caminho | Perfil |
|---|---|---|
| Perfil corrente | `$HERMES_HOME/state.db` | o que a sessão atual usa |
| Perfis extras | `$HERMES_HOME/profiles/<nome>/state.db` | `hermes --profile <nome>` |
| Hermes default nativo | `~/.hermes/state.db` (no Termux: `/data/data/com.termux/files/home/.hermes/state.db`) | perfil `default` da instalação de base |
| Backups | `state.db.bak-*`, `state.db.snapshot-*`, `sessions/` | recuperação |

**Não existe `status.db`.** O operador pode chamar o store assim, de memória; o store de
sessões é `state.db` (tabelas `sessions` e `messages`). Procure pelo caminho canônico —
não saia caçando o nome que veio na frase nem conclua que "não existe" porque o termo não
bateu.

## Procedimento

1. **Ache o store certo antes de buscar.** Liste os candidatos com tamanho
   (`state.db` grande = histórico longo). Em instalação multi-perfil, busque no perfil
   **e** no default nativo: o trabalho de meses anteriores costuma ter ficado no default,
   antes da criação da rama.
2. **Abra SEMPRE read-only:**
   ```python
   con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)   # uri=True é obrigatório no modo ro
   ```
   Nunca escrever, `VACUUM` ou `DELETE` em store de outro perfil — é estado vivo de outra
   sessão/gateway.
3. **Busque por conteúdo e agregue por sessão**, não por mensagem:
   ```sql
   SELECT session_id, count(*) c, min(timestamp), max(timestamp)
     FROM messages WHERE lower(content) LIKE '%termo%'
    GROUP BY 1 ORDER BY c DESC;
   ```
   Junte `sessions` (`title`, `source`, `chat_id`, `message_count`, `started_at`) para
   nomear as candidatas.
4. **Exija um segundo termo discriminante.** Nome de cliente/empresa aparece como contexto
   ambiente em dezenas de sessões (consolidação de KB, infra, crons). Combine com o termo do
   **artefato ou projeto** (nome do repo, `contrato`, `etapa`, `vercel`, `entrega`) e um
   `HAVING count(*) >= 3` — sem isso o ranking é dominado por sessão que só citava o nome.
5. **Leia em bookend, não a sessão inteira:** primeira mensagem do usuário (objetivo) +
   última resposta do assistente (resolução) de cada candidata resumem bem. Abra a sessão
   completa só se o pedido for "o que decidimos em detalhe".
6. **Toda consulta é varrimento de arquivo inteiro** (`LIKE` em ~250 mil mensagens leva
   ~20 s num store de 1 GB): construa o `WHERE` no Python, restrinja por `timestamp` quando
   o período é conhecido e rode em paralelo as consultas independentes.
7. **Reporte em ordem cronológica**, por sessão: id (`@session:<id>`), título, fonte
   (telegram/whatsapp/tui/cli/cron/subagent), intervalo e **o que aquela sessão produziu** —
   não o resumo da conversa. Quem lê quer a linha do tempo dos artefatos.

Cookbook de SQL (esquema de `sessions`/`messages`, FTS, filtros por período, bookends,
sessões sem título): `references/state-db-schema.md`.

## Pitfalls

- **Procurar no perfil errado e concluir que "não existe".** `session_search` do perfil
  corrente não vê o default nem os outros perfis; antes de responder "não achei", varra os
  `state.db` existentes na máquina.
- **Contar menções como relevância.** Sessão com 200 menções do nome do cliente pode ser
  infra; a sessão que **entregou** pode ter 40. Julgue por título, fonte e par de bookends.
- **Tratar a lembrança do operador como localização exata.** Ele lembra do assunto e
  frequentemente erra o arquivo/nome; confirme o caminho real no sistema antes de reportar.
- **Devolver transcrição bruta.** O valor está em: sessão → quando → o que saiu dela →
  onde o artefato está hoje. Sem isso, o operador tem que ler o mesmo que você leu.
- **Confundir menção com existência de artefato.** Sessão que *fala* de um repo não prova
  que ele existe hoje: confirme no sistema de arquivos ou no remoto antes de afirmar onde
  o código está.
