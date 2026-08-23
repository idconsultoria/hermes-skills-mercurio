# SQL Casting Pitfalls em Queries de Teste do Sandbox

Colunas PostgreSQL de tipos complexos precisam de cast explícito ao concatenar com
`||` em queries de teste. Sem o cast, o Postgres lança erros que se manifestam de
forma confusa no driver Python.

## Colunas `text[]` (arrays)

```sql
-- ERRADO (malformed array literal):
SELECT titulo || '|||' || COALESCE(area_tematica, '{}')

-- CORRETO:
SELECT titulo || '|||' || COALESCE(area_tematica::text, '{}')
```

Colunas como `area_tematica`, `porte_elegivel` (tipo `text[]`) precisam de `::text`.
O Postgres tenta interpretar a string concatenada como literal de array e falha.

## Colunas `timestamptz`

```sql
-- ERRADO (invalid input syntax for type timestamp with time zone: ""):
SELECT titulo || '|||' || COALESCE(prazo_inscricao, '')

-- CORRETO:
SELECT titulo || '|||' || COALESCE(prazo_inscricao::text, '')
```

`prazo_inscricao` (tipo `timestamp with time zone`) não aceita `''` como valor vazio
no COALESCE — precisa do cast `::text` primeiro.

## Sintoma no driver Python

O erro de SQL é mascarado como:
```
ValueError: not enough values to unpack (expected 9, got 1)
```
Isso acontece porque `psql -At` retorna string vazia (ou "ERR:...") em vez da
linha esperada. O `row.split("|||")` encontra 1 elemento em vez de N.

**Debug**: imprima `repr(row)` antes do split para ver o retorno bruto do psql.

## Referência
- Projeto: ArtemisHub (`artemishub`, PostgreSQL 17)
- Ocorreu durante verificação de IA (análise de editais) em 2026-08-22
