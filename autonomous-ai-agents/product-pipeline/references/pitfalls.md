# Catálogo de armadilhas — product-pipeline

Cada item tem ID estável. Cite o ID no relatório em vez de repetir o texto.

**Como usar:** os títulos são sintomas. Busque pelo que você está vendo (`grep -i "tela branca"`),
não pelo nome da causa. Se não achar, vá para a fase correspondente em `pipeline-fase*`.

IDs: `P-<área>-<n>`. Áreas: PROC processo · PI Pi Agent · AGY revisão · DSN design ·
FRONT frontend · BACK backend · DEP deploy · ENV ambiente · RESEARCH pesquisa · TOOLS Google.


## Processo, escopo e verificação

### P-PROC-01 — Hermes coleta evidência, NÃO diagnóstica bugs na 4e

Só reportar o que viu.

### P-PROC-02 — F1 scope: manter conceitual

Feature matrix, schema de dados, entidades e arquitetura são materiais de F3 em diante. A ideação deve ficar em nível de promessa, persona, nome/conceito e delimitação de escopo. **Não fixar entidades, schemas ou campos durante a consolidação da F1** — o que importa são as regras (ex: "IA não altera o schema"), não a estrutura em si. O nome do projeto carrega o conceito — registrar no `ideation-result.md`.

### P-PROC-03 — NUNCA avançar fases sem a anterior concluída

O usuário corrigiu este comportamento 2x: "Espere cada etapa terminar antes de seguir para a próxima. Seja fiel à skill." e "Espere as revisões terminarem antes de seguir as etapas seguintes." Execução sequencial estrita é mandatória. Use `process(action='wait')` para bloquear até o processo terminar antes de iniciar a próxima fase.

### P-PROC-04 — NUNCA escrever frontend manualmente

"Aliás, pode apagar tudo de frontend feito manualmente por você na última tentativa." Todo HTML/CSS/JS é gerado exclusivamente por Pi Agent. Hermes não edita código. Se o Pi gerou algo incompleto, Pi corrige (com feedback do agy), nunca Hermes.

### P-PROC-05 — F4b code-tasks docs são corrigidos no MESMO loop que o código

Quando agy revisa F4b, ele encontra issues tanto no código quanto nos docs de engenharia (code-tasks.md, ERD.md, test-plan.md, etc.). O Pi best DEVE corrigir AMBOS na mesma iteração. Não corrigir só o código e deixar os docs com issues pendentes — isso gera deploy com docs inconsistentes.

### P-PROC-06 — Gap review após pull/rebrand — verificar estado real antes de agir

Quando o usuário faz alterações no repo (pull, rebrand, refactor), o estado do código pode ser radicalmente diferente do esperado. Antes de fazer deploy ou correções, executar `git pull` e depois Pi best faz revisão exaustiva (code-review + dogfood QA) gerando `gap-report.md` que mapeia TODOS os gaps vs PRD + referência de UI. Só então decidir se deploya direto ou executa correções. Exemplo real: V6.0 rebrand reduziu design-system.html de 118KB para 1.3KB placeholder — deploy sem gap review teria publicado shell vazio. Template do relatório em `skill_view(name='product-pipeline', file_path='references/gap-report-template.md')`.

### P-PROC-07 — Gap report define plano de ação, não apenas diagnóstico

O gap-report.md de 83 itens do VERO organizou as correções em 5 fases com estimativas de esforço (Fundação 8h → Services 6h → Modais 14h → Fluxos 6h → UX 6h), totalizando ~40h alinhadas com o code-tasks.md. Esse padrão de fases é reutilizável: usar como template para qualquer projeto que precise de correção pós-gap-review.

### P-PROC-08 — Pi best refatora monólito → modular em uma sessão

Com deepseek-flash, Pi consegue refatorar um arquivo HTML monolítico de 80KB em 35+ arquivos modulares (CSS, JS, views, services, utils, store) em ~12 minutos. Incluir no prompt: estrutura de diretórios desejada, regras de modularização, e seed data expandido. O build.sh e verificação `node --check` garantem que a saída é funcional. Padrão comprovado no VERO Fase 1.

### P-PROC-09 — Auditoria de protótipo F4a: mock data é ESPERADO, não é gap.

