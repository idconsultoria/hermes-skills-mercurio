# Execução de ondas pré-checklist — ciclo, política 🔴/🟢 e pitfalls (validado Zera, 08/2026)

> Fonte: execução das ondas 1–3 do projeto Zera (ex-CFP IA). Tudo aqui foi validado em produção
> real no ciclo de code-tasks.

## Ciclo de code-tasks com modelos especializados (preferência explícita do usuário)

Para cada onda do checklist, papéis de modelo distintos:

| Papel | Modelo | Comando |
|---|---|---|
| Code-tasks (spec) | **Pi best** (deepseek-v4-pro) | `pi --name "proj-ondaN-code-tasks" -p "$(cat prompts/pi-best-code-tasks-ondaN.md)" --provider opencode-go --model deepseek-v4-pro` |
| Execução | **Pi cost** (deepseek-v4-flash) | `pi --name "proj-ondaN-loteM" -p "$(cat prompts/pi-cost-ondaN-loteM.md)" --provider opencode-go --model deepseek-v4-flash` |
| Revisão | **agy** | `ssh oracle-host 'cd <shared> && /home/ubuntu/.local/bin/agy -p "$(cat prompts/agy-review-ondaN.md)" --dangerously-skip-permissions --print-timeout 10m'` |
| Correção | **Pi best max** (thinking xhigh, MESMA sessão do executor) | `pi --session <mesmo jsonl> -p "$(cat prompts/pi-best-ondaN-retomada.md)" --provider opencode-go --model deepseek-v4-pro` |
| Re-revisão | **agy** | mesmo comando, até `ACORDO: <ONDA> FINALIZADA` |
| Documentação | **Pi cost max** (thinking xhigh) | `pi -p ...` — SAD/ERD/contracts/code-tasks + `## Histórico de atualizações` |

Regras:
- Hermes **nunca** escreve código de produto — orquestra, valida, commita.
- Cada onda = UM ciclo completo: code-tasks → execução (lotes sequenciais, nunca paralelo) → agy Turno 1
  → correção na MESMA sessão → agy Turno 3 → `ACORDO` → docs (Pi cost max) → commit + atualização da
  planilha Roadmap (status das tasks do escopo).
- Pi cost com `background=true` + `notify_on_complete=true`; monitorar por arquivos/`pi-session-audit`,
  nunca por stdout. Nunca usar `timeout` com Pi/agy (mata silenciosamente).

## Política de decisão 🔴/🟢 (bloco obrigatório em TODO prompt de Pi)

Documento canônico: `product/management/politica-decisao.md` no repo + vinculação no AGENTS.md.

- 🔴 **REVISÃO OBRIGATÓRIA — parar e pedir aval ao usuário:**
  - Tecnologia crítica não especificada (lib/framework/serviço novo fora da Base Técnica/PRD/ADRs)
  - Princípios de design/arquitetura (contrato de API público, schema, identidade visual)
  - Forma específica de implementação de funcionalidade crítica (auth, motor, LLM, LGPD, notificações)
  - Custo recorrente (provider pago, domínio, observabilidade SaaS)
  - Deploy para produção (não-staging)
  - Mudança de escopo do plano
- 🟢 **EXECUTA DIRETO (reporta no final):**
  - Implementação dentro de decisão já tomada · correções mecânicas (lint, typos) · QA/verificação
    (tsc, pytest, dogfood) · documentação técnica · infra staging/CI · atualização da planilha · commits.
- **Regra de ouro:** reversível com esforço pequeno → executa; difícil de reverter ou afeta custo/usuário/
  contrato público → pergunta; dúvida genuína → pergunta. Checkpoints 🔴 agrupados em lote (não um a um).

### Como o bloco entra nos prompts

Todo prompt de Pi (best/cost/max) deve conter algo como:

```
## POLÍTICA DE DECISÃO (OBRIGATÓRIA)
Leia `product/management/politica-decisao.md` ANTES de implementar:
- 🔴 ... → PARE e reporte (decisão, 2-3 opções, recomendação, impacto) em vez de codar por suposição.
- 🟢 ... → execute direto.
- Ao final declare: "Política de decisão: nenhuma decisão 🔴" OU liste as 🔴 reportadas.
```

