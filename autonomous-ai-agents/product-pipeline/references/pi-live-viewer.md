# Pi Live Viewer — assistir a sessão Pi progredindo em tempo real

> Padrão validado no Zera (ago/2026): o usuário queria ver a sessão Pi (ex.: `zera-onda3-lote1`)
> progredindo "como se tivesse invocado ele mesmo", sem esperar o Hermes reportar.

## Por que não usar a TUI interativa do Pi para isso

`pi --session <jsonl>` (sem `-p`) abre a TUI com a sessão carregada — mas a TUI **não segue ao vivo**:
mostra um snapshot no momento em que abre. Pior: se o job Pi já está rodando em background escrevendo no
MESMO JSONL, abrir a TUI cria **dois escritores** no arquivo → risco real de corromper a sessão
(entradas intercaladas fora de ordem). Regra: nunca abrir a TUI sobre um JSONL que outro processo está
appendando.

## Solução: reutilizar o exportador HTML do próprio Pi

O Pi tem `pi --export <jsonl> <out.html>` que renderiza a sessão com **a interface real do Pi**
(mesmos componentes: assistant message, tool execution, bash execution, diff, thinking; tema `#8abeb7`).
Não reimplementar a TUI — o export já é fiel.

Fluxo (scripts em `/opt/data/scripts/`):

1. **`pi_follow.py`** — modo espectador no terminal (cores): faz `tail -f` do JSONL e formata cada
   evento (fala do Pi em ciano, tool calls em verde, resultados truncados, thinking em dim).
   `--replay` mostra o histórico existente antes de seguir. Só lê o arquivo — seguro.
2. **`pi_follow_web.py [porta]`** — watcher + servidor HTTP: a cada 2s vê se o JSONL cresceu, roda
   `pi --export` de novo, e serve o HTML com **script de polling** injetado.

```bash
# no container (serve na 8100)
python3 /opt/data/scripts/pi_follow_web.py 8100
```

## Por que polling com re-render (e não meta-refresh)

O `<meta http-equiv="refresh">` recarrega a página inteira → **zera o scroll** (usuário perde o
progresso de leitura). A correção (validada): injetar JS que a cada 4s faz `fetch('...html?t='+Date.now())`,
extrai o novo `session-data` (base64 JSON), e **re-executa o script do export** (marcado com
`id="pi-export-script"`, recriado via `replaceWith` clone) — re-renderiza só o conteúdo, preservando
`scrollTop`. Auto-follow (rola até o fim) SÓ se o usuário já estiver no fim; se está lendo no meio,
mantém a posição.

Detalhe de implementação do export:
- O HTML tem `<script id="session-data" type="application/json">BASE64</script>` e um bundle inline que
  decodifica e renderiza em `#messages`/`#content` (scroll container). O watcher marca o bundle com id
  e injeta o script live antes de `</body>`.
- Headers `Cache-Control: no-store` no servidor + `?t=Date.now()` no fetch para nunca servir cache.

## Pitfalls (todos encontrados na prática)

| Situação | Correção |
|---|---|
| `docker exec` sem `-u` roda como **root** → `~` = `/root` | Usar caminho absoluto `/opt/data/home/.pi/agent/sessions/...` no script (não `expanduser`) |
| `docker exec -it` falha do PowerShell: "cannot attach stdin to a TTY-enabled container" | **Tirar o `-it`** — o viewer não precisa de stdin, só lê e imprime |
| Túnel `-L 8100:localhost:8100` dá "not found" | O servidor roda DENTRO do container (rede `ai_mesh`, IP ex.: `172.19.0.6`, porta NÃO publicada). Túnel correto: `ssh -L 8100:172.19.0.6:8100 ubuntu@host` |
| Browser mostra versão antiga (sem script live) | Hard refresh `Ctrl+Shift+R` uma vez após trocar a implementação (cache do browser) |
| "Mensagens novas não chegam" | Checar se o JSONL cresceu (`wc -c`; o watcher loga `export ok (N bytes)`). Pi parado por minutos durante pytest longo NÃO é travamento — não escreve no JSONL até o teste terminar |
| Porta 8100 ocupada após matar o processo | `fuser -k 8100/tcp` ou matar o PID; `ss -tlnp` para conferir; subir em outra porta (`pi_follow_web.py 8101`) |
| Script `pi_follow.py --replay` como caminho | Filtrar flags antes de pegar o path (`args = [a for a in sys.argv[1:] if not a.startswith('--')]`) |

## Verificação (dogfood do viewer)

Para provar que o polling funciona (sem depender do usuário):
1. Anotar `document.getElementById('session-data').textContent.length` no `browser_console`.
2. Esperar o JSONL crescer (verificar `wc -c` no terminal).
3. Re-checar no browser: o length e a última mensagem (`#messages > *:last`) devem mudar sozinhos.
4. Se `changed: false` persistir com JSONL crescendo, o script live não foi injetado (hard refresh) ou
   o export não está sendo regenerado (log do watcher).
