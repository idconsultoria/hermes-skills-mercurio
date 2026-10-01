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
8. **Não invente fato para preencher o email.** Data de aprovação, motivo da demora, etapa de
   tramitação interna ("fechado com o jurídico"), promessa de prazo — tudo isso tem de estar
   no thread ou no registro. Ausência de fato vira omissão, não invenção: corte o parágrafo.

## Tamanho e vocabulário (preferência do principal)

- **Email de convite é curto.** O padrão do Gustavo é: saudação, o que é, os links/arquivos,
  o que precisa saber, pergunta de próximo passo, fechamento. Mirror do email de renegociar:
  ele escreve direto, em prosa, sem lista numerada de pontos. **~100 a 150 palavras** para um
  convite com artefato; cada bloco extra que você acrescenta tem custo de leitura sem
  ganho de decisão. Se o tom está bom e ele pede para encurtar, o problema é quantidade de
  conteúdo, não o tom.
- **Não peça desculpa por atraso que não é atraso.** Resposta no mesmo dia útil não pede
  desculpa por demora — pedir desculpa por algo que não aconteceu soa falso e abre flanco
  ("o que mais atrasou?").
- **O documento em revisão é MINUTA, não contrato.** Chame de minuta no email e no corpo da
  conversa enquanto não houver assinatura. No documento, o rótulo institucional pode
  continuar "CONTRATO DE PRESTAÇÃO DE SERVIÇOS" — o padrão da ID — mas o tratamento no
  relacionamento é "minuta".

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

## Criar rascunho na thread certa (Gmail API) — antes de enviar

Tres coisas que quebram silenciosamente e custam uma iteração cada:

1. **Todos os headers precisam estar no `raw` do draft na criação.** `users.messages().modify`
   **não** adiciona header — ele só mexe em `labelIds` e `classificationLabelValues`
   (erro: `No label or Classification Label updates provided`). Cc, Reply-To e tudo mais vão
   no `raw`, senão o rascunho nasce sem cópia.

2. **Para o rascunho cair NA thread original, mande `threadId` dentro do `Draft.message`.** Sem
   isso o rascunho nasce numa thread nova, sozinho, e o cliente perde a cadeia. A API exige os
   três critérios ao mesmo tempo: `threadId` + headers `References`/`In-Reply-To` em RFC 2822
   + `Subject` **idêntico** ao da thread (com o `Re:` já incluso).

3. **`drafts.get` NÃO aceita `metadataHeaders`** (so `format`, `id`, `userId`) —
   `TypeError: Got an unexpected keyword argument`. Para ler destinatários, chame com o
   padrão e filtre `payload.headers` na mão. Já `messages.get` aceita `metadataHeaders`.

Receita mínima:

```python
from email.message import EmailMessage          # não usar msg.set_content (ver pitfalls)
m = EmailMessage()
m["From"] = "Principal ID Consultoria <admin@idconsultoria.ai>"
m["To"] = "cliente@x.com"; m["Cc"] = ", ".join(CC)
m["Subject"] = "Re: " + assunto_original        # tem que bater com a thread
m["In-Reply-To"] = mid_do_ultimo
m["References"]  = (refs_anteriores + " " + mid_do_ultimo).strip()
m.set_content(corpo, subtype="plain", charset="utf-8")
raw = base64.urlsafe_b64encode(m.as_bytes()).decode()
dr = g.users().drafts().create(userId="me",
        body={"message": {"raw": raw, "threadId": THREAD_ID}}).execute()
```

**Verificação do rascunho (leia de volta, não confie no retorno):**
`drafts.get(id).message` → conferir `labelIds` contém `DRAFT` e **não** contém `SENT`;
`To`/`Cc` batem com o aprovado; `threadId` é o da conversa; e o corpo decodificado é
byte-a-byte igual ao texto aprovado. Se criar duas vezes (por causa de um erro no meio),
apague o rascunho antigo — duplicata na caixa é pior que rascunho faltando.

## Verification of sending (mandatory)

"Aceito pelo servidor" prova que saiu, não **o que** saiu nem **para quem**. Reler a mensagem
enviada (`messages.get`, `format=full`) e conferir:

- `threadId` == a conversa original; `In-Reply-To`/`References` apontando para a mensagem dele;
- `From` (nome exibido + endereço), `To`, `Cc` exatamente como aprovado;
- corpo `text/plain` (base64url decodificado) **byte a byte** contra o texto aprovado — compare
  hash, não confie no olho.

Reporte ao principal nesse formato: id da mensagem, horário local, remetente, destinatários/cópia,
thread, e a confirmação de que o corpo bate com o aprovado. Receita de API em
`references/gmail-thread-reply-and-verify.md`.

## Roteiro do email de convite (minuta para revisão)

Quando a condição já está fechada e o próximo passo é o cliente ler um artefato, o
email **não** recount a negociação — ele entrega e destrava.

