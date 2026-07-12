# Padrão de Consolidação: Pesquisa Profunda Multi-Agente para Documentos de Estratégia

> Referência para o `pipeline-educacional`. Use este padrão quando o documento final exigir dados de mercado, benchmarks e referências externas em múltiplas dimensões.

## Quando usar

- Documentos de estratégia que cobrem 5+ dimensões (mercado, precificação, GTM, riscos, personas, etc.)
- Cada dimensão exige pesquisa externa com dados numéricos
- O documento final deve ter 30+ referências citáveis

## Estrutura de Lotes

Disparar subagentes em lotes de 3, por afinidade temática. Cada lote roda em paralelo. Lotes seguintes dependem do resultado dos anteriores para evitar duplicação.

### Lote 1 — Fundação (3 subagentes)
Cobre as dimensões centrais do documento: mercado, GTM, posicionamento.

### Lote 2 — Aprofundamento (3 subagentes)
Cobre o que o lote 1 revelou como gaps: operação, riscos, precificação detalhada.

### Lote 3 — Complementares (3 subagentes)
Cobre ângulos que só fazem sentido após os lotes 1 e 2: personas, parcerias, copywriting.

## Instruções para subagentes

Cada subagente deve receber:
- Contexto completo do projeto (nome, preços, público, formato)
- `role='leaf'` (sem re-delegação)
- Instrução explícita: "Incluir dados numéricos sempre que disponível. Responda em português."
- `goal` específico com 4–5 tópicos numerados

## Consolidação

1. Subagentes escrevem arquivos `.md` em `/opt/data/`
2. Copiar para `referencias/` do projeto
3. Expandir seções do documento mestre com `patch` cirúrgico (não rewrite)
4. Cada seção expandida referencia a fonte da pesquisa
5. Referências seguem formato ABNT-like com hyperlinks

## Anti-padrões

- ❌ 3 subagentes para 9 seções — cobertura insuficiente
- ❌ Reescrever o documento inteiro a cada lote — perde-se o histórico
- ❌ Subagentes sem instrução de idioma — contaminam o documento com inglês
