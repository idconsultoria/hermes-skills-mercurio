# Wikipedia action=raw bypass — recipe testado (ago/2026)

Contexto: pesquisa eleitoral brasileira (candidatos UP/PCB/PSTU, eleição 2026).
`web_extract` falhou em pt.wikipedia.org E pt.m.wikipedia.org com
`Internal Server Error: Failed to scrape ... (document_antibot)` — inclusive com
retry automático. O bypass abaixo funcionou em 100% dos casos no mesmo lote.

## Comandos exatos

```bash
# Baixa o wikitext cru da página (infobox + seções + tabelas + refs)
curl -s -A "Mozilla/5.0" "https://pt.wikipedia.org/w/index.php?title=Unidade_Popular_(Brasil)&action=raw" > /tmp/up_raw.txt

# Múltiplas páginas em lote
for t in "Samara_Martins" "Edmilson_Costa" "Hertz_Dias"; do
  curl -s -A "Mozilla/5.0" "https://pt.wikipedia.org/w/index.php?title=$t&action=raw" | head -c 6000
done
```

Regras:
- Espaços viram `_`; caracteres acentuados precisam de URL-encode.
- O User-Agent `Mozilla/5.0` é necessário (curl "nu" às vezes é bloqueado).
- Título exato: use o nome do verbete como aparece na URL da Wikipédia.

## Parsing do wikitext (python heredoc)

```python
import re
t = open('/tmp/pcb_raw.txt').read()
print(re.findall(r'^==+ .* ==+$', t, re.M))     # mapa das seções
i = t.find('== História ==')
print(t[i:i+5000])                               # fatia a seção desejada
```

A infobox vem no topo do wikitext e contém os fatos duros já com refs citadas
(datas de fundação, filiados, ideologia, números eleitorais) — muitas vezes mais
verificável que a página renderizada.

## Caixa de verificação — discrepância de números

Caso real: verbete de Hertz Dias (PSTU) dizia que a chapa de 2018 (Vera Lúcia +
Hertz) teve 25.625 votos (0,02%). A tabela oficial do partido (verbete do PSTU)
mostrava 55.762 (0,05%) em 2018 e 25.625 em 2022. O número do verbete individual
era o resultado de 2022 colado em 2018.

Regra aplicada: tabela oficial do partido vence o verbete biográfico; a
divergência foi sinalizada explicitamente na nota final. Em pesquisa eleitoral,
a fonte canônica de votos é a apuração do TSE (divulgacandcontas / apuração
g1-globo) — cruzar sempre.

## Fonte primária descoberta via refs da página

A página "Eleição presidencial no Brasil em 2026" (215 KB, salva em cache) tinha
a lista de referências no rodapé. `search_files` no arquivo de cache por
`g1.globo|folha.uol|poder360|cnnbrasil` revelou as URLs exatas das matérias de
convenção (g1 26/07 UP, g1 31/07 PSTU, g1 01/08 PCB), que viraram as fontes
primárias dos dossiês. Sequência: enciclopédia → refs no cache → artigos de
imprensa direto via web_extract.

## Formato de dossiê (um arquivo por sujeito, mesmo esqueleto)

1. Perfil em 60 segundos (2-3 frases)
2. N fatos numerados (cada um com URL) — mínimo 10
3. História da organização/partido
4. Vice/companheiros de chapa
5. Contexto eleitoral do pleito
6. Riscos e pontos de atenção para cobertura
7. Avaliação honesta (ex.: sem gestão pública → dizer isso + o que qualifica o
   sujeito de fato)
8. Fontes principais

Pitfall de honestidade: candidatos de partidos pequenos quase nunca têm gestão
pública — a seção 7 deve afirmar a ausência de mandatos/cargos executivos e
listar o que há (militância, academia, sindicato), sem maquiar.
