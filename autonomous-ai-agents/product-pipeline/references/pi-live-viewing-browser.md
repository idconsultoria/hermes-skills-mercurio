# Pi live-viewing no browser com a interface REAL do Pi (pi_follow_web)

> Validado em 08/2026 (Zera). O usuário quis acompanhar uma sessão Pi rodando em background "como se
> tivesse invocado ele mesmo" — sem corromper o JSONL e sem reimplementar a TUI.

## Ideia central

O Pi tem um exportador embutido que renderiza a sessão com a **interface original da TUI** (mesmos
componentes e tema) em HTML:

```bash
pi --export <session.jsonl> <saida.html>
```

(NOTA: a sintaxe é `pi --export <arquivo> [saida]` — NÃO funciona `pi --session X --export Y`, dá
"File not found".)

Combinando com um watcher + servidor HTTP, dá para ter a TUI do Pi ao vivo no browser:

1. Watcher verifica a cada ~2s se o JSONL cresceu (`wc -c` / `os.path.getsize`).
2. Quando cresceu, re-roda `pi --export` para o HTML.
3. Servidor HTTP (Python `http.server`) serve o HTML.
4. **Não usar `<meta refresh>`** — recarrega a página inteira e o usuário perde a posição de leitura
   (reclamação real). Em vez disso, injetar script de polling que:

   - faz `fetch('pi-follow-live.html?t=' + Date.now(), {cache:'no-store'})`
   - extrai o novo `session-data` (o export guarda o JSON da sessão em `<script id="session-data">`)
   - substitui o `session-data` e **re-executa o script do export** (marcado com `id="pi-export-script"`)
     para re-renderizar só as mensagens
   - **preserva o scroll** (`#content` é o container): se o usuário estava no meio da leitura, mantém
     `scrollTop`; só faz auto-follow (rola pro fim) se já estava no fundo (`scrollHeight - scrollTop
     - clientHeight < 80`).

## Estrutura do HTML export (p/ o script de polling)

- `#session-data` — `<script type="application/json">` com base64 do JSON da sessão
- `#messages` — container onde o JS do export renderiza as mensagens
- `#content` — container com `overflow-y: auto` (é onde o scroll mora)
- O bundle JS do export é o maior `<script>` inline sem `src` — marcar com `id` para re-executar

## Acesso via SSH (PowerShell) — pitfalls

- **`docker exec -it` falha** do PowerShell/SSH: "cannot attach stdin to a TTY-enabled container".
  Usar `docker exec` SEM `-it` (scripts read-only não precisam de TTY).
- **`docker exec` sem `-u` roda como root → `~` = /root**. Scripts que acessam sessões Pi precisam de
  caminho absoluto (`/opt/data/home/.pi/...`) ou `-u hermes`.
- **Túnel SSH para o container**: o container `hermes_agent` está na rede `ai_mesh` com IP
  `172.19.0.6`. `ssh -L 8100:localhost:8100` aponta pro HOST (onde nada escuta) → not found.
  Correto: `ssh -i chave -L 8100:172.19.0.6:8100 ubuntu@<host>` e abrir `http://localhost:8100/pi-follow-live.html`.

## Script de referência

`scripts/pi_follow_web.py` (não commitado como script aqui — versão funcional mantida em
`/opt/data/scripts/pi_follow_web.py`): watcher + servidor + injeção do script live com polling e
scroll preservation. Para acompanhar no terminal (sem browser), usar `scripts/pi_follow.py`.

## Alternativa descartada (por que)

Abrir a TUI interativa de verdade (`pi --session <arquivo>` sem `-p`) carrega o histórico mas o arquivo
passa a ter **dois escritores** (você + o job em background) → risco de corromper o JSONL. O modo
espectador (read-only) é seguro. Se o usuário quiser assumir a sessão, matar o job background primeiro.
