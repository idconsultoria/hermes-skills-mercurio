# Sincronização host ↔ container (volume compartilhado) — regras do usuário

> Correção explícita do Gustavo (14/08/2026): ele bloqueou `git reset --hard origin/main` no host
> Oracle durante o fluxo agy. **NUNCA rodar `git reset --hard` no host para "sincronizar" o repo.**

## Por quê (o que o usuário apontou)

1. **O volume É compartilhado.** `/home/ubuntu/selfhost/shared/code/workstation/cfp-ia` no host é o
   MESMO diretório de `/opt/data/code/workstation/cfp-ia` no container. Quando o Hermes commita e
   pusha do container, o host já vê o estado atual — não existe "sincronização" a fazer via reset.
2. **Reset pode DESTRUIR trabalho não commitado.** O agy (Antigravity) edita
   `product/engineering/feedbacks.md` como parte da revisão — um `reset --hard` na hora errada
   comeria o review inteiro. O volume compartilhado cuida da sincronização sozinho.

## O que fazer em vez disso

- **Antes de rodar o agy:** apenas verificar que o host está no commit certo com
  `git log --oneline -1` (leitura, sem mutação). Se o arquivo do prompt de review já foi pushado,
  o host já o tem.
- **Depois do agy:** `git status -s` no container — se o agy editou arquivos (ex.: feedbacks.md),
  commitar direto. **Sem reset antes ou depois.**
- Se o `git add`/`commit` no container falhar com permissão (porque o agy rodou como uid 1001/ubuntu
  e chownou o `.git`): corrigir o owner PELO HOST, nunca resetar:
  ```bash
  ssh oracle-host 'sudo chown -R 10000:10000 /home/ubuntu/selfhost/shared/code/workstation/cfp-ia/.git'
  # e também prompts/ + product/ quando o agy mexeu neles
  ```
- **Diagnóstico de permissão:** sintoma clássico é `git add`/write falhando no container com
  "Permission denied" num arquivo `.hermes-tmp.*` — checar `ls -ld` da pasta (owner 1001/ubuntu =
  o agy passou por ali). Corrigir com o chown acima, NÃO com reset.

## Padrões que já funcionam (sem reset)

| Ação | Comando |
|---|---|
| Confirmar host no commit certo | `ssh oracle-host 'cd <repo> && git log --oneline -1'` |
| Commit do feedbacks do agy | `cd /opt/data/... && git add product/engineering/feedbacks.md && git commit && git push` |
| Corrigir owner após agy | `ssh oracle-host 'sudo chown -R 10000:10000 <repo>/.git <repo>/prompts <repo>/product'` |
| Rodar agy (review) | `ssh oracle-host 'cd <repo> && /home/ubuntu/.local/bin/agy -p "$(cat prompts/agy-review-*.md)" --dangerously-skip-permissions --print-timeout 15m'` |

## Lição de processo

`git reset --hard` no host é uma operação irreversível e **nunca é necessária** neste fluxo —
carreguei o hábito das primeiras sincronizações, o usuário o bloqueou, e a regra agora é absoluta.
Quando o shared volume estiver no commit errado (raro), o caminho é `git checkout`/`git pull` no
host se o working tree estiver limpo — mas NUNCA `reset --hard` com trabalho não commitado à vista.
