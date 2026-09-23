---
name: formalizacao-acordo-cliente
description: "Use ao formalizar por escrito acordo fechado com cliente."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
category: business
type: Orchestrator
timestamp: 2026-09-11T00:00:00Z
metadata:
  hermes:
    tags: [comercial, negociacao, email, gmail, verificacao, sigilo, follow-up, id-consultoria]
    related_skills: [elaboracao-proposta-comercial, hermes-cron-script-dispatch, id-comunicacao-multiusuario]
---

# Formalização por escrito de acordo negociado (cliente/parceiro da ID)

O passo que fecha a negociação: o que foi combinado em áudio/WhatsApp/reunião vira registro
escrito, com prazo e gancho de follow-up. É aqui que erro de forma custa caro — texto a mais
vira âncora contra a ID, e envio não verificado vira "eu não recebi". Cobre também cobrança de
resposta e a resposta a um acordo recebido de parceiro.

## When to Use

- A negociação já aconteceu e falta o registro por escrito (contraproposta, condições fechadas,
  resposta a uma proposta recebida).
- O principal pede "formalize isso por e-mail", "manda a resposta para <cliente>".
- **Não usar para:** proposta comercial nova (skill `elaboracao-proposta-comercial`, user-owned)
  nem contrato já assinado (`analise-contratual`).

## Gates (valem em toda instância)

1. **Nada da mecânica interna vai ao cliente.** Divisão de valores, repasse a terceiros ou a
   pessoa física, margem e "o preço é baixo porque é projeto de aprendizagem" ficam **fora** do
   texto. Justificativa de preço é escopo, prazo, quem executa, quem supervisiona, garantia. O
   cliente lê fragilidade e passa a ancorar aí — regra explícita do principal.
2. **Texto aprovado é imutável.** Envie exatamente o que o principal aprovou; qualquer ajuste
   volta para aprovação antes do envio.
3. **Thread única.** Responda na conversa existente (`In-Reply-To` + `References`, assunto `Re:`).
   Não abra conversa nova para o mesmo assunto — o cliente perde a cadeia e a prova do combinado.
4. **Destinatários = os que já estão na conversa.** Não acrescentar cópia nova (sócio, jurídico,
   financeiro) sem ok explícito: muda quem acompanha valores e contrato.
5. **Prazo no corpo.** Declare validade/data-limite de assinatura — sem data não existe follow-up
   legítimo depois.
6. **Identidade de envio.** Use a identidade que já conversa com aquele cliente e confira o nome
   exibido (registro e assinatura por sócio em `id-comunicacao-multiusuario`).
7. **Ação visível exige ok.** Envio a cliente/parceiro é ação externa: só depois do ok do principal.

## Pipeline

1. Reunir o material: a negociação (áudio/transcrição), a proposta anterior e o que ficou acordado.
2. Rascunhar e mandar o rascunho ao principal — **aguardar ok explícito** (uma coisa de cada vez).
3. Achar a conversa: `users().messages().list(userId="me", q="<assunto ou remetente>")` → obter o
   `threadId` e o `Message-ID` da última mensagem do interlocutor (header, não o id interno).
4. Enviar como resposta: `users().messages().send(userId="me", body={"threadId": <id>,
   "raw": <RFC822 em base64url>})`, com `In-Reply-To` = Message-ID dele e `References` = cadeia
   anterior + Message-ID dele; `From` no formato `Nome <email>` que o cliente conhece.
5. **Verificar lendo de volta** (seção abaixo) — inegociável.
6. Reativar o monitor da resposta: cron com `--monitor-script` (ver `hermes-cron-script-dispatch`),
   conferindo `model_snapshot`/`provider_snapshot` == default atual para o gate não falhar fechado.

## Verificação de envio (obrigatória)

"Aceito pelo servidor" prova que saiu, não **o que** saiu nem **para quem**. Reler a mensagem
enviada (`messages.get`, `format=full`) e conferir:

- `threadId` == a conversa original; `In-Reply-To`/`References` apontando para a mensagem dele;
- `From` (nome exibido + endereço), `To`, `Cc` exatamente como aprovado;
- corpo `text/plain` (base64url decodificado) **byte a byte** contra o texto aprovado — compare
  hash, não confie no olho.

Reporte ao principal nesse formato: id da mensagem, horário local, remetente, destinatários/cópia,
thread, e a confirmação de que o corpo bate com o aprovado. Receita de API em
`references/gmail-thread-reply-and-verify.md`.

## Pitfalls

- **Enviar sem reler** — não se sabe se saiu na thread certa, com o texto aprovado e para as
  pessoas certas. O relatório ao principal vem do read-back, não do retorno do `send`.
- **Adicionar cópia nova em silêncio** — muda quem vê valores; exige ok explícito.
- **Explicar a formação do preço** (custo, repasse, aprendizagem) — vira alavanca contra a ID nas
  próximas rodadas.
- **Assunto novo / conversa nova** para o mesmo negócio — quebra a cadeia que serve de registro.
- **Deixar o monitor desligado** depois do envio — a resposta chega e ninguém avisa; reative e
  verifique o snapshot de modelo.

## References

- `references/gmail-thread-reply-and-verify.md` — chamadas Gmail API para achar a conversa,
  responder na thread e verificar o envio (headers, threadId, hash do corpo).
