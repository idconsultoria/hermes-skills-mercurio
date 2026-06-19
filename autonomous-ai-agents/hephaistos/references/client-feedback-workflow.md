# Client Feedback → Code Plan Workflow

> Como processar um documento de feedback de cliente, mapear para o código e gerar um plano de ação priorizado. Usado no Desconsultor V2.6 (2026-06-16).

## Fases

### 1. Extrair Feedback

**Fontes comuns:**
- `.doc` (Word antigo) → `antiword arquivo.doc`
- `.docx` → `pandoc arquivo.docx -t plain` ou `python3 -m docx2txt`
- `.pdf` → `pdftotext -f N -l N arquivo.pdf -` (páginas específicas)
- WhatsApp export → parse de timestamps e remetentes

**Fallback quando busca web falha:**
Se Firecrawl/Google/DuckDuckGo estiverem todos offline, usar dados internos do projeto:
- `layout.tsx` → metadata (autor, descrição, keywords, OG)
- `README.md` → visão geral, stack, dados da pesquisa
- PDF do TCC no projeto → `pdftotext` páginas específicas
- `package.json` → dependências e scripts

### 2. Mapear Feedback → Código

Para cada ponto do feedback:
1. Identificar componente/arquivo afetado
2. Classificar severidade (P0/P1/P2/P3)
3. Agrupar por arquivo para minimizar idas e vindas

**Classificação de severidade:**
| Nível | Critério |
|-------|----------|
| P0 🔴 | Dado errado (texto alterado, informação incorreta), funcionalidade quebrada |
| P1 ⚠️ | UI quebrada (legenda, alinhamento), inconsistência visual |
| P2 🟡 | Melhoria de copy, dados adicionais |
| P3 🔵 | Nice-to-have, otimizações |

### 3. Gerar Plano em Blocos

Estrutura:
```
## 📋 Plano de Ação

### 🔴 FASE 1: [Nome] — Blocos A, B, C
| # | O quê | Arquivo | Severidade |

### 🟡 FASE 2: [Nome] — Bloco D
| Categoria | Escopo | Método |
```

**Regras:**
- Máximo 2 fases por plano (evitar over-planning)
- Cada bloco com 3-5 itens
- Sempre listar arquivo exato + severidade
- Fase 2 só inicia após Fase 1 aprovada

### 4. Perguntas Bloqueantes

Antes de iniciar implementação, identificar o que **depende do cliente**:
- Fonte original de dados alterados pela IA
- Aprovação de direção visual
- Assets faltantes (fotos, logos)

Fazer a pergunta explicitamente, não presumir.

## Anti-Patterns

- ❌ Implementar antes de mapear todos os pontos
- ❌ Misturar correções de feedback com novas features na mesma fase
- ❌ Assumir que "a IA ajustou o texto" é aceitável — sempre pedir a fonte original
- ❌ Pular a pergunta bloqueante e depois ter que refazer
- ❌ Usar emojis (✦ ⚠ 🌿 🧠) em vez de ícones Lucide — o usuário rejeita
- ❌ Fazer design visual direto (layout de seção, escolha de ícone, posicionamento) em vez de delegar ao agy

## Lessons Learned (Desconsultor V2.6, 2026-06-16)

1. **Emojis são proibidos.** Mesmo em badges decorativos ou glyphs de arquétipos. Substituir por Lucide icons (`Star`, `AlertTriangle`, `Leaf`, `Brain`, `Sparkles`, etc.). Se não existir equivalente exato, usar o mais próximo.
2. **Design visual = agy, SEMPRE.** A seção "Quem sou eu" (foto, bio, links, layout do card) deveria ter sido delegada ao agy. O Hermes fazer isso diretamente viola a regra #3 do Hephaistos e o usuário corrigiu.
3. **PDFs locais são fonte primária quando busca web falha.** Extrair com `pdftotext` páginas específicas e mapear dados para gráficos.
