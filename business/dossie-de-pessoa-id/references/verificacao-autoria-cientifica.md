# Verificação de autoria científica (quem publicou o quê)

Receita para "quais artigos fulano publicou / de quais é coautor". Não use buscador web
para isso: nome de autor é indexado mal e devolve homônimo. Vá às APIs na ordem abaixo.

## 1. OpenAlex — achar o autor e o ORCID

```
api.openalex.org/authors?search=<nome>&per-page=25
```

Retorna `works_count`, `last_known_institutions` e `ids.orcid`. Nome brasileiro comum
produz **vários author IDs para a mesma pessoa** e homônimos com o mesmo nome: liste
todos, compare instituição e conjunto de coautores antes de escolher.

Depois: `api.openalex.org/works?filter=author.id:<ID>&per-page=50&sort=publication_year:desc`
para título, veículo, DOI, ano e lista de autores.

## 2. ORCID — a identidade e a lista curada

```
pub.orcid.org/v3.0/<orcid>/record
pub.orcid.org/v3.0/<orcid>/works
```

- `person.biography` é o desempate: o próprio autor descreve formação, vínculo e empresa.
  Se a bio bater com o contexto do dossiê, a identidade está confirmada.
- `/works` traz o que o autor cadastrou — inclusive itens que os agregadores não linkaram
  (preprint, monografia, periódico de baixo índice).

## 3. Crossref — ordem dos autores

```
api.crossref.org/works/<doi>
```

Só o Crossref dá `author[]` na sequência de publicação, mais `container-title` e `volume`.
Reporte a posição explícita ("3º de 11"): primeiro autor ≠ coautor, e o pedido costuma
ser justamente sobre coautoria.

## 4. Casos específicos

- **Preprint**: `api.crossref.org/works/10.20944/preprints...` responde igual.
- **Monografia/TCC**: repositório institucional DSpace (ex.: `ri.ufs.br/jspui/handle/...`)
  confirma na própria página `Document Type: Monografia`, orientador e curso. É trabalho
  acadêmico, não artigo — classifique à parte.

## Regras de leitura

- **Obra que só o agregador atribui e o ORCID do autor não lista = homônimo suspeito.**
  Confirme pela continuidade do grupo de coautores; sem isso, declare como não confirmada
  em vez de somar ao currículo.
- Semantic Scholar é ruidoso com nome brasileiro (devolve abreviação "W. Vieira" e obra
de outra década): sirva-se dele para achar itens extras, nunca como fonte de identidade.
- Periódico predatório ou de baixo índice aparece igual a qualquer outro: informe veículo
  e volume, sem juízo de valor que o dado não sustenta.

## Formato da entrega

1. Identidade confirmada (ORCID + uma linha de bio).
2. Artigos em periódico: ano · título · veículo · volume · posição na autoria · DOI.
3. Pré-prints.
4. Trabalhos acadêmicos (monografia, tese).
5. Ressalva curta: anais de congresso e capítulos não são cobertos por essas bases, e o
   Lattes exige verificação humana — a lista pode estar incompleta.
