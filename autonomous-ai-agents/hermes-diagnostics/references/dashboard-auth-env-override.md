# Dashboard Login Failing — Env-Over-Config Override

> Diagnóstico completo para `Invalid username or password` no dashboard Hermes
> (porta 9119) mesmo quando `dashboard.basic_auth` no config.yaml está correto.

## Sintoma

- Login web em `http://<ip>:9119/login` rejeita com `Invalid username or password`.
- `config.yaml` tem `dashboard.basic_auth.username` / `.password` corretos.
- Teste via API com as credenciais corretas também retorna 401.

## Causa raiz

O plugin `plugins/dashboard_auth/basic` resolve configuração com precedência
**env > config.yaml** (`_resolve()` no `register()`): se
`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`
estão setadas no ambiente do processo (mesmo que com valores placeholder),
elas **vencem** o `dashboard.basic_auth` do config.yaml silenciosamente.

Placeholders típicos encontrados na prática:
- `HERMES_DASHBOARD_BASIC_AUTH_USERNAME=seu_usuario_aqui`
- `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<placeholder 27 chars>`
- `HERMES_DASHBOARD_SESSION_TOKEN=meu_token_secreto_123`

Cadeia de origem no container s6-overlay:
1. Host `docker-compose.yml` → `environment:` (frequentemente com indireção
   `${VAR}`) e/ou arquivo `.env` ao lado do compose.
2. `docker run`/compose injeta no ambiente do container.
3. s6-overlay materializa em `/run/s6/container_environment/`.
4. Script do serviço `docker/s6-rc.d/dashboard/run` usa
   `#!/command/with-contenv sh` → processo `hermes dashboard` herda as envs.

**Atenção:** `HERMES_DASHBOARD_INSECURE=1` **não desativa mais o auth gate**
(hardening de junho/2026 — aceito mas ignorado; dashboard não-loopback exige
provider de auth).

## Verificação (3 passos)

### 1. Env efetiva do processo

```bash
ps aux | grep 'hermes dashboard'          # achar PID (ex: 133)
tr '\0' '\n' < /proc/<PID>/environ | grep DASHBOARD
# Se aparecer HERMES_DASHBOARD_BASIC_AUTH_USERNAME com valor placeholder → é isso.
# Fonte no container: ls /run/s6/container_environment/ | grep DASHBOARD
```

### 2. Teste do endpoint real (server-side, não confia em screenshot)

O form do dashboard faz fetch para `/auth/password-login` (JSON) — **não** é
`POST /login` (esse retorna 405) e precisa do campo `provider: "basic"`
(sem ele → 422).

```bash
curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:9119/auth/password-login \
  -H 'Content-Type: application/json' \
  -d '{"provider":"basic","username":"gustavomello9600","password":"Gustav0!","next":""}'
```

- `401 {"detail":"Invalid credentials"}` com a credencial **correta** do config
  → prova override de env (o processo compara contra outro valor).
- Sucesso → `{"next":...}` + 302/redirect com cookie.

### 3. Rastrear até o host

```bash
ssh oracle-host 'docker inspect hermes_agent --format "{{index .Config.Labels \"com.docker.compose.project.config_files\"}}"'
ssh oracle-host 'grep -n "HERMES_DASHBOARD" <compose>/docker-compose.yml'
ssh oracle-host 'grep -nE "HERMES_DASHBOARD_BASIC_AUTH" <compose>/.env'
```

## Correção (duas partes)

1. **Durável (host):** corrigir os valores reais no `.env` (ou `environment:`)
   do compose e recriar com `docker compose up -d <service>`. ⚠️ Recriar o
   container **derruba a sessão atual** do gateway — agendar ou pedir OK ao
   usuário (ver skill `oracle-host-access`, pitfall "Container restarts = lost session").

2. **Sem derrubar o gateway:** aplicar apenas no serviço do dashboard:

```bash
# como root dentro do container (docker exec -u root ...) — sem sudo no container
ssh oracle-host 'docker exec -u root hermes_agent sh -c \
  "echo gustavomello9600 > /run/s6/container_environment/HERMES_DASHBOARD_BASIC_AUTH_USERNAME; \
   echo Gustav0! > /run/s6/container_environment/HERMES_DASHBOARD_BASIC_AUTH_PASSWORD"'
# reiniciar SÓ o serviço do dashboard (s6), gateway/WhatsApp ficam de pé
ssh oracle-host 'docker exec hermes_agent s6-svc -r /run/service/dashboard'  # ou caminho s6 equivalente
```

Verificar de novo com o curl do passo 2.

## Pitfall: não acusar typo do usuário com base em OCR

`vision_analyze` em screenshot é não-confiável em nível de caractere (leu
`gustavomcllo9600` onde o usuário tinha digitado `gustavomello9600`). Regra:
**nunca concluir erro de digitação do usuário por OCR** — o teste server-side
(curl passo 2) é a única prova. Se a credencial correta retorna 401, o
problema é do servidor, não do input.
