# Acompanhar sessão Pi AO VIVO com a TUI ORIGINAL (sem interferir)

O usuário quer ver a sessão do Pi progredindo **como se tivesse invocado a TUI ele mesmo** — tokens,
custo, tool calls, footer — SEM anexar ao processo (anexar = 2 escritores no mesmo JSONL = corrupção).
Construído e validado no Zera (14/08/2026). Três níveis de espectador, todos read-only:

## 1. Texto formatado — `pi_follow.py` (`/opt/data/scripts/pi_follow.py`)

Faz tail do JSONL e formata falas (ciano), tool calls (verde), resultados (dim), thinking (dim).
`--replay` mostra o histórico antes de seguir ao vivo. Não escreve no arquivo — seguro.

## 2. Browser com a interface do Pi — `pi_follow_web.py` (`/opt/data/scripts/pi_follow_web.py`)

- Watcher + HTTP server (porta 8100) que **re-exporta a sessão via `pi --export <session> <out.html>`**
  a cada mudança do JSONL (o export usa os componentes REAIS da TUI — tema `#8abeb7`, fidelidade total).
- Injeta um script de polling (`<meta refresh>` NÃO — zera a posição de leitura) que faz fetch do HTML
  novo, extrai o `session-data` atualizado e re-renderiza preservando o scroll (auto-follow só se o
  usuário já estiver no fim). Endpoint: `http://localhost:8100/pi-follow-live.html`.
- O `pi --export` da sintaxe é `pi --export <caminho_sessao> <saida.html>` (NÃO `--session` + `--export`).

## 3. TUI ORIGINAL — `pi_follow_tui.mjs` (a melhor experiência)

Copia para dentro da árvore do pacote e roda com node. Reusa os componentes reais do Pi:

```bash
cp /opt/data/scripts/pi_follow_tui.mjs /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent/
cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent && node pi_follow_tui.mjs
```

Usa: `TUI` + `Container` da lib `@earendil-works/pi-tui` (ANINHADA em
`pi-coding-agent/node_modules/@earendil-works/pi-tui` — não está no root), `SessionManager.open(path)`
(carrega o JSONL read-only), `AssistantMessageComponent`, `ToolExecutionComponent`,
`UserMessageComponent`, `FooterComponent` (footer real com ↑input ↓output R$custo %contexto).

### Pitfalls de implementação (todos vistos em produção)

1. **Imports: caminhos RELATIVOS ao dist, não nome de pacote.** O `exports` do package.json do
   `pi-coding-agent` bloqueia subpaths (`@earendil-works/pi-coding-agent/dist/...` → ERR). Importar
   direto: `./node_modules/@earendil-works/pi-tui/dist/...` e `./dist/modes/interactive/components/...`.
2. **`initTheme()` obrigatório antes de montar a TUI** (de `dist/modes/interactive/theme/theme.js`).
3. **API da TUI:** `tui.addChild(root)` (NÃO `setRoot`), `tui.start()`/`tui.stop()` (NÃO mount/unmount).
4. **FooterComponent precisa de `session.sessionManager`** + um shim `footerData` com
   `getGitBranch()`, `getExtensionStatuses()`, `getAvailableProviderCount()` (senão quebra o render).
5. **Sessão não precisa de estado vivo**: montar a partir do JSONL via `SessionManager.open` + polling
   do mtime para re-render a cada ~2s — o footer soma tokens/custo de TODA a sessão.

### Pitfalls de ambiente (docker/ssh/túnel)

- `docker exec` sem `-u` roda como **root** → `~` = `/root`, sessões não encontradas. Usar caminho
  absoluto `/opt/data/home/.pi/agent/sessions/...` nos scripts (ou `--user hermes`).
- `docker exec -it` via `ssh` SEM `-t` no ssh falha: *"cannot attach stdin to a TTY-enabled
  container because stdin is not a terminal"*. O `-it` do docker exige TTY — o ssh precisa de `-t`:
  `ssh -t user@host "docker exec -it hermes_agent bash -lc '...'"`. Alternativa robusta: entrar no
  host primeiro, depois `docker exec -it` (2 passos).
- **Túnel SSH para o browser:** o container está numa rede bridge (`ai_mesh`, IP 172.19.0.6) com
  portas NÃO publicadas. `-L 8100:localhost:8100` aponta pro HOST (nada escuta) → not found. Usar o
  IP do container: `-L 8100:172.19.0.6:8100` (verificar com `docker inspect <container>
  --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'`).
- Porta 3000 ocupada por outro serviço (ex.: WhatsApp bridge) → E2E/next start em porta alternativa
  (`E2E_BASE_URL`/`PORT`).

## Quando o JSONL "parou" — nem sempre é stall

O Pi escreve o JSONL por APPEND; durante um comando bash LONGO (pytest completo, build) ele NÃO
escreve até o tool result voltar. JSONL estável por 3-5 min durante "Now the full suite:" é espera
legítima, não stall. Verificar com `wc -c` duas vezes com intervalo + `ps aux` antes de concluir.
