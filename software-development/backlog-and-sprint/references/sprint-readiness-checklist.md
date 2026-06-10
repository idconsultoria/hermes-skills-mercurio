# Sprint Readiness Checklist

> Antes de iniciar a execução de uma Sprint (Brief → Planning → Design → Engineering), verificar o estado da branch para evitar retrabalho e surpresas.

## 1. Branch Baseline

- [ ] Branch existe no remoto: `git branch -a | grep NOME_DA_BRANCH`
- [ ] Branch foi criada a partir de `master` (não de uma branch de sprint anterior)
- [ ] Working directory limpo: `git status --short` — sem lixo de sprints passadas (prompts órfãos, `_staging/`, scripts avulsos)
- [ ] Commits da branch são apenas docs + infra: `git log --oneline master..HEAD`

## 2. Preview Pipeline

- [ ] `.github/workflows/preview.yml` existe
- [ ] Trigger é genérico: `pull_request: [opened, synchronize, reopened, closed]` — sem `branches: [master]`
- [ ] Container names usam `${PR_NUMBER}` (não nome fixo)
- [ ] DB isolation: `taskflow_pr_${PR_NUMBER}` ou similar
- [ ] URL dinâmica via sslip.io/NPM: `https://${PR_NUMBER}.dominio.sslip.io`
- [ ] Cleanup job existe (remove containers + DB + imagens ao fechar PR)
- [ ] GHCR_TOKEN (PAT clássico) e SSH_PRIVATE_KEY configurados como secrets

## 3. Sprint Docs Preservados

Verify docs from the previous sprint were correctly cherry-picked:

- [ ] `product/sprint_N/user-stories.md` — stories da sprint anterior (referência)
- [ ] `product/sprint_N/brief-notes.md` — decisões de design anteriores
- [ ] `product/sprint_N/design/` — wireframes, user-flows, prototype
- [ ] NENHUM código de engenharia da sprint anterior no working tree
- [ ] NENHUM `product/sprint_N/engineering/` preservado (é do ciclo passado)

## 4. Sprint Cycle Phase

Check which phase of the sprint execution cycle the branch is at. **For each phase, verify markers, not just file existence** — a sprint reattempt may have docs from a previous attempt that never completed the full phase.

| Fase | Arquivos esperados | Marcador de conclusão | ⚠️ Armadilha comum |
|------|--------------------|----------------------|-------------------|
| **2.2a — Brief** | `product/sprint_N/brief-notes.md` | Perguntas + respostas do usuário registradas | —
| **2.3 — Planning** | `product/sprint_N/user-stories.md` | `<!-- PHASE_COMPLETE: planning -->` ao final do arquivo | —
| **2.4 — Design** | `product/sprint_N/design/wireframes.md`, `user-flows.md`, `prototype.html` + **`product/sprint_N/feedbacks_sprint_N.md`** | `<!-- PHASE_COMPLETE: design -->` em wireframes.md **E** `ACORDO: AVANÇAR PARA ENGENHARIA` no feedbacks.md | ❌ **Design gerado pelo Pi mas SEM revisão agy é o erro mais comum.** O Pi pode marcar `PHASE_COMPLETE: design` sozinho. O verdadeiro gate é o `ACORDO` do agy. Se feedbacks.md não existe ou não tem ACORDO, a fase de design NÃO está completa — roda agy review primeiro. |
| **2.5 — Engineering** | `product/sprint_N/engineering/` com code-tasks, feedbacks | `## ACORDO: SPRINT N CONCLUIDA` no feedbacks.md | —
| **2.6 — Review** | Relatório enviado ao usuário | — | —
| **2.7 — Close** | PR criada e mergeada | — | —

### Diagnóstico rápido (reattempt)

Quando uma branch é uma reattempt de uma Sprint anterior:

```bash
# 1. Verificar se PHASE_COMPLETE existe (Pi gerou output?)
grep -rn "PHASE_COMPLETE" product/sprint_N/ 2>/dev/null

# 2. Verificar se ACORDO existe (agy aprovou?)
grep -rn "ACORDO\|APROVADO" product/sprint_N/ 2>/dev/null

# 3. O gap mais comum: PHASE_COMPLETE: design existe, mas ACORDO não.
#    Isso significa: Pi gerou designs, mas agy nunca revisou.
#    → A sprint NÃO avançou além do gate de design.
```

## 5. Cleanup: Lixo do Working Tree

Uncommitted artifacts from previous sprint executions that should NOT carry forward:

```
❌ _sprint*_staging/       — staging dirs de código gerado por Pi
❌ prompts/pi-sprint*.md  — prompts específicos da sprint anterior
❌ scripts/*.sh           — scripts específicos (se não forem genéricos)
❌ .github_backup/        — backup manual
```

If these exist, `git clean -nd` to preview, then `git clean -fd` to remove.

---

## Exemplo (reattempt: sprint1-v2 no taskflow)

```bash
# Verificar baseline — branch renamed de sprint1.5 para sprint1-v2
git branch -a | grep sprint1-v2
git diff --name-only master..sprint1-v2
git status --short  # deve estar limpo (só .hermes/ se houver)

# Verificar preview
cat .github/workflows/preview.yml | head -5
grep "branches:" .github/workflows/preview.yml || echo "✅ genérico"

# Verificar docs
ls product/sprint_1/user-stories.md product/sprint_1/brief-notes.md product/sprint_1/design/

# Verificar fase real (reattempt — docs existem mas agy review nunca foi feito)
grep "PHASE_COMPLETE" product/sprint_1/user-stories.md product/sprint_1/design/wireframes.md
grep "ACORDO" product/sprint_1/ 2>/dev/null || echo "❌ Sem ACORDO — agy nunca revisou os designs"
ls product/sprint_1/feedbacks_sprint_1.md 2>/dev/null || echo "❌ feedbacks_sprint_1.md não existe"

# Se ACORDO ausente: fase 2.4 incompleta — rodar agy review antes de engineering
```
