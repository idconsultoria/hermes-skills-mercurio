---
name: digital-clone-persona
description: "Create digital clone personas through deep web research — discover, extract, and

Load this skill when the user asks you to create an AI persona or \"clone digital\" of a real person through research. Combines deep-web reconnaissance with persona-crafting to produce a roleplayable character that can act as consultant, mentor, critic, or strategist in that person's voice."
triggers:
  - clone digital
  - digital clone
  - persona IA
  - AI persona
  - incorporar persona
  - deep research persona
metadata:
  related_skills: [deep-research, user-interview, product-pipeline]
type: Research
timestamp: 2026-06-14T05:15:09Z
---

# Digital Clone Persona

> **Core principle:** A digital clone is not a resume summary — it's a **behavioral and philosophical mirror**. You're not listing what the person did; you're capturing *how they think, speak, and decide*.

Load this skill when the user asks you to create an AI persona/"clone digital" of a real person through research. Combines deep-web reconnaissance with persona-crafting to produce a roleplayable character that can act as consultant, mentor, critic, or strategist in that person's voice.

---

## Pipeline Overview

```
Pedido: "Crie um clone digital de [Pessoa]"
   │
   ▼
[Phase 1] Multi-platform recon (web_search + browser)
   │         ├─ LinkedIn (headline, bio, experience, skills, recommendations)
   │         ├─ Portfolio (Behance, Dribbble, personal site, GitHub)
   │         ├─ Content (Medium, blog, Substack, YouTube, podcast appearances)
   │         ├─ Social (Instagram, Twitter/X, TikTok — bio + recent posts)
   │         ├─ Professional (Alura, Coursera, courses, certifications)
   │         ├─ Business (CNPJ, company sites, partnerships, Escavador)
   │         └─ News/press (awards, features, interviews)
   │
   ▼
[Phase 2] Extract & categorize findings
   │         ├─ Identity: name, origin, age, location, education
   │         ├─ Trajectory: career arc, key roles, companies, timeline
   │         ├─ Expertise: skills, domains, tools, methodologies
   │         ├─ Voice: speech patterns, catchphrases, register, humor
   │         ├─ Philosophy: core beliefs, decision frameworks, influences
   │         └─ Achievements: awards (e.g. Cannes Lions), recognitions
   │
   ▼
[Phase 3] Structure persona document
   │         ├─ Identity table
   │         ├─ Thinking framework (philosophy + reasoning dialect)
   │         ├─ Specialties & depth map
   │         ├─ Voice & communication style (with examples)
   │         ├─ Anti-persona (what they DON'T say/do)
   │         ├─ Modes of activation (critic / mentor / creator / strategist)
   │         └─ Reference list with source links
   │
   ▼
[Phase 4] Deliver as knowledge artifact
            ├─ Write to disk as a .md file
            ├─ Save a condensed version as a skill reference
            └─ Offer activation prompt
```

---

## Phase 1: Multi-Platform Recon

### Priority sources (in order of value):

| Source | Why | What to extract |
|--------|-----|-----------------|
| **LinkedIn** | Professional identity hub | Headline, bio ("E aí, meu hierofante..."), experience timeline, skills, recommendations, posts |
| **Behance / Portfolio** | Visual + case study evidence | Projects, tools used, design fields, quality level, process documentation |
| **Medium / Blog** | Unfiltered thinking | Writing style, depth of reflection, philosophy, language register |
| **Instagram / Twitter/X** | Personality + cultural taste | Bio text, content themes, tone, humor, communities |
| **Course platforms** (Alura, Coursera) | Confirmed skills | Completed courses, specializations, learning trajectory |
| **Company sites** | Current venture | Mission, positioning, services, team |
| **News/press** | Achievements | Awards (Cannes Lions, etc.), interviews, features |
| **Escavador / AboutCompany** | Legal/formal identity | Full name, CNPJ, partnerships, official roles |

### Recon techniques

- **LinkedIn blocked?** Search for Google/LinkedIn cached snippets. The headline and about-section text often appear in web search results even without a logged-in session.
- **Medium blocked by Cloudflare?** Try Google cache, or search for article title in quotes — the description from search results often contains the opening paragraph.
- **Instagram blocked?** The bio is indexed by Google — search `site:instagram.com "person name" bio`.
- **Behance never blocks.** Always a safe source. Navigate to profile, click into projects for tool/field tags.
- **Multiple profiles?** The person may have a professional Instagram (@taciobrito) and a personal one (@tacio_brito_). Check both — different data.

### When sources conflict

- LinkedIn headline > Behance bio > Instagram bio (professional declarations are more current on LinkedIn)
- Course completion dates on Alura/Coursera are factual — trust them over self-reported skill claims
- Cannes Lions mention in LinkedIn headline → search for confirmation in news/press (the user may be the only source)

---

## Phase 2: Extract & Categorize

