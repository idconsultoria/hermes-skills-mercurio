# MCP connection debug — args string vs lista YAML

Transcript real (2026-08-13). Síntoma: depois de `reload-mcp`, as tools `mcp_open_design_*` não apareciam; o server ficava **parked**.

## Cadeia de sintomas

1. `logs/errors.log`:
   ```
   WARNING tools.mcp_tool: MCP server 'open-design' failed initial connection after 3 attempts,
   parking until a reconnect is requested (state: connecting → parked): McpError: Connection closed
   ```
2. `logs/mcp-stderr.log` (stderr do processo MCP spawnado):
   ```
   Error: Cannot find module '/opt/data/['
       code: 'MODULE_NOT_FOUND'
   ```
   — o arquivo pode crescer até **GBs** com tentativas repetidas; truncar com `: > logs/mcp-stderr.log` (mantém inode, o gateway pode continuar escrevendo).

## Causa raiz

`args` do bloco MCP estava como **string JSON multi-line** no config.yaml:
```yaml
args: '["/opt/data/open-design-repo/apps/daemon/dist/cli.js", "mcp", "--daemon-url",
  "http://127.0.0.1:7456"]'
```
O MCP client recebe `args` como string; `args[0]` de uma string é o primeiro caractere (`[`), e o monta como module path → `os.path.join(cwd, '[')` = `/opt/data/[` → MODULE_NOT_FOUND → conexão fecha → 3 tentativas → parked.

## Correção

Converter para **lista YAML** (o tipo que o client espera):
```yaml
args:
  - /opt/data/open-design-repo/apps/daemon/dist/cli.js
  - mcp
  - --daemon-url
  - http://127.0.0.1:7456
```
Verificar o tipo parseado: `/opt/hermes/.venv/bin/python -c "import yaml; print(type(yaml.safe_load(open('/opt/data/config.yaml'))['mcp_servers']['open-design']['args']))"` → deve ser `<class 'list'>`.

## Pitfalls associados

- **`.npmrc` + `nvm.sh` corrompe stdout do MCP**: source do `nvm.sh` imprime `Your user's .npmrc file ... incompatible with nvm` no STDOUT. MCP stdio exige stdout 100% JSON — uma linha de texto quebra o protocolo. Sempre `command: <node absoluto>` no bloco MCP, nunca via nvm.sh.
- **Edição cirúrgica, não `yaml.safe_dump`**: `safe_dump` reescreve o config inteiro (perde comentários, muda indentação — arriscado). Editar por replace de string com backup.
- **`hermes mcp test <server>`** valida o config ATUAL sem precisar de reload: lista as tools se a conexão funciona. Se passar, o próximo reload carrega.
- **Restaurar backup errado**: backups com timestamp anterior à edição revertem os caminhos novos (ex.: volta `/opt/data/...` → `/tmp/...`). Conferir o diff após restaurar.
- Exit code 11 do node em pipelines `| head` é ruído (SIGPIPE), não falha real — checar health, não exit code.
