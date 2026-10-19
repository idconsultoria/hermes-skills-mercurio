---
name: git-fork-isolation
description: "Isolar fork de rama do canônico com push guardado seguro."
category: cicd-oracle-preview
type: Orchestrator
timestamp: 2026-08-23T00:00:00Z
---

# Git Fork Isolation — push seguro num fork de rama

> Isola um fork de rama (ex.: repo de skills do Mercúrio `idconsultoria/...`) do repo canônico,
> garantindo que qualquer forward empurre SÓ para o fork certo, com credencial blindada e
> sem vazar segredo. Validado 23/08/2026 ao separar skills do Mercúrio do canônico.

## When to Use

- Operar/deployar/replicar um **fork de rama** que não pode tocar o repo principal ou canônico.
- Criar/verificar um "fork" e garantir que é um repo **independente** (não um rename do mesmo repo).
- Tornar um repo privado; empurrar com `GITHUB_TOKEN` sem deixar token em `git config`/URL/scripts.
- Qualquer ambiente com múltiplos repos/ramas onde push no remote errado causa contaminação.
- **Mudar o dono de um repo** entre a conta pessoal do dono e a conta da ID (§4) — inclusive
  na véspera de uma entrega, quando o ativo precisa passar para a conta da casa.

## 1. Fork real vs rename — SEMPRE verificar via API

`hermes-agent-skills` vs `hermes-skills-mercurio` pareciam 2 repos, mas eram o **mesmo objeto**
(id `1264877806` idêntico, `fork: False`, mesma `created_at`). GitHub mantém o nome antigo como
**redirect/rename** — push num deles afeta o outro. **Nunca assumir independência pelo nome.**

Verificar (token do `.env` via API):
```python
import json, urllib.request, re
tok = re.search(r'GITHUB_TOKEN\s*=\s*([^\s]+)', open('/opt/data/.env').read()).group(1).strip().strip('"')
def gh(u):
    req = urllib.request.Request(u, headers={'Authorization':f'token {tok}',
        'Accept':'application/vnd.github+json','User-Agent':'audit'})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
for repo in ['<owner>/<repoA>','<owner>/<repoB>']:
    d = gh(f'https://api.github.com/repos/{repo}')
    print(repo, '->', d['full_name'], 'id', d['id'], 'created', d['created_at'], 'fork', d['fork'])
# id/full_name iguais = MESMO repo físico.
```
Confirmações locais: `git remote -v` (fetch/push), `git reflog` (clone recém-feito mostra só
`clone` — histórico de push mora no remoto, não local).

**Criar um fork independente:** `POST /repos/<origem>/forks` com `{"name":...,"default_branch_only":false}`
→ recai no usuário autenticado do token. Depois force-push do master desejado `git push -f origin master`
(só se o repo é seu e você tem admin; nunca no canônico).

## 2. Torne privado — limites da plataforma

- ⚠️ **`Public forks can't be made private` (HTTP 422).** Um fork público NÃO pode virar privado
  via `PATCH /repos/{repo}` `{"private":true}`. Para repo privado real: recriar como **repo NORMAL
  privado** (não-fork) e re-pushar o master — **ação destrutiva, exige ok explícito do dono**.
- Token de **colaborador** (pull, sem admin) NÃO consegue deletar/arquivar/privar repo de outra conta —
  só o dono.
- Verificar sempre o resultado (`private`, `visibility`) após PATCH; não confiar no "sucesso" sem ler
  a resposta.

## 3. Push guardado — credencial nunca em URL fixa

Padrão `push-<projeto>.sh` (validado como `push-skills-mercurio.sh`):
```bash
#!/bin/bash
set -e
cd /data/data/com.termux/files/home/capitolium/skills
# 1) valida o remote ANTES — aborta se não for o repo da rama
case "$(git remote get-url origin)" in
  *"idconsultoria/hermes-skills-mercurio.git"*) echo "[push] remote OK";;
  *) echo "[push] ABORTADO: origin não é o fork esperado" >&2; exit 3;;
esac
# 2) token do .env em runtime (nunca hardcoded, nunca echo)
TOK=$(sed -n 's/^GITHUB_TOKEN=[[:space:]]*\(.*\)/\1/p' /opt/data/.env | tr -d '"' | head -1)
[ -z "$TOK" ] && { echo "[push] sem token" >&2; exit 4; }
# 3) push autenticado transitório, depois restaura URL limpa
git remote set-url origin "https://${TOK}@github.com/idconsultoria/hermes-skills-mercurio.git"
git push origin master; RC=$?
git remote set-url origin "https://github.com/idconsultoria/hermes-skills-mercurio.git"
exit $RC
```
- **Token fine-grained `gho_`:** user na URL = o próprio token, senha vazia.
- Pós-push: confirmar `git status -sb` sincronizado e `git remote -v | grep -c gho_` == 0 (sem token
  residual no config). `chmod 700` no script. Apagar scripts temporários que embutem token.

