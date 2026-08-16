# Espelhamento em massa de product/ → Google Drive (padrão Zera/CFP IA)

Fluxo validado 2026-08-14 (Zera/CFP IA): espelhar ~90 docs de `product/` no Drive e depois
reorganizá-los em subpastas temáticas. Complementa `md-to-gdoc.md`/`mermaid-rendering.md`.

## Espelhamento extra fora do fim de quinzena

O AGENTS.md do projeto manda espelhar "somente após sinalização explícita do usuário de fim de
quinzena". O usuário pode pedir **espelhamento extra** a qualquer momento ("espelhe tudo que não for
código em product/"). Procedimento:

1. **Mapear TODOS os .md de product/** e separar:
   - já mapeados nos scripts (`espelhar_gestao.sh`/`_engenharia.sh`/`_design_v2.sh`) → atualizar com
     `--doc-id` (preserva IDs);
   - novos → criar com `--parent <pasta>` (Gestão `1KKYtedSpNDYTVJENjRk42yHdBB0scHMJ`, Engenharia
     `17lBPefqbH4CcbnwFZkJYSeXTLzMIcK-j`, Design `12J-LRtfjOwErYQzRERl1PkJb8iFghStD`, Pesquisa
     `1r5wjyGc3qg-4z9NujWAi4Cag3weh8VaN`, Ideação `1Mx4nG9zrP_jW9UJar6k3SmERxeraeI_e`).
2. **Filtrar ruído de trabalho interno** (NÃO espelhar): `*-demo.md`, `feedbacks.md` (loop agy),
   `auditoria-rastreabilidade*`, `review-report.md`, `revisao-copys-tom-voz.md`, `artefatos/README*`.
   Script de exemplo: `/opt/data/igor-docs-md/espelho_extra.py` (gera a lista pendente + cria docs
   novos com `--parent`, anti-429 com sleep 3s).
3. **Consolidar IDs num script de atualização** (`espelhar_extra.sh`) — o próximo espelhamento de
   tudo vira 1 comando: os 3 scripts originais + `espelhar_extra.sh`.
4. **Anti-429:** os scripts originais têm `sleep` entre docs (8 docs de gestão ≈ 4-5 min); rodar em
   background (`background=true` + `notify_on_complete=true`) — cada doc imprime
   "Conteúdo aplicado: N blocos (M operações)".

## Reorganização em subpastas temáticas (mover 100s de docs)

1. **Mover exige `addParents`/`removeParents` como QUERY PARAMS — NUNCA `parents` no body do PATCH.**
   `PATCH files/{id}` com body `{"parents": [new]}` → **403 Forbidden**. Padrão correto:
   ```
   PATCH files/{id}?addParents={new}&removeParents={old}&fields=id,parents
   ```
   `removeParents` vazio também dá 403 — o parent antigo é obrigatório (buscar via `fields=parents`
   antes de mover).
2. **DELETE retorna corpo VAZIO** — `json.loads(resp)` falha com `JSONDecodeError`. Tolerar resposta
   vazia (`if not resp: return {}`) no wrapper da API.
3. **Pasta duplicada ao re-executar:** se um run anterior criou a subpasta mas falhou no meio (403),
   um segundo run cria outra com o mesmo nome. Antes de criar, procurar por nome; se já existe,
   fundir (mover itens da vazia → cheia) e apagar a duplicada.
4. **Match por substring em massa:** chaves específicas por subpasta (ex.: "LGPD & Privacidade" →
   `[RIPD, Termo de Uso, Política de Privacidade, Inventário, Fluxo de Solicitações]`). Chaves
   amplas (".pdf") podem casar o mesmo arquivo em duas subpastas — o último move vence (inofensivo,
   mas confira o destino final).
5. **Dry-run antes de executar** (`--dry`): imprime "criaria X / moveria Y" sem tocar no Drive.
   Script de exemplo: `/opt/data/igor-docs-md/organizar_drive.py` (88 docs movidos em 1 execução,
   PRD/Roadmap mantidos na raiz conforme pedido do usuário).
6. **Mover NÃO quebra os scripts de espelhamento:** os scripts usam `--doc-id` (localiza o doc por
   ID, independente da pasta). Só se quiser que o espelhamento futuro TAMBÉM force a pasta certa é
   que os scripts precisariam mover de volta — opcional.

## Verificação pós-espelhamento (mermaid)

`/opt/data/igor-docs-md/verificar_mermaid_drive.py` — conta blocos ` ```mermaid ```` em cada .md
local vs imagens `inlineObjects` no doc do Drive (Docs API `?fields=inlineObjects`), e avisa quando
um doc tem múltiplos nodes/linha (padrão que merece checagem visual — ver
`mermaid-rendering.md` "MÚLTIPLOS nodes por linha").
