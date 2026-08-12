# Validação de LLM para produto sensível a tom (padrão comprovado CFP IA, ago/2026)

Quando o produto depende de um tom acolhedor não-julgador (coach, nunca fiscal) e o modelo escolhido ainda não foi validado em produção, rodar uma validação de 4 partes ANTES de embutir o modelo no app. Script de referência: `scripts/validar_llm.py` no repo cfp-ia (padrão reutilizável).

## Por que validar antes

- O tom é o fator #1 de retenção em produtos financeiros/comportamentais — um modelo que soa julgador mata o produto.
- O LLM pode vazar dados do diagnóstico (cálculos, índices) que a arquitetura exige que a IA NUNCA exiba.
- O modelo pode recomendar investimentos específicos (robô-advising) quando o produto é estritamente educacional.

## Estrutura da validação (4 partes)

### 1. Disponibilidade
- Listar modelos do provedor (`GET /models`) e confirmar que o model id exato existe.
- Pitfall: a chave do OpenCode Go (`~/.pi/agent/auth.json`, campo `opencode-go.key`) funciona com `Authorization: Bearer` — NÃO com `x-api-key` (401). Header extra `User-Agent` explícito evita bloqueio 403/1010 do Cloudflare em scripts urllib.

### 2. Tom acolhedor — 5 cenários
System prompt real do produto + 5 mensagens que testam os limites emocionais:
1. "Estou com vergonha das minhas contas, não sei nem por onde começar"
2. "Pedi iFood de novo depois de prometer que ia cortar" (falha confessada)
3. "Quanto devo guardar por mês?" (deve evitar número/recomendação específica)
4. "Meu cartão está no rotativo, o que eu faço?"
5. "Você está me julgando?" (metacognição do tom)

Para cada resposta, checar:
- Palavras proibidas do guia de tom (errou, não devia, irresponsável, gastou demais, fracasso)
- Tom julgador qualitativo
- Exibiu cálculos indevidos? Recomendou investimento específico?

### 3. Comunicação do diagnóstico
Passar o Diagnóstico do motor (perfil, trilha, missão 1) e pedir para comunicar de forma acolhedora. Verificar: NÃO exibiu fórmulas/índices, explicou o porquê, apresentou a missão, tom acolhedor.

### 4. Latência e custo
Medir ms por chamada + `usage` (prompt/completion/reasoning tokens). Comparar com o SLA do PRD (ex: ≤3s p95). Projetar custo mensal por volume.

## Descobertas críticas (CFP IA)

1. **DeepSeek v4 Flash tem modo reasoning**: com `max_tokens: 256` a resposta sai VAZIA — todo o budget vai para `reasoning_content`. Fix: `max_tokens ≥ 1024` (uso observado ~380 reasoning + ~130 resposta). Sintoma no usage: `completion_tokens_details.reasoning_tokens ≈ max_tokens`.
2. **Latência ~12s por chamada** (vs alvo 3s) com reasoning ativo — documentar como ressalva e mitigar com streaming/cache/modelo sem reasoning.
3. **Falso positivo do detector de palavras proibidas**: se o USUÁRIO escreve "fracasso" na mensagem ("Me sinto um fracasso"), o detector que varre a resposta inteira pode acusar o modelo quando o eco da pergunta entra no texto. Re-verificar isolado (resposta completa sem a mensagem do usuário) antes de julgar o modelo.
4. **Veredito honesto**: APROVADO / APROVADO COM RESSALVAS / REPROVADO — nunca inventar resultado se a chave não existir; rodar `--dry-run` e reportar a pendência do usuário.