**Clone autenticado — mesma disciplina, com o header certo.** No git sobre HTTPS o header
`Bearer` **não** autentica: o git volta a pedir usuário (`fatal: could not read Username for
'https://github.com'`). Use Basic com `x-access-token` e confira depois que o token não ficou
gravado no config:
```bash
B64=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c http.extraheader="Authorization: Basic $B64" clone https://github.com/<owner>/<repo>.git <dir>
grep -c "$TOK" <dir>/.git/config   # tem que dar 0
```

## 4. Mudança de dono do repo (transferência entre contas)

`POST /repos/{owner}/{repo}/transfer` com `{"new_owner": "<destino>"}` devolve **202** — a
transferência é assíncrona: **não está concluída só porque o POST voltou**. O aceite é do
destino e, para **conta pessoal, não existe API de aceite**: `GET /user/repository_invitations`
autenticado como o destino volta **vazio** (esse endpoint serve convite de colaboração/org), e o
link de aceite é de uso único e só funciona com **sessão de navegador logada na conta destino**.
Corolário: PAT nenhum, de nenhum dos dois lados, completa o aceite — quem clica é o dono. Não
prometa `PATCH /user/repository_invitations/{id}` para transferência entre contas pessoais: o id
não existe.

**Conferir se há transferência pendente:** o e-mail do GitHub é a evidência autoritativa (vai
para a caixa do destino, validade ~24 h, e expira em silêncio):
`from:github.com subject:"Repository transfer"`, corpo com
`github.com/repositories/transfers/<token>`.

**Antes de aceitar, MEÇA o "você vai perder" do e-mail em vez de acreditar nele** — a lista
(Pages, wikis, Insights, draft PRs, branch/tag protection, codeowners) depende do plano do
destino. Leia do repo: `has_pages`, `has_wiki`, `branches/<branch>/protection` (404 = não há
nada configurado), `rulesets` (**403 "Upgrade to GitHub Pro" = aquele lado está em Free**, logo
não havia nada a perder), contagem de `hooks` / `keys` / `actions/workflows` / `forks` /
`issues`. Plano de cada lado: `.plan.name` em `GET /user`. Com os dois lados em Free e o repo sem
nada disso, a perda é **zero** — e isso se afirma com número, não com "provavelmente não perde".

**Verificação pós-aceite (read-back, sempre):**
- destino `GET /repos/<novo-dono>/<repo>` → **200**;
- origem → **301 + `Location`** (redirect: remote, clone e link antigos continuam funcionando —
  mesmo mecanismo do rename da §1);
- `full_name`, `size`, `default_branch`, `created_at`, `pushed_at` e o **HEAD sha** preservados;
- `collaborators`: dono novo `admin`; dono antigo **rebaixado a colaborador (`write`)** — não some.

Transferir **não** mexe em deploy externo: site estático publicado pelo CLI (Vercel) não tem
integração git com o repo — 0 workflows e 0 hooks no repo confirmam que não há auto-deploy a
quebrar. O risco real da transferência é o **clone local** (que já pode não existir mais) e a
janela de 24 h do aceite — diga isso ao principal antes que ele tema pela entrega.

**Pitfall: descobrir de qual conta é o token ANTES de agir.** Num nó com vários Hermes convivem
vários `.env` (`$HERMES_HOME/.env` = conta da ID; `~/.hermes/.env` do default nativo = conta
pessoal do dono), e um loop que lê vários arquivos deixa **o último** token lido — o mesmo
comando passa a agir como outra conta sem avisar. Imprima `GET /user` → `login` e decida por
esse resultado quem pode aceitar/pushar; sem isso a conclusão sai invertida ("não há convite"
quando o convite está na outra conta).

## 5. Pitfalls

- **`error in libcrypto` ao usar chave → checar newline/bytes antes de culpar corrupção.** Uma chave
  PEM criptograficamente íntegra falha no `ssh-keygen` se faltar o `\n` final ou um byte. Comparar
  cópia×original com `md5sum`+`od -c`; validar com `ssh-keygen -y -f <arquivo>` no ARQUIVO COMO VEIO,
  antes de re-parssear/re-encodar (re-encodar com parser manual mal-escrito pode "corromper" na hora
  de gravar e gerar falso diagnóstico).
- **`.gitignore` de um repo de skills local** deve ignorar `**/references/*.pem`, `**/references/*.key`,
  `**/references/*_deploy_key*` — chave de deploy de skill fica só em `references/`, nunca commitada.
- **Push no repo errado por colisão de nome/rename:** sempre o guard `git remote get-url origin` antes
  de qualquer `git push`. Conferir o origin a cada sessão, não confiar em memória.