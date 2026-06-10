# Relations Batch 3

Relations analysis for 27 skills at depth 1. Both sides of each relation were read and confirmed.

---

## research/polymarket
### Relations
- No relations found with the other 26 skills in this batch. Polymarket is a standalone prediction-market data query skill with no overlap with product development, social media, or productivity skills.

---

## research/research-paper-writing
### Relations
- `uses` → `software-development/plan`
  (source: research-paper-writing lists `plan` in its frontmatter `related_skills`. The paper pipeline's Phase 0 includes creating structured plans before execution. Plan mode's bite-sized task structure maps to the paper's phase-based approach. Confirmed by reading both SKILL.md files.)

---

## research/tech-trend-discovery
### Relations
- No relations found with the other 26 skills in this batch. Tech-trend-discovery is a standalone research skill for monitoring Reddit/HN/tech press trends — it shares no overlap with product development pipelines, productivity tools, or software development workflows in this batch.

---

## research/user-interview
### Relations
- `used_by` → `software-development/ideation-drilling`
  (source: ideation-drilling is Fase 1 of the product pipeline; its description says "Próxima fase: Carregar a skill de pesquisa (deep-research)..." — user-interview is part of this research phase. User-interview's SKILL.md states: "Use during the Research phase (Fase 2) of the product pipeline." The ideation output informs what to research. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/backlog-and-sprint`
  (source: backlog-and-sprint's Sprint Brief phase (2.2a) involves a user interview for clarification — structured listening to understand backlog items before sprint planning. The interview patterns in backlog-and-sprint align with user-interview's protocol. Confirmed by reading both SKILL.md files.)

---

## social-media/brand-iaf-conteudo
### Relations
- No relations found with the other 26 skills in this batch. Brand IAF is a standalone brand identity and content-generation skill for the IA que Funciona community. It shares no direct dependencies or overlaps with the other skills analyzed.

---

## social-media/xurl
### Relations
- No relations found with the other 26 skills in this batch. xurl is a standalone X/Twitter API CLI wrapper with no overlap to the other skills in scope.

---

## software-development/agy
### Relations
- `used_by` → `software-development/backlog-and-sprint`
  (source: backlog-and-sprint explicitly invokes agy for Sprint Design Review and Engineering Review via tmux sessions. Section 2.4 covers the full "agy design review" workflow with tmux send-keys, approval markers, and re-approval cycles. Confirmed: agy SKILL.md covers the CLI interface that backlog-and-sprint uses, and backlog-and-sprint SKILL.md has dedicated sections for agy integration.)
- `used_by` → `productivity/relatorio-de-custos`
  (source: relatorio-de-custos explicitly states "NUNCA escreva o HTML manualmente. O usuário prefere o agy para output visual" and "Gerar o Relatório Completo via Agy (MÉTODO PREFERENCIAL)". The full workflow covers scoping prompts to host, running agy with 300s timeout, and copying generated HTML back. Confirmed by reading both SKILL.md files.)

---

## software-development/backlog-and-sprint
### Relations
- `uses` → `software-development/agy`
  (source: backlog-and-sprint explicitly invokes agy for sprint design review and engineering review phases. The skill has dedicated sections (2.4, 2.6) with tmux session management, approval markers, and agy re-approval cycles. Confirmed: both SKILL.md files read.)
- `uses` → `research/user-interview`
  (source: backlog-and-sprint's Sprint Brief phase (2.2a) "Sprint Brief — User Interview for Clarification" involves structured questions and interview techniques that align with user-interview's protocol. The skill explicitly mentions interviewing the user to clarify backlog items before sprint planning. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/ideation-drilling`
  (source: ideation-drilling is Fase 1 of the product pipeline that defines the product vision; backlog-and-sprint is Fase 5 that executes sprints. Ideation results flow into the pipeline that includes sprint execution. Confirmed by reading both SKILL.md files — ideation-drilling states "Próxima fase: Carregar a skill de pesquisa" and backlog-and-sprint references the broader product pipeline context.)

---

## software-development/hermes-agent-skill-authoring
### Relations
- `uses` → `software-development/plan`
  (source: hermes-agent-skill-authoring lists `plan` in its frontmatter `related_skills`. The skill authoring process follows a structured approach similar to plan mode — survey peers, draft, validate, commit. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/skill-curation`
  (source: skill-curation explicitly says "Does NOT cover authoring SKILL.md files (see hermes-agent-skill-authoring)" — defers all authoring operations to this skill. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/skills-repo-curator`
  (source: skills-repo-curator manages the evolve cycle which involves editing and merging skills — operations that require skill authoring knowledge. The evolve step 7 ("Auditoria de descrições") involves editing SKILL.md files with frontmatter validation that hermes-agent-skill-authoring defines. Confirmed by reading both SKILL.md files.)

---

## software-development/ideation-drilling
### Relations
- `uses` → `research/user-interview`
  (source: ideation-drilling is Fase 1 of the product pipeline; it explicitly says the next phase is research. User-interview's SKILL.md says "Use during the Research phase (Fase 2) of the product pipeline — Understanding user needs, pain points, and behaviors — Before defining personas or user stories". The ideation result directly informs what to investigate in user interviews. Confirmed by reading both SKILL.md files.)
- `parent` → `software-development/backlog-and-sprint`
  (source: ideation-drilling defines the product vision (Fase 1) that feeds into the entire product pipeline. Backlog-and-sprint executes sprints (Fase 5) based on this vision. Ideation-drilling explicitly mentions the pipeline context with backlog-and-sprint as a downstream phase. Confirmed by reading both SKILL.md files — product-pipeline skill at `skills/autonomous-ai-agents/product-pipeline/` references both and confirms the parent/child relationship.)

---

## software-development/plan
### Relations
- `uses` → `software-development/test-driven-development`
  (source: plan's SKILL.md explicitly states "See `test-driven-development` skill for details" in the TDD section. Plan's Principles list TDD as a core methodology. Plan's related_skills lists test-driven-development. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/spike`
  (source: spike's SKILL.md explicitly states: "If the work is production path — use the `plan` skill instead". Spike defers production-bound work to plan mode. Spike lists plan in its related_skills. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/hermes-agent-skill-authoring`
  (source: hermes-agent-skill-authoring lists plan in its related_skills. The structured survey-draft-validate workflow mirrors plan mode's approach. Confirmed by reading both SKILL.md files.)
- `used_by` → `research/research-paper-writing`
  (source: research-paper-writing lists plan in its frontmatter related_skills. The paper pipeline's Phase 0 (Setup) creates structured plans before execution, aligning with plan mode. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/systematic-debugging`
  (source: systematic-debugging lists plan in its frontmatter related_skills. The debugging methodology involves planning the investigation approach before executing fixes. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/backlog-and-sprint`
  (source: backlog-and-sprint's sprint cycle involves planning phases (brief → planning → design → eng). While not directly referencing the plan skill by name, the planning phase structure aligns with plan mode's methodology. Confirmed by reading both SKILL.md files.)
- `similar` → `software-development/spike`
  (source: both are planning-oriented skills. Plan is for production-path implementation planning; spike is for throwaway validation experiments. Spike says use plan for production work. Both are pre-implementation planning activities at different levels of commitment. Confirmed by reading both SKILL.md files.)

---

## software-development/skill-curation
### Relations
- `uses` → `software-development/hermes-agent-skill-authoring`
  (source: skill-curation explicitly says "Does NOT cover authoring SKILL.md files (see hermes-agent-skill-authoring)" — it defers all authoring to this skill. Lists hermes-agent-skill-authoring in related_skills. Confirmed by reading both SKILL.md files.)
- `similar` → `software-development/skills-repo-curator`
  (source: both are meta-skills managing the skill lifecycle. skill-curation discovers/evaluates/installs community skills from external sources. skills-repo-curator manages the git repository's index.md, runs evolve cycles, and maintains the local skill catalog. Both deal with skill management but at different levels — skill-curation for acquisition, skills-repo-curator for internal organization. Confirmed by reading both SKILL.md files.)

---

## software-development/skills-repo-curator
### Relations
- `uses` → `software-development/hermes-agent-skill-authoring`
  (source: skills-repo-curator's evolve cycle includes editing and merging skills (step 7), which involves SKILL.md authoring operations. The evolve step "Auditoria de descrições" validates frontmatter against the conventions defined in hermes-agent-skill-authoring. Confirmed by reading both SKILL.md files.)
- `similar` → `software-development/skill-curation`
  (source: both are meta-skills for managing the Hermes skills ecosystem. skill-curation discovers and installs community skills from external sources; skills-repo-curator manages the local git repository, runs evolve cycles, and maintains the index. They operate at different levels of the skill lifecycle but share the domain of skill management. Confirmed by reading both SKILL.md files.)

---

## software-development/spike
### Relations
- `uses` → `software-development/plan`
  (source: spike's SKILL.md explicitly says: "If the work is production path — use the `plan` skill instead". Spike is explicitly framed as a precursor/preparatory activity to plan-mode work. Spike lists plan in its related_skills. Confirmed by reading both SKILL.md files.)
- `similar` → `software-development/plan`
  (source: both are planning/exploration skills. Spike validates feasibility through throwaway experiments; plan creates structured implementation plans for production. They serve different purposes but occupy adjacent territory in the pre-implementation phase. Confirmed by reading both SKILL.md files.)

---

## software-development/systematic-debugging
### Relations
- `uses` → `software-development/test-driven-development`
  (source: systematic-debugging's Phase 4 explicitly says: "Use the `test-driven-development` skill" when creating regression tests. The skill says "When fixing bugs: 1. Write a test that reproduces the bug (RED) 2. Debug systematically to find root cause 3. Fix the root cause (GREEN)". Systematic-debugging lists test-driven-development in related_skills. Confirmed by reading both SKILL.md files.)
- `uses` → `software-development/plan`
  (source: systematic-debugging lists plan in its frontmatter related_skills. The systematic approach (investigate → analyze → hypothesize → fix) follows a structured plan-like methodology. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/test-driven-development`
  (source: TDD's SKILL.md has a dedicated "With systematic-debugging" section that says: "Bug found? Write failing test reproducing it. Follow TDD cycle. The test proves the fix and prevents regression." TDD lists systematic-debugging in its related_skills. Confirmed by reading both SKILL.md files.)

---

## software-development/test-driven-development
### Relations
- `uses` → `software-development/systematic-debugging`
  (source: TDD's SKILL.md explicitly says "With systematic-debugging — Bug found? Write failing test reproducing it. Follow TDD cycle." TDD lists systematic-debugging in its related_skills. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/plan`
  (source: plan's SKILL.md says "See `test-driven-development` skill for details" and includes TDD as a core principle. Plan lists test-driven-development in its related_skills. Confirmed by reading both SKILL.md files.)
- `used_by` → `software-development/systematic-debugging`
  (source: systematic-debugging's Phase 4 says "Use the `test-driven-development` skill" for creating regression tests. Systematic-debugging lists test-driven-development in its related_skills. Confirmed by reading both SKILL.md files.)

---

## productivity/airtable
### Relations
- `similar` → `productivity/notion`
  (source: both are database/platform API integration skills covering CRUD operations on structured data stores. Airtable lists notion in its related_skills; notion lists airtable in its related_skills. Both API skills use curl/CLI patterns for database operations (tables, records, filters, pagination). Confirmed by reading both SKILL.md files.)
- `similar` → `productivity/google-workspace`
  (source: both are productivity platform API integrations. Airtable lists google-workspace in its related_skills; google-workspace lists airtable in its related_skills. Both cover data operations (CRUD) on cloud platforms via API/CLI. Confirmed by reading both SKILL.md files.)

---

## productivity/google-workspace
### Relations
- `similar` → `productivity/airtable`
  (source: google-workspace lists airtable in its related_skills; airtable lists google-workspace in its related_skills. Both are cloud productivity platform API integrations. Confirmed by reading both SKILL.md files.)
- `uses` → `productivity/ocr-and-documents`
  (source: google-workspace lists ocr-and-documents in its frontmatter related_skills. Google Drive handles various document types (PDFs, images) that may need text extraction, which ocr-and-documents covers. Confirmed by reading both SKILL.md files.)

---

## productivity/html-report-hermes
### Relations
- `uses` → `software-development/agy`
  (source: html-report-hermes' routing rule explicitly says "Hermes CRT (Visual/Showcase) → USE AGY". For CRT mode pages, it defers all HTML generation to agy via SSH pipeline. Confirmed by reading both SKILL.md files.)
- `uses` → `productivity/html-to-pdf-chromium`
  (source: html-report-hermes says "Converter para .pdf — via Chromium headless (veja skill html-to-pdf-chromium)" in its Telegram Delivery section. When users need PDF conversion of generated HTML reports, it defers to html-to-pdf-chromium. Confirmed by reading both SKILL.md files — html-to-pdf-chromium lists html-report-hermes in its related_skills.)
- `used_by` → `productivity/relatorio-de-custos`
  (source: relatorio-de-custos lists html-report-hermes in its related_skills. The cost report skill explicitly says the report should use "design Hermes Style Guide (azul royal, Spectral + Space Mono, dourado)" which matches html-report-hermes' Hermes Official design system. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/html-to-pdf-chromium`
  (source: html-to-pdf-chromium lists html-report-hermes in its related_skills. The pipeline of HTML → (html-report-hermes) → PDF (html-to-pdf-chromium) means html-to-pdf-chromium processes reports created by html-report-hermes. Confirmed by reading both SKILL.md files.)

---

## productivity/html-to-pdf-chromium
### Relations
- `uses` → `productivity/html-report-hermes`
  (source: html-to-pdf-chromium lists html-report-hermes in its related_skills. The PDF conversion tool expects HTML input that follows the design systems defined in html-report-hermes. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/html-report-hermes`
  (source: html-report-hermes explicitly references html-to-pdf-chromium for PDF conversion of generated HTML reports. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/nano-pdf`
  (source: nano-pdf lists html-to-pdf-chromium in its related_skills. Both are PDF-related tools — html-to-pdf-chromium creates PDFs from HTML, nano-pdf edits existing PDFs. Nano-pdf's workflow may involve converting HTML to PDF first. Confirmed by reading both SKILL.md files.)

---

## productivity/maps
### Relations
- No relations found with the other 26 skills in this batch. Maps is a standalone location intelligence skill (geocoding, POIs, routing, timezones) using OpenStreetMap data. It lists taskflow-mcp in its related_skills, but taskflow-mcp does NOT list maps — this is a one-directional declaration for potential location-based task features, not a confirmed reciprocal relation.

---

## productivity/nano-pdf
### Relations
- `uses` → `productivity/ocr-and-documents`
  (source: nano-pdf lists ocr-and-documents in its related_skills. OCR may be needed to extract text from scanned PDFs before editing with nano-pdf. Confirmed by reading both SKILL.md files.)
- `uses` → `productivity/html-to-pdf-chromium`
  (source: nano-pdf lists html-to-pdf-chromium in its related_skills. The PDF editing pipeline may require converting HTML to PDF before applying edits. Confirmed by reading both SKILL.md files.)
- `similar` → `productivity/ocr-and-documents`
  (source: both deal with PDF/document manipulation — nano-pdf for text editing, ocr-and-documents for text extraction. Ocr-and-documents lists nano-pdf in its related_skills; nano-pdf lists ocr-and-documents in its. They're complementary PDF tools in the document processing pipeline. Confirmed by reading both SKILL.md files.)

---

## productivity/notion
### Relations
- `similar` → `productivity/airtable`
  (source: both are database/platform API skills. Notion lists airtable in its related_skills; airtable lists notion in its. Both cover database CRUD, page/record creation, filtering, and querying via API/CLI. Confirmed by reading both SKILL.md files.)
- `similar` → `productivity/taskflow-mcp`
  (source: notion lists taskflow-mcp in its related_skills; taskflow-mcp lists notion in its related_skills. Both deal with structured data management — Notion for general-purpose databases/pages, TaskFlow for GTD task management. They share task/database management semantics. Confirmed by reading both SKILL.md files.)

---

## productivity/ocr-and-documents
### Relations
- `uses` → `productivity/powerpoint`
  (source: ocr-and-documents explicitly says "For PowerPoint: see the `powerpoint` skill" and "For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support)". Ocr-and-documents lists powerpoint in its related_skills. Confirmed by reading both SKILL.md files.)
- `uses` → `productivity/nano-pdf`
  (source: ocr-and-documents lists nano-pdf in its related_skills. After extracting text from PDFs, edits may be needed via nano-pdf. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/google-workspace`
  (source: google-workspace lists ocr-and-documents in its related_skills. Document extraction from Drive files may use ocr-and-documents' capabilities. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/nano-pdf`
  (source: nano-pdf lists ocr-and-documents in its related_skills. OCR may be needed to extract text before editing PDFs. Confirmed by reading both SKILL.md files.)
- `similar` → `productivity/nano-pdf`
  (source: both are PDF/document processing tools. ocr-and-documents covers extraction; nano-pdf covers editing. They're complementary but share the PDF manipulation domain. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/powerpoint`
  (source: powerpoint lists ocr-and-documents in its related_skills. Converting PPTX to images or extracting text may involve document processing. Confirmed by reading both SKILL.md files.)

---

## productivity/powerpoint
### Relations
- `uses` → `productivity/ocr-and-documents`
  (source: powerpoint lists ocr-and-documents in its related_skills. The PowerPoint skill's image conversion pipeline (soffice → pdftoppm) and text extraction may leverage document processing tools. Confirmed by reading both SKILL.md files.)
- `used_by` → `productivity/ocr-and-documents`
  (source: ocr-and-documents explicitly defers PPTX handling to the powerpoint skill, saying "For PPTX: see the `powerpoint` skill". Confirmed by reading both SKILL.md files.)

---

## productivity/relatorio-de-custos
### Relations
- `uses` → `software-development/agy`
  (source: relatorio-de-custos explicitly states "NUNCA escreva o HTML manualmente. O usuário prefere o agy para output visual" and has a complete section "Gerar o Relatório Completo via Agy (MÉTODO PREFERENCIAL)" with prompt creation, SSH copy, and 300s timeout workflow. Confirmed by reading both SKILL.md files.)
- `uses` → `productivity/html-report-hermes`
  (source: relatorio-de-custos lists html-report-hermes in its related_skills. The cost report uses the "Hermes Style Guide (azul royal, Spectral + Space Mono, dourado)" design system defined in html-report-hermes' Hermes Official mode. The report structure (hero, KPI cards, tables) follows html-report-hermes' template. Confirmed by reading both SKILL.md files.)

---

## productivity/taskflow-mcp
### Relations
- `similar` → `productivity/notion`
  (source: taskflow-mcp lists notion in its related_skills; notion lists taskflow-mcp in its. Both are task/data management tools — TaskFlow for GTD task management via MCP, Notion for general-purpose databases/pages via API. They share structured data management semantics and both support task tracking workflows. Confirmed by reading both SKILL.md files.)
