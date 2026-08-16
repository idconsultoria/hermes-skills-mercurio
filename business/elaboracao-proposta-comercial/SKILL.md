---
name: elaboracao-proposta-comercial
description: "ID Consultoria commercial proposals — client context to branded HTML + minuta.

Load this skill when creating a commercial proposal from client context (documents, negotiation messages, meeting minutes). Builds the branded HTML proposal by editing the brand template directly, and produces a Google Docs contract minuta in the Minutas subfolder, preserving first/last pages. Validates content incrementally with the user following the Guia de Princípios."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [proposta, consultoria, comercial, contrato, minuta, drive, docs, pdf]
    related_skills: [analise-contratual, google-workspace, research-report-standards]
type: Orchestrator
timestamp: 2026-08-14T06:30:00Z
---

# Elaboração de Proposta Comercial

## Overview

Pipeline completo para criar uma **proposta comercial** da ID Consultoria a partir de contexto do cliente (documentos, mensagens de negociação, atas de reunião). O processo é **passo-a-passo com validação do usuário**: o conteúdo é construído e validado incrementalmente seguindo o Guia de Princípios (references/guia-principios.md). A entrega final tem dois artefatos:

1. **HTML da proposta** — o agente EDITA o modelo de marca (templates/modelo_proposta.html) diretamente, como agente de IA, adaptando cada seção ao pedido do usuário. O modelo é apenas **referência de marca/estrutura, não retrato final** — a proposta deve sair pronta e diferente, moldada ao cliente e ao contexto, não um simples preenchimento de placeholders.
2. **Link do Google Docs com a minuta do contrato** — cópia de um contrato-modelo existente, editada para a proposta, salva na subpasta "Minutas" (references/contratos-drive.md). **Preservar a primeira e última páginas** do Doc copiado (são capa e contracapa).

## When to Use

- Usuário pede para criar/elaborar uma proposta comercial para um cliente.
- Usuário fornece contexto (PDFs, documentos, mensagens de negociação, atas) e quer a proposta + minuta.
- Reusar o modelo de proposta da marca (o deck estilo Minuzzo) para um novo cliente.

**Não usar para:** contratos já assinados (use analise-contratual), propostas de outras empresas, ou conteúdo que não seja da ID Consultoria.

## Pipeline

### Passo 0 — Coletar contexto

Receber do usuário (arquivos, mensagens, links) e extrair os dados essenciais:

| Dado | Onde usar |
|---|---|
| Nome do cliente ({{CLIENTE_NOME}}) | capa, resumo, final |
| Logo do cliente ({{CLIENTE_LOGO_URL}}) | capa |
| Título ({{TITULO_PROPOSTA}}) | capa |
| Subtítulo ({{SUB_TITULO_PROPOSTA}}) | capa |
| Escopo / entregáveis / exclusões | slides Escopo, Resumo |
| Metodologia e fases | slide Metodologia |
| Valores, pacotes, desconto | slides Investimento |
| Condições de pagamento e validade | Condições, Resumo, final |
| Casos/depoimentos relevantes | slide Quem já confiou (usar portfolio, references/portfolio.md) |

### Passo 1 — Rascunho do conteúdo (uma seção por vez)

Seguir o **Guia de Princípios** (references/guia-principios.md): storytelling problema → solução → prova → preço; ROI antes do preço; 3 opções com o médio recomendado; escopo com exclusões; responsabilidades de cada parte; validade 14–30 dias.

**Regra do usuário:** UMA coisa de cada vez. Propor o rascunho seção a seção e **aguardar ok explícito** antes de prosseguir. Nunca gerar o documento inteiro sem validação intermediária.

- Validar com o usuário: título, resumo executivo (com preço), entendimento do desafio, escopo (incluindo fora do escopo), investimento (3 opções + desconto), condições comerciais.
- Preencher os placeholders correspondentes no mapa (references/placeholders.md).

### Passo 2 — Editar o HTML como agente (NÃO preencher via script)

Copiar o modelo para o diretório de trabalho e **editar o HTML inteiro como agente de IA**:

```bash
mkdir -p /opt/data/work/proposta_<cliente>
cp skills/business/elaboracao-proposta-comercial/templates/modelo_proposta.html \
   /opt/data/work/proposta_<cliente>/Proposta_<cliente>.html
```

Regras de edição:
- **O template é referência de marca (cores, tipografia, estrutura), não retrato final.** Entregar uma proposta pronta e diferente, moldada ao que o usuário pediu: trocar seções, reorganizar slides, ajustar a narrativa, incluir/remover blocos conforme o contexto do cliente.
- Substituir os placeholders `{{...}}` pelos valores validados (mapa em references/placeholders.md).
- **Prova social real**: usar `references/portfolio.md` (clientes com logos em `assets/clientes/`) — nunca inventar cases.
- Manter a identidade: fundo escuro + teal `#4AC6D3` (diamond no canto), capa/contracapa, tipografia Neulis/Nunito.
- O `scripts/preencher_proposta.py` existe como utilitário, mas **o fluxo padrão é edição manual pelo agente** (permite entregar algo único, não uma cópia mecânica).

Verificar visualmente no navegador (browser_navigate no arquivo local) — zero overflow, cores, alinhamento, logos dos clientes com contraste adequado.

### Passo 3 — Renderizar PDF (quando o usuário pedir PDF)

O usuário pode validar o HTML diretamente ou pedir PDF. Se PDF:

```bash
node scripts/render_pdf.mjs /opt/data/work/proposta_<cliente>/Proposta_<cliente>.html \
  /opt/data/work/proposta_<cliente>/Proposta_<cliente>.pdf
```