### Identity profile template

```
Nome completo: [Full name as per legal/formal sources]
Naturalidade: [Hometown/region — e.g. Itabaiana, Sergipe]
Residência: [Current city, state]
Idade: [Age or range]
Formação: [Degrees, universities, specializations]
Empresa: [Current venture(s)]
Cargo atual: [Current title]
Premiações: [Awards with year — e.g. Cannes Lions 2023]
```

### Trajectory arc

Map a timeline of roles → no need for exact dates, but capture the arc:
```
- Started early (e.g. "design desde os 10 anos")
- Education pivot (e.g. Graphic Design → Anthropology → Org Psych)
- Career inflection point (e.g. agency → consultancy → founder)
- Peak achievement (e.g. Cannes Lions)
- Current focus (e.g. cultural consulting + AI)
```

### Voice extraction

Listen for **signature phrases** that no one else would say:

- LinkedIn headline that breaks convention (e.g. *"E aí, meu hierofante"*)
- Recurring themes (Star Trek, sci-fi, Harry Potter house)
- Degree of formality (formal? casual? regional slang?)
- Humor type (ironic? dry? dad jokes? nerdy references?)
- Pet peeve topics they'd push back on

Collect at least 3 direct quotes from their writing/posts. These are the most valuable input for voice crafting.

### Philosophy distillation

From their writing, professional choices, and stated beliefs, extract:

- **Core thesis** — the idea that connects all their work
- **Decision framework** — how they decide between options
- **What they reject** — anti-patterns, design crimes, bad advice
- **Influences** — authors, thinkers, designers, works they reference

---

## Phase 3: Structure the Persona Document

### Required sections

```
## 📋 Identidade
[Tabela com os dados-chave]

## 🧠 Estrutura de Pensamento
- Núcleo filosófico
- Dialeto de raciocínio (steps: sonda → questiona → conecta → materializa → revisa)

## 🎯 Especialidades
- Domain 1: [depth + proof]
- Domain 2: [depth + proof]

## 🗣 Voz e Estilo de Comunicação
- Como fala (regionalidade, registro, humor)
- Padrões de fala (3-5 exemplos de frases típicas)
- O que NÃO diz (anti-patterns)

## 🛠 Modos de Ativação
### Modo [Crítico / Mentor / Criador / Estrategista]
Atua como [descrição do papel].
Prompt de ativação: [frase para ligar o modo]

## ⚠️ Anti-persona
[O que o clone NÃO é — limites para não quebrar o personagem]

## 📚 Referências que alimentam o repertório
[Livros, autores, obras, cultura pop]

## 🔗 Links vivos
[Todas as fontes consultadas]

## 📝 Histórico da pesquisa (opcional)
[Data | Fonte | Achado]
```

### Voice examples — embed real quotes

Use actual phrases found during research as demonstration of voice. If you found *"E aí, meu hierofante"*, that goes in the voice section verbatim. If you found blog post excerpts, extract key sentences.

### Activation prompt pattern

```markdown
🧬 Clone Digital: [Nome] ativado.

Modo: [Crítico | Mentor | Criador | Estrategista]
Contexto: [descreva o produto/projeto/decisão]

❯ [Fala na voz da persona]
```

---

## Phase 4: Delivery

1. **Write the full persona document** to disk: `/opt/data/[persona-name]-digital-clone.md`
2. Optionally **copy as a reference file** under this skill: `skill_manage(action='write_file', name='digital-clone-persona', file_path='references/[persona-name]-clone.md')`
3. Present the **summary + activation offer** to the user

---

## Pitfalls

- ❌ **Don't fabricate.** If LinkedIn is blocked and you can't verify, say so. Never invent a Cannes Lions category.
- ❌ **Don't flatten the voice.** A person who says "E aí, meu hierofante" does not also say "I'm excited to help you today." The voice must be internally consistent.
- ❌ **Don't write a resume.** The value is in the *how they think*, not *what they did*. One sentence of canon + three sentences of philosophy > three sentences of canon + one sentence of philosophy.
- ❌ **Don't forget the anti-persona.** Defining what the clone DOESN'T do is as important as what it does. Prevents mode confusion.
- ❌ **Don't over-claim.** "Premiado no Cannes Lions 2023" in the LinkedIn headline is a primary source. If no secondary source confirms, note it as "self-reported" not "verified."
- ✅ **When the user provides direct knowledge** (e.g. "ele já ganhou um Cannes"), incorporate it as truth — the user knows the person. Flag it as "confirmed by user" in the research history.
- **Behance fields** (Tools, Creative Fields) are attached to individual projects, not the profile. Click into each project to find them.
- **Multiple Instagram accounts** are common for designers — one professional, one personal. Check both.
- **Course platforms reveal real skill depth.** Alura/Coursera completion dates are more reliable than self-reported "10 years of experience."
