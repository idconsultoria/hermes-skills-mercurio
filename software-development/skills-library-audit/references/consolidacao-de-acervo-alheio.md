# Consolidar um acervo de skills que não é seu

Receita de decisão para quando o pedido é "consolide as skills do perfil X" — acervo
 herdado, de outra agente, ou nunca gerenciado. O objetivo é sair com o catálogo
enxuto, correto e **reversível**, e com a razão de cada decisão registrada.

Toda decisão aqui sai de **evidência lida**, nunca do nome da pasta ou da skill.

---

## 1. Inventário antes de qualquer escrita

| Evidência | O que responde | Onde |
|---|---|---|
| `find $DIR -name SKILL.md \| wc -l` | quantas existem no disco | disco |
| hash do corpo normalizado (frontmatter fora) | quantas são realmente idênticas | `re.sub(r'\s+',' ',corpo)` |
| `author:` no frontmatter | **de quem** é a skill | ownership |
| `platforms: [...]` + existência do binário | se ela roda **aqui** | viabilidade |
| `.usage.json` (`use_count`, `last_used_at`) | se ela é usada de verdade | valor |
| arquivo de procedência (`.origem`, `.source`) | **de qual perfil/repo veio** | origem |
| `related_skills:` que não resolvem | dívida herdada | integridade |

Conte também skills com **nenhum sinal de uso** — é o melhor alvo de corte: 30–50% do acervo
costando contexto sem nunca disparar é o principal ganho de consolidação.

`git init` + commit de baseline **antes** do primeiro corte, sem versionar locks, cache,
telemetria e blobs de backup. Sem isso, apagar diretório de skill é irreversível.

---

## 2. O marcador de procedência decide a direção do merge

Duas cópias com corpo idêntico **não** são simétricas: uma é original, a outra é cópia.
A pergunta "qual fica?" tem resposta objetiva, e ela é o arquivo de procedência — não o
tamanho, não a data, não o `type:` mais completo.

```
casa/architecture-diagram/.origem:
  acervo da casa (copiada de /opt/.../profiles/jupiter/skills/creative/architecture-diagram)
```

O `.origem` revelou que a pasta inteira era **espelho de outro perfil**. Isso inverteu a
decisão: a cópia da "casa" era a derivada, e a categoria natural era o original. Sem ler
esse arquivo, a direção do merge é um palpite.

**Antes de remover a perdedora, mova o marcador de procedência para a vencedora** — a
informação "de onde veio" é o que impede a mesma cópia de ressurgir na próxima consolidação.

Pasta sem semântica própria (nome genérico, tipo "acervo", "casa", "comum", "shared") não é
categoria: é onde a curadoria despejou. Dissolva — cada skill vai para a categoria que
descreve o que ela faz, ou sai do escopo.

---

## 3. Gêmeos divergentes: o merge é nos dois sentidos

Corpo diferente entre as cópias não significa "escolha a maior". Os dois lados costumam
ter valor em cobertura diferente:

- uma tem o corpo **adaptado** (`type`, `timestamp`, escopo do dono, marca local)
- a outra tem os **arquivos de apoio** que a adaptada perdeu (scripts, `references/`)

Direção correta: **corpo adaptado + união dos arquivos de apoio**.

Colisão de nome com conteúdo **diferente** não se resolve escolhendo: guarde a versão
descartada em `_divergencia/<caminho-original>/` dentro da skill vencedora. O conteúdo fica
recuperável e a decisão fica visível para quem sabe o que procurou.

Onde a camada de valor mora (ex.: a versão do dono tem `references/id-humanizacao.md` e a
cópia não tem), quem fica é quem tem a camada — e a evidência é o arquivo, não o `related_skills`.

---

## 4. Purga de escopo: três filtros, arquivar em vez de apagar

| Filtro | Teste | Destino |
|---|---|---|
| **Propriedade** | `author:` é de outro agente do time | `_fora-do-escopo/` |
| **Plataforma** | `platforms: [macos]` e o binário não existe no host | `_fora-do-escopo/` |
| **Ofício** | a skill opera um cargo que não é o desta agente | `_fora-do-escopo/` |

