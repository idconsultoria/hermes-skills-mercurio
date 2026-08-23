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

## Verificação do pacote
- `unzip -l` (ou `zipfile.infolist()`) para confirmar o conteúdo.
- Scan de segredos nos .md antes de entregar; só placeholders.
- Confirmar que o HTML atribui MEDIA: `<caminho>` e os .md estão no .zip.

Ver `references/mercurio-snapshot.md` para o exemplo concreto de levantamento da rama Mercúrio.