Ao auditar rastreabilidade de protótipo de alta fidelidade (pré-integração), avaliar se cada passo de cada fluxo é **REPRODUZÍVEL na tela com dados mockados** — e NÃO se está conectado ao backend. Usar a classificação DEMONSTRADO / DEMONSTRÁVEL PARCIAL / NÃO DEMONSTRÁVEL. Dois passos de auditoria: v1 (critério backend — marca tudo PARCIAL) e v2 (critério mock — isola gaps reais de demonstração). Método completo, matriz card-a-card do dashboard e checklist do que NÃO é gap: `references/prototipo-mock-audit-criterio.md`.

### P-PROC-10 — Verificação de completude de formulários — comparar campo a campo

Modais de criação frequentemente têm 70-90% dos campos ausentes. Para verificar: ler `referencia_completa_de_ui.md` (checklist definitiva), abrir cada modal no browser, comparar cada campo individualmente. Exemplo: modal de Aplicação tem 6 blocos com 25+ campos na referência, mas implementação atual tem 1 campo. Usar Pi + dogfood para auditoria sistemática, NÃO confiar em inspeção visual rápida.

### P-PROC-11 — Correção massiva de modais em um único prompt Pi

Após gap review, é mais eficiente consolidar TODAS as correções de modais (Fases 3-5) em UM prompt Pi best (~9KB) do que em sprints separados. Um prompt exaustivo listando cada campo de cada modal (referenciando `referencia_completa_de_ui.md`) permite que o Pi reescreva todas as views em uma sessão (~12-15 min, deepseek-flash). O padrão: "Para cada view, completar TODOS os campos da referência de UI. Nenhum campo pode faltar." Testado com 8 views reescritas em uma execução (VERO Fase 3-5).

### P-PROC-12 — Hierarchy-driven expansion — quando o usuário fornece uma especificação de UI completa

Se um documento como `hierarquia_de_páginas_e_componentes.md` é fornecido definindo cada página, sub-página, filtro, coluna de tabela e campo de modal, o fluxo correto é:
1. `git pull` para obter o estado mais recente (inclui design-system atualizado + hierarquia)
2. Pi best gera `code-tasks-v2.md` analisando o delta entre implementação atual e a hierarquia
3. Pi best executa TODAS as tasks em uma sessão (deepseek-flash, timeout 60min)
4. SINCRONIZAR local → shared volume
5. Build + deploy
6. agy revisa integridade estrutural (views conectadas? CSS implementado? seed data expandido?)
7. Pi corrige issues do agy → agy confirma → ACORDO
8. Dogfood QA no browser (verificar runtime JS, navegação entre 3-4 views)
9. Relatório + commit + push

> Cuidado: Pi tende a implementar ~60% do escopo na primeira execução e reportar 100%. O agy normalmente encontra 3-5 issues críticas (CSS ausente, views órfãs, seed data não expandido). Uma segunda iteração resolve.


## Pi Agent — invocação e monitoramento

### P-PI-01 — Pi best não streama stdout intermediário

Com DeepSeek V4.1 Flash, Pi pode levar alguns minutos por documento sem produzir stdout. Monitorar pelos arquivos de saída, não pelo output do processo. Usar `terminal(background=true)` + `ls -la` periódico.

### P-PI-02 — batch-splitting para tarefas grandes do Pi

Quebrar em lotes de 2-3 docs. o modelo best aguenta ~3 docs/sessão; o modelo cost ~2.

### P-PI-03 — Pi parece travado mas output já está completo

Verificar arquivos no shared volume antes de matar.

### P-PI-04 — Prompt file ausente mata Pi silenciosamente

Se o prompt file não existe (ex: `cat prompts/pi-layer6-polish.md`), Pi morre imediatamente com exit code 1. Verificar `ls prompts/` antes de invocar. Se um layer não tem prompt, criar antes de disparar Pi.

### P-PI-05 — delegate_task timeout (600s)

Executar Pi diretamente do Hermes, não delegar.

### P-PI-06 — o modelo cost para docs de engenharia

Suficiente. o modelo best reservado para decisões arquiteturais.

### P-PI-07 — Pi skills não existem por padrão

Instalar manualmente.

### P-PI-08 — MiniMax M3 free encerrado

Usar `opencode-go/deepseek-flash`.

### P-PI-09 — DeepSeek V4.1 Flash timeout

Usar o modelo cost ou `/compact preserve:context`.

### P-PI-10 — Monitoramento de Pi — intervalos curtos

Usuário prefere monitoramento frequente com intervalos de 2-3 minutos (não 5+). Verificar arquivos de saída com `find` a cada ~120s. Se o Pi ficar 5+ minutos sem escrever novos arquivos, auditar a sessão JSONL para ver se estagnou (skill `pi-session-audit`).