Além disso, prompts de retomada devem ter seção "DECISÕES JÁ TOMADAS — não redecidir" listando D1..Dn
resolvidas + ADRs, para o Pi não reabrir decisão fechada. Cada 🔴 resolvida vira linha na política
(ex.: D14 service token, D15 multi-etapas UI, D16 múltiplas conversas) + ADR (ex.: ADR-018..021).

### Padrões de decisão que apareceram no Zera (referência)

- D12 auth frontend → **cookie httpOnly + same-site** (refresh httpOnly; Secure; SameSite=Strict,
  access em memória, refresh silencioso, CORS_ORIGINS explícito) — recomendado sobre localStorage.
- D4 persistência do bot → usuário escolheu **Opção C (bot vira canal do núcleo agêntico B04)** mesmo
  sendo mudança de escopo; registrar ADR e assumir o custo.
- Terminologia: usuário vê "conversas", nunca "sessões" — "sessão" é técnico interno. Regra de UX/copy.

## Pitfall — agy em modo print aborta sem `--dangerously-skip-permissions`

- `echo "n" | agy -p "..."` ou `agy -p "..."` puro: o agy imprime a 1ª linha ("I will start by...") e
  **aborta** (EOF no stdin / pedido de permissão de tool bloqueia). `tmux` + `tee` também falharam.
- **Funciona:** `/home/ubuntu/.local/bin/agy -p "$(cat prompts/...)" --dangerously-skip-permissions --print-timeout 10m`.
  O `--dangerously-skip-permissions` auto-aprova as tool permissions; o `--print-timeout` dá tempo.
- Rodar via `ssh oracle-host 'cd <shared_repo> && ...'`. O agy escreve o review direto no shared volume
  (mesmo filesystem) — o container vê as mudanças na hora; não precisa copiar nada.
- Caminho absoluto do binário: `/home/ubuntu/.local/bin/agy` (PATH via SSH nem sempre inclui).

## Pitfall — shared volume: agy chown quebra o .git para o container

O agy roda como `ubuntu` no host; quando precisa editar arquivos do shared volume, ele faz
`sudo chown ubuntu:ubuntu` em partes do repo (ex.: `.git`, feedbacks.md). Como o volume é compartilhado,
**o container (UID 10000/hermes) perde escrita** e `git add`/commit falham com "Permission denied"
(index.lock, FETCH_HEAD).

Fix no host antes de commitar no container:
```bash
ssh oracle-host 'sudo chown -R 10000:10000 /home/ubuntu/selfhost/shared/code/workstation/<proj>/.git'
```
(Ou `chown -R hermes:hermes`.) Depois disso o container volta a commitar/pushar normalmente.

## Pitfall — push GitHub a partir do host Oracle não tem credenciais

O host tem o repo clonado via HTTPS sem credencial armazenada → `git push` no host falha
("could not read Username"). O container tem o token (`~/.config/gh/hosts.yml` / `~/.git-credentials`).
Fluxo comprovado:
1. Fazer commits SEMPRE no container (`/opt/data/code/workstation/<proj>`).
2. Sincronizar host ← container via `git fetch` + `git reset --hard origin/main` no host (para o agy ver
   o estado novo), corrigindo owner do `.git` antes.
3. Trazer mudanças do agy de volta: copiar via `ssh oracle-host 'cat <file>'` para o container (arquivos
   alterados) — NÃO usar `git format-patch` + `git apply` (falha quando o container tem versão divergente
   do mesmo arquivo). Depois commitar no container e push.

## Pitfall — docker exec sem `-u` roda como root → `~` = /root

Ao rodar scripts no container via `docker exec hermes_agent python3 script.py` sem `-u hermes`, o HOME é
`/root` e caminhos como `~/.pi/...` não resolvem. Usar caminhos absolutos (`/opt/data/home/.pi/...`) em
qualquer script invocado via docker exec, ou passar `-u hermes`.
