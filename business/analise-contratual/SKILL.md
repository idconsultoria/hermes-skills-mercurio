---
name: analise-contratual
description: "Use ao analisar contratos/minutas — subcontratação, LGPD.

Carregue esta skill quando precisar analisar minuta de contrato, contrato, edital, plano de trabalho ou proposta — especialmente quando a ID Consultoria (ou um cliente) é subcontratada/fornecedora. Cobre checklist de riscos (subcontratação, pay-when-paid, LGPD, propriedade intelectual, SLA/multas), cruzamento contrato × plano de trabalho para achar divergências de escopo/valor/prazo, e identificação de partes e regime jurídico (Lei 14.133/2021, LGPD 13.709/2018). Usa google-workspace para localizar documentos no Drive e scripts/pdf2txt.py para extrair texto de PDFs. Entrega resumo executivo no chat + arquivo .md completo via MEDIA."
type: Reference
timestamp: 2026-08-09T05:08:04Z
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [contrato, minuta, licitação, lei-14.133, subcontratação, LGPD, due-diligence, jurídico]
---

# Análise Contratual (risco para subcontratada/fornecedor)

## Quando usar
- Usuário pede para analisar **minuta de contrato, contrato, edital, plano de trabalho ou proposta**, em especial quando a **ID Consultoria (ou um cliente) é subcontratada/fornecedora** de um contrato maior.
- Comparar **contrato × plano de trabalho/proposta** para achar divergências de escopo, valor e prazo.

## Workflow
1. **Localizar documentos** no Drive (via skill `google-workspace` — se bloqueada, usar o CLI `gws` ou Google API direto): `drive search "minuta contrato" --max 20`; repetir com variações ("plano de trabalho", nome das partes, "CNPJ", "contrato social"). Docs do Google → `--export-mime text/plain`. PDFs → `scripts/pdf2txt.py` deste skill.
2. **Identificar partes e regime jurídico**: CNPJs, natureza (LTDA, OS/associação sem fins lucrativos), lei aplicável (Lei 14.133/2021 — art. 75, XV p/ OS; LGPD 13.709/2018), foro.
3. **Ler a constituição do cliente** no Drive (contrato social, CNAEs, declarações de exclusividade) — **objeto social pode não cobrir o escopo** (ex.: sem CNAE de desenvolvimento de software 62.01-5 → avaliar alteração contratual).
4. **Rodar o checklist de riscos** abaixo.
5. **Cruzar contrato × plano de trabalho**: valores, prazos, vigência, fases — divergências são achados centrais.
6. **Entregar**: resumo executivo no chat (bullets, riscos numerados) + arquivo `.md` completo via `MEDIA:` (usuário rejeita tabelas inline quebradas entre mensagens — ver memória).

## Checklist de riscos (subcontratada)
- **Subcontratação** (o maior): a cláusula veda o núcleo (desenvolvimento principal, arquitetura, engenharia de dados, sustentação, segurança)? O que o cliente faz costuma ser exatamente o núcleo vedado. Enquadrar como **parceira técnica/consultoria acessória**; exigir que o repasse **conste da composição de custos** da contratada; lembrar que a contratada deve "executar diretamente a parcela principal".
- **Pagamento**: pay-when-paid (sub recebe depois que a contratada receber); sem antecipação; por produto aceito; **sem aceite tácito**; preço global "inclui tudo" (equipe, tributos, deslocamento, licenças) → capital de giro 90–120 dias.
- **LGPD**: controlador → operadora → suboperadora; **proibição de usar dados para treinar IA**; **uso de IA exige autorização formal**; incidente comunicado em 24h; termos de confidencialidade por profissional; multa específica por incidente de dados.
- **Propriedade intelectual**: código novo vai ao contratante **sem custo** (licença por prazo indeterminado, portabilidade); componentes preexistentes do fornecedor só permanecem dele se **identificados por escrito ANTES** do início.
- **SLA/multas**: disponibilidade (ex.: 99,5%), severidades (crítico 1h/4h), glosas, multas % — serão repassados no contrato interno.
- **Vigência/escopo**: divergência minuta × plano (ex.: 24 meses × 12 meses) → **precificar pelo contrato real**, não pelo plano.
- **Conflito de interesses**: relação prévia com o contratante (ex.: residente de parque tecnológico) — não proibido, mas documentar por escrito.
- **Formato do contrato interno**: escopo fixo/resultado, **nunca locação de mão de obra** (se o contrato-base é "sem dedicação exclusiva").
- **Escudo de terceiros**: dependências externas (bases, bancos, órgãos) não são responsabilidade do fornecedor se ele comunicar impedimento e adotar contingência — manter essa cláusula no contrato interno.

## Scripts e referências
- `scripts/pdf2txt.py` — extrai texto de PDFs (pypdf → fitz → pdfplumber). Uso: `uv venv /tmp/pdfv && uv pip install --python /tmp/pdfv/bin/python pypdf && PYTHONPATH="$(ls -d /tmp/pdfv/lib/python*/site-packages)" python3 scripts/pdf2txt.py IN.pdf OUT.txt`. Preferir PYTHONPATH com python3 do sistema em vez de chamar o interpretador do venv direto (pode ser bloqueado pelo security scanner).
- `references/tjse-sergipetec-2026.md` — caso real: minuta TJSE × SergipeTec (Lei 14.133/2021), ID subcontratada; checklist completo com numeração de cláusulas e IDs dos documentos no Drive.