## agy — revisão, permissões e limites

### P-AGY-01 — agy prototype — executar no host, não no container

agy está em `agy (no host)` no host Oracle. Usar `ssh oracle-host` com `--print` para geração não-interativa. O modelo `gemini-3.1-pro` funciona bem para protótipos complexos. `--print-timeout 5m` evita timeout prematuro.

### P-AGY-02 — agy SSH: prompt file deve ser copiado para o host

agy roda no Oracle host, não no container Hermes. O prompt file precisa ser copiado via `cat prompts/file.md | ssh oracle-host 'cat > /tmp/file.md'` antes de invocar. Referenciar com `agy --print "$(cat /tmp/file.md)"` no host. Não é possível ler arquivos do container diretamente do host via agy.

### P-AGY-03 — `agy -p` stallou em Docker commands

### P-AGY-04 — `agy design` NÃO valida código existente

Gera novo design hipotético. Usar browser tools.

### P-AGY-05 — agy output token limit (>70KB)

Quebrar em CSS/HTML/JS separados.

### P-AGY-06 — agy headless requer --dangerously-skip-permissions

Sem essa flag, o agy em modo `--print` (não-interativo) NÃO consegue usar `write_file`. O output será: `no output produced — a tool required the "write_file" permission that headless mode cannot prompt for, so it was auto-denied`. **Sempre usar:**
```bash
ssh oracle-host 'agy (no host) --print "$(cat /tmp/prompt.md)" --dangerously-skip-permissions'
```

### P-AGY-07 — Verificar TODAS as issues do agy antes de fazer deploy

Após Pi corrigir baseado no feedback do agy, verificar CADA issue listada no `feedbacks.md` ou `review-report.md`. Não confiar que "Pi corrigiu tudo" — auditar explicitamente. Padrão: `grep "RESOLVIDO\|🟢\|ACORDO"` no arquivo de feedback. Só fazer deploy quando TODAS as issues 🔴 estiverem resolvidas e agy tiver escrito `ACORDO`.

### P-AGY-08 — Pi "done" summary NÃO é evidência — agy SEMPRE re-verifica

Após Pi executar um lote grande de tasks (ex: 81 tasks), o output summary do Pi lista bullet points do que foi feito, mas isso é ASPIRACIONAL, não factual. Na prática: Pi disse que implementou CSS da sidebar secundária, conectou 21 views ao router, expandiu seed data e atualizou 7 modais — agy verificou e NENHUMA dessas entregas estava completa. O CSS não existia, as views estavam órfãs (`renderPlaceholder`), seed data não foi expandido, e só 1 de 7 modais foi atualizado. **Nunca pular a revisão do agy após Pi executar code-tasks em lote — Pi superestima seu próprio progresso.** O agy é a única fonte confiável de verificação de completude.

### P-AGY-09 — agy não pega erro de runtime

Revisar arquivos `.js` não executa o código. `fmt is not defined`, `TypeError: Cannot read
properties of undefined` e outros erros de escopo só aparecem quando o navegador roda a página —
e o agy pode aprovar código que quebra na primeira navegação. **Sempre complementar com browser:**
navegar 3–4 views, checar `browser_console()` em cada transição, confirmar que a tabela renderiza
dados reais. O loop completo é agy revisa → browser verifica → se ambos OK, `ACORDO`.

## Design system, Stitch e revisão visual

### P-DSN-01 — Stitch MCP — config no `$HERMES_HOME/config.yaml`, NÃO no `.hermes/config.yaml`

O override (`~/.hermes/config.yaml`) funciona para desenvolvimento rápido, mas o config principal (`$HERMES_HOME/config.yaml`) é o repositório oficial. Stitch MCP HTTP não funciona via npx proxy — usar `url:` + `headers:` + `transport: http`. A API key vai no header `X-Goog-Api-Key`. Editar via SSH no host com Python (não sed) para evitar YAML malformado.

### P-DSN-02 — Stitch MCP — design system ANTES das screens

Sempre verificar/atualizar o design system no Stitch antes de gerar screens. Screens geradas com tokens errados (LIGHT em vez de DARK, fonte errada) precisam ser descartadas e regeneradas.

### P-DSN-03 — Stitch UpdateDesignSystem — fontes limitadas

BRICOLAGE_GROTESQUE não funciona no UpdateDesignSystem. Usar SPACE_GROTESK como alternativa. Testar fontes no Update antes de tentar no Create.

