# Evolve — relatório 2026-11-09

## Estado

| Métrica | Entrada | Saída |
|---|---|---|
| Skills no catálogo | 179 | **178** |
| Skills no disco | 180 | **178** |
| Relações | 276 | **304** |
| Órfãos (grafo) | 13 | **1** (justificado) |
| Categorias | 15 | 15 (`media` criada na etapa update) |

## Merges

### M1 — `business/cobranca-cliente-aprovacao` → `business/cobranca-clientes-id`
Duas versões da mesma política do dono, escritas em 04/11 em sessões diferentes. Sobreviveu a
que tem `references/fluxo-operacional.md` + `scripts/ler_thread_gmail.py` e metadados ID-scoped.
Absorvido (5.191 → 9.712 chars):
- `## Tom do texto (registro do dono, 04/11/2026)` — neutro e direto, estrutura fato → promessa
  não cumprida → pedido objetivo → dados → assinatura; `descricao_entrega` guardado para o N3.
- `## Antes de escrever o texto (não pule)` — extrato primeiro, leitura da thread **e** dos
  últimos 30 dias do domínio, promessa sem data não é prazo, rascunho obsoleto se o contexto muda.
- `## Como operar (motor)` — CLI do `cobranca_fluxo.py` (`status/preparar/listar/aprovar/enviar/
  prazo/pago`), cron 09:05 no DM do dono, e a nota de que sucede o `cobranca_sm_diaria.sh`
  documentado nas references.
- `## Novo cliente` — clonar `work/cobranca-sm/` e os campos de `config.json`/`estado.json`.
- 6 armadilhas: saudação/data pelo horário do envio (não do rascunho), thread forçada
  (`threadId` + `In-Reply-To`), fail-closed, uma cobrança por dia, feriado não é dia útil,
  sem emoji + assinatura fixa.
- Descrição ganhou parágrafo de gatilho (era one-liner).

### M2 — `software-development/local-postgres-sandbox` → `software-development/postgres-sandbox-verification`
Mesmo workflow (extrair `.deb`s → `initdb` → `pg_restore` → backend real → driver HTTP com prova
por SQL), mesmo toolchain, pitfalls sobrepostos. Absorvido:
- 3 pitfalls: upsert `ON CONFLICT (email)` idempotente; `delete_rule` das FKs antes do DELETE
  (CASCADE em `sessoes→usuarios` × 500 sem CASCADE); dump com schema fora de `public`
  (`pg_restore -l` antes de assumir onde está a tabela).
- `references/artemishub-auth-diagnostico.md` e `references/artemishub-auth-usuarios.md`.
- `references/opencode-llm-diagnostico.md` é fora de tema (diagnóstico de chave/fallback LLM) →
  realocado para `autonomous-ai-agents/hermes-inference-config/references/`, onde convive com
  `credential-failure-diagnosis.md` e `opencode-provider-setup.md`.

Cópias de segurança dos absorvidos: `cache/scratch/absorbed-cobranca-cliente-aprovacao/`,
`cache/scratch/absorbed-local-postgres-sandbox-SKILL.md` (fora do repo).

## Pares avaliados e mantidos separados (depth-1)

- `microsoft-office` × `powerpoint` × `docx`/`xlsx` — `microsoft-office` é guarda-chuva por
  extensão; `powerpoint` guarda o checklist de deck (template, verificação visual, PDF); `docx` e
  `xlsx` são toolchains próprias. Fundir apagaria o valor real do `powerpoint`.
- `cobranca-clientes-id` × `invoice-chase` — rotina ID com gate de extrato e motor próprio ×
  estratégia genérica de ledger (decisão de 02/11 mantida).
- `contrato-prestacao-servicos-b2b` × `contratos-justos-id` × `analise-contratual` ×
  `direito-empresarial-brasileiro` — redigir contrato novo × régua do contrato justo × revisar
  minuta alheia × pano de fundo jurídico. Fluxos distintos; relacionadas, não fundidas.
- `design-md` × `brand-design-system-html` — spec de tokens (DESIGN.md, lint, export) × design
  system de marca do cliente em HTML. Ferramentas e artefatos diferentes.

## Órfãos

13 nós estavam ilhados (os 12 novos + `openhue`). Fechados 12 com 28 arestas:

- `cobranca-clientes-id` → invoice-chase, emissao-nfse, gestao-financeira-id, google-workspace
- `dossie-de-pessoa-id` → id-comunicacao-multiusuario (a própria skill manda consultar o registro
  por `chat_id` do sócio)
- `contrato-prestacao-servicos-b2b` → contratos-justos-id, direito-empresarial-brasileiro,
  formalizacao-acordo-cliente, md-to-timbrado-id
- `doc-brand-theming` → google-docs-formatting, md-to-timbrado-id, brand-design-system-html,
  contrato-prestacao-servicos-b2b (as três primeiras já estavam no `related_skills` do frontmatter)
- `microsoft-office` → powerpoint, docx, xlsx, pdf
- `powerpoint` → html-deck-to-pptx, design-md
- `design-md` → brand-design-system-html, documento-a4-marca-id
- `airtable` → google-sheets-automation, xlsx
- `box` → google-workspace
- `gif-search` → songsee, comfyui · `songsee` → comfyui
- `llm-wiki` → systematic-research, deep-research

`openhue` permanece órfã **com justificativa**: única skill de smart-home do fork, sem par
semântico no catálogo; não há com quem fundir nem motivo para deletar.

## Grafo

`python3 scripts/generate_catalog_graph.py` → **178 nós / 304 arestas / 1 órfão**.
`skills_graph.html` 114 KB.

## Pendências registradas (não executadas nesta run)

1. **82 descrições de uma linha** (sem 2º parágrafo) — mesma decisão editorial de 26/10: as
   one-liners do fork são auto-contidas e a expansão em lote produziria parágrafo genérico sem
   lastro. Backlog oportunístico (expandir quando a skill for editada por outro motivo).
2. **9 pares de relações duplicadas** no apêndice (`augmentation-process-design→augmentacao-query`,
   `product-pipeline→backlog-and-sprint`, `dedalo-squad→bpmn-diagram-renderer`,
   `html-pdf-fidelity→html-to-pdf-chromium`, `emissao-nfse→inter-api-id-consultoria`,
   `planejamento-estrategico-8h-id-olimpo→planejamento-estrategico-2h`,
   `hermes-inference-config→hermes-agent`, `hermes-cron-script-dispatch→hermes-agent`,
   `artemishub-onboarding-patterns→devops-artemishub`). Inócuas na renderização (o grafo deduplica),
   mas poluem o arquivo. Cada linha aparece 2× — remoção exige patch com contexto largo; deixado
   para a próxima run.
3. **Skills de comunidade fora do escopo ID** (`airtable`, `box`, `gif-search`, `songsee`,
   `llm-wiki`, `design-md`) — mantidas por uso plausível; candidatas a arquivamento se o dono
   decidir enxugar o catálogo. Não deletadas sem aprovação.
