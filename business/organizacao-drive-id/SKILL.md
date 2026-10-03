---
name: organizacao-drive-id
description: "Use ao organizar pastas e docs de cliente no Drive da ID."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [drive, google, pastas, subpastas, simplexis, contrato, cliente, arquivamento, email, tom]
    related_skills: [auxiliar-adm-id, google-workspace, formalizacao-acordo-cliente, contratos-justos-id]
type: Orchestrator
timestamp: 2026-09-30T22:00:00Z
---

# Organização do Drive da ID + email para cliente

Dois assuntos que aparecem juntos em toda entrega comercial: **arrumar a pasta do projeto
no Drive** e **escrever o email que acompanha**. Este skill cobre os dois.

## Gate 1 · Antes de mover qualquer coisa

1. **Liste a pasta destino antes de criar** e confira se ela já não existe (evita duplicata).
2. **Nunca apague nem mova material que o principal não pediu.** Duplicatas, versões
   antigas e arquivos de teste: **reporte e ofereça arquivar**, não decida sozinho.
3. **Achados do tipo "isso não é do projeto X"** vão ao relatório, não para o lixo. O
   principal decide.

## Gate 2 · Estrutura de pasta por projeto

A ID numera por contrato dentro da pasta do cliente (`4.2.14. Solution Master` →
`Contrato 1`, `Contrato 2`, ...). Dentro de cada contrato use esta grade — que espelha o
que o Contrato 1 já faz (Dédalo: `00 Controle`, `01 Subprodutos`, `02 Base de Conhecimento`):

```
Contrato N - <nome do projeto>/
  00 - Controle e Contrato     ficha de escopo/protótipo, minuta vigente
  01 - Requisitos e Proposta   PRD, escopo do cliente, proposta enviada
  02 - Mercado e Alinhamento   análise de concorrência, notas de alinhamento
  03 - Prototipo e Design      protótipo, design system, telas, LEIA-ME
```

Nomes com prefixo numérico ordenam sozinhos no Drive e dizem o que é cada coisa sem
abrir. O `00` é o índice: quem chega depois acha o que precisa primeiro.

**Se o cliente mandou artefatos num ZIP:** descompacte e suba cada arquivo solto, com o
nome próprio — não o ZIP inteiro, que ninguém abre. Confirme os bytes depois do upload
(`files.get(fields="size")` + `get_media` e comparar tamanho); arquivo vazio é sintoma de
upload interrompido, e sobra duplicado.

**Subpasta = um artefato por vez.** Se o ZIP traz mais de um arquivo, cada um vira um item
nomeado, e uma ficha curta aponta para o que é link externo (protótipo em Vercel, ambiente
de demonstração) — **link solto no corpo de um documento se perde**; registre em lugar com
endereço próprio.

## Gate 3 · Mover e copiar — a parte que mais dá erro

**`files.update(addParents=X, removeParents=Y)` numa chamada só dá 404** quando `Y` é uma
pasta compartilhada. Separe em **duas chamadas**: primeiro `addParents`, reler `parents`,
depois `removeParents` de cada pai antigo, um a um. Confirme com `fields="id,parents"`.

**Writer não move arquivo de outro dono.** Quando o `admin@idconsultoria.ai` tem papel
`writer` num arquivo cujo `owners` é outra conta, mover devolve 403 e o arquivo **some do
radar** (na prática: cai em "Meu Drive"). Duas saídas:

- **Copiar** (`files.copy` + `parents`) e deixar o original onde está — seguro e reversível.
- Pedir ao principal a transferência de posse.

Nunca assumir posse de arquivo de conta pessoal por conta própria.

**Nome real, não nome lembrado.** Antes de mover por nome, `files.get(fields="name")` e
confira caractere a caractere: um sufixo `v2` que não existe faz o arquivo "não ser
encontrado", e dois arquivos com o mesmo nome exigem desambiguar por `modifiedTime` e
conteúdo. **Sempre mova por ID**, resolvendo o nome só na busca.

**Falhou no meio? Liste antes de tentar de novo.** A tentativa anterior pode ter criado
subpasta vazia, movido metade dos arquivos ou deixado o original órfão.

