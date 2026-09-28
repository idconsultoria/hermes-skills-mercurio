---
name: hermes-environment-replication
description: "Replicar instância Hermes viva p/ nova VM."
category: autonomous-ai-agents
type: Orchestrator
timestamp: 2026-08-22T00:00:00Z
---

# Replicação de instância Hermes (auditoria + pacote portável)

Use quando o principal pedir para **reimplementar/clonar uma instância Hermes existente**
(ex.: "fazer uma cópia minha em outra VM", "quero passar isso a um modelo executar") — em
especial as ramas do ecossistema Oracle/ID. O objetivo é um artefato que um agente/modelo
leia e execute **sem acesso à máquina de origem**.

## Princípio central
**Não invente a stack a partir de memória/template genérico** — levante o ambiente REAL de
produção e derive o pacote dele. A regra da ID: "replicar = conferir a base antes de executar;
padrão ausente = avisar, não executar."

## O que auditar no ambiente vivo (checklist)
Colete cada um — são os blocos do pacote:
- **Estrutura**: `ls -la /opt/data`, `du -sh */` (topo do volume de trabalho).
- **config.yaml**: model/provider, fallbacks, web/browser backend, auxiliary (vision/compression),
  tts (comando real), stt, memory, delegation, approvals, plugins.enabled, platform_toolsets, cron.
- **.env**: apenas os NOMES das chaves (`while IFS='=' read -r k v; do case "$k" in ... esac; done < .env`),
  nunca valores. Crie template com placeholders.
- **Identidade**: leia `SOUL.md` integral; memória (MEMORY.md) e user profile.
- **Skills**: é um clone git? `git -C skills remote -v` + `status -sb`; atenção a working-tree
  não-commitado — avisar e deixar explícito commitado vs sujo.
- **KB/plugins**: como o plugin resolve caminhos (ex.: engine.py `KB_ROOT = HERMES_HOME/context-kb`).
- **Venvs**: pacotes (`pip list` real); scripts úteis com caminhos/disparos reais.
- **Cron**: ler `cron/jobs.json` (agenda, script, tipo agente/no_agent, delivery).
- **Motores/integrações**: apps dedicados (NFS-e, bridges), entradas de dados trocadas por path.

## Entregáveis do pacote (formato do principal da ID)
- **HTML em identidade ID** (skill `id-design-guide`) como relatório de entrega no chat.
- **.md versionados num .zip** quando o principal disser que vai passar a outro modelo.
  Cada arquivo self-contained; o arquivo chave é o **mapa de conexões de código**
  (variável env → config → componente / contrato de dados trocado por path).

Nomenclatura de arquivos: **versão** (`-v1`...), nunca reutilizar nome anterior.

## Regra de posse do job recorrente (correção do dono)

> "O Cron semanal de consolidação de Skills da Fama deve ser executado por ela mesma, não por você."

Ao instalar estrutura de gestão num **perfil de outro agente**, o job recorrente é
**daquele agente**, executado no **cron dele**. O agente que constrói só faz a instalação e a
primeira rodada. Motivo: a consolidação é higiene do repertório daquele agente, a evidência
que ela usa (uso, curadoria, escopo) é a dele, e um job instalado por fora não sobrevive à
revisão de que o dono faz das próprias rotinas.

Três consequências que já custaram retrabalho quando essa regra foi quebrada:

- **Os artefatos vão para o diretório skills do alvo**, não para o seu. O prompt do job aponta
  para o path do outro perfil e para o SOUL.md daquele agente; nenhum caminho do agente
  executor entra no prompt.
- **A periodicidade vem do dono, não do seu default.** O dono pediu semanal num caso em que o
  equivalente no seu perfil é diário — copiar o próprio schedule é palpite, e frequência
  dobrada em carga de LLM custa dinheiro sem o dono pedir.
- **Identifique o agente do job explicitamente** (model/provider e perfil, via `hermes profile`
  e a config do alvo) e confirme que o disparo pertence ao `HERMES_HOME` dele. Job criado no
  cron errado é job que nunca roda e que ninguém percebe.

## Pitfalls (todos encontrados na prática)
- **`.zip` pode não existir no container** → crie com o módulo `zipfile` do Python
  (`zipfile.ZipFile(..., ZIP_DEFLATED)` + `os.walk`), não com o binário `zip`.
- **`write_file` com conteúdo grande estoura o stream** → escreva o arquivo em **blocos**:
  um `write_file` inicial e depois **apendas via `patch`** (old_string = trecho final único +
  new_string = trecho + nova seção). Mire blocos < ~8k tokens.
- **Diretório de entregas pode ser de outro usuário (root)** → dir destino com
  `permission denied`; teste de gravação ou use um subdir próprio (ex.: `entregas/`).
- **Segredos**: imprima apenas nomes de chaves + placeholders (`<key>`). Antes de entregar,
  **scan por segredos reais** (regex de valores: `sk-`, `AIza`, `=....{20,}`, senhas) — cuidado
  com **falso positivo** quando o regex casa com o NOME da chave; afine para casar VALOR.
- **Repos de spec podem ser 404 por serem privados** (spec `install-*.sh` instalada via
  repositório privado). Derive do ambiente vivo e avise o principal que o repo pode exigir
  acesso/token.
- **Não cravar "comando X não existe" como regra** no pacote — documente o FIX equivalente
  (ex.: python zipfile) para o destino.
- **Alvo sem estrutura de gestão: instalar é metade do trabalho, e a outra metade é dizer o que
  faltava.** Antes de propor, levantar o que o alvo **não** tem — git na árvore de skills,
  `index.md` de catálogo, `AGENTS.md` de regras, flag de consolidação desligada na config. Sem
  isso, o sintoma (duplicata, nome ruim, descrição inerte) se repete no próximo ciclo: a causa
  é a ausência do sistema, não o arquivo. Verificar a flag no `config.yaml` do alvo — o curator
  vem ligado por padrão e só a consolidação costuma estar desligada.
- **Categoria sem semântica própria é resíduo de curadoria, não domínio.** Categoria que
  concentra "versão adaptada" de várias origens (e guarda arquivo de proveniência como
  marcador) dissolve-se: cada skill vai para a categoria que descreve o que ela faz, e a pasta
  some do catálogo. Conferir por que a categoria nasceu antes de dissolver — às vezes ela é o
  único lugar onde a adaptação do agente está registrada.
- **Skill de outro agente do mesmo time não é skill sua.** Quando o catálogo foi populado por
  curadoria mútua, filtro pelo campo `author` e pelo domínio declarado no SOUL.md: método de
  outro cargo duplica autoridade e faz o agente executar regra alheia. Retirar para um
  diretório de fora-do-escopo, **preservando a SKILL.md**, com README que registra o autor
  original e a condição de reativação. Nunca apagar: o outro agente pode continuar usando.

## Verificação do pacote
- `unzip -l` (ou `zipfile.infolist()`) para confirmar o conteúdo.
- Scan de segredos nos .md antes de entregar; só placeholders.
- Confirmar que o HTML atribui MEDIA: `<caminho>` e os .md estão no .zip.

Ver `references/mercurio-snapshot.md` para o exemplo concreto de levantamento da rama Mercúrio.
Ver `references/ciclo-consolidacao-fork-pitfalls.md` para a tabela de triagem de duplicatas
(assinatura medida → decisão) e para as armadilhas de consolidação por fork.

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e visual local): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/opt/mercurio-data/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
