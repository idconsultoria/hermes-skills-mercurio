# Espectador ao vivo de sessão Pi com a TUI ORIGINAL (pi_follow_tui.mjs)

Técnica validada em Zera (14/ago/2026): acompanhar uma sessão Pi rodando em background **com a mesma
TUI do Pi** (componentes reais, footer com tokens/custo/modelo), sem risco de corromper o JSONL
(só leitura) — enquanto o job real roda em `terminal(background=true)`.

## Por que não usar alternativas mais simples

| Abordagem | Resultado |
|---|---|
| `tail -f` do JSONL cru | Funciona, mas feio — sem métricas, sem formatação |
| `pi --export <jsonl> <out.html>` | Renderiza a sessão com a TUI real em HTML estático (pós-evento, snapshot) |
| TUI interativa `pi --session <jsonl>` | **PERIGO**: o job em background escreve no MESMO arquivo → 2 escritores → corrompe o JSONL |
| **`pi_follow_tui.mjs`** (este) | Lê o JSONL, re-renderiza a cada ~2s com os componentes REAIS da TUI — seguro (só leitura) |
| Modo RPC (`--mode rpc`) | Emite eventos em tempo real, mas exige que o JOB FOI INICIADO em RPC mode — não dá para anexar a job já rodando em print-mode |

## Localização obrigatória do script

O script DEVE ficar **dentro da árvore do pacote** do Pi (senão o Node não resolve os módulos ESM):

```
/opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent/pi_follow_tui.mjs
```

O package.json do `pi-coding-agent` tem `"exports"` que **bloqueia subpaths** — imports do tipo
`@earendil-works/pi-coding-agent/dist/...` falham com `ERR_PACKAGE_PATH_NOT_EXPORTED`. Usar caminhos
relativos ao `dist/`:

```js
import { Container, TUI, ProcessTerminal, Spacer, Text } from "./node_modules/@earendil-works/pi-tui/dist/index.js";
import { SessionManager } from "./dist/core/session-manager.js";
import {
  AssistantMessageComponent, ToolExecutionComponent, UserMessageComponent, FooterComponent,
} from "./dist/modes/interactive/components/index.js";
```

## Inicialização obrigatória

- **`initTheme("default", false)` ANTES de qualquer componente** — senão `Error: Theme not initialized. Call initTheme() first.` (import de `./dist/modes/interactive/theme/theme.js`).
- **TUI é um `Container`** — usar `tui.addChild(root)` (NÃO existe `setRoot`), `tui.start()`/`tui.stop()` (NÃO existe `mount`/`unmount`).
- Limpar o chat: `chatContainer.clear()` (Container tem `clear()`) ou `children.splice(0, len)`.

## API dos componentes reais

- `SessionManager.open(path)` carrega o JSONL **read-only**; `session.buildSessionContext()` devolve `{ messages, model, thinkingLevel }`.
- Replicar o `renderSessionContext` do interactive-mode:
  - `assistant` → `new AssistantMessageComponent(message, hideThinking, markdownTheme)` + para cada `content.type === "toolCall"` → `new ToolExecutionComponent(name, id, args, {}, undefined, tui, cwd)`; guardar em mapa `pendingTools[content.id]`.
  - `toolResult` → `pendingTools.get(message.toolCallId).updateResult(message)`.
  - `user` → extrair texto (content pode ser string ou `{type:"text"}`), `new UserMessageComponent(text, theme)`, com `Spacer(1)` antes se já houver filhos.
- **FooterComponent** exige um `session` shim com: `state` (`{model: {provider, modelId, contextWindow} | null}`), `sessionManager` (o SessionManager real serve — ele tem `getEntries()`, `getCwd()`, `getSessionName()`), `getContextUsage()` (retornar `{percent: 0, contextWindow}`), `modelRegistry` (`{isUsingOAuth: () => false}`).
- **footerData** precisa de: `getGitBranch()`, `getExtensionStatuses()`, `getAvailableProviderCount()`, `onBranchChange(fn)`.

O footer renderiza sozinho: `↑<input> ↓<output> R<cacheRead> $<custo> <contexto>%/128k (auto)` — ex. real:
`/opt/data/code/workstation/cfp-ia • zera-onda3-lote2` / `↑100k ↓32k R5.6M $0.039 0.0%/128k (auto) no-model`

## Acesso do usuário (Windows/PowerShell → host Oracle → container)

- `docker exec -it` exige TTY real → o `ssh` precisa de **`-t`**:
  ```powershell
  ssh -t -i .\chave.key ubuntu@<host> "docker exec -it hermes_agent bash -lc 'cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent && node pi_follow_tui.mjs'"
  ```
  Sem `-t`: `cannot attach stdin to a TTY-enabled container because stdin is not a terminal`.
- Alternativa mais robusta (2 passos): `ssh` no host, depois `docker exec -it hermes_agent bash -lc '...'`.
- **`docker exec` sem `-u` roda como root** → `~` = `/root`; usar caminhos absolutos
  (`/opt/data/home/.pi/agent/sessions/...`) em scripts, nunca `~`.
- Container é `hermes_agent`; sessões em `/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-cfp-ia--/`.

## Polling

- Watcher a cada ~2s: `fs.statSync(path).size` mudou → re-render. Re-render limpa o chat e reconstrói
  tudo (componentes são baratos). Scroll segue o fim (a TUI do Pi não preserva posição de leitura —
  aceitável para acompanhar progresso).
- Sessão "parada" pode ser legítima: Pi rodando pytest/suíte longa não escreve no JSONL até o
  resultado fechar (pode ficar 2-4 min estável). Verificar com `wc -c` + última entrada, não matar.