### P-DSN-04 — Stitch MCP — usar o mesmo design system id em todas as telas

Para consistência visual, passar `designSystem: assets/<id>` em toda chamada de `generate_screen_from_text`.

### P-DSN-05 — Stitch MCP — usar HTTP direto, não stdio proxy

A API key funciona no header `X-Goog-Api-Key` quando usada via HTTP MCP direto (`url:` + `headers:`). O `@_davideast/stitch-mcp` package tem um subcomando `tool` que NÃO funciona com API key. Usar `transport: http` com headers no config do Hermes. Ver `skill_view(name='product-pipeline', file_path='references/google-stitch-mcp.md')`.

### P-DSN-06 — Pi cost frontend sem contexto visual dos design HTMLs

O prompt pode ter os tokens hex copiados, mas Pi NÃO vê o layout renderizado (glassmorphism, posicionamento, protótipo). Isso produz frontend com tokens corretos mas layout genérico. **Sempre incluir `cat design-system.html` e `cat index.html` (protótipo) no prompt do Pi cost** quando o layer for frontend. Verificar pós-execução com auditoria de sessão (passo 8 do F4b).

### P-DSN-07 — Verificação de leitura de design files pelo Pi — auditoria JSONL

Após Pi gerar frontend, verificar se ele realmente leu os arquivos de design ou só os mencionou em `ls`. Técnica:
```python
import json, glob
for sf in sorted(glob.glob(os.path.expanduser('~/.pi/agent/sessions/--*projeto*--/*.jsonl')))[-5:]:
    text = open(sf).read()
    for kw in ['design-system.html', 'index.html']:
        if kw in text:
            found = any(kw in line and ('cat ' in line.lower() or 'read_file' in line.lower()) for line in text.split(chr(10)))
            print(f'  {"✅" if found else "⚠️"} {kw}: {"lido" if found else "mencionado mas não lido"}')
```
Se não foram lidos, recriar o prompt instruindo explicitamente `cat product/design/design-system.html` antes de escrever frontend.

### P-DSN-08 — Pi salva arquivos no path LOCAL, não no shared volume — sincronizar ANTES da revisão do agy

Quando o projeto está clonado em `$LOCAL/<projeto>/`, o Pi Agent salva em `$LOCAL/<projeto>/product/` (path local), mas o agy SEMPRE lê de `$WS/<projeto>/product/` (shared volume). Se a sincronização for feita só depois do deploy, o agy vê os arquivos ANTIGOS e reporta "NÃO RESOLVIDO" para correções que já foram aplicadas. Isso força uma iteração extra no loop de revisão — desperdiçando tokens e tempo.

**Sequência correta após Pi terminar:**
```bash
# 1. Sincronizar do path local → shared volume (ANTES de qualquer review)
cp $LOCAL/<projeto>/product/design/js/app.js $WS/<projeto>/product/design/js/app.js
cp $LOCAL/<projeto>/product/design/js/router.js $WS/<projeto>/product/design/js/router.js
cp $LOCAL/<projeto>/product/design/js/views/*.js $WS/<projeto>/product/design/js/views/
cp $LOCAL/<projeto>/product/engineering/*.md $WS/<projeto>/product/engineering/

# 2. Rodar build.sh do path LOCAL (copia para public/)
cd $LOCAL/<projeto>/product/design && bash build.sh

# 3. Deploy (vercel build + vercel deploy --prebuilt)

# 4. SÓ ENTÃO invocar agy (que lê do shared volume)
ssh oracle-host 'agy (no host) --print "..." --dangerously-skip-permissions'
```

**Verificação de sincronização:**
```bash
# Comparar timestamps — shared volume deve ser >= local
ls -la $LOCAL/<projeto>/product/design/js/app.js $WS/<projeto>/product/design/js/app.js
```

> Exemplo real: VERO F4e — agy reportou 4 issues como "NÃO RESOLVIDO" na iteração 2 porque o router.js e app.js corrigidos pelo Pi não foram sincronizados para o shared volume. O Pi corrigiu corretamente (try/catch, admin route, compras view, secondaryNavs), mas o agy leu as versões antigas. Após `cp` manual, agy aprovou `ACORDO: MVP APROVADO`.

### P-DSN-09 — F4a e F4b têm o MESMO loop de revisão (agy→Pi→agy até ACORDO)

