#!/usr/bin/env node
/**
 * pi_follow_tui.mjs — Espectador da sessão Pi ao vivo usando a TUI ORIGINAL do Pi Agent.
 *
 * Reutiliza os componentes reais do Pi (não um clone):
 *   - TUI + Container + Spacer da lib @earendil-works/pi-tui
 *   - AssistantMessageComponent, ToolExecutionComponent, UserMessageComponent, FooterComponent
 *   - SessionManager.open() para carregar o JSONL (read-only — seguro com job em background)
 *
 * Mostra ao vivo: mensagens, tool calls, raciocínio (thinking) e o footer de tokens/custo
 * (↑input ↓output Rcache $custo %contexto), atualizando a cada 2s quando o JSONL cresce.
 *
 * USO (IMPORTANTE — deve rodar DENTRO do package tree do pi p/ os imports resolverem):
 *   cp pi_follow_tui.mjs /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent/
 *   cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent
 *   node pi_follow_tui.mjs                       # segue a sessão mais recente
 *   node pi_follow_tui.mjs /caminho/sessao.jsonl # segue sessão específica
 * Ctrl+C para sair.
 *
 * Do Windows PowerShell via SSH (o -t no ssh é OBRIGATÓRIO):
 *   ssh -t -i <key> ubuntu@<host> "docker exec -it hermes_agent bash -lc 'cd /opt/data/pi-global/lib/node_modules/@earendil-works/pi-coding-agent && node pi_follow_tui.mjs'"
 */
import { Container, TUI, ProcessTerminal, Spacer } from "./node_modules/@earendil-works/pi-tui/dist/index.js";
import { SessionManager } from "./dist/core/session-manager.js";
import {
  AssistantMessageComponent,
  ToolExecutionComponent,
  UserMessageComponent,
  FooterComponent,
} from "./dist/modes/interactive/components/index.js";
import { initTheme } from "./dist/modes/interactive/theme/theme.js";
import fs from "node:fs";
import path from "node:path";

const SESSIONS_DIR = "/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-cfp-ia--/";
const POLL_MS = 2000;

function newestSession() {
  const files = fs
    .readdirSync(SESSIONS_DIR)
    .filter((f) => f.endsWith(".jsonl"))
    .map((f) => path.join(SESSIONS_DIR, f))
    .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  return files[0] || null;
}

// ---------- shim do footerData (o que FooterComponent espera) ----------
class SimpleFooterData {
  constructor() {
    this.branch = "";
    this.availableProviderCount = 1;
    this._listeners = new Set();
  }
  getGitBranch() { return this.branch; }
  onBranchChange(fn) { this._listeners.add(fn); return () => this._listeners.delete(fn); }
  getAvailableProviderCount() { return this.availableProviderCount; }
  setAvailableProviderCount(n) { this.availableProviderCount = n; }
  getExtensionStatuses() { return []; }
}

// SessionManager pode não expor getSessionName/getCwd — stubs seguros
if (!SessionManager.prototype.getSessionName) {
  SessionManager.prototype.getSessionName = function () { return null; };
}
if (!SessionManager.prototype.getCwd) {
  SessionManager.prototype.getCwd = function () { return this.cwd; };
}

// ---------- TUI (API real: addChild + start, NÃO setRoot/mount) ----------
initTheme("default", false); // OBRIGATÓRIO antes de render (senão "Theme not initialized")
const tui = new TUI(new ProcessTerminal(), false);
const root = new Container({ direction: "column" });
const chatContainer = new Container({ direction: "column", scrollable: true, flexGrow: 1 });
const footerContainer = new Container({ direction: "row" });
root.addChild(chatContainer);
root.addChild(footerContainer);
tui.addChild(root);
tui.start();

let footer = null;
let lastSize = -1;

function extractUserText(message) {
  const parts = [];
  for (const c of message.content || []) {
    if (typeof c === "string") parts.push(c);
    else if (c.type === "text") parts.push(c.text);
  }
  return parts.join("").trim();
}

// ---------- render (espelha renderSessionContext do interactive-mode) ----------
function renderSession(sessionPath) {
  try {
    const session = SessionManager.open(sessionPath, undefined, "/opt/data/code/workstation/cfp-ia");
    const context = session.buildSessionContext();
    chatContainer.children.splice(0, chatContainer.children.length);

    const pendingTools = new Map();
    for (const message of context.messages) {
      if (message.role === "assistant") {
        chatContainer.addChild(new AssistantMessageComponent(message, false, undefined));
        for (const content of message.content || []) {
          if (content.type === "toolCall") {
            const tc = new ToolExecutionComponent(content.name, content.id, content.arguments, {}, undefined, tui, session.cwd);
            chatContainer.addChild(tc);
            pendingTools.set(content.id, tc);
          }
        }
      } else if (message.role === "toolResult") {
        const comp = pendingTools.get(message.toolCallId);
        if (comp) { comp.updateResult(message); pendingTools.delete(message.toolCallId); }
      } else if (message.role === "user") {
        const text = extractUserText(message);
        if (text) {
          if (chatContainer.children.length > 0) chatContainer.addChild(new Spacer(1));
          chatContainer.addChild(new UserMessageComponent(text, undefined));
        }
      }
    }

    // Footer — componente REAL: espera session.state, session.sessionManager,
    // session.getContextUsage() e session.modelRegistry
    let modelState = { contextWindow: 0 };
    for (const e of session.getEntries()) {
      if (e.type === "model_change") {
        modelState = { provider: e.provider, modelId: e.modelId, contextWindow: e.contextWindow || 128000 };
      }
    }
    const footerSession = {
      state: { model: modelState.provider ? modelState : null },
      sessionManager: session,
      getContextUsage: () => ({ percent: 0, contextWindow: modelState.contextWindow }),
      modelRegistry: { isUsingOAuth: () => false },
    };
    if (footer) footerContainer.removeChild(footer);
    footer = new FooterComponent(footerSession, new SimpleFooterData());
    footerContainer.addChild(footer);
    tui.requestRender();
  } catch (err) {
    // sessão pode estar sendo escrita no meio — tenta de novo no próximo tick
  }
}

// ---------- watcher (só leitura; não escreve no JSONL) ----------
function tick() {
  const sessionPath = process.argv[2] || newestSession();
  if (!sessionPath) return;
  try {
    const size = fs.statSync(sessionPath).size;
    if (size !== lastSize) { renderSession(sessionPath); lastSize = size; }
  } catch { /* arquivo sendo escrito/rotacionado */ }
}

const sessionPath = process.argv[2] || newestSession();
if (!sessionPath) { console.error("Nenhuma sessão encontrada em", SESSIONS_DIR); process.exit(1); }
console.error(`▶ seguindo: ${path.basename(sessionPath)} (Ctrl+C para sair)`);
renderSession(sessionPath);
setInterval(tick, POLL_MS);

process.on("SIGINT", () => { tui.stop?.(); process.exit(0); });
