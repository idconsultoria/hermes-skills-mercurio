# Agy Engineering Review — Sprint QA

> Pattern testado na Sprint 1 TaskFlow: agy revisa código, Pi best corrige, agy re-revisa e aprova.

## Fluxo Completo

```
1. agy review inicial → feedbacks.md (lista issues com severidade)
2. Pi best corrige (MiniMax M3, via --provider opencode-go --model minimax-m3)
3. agy re-review → verifica cada correção → APROVADO SEM RESSALVAS
4. Hermes add approval marker → commit
```

## Prompt de Re-review (após Pi best corrigir)

```bash
# Matar sessão anterior
ssh oracle-host 'tmux kill-session -t agy-eng 2>/dev/null; true'
ssh oracle-host "ps aux | grep '/bin/agy' | grep -v grep | awk '{print \$2}' | xargs -r kill 2>/dev/null; true"

# Iniciar
ssh oracle-host 'tmux new-session -d -s agy-eng -x 120 -y 40 \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8

# PARTE 1 — localização do feedback + instrução de não rodar testes
ssh oracle-host 'tmux send-keys -t agy-eng \
  "Re-review Sprint N engineering at /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/engineering/feedbacks.md. The N issues from the previous review have been fixed and committed (git log). Verify each fix was applied correctly. DO NOT run tests. Write confirmation in the same feedbacks.md file." Enter'
sleep 3

# PARTE 2 — lista de verificações específicas
ssh oracle-host 'tmux send-keys -t agy-eng \
  "Verify each fix: (1) [fix 1 description], (2) [fix 2 description], (3) [fix 3 description], etc. Read the actual files to confirm each fix." Enter'
sleep 3

# PARTE 3 — marcador de aprovação
ssh oracle-host 'tmux send-keys -t agy-eng \
  "If ALL N fixes are correctly applied and the previous concerns are resolved, append: ## APROVADO: SPRINT N CONCLUIDA SEM RESSALVAS. If any fix is incomplete, list which ones still need work." Enter'
```

## Permission Handling

agy pede confirmação para cada comando (`git show`, `git log`, etc.). **Sempre aprovar com option "3" (always allow)** para evitar múltiplos prompts:

```bash
ssh oracle-host 'tmux send-keys -t agy-eng "3" Enter'
```

Comandos comuns que agy tenta e podem ser aprovados permanentemente:
- `git log`, `git show`, `git diff` — seguros, aprovar option 3
- `ls`, `cat`, `find` — seguros, aprovar option 3
- `pytest`, `python -m pytest` — **NÃO rodar no host** (dependências no container). Se agy tentar, negar e re-enfatizar "DO NOT run tests"
- `sudo chown`, `sudo chmod` — aprovar se for corrigir permissões do feedback file

## agy NÃO consegue rodar testes no host

O pytest e dependências Python estão no container Docker, não no host. agy (Gemini 3.5 Flash) não tem acesso ao container. Se agy insistir em rodar testes:
1. Negar a permissão
2. Re-enfatizar "DO NOT run tests — review code only"
3. Rodar os testes manualmente via Hermes no container

## Marcadores de aprovação

| Fase | Marcador |
|------|----------|
| Design aprovado | `## ACORDO: AVANÇAR PARA ENGENHARIA` |
| Engineering aprovado | `## ACORDO: SPRINT N CONCLUIDA` |
| Re-review sem ressalvas | `## APROVADO: SPRINT N CONCLUIDA SEM RESSALVAS` |

Se agy não adicionar o marcador exato (escreve "Conclusion" ou outro texto), adicionar manualmente via host:
```bash
ssh oracle-host 'echo -e "\n## APROVADO: SPRINT N CONCLUIDA SEM RESSALVAS" >> /path/to/feedbacks.md'
```

## agy Engineering Review Checklist

O que agy DEVE verificar:
- [ ] Import paths resolvem corretamente (nenhum missing module)
- [ ] Service layer encapsulamento respeitado (nenhum ORM direto na route)
- [ ] EventBus/Webhooks wireados corretamente
- [ ] Testes existem para novas funcionalidades
- [ ] Schemas Pydantic atualizados com novos campos/enums
- [ ] Documentação sincronizada (api-contracts, ERD, tech-specs, SAD, test-plan)
- [ ] Docker/CI configurado para novos serviços
- [ ] Frontend chama backend real (não mock estático)