Não tratar F4b como "revisão única". O fluxo é idêntico ao F4a: agy revisa → Pi corrige → agy re-revisa → repete até agy escrever `ACORDO: ENGENHARIA FINALIZADA`. Na prática, foram necessárias 2 iterações para F4b (6 issues na 1ª, 0 na 2ª). Nunca fazer deploy com issues 🔴 pendentes no review-report.md.

### P-DSN-10 — O loop de revisão agy é OBRIGATÓRIO também em code-tasks de demonstração 100% mock (F4a demo loop).

Correção real do usuário (CFP IA, ago/2026): *"Você não parece ter carregado todo o loop da skill. Tem a parte de revisão com o Agy no final. Relembre a skill product-pipeline corretamente"* — eu tinha planejado só Pi gera → build → commit, sem agy. O plano correto para QUALQUER execução de code-tasks (mesmo mock-only, fechando lacunas de demonstração) é: Pi gera (lotes sequenciais, nunca paralelo) → **sync local→shared volume** → agy Turno 1 (escreve feedbacks.md) → Pi Turno 2 (correções) → agy Turno 3 (re-review até `ACORDO: DEMO FINALIZADA`) → build → commit.

### P-DSN-11 — Clone digital não é a pessoa real

O clone digital é hipótese, não retrato: o modelo infere crenças, filosofia e citações que a
pessoa não endossa. Separar dado verificável (idade, formação, links, commits) de inferência do
modelo; apresentar ao usuário para validação; tratar a correção dele como verdade final e
remover o traço de **todas** as seções. Exemplo: o clone do Tácio atribuiu a ele "o método é a
jaula"; o usuário corrigiu, e o traço foi removido de 5 pontos do documento.

## Frontend — SPA, rotas e wiring

### P-FRONT-01 — Frontend pode usar endpoints que não existem no backend

Pi cost gera frontend e backend separadamente, e o frontend pode referenciar rotas que o backend não implementou (ex: `/actions` em vez de `/tasks`). Verificar todas as URLs no frontend JS contra os routers registrados em main.py. Padrão: `api.get('/actions')` → `api.get('/tasks')`, `api.patch('/actions/${id}')` → `api.patch('/tasks/${id}')`.

### P-FRONT-02 — Dashboard/Weekly/Timeline routes não existem por padrão

Pi cost gera apenas CRUD básico (tasks, projects, contexts, auth, search). Endpoints agregados **não são criados** a menos que o prompt os peça explicitamente. Incluir seção de rotas agregadas obrigatórias no prompt.

### P-FRONT-03 — CORS + credentials + wildcard é inválido

`allow_origins=["*"] + allow_credentials=True` é rejeitado por navegadores. Usar `allow_origins=settings.CORS_ORIGINS` com lista explícita.

### P-FRONT-04 — Frontend scaffolding

Criar arquivos manualmente, não usar `create-vite`.

### P-FRONT-05 — design-system.html PODE ser o frontend deployável

Para MVPs puramente frontend (SPA estática com dados mockados, deploy Vercel/Netlify), o `design-system.html` gerado pelo Pi na F4a frequentemente é funcional o suficiente para ser o frontend final. Não precisa executar 103 code-tasks da F4b se o HTML já cobre todos os módulos. Decisão: verificar se o design-system.html tem SPA routing, todos os modais do PRD e dados mockados. Se sim → deploy direto. Se não → Pi cost executa code-tasks para preencher gaps.

### P-FRONT-06 — SPA vanilla: 3 registros obrigatórios ao adicionar uma nova view

Quando Pi cria uma nova view (ex: `compras.js`, `admin.js`) em uma SPA vanilla, o `app.js` precisa de 3 registros explícitos ou a navegação quebra silenciosamente (clique no sidebar não faz nada, sem erro visível, fica na página anterior):
1. **Rota:** `VERO.router.route('compras', () => VERO.views.compras.render(container))` — sem isso, o router não encontra o handler
2. **secondaryNavs:** `secondaryNavs.compras = [...]` ou `secondaryNavs.compras = null` — sem isso, `updateSecondarySidebar()` lança TypeError ao acessar propriedade de `undefined`
3. **RBAC (se necessário):** `if (!VERO.authService.temPermissao('admin')) { renderAcessoRestrito(); return; }` — sem isso, usuários sem permissão acessam rotas restritas

