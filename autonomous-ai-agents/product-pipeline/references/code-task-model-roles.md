# Code-tasks: papéis por modelo + pitfalls de CI/Postgres

> Refinamento explícito do usuário (CFP IA/Zera, 14/08/2026). Substitui qualquer leitura
> simplista de "Pi cost sempre" ou "Pi best sempre" num ciclo de code-tasks.

## Papéis fixos por modelo num ciclo de code-tasks

| # | Papel | Modelo | Detalhes |
|---|-------|--------|----------|
| 1 | **Code-tasks (spec)** | **Pi best** (v4-pro, SEM `--thinking xhigh`) | Gera/atualiza `product/engineering/code-tasks.md` com gap analysis honesto contra o código real (o checklist da planilha pode estar desatualizado) |
| 2 | **Execução** | **Pi cost** (v4-flash) | Executa as code-tasks em lotes sequenciais (nunca paralelo) |
| 3 | **Revisão** | **agy** | Autoridade final; Turno 1 (feedbacks.md) e Turno 3 até `ACORDO: <ONDA> FINALIZADA` |
| 4 | **Correção** | **Pi best max** (v4-pro + `--thinking xhigh`) | Corrige issues do agy na MESMA sessão do executor (`pi --session <jsonl>`), nunca sessão nova |
| 5 | **Documentação** | **Pi cost max** (v4-flash + `--thinking xhigh`) | Atualiza SAD/ERD/api-contracts/test-plan/code-tasks + `## Histórico de atualizações` |

**Regras:**
- Verificar retomada: o JSONL cresce por APPEND (mesmo arquivo, tamanho aumenta).
- Cada onda = um ciclo completo (code-tasks → execução → agy → correção → ACORDO). Nunca avançar sem ACORDO.
- Pi/agy rodam SEM timeout (foreground sem flag ou background=true); monitorar por arquivos e pi-session-audit, não por stdout.
- Deploy para produção (não-staging) só com ok explícito do usuário.

## Política de decisão 🔴/🟢 (padrão do usuário, 14/08/2026)

- 🔴 **Parar e pedir aval** antes de implementar: tecnologia crítica não especificada, princípios de design/arquitetura, forma de implementação de funcionalidade crítica (auth, motor, LLM, LGPD), custo recorrente, deploy produção, mudança de escopo. Formato: 3–5 linhas, 2–3 opções + recomendação. Via `clarify`.
- 🟢 **Executar direto**: implementação dentro de decisão já tomada, correções mecânicas, QA/verificação, documentação técnica, infra staging/CI, atualização da planilha, commits.
- Regra de ouro: reversível com esforço pequeno → executa; afeta custo/usuário/contrato público → pergunta; dúvida genuína → pergunta.
- Documento canônico no repo: `product/management/politica-decisao.md` (projeto) — os prompts dos agentes devem carregá-la.

## Pitfalls de CI/Postgres em projetos Alembic+SQLite (aprendido em CFP IA/Zera)

1. **Boolean `server_default` no Postgres:** `server_default=text("0")` numa coluna Boolean falha no Postgres com
   `DatatypeMismatchError: column "arquivada" is of type boolean but default expression is of type integer`
   enquanto SQLite tolera (por isso passa local e quebra só no CI). Fix: usar `text("false")`/`text("true")`
   para Boolean — `"0"` só é válido em colunas Integer.
2. **Testes de migrations PG ficam obsoletos quando a cadeia cresce:** ao adicionar migrations novas, atualizar
   `tests/integration/test_migrations_pg.py::test_cadeia_revisoes_completa` (lista de revisions + head atual).
   É comum o Pi cost atualizar o teste SQLite (`tests/test_migrations.py`) e esquecer o de PG — o CI pega.
3. **Validar migrations com Postgres real:** testes locais com SQLite não exercitam o dialeto PG
   (JSONB, CHECK, boolean defaults). O CI (ou `ZERA_TEST_PG_DSN` + Postgres container) é quem descobre.
   Docker indisponível no container Hermes → documentar comando docker exato no README e deixar o teste
   pular limpo sem PG (skip), validando o corpo contra SQLite.

## Workflow de CI troubleshooting (GitHub Actions)

- `curl -H "Authorization: Bearer <token>" "https://api.github.com/repos/<user>/<repo>/actions/runs?per_page=N"`
  (token em `~/.config/gh/hosts.yml` → `github.com.oauth_token`).
- Por run: `/actions/runs/<id>/jobs` → achar step com `conclusion=failure`; depois
  `/actions/jobs/<job_id>/logs` → `grep -B2 -A25 "AssertionError|FAILED|Error"`.
- O passo "Lint (ruff)" e "Testes" são jobs separados — sempre checar QUAL job falhou antes de assumir lint.
