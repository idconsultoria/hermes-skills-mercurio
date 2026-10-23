# Casos completos com artefatos brutos simulados (para especialista de domínio)

**Contexto:** no ciclo CFP IA (ago/2026), o usuário exigiu que os "casos completos" de usuários (insumo para o Igor, CFP certificado) fossem construídos com **artefatos brutos simulados idênticos aos que o usuário subiria no app** — não apenas resumos de orçamento. Requisito literal: *"Os arquivos de cada usuário das entrevistas devem ser os mesmos que ele subiria se usasse a aplicação como fonte. Simulações de extratos bancários, rascunhos de contratos com instituições financeiras, etc. Tudo para traçar o caso mais realista possível (de forma simplificada) para que um CFP real pudesse trabalhar no caso."*

## Padrão por caso (3 arquivos HTML → PDF por usuário)

| Arquivo | Conteúdo |
|---------|----------|
| `casoN-extrato-bancario.html` | Extrato de 3 meses (banco fictício): receitas (salário, PJ), despesas coerentes com o orçamento CS/EV/SD, saldo acumulado linha a linha (pode ficar negativo no 3º mês), categorias sugeridas (supermercado/alimentação/transporte/lazer/moradia/saúde/dívida/renda) |
| `casoN-fatura-cartao.html` | Fatura (bandeira fictícia): lançamentos, total, valor mínimo (15%), aviso de rotativo quando aplicável, juros do rotativo do mês anterior |
| `casoN-contratos.html` | Empréstimos/financiamentos/parcelamentos com CET, juros a.m., saldo devedor; resumo do rotativo; planilha de investimentos (se houver) |

**Consistência obrigatória:** somas dos extratos/faturas DEVEM bater com os totais do orçamento do caso (`casos-completos.md`); saldo contínuo linha a linha; IE/SE/SR resultantes devem reproduzir o perfil calculado pelo motor.

## Regras de geração

- Gerar via **Pi cost** (DeepSeek v4 Flash) com prompt pedindo HTML single-file embutindo o design system temporário (`cat product/design-system-temporario.html` antes) — zero emojis, tabelas `.table-wrap > table`.
- Simplificar sem perder realismo: 15–25 lançamentos/mês no extrato; 10–15 na fatura.
- Se um número nominal dos artefatos divergir da dívida "estimada" da entrevista (ex.: soma dos saldos R$ 6.600 vs "~R$ 8.000" declarado), **registrar a divergência no README** para o especialista reconciliar — não silenciar.

## PDF para o Drive (WeasyPrint — Oracle ARM64)

Chromium x86 falha com `Exec format error` em ARM64 (ver skill `html-to-pdf-chromium`). Usar WeasyPrint:

```python
# venv: uv venv /opt/data/venvs/pdf && uv pip install --python /opt/data/venvs/pdf/bin/python weasyprint
import re
content = open('caso1-extrato-bancario.html').read()
content = re.sub(r'<link[^>]*fonts\.googleapis[^>]*>', '', content)
content = re.sub(r'<link[^>]*fonts\.gstatic[^>]*>', '', content)
content = content.replace('Inter,', 'DejaVu Sans,').replace('JetBrains Mono,', 'DejaVu Sans Mono,')
content = content.replace("'Inter'", 'DejaVu Sans').replace('"Inter"', 'DejaVu Sans')
if 'print-color-adjust' not in content:
    content = content.replace('</style>', '* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }\n</style>')
open('caso1-extrato-bancario-weasy.html', 'w').write(content)

import weasyprint
weasyprint.HTML(filename='caso1-extrato-bancario-weasy.html').write_pdf('caso1-extrato-bancario.pdf')
```

Batch para N arquivos: loop sobre `caso*.html`, preparar `-weasy.html`, gerar `-weasy.html → .pdf`. Verificar visualmente 1 página no browser (`browser_navigate file://...` + snapshot) antes de subir.

## Entrega no Drive

- Criar pasta dedicada do parceiro: `$GAPI drive create-folder "Trabalho do Igor — ..." --parent <pasta-raiz-projeto>`
- Upload com nomes legíveis: `$GAPI drive upload caso1-extrato-bancario.pdf --name "Artefato Rafael A (Endividado) — Extrato Bancário" --parent <folder_id>`
- Compartilhar como writer (`--type anyone --role writer`) para o parceiro poder comentar.
- O **documento mestre do parceiro** (Google Docs, 1 único, didático, não extenso) lista as entregas dele, relevância e prazos — os PDFs são anexos de contexto. Nada de .md para o parceiro.

## Estrutura final no repo

```
product/management/
├── casos-completos.md          ← dados consolidados + motor aplicado (fonte)
├── casos-completos.html        ← premium (design system) — para PDF
├── casos-completos.pdf
└── artefatos/
    ├── README-artefatos.md     ← consistência numérica + divergências
    ├── caso1-extrato-bancario.html/.pdf
    ├── caso1-fatura-cartao.html/.pdf
    ├── caso1-contratos.html/.pdf
    ├── caso2-* / caso3-*
    └── (*-weasy.html = preparados para WeasyPrint; commitáveis)
```