**Verificação pós-Pi:**
```bash
# Confirmar que cada nova view tem os 3 registros
grep "router.route.*compras\|router.route.*admin\|router.route.*faturamento" js/app.js
grep "secondaryNavs.*compras\|secondaryNavs.*admin\|secondaryNavs.*faturamento" js/app.js
grep "temPermissao.*admin" js/app.js
```
> Exemplo real: VERO F4e — agy identificou 4 bugs de router (admin não registrado, compras como placeholder, secondaryNavs sem apontamentos, JS exception na troca de views) mesmo com o código de view correto. Todos eram falhas de wiring no app.js.
>
> **Quando o wiring quebra em massa (50+ placeholders com todas as views existindo):** Ver `references/mass-route-reconnection.md` — padrão de reescrita do router que conecta as views existentes em uma sessão Pi, eliminando todos os renderPlaceholder de uma vez.

### P-FRONT-07 — IIFE closure scope bug em views vanilla JS

Padrão recorrente em SPA com módulos IIFE: `var store = VERO.store, dom = VERO.dom, fmt = VERO.format` declarado DENTRO de `render()`, mas funções helper como `_renderRows()`, `_paginationHtml()`, `_modalHtml()` tentam usar essas variáveis sem tê-las em escopo. O erro em runtime é `ReferenceError: fmt is not defined` ou `TypeError: Cannot read properties of undefined (reading 'get')`.

**Sintoma:** Router tenta carregar a view, console mostra `VERO Router: erro ao carregar módulo "apontamentos"`, tela mostra fallback "⚠️ Erro ao carregar módulo".

**Fix correto:** Passar `fmt`/`store`/`dom` como PARÂMETROS para as funções helper que precisam deles:
```js
// ERRADO — fmt só existe dentro de render()
function render(container) {
  var store = VERO.store, fmt = VERO.format;
  html += _renderRows(store, items);  // _renderRows não acessa fmt
}
function _renderRows(store, items) {
  items.forEach(function(a) {
    html += '<td>' + fmt.formatData(a.data) + '</td>';  // ReferenceError!
  });
}

// CERTO — passar fmt como parâmetro
function render(container) {
  var store = VERO.store, fmt = VERO.format;
  html += _renderRows(store, items, fmt);
}
function _renderRows(store, items, fmt) { ... }

// Também cerTO — declarar no escopo IIFE (se a view for carregada depois das deps)
VERO.views.apontamentos = (function() {
  var store = VERO.store, dom = VERO.dom, fmt = VERO.format;  // IIFE scope
  function render(container) { ... }
  function _renderRows(items) { ... }  // acessa fmt do closure
})();
```
**Atenção com IIFE-level:** Só funciona se o script da view carregar DEPOIS de store.js, dom.js e format.js no index.html. Se houver dúvida sobre ordem de carregamento, prefira passar como parâmetro.

**Verificação pós-Pi em todas as views:**
```bash
# Encontrar funções helper que usam fmt/store/dom mas não os recebem como parâmetro
for f in js/views/*.js; do
  helpers=$(grep -n "function _" "$f" | grep -v "render")
  fmt_in_render=$(sed -n '/function render/,/^  }/p' "$f" | grep -c "var.*fmt = VERO.format")
  echo "$f: render declara fmt=$fmt_in_render, helpers=$(echo "$helpers" | wc -l)"
done
```

**Variante: variable shadowing em callbacks aninhados** — O mesmo padrão de escopo pode ocorrer via shadowing acidental: `var s = VERO.store` declarado no topo, mas um `reduce` interno usa `s` como nome de acumulador, sombreando a store. Sintoma: `TypeError: s.find is not a function` (porque `s` virou número). **Fix:** usar nomes distintos (`store` para a store, `acc`/`sum` para acumuladores). Ver `references/variable-shadowing-in-callbacks.md` para diagnóstico completo, checklist de nomes e script de detecção. Exemplo real: `nutricao-aplicacoes.js` — `s` era `VERO.store` mas foi sombreado por `s` no `reduce` interno.

> Exemplo real: VERO — apontamentos.js quebrou após modularização. `fmt` declarado em `render()` mas usado em `_renderRows()` e `_refreshTable()`. Corrigido passando `fmt` como 3º parâmetro. Outras 6 views não usavam `fmt` e estavam OK.

### P-FRONT-08 — Sidebar alignment audit — verificar contra referencia_completa_de_ui.md

Após Pi gerar o sidebar (app.js + index.html), SEMPRE verificar contra a referência de UI item por item. Pi frequentemente introduz desvios:

