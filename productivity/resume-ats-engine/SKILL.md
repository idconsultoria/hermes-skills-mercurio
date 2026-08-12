---
name: resume-ats-engine
description: "Currículo ATS: desenha p/ vaga, exporta .docx/PDF e avalia.

Carregue esta skill quando for otimizar um currículo para uma vaga específica — desenho direcionado ao ATS, exportação .docx/PDF e avaliação 0-10 da adequação. Integra docx, pdf, html-to-pdf-chromium e html-report-hermes."
version: 1.1.0
author: Hermes (sintetizado de Paramchoudhary/ResumeSkills, varunr89/resume-tailoring-skill, dabydat/resume-builder-skill, ComposioHQ, claude-office-skills)
license: MIT
platforms: [linux]
type: Orchestrator
timestamp: 2026-08-11T00:00:00Z
metadata:
  hermes:
    tags: [resume, cv, curriculum, ats, job-application, career, cover-letter]
    category: productivity
    related_skills: [docx, pdf, html-to-pdf-chromium, html-report-hermes, agy]
---

# Resume ATS Engine — currículo otimizado por vaga + avaliação 0-10

Desenha um currículo profissional ATS-otimizado para **uma vaga específica**, a partir de **quaisquer informações que o usuário fornecer** (texto, arquivo .md/.docx/.pdf, URL de vaga), exporta em **.docx e PDF**, e entrega uma **avaliação criteriosa (nota 0-10 em 7 eixos)** sobre a força do currículo para aquela vaga, com **análise da concorrência esperada** e do posicionamento do candidato frente a ela.

**Princípio central (herdado de todos os repos-fontes):** truth-preserving optimization. Nunca fabricar experiência, métrica ou tecnologia. Tailoring = reordenar, re-enfatizar e reformular o que existe — nunca inventar. O candidato será perguntado sobre tudo no currículo em entrevista.

## When to Use (Quando usar)

- Usuário pede currículo/CV/resume novo, otimizado, ATS-friendly, "para essa vaga"
- Usuário tem uma vaga (texto, URL ou arquivo) e quer currículo sob medida + saber se vale aplicar
- Usuário quer avaliar o currículo atual contra uma vaga ("nota", "quão competitivo estou?")

## Pré-requisitos (uma vez)

```bash
# venv dedicado — DOCX via python-docx, PDF via WeasyPrint (ARM64-safe), verificação via pypdf
uv venv /opt/data/.venvs/resume-ats --python 3.13
uv pip install --python /opt/data/.venvs/resume-ats/bin/python python-docx weasyprint pypdf
```
Se WeasyPrint falhar na instalação: usar a skill `html-to-pdf-chromium` (fallback WeasyPrint) ou `soffice --headless --convert-to pdf` se LibreOffice existir.

## Fluxo (5 fases)

### Fase 0 — Intake (qualquer formato de entrada)

Colete **vaga** e **informações do candidato**:

- **Vaga**: texto colado, URL (usar `web_extract`) ou arquivo (`.docx`/`.pdf` — `read_file` extrai texto).
- **Candidato**: texto livre, arquivo (`.md`, `.docx`, `.pdf`), export do LinkedIn, ou respostas curtas. Se o usuário não der nada estruturado, faça perguntas direcionadas (máx. 1 rodada) sobre: contato, cargo atual, últimos 2-3 empregos (empresa, período, 2-3 entregas com números se souber), stack/ferramentas, formação, certificações.
- **Se faltarem dados críticos** (ex.: zero experiência informada, sem contato): gere mesmo assim com placeholders `[INFORMAR: ...]` e **penalize no eixo Completude** — não trave o fluxo.

### Fase 1 — Estruturar o candidato

Monte o JSON de entrada do script (schema em `scripts/build_resume.py`):

```json
{
  "meta": {"name": "", "email": "", "phone": "", "location": "", "linkedin": "", "github": "", "website": "", "target_title": "", "lang": "pt|en"},
  "summary": "",
  "skills_groups": [{"title": "", "items": []}],
  "experience": [{"title": "", "company": "", "location": "", "dates": "", "bullets": []}],
  "projects": [{"name": "", "description": "", "link": ""}],
  "education": [{"degree": "", "school": "", "dates": ""}],
  "certifications": []
}
```

Regras de estruturação (detalhe em `references/best-practices.md`):
- Bullets sempre com **verbo de ação no passado + o que fez + contexto técnico/domínio + impacto mensurável** (fórmula XYZ/STAR condensada). Se o usuário não deu número, estime apenas com `~`/faixa e sinalize no relatório — ou peça.
- Para vagas de tecnologia: seção Skills **no topo**, logo após contato. Para outras áreas: Resumo curto (2-3 linhas) primeiro, Skills depois.
- Educação no fim para quem tem 3+ anos de experiência; no topo para júnior/estudante.
- Idioma do currículo = idioma da vaga (pt→pt, en→en). Termos técnicos ficam em inglês.

