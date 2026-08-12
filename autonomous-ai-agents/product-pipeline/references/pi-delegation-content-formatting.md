# Pi Cost Max + Delegação Conteúdo vs. Formatação (preferência do usuário)

Padrão validado em 2026-08-12 no projeto CFP IA (checklist pré-MVP). O usuário corrigiu o fluxo
quando o Hermes criou a tabela sozinho: **"apague tudo que você mesmo fez. Delegue a criação da
tabela original para o pi-cost-max"**.

## Esforço máximo no Pi

Combo para tarefas pesadas (CSV extensivo, especificações grandes, docs):

```bash
/opt/data/pi-global/bin/pi-cost-max -p "$(cat prompt.md)" --name "tarefa-x"
```

- Wrapper fixa: `--provider opencode-go --model deepseek-v4-flash --thinking xhigh`
- `--thinking` aceita `off|minimal|low|medium|high|xhigh` — `xhigh` = esforço máximo
- **NUNCA** usar Zen free (`opencode/deepseek-v4-flash-free`) para isso — lento/rate-limited;
  o usuário pede explicitamente o OpenCode Go
- Contexto 1M é padrão do deepseek-v4-flash via opencode-go (sem flag extra)
- Validar: `pi-cost-max --print "OK"` → esperado `OK` (1ª chamada ~2s)

## Fluxo de delegação (Pi gera CONTEÚDO → Hermes formata)

1. **Apagar o que o Hermes fez antes** — quando o usuário pedir "delegue ao pi-cost-max", a
   tabela original deve nascer do Pi. Remover abas/arquivos prévios (ex.: `deleteSheet` nas
   abas que o Hermes criou) antes de disparar.
2. **pi-cost-max gera o conteúdo do zero** — arquivo de dados (CSV) com TODA a especificação,
   **sem ver trabalho prévio**. O prompt deve dizer: "não leia scripts/checklists existentes;
   crie do zero" (evita viés de contaminação pelo trabalho do Hermes).
3. **Insumo antes de disparar**: coletar a **árvore de arquivos do Drive** (nomes + descrições +
   URLs, via `files?q=<folder> in parents` recursivo) e embutir no prompt — o Pi devolve links
   relevantes por linha (ex.: coluna `links_drive` com `|`-separados, máx. 4 links por tarefa).
4. **Depois que o Pi termina** (verificar CSV: cabeçalho, nº linhas, amostra), o Hermes sobe o
   arquivo e aplica formatação estado-da-arte (chips, dropdowns, semáforos, freeze, autofiltro,
   fórmulas) — ver `google-docs-formatting` → `references/sheets-rich-tab-formatting.md`.
5. **Não testar localmente quando o usuário pedir** — ele valida via hot reload/Android; Hermes
   só faz typecheck/sintaxe e entrega o comando.

## Prompt de delegação — estrutura que funcionou

O prompt do pi-cost-max deve conter:
- Contexto do projeto (resumo do que JÁ está implementado — para status fiéis)
- Colunas EXATAS do CSV (ordem + semântica de cada coluna)
- Lista de categorias obrigatórias
- Regras de status (o que marcar CONCLUIDO vs NAO_INICIADO)
- **Árvore do Drive embutida** entre marcadores `[INICIO_ARVORE]` ... `[FIM_ARVORE]`
- Restrições técnicas (separador `;`, UTF-8, aspas, mínimo de tarefas)
- Critérios de qualidade verificáveis + marcador final `PHASE_COMPLETE: <nome>`

Exemplo real: prompt de 16KB gerou CSV com 89 tarefas, 16 colunas, 11 categorias, links por
tarefa, sem contaminação pelo script anterior do Hermes.