O filtro de propriedade é o que mais se esquece e o que mais dói: um acervo que carrega
método de outro cargo cria **dupla autoridade** — duas skills capazes de decidir oferta,
preço ou canal, e a agente passa a executar regra alheia em vez de aguardar a decisão do
dono. Leia o `author:` de **todas**, não só das suspeitas.

Arquive, não apague: mova a pasta para `_fora-do-escopo/<categoria>/<skill>` com o
`SKILL.md` intacto e escreva um `README.md` que diga **de quem é cada uma, por que saiu e
como reativar**. Reativar exige decisão escrita do dono — mover o diretório de volta não
basta. Um prefixo com `_` mantém o acervo fora do catálogo sem exigir exclusão no
`skills_list`.

Verifique o binário antes de banir por plataforma: `which <ferramenta>` e o `uname`. Some
com o que **nunca roda aqui**, não com o que tem caminho incomum.

---

## 5. Referência herdada: some a morta, reponta a viva

`related_skills:` herdado de repos upstream aponta para skills que nunca vieram junto
(`ocr-and-documents`, `excalidraw`, `subagent-driven-development` — nomes de outro repo).
Duas saídas, por skill: remover a entrada, ou **repontar para a skill real** que cobre o
mesmo terreno. Repontar é melhor: preserva a intenção e conserta a dívida.

Só conte entrada morta no campo `related_skills` (e em link de arquivo relativo). Varredura
por backtick em prosa vira **ruído**: flag de CLI, nome de pacote e placeholder de template
casam como se fossem skill.

Placeholder (`references/styles/<style>.md`, `references/<cliente>-brand.md`) **não** é
quebra: é template. Só conte caminho concreto que não existe.

---

## 6. Atribuição cruzada: o path é compartilhado, o nome não

Quando um acervo herda instruções de outro perfil, o defeito costuma ser a **assinatura**,
não o path. Verifique se o path citado existe para *esta* agente antes de "consertar" — um
renderer em `/opt/data/...` compartilhado entre perfis é válido; a seção que o descreve
como "do perfil X" é que está errada. Reescreva o rótulo preservando o caminho e o conteúdo
técnico.

Mesmo teste para o `SOUL.md`: skill que descreve o host com o nome de outra agente
("Oracle Linux, Hermes container") tem a **orientação** errada, não o runtime errado — o
caminho pode ser válido e a descrição é que não.

---

## 7. Cluster que PARECE duplicata e não é

Suspeita de fusão em massa é hipótese, não plano. Antes de fundir skills de um mesmo
assunto, **leia o corpo de cada uma procurando declaração de escopo**. Cluster maduro
costuma declarar a fronteira no próprio texto:

> "As duas outras skills são user-owned; não duplicar aqui regra que pertença a elas."
> "`conteudo-id/governanca-conteudo-id` vem antes: esta skill opera dentro da precedência
> que ela estabelece e nunca redefine canal, cadência, meta, oferta, preço ou prova."

Esse tipo de guarda é **arquitetura deliberada**: fundi-la destrói a separação que alguém
construiu de propósito, e o monopólio da autoridade volta em forma de skill única gigante.
Agrupamentos que **não** têm guarda nenhuma (o mesmo assunto declarado três vezes, sem
fronteira escrita) são fusão legítima.

Regra de decisão: **guarda explícita no corpo preserva; ausência de guarda justifica fusão.**

Pack de skills externas com `evals/` em todas e procedência comum é **unidade**, não
acúmulo: não se dissolve porque são 28. O corte ali é por valor de uso, não por número.

---

## 8. Fechamento

1. Baseline commit antes do primeiro corte; confirmar `git log --oneline -1` aponta para ele.
2. Uma decisão por vez, cada uma com validação no mesmo passo (YAML parse, hash, contagem).
3. Registro escrito da rodada (tabela de merges, purgas e dissoluções) dentro do próprio
   acervo, para a próxima rodada saber o que já foi decidido e por quê.
4. Recontagem e conferência final contra o disco — o número declarado é afirmação dura.