| Desvio comum | Exemplo real | Correção |
|-------------|-------------|----------|
| **Nome errado** | "MIP e MID" em vez de "MIP e MED" | Renomear no HTML do sidebar |
| **Item ausente** | "Apontamentos" não listado | Adicionar à lista de links |
| **Item extra** | "Colheita" no sidebar (não está na ref) | Remover — Colheita é sub-fluxo, não item do menu |
| **Sem grupos** | Todos os links planos, sem labels de seção | Adicionar section headers (PRODUÇÃO AGRÍCOLA, etc.) |
| **Admin ausente** | "⚙️ Administrador" não aparece | Adicionar ao final do sidebar com RBAC |
| **Telas placeholder** | Módulos secundários renderizam `renderPlaceholder()` em vez da view real | Registrar rota com `VERO.views.compras.render(container)` |

**Checklist de verificação pós-Pi:**
```bash
# 1. Sidebar tem todos os itens da referência?
grep -c "Apontamentos\|MIP e MED\|Administrador\|PRODUÇÃO AGRÍCOLA" index.html

# 2. Nenhum placeholder escapou? (não deve ter nenhum match)
grep -c "renderPlaceholder" js/app.js

# 3. Colheita NÃO está no sidebar? (deve ser 0)
grep -c "Colheita" index.html | grep -v "title\|heading"

# 4. Nomes estão corretos? (deve ser 0)
grep -c "MIP e MID" index.html js/app.js
```
> Exemplo real: VERO — sidebar tinha "MIP e MID", faltava "Apontamentos" e "Administrador", incluía "Colheita" indevidamente, 9 telas mostravam "Em desenvolvimento". Tudo corrigido em um prompt Pi de 4.8KB.


## Backend, banco e testes

### P-BACK-01 — Seed script requer tabelas criadas

`app/seed.py` assume que as tabelas existem (SELECT antes de INSERT). No container com PostgreSQL, as tabelas são criadas por Alembic. Para testar localmente com SQLite, primeiro criar tabelas: `Base.metadata.create_all(engine)` antes de rodar seed. Seed é idempotente — segunda execução mostra ⏭️ para todas as entradas.

### P-BACK-02 — Alembic env.py não deve substituir asyncpg por psycopg2

O env.py gerado pode conter `configuration["sqlalchemy.url"].replace("postgresql+asyncpg://", "postgresql+psycopg2://")`. `psycopg2` não está instalado na imagem slim. Remover a substituição — `async_engine_from_config()` funciona com asyncpg para DDL. Se migrations não existirem, gerar com `alembic revision --autogenerate -m "initial_schema"` dentro do container.

### P-BACK-03 — SQLite `func.now()`

Precisão de segundos. Usar `default=datetime.now(timezone.utc)` em vez de `server_default`.

### P-BACK-04 — Pi adora "***" como placeholder de senha

*" como placeholder de senha** — Substituir por `"secret123"`.

### P-BACK-05 — Backend restart: ConnectionResetError

Aguardar health check 200.

### P-BACK-06 — UUID no PostgreSQL vs String(36)

Usar `UUID` do dialect PostgreSQL.

### P-BACK-07 — Pi best overshoot em conftest

Não aceitar mudança no `event_loop` sem testar.

### P-BACK-08 — bcrypt pin

`bcrypt==4.0.1` no Dockerfile.


## Docker, deploy e host Oracle

### P-DEP-01 — Dockerfile: permissão 600 no host vira arquivo de 0 bytes na imagem

Quando um arquivo tem permissão `-rw-------` (600) e o dono é o usuário do container (hermes, uid 10000), o Docker daemon não consegue ler o conteúdo durante COPY, resultando em arquivo de 0 bytes na imagem. **Solução:** `chmod 644` em todos os novos arquivos antes de `docker compose build`.

### P-DEP-02 — Portas ocupadas no host Oracle

Portas comuns (5432, 8000, 80, 8080, 6379) podem estar ocupadas por outros projetos. Verificar com `ss -tlnp | grep -E ":{port} "`. Para db, usar `expose:` em vez de `ports:`. Para backend, usar `expose:` e deixar nginx como única porta externa. Escolher porta alternativa (>8080) e atualizar CORS origins.

### P-DEP-03 — Tests fora do Docker build context

`docker cp` obrigatório.

### P-DEP-04 — Oracle Cloud: portas

Apenas 80/443 externas. Usar NPM.

### P-DEP-05 — API QA via execute_code não alcança containers Docker