### Fase 2 — Analisar a vaga

Use `references/analise-vaga.md`. Extraia do JD:

- **P1 — Obrigatórios** (deal-breakers): anos de experiência, stack obrigatória, formação, certificações.
- **P2 — Importantes** (fortemente desejados). **P3 — Bônus** (nice-to-have).
- **Soft skills enfatizadas**, **termos de domínio/indústria**, **sinais de senioridade** (mentoria, arquitetura, liderança).
- **Sinais de concorrência** (para Fase 4): senioridade, genericidade do stack, modalidade, localização, salário, popularidade da empresa. Se a vaga for URL, pesquise a empresa (site, LinkedIn) para calibrar.

### Fase 3 — Desenhar o currículo (tailoring truth-preserving)

Aplique `references/best-practices.md`:
1. **Reordenar, não reescrever**: bullets mais relevantes à vaga primeiro em cada cargo.
2. **Espelhar a linguagem do JD**: se pedem "CI/CD", use "CI/CD" (e não só "continuous integration"). Mesmo termo, sem keyword stuffing.
3. **Skills em primeiro** (tech), agrupadas e liderando pela categoria mais relevante à vaga.
4. **Estrutura ATS-rígida**: single column, sem tabelas, sem imagens/logos, sem headers/footers com contato, seções com títulos padrão ("Experience", "Skills", "Education"), fonte Calibri/Arial 10-11pt, margens 0.75", 1 página (<10 anos) ou 2 (sênior).
5. **Checklist final** de `references/best-practices.md` antes de exportar (sem pronomes, sem períodos no fim de bullets, datas com en dash, URLs limpas sem "https://").

> **Regra de design (validada com o usuário):** o **currículo é SEMPRE um documento formal** (padrão ATS: single column, sem cards, sem cores de fundo, sem elementos decorativos), independentemente da área do candidato. A **criatividade/estética caprichada vai na CARTA DE APRESENTAÇÃO** (ver Fase 6) — especialmente para profissionais de áreas criativas (comunicação, marketing, design, influência), onde a carta é a amostra de estilo.

### Fase 4 — Avaliar (nota 0-10 em 7 eixos + concorrência)

Siga `references/rubrica-avaliacao.md` — a rubrica completa com critérios e faixas:

| Eixo | Peso |
|---|---|
| E1 Match com a vaga (P1/P2/P3 + keywords) | 25% |
| E2 Impacto e quantificação (bullets) | 20% |
| E3 Estrutura e compatibilidade ATS | 15% |
| E4 Conteúdo e completude (lacunas) | 15% |
| E5 Posicionamento e senioridade | 10% |
| E6 Escaneabilidade (5-segundo scan) | 10% |
| E7 Idioma e apresentação | 5% |

- **Nota final = Σ (peso × nota)** — justifique cada nota com evidência do currículo vs JD.
- **Análise de concorrência**: estime o nível esperado de disputa (Muito Alta/Alta/Média/Baixa) a partir dos sinais da vaga + estime o **percentil do candidato** (top 5%, top 20%...) cruzando a nota final com o perfil típico de quem disputa.
- **Verdict**: aplicar forte / aplicar com ajustes / repensar (faixas de Match: 75-89% excelente fit; 60-74% bom com cover letter forte; <60% stretch).
- Gere `avaliacao.md` com: tabela eixos×notas×pesos, justificativas, pontos fortes, pontos fracos, concorrência esperada, competitividade, top-5 ações para subir a nota.

### Fase 5 — Exportar e verificar

1. Salve o JSON em `/opt/data/tmp/resume_<nome>.json` (**nunca em /tmp** — fora do HERMES_WRITE_SAFE_ROOT, MEDIA quebra).
2. Rode o gerador:
   ```bash
   /opt/data/.venvs/resume-ats/bin/python /opt/data/skills/productivity/resume-ats-engine/scripts/build_resume.py \
     /opt/data/tmp/resume_<nome>.json /opt/data/tmp/resume_<nome>
   ```
   Gera `<base>.docx`, `<base>.pdf` e **verifica automaticamente** que o PDF tem texto extraível (pypdf) e que o nome do candidato aparece nele — falha com aviso se o PDF não for ATS-parseável.
3. **Confira que os 3 arquivos existem** (`ls -lh`) antes de referenciar no MEDIA — path inexistente é ignorado silenciosamente e o usuário não recebe nada.
4. Confira a contagem de páginas (o script reporta) — 1 página para júnior/mid, máx 2.
5. Entregue via MEDIA: `.docx` (para editar), `.pdf` (para enviar), `avaliacao.md` (relatório). No WhatsApp/Telegram, liste as 3 linhas `MEDIA:` no final; se a plataforma aceitar só 1, mande em mensagens separadas.

## Fase 6 — Carta de apresentação (opcional, agy → HTML → PDF)

