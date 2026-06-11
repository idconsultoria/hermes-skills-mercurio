# Deep Research Skills Ranking — June 2026

> Generated from curation session. Covers all known Hermes Agent deep-research
> skills found via web search, GitHub, HermesHub, and review sites.

---

## 🥇 TIER 1 — Multi-Agent Pipelines (Elite)

### 1º Provable0816/academic-research (⭐ v2.9.4)
- **13 specialized agents** across 6 phases
- **7 modes**: socratic, full, quick, review, lit-review, fact-check, systematic-review
- **Output**: APA 7.0 complete report (Title → Abstract → Discussion → References)
- **Differentials**: Socratic mode for vague questions, simulated peer review, bias/ethics checks
- **Best for**: Academic papers, systematic reviews, meta-analyses, dissertations
- **Install**: `hermes skills tap add Provable0816/academic_research_skills_for_hermes`
- **Feedback**: Only skill with full multilingual support (EN + Traditional Chinese)

### 2º oh-my-hermes — omh-deep-research (⭐ 54)
- **Multi-phase**: Decompose → 3-5 parallel researchers → Synthesizer → Verifier → Confirmed report
- **Cost**: 5-8 delegate_task calls (happy path), up to ~14 worst-case
- **Differentials**: Source verification + citation confirmation, READ-ONLY contracts, strike caps
- **Integration**: Composes with full OMH suite (deep-interview → ralplan → ralph → autopilot)
- **Best for**: Web research, due diligence, technical decisions
- **Install**: `hermes skills tap add witt3rd/oh-my-hermes && hermes skills install omh-deep-research`

### 3º LeePepe/hermes-skills — deep-research (GPT-Researcher inspired)
- **Pipeline**: 4 parallel researchers (Web, GitHub, News, Academic) → 4 parallel reviewers → Roundtable → Report
- **Depth levels**: Quick (2-3 sub-questions), Standard (4-6), Deep (6-8 + recursive)
- **Differential**: Simulated roundtable with 4 roles debating contradictions
- **Output**: Report with confidence indicators (🟢 HIGH / 🟡 MEDIUM / 🔴 CONTESTED)
- **Best for**: Competitive analysis, market research, technology evaluation
- **Install**: `hermes skills tap add LeePepe/hermes-skills && hermes skills install deep-research`
- **Installed**: ✅ (this session)

---

## 🥈 TIER 2 — Structured Protocols

### 4º ChuckSRQ/awesome-hermes-skills — deep-research (⭐ 66)
- **9 analytical lenses**: Technical, Economic, Historical, Business, Strategic, Customer, Product, Contrarian, First-Principles
- **Output**: 4 files — executive-summary, deep-dive, key-players, open-questions
- **Differential**: Contradiction resolution as feature, pluggable methodologies (Verification, Causal, Scenario, Decision)
- **Best for**: Strategic decisions, investments, market analysis
- **Install**: `hermes skills tap add ChuckSRQ/awesome-hermes-skills && hermes skills install deep-research`

### 5º alexferrari88/hermes-deep-research (⭐ v0.2.0)
- **9 phases**: Frame → Research Map → Broad → Select → Deep → Specialist Passes → Evidence Ledger → Synthesis → Critique → Package
- **4 modes**: Scout (3-5 sources), Standard (8-15), Deep (15-30), Forensic (20-40+)
- **Differential**: Evidence Ledger — formal evidence record with confidence levels
- **5 non-negotiables**: never from memory, multi-angle search, read full sources, use Python for scoring, separate fact/synthesis/inference/speculation
- **Best for**: OSS due diligence, startups, executive memos
- **Install**: `hermes skills tap add alexferrari88/skills && hermes skills install hermes-deep-research`

### 6º carycoooper/Hermes-Premium-Skills (⭐ v2.0.0)
- **4 phases**: Query Analysis → Multi-Source → Synthesis → Report
- **Commands**: `deep-research [topic]`, `deep-research compare A vs B`, `deep-research verify [claims]`, `deep-research monitor [topic]`
- **Differential**: Based on OpenClaw Deep Research (180K+ installs) with Hermes optimizations
- **Best for**: Fact-checking, continuous monitoring, quick comparisons
- **Install**: `hermes skills tap add carycoooper/Hermes-Premium-Skills-Collection`

---

## 🥉 TIER 3 — Specialized & Bundled

### 7º Felo Search + Web Fetch (⭐ 202)
- Free real-time search with source attribution
- Not a multi-agent pipeline — single skill
- Bulk install: `bash <(curl -s https://raw.githubusercontent.com/Felo-Inc/felo-skills/main/scripts/install-hermes.sh)`
- **Best for**: Quick research with citations, fact-checking

### 8º arxiv (bundled)
- Native arXiv search — academic papers
- Zero configuration, always available
- **Best for**: ML/AI literature searches

### 9º blogwatcher (bundled)
- RSS/Atom feed monitoring
- Good as data source for larger pipelines
- **Best for**: Feeding fresh content into research workflows

---

## Tradeoffs Summary

| Skill | Agents | Modes | Tokens | Complexity | Best For |
|-------|:------:|:-----:|:------:|:----------:|----------|
| academic-research | 13 | 7 | 🔴 High | High | Academia, systematic reviews |
| omh-deep-research | 5-8 | 1 | 🟡 Medium | Medium | Web due diligence |
| LeePepe GPT-Research | 8+4 | 3 | 🟡 Medium | Medium | Tech/market research |
| ChuckSRQ 9 lenses | 0* | 1 | 🟢 Low | Medium | Strategic analysis |
| alexferrari88 protocol | 0* | 4 | 🟢 Low | Medium | OSS evaluation |
| carycooper v2.0 | 0* | 4 | 🟢 Low | Low | Fact-check, monitor |

* `0*` = uses parent Hermes as executor, not delegate_task batch
