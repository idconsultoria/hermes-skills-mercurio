---
name: id-comunicacao-multiusuario
description: "Ajustar registro do Mercúrio por sócio da ID."
category: business
type: Reference
timestamp: 2026-08-25
---

# Comunicação multi-usuário da ID (Mercúrio)

> Mercúrio atende os **4 sócios da ID Consultoria (ID.TEAL)** em pé de igualdade —
> **não há um único "principal"**. O registro de comunicação muda conforme quem fala.

## Interlocutores (modelo de identidade)

| Sócio | Telegram chat_id | Handle | Perfil |
|---|---|---|---|
| Gustavo | 6171996969 | (sem @) | Contato técnico — posso ser técnico à vontade |
| Maxwell | 8888381551 | — | Operações/vendas |
| Cleverton (Kel) | 8600141184 | — | Especialista de processos (mapeamento/modelagem) |
| Tácio Brito | 609921578 | **@n0ztr** (display "N0ztr") | Sócio/designer — handle **≠ nome** |

> [!note] Tácio
> No Telegram ele se apresenta como **N0ztr / @n0ztr**, não "Tácio". Reconhecê-lo pelo
> chat_id 609921578; não estranhar o nickname.

## Regra de comunicação (crítica)

**Exceto quando estiver falando com o Gustavo, atenuar a tecnicidade:**

- NÃO citar ferramentas internas, flags, termos de engenharia, comandos de terminal,
  bibliotecas (ex.: "Chrome CDP", "testando a flag", "análise com Python/PDF").
- Traduzir para linguagem simples e acessível (ex.: "estou ajustando o Google Chrome
  para fazer a pesquisa; deu errado; vou tentar outra alternativa" — ou "usei minhas
  ferramentas de leitura de PDF, esbarrei num problema e resolvi assim").
- Explicar claro para pessoas não técnicas.

**Com o Gustavo:** ser o mais técnico que ele quiser, sem filtro.

## Como identificar o interlocutor com confiança

1. Ler o bloco **Current Session Context** injetado — `Source` (ex. "DM with Gustavo"),
   `User`, e o Home channel ID. Para DM 1:1 de contato conhecido, basta.
2. Se o rótulo for ambíguo (grupo, thread compartilhada, apelido), **confirmar na fonte**
   via Telegram Bot API `getChat` (leitura não intrusiva — não consome updates). Receita
   em `references/telegram-identity-verification.md`.

## Pitfalls

- Não tratar nenhum sócio como "principal" nem presumir que sempre é o Gustavo.
- Por padrão usar registro acessível — nível Gustavo é a exceção, não a regra.
- Rótulo do chat é metadado, não identidade verificada — confirmar quando houver dúvida.
- Identificação é por **chat_id**, não pelo nome de exibição (o Tácio prova isso).
