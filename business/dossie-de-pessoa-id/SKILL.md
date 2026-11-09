---
name: dossie-de-pessoa-id
description: "Use ao montar dossiê de pessoa da ID a partir da base."
category: business
type: Reference
timestamp: 2026-11-04
---

# Dossiê de pessoa a partir da base da ID

Carregue quando o pedido for "o que você sabe sobre mim/falano", due diligence de
parceiro antes de proposta ou reunião, ou checagem de histórico de um contato.

## Regra de ouro

A **página de conceito é o resumo, não o estado mais recente**. O que aconteceu depois
do `stale_after` / "Última atualização" só existe nas fontes espelhadas. Sempre desça
para as fontes antes de responder — "busca maior" é o padrão, não a exceção.

## Passo 1 — Identidade de quem pergunta

- O `chat_id` do log do gateway manda, não o rótulo do chat.
- Sócio conhecido → registro de `id-comunicacao-multiusuario` (técnico só com o Gustavo).
- Pessoa de fora da sociedade → linguagem acessível, sem encanamento.
- Nome comum: confirmar por âncora (empresa, cidade, curso, Telegram) antes de atribuir fato.

## Passo 2 — Camada KB

```
kb_search <nome>   →   kb_read people/<slug>
```

Anotar do conceito: resumo, `## Status`, papel, vínculo, pendências, `status: draft`
e `stale_after`. Página `draft` vencida = dizer isso na resposta, nunca apresentar como
estado atual.

## Passo 3 — Varredura nas fontes

```
search_files(pattern="Nome|apelido", path="<HERMES_HOME>/context-kb",
             target="content", output_mode="count", limit=100)
```

Ranquear os arquivos por `mtime` com Python e ler os 8–10 mais recentes. Onde o histórico
real mora:

- `sources/whatsapp/dms/<pessoa>-*.md` — relação privada, pedidos e contexto informal.
- `sources/whatsapp/groups/*` — projeto, decisões, atribuição de papel.
- `sources/fathom/meetings/*` — o que foi combinado em reunião.
- `sources/mercurio/telegram/*` — o que a pessoa já pediu ao agente (entregas, propostas).

Dentro dos arquivos, grep por palavra-chave de negócio (proposta, contrato, edital,
reunião, remuneração, escopo) em vez de ler tudo. Timestamps das fontes são **UTC** —
converter para BRT ao exibir.

## Passo 4 — Ruído

- Apelido curto casa com termo técnico (ex.: "wall" em "wall diagram", "firewall"): descartar.
- Homônimo: mesma pessoa na KB ≠ mesma pessoa numa base externa. Confirme antes de atribuir.

## Passo 5 — O que entra no dossiê

1. Identidade e trajetória (como a relação começou, com data).
2. Papel atual e natureza do vínculo — separar **cargo formal**, **enquadramento comercial**
   e **o que de fato executa**.
3. Frentes em curso, cada uma com número (valor, prazo, participação).
4. Últimos 60–90 dias.
5. Pendências e lacunas documentais.

## Passo 6 — Filtro de privacidade (não negociável)

- **Não repassar o que terceiros disseram sobre a pessoa em conversa privada** (opinião de
  sócio, conflito, fofoca), mesmo que esteja na base. A resposta é sobre a pessoa, não sobre
  o que falam dela.
- Saúde, vida amorosa, família e dívida pessoal ficam fora — só entram se a própria pessoa
  abrir o assunto.
- Citar fonte é bom; citar conversa alheia não é.

## Passo 7 — Entrega

- DM: dossiê normal, bullets curtos, números na frente.
- Grupo: ≤3 linhas + anexo (regra do grupo da ID).
- Fechar com a lacuna e **uma** pergunta ("atualizo a ficha com o que mudou desde <mês>?")
  e, se fizer sentido, oferecer verificação externa (publicações, empresa, processo).
- Atualizar a KB só por `kb_note`/`kb_correct`, **com ok explícito** — nunca escrever no
  canônico.
- **Proposta não publicada não existe.** `kb_note` grava um arquivo *não rastreado* em
  `context-kb/proposals/`; a consolidação roda no host Oracle, que só enxerga o que está em
  `origin/master`. Sem `git add` → `commit` → `git push`, a proposta nunca é aplicada e o
  silêncio do ciclo parece aprovação. Depois do push, confirmar `git ls-remote origin master`
  igual ao `HEAD` local.
- `out_of_scope: true` no frontmatter é esperado quando as páginas-alvo têm `scope: both`
  (pessoa, empresa, projeto) e o perfil escreve só em `scope: id`: a proposta fica na fila e a
  Atena adjudica. Não reenviar esperando resultado diferente — apenas avisar que pode levar
  um ciclo.
- Depois de publicar, se o sócio pediu para acompanhar, criar cron silencioso (watchdog) que
  faz `git pull` e só emite saída quando o `status:` da proposta sai de `pending`.

## Pitfalls

- Responder só com o conceito da KB quando a pergunta é "o que você sabe sobre mim":
  entrega um retrato de meses atrás e queima a rodada.
- Não perguntar "quem é você?" para contato já registrado em allowlist/KB — identificar e responder.
- Não despejar mensagens cruas: sintetizar em frentes e datas.
- Publicação científica, CNPJ ou processo: é verificação externa — receita em
  `references/verificacao-autoria-cientifica.md` (OpenAlex → ORCID → Crossref, com o
  teste de homônimo).
- Trajetória profissional atual e sinal de interação científica fora da academia vêm do
  LinkedIn — receita e limites em `references/perfil-linkedin.md`.
