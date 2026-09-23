# Mineração de transcrições diarizadas (receita)

Objetivo: reduzir 250-280 mil caracteres de transcrição ruidosa a algumas centenas de candidatos de encaminhamento, legíveis no contexto do agente, **sem** ler o arquivo inteiro.

## Passo 1 — Dedupe por corpo da fala

A pipeline de áudio reprocessa blocos e duplica turnos com timestamp deslocado. O dedupe é por **texto da fala**, não por linha inteira (o timestamp muda):

```python
import re
lines = [l for l in tr.split("\n") if l.startswith("[")]
seen, clean = set(), []
for l in lines:
    body = re.sub(r'^\[[^\]]+\]\s*\S+\s*', '', l)
    if body in seen:
        continue
    seen.add(body); clean.append(l)
```

Reporte a taxa de duplicação: ela calibra a confiança no tamanho percebido da reunião (medido em sessão real: 6% e 16%).

## Passo 2 — Fatiar em sentenças e filtrar por compromisso

Cada turno é um parágrafo; o candidato é a **sentença**. Conjunto de padrões PT-BR com recall alto (compromisso explícito + atribuição + prazo + artefato):

```
(vou |vamos |fico de|ficou de|fica de|fica com|fica respons|respons[aá]vel|me comprometo|deixa comigo|
pode deixar|t[aá] feito|j[aá] fiz|combinad|encaminh|tarefa|prazo|
at[eé] (segunda|ter[çc]a|quarta|quinta|sexta|s[aá]bado|domingo|amanh|o fim|o final|semana)|
pr[oó]xima (semana|sess[aã]o|reuni)|semana que vem|manda(r|mos)? |envia(r)? |agenda(r|mos)? |
marcar|marquei|marcamos|marca um|implanta|implementar|configura|instalar|criar (um|uma|o|a|os|as)|
criar agente|desenvolver|documenta(r|ção)|levantar|pesquisar|prospectar|follow|esteira|checklist|
entregar|preciso|tem que|tenho que|vai ter que|contratar|fechar contrato|proposta|or[çc]amento|planilha)
```

```python
for l in clean:
    m = re.match(r'\[([^\]]+)\]\s*(\S+)\s*(.*)', l, re.S)
    if not m:
        continue
    sp, ts, body = m.groups()
    for s in re.split(r'(?<=[.!?])\s+', body):
        s = s.strip()
        if len(s) > 20 and re.search(PAT, s, re.I):
            hits.append([ts, sp, s])
```

Saída medida: 2635 turnos → 327 candidatos (~22 mil caracteres) numa sessão de 4h53; 2344 turnos → 257 candidatos (~16 mil) numa de 2h47.

## Passo 3 — Ler o fechamento inteiro

Metas, prazos e donos se concentram no fechamento, onde o filtro por palavra-chave perde precisão (frases curtas de decisão: "cento e vinte e cinco até o final do ano"). Leia os últimos ~25% das linhas **sem filtro**, tratando timestamp como inválido.

## Passo 4 — Triagem do candidato

Cada candidato vira uma de três coisas:

1. **Encaminhamento** — tem verbo de ação + algo atribuível (dono citado, prazo, artefato).
2. **Contexto** — discussão que explica uma decisão; não entra na lista, mas sustenta a evidência.
3. **Ruído** — "vou botar um post-it", "eu vou ali, peraí". Descarte sem cerimônia: falso positivo no filtro é barato, falso negativo é caro.

## Passo 5 — Formato de saída

Numeração estável por sessão (`S1-7`) para permitir cobrança posterior; por item: ação, responsável, prazo literal, evidência (citação curta + timestamp só quando o timestamp é confiável), rótulo do falante e confiança. Feche com as **lacunas da ata** em lista própria.

## Armadilhas de execução

- **Delegar o arquivo inteiro a um subagente estoura o teto de relógio do filho e não sobra artefato.** Fatie por faixa de linhas (~700-900 por filho), cada um gravando o próprio arquivo antes de responder.
- **Rodar o filtro no arquivo cru, sem dedupe**, duplica candidatos e infla a leitura — dedupe primeiro.
- **Nomes deformados** mudam de forma ao longo da transcrição; normalizar cedo (um de-para por sessão) evita dois donos para o mesmo item.
