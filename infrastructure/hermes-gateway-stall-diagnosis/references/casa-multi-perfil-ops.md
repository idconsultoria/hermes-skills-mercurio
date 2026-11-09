# Casa multi-perfil: configurar, traduzir e reiniciar sem derrubar a casa

Escopo: um único processo de gateway serve N perfis (multiplex) além do home default. Mudança
de configuração nesse arranjo tem duas armadilhas próprias: o adapter cai quando o config muda, e
o teste feito com o ambiente errado dá veredito falso.

## 1 · Configurar por perfil

`hermes -p <perfil> config set <chave> <valor>` grava `profiles/<perfil>/config.yaml`; sem `-p`,
grava o `config.yaml` do home (perfil default). "Casa toda" = **default + cada perfil**, um comando
por home. Prefira o CLI a editar YAML à mão: ele valida o valor (ex.: `display.language` contra os
catálogos disponíveis e normaliza tag regional — `pt-BR` grava `pt`).

## 2 · Regra do restart único

Editar o config de um perfil **com o gateway no ar** dispara
`[MULTIPLEX] Re-scanned profile '<p>' after config/.env change (0 adapter(s) connected)` e o adapter
daquele perfil **não volta sozinho** (observado sem reconexão em ~10 min). Procedimento:

1. aplicar **todas** as mudanças de uma vez;
2. **um** restart do gateway (ou do supervisor, se o launcher também mudou);
3. conferir a volta por `logs/gateway.log`: `✓ <plataforma> connected (profile: <p>)` até N/N.

O boot é sequencial (~15–60 s por perfil; a primeira volta depois de um update pode passar de
10 min). Contar 0 conexões nos primeiros minutos é fila, não falha — só conclua queda se houver
traceback ou o processo tiver morrido.

## 3 · Sondar o runtime da instalação alvo sem falso positivo

Rodar o CLI/interpretador da instalação investigada com o ambiente da sessão importa os módulos da
instalação **de quem executa** (`ModuleNotFoundError` de dependência, ou `_locales_dir()` apontando
para a árvore errada) e produz veredito falso. Use ambiente mínimo:

- `PATH`, `HOME`, `TMPDIR` e `HERMES_HOME` do home alvo; **nunca** herde `PYTHONPATH`;
- `cwd` = `<installs>/<key>/environments/<hash>/workspace`;
- interpretador = `<geração>/venv/bin/python`; CLI = `<geração>/venv/bin/hermes`.

Sonda de idioma (mesma do processo vivo):

```python
from agent.i18n import get_language, _locales_dir, t
print(_locales_dir(), _locales_dir().is_dir())
print(get_language(), t('gateway.status.header'))
```

## 4 · `/proc` como evidência — e seus limites

- `/proc/<pid>/environ` é o ambiente **do exec**: `export` feito depois pelo script de supervisão
  não aparece nele para o supervisor, apenas nos filhos. Para provar que uma variável do supervisor
  chegou ao serviço, leia o environ do **gateway**, não o do supervisor.
- `readlink -f /proc/<pid>/exe` + `grep -c '<venv antigo>' /proc/<pid>/maps` provam interpretador e
  ABI reais; testar import no ambiente isolado **não** substitui essa leitura.
- Logo após um `kill`, o PID que aparece pode ser um processo efêmero do caminho de parada: confirme
  `readlink -f /proc/<pid>/exe` e o pai (`ps -o ppid=`) antes de anunciar regressão (ex.: "voltou
  para o Python antigo").

## 5 · Instalar um idioma na casa toda

1. **Paridade do catálogo primeiro** — `scripts/i18n-catalog-parity.py <locales-dir> <lang>`.
   Chave faltando = linha em inglês; placeholder divergente = `KeyError`/chave crua em produção.
2. `hermes -p <perfil> config set display.language <lang>` no default e em cada perfil.
3. Um restart (regra da seção 2).
4. Verificar a resolução **por home do perfil**, não só no default.

Precedência: `HERMES_LANGUAGE` (env) > `display.language` (config) > `en`. Home sem
`display.language` cai em inglês mesmo com catálogo presente — por isso a instalação é por perfil.