```
Saudação com a hora certa do dia (boa noite / boa tarde, conforme o envio real)
1 linha: o que você está mandando ("Duas minutas para vocês revisarem")
1 linha: o que já está pronto do lado deles ("Já liberei o acesso a todos os endereços
        dessa conversa, e os documentos estão abertos para comentário direto no texto")
Os artefatos: rótulo curto + link em linha própria
Valores: uma linha, nos números fechados, sem renegociar
Próximo passo: uma pergunta que o cliente responde com um "sim" ou com um dado
Fecho curto: canal aberto ("Se precisarem de algum esclarecimento, basta responder
        neste email que a gente responde")
Assinatura do corpo que já é uso da casa
```

- **Cada parágrafo faz UM trabalho.** Se um parágrafo não move o cliente (entregar,
  informar, destravar, perguntar), ele sai.
- **Rode o `humanizer` no rascunho** antes de mostrar ao principal. Ele audita emdash,
  negrito, emoji, hedging, regra de três e artefato de chatbot. Em email comercial o
  excesso aparece como "recheado com coisa demais".
- **Não hardcode quebra de linha dentro do parágrafo.** O email vai como texto contínuo:
  quebrar no meio da frase para caber na tela mostra que o rascunho foi colado de outro
  lugar. Só quebre onde a quebra é semântica (rótulo do link, lista).
- **O texto aprovado é imutável** — se o principal editar uma palavra no rascunho e o ok
  for "pode mandar", vale a versão com a edição dele, não a sua.

## Compartilhar o artefato com o cliente antes do envio

Quando o convite leva link de Google Doc, a permissão é parte do convite — não um extra
posterior:

1. Antes de redigir, liste todos os endereços que aparecem na thread (From/To/Cc de
   **cada** mensagem, incluindo as antigas, não só a última).
2. `permissions().create(role="commenter", sendNotificationEmail=True)` para cada um.
3. **Confira depois** com `permissions().list(fields="permissions(emailAddress,role,type)")`:
   `sendNotificationEmail=True` responde OK mesmo quando o convite falha em silêncio para
   endereço sem conta Google.
4. O papel certo é `commenter` (lê e comenta no texto). `reader` não sirve para quem precisa
   marcar o trecho; `writer`/`owner` no cliente é erro de segurança.

Mencionar "já liberei o acesso" no corpo do email só depois de confirmar o passo 3 — sem
isso é afirmação que o cliente pode testar e dar falsa.

## Pitfalls

- **Enviar sem reler** — não se sabe se saiu na thread certa, com o texto aprovado e para as
  pessoas certas. O relatório ao principal vem do read-back, não do retorno do `send`.
- **Adicionar cópia nova em silêncio** — muda quem vê valores; exige ok explícito.
- **Explicar a formação do preço** (custo, repasse, aprendizagem) — vira alavanca contra a ID nas
  próximas rodadas.
- **Assunto novo / conversa nova** para o mesmo negócio — quebra a cadeia que serve de registro.
- **Deixar o monitor desligado** depois do envio — a resposta chega e ninguém avisa; reative e
  verifique o snapshot de modelo.
- **Reescrever um trecho do Doc direto por deletes soltos em vez de refazer a faixa.** Em
  anexos, bullets e tabelas do Docs, `deleteContentRange` caractere a caractere desloca os
  índices seguintes e corrompe o vizinho: no mesmo lote, "Pesquisa" virou "Pesuisa" e
  "Governança" virou "Gvernança", sem erro da API. **Refaça a faixa inteira** de uma vez
  (do marco inicial ao final: `ANEXO I` → `ANEXO II`), reinsira o texto já no formato
  final e aplique estilo/bullet por **casamento de texto** sobre o doc relido — nunca por
  índice guardado de antes do insert.
- **Varredura de estilo sem janela de alcance estraga a CAPA.** Um laço que normaliza
  `HEADING_1` sem limitar o trecho alcançou o início do documento e apagou o tamanho (36pt),
  a cor do título e a cor do rótulo de tipo. O sintoma é silencioso: **o texto continua
  correto, só o estilo some**. Depois de qualquer edição em lote, confira os `textRuns` dos
  primeiros parágrafos (rótulo de tipo + título da capa), não só o texto extraído.
- **Tabela criada por API: `insertText` desloca todos os índices seguintes.** Preenchendo
  várias células num único `batchUpdate` com índices pré-calculados, **todo o texto cai na
  primeira célula** e as demais ficam vazias. Preencha **de trás para frente** e **uma
  tabela por execução** (relendo o documento entre elas) — ler as duas do mesmo snapshot
  deixa a segunda com índices stale e o texto vaza para a anterior.

## References

- `references/gmail-thread-reply-and-verify.md` — chamadas Gmail API para achar a conversa,
  responder na thread e verificar o envio (headers, threadId, hash do corpo).