`execute_code()` roda dentro do container Hermes e não consegue alcançar containers no Oracle host via localhost. Para API QA, usar `ssh oracle-host` + curl diretamente no terminal, ou apontar para o IP do gateway Docker (`172.19.0.1`).


## Ambiente, permissões e paths

### P-ENV-01 — agy via SSH pode quebrar permissões do container

agy (SSH host, uid 1001) pode executar `sudo chown -R ubuntu:ubuntu` no diretório do projeto, e o container Hermes (uid 10000) perde escrita. **Fix REAL (comprovado CFP IA ago/2026):** `sudo chmod -R 777` pelo hermes FALHA com "Operation not permitted" quando o diretório pertence ao uid 1001 — o hermes não é dono nem tem permissão de escrita no pai. A correção que funciona é pelo host: `ssh oracle-host 'sudo chown -R 10000:10000 $WS/PROJETO'`. Verificar permissões após agy executar. **Prevenir:** antes de cada invocação do agy, rodar o chown de ida; depois, o chown de volta — ou conferir com `ls -ld` se o dono é `hermes`.

### P-ENV-02 — Pi PATH pode não estar definido

Pi está em `$PI`. Se `which pi` falhar, exportar PATH ou usar caminho absoluto.

### P-ENV-03 — Commit + tag ANTES de invocar Pi para fixes

Criar checkpoint antes de Pi modificar código.

### P-ENV-04 — Permissão do container — agy pode quebrar com chown

evitar. Ver pitfall "agy via SSH" acima.

### P-ENV-05 — UID mismatch

Hermes (10000) vs Pi (1001). Verificar permissões antes de cada fase.

### P-ENV-06 — Pre-flight check

Verificar antes de cada fase. O usuário não quer gastar tokens debugando permissão.

### P-ENV-07 — Workstation 777 não herda

Rodar `chmod -R 777` após criar pastas.

### P-ENV-08 — Git add com path explícito

`git add product/management/` em vez de `-A`.

### P-ENV-09 — Mirror `<projeto>.old/`

Verificar e remover lixo após corrigir permissões.

### P-ENV-10 — Prompt files no shared volume

UID mismatch bloqueia leitura do Pi.

### P-ENV-11 — patch/write_file falha com UID 1001

`chmod o+w` no diretório pai ou usar SSH.


## Pesquisa web (F2)

### P-RESEARCH-01 — web_search rate-limit por sessão

Primeiras 1-2 chamadas paralelas de `web_search` funcionam, mas chamadas subsequentes na mesma sessão retornam `{"data": {"web": []}}`. Isso NÃO é "backend quebrado" — é exaustão de cota por sessão. **Workaround:** front-load TODAS as queries críticas na primeira chamada paralela (até 5 queries em um batch). Se queries subsequentes falharem, ir direto para `web_extract` em URLs de alta autoridade conhecidas. Não retentar `web_search` com phrasing diferente — não vai recuperar. Ver `references/market-gtm-research-sources.md`.

### P-RESEARCH-02 — Blogs de plataformas edtech reestruturados

Thinkific, Kajabi, LearnWorlds, Teachfloor, Mighty Networks e similares reestruturaram blogs em 2024-2025. URLs de artigos 2022-2024 retornam 404 generalizado. Para pesquisa de mercado de cursos/edtech, usar sites de research/CRO (acceleroi.com, firstpagesage.com, digitalapplied.com) e market research firms (gminsights.com) — essas fontes têm dados de benchmark persistentes. Ver `references/market-gtm-research-sources.md`.

### P-RESEARCH-03 — Subagentes F2 precisam de instrução explícita de fallback

web_search rate-limita após 1-2 chamadas. Subagentes não sabem disso e ficam em loop de retry. Instruir NO CONTEXTO do delegate_task: "Se web_search retornar vazio 2x seguidas, ABANDONE web_search e use SOMENTE web_extract + browser_navigate em URLs diretas. Não insista em web_search com phrasing diferente."


## Google Workspace

### P-TOOLS-01 — Google OAuth PKCE — setup.py não persiste code_verifier

O script `setup.py` do google-workspace gera URLs de auth sem salvar o PKCE verifier. A troca falha com `Missing code verifier`. Usar `google_oauth_gen.py` + `google_oauth_exchange.py`. Ver `skill_view(name='product-pipeline', file_path='references/google-oauth-pkce-workaround.md')`.

### P-TOOLS-02 — Google token expira após ~7 dias

Refresh falha com `invalid_grant`. Re-autenticação completa PKCE necessária.
