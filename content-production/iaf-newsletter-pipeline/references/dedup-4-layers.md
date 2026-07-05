# Dedup em 4 Camadas — Fundamentação

Este documento registra por que e como o dedup da IAF newsletter evoluiu para 4 camadas, incluindo falhas reais que motivaram cada camada.

## Camada 1 — Fato (sempre existiu)

Compara verbo central + entidade. Mesmo verbo sobre mesma entidade = duplicata.

**Falha real:** "OpenAI limitou GPT-5.6" e "GPT-5.6 restrito pelo governo" foram tratados como itens diferentes porque os títulos são diferentes. Mas o fato é o mesmo (governo restringiu acesso). Criada para evitar recontar o mesmo fato com ângulo diferente.

## Camada 2 — Entidade (adicionada em 15/06/2026)

Desenvolvimento novo sobre mesma entidade é válido. Diferencia "mesmo fato, ângulo diferente" (remove) de "entidade conhecida, fato novo" (mantém).

**Falha real:** "Anthropic protocola S-1" (IPO) e "Anthropic perde executivos para Google" (RH) são sobre a mesma entidade (Anthropic) mas fatos completamente diferentes. A versão inicial do dedup removia a segunda por "Anthropic já apareceu demais".

## Camada 3 — Tese Editorial (adicionada em 29/06/2026)

Antes de escrever o editorial, verifica se a TESE CENTRAL já foi usada em editoriais recentes. Não basta verificar entidades/fatos individuais — o GANCHO NARRATIVO do editorial pode se repetir mesmo com exemplos diferentes.

**Falha real (29/06/2026):**
- 26/06: editorial "governo virou gatekeeper"
- 27/06: editorial "governo é porteiro que decide quem usa modelos"  
- 29/06 (erro): editorial "portão trancou — acesso restrito"

Três edições com a MESMA TESE (governo americano controlando acesso a IA de fronteira), apenas com palavras diferentes. O leitor já absorveu o argumento. A newsletter ficou repetitiva.

## Camada 4 — Edições Especiais (adicionada em 29/06/2026)

Verifica se o tema central do editorial já foi coberto em uma edição especial dedicada.

**Falha real (29/06/2026):** GPT-5.6 Sol tinha edição especial (`especial-gpt56.html`) no archive. O editorial sobre GPT-5.6 reescreveu informação que já estava coberta. Agora: se existe especial, limite a 1 artigo no radar apontando para o link da especial.
