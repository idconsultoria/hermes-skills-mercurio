# Despacho de uma camada de code-tasks do Pi no host Oracle (padrão testado — Sprint 5 / Zera)

Padrão que funciona, repetido nas camadas L1→L5a (cada uma ~35–60 min, 300–400 testes passando no fim).

## 1. Runner no host (`product/sprint_5/run-pi-L<N>.sh`)

```bash
#!/usr/bin/env bash
set -u
cd /home/ubuntu/cfp-ia
export PATH="$HOME/.pi-global/bin:$PATH"
mkdir -p /home/ubuntu/zera-runs
LOG=/home/ubuntu/zera-runs/fase<N>-pi-cost-L<N>.log
echo "START $(date -u)" > "$LOG"
pi-cost --name "zera-sprint5-L<N>" -p "$(cat product/sprint_5/prompts/fase<N>-pi-cost-L<N>.md)" >> "$LOG" 2>&1
echo "EXIT:$?" >> "$LOG"
```

Disparo: `tmux new -d -s piL<N> "bash .../run-pi-L<N>.sh"`.

## 2. Pitfalls reais (custaram tempo)

- **`--dangerously-skip-permissions` é flag do agy, NÃO do pi.** Passar isso ao `pi-cost` mata o processo em 1 s com `Error: Unknown option` e `EXIT:1` no log. O padrão do pi é `--name <nome> -p "<prompt>"` e nada mais.
- **`Warning: Model "deepseek-flash" not found for provider "opencode-go". Using custom model id.`** aparece em toda execução e é inofensivo — o run segue normal.
- **Prompt lido por inteiro no início (`-p "$(cat arquivo)"`).** Arquivo criado ou corrigido *depois* do disparo não entra na execução → se a fonte de verdade mudou (ex.: o nome real do caminho de um doc), mate a sessão e relance com o prompt corrigido.
- **Caminho de fonte de verdade errado é fatal.** Conferir no host antes de disparar onde os arquivos realmente estão (ex.: material do especialista vivia em `docs/reuniao-2026-08-28/spec/`, não em `product/management/`).
- **Um lote por sessão tmux, serializado.** Dois lotes no mesmo repo ao mesmo tempo conflitam na working tree (o Pi não commita; o orquestrador commita).

## 3. Verificação independente (obrigatória antes de commitar)

O relatório do Pi é auto-relato. Rodar eu mesmo, no host:

```bash
cd /home/ubuntu/cfp-ia && .venv/bin/pytest -q | tail -3   # ~2–3 min para 390 testes
```

Checar também:
- `git status --porcelain` — só arquivos do escopo do lote;
- **nenhum** arquivo em `frontend/` ou `web/` (front é território exclusivo do agy);
- contagem de testes por arquivo novo vs. o contrato do lote;
- migrations: numeração livre (0009/0010/0011/0012 já consumidas) e cadeia `upgrade→downgrade→upgrade`.

Só depois: commits temáticos (código, testes, migration/espelhos, docs) e atualização da checklist viva.

## 4. Watcher assíncrono no Termux

Script local que faz polling de `tmux has-session -t piL<N>` a cada 30 s e, ao encerrar, imprime log + relatório + `git status`. Disparar como processo em background com notificação:

```bash
bash scripts/watch-piL<N>.sh    # background=true, notify=true
```

Sem isso o fim do lote não avisa ninguém — tmux no host não devolve callback.

## 5. Ordem que rendeu certo (L1→L5b)

1. prompt do lote escrito com: contrato da camada (code-tasks), baseline medido, alvo de testes, regras invioláveis (não commitar, não tocar front), formato do relatório;
2. disparo em tmux + watcher;
3. verificação própria (suíte + escopo);
4. commits temáticos;
5. checklist viva atualizada e commitada;
6. próximo lote.
