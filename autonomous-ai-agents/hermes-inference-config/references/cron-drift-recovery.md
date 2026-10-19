# Cron drift recovery

Despining cures `HTTP 401` and `drift_skip` after model renames (verified on the
Ciclo de Consolidação and Alíquota ISS jobs).

Três sintomas pertencem a esta mesma classe — sempre confira o **snapshot**, não só o pin:
`HTTP 401 Model is not supported` (modelo não existe na rota resolvida), `[drift_skip]`
(falha-fechado do guard #44585) e `HTTP 410 Model has been deprecated` /
`HTTP 403 ... free tier` (snapshot despinado, porém morto).

## Symptoms observed

- `cronjob list` → `last_status: error`, `last_error: RuntimeError: HTTP 401: Model hy3-free is not supported`
  Output files in `$HERMES_HOME/cron/output/<job_id>/2026-09-01_02-01-07.md` contain `## Error` with the same 401.
- Earlier history same jobs showed `[drift_skip]` for unpinned jobs when `model.default` drifted
  (`deepseek-v4-flash` → `deepseek-v4-flash-vision-exp`, `opencode-free` → `opencode-go`).
  Output: `RuntimeError: [drift_skip] Skipped to prevent unintended spend ... model_snapshot differs`.
- `cronjob list` also showed `gateway_running: false` → `These jobs are saved but will NOT fire`.

## Diagnosis steps that worked

```bash
# 1. List jobs + last errors
hermes cron list
cat $HERMES_HOME/cron/jobs.json | python3 -c "import json; [print(j['id'], j['model'], j['provider'], j['last_error']) for j in json.load(open('jobs.json'))['jobs']]"

# 2. Inspect last cron output
ls -lt $HERMES_HOME/cron/output/8a7f5f65ed76/
grep -a "## Error" -A5 $HERMES_HOME/cron/output/8a7f5f65ed76/*.md | grep -E "RuntimeError|HTTP|drift"

# 3. Check current inference config (one key at a time)
hermes config get model
hermes config get providers
hermes config get fallback_providers
cat $HERMES_HOME/config.yaml | grep -A20 "model:\|fallback"
```

Config on 2026-09-01:

```yaml
model:
  default: muse-spark-1.2-contributor-free
  provider: opencode-free   # alias → opencode-zen @ https://opencode.ai/zen/v1
fallback_providers:
  - { model: muse-spark-1.2-contributor, provider: opencode-go, base_url: https://opencode.ai/zen/go/v1 }
  - { model: hy3, provider: opencode-go }
# hy3-free (opencode-free) no longer exists → pin to it gives 401
```

## Terceiro sintoma — snapshot despinado porém MORTO (`HTTP 410` / `403 free tier`)

Despinado não garante rota viva. Um job com `model: null` / `provider: null` que foi criado sob
uma resolução antiga continua com `provider_snapshot`/`model_snapshot` daquele momento, e **é o
snapshot que o agendador usa**. Quando o modelo do snapshot é descontinuado, o job não pula: ele
tenta rodar e morre no provider —
`last_error: RuntimeError: HTTP 410: Model <x> has been deprecated` — ou
`HTTP 403: ... OpenCode's free tier can only be used from within OpenCode`.

Discriminador rápido: `pinned: False` + snapshot ≠ `hermes config get model` = snapshot morto.

```
cronjob_manage(action='resnap', job_id='<id>')   # um job
cronjob_manage(action='resnap', all=true)        # todos os não-pinados
```

`resnap` adota a resolução global atual **sem pinar** (segue acompanhando trocas futuras). É a via
preferida; o truque `--model "" --provider ""` só recalcula quando a chamada muda eixo de fato.

## Fix — despin to follow global (user preference 2026-09-01)

User said "Despine e deixe usar o global" → "Sim, despine todos". Preference is
inheritance, not pinning, for all crons.

```bash
hermes cron edit 8a7f5f65ed76 --model "" --provider ""  # Ciclo Consolidação
hermes cron edit 3dfe43219f1b --model "" --provider ""  # Alíquota ISS
# Both now show model: None / provider: None → inherit model.default + fallback chain
# Verify:
hermes cron list
cat $HERMES_HOME/cron/jobs.json | python3 -c "import json; print([(j['id'], j['model'], j['provider']) for j in json.load(open('jobs.json'))['jobs']])"
```

- Unpinning recalculates `model_snapshot`/`provider_snapshot` → drift guard (#44585) clears.
- Gateway must be running: `hermes cron status` / `hermes gateway start`. Without it, unpinned jobs still won't tick.

## Re-executar depois do conserto

`cronjob_manage(action='run', job_id='<id>')` roda na hora, em **background**: o resultado volta
como mensagem nova, então não fique esperando nem perguntando. Passe um `prompt` transitório só
quando quiser contextualizar aquela execução (ex.: "reexecução manual: a falha anterior foi de
rota, não de dado — compare registrado × coletado agora").

Re-execute **apenas** os jobs que falharam por causa da rota morta:

- one-shot já `completed`/`enabled: false` → conserte o snapshot, **não** re-execute (o conteúdo é
  de uma data que passou);
- job que falhou por outra causa (script, módulo Python ausente, credencial, e-mail não
  encontrado) → o resnap não conserta; diagnostique à parte e reporte antes de reativar.

Confirme o conserto lendo `jobs.json` (`provider_snapshot`/`model_snapshot` iguais à resolução
atual), não pelo `cron list` — este segue exibindo o `last_error` histórico.

## Verificação pós-correção — o que prova e o que não prova

- `hermes cron list` / `hermes cron doctor` seguem exibindo o `last_error` **histórico**
  (`drift_skip`, 401) depois do conserto: é passado, não estado atual. A prova é o snapshot —
  `$HERMES_HOME/cron/jobs.json` → `model_snapshot`/`provider_snapshot` iguais ao `hermes config get model`
  atual (`cron_model_drift_axes(job, current_provider=..., current_model=...) == []`).
- Se o job já estava despinado e o snapshot continuar defasado, force mudança real de eixo:
  `hermes cron edit <id> --model <default-atual> --provider <provider-atual>` e depois
  `--model "" --provider ""` — é a segunda chamada que recalcula os snapshots.
- O guarda anuncia o skip **uma vez** e continua pulando em silêncio. Job cujo valor é alertar
  (monitor de resposta de e-mail, watcher) que falha fechado simplesmente nunca grita — reconfira
  o snapshot depois de pausar/retomar o job e de toda troca de modelo/provider.

## When to re-pin instead

Only if cron must stay on a specific model regardless of global (e.g., heavy reasoning needs `hy3` on `opencode-go`). Then:

```bash
hermes cron edit <id> --model hy3 --provider opencode-go
# successor of hy3-free; verify it exists in providers/fallback_providers first
```

## Auditoria de todas as rotas de cron

```bash
python3 -c "import json;d=json.load(open('$HERMES_HOME/cron/jobs.json'));jobs=d.get('jobs',d);[print(j['id'],'|',(j.get('name') or '')[:38],'| pinned:',bool(j.get('model') or j.get('provider')),'| snap:',j.get('provider_snapshot'),'/',j.get('model_snapshot'),'| enabled:',j.get('enabled'),'| last:',j.get('last_status')) for j in jobs]"
```

Leitura: `snap:` diferente de `opencode-go/<default atual>` = candidato a `resnap`. Jobs
`no_agent: true` (script-only) não passam por inferência — ignore-os.

## References in this repo

- This recovery pattern extends `hermes-inference-config` SKILL.md section "CRITICAL — cron jobs follow the chain only when UNPINNED" and "Diagnosing model errors from logs".
- For consolidation cycle recovery after partial failure, see `skills-repo-curator` pitfalls ("Ciclo pode morrer no meio e deixar working directory sujo").
