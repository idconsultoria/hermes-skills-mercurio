# Pi Live Viewer — variante BROWSER (pi_follow_web.py)

> Técnica validada 14/08/2026 (projeto Zera/CFP-IA). Complementa `pi-live-viewer-tui.md`:
> quando o usuário prefere acompanhar no **navegador** (não terminal), a variante web entrega
> a interface real do Pi (`pi --export` renderizado) com atualização ao vivo SEM recarregar a
> página. Script funcional: `/opt/data/scripts/pi_follow_web.py` (watcher + servidor HTTP).

## Pipeline

1. **Watcher**: a cada ~2s compara o tamanho do JSONL da sessão; se cresceu, re-exporta com
   `pi --export <jsonl> <out.html>` (o export usa os componentes REAIS da TUI → fidelidade total).
2. **Servidor**: `python3 -m http.server` servindo o HTML exportado (porta 8100 no container).
3. **Injeção**: substitui `<meta http-equiv="refresh">` por um **script de polling JS** que:
   - a cada 4s faz `fetch('pi-follow-live.html?t='+Date.now(), {cache:'no-store'})`
   - extrai o novo `session-data` (bloco `<script id="session-data">…</script>`)
   - se mudou, atualiza `el.textContent` e **re-executa o bundle do export** (clone do script
     `id="pi-export-script"` via `replaceWith`) → re-renderiza as mensagens
   - **preserva o scroll**: guarda `scrollTop` antes; restaura depois SE o usuário está no meio
     da leitura; só auto-scrolla (follow) se ele já estiver no fim (distância < ~80px do fundo)

## Por que meta-refresh é inaceitável

`<meta http-equiv="refresh" content="4">` recarrega a página INTEIRA a cada ciclo →
**zera a posição de leitura**. O usuário reclama imediatamente ("a página recarrega e eu perco
o progresso"). O polling com re-render preserva a leitura — comportamento esperado:
"se estou lendo no meio, não me arraste; se estou no fim, acompanha" (estilo terminal).

## SSH tunnel para container em rede própria

O servidor roda DENTRO do container (rede `ai_mesh`, ex.: IP `172.19.0.6`). O túnel deve
apontar para o **IP do container**, não `localhost` do host (nada escuta lá):

```powershell
# ERRADO:  ssh -L 8100:localhost:8100 ubuntu@HOST
# CERTO:
ssh -L 8100:172.19.0.6:8100 ubuntu@HOST
# → http://localhost:8100/pi-follow-live.html
```

Confirmar alcance do host→container antes: `curl http://172.19.0.6:8100/health`.

## Porta 3000 local ocupada (dev)

O `playwright.config.ts` já antecipa: quando a 3000 está ocupada (ex.: whatsapp-bridge da infra),
use `E2E_BASE_URL`/`PORT` alternativos (3100). Nunca mate o bridge.

## Pitfalls

- **Servidor antigo preso na porta**: `kill` do processo wrapper não libera o socket TCP.
  Verificar com `ss -tlnp | grep PORTA` + `fuser -k PORTA/tcp` antes de subir novo.
- **Polling "não mostra mensagens novas"**: quase sempre o JSONL parou de crescer por pausa
  LEGÍTIMA (pytest longo rodando — resultado só entra no fim). Não é bug do viewer: comparar
  tamanho do JSONL em dois instantes antes de mexer no script.
- **Cache do navegador**: página antiga (com meta-refresh) persiste no cache; `Ctrl+Shift+R`
  força reload. A versão com script live não tem `http-equiv="refresh"` (grep confirma).
- Esta variante NÃO mostra footer de tokens/custo ao vivo (o export é estático entre ciclos) —
  para métricas em tempo real use a TUI (`templates/pi_follow_tui.mjs`).
