# Fallback de APIs acadêmicas + recuperação de subagentes (validado 15/08/2026)

Sessão de referência: deep-research sobre valuation (web_search fora em todos os contextos, Semantic Scholar 429, 3 subagentes timeout em 600s). Tudo abaixo foi executado e funcionou.

## 1. OpenAlex — metadados de papers (fallback nº 1)

```bash
# Busca por relevância (título+abstract)
curl -s 'https://api.openalex.org/works?search=valuation%20biotechnology%20rNPV&per-page=5&select=display_name,publication_year,cited_by_count,doi'
# Busca por título (filter title.search é mais preciso para papers conhecidos)
curl -s 'https://api.openalex.org/works?filter=title.search:Cassimon%20pharmaceutical%20real%20options&per-page=5&select=display_name,publication_year,cited_by_count,doi'
# Por DOI — inclui abstract_inverted_index e authorships
curl -s 'https://api.openalex.org/works/doi:10.1038/nbt0901-813?select=display_name,publication_year,cited_by_count,abstract_inverted_index,authorships'
```

- Sem auth; 429 raros; mandar `-H 'User-Agent: research-script/1.0 (mailto:x@y)'`.
- `abstract_inverted_index` = `{palavra: [posições]}` — reconstruir: `' '.join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))`.
- Exemplo real: confirmou Stewart/Allison/Johnson 2001 (Nature Biotech, doi 10.1038/nbt0901-813, 106 citações) e Kellogg/Charnes/Demirer 1999 (real options biotech).

## 2. Europe PMC fullTextXML — texto completo quando PMC bloqueia

pmc.ncbi.nlm.nih.gov responde reCAPTCHA ao web_extract. O endpoint de texto completo da Europe PMC funciona:

```bash
curl -s -m 60 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6409418/fullTextXML' -o paper.xml
```

Parse útil:
```python
import re
xml = open('paper.xml', encoding='utf-8', errors='ignore').read()
text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', xml))
tables = re.findall(r'<table-wrap[^>]*>(.*?)</table-wrap>', xml, re.S)  # tabelas de dados
# frases com números: re.findall(r'[^.]*?(?:success rate|% )[^.]*\.', text)
```

Exemplo real: extraiu a Tabela 2 do Wong-Siah-Lo 2019 (POS por grupo terapêutico: oncologia 3,4%, global 13,8%, transições 66,4%/58,3%/59,0%) — o núcleo de dados de um modelo rNPV.

## 3. NCBI eutils — confirmação de PMID/PMC/DOI

```bash
curl -s 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=<query>&retmode=json'
curl -s 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<pmid>&retmode=json' | python3 -c "import json,sys; d=json.load(sys.stdin); [print(u, d['result'][u].get('title','')[:80]) for u in d['result'] if u!='uids']"
```

## 4. GitHub API — descoberta de repos quando web_search falha

```bash
curl -s 'https://api.github.com/search/repositories?q=valuation+skill&sort=stars&order=desc&per_page=5'
```

- Extrair com python (`json.loads`) e imprimir só `full_name`, `stargazers_count`, `updated_at[:10]`, `description` — o output cru estoura o limite do terminal (~50KB) em queries amplas.
- 8 queries em ~5s nesta sessão, sem rate-limit. GitHub API é a via mais confiável quando TODOS os motores de busca estão degradados.
- web_extract no próprio github.com também funciona bem para ler README/estrutura do repo (SKILL.md, skills/, scripts/).

## 5. Recuperação de subagentes timeout — live transcripts

Cada subagente grava um log append-only em:
```
/opt/data/cache/delegation/live/<delegation_id>/task-<N>.log
```
Contém: goal completo, todo do subagente, TODAS as chamadas de tool com resultados (web_extract às vezes com o conteúdo inteiro), caminhos de arquivos cacheados (`/opt/data/cache/web/<domain>-<hash>.md` — reler com read_file em vez de re-extrair), outputs de execute_code/terminal. Nesta sessão: 3 subagentes timeout (600s) → ~100 achados recuperados lendo os 3 logs (34KB, 9,7KB, 28KB). Ler os logs ANTES do state.db; mostrar onde cada agente parou evita re-pesquisar o que já foi coletado.

## 6. Padrões de URL de autoridade — finanças/valuation (domínio novo, validado 15/08/2026)

- **Damodaran (Stern/NYU)**: `pages.stern.nyu.edu/~adamodar/New_Home_Page/writing.html` (índice de papers); `pdfiles/papers/younggrowth.pdf` (Valuing Young, Start-up and Growth Companies, 2009 — texto completo extraível).
- **IPEV Valuation Guidelines**: `privateequityvaluation.com/Valuation-Guidelines` (seção early-stage: PWERM/OPM/CVM/hybrid, fatores qualitativos).
- **IVSC**: `ivsc.org`.
- **Nature Biotech** (paywall/JS) — usar OpenAlex para metadados, Europe PMC para open access.
- **Wikipedia en/pt**: infoboxes de empresas biotech trazem funding/exit (Beam ~US$1B pré-IPO; Prime Medicine deal BMS US$110M+US$3,5B; Verve adquirida pela Lilly) — bom para cases com números verificáveis.
- **BIO/Biomedtracker PDFs**: URLs de `bio.org/sites/default/files/...` frequentemente 404 — não confiar em links achados em busca; buscar alternativa (Europe PMC, papers, press releases) e marcar confiança.
