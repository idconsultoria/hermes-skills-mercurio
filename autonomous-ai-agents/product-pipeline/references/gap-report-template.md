# Gap Report — Template e Metodologia

> Template comprovado em VERO (83 gaps, 349 linhas). Usar após pull/rebrand
> ou quando o estado do código diverge do esperado.

## Quando gerar

- Após `git pull` que mostra redução drástica em arquivos (ex: 118KB → 1.3KB)
- Após rebrand ou refactor manual do usuário
- Quando há suspeita de que modais/formulários estão incompletos
- Entre F4b e F4d como validação de completude

## Metodologia (revisão dupla)

### Revisão A: Code Review (estrutural)
- Comparar cada modal, campo de formulário, tabela contra `referencia_completa_de_ui.md`
- Verificar regras de negócio do PRD no código (grep por nomes de função)
- Contar campos por modal: implementados / esperados
- Auditar arquitetura: monólito vs modular

### Revisão B: Dogfood QA (funcional)
- Simular usuário real em cada fluxo
- Abrir cada modal de criação e verificar campo por campo
- Testar cálculos (MIP, irrigação, LMR) com dados reais
- Verificar navegação entre módulos

## Formato do Relatório

```markdown
# Gap Report — [PROJETO] MVP → Produção

## Sumário Executivo
| Métrica | Valor |
|---------|-------|
| Total de gaps | N |
| 🔴 Críticos | N |
| 🟠 Altos | N |
| 🟡 Médios | N |
| 🟢 Baixos | N |

## Gaps por Módulo

### [Módulo]
| ID | Severidade | Descrição | Local (linha) | Correção necessária |
|----|-----------|-----------|---------------|---------------------|
| GAP-001 | 🔴 | Descrição precisa | L123 | Ação concreta |

## Regras de Negócio Não Implementadas
| RN | Status | Evidência |
|----|--------|-----------|

## Matriz de User Stories × Implementação
| US | Título | Status | Gaps relacionados |

## Recomendações
### Fase 1 — Fundação (~Xh)
### Fase 2 — Services (~Xh)
### Fase N — UX (~Xh)

## Conclusão
- N de M épicos implementados
- % de campos de formulário presentes
- Estimativa total: ~Xh
```

## Execução

O Pi best (deepseek-v4-pro) executa a revisão com prompt que instrui:
1. Ler PRD.md, referencia_completa_de_ui.md, user-stories.md
2. Ler o código fonte atual
3. Revisão dupla (code-review + dogfood QA)
4. Gerar gap-report.md com o formato acima

Tempo típico: 5-10 minutos para 80KB de código.

## Padrão de severidade

- 🔴 **Crítico**: bloqueia uso em produção, funcionalidade ausente ou quebrada
- 🟠 **Alto**: funcionalidade presente mas incompleta (>50% campos ausentes)
- 🟡 **Médio**: UX, validação, polimento
- 🟢 **Baixo**: cosmético, documentação, otimização