## Gate 4 · Email para cliente — voz do Gustavo

Calibre lendo as respostas anteriores do principal na thread antes de escrever. Os traços
são consistentes:

- **Primeira pessoa, "você"** — nunca "a CONTRATANTE" nem "prezado cliente".
- **Curto.** Um parágrafo faz uma coisa. Passou de ~150 palavras, corte.
- **Abre acknowledge, vai ao ponto, fecha com convite.** Sem preâmbulo de "espero que ajude".
- **Frases do Gusti:** "me confirma", "prefiro ajustar agora do que descobrir no meio do
  caminho", "se estiver de acordo", "qualquer coisa, estou à disposição".
- **Nada de rodapé de IA, nada de emoji, nada de aspas curvas.**

### O que nunca entra

| Nunca | Por quê |
|---|---|
| "Peço desculpas pela demora" | Se a resposta sai no mesmo dia, não há demora a reconhecer — e a desculpa falsa sinaliza fraqueza |
| "Estou fechando com o jurídico" | Não é verdade nem interessa ao cliente; vira promessa de prazo |
| Explicar formação de preço, margem, "projeto de aprendizagem" | Vira âncora na próxima rodada |
| Parágrafo de contexto histórico do projeto | O cliente vive isso; você não precisa recapitular |
| Lista numerada de "pontos importantes" | Vira wallpaper. Pontos vaem em prosa, na ordem da conversa |

O principal escreve em **primeira pessoa** ("me confirma", "eu consolido", assinatura
"Gustavo e Cléverton"). Escreva como ele falaria, não como a empresa.

**Rascunho antes de enviar, sempre.** Quando o principal pedir revisão, entregue o texto
no chat com **thread, destinatários exatos e verificações em nota ao pé**, e espere o ok.
Vier o ok: crie o **rascunho no Gmail** (não envie) e diga o que fez. Rascunho criado em
thread errada é rascunho perdido — ver `references/drive-e-gmail.md`.

**Minuta não é contrato.** Documento em revisão chama-se MINUTA no título, no corpo e no
assunto do email: contrato pressupõe assinatura, minuta é o que ainda pode mudar.

## Gate 5 · Verificação — sempre por leitura de volta

Nada de "foi movido", "foi compartilhado", "foi salvo" baseado no retorno da chamada.

- **Drive:** relistar a pasta e conferir nome por nome. Movido = está **dentro** da subpasta,
  não "não está mais na raiz" (pode ter ido parar em "Meu Drive").
- **Compartilhamento:** `permissions.list(fields="permissions(emailAddress,role)")` e contar
  um a um. `sendNotificationEmail` responde mesmo quando o convite falha silenciosamente
  para e-mail sem conta Google.
- **Email/rascunho:** `labelIds` contém `DRAFT` e **não** contém `SENT`; corpo decodificado
  é byte-a-byte igual ao aprovado; `threadId` é o da conversa.

## Pitfalls

- **`gustavomelloenciv@gmail.com` é fallback VETADO** — e é `owner` de muito material da
  ID espalhado no Drive. Ao achar arquivo dele você **não** pode mover (403). Copie e
  reporte; não tente tomar posse.
- **Fila de nomes iguais:** com várias cópias de um mesmo documento, a busca por nome exato
  devolve várias. Desambigüe por `modifiedTime`, nº de blocos e presença dos
  requisitos-chave antes de escolher a canônica.
- **Upload por `media_body` sem objeto de upload** dá `TypeError: media_filename must be
  str or MediaUpload`. Use `MediaFileUpload(path, mimetype=..., resumable=True)`.
- **`files.update(name=...)` não é parâmetro do update.** Renomear é patch à parte:
  `files.update(fileId=X, body={"name": novo}, fields="id,name")`.
- **Texto corrompido ao gerar documento longo:** confira caracteres não-ASCII antes de
  subir. Resíduo cirílico/chinês = arquivo contaminado (ver `md-to-timbrado-id`).

## Arquivos desta skill

- `references/drive-e-gmail.md` — API de Drive (mover, copiar, permissões) e de Gmail
  (rascunho na thread, verificação de envio), com as assinaturas exatas e os erros reais.
