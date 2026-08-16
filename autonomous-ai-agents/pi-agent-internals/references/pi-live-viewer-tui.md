# Pi Live Viewer — reutilizando os componentes reais da TUI do Pi

> Técnica validada em 14/08/2026 (projeto Zera/CFP-IA). Objetivo: acompanhar uma sessão Pi
> **em andamento** (job em background) com a MESMA interface da TUI original — mensagens,
> tool calls e o footer de tokens/custo — sem corromper o JSONL (read-only).

## Por que não usar `pi --export` para live

- `pi --export <jsonl> <out.html>` gera um HTML **estático** fiel à TUI (1.2MB, tema real), útil como
  snapshot. Mas não mostra métricas ao vivo (tokens/custo) e recarregar a página perde o scroll.
- Injetar `<meta http-equiv="refresh">` recarrega a página inteira → perde posição de leitura.
- Script de polling JS (fetch + re-executar o bundle do export) funciona mas é frágil e ainda não
  mostra footer de tokens ao vivo.

## Caminho certo: instanciar os componentes reais num app Node próprio

O pacote Pi (v0.78.1) exporta os componentes da TUI como classes reutilizáveis. Você monta um
**espectador** que lê o JSONL com `SessionManager.open` (read-only) e renderiza com os componentes
oficiais. Script funcional: `templates/pi_follow_tui.mjs` (copiar para dentro da árvore do pacote).

### Imports (paths relativos — o `exports` do package.json BLOQUEIA subpaths)

```js
import { Container, TUI, ProcessTerminal, Spacer } from "./node_modules/@earendil-works/pi-tui/dist/index.js";
import { SessionManager } from "./dist/core/session-manager.js";
import { AssistantMessageComponent, ToolExecutionComponent,
         UserMessageComponent, FooterComponent } from "./dist/modes/interactive/components/index.js";
import { initTheme } from "./dist/modes/interactive/theme/theme.js";
```

- O script DEVE morar dentro da árvore do pacote (ex.: `/opt/data/pi-global/lib/node_modules/
  @earendil-works/pi-coding-agent/pi_follow_tui.mjs`) para o Node resolver os módulos.
- A lib `pi-tui` fica **aninhada** em `pi-coding-agent/node_modules/@earendil-works/pi-tui`
  (não em `/opt/data/pi-global/lib/node_modules/`).

### API (descoberta por debugging — difere da intuição)

| Item | Verdade |
|---|---|
| `TUI` | `new TUI(new ProcessTerminal(), false)` — é um `Container`. **NÃO tem** `setRoot`/`mount`/`unmount`. Use `tui.addChild(root)` + `tui.start()` / `tui.stop()`. |
| Tema | **OBRIGATÓRIO** chamar `initTheme("default", false)` antes de renderizar; sem isso os componentes lançam `Error: Theme not initialized. Call initTheme() first.` |
| `SessionManager.open(path)` | Carrega o JSONL read-only. `buildSessionContext()` devolve `{messages, model, thinkingLevel}`. `getEntries()` para o footer. |
| Tool calls | Estão **dentro** de `message.content` como `{type:"toolCall", name, id, arguments}` — não são entradas top-level. |
| `usage` por mensagem | Em `message.usage`: `{input, output, cacheRead, cacheWrite, totalTokens, cost:{total}}` — só em `role==="assistant"`. |
| `FooterComponent` | Espera `session.state`, `session.sessionManager` (com `getEntries/getCwd/getSessionName`), `session.getContextUsage()`, `session.modelRegistry.isUsingOAuth()`; e `footerData.getGitBranch()`, `footerData.getExtensionStatuses()`, `footerData.getAvailableProviderCount()`, `footerData.onBranchChange()`. SessionManager real cobre `sessionManager`; crie shims para o resto (ver template). |

### Footer (o que o usuário quer ver ao vivo)

A TUI mostra: `↑input ↓output RcacheRead WcacheWrite $cost %/contextWindow (auto)`.
O template soma `usage` de todas as entries assistant — igual ao `FooterComponent` original.

### Pitfalls

- **docker exec roda como root** → `~` = `/root`, não `/opt/data/home`. Use caminhos absolutos
  (`/opt/data/home/.pi/agent/sessions/...`) ou `-u hermes`.
- **`docker exec` sem `-it`** → `cannot attach stdin to a TTY-enabled container`; para um script
  read-only que só imprime, rode sem `-it` (`docker exec hermes_agent python3 script.py`).
- **TUI real precisa de `-it`** (alternate screen) — o espectador TUI sim, o viewer HTML não.
- **Windows PowerShell: `ssh -t` OBRIGATÓRIO antes de `docker exec -it`.** Sem o `-t` no ssh,
  o comando remoto roda sem PTY e o docker falha com `cannot attach stdin to a TTY-enabled
  container because stdin is not a terminal`. Comando que funciona:
  ```powershell
  ssh -t -i .\chave.key ubuntu@HOST "docker exec -it hermes_agent bash -lc 'cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent && node pi_follow_tui.mjs'"
  ```
  Alternativa robusta: entrar no host (`ssh`), depois `docker exec -it ...` dentro da sessão SSH
  interativa (o TTY existe). Para scripts read-only sem TUI, `docker exec` SEM `-it` funciona.
- **Container em rede própria** (`ai_mesh`, IP 172.19.0.x): túnel SSH `-L porta:172.19.0.6:porta`,
  não `localhost` (localhost do host não alcança o container).
- Sessão em andamento pode ter **pausas legítimas** (pytest rodando): o JSONL não cresce durante
  execução longa; o resultado só entra no fim. Não confundir com travamento — auditar com
  `pi-session-audit` (progress classification) antes de intervir.

## Rodar

```bash
cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent
node pi_follow_tui.mjs                 # segue a sessão mais recente
node pi_follow_tui.mjs /caminho/sessao.jsonl
```

Via SSH (do host, no container):
```bash
ssh ubuntu@HOST "docker exec -it hermes_agent bash -lc 'cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent && node pi_follow_tui.mjs'"
```
