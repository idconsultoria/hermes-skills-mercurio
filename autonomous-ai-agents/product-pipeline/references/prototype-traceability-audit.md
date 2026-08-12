# Auditoria de Rastreabilidade (Protótipo vs User Flows / User Stories)

Padrão comprovado no CFP IA (11/08/2026) para responder: *"os user flows e user
stories estão contemplados no protótipo?"* — com o Pi Cost como auditor e a
skill `pi-session-audit` para validar o trabalho.

## Quando usar

- Usuário pergunta se o protótipo de alta fidelidade (F4a) cobre as stories/flows
- Antes de iniciar a integração frontend↔API (F4d) — mapeia o que está pronto
- Para gerar o catálogo de "backend pronto para conectar" como insumo de priorização

## Fluxo

1. **Preparar prompt auto-contido** (`prompts/pi-auditoria-rastreabilidade.md`):
   - Lista ordenada de arquivos a ler (user-flows.md, user-stories.md, cada page.tsx,
     mock-data.ts, componentes, routers FastAPI, motor)
   - Regras: NÃO editar nada; "componente existe" ≠ "fluxo implementado"; componente
     pode existir sem callback ligado (onAcao/onContinuar nunca passados)
   - Estrutura de saída (6 seções): matriz US→protótipo, matriz fluxo→protótipo,
     gaps priorizados, componentes órfãos, notas de mock data, backend pronto p/ conectar
   - Marcador final `<!-- PHASE_COMPLETE: auditoria-rastreabilidade -->`

2. **Executar Pi Cost** (sessão nomeada, background, sem timeout):
   ```bash
   export PATH="/opt/data/pi-global/bin:$PATH"
   pi --name "projeto-auditoria-rastreabilidade" -p "$(cat prompts/pi-auditoria-rastreabilidade.md)" \
      --provider opencode-go --model deepseek-v4-flash
   ```

3. **Validar com pi-session-audit** (⚠️ Pi pode listar arquivos com `ls` e ainda
   escrever relatório substancial — o flag "só em ls" NÃO é prova de trabalho vazio;
   julgar pelo conteúdo do relatório, não pelo método de leitura):
   - Sessão em `~/.pi/agent/sessions/--<path>--/<timestamp>_*.jsonl`
   - Custo típico v4-flash: ~$0.02-0.05, 1-2M tokens com >90% cache hit
   - Conferir `PHASE_COMPLETE` + tamanho do relatório (>10KB = substancial)

4. **Entregar**: commitar relatório + prompt (política de versionamento do AGENTS.md),
   e resumir ao usuário em formato "como seria na reunião" (PM/Designer/Engenharia).

## O que o relatório de qualidade contém (CFP IA, 38KB, 291 linhas)

- **Matriz US→protótipo**: legenda SIM/PARCIAL/NÃO; evidência por linha de arquivo;
  diverge de contrato (ex.: formulário coleta campos que não existem no schema da API)
- **Matriz fluxo→protótipo**: passo a passo marcado `✗ NÃO IMPLEMENTADO`
- **Gaps priorizados**: severidade (crítico/alto/médio/baixo) + evidência + sugestão
- **Componentes órfãos**: grep de imports; o achado frequente é o INVERSO —
  componentes renderizados sem callback ligado
- **Notas de mock data**: onde o mock trava a fidelidade (dashboard fixo, chat lookup
  table, onboarding não dispara motor)
- **Backend pronto para conectar**: endpoints testados (92 testes) com
  método/rota → o que faz → tela que consumiria → dificuldade baixa/média/alta

## Veredito padrão

> "O protótipo conta a história como **storyboard**, não como sistema."

Visual/narrativo excelente, funcionalidade para de contar a história nos pontos de
diferenciação (diagnóstico não calculado, chat não conversa, sessão não recupera,
ações não agem). O backend já está pronto para virar a demo em sistema —
`GET /dashboard/summary` mapeia 1:1 com o mock (maior ganho por esforço).

## Pitfalls

- Pi Cost com v4-flash demora 3-6 min em tarefa grande; não matar por "parece parado"
- Prompt NÃO deve pedir código/refatoração — só auditoria (evita Pi "consertar" durante a análise)
- Diferenciar "spec desatualizado" (US-001 pede pontuação 0-100 mas PRD v2 evoluiu) —
  é decisão de produto do usuário, não gap de implementação
- Reportar os 3 próximos passos de integração mais valiosos (não todos)
