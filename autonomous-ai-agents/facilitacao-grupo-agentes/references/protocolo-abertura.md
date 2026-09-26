# Protocolo de abertura — mensagem copy-paste

O facilitador não tem poder sobre a configuração dos outros agentes. O que instala o
protocolo no grupo é o **anúncio de abertura**: ele é lido por todos os agentes
presentes, e é a partir dele que a regra "devolva a palavra para mim" passa a valer.

Publicar na abertura, antes da pauta. Uma mensagem só.

---

## Modelo

```
Reunião conduzida por mim. Protocolo, sem exceção:

1. A palavra é minha. Eu dou a um de cada vez, por menção.
2. Ao terminar seu turno, encerre a mensagem com a minha menção
   (<@handle_do_facilitador>). Sem isso eu não sei que você falou e a
   reunião trava.
3. Precisa falar com outro agente? Peça a mim. Eu passo a bola. Não marque
   o colega você mesmo — duas menções na mesma mensagem acordam os dois ao
   mesmo tempo e a ordem de fala se perde.
4. Uma menção por mensagem, sempre no final. Mencionar no meio faz o bot
   reagir com o texto ainda pela metade.
5. Fale só do item atual. Se um item não é seu, não responda mesmo assim.
6. Sem resposta não tem segunda chamada: o item fica para o fim.
7. Silêncio de quem não é chamado é esperado. Não espere ser chamado por
   conta própria — se não teve menção, não é a sua vez.
```

---

## Racional, por linha

| Linha | Por que existe |
|---|---|
| 1 | A autoridade de turno precisa ser declarada, não presumida. |
| 2 | É a regra que o dono pediu: **devolver a fala ao facilitador**. Sem menção final, o turno se perde. |
| 3 | Proibição de marcação cruzada entre agentes — a razão número um de dois bots acordarem juntos. |
| 4 | Protege contra o quadro de edição truncado durante streaming. |
| 5 | Evita que todo agente responda a toda menção humana, o que destrói a pauta. |
| 6 | Evita cutucar agente mudo e queimar o orçamento de mensagens do grupo. |
| 7 | Fecha o principal comportamento alternativo dos bots: responder por conta própria. |

## Como usar

- Publicar uma vez, na abertura. Não repetir a cada item.
- Se um agente violar a regra (marcar colega, não devolver a palavra, falar fora do
  item), corrigir em uma linha e devolver a bola: `Regra 3 — passa por mim. @<handle>`
  A repetição pública é o mecanismo de aprendizado; bronca longa não é.
- Se o humano abrir a reunião antes do anúncio, encaixar o protocolo logo abaixo da
  primeira pauta, sem bloquear o andamento.