Requisito: Chromium do Playwright instalado. Instalar com:
```bash
mkdir -p /opt/data/.playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright npx playwright install chromium
```
⚠️ O caminho padrão `/opt/hermes/.playwright` NÃO tem permissão de escrita — usar `/opt/data/.playwright`. O PDF sai com 1 página por slide (1920×1080).

### Passo 4 — Criar a minuta no Google Docs

1. Escolher o contrato-modelo base (references/contratos-drive.md): preferir "Modelo de Contrato de Consultoria de Escopo Fixo" para projetos com escopo definido, ou "Modelo de Contrato de Consultoria Ágil" para retainer/contínuo.
2. Copiar o Doc (Drive API `files.copy`) para a subpasta **Minutas** (ID em references/contratos-drive.md).
3. Editar o corpo via Docs API: **preservar a primeira e última páginas** (capa e contracapa — não tocar nelas); substituir dados do cliente (qualificação da CONTRATANTE), escopo (Cláusula 2), revisões, remuneração (Cláusula 8 — valores e parcelas), prazo, vigência e demais cláusulas conforme a proposta.
4. Compartilhar o link (o usuário pede o link; verificar permissão de acesso).
5. Confirmar com o usuário antes de qualquer modificação no Docs.

### Passo 5 — Entregar

- Enviar o **HTML** ao usuário (MEDIA ou navegador) — artefato principal, pronto e diferente do modelo.
- Enviar o **PDF** ao usuário se solicitado (Telegram via Bot API ou MEDIA conforme plataforma).
- Enviar o **link do Google Docs** da minuta.
- Resumo final: o que foi entregue, onde está a minuta, próximos passos (apresentação ao vivo, follow-up).

## References

- `references/guia-principios.md` — 12 princípios de elaboração (baseado em pesquisa: HBR, RAIN, McKinsey SCR, GBB, etc.). **Conteúdo deve seguir este guia.**
- `references/placeholders.md` — mapa completo dos placeholders do modelo HTML.
- `references/contratos-drive.md` — pasta do Drive, IDs dos contratos-modelo, subpasta Minutas, instruções de cópia e edição.
- `references/portfolio.md` — cases, serviços e **clientes reais** da ID (site + apresentação Pazion) para prova social e seção "Quem já confiou".
- `assets/clientes/` — logos de clientes já atendidos (XP Investimentos, Santa Maria, OxPay, Emerge, Ravello) extraídas do pitch Pazion; usar na prova social.
- `templates/modelo_proposta.html` — modelo HTML de marca com placeholders (fontes, fundos e logos embutidos). **Referência de marca/estrutura, não retrato final — o agente edita e adapta.**
- `scripts/preencher_proposta.py` — utilitário opcional de preenchimento (fluxo padrão: edição manual pelo agente).
- `scripts/render_pdf.mjs` — renderiza HTML → PDF via Playwright/Chromium.

## Common Pitfalls

1. **Gerar tudo de uma vez.** O usuário quer validação passo-a-passo (UMA coisa de cada vez). Rascunho por seção, aguarda ok.
2. **Usar o template como retrato final.** O modelo é referência de marca — a proposta deve sair **editada e única**, adaptada ao pedido do usuário, não uma cópia mecânica com placeholders trocados. Editar o HTML como agente; `preencher_proposta.py` é só utilitário.
3. **Não preservar capa/contracapa do contrato.** Ao copiar o Doc-modelo, editar apenas o corpo (cláusulas), nunca a primeira/última página.
4. **Valores inconsistentes entre proposta e minuta.** A remuneração/condições da minuta devem espelhar exatamente os valores e condições da proposta.
5. **Prova social vazia ou inventada.** Usar cases/clientes REAIS do portfolio (references/portfolio.md) com logos em `assets/clientes/` e métricas; nunca inventar resultados ou logos.
6. **Esquecer a validade (14–30 dias)** na proposta, no resumo executivo e na minuta.
7. **HTML sem verificação.** Sempre abrir o HTML editado no navegador (browser_navigate) e conferir overflow/cores antes de entregar/gerar PDF.
8. **Fundo/ícone errado por slide.** O slide de fundo teal (Resumo Executivo) usa destaque `#005465`; os demais slides de fundo escuro usam teal `#4AC6D3` (diamond do canto). Não inverter.
9. **Subpasta errada no Drive.** A minuta vai em `Minutas` (dentro de "1.1.2. Modelos de Contrato"), não na raiz.
10. **Citar cliente do portfolio sem contexto.** Escolher 1–3 clientes RELEVANTES ao projeto (ex.: fintech → OxPay; varejo/construção → Santa Maria/Ravello; indústria → Heineken). Não listar todos os 9 de uma vez.

## Verification Checklist

- [ ] Conteúdo validado seção a seção com o usuário (ok explícito)
- [ ] HTML editado pelo agente (modelo como referência, não retrato final) — proposta única, adaptada ao pedido
- [ ] Todos os placeholders preenchidos (grep por `{{` no HTML final retorna 0)
- [ ] Prova social com clientes reais (references/portfolio.md) e logos de `assets/clientes/` quando aplicável
- [ ] HTML conferido no navegador: zero overflow, cores corretas por slide
- [ ] PDF gerado com 1 página por slide (quando solicitado)
- [ ] Minuta criada como cópia do contrato-modelo na subpasta Minutas
- [ ] Primeira e última páginas do Doc preservadas
- [ ] Valores/condições da minuta = valores da proposta
- [ ] Link do Docs compartilhado e entregue