Quando o usuário pedir carta de apresentação/cover letter (ou o verdict recomendar "aplicar com cover letter forte"):

1. **Montar o prompt** com dados do candidato + vaga seguindo `references/cover-letter-prompt.md` (template + design system premium; prompt < 25KB).
2. **Executar o agy** conforme a skill `agy`: `--print` via `ssh oracle-host`, SEMPRE em background (`terminal(background=true, notify_on_complete=true)`), sem timeout. Acompanhar com `process(action='poll')`.
3. **Trazer o HTML** do host (agy grava arquivos no disco do host — conferir o caminho pedido no prompt) para `/opt/data/`.
4. **Renderizar para PDF** — **preferir `--chromium`** (padrão da IAF newsletter: Chromium headless no host via ssh, render fiel ao navegador — drop caps, chips, ornamentos; o WeasyPrint degrada CSS moderno):
   ```bash
   /opt/data/.venvs/resume-ats/bin/python /opt/data/skills/productivity/resume-ats-engine/scripts/render_html_to_pdf.py \
     /opt/data/carta_<nome>.html /opt/data/tmp/carta_<nome>.pdf --chromium
   ```
   O script sanitiza Google Fonts, injeta compactação de 1 página e valida contagem + texto extraível. Sem `--chromium`, usa WeasyPrint com auto-fix (fallback).
5. **Entregar**: PDF via MEDIA. Se o usuário quiser o HTML, ZIPAR (Telegram descarta .html silenciosamente).
6. **Fallback** se agy falhar (cota/timeout): prompt fracionado → HTML manual com os tokens do template → Pi best (GLM 5.2). Detalhes em `references/cover-letter-prompt.md`.

### Carta criativa (profissionais de áreas criativas)

Para profissionais criativos (comunicação, marketing, design, influência, jornalismo), a carta pode — e deve — ser **visualmente caprichada**: é a amostra de estilo e o primeiro impacto. Use `references/carta-criativa.md`:

1. **Pesquise referências visuais antes** (Pinterest, Dribbble, Behance): layouts editoriais, letterheads elegantes, tipografia expressiva. Baixe 2-4 imagens e envie ao host (`/home/ubuntu/refs/`) — o agy aceita imagens como input.
2. **Injete as referências no prompt**: descreva o que cada referência ensina (hierarquia tipográfica, uso de cor, composição) + caminhos das imagens no host.
3. **Peça explicitamente para caprichar**: design editorial premium, identidade do candidato (ex.: paleta do media kit), cards/boxes de números permitidos aqui (diferente do currículo), assinatura elegante.
4. Renderize com `render_html_to_pdf.py` (valida 1 página + texto extraível) e inspecione visualmente antes de entregar — carta feia é pior que carta simples.

## Saída para o usuário

No chat: resumo de 4-5 linhas — nota final, eixo mais forte, eixo mais fraco, nível de concorrência da vaga e verdict. Detalhe completo no `avaliacao.md` (tabela estruturada — o usuário prefere tabelas em arquivo, não inline).

## Verificação de qualidade (antes de entregar)

- [ ] PDF tem texto extraível (script já valida)
- [ ] Nenhum bullet inventado — tudo rastreável ao input do usuário
- [ ] Bullets sem pronomes, sem "Responsible for", sem clichês (spearheaded, leveraged, utilized)
- [ ] Skills e bullets espelham a linguagem do JD
- [ ] 1-2 páginas, margens 0.75", fonte padrão, sem tabelas/imagens
- [ ] Currículo SEMPRE formal (sem cards, sem cores de fundo, sem decoração) — criatividade só na carta
- [ ] Carta criativa (se aplicável): design intencional (cores/tipografia/boxes de números) E texto ainda extraível no PDF
- [ ] Contato no corpo (nunca em header/footer)
- [ ] Datas consistentes (ex.: "2021 – Present")

## Pitfalls

- **Nunca** preencher lacuna de métrica com número inventado — use estimativa sinalizada ou `[INFORMAR]` e desconte no E4.
- **Não** fazer currículo "genérico bonito" sem referência à vaga — o valor está no match.
- **Não** usar tabelas/colunas/multicolunas no DOCX — quebra parse de ATS legado.
- **Currículo NUNCA com cards/cores/decoração** — o usuário validou: criatividade só na carta.
- WeasyPrint exige fontes do sistema: use `DejaVu Sans`/`DejaVu Serif` no HTML do PDF (Calibri fica só no DOCX).
- Se o usuário colar texto com formatação estranha, normalize antes de estruturar (sem bullets aninhados, sem listas de 20 itens por cargo — máx. 5-6 bullets por cargo).
- **Nunca `skill_manage(action='delete')` na skill inteira para remover um arquivo** — use `remove_file` com `file_path`. (Aconteceu em 11/08/2026: delete acidental da skill inteira.)
