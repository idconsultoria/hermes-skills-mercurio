# Exemplo concreto — snapshot da rama Mercúrio (levantado 22/08/2026)

Referência de como o checklist do SKILL.md foi aplicado na instância Mercúrio. Use como
modelo de detalhe para auditorias de outras instâncias.

## Topologia alvo
- Container `hermes_mercurio`, rede Docker `ai_mesh`, `HERMES_HOME=/opt/data`.
- Hermes instalado em `/opt/hermes/bin/hermes`; estado/volume em `/opt/data`.
- Gateway Telegram: bot `mercurio_id_bot`; allow-list de DM.
- Daemon Docker **não** acessível de dentro do container (builds de imagem de SO no host).

## Blocos auditados e como chegar neles
| Bloco | Comando/leitura | O que registrar |
|-------|-----------------|-----------------|
| Estrutura | `ls -la /opt/data` + `du -sh */` | dirs de estado, venvs, scripts, motores |
| config.yaml | `read_file /opt/data/config.yaml` | model/provider+fallbacks, web/browser, auxiliary, tts, plugins, cron |
| .env | extrair só nomes: loop `IFS='=' read` | nomes de chaves (rotacionar valores) |
| Identidade | `read_file /opt/data/SOUL.md` integral | persona da rama (copiar 1:1) |
| Memória | memories/ | MEMORY.md + user profile |
| Skills | `git -C skills remote -v` + `status -sb` | origem do fork + working-tree sujo |
| Plugin KB | `grep KB_ROOT plugins/context-kb/engine.py` | resolução de caminho + filtro scope:id |
| Cron | `cat cron/jobs.json` | agenda, script, tipo agente/no_agent |

## Pacote gerado (13 .md → .zip)
`00-leia-me.md` · `01-arquitetura-stack.md` · `02-config-hermes.md` · `03-variaveis-env.md` ·
`04-identidade-soul-memoria.md` · `05-skills.md` · `06-context-kb-plugin.md` ·
`07-venvs-scripts-integracoes.md` · `08-cron-jobs.md` · `09-conexoes-nivel-codigo.md` ·
`10-procedimento-deploy.md` · `11-checklist-validacao.md` · `12-segredos-e-acessos.md`

O arquivo mais importante é o **09 — conexões em nível de código** (variável env → config →
componente; contratos de dados trocados por path, ex. `aliquota_iss.json` → `pAliq` no motor NFS-e).

## Pontos firmes deste ambiente
- Model default `deepseek-v4-flash` via `opencode-go`; fallbacks opencode-zen.
- Web: `firecrawl`, busca `ddgs`; browser via `chrome-cdp:9223`.
- Plugin único: `context-kb` (leitura, filtra `scope:id`).
- 2 cron jobs: ISS dia 5 10h (agente), iData diário 7h (no_agent/watchdog).
- Motor NFS-e: Aracaju usa protocolo **Nacional** → DPS via `nfelib`.
- Integrações: Google 2 contas, Firecrawl, Inter, NFS-e.

## Pendências registradas (validar ao replicar)
- Certificado A1 e-CNPJ **expirado** (renovação via contabilidade AAD).
- iData/Inter registrou falha de auth recente.
- Repo de spec `hermes-mercurio` (install-mercurio.sh) deu 404 — possivelmente privado.