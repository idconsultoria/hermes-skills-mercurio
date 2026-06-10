# Relations Batch 2

## data-science/jupyter-live-kernel

### Relations
- No relations found to other skills in this batch. It's a standalone interactive Python REPL via Jupyter kernels — no other skills in this batch depend on or are related to it.

---

## dogfood/dogfood

### Relations
- `similar` → `github/codebase-inspection`
  (source: Both are systematic quality-analysis tools. Dogfood performs exploratory QA of web apps via browser/API testing; codebase-inspection analyzes repositories for structural and architectural quality. Both share a phased workflow (plan → explore → collect → categorize → report), produce diagnostic reports with severity ratings, and test infrastructure readiness. Neither directly depends on the other, but they are complementary quality-assurance patterns for different targets.)

---

## email/himalaya

### Relations
- No relations found to other skills in this batch. Standalone CLI email client skill — no other batch skill depends on or relates to IMAP/SMTP email operations.

---

## github/codebase-inspection

### Relations
- `similar` → `github/github-code-review`
  (source: Both analyze code quality. Codebase-inspection does structural/codebase audits (LOC, dependencies, architecture); github-code-review reviews PR diffs and local changes. Complementary analysis tools at different stages — pre-PR cleanup (inspection) vs during-PR (review). Confirmed by reading both: codebase-inspection metadata has related_skills: [github-repo-management, github-code-review]; github-code-review mentions code-review as pre-PR and PR-review.)
- `uses` → `github/github-repo-management`
  (source: Codebase inspection requires a repository to operate on — cloning, checking out branches, examining remotes. The repo-management skill provides the operations (clone, fork, branch management) that precede inspection. Confirmed by reading both: codebase-inspection metadata lists github-repo-management as related.)
- `similar` → `dogfood/dogfood`
  (source: Both are systematic quality analysis tools — codebase-inspection for repositories, dogfood for web applications. Shared diagnostic/report workflow.)

---

## github/github-auth

### Relations
- `used_by` → `github/github-code-review`
  (source: Code review needs authenticated access to fetch PRs, post comments, and submit reviews via gh CLI or GitHub API. Code review's SKILL.md explicitly states "Authenticated with GitHub (see github-auth skill)" as prerequisite.)
- `used_by` → `github/github-issues`
  (source: Issue management requires auth to create, triage, label, and close issues. Issues SKILL.md: "Authenticated with GitHub (see github-auth skill)" as prerequisite.)
- `used_by` → `github/github-pr-workflow`
  (source: PR lifecycle — branch, commit, open, merge — requires git push and gh CLI or REST API auth. PR workflow SKILL.md: "Authenticated with GitHub (see github-auth skill)" as prerequisite.)
- `used_by` → `github/github-repo-management`
  (source: Cloning, creating, forking repos, managing secrets and releases all require auth. Repo management SKILL.md: "Authenticated with GitHub (see github-auth skill)" as prerequisite.)
- `used_by` → `infrastructure/deployment-pipeline`
  (source: The CI/CD pipeline pushes Docker images to ghcr.io and pulls them on the deploy server — both operations need GitHub tokens (GITHUB_TOKEN, GHCR_TOKEN). Deployment SKILL.md has an entire section on ghcr.io auth patterns — token scopes, PAT setup, GITHUB_TOKEN vs GHCR_TOKEN — and lists github-auth in related_skills.)

---

## github/github-code-review

### Relations
- `uses` → `github/github-auth`
  (source: Prerequisite auth for PR interactions. Code review SKILL.md: "Authenticated with GitHub (see github-auth skill)")
- `used_by` → `github/github-pr-workflow`
  (source: PR workflow includes code review as a step. PR workflow SKILL.md lists github-code-review in related_skills and has an end-to-end PR workflow that includes review steps.)
- `similar` → `github/codebase-inspection`
  (source: Both analyze code. Codebase-inspection metadata lists github-code-review as related; codebase-inspection mentions "Pre-PR cleanup: scan for structural issues before proposing changes".)

---

## github/github-issues

### Relations
- `uses` → `github/github-auth`
  (source: Prerequisite auth for issue management. Issues SKILL.md: "Authenticated with GitHub (see github-auth skill)")
- `used_by` → `github/github-pr-workflow`
  (source: PR workflow references issues with "Closes #42" pattern and has `gh issue develop 42 --checkout` to create branches from issues. PR workflow SKILL.md mentions linking PRs to issues.)
- `similar` → `github/github-repo-management`
  (source: Both are GitHub project management skills — issues for bug/feature tracking, repo management for repository configuration. Complementary but distinct domains within GitHub.)

---

## github/github-pr-workflow

### Relations
- `uses` → `github/github-auth`
  (source: Prerequisite auth. PR workflow SKILL.md: "Authenticated with GitHub (see github-auth skill)")
- `uses` → `github/github-code-review`
  (source: PR workflow end-to-end recipe includes review step. PR workflow SKILL.md lists github-code-review in related_skills.)
- `uses` → `infrastructure/deployment-pipeline`
  (source: PR workflow's CI monitoring, auto-fixing, preview deployment, and merge phases all reference deployment-pipeline. PR workflow SKILL.md: "For CI monitoring, auto-fixing CI failures, and preview deployment, see deployment-pipeline" and "For PR preview environments, deploy CI, and deployment pipeline patterns, see deployment-pipeline.")
- `uses` → `infrastructure/oracle-host-access`
  (source: PR workflow SKILL.md: "For SSH-based host access during deployment, see oracle-host-access". Lists oracle-host-access in related_skills.)
- `similar` → `github/github-repo-management`
  (source: Both manage GitHub operations — PR workflow focuses on PR lifecycle (branch → commit → PR → merge), repo management handles repo CRUD (clone/create/fork/releases/secrets). Complementary but related GitHub administration.)

---

## github/github-repo-management

### Relations
- `uses` → `github/github-auth`
  (source: Prerequisite auth. Repo management SKILL.md: "Authenticated with GitHub (see github-auth skill)")
- `similar` → `github/github-pr-workflow`
  (source: Both are GitHub repository operations skills — one focuses on repo-level CRUD, the other on PR lifecycle.)
- `similar` → `github/github-issues`
  (source: Both are GitHub project management — repo management for settings/releases/secrets, issues for bug/feature tracking.)
- `used_by` → `github/codebase-inspection`
  (source: Codebase inspection requires repos to analyze. Codebase-inspection metadata lists github-repo-management as related_skill.)

---

## infrastructure/ai-voice-selfhost

### Relations
- `uses` → `infrastructure/oracle-host-access`
  (source: Deploying TTS models on Oracle ARM64 requires SSH access to the host. The ai-voice-selfhost SKILL.md repeatedly uses `ssh oracle-host` for copying files, building Docker, and verifying. Oracle-host-access SKILL.md explicitly lists ai-voice-selfhost in related_skills.)
- `uses` → `mlops/huggingface-hub`
  (source: Models (OmniVoice, Fish Speech GGUF, etc.) are downloaded from HuggingFace Hub. The ai-voice-selfhost SKILL.md mentions model download from HuggingFace, uses HF model IDs, and references `wget` from HF URLs.)
- `similar` → `mlops/inference/llama-cpp`
  (source: Both are local ML inference skills — ai-voice-selfhost for TTS models (Fish Speech S2 GGUF via s2.cpp), llama-cpp for LLM GGUF inference. Both use GGUF quantization, run on CPU/ARM64, deploy via Docker, expose OpenAI-compatible endpoints, and involve model discovery on HuggingFace Hub.)

---

## infrastructure/deployment-pipeline

### Relations
- `uses` → `github/github-auth`
  (source: CI/CD pipeline uses GITHUB_TOKEN and GHCR_TOKEN for ghcr.io registry auth. Deployment SKILL.md has extensive ghcr.io auth sections covering token scopes, PAT setup, and references github-auth.)
- `uses` → `infrastructure/oracle-host-access`
  (source: Deploy step uses SSH to the Oracle host for `docker compose pull && up -d`. Deployment SKILL.md references SSH deploy key setup, appleboy/ssh-action, and oracle-host-access in related_skills.)
- `used_by` → `github/github-pr-workflow`
  (source: PR workflow's CI/CD and deploy phases reference deployment-pipeline. PR workflow SKILL.md explicitly directs to deployment-pipeline for CI monitoring, auto-fixing, and PR previews.)
- `similar` → `infrastructure/vercel-deploy`
  (source: Both are deployment skills — deployment-pipeline for Docker/SSH/GitHub Actions deployments, vercel-deploy for static site/frontend deployments to Vercel. Different targets (bare-metal Docker vs serverless Jamstack) but both cover the full deploy lifecycle: auth, build, deploy, verify.)

---

## infrastructure/oracle-host-access

### Relations
- `used_by` → `infrastructure/deployment-pipeline`
  (source: Deployment pipeline's SSH deploy step requires oracle-host-access for key setup and SSH config. Oracle-host-access references deployment-pipeline in related_skills and says "See references/selfhost-initial-setup.md for the pattern to set up a new selfhost service.")
- `used_by` → `infrastructure/ai-voice-selfhost`
  (source: TTS model deployment uses SSH to copy files, build Docker, and start containers on the Oracle host. Oracle-host-access lists ai-voice-selfhost in related_skills.)
- `used_by` → `github/github-pr-workflow`
  (source: PR workflow references oracle-host-access for SSH-based host access during deployment. PR workflow SKILL.md lists oracle-host-access in related_skills.)

---

## infrastructure/vercel-deploy

### Relations
- `similar` → `infrastructure/deployment-pipeline`
  (source: Both are deployment skills covering authentication, build, deploy, verification, and pitfall documentation. Targets differ (Vercel serverless vs Docker bare-metal) but share the same deployment lifecycle pattern.)

---

## media/hyperframes-video-production

### Relations
- `similar` → `media/youtube-content`
  (source: Both are media production skills — hyperframes produces MP4 videos from HTML compositions, youtube-content extracts and transforms YouTube transcripts. Complementary: both work with video content but at different stages (production vs consumption).)

---

## media/youtube-content

### Relations
- `similar` → `media/hyperframes-video-production`
  (source: Both are video-related media skills. One produces video from scratch, the other extracts content from existing videos.)
- `uses` → `research/llm-wiki`
  (source: YouTube transcripts are a natural source for wiki ingestion — the llm-wiki skill's ingest pipeline accepts articles, transcripts, and web content as raw sources for its knowledge base. While not explicitly cross-referenced in SKILL.md metadata, the workflow is directly complementary: extract transcript → ingest into wiki for persistent knowledge.)

---

## messaging-platforms/whatsapp-bridge-baileys

### Relations
- No relations found to other skills in this batch. Standalone WhatsApp bridge skill — no other batch skills share the messaging domain or toolchain.

---

## mlops/evaluation/lm-evaluation-harness

### Relations
- `uses` → `mlops/inference/vllm`
  (source: lm-evaluation-harness supports vLLM as a backend for 5-10x faster evaluation. The SKILL.md has a dedicated "Evaluate with vLLM" workflow showing `lm_eval --model vllm` configuration. Dependencies include vllm.)
- `uses` → `mlops/huggingface-hub`
  (source: Evaluates HuggingFace models directly by ID. The SKILL.md examples use `pretrained=meta-llama/Llama-2-7b-hf` and other HF model IDs.)
- `similar` → `mlops/evaluation/weights-and-biases`
  (source: Both are MLOps evaluation/experiment tracking tools. lm-evaluation-harness benchmarks models on academic tasks; W&B tracks experiments, hyperparameters, and model registry. Complementary in an ML pipeline — you'd use lm-eval to benchmark and W&B to log/compare results.)

---

## mlops/evaluation/weights-and-biases

### Relations
- `uses` → `mlops/huggingface-hub`
  (source: W&B integrates with HuggingFace Transformers natively — `report_to="wandb"` in TrainingArguments auto-logs metrics. The SKILL.md has a dedicated "HuggingFace Transformers" integration section.)
- `similar` → `mlops/evaluation/lm-evaluation-harness`
  (source: Both are ML experiment tracking/evaluation tools. W&B tracks training runs and hyperparameters; lm-eval benchmark models. Part of the same MLOps evaluation stack.)

---

## mlops/huggingface-hub

### Relations
- `used_by` → `mlops/evaluation/lm-evaluation-harness`
  (source: lm-eval loads models directly from HF Hub by ID.)
- `used_by` → `mlops/inference/llama-cpp`
  (source: llama.cpp discovers and downloads GGUF models from HF Hub. The SKILL.md's entire Model Discovery workflow is Hub-based: search HF, check local-app page, query tree API.)
- `used_by` → `mlops/inference/vllm`
  (source: vLLM loads models from HF Hub by ID. All examples use `model="meta-llama/Llama-3-8B-Instruct"` or similar HF model paths.)
- `used_by` → `infrastructure/ai-voice-selfhost`
  (source: TTS models (Fish Speech GGUF, OmniVoice) are downloaded from HF Hub as part of Docker deployment.)

---

## mlops/inference/llama-cpp

### Relations
- `uses` → `mlops/huggingface-hub`
  (source: Core model discovery workflow is HF Hub-based: search `https://huggingface.co/models?apps=llama.cpp`, check local-app pages, query tree API for GGUF files. Direct `llama-server -hf repo:quant` syntax loads from Hub.)
- `similar` → `mlops/inference/vllm`
  (source: Both are LLM inference engines. llama.cpp targets CPU/edge/single-user with GGUF quantization; vLLM targets GPU/production/high-throughput with PagedAttention. Both expose OpenAI-compatible endpoints, support quantization, and load models from HF Hub. vLLM SKILL.md explicitly lists llama.cpp as an alternative: "llama.cpp: CPU/edge inference, single-user".)
- `similar` → `infrastructure/ai-voice-selfhost`
  (source: Both serve ML models locally with Docker, CPU inference, GGUF quantization, and OpenAI-compatible API endpoints. Different domains (LLM vs TTS) but identical deployment patterns.)

---

## mlops/inference/vllm

### Relations
- `uses` → `mlops/huggingface-hub`
  (source: All vLLM examples load models from HF Hub by repository ID. Dependencies include transformers.)
- `used_by` → `mlops/evaluation/lm-evaluation-harness`
  (source: lm-eval supports vLLM as a high-throughput backend. The lm-eval SKILL.md has Workflow 4 specifically for vLLM evaluation.)
- `similar` → `mlops/inference/llama-cpp`
  (source: Both are LLM inference engines serving OpenAI-compatible APIs. Different performance/use-case profiles but same domain.)

---

## mlops/pi-session-audit

### Relations
- No relations found to other skills in this batch. Standalone auditing skill for Pi Agent sessions — no other batch skill shares the Pi Agent domain or session-auditing toolchain.

---

## note-taking/obsidian

### Relations
- `used_by` → `research/llm-wiki`
  (source: llm-wiki SKILL.md explicitly states: "The wiki directory works as an Obsidian vault out of the box" with wikilinks, Graph View, YAML frontmatter for Dataview. Has a dedicated "Obsidian Integration" section describing how to point Obisidian at the wiki directory. Lists obsidian in related_skills and suggests setting `OBSIDIAN_VAULT_PATH` to the wiki path for cross-compatibility.)

---

## read-reddit/read-reddit

### Relations
- `similar` → `research/blogwatcher`
  (source: Both consume web feeds — read-reddit reads Reddit subreddits via RSS feeds; blogwatcher monitors blogs via RSS/Atom feeds. Same underlying technology (RSS/Atom XML parsing), similar use case (content discovery and curation).)

---

## research/arxiv

### Relations
- `used_by` → `research/deep-research`
  (source: The deep-research pipeline's academic research phase searches arXiv, Google Scholar, and Semantic Scholar for papers. The deep-research SKILL.md Phase 1 details the academic agent that searches arXiv, and mentions "arXiv API sometimes unstable, prepare Google Scholar as fallback.")
- `similar` → `research/llm-wiki`
  (source: Both are academic/research tools. arXiv discovers papers; llm-wiki compiles and cross-references knowledge from discovered sources. Complementary: arXiv findings feed into the wiki for persistent knowledge storage.)

---

## research/blogwatcher

### Relations
- `similar` → `read-reddit/read-reddit`
  (source: Both are feed-reading skills — blogwatcher for RSS/Atom blog feeds, read-reddit for Reddit RSS feeds. Both use XML parsing, feed discovery, and content curation patterns.)
- `used_by` → `research/deep-research`
  (source: The deep research pipeline includes a news/current-events phase that could consume blogwatcher-tracked feeds. While not explicitly referenced in SKILL.md metadata, blogwatcher's function (monitoring blog/RSS updates) directly feeds into deep-research's news research agent.)

---

## research/deep-research

### Relations
- `uses` → `research/arxiv`
  (source: Academic phase of the deep research pipeline searches arXiv papers. Deep-research SKILL.md explicitly defines an academic sub-agent that searches arXiv, Google Scholar, Semantic Scholar.)
- `uses` → `research/blogwatcher`
  (source: The news/current-events research phase in deep-research could leverage blog/feed monitoring. Blogwatcher's RSS monitoring function directly supports the news research agent's goal of finding latest developments.)
- `similar` → `research/llm-wiki`
  (source: Both synthesize research into structured output. Deep-research produces depth reports with confidence-graded findings; llm-wiki builds a persistent interlinked knowledge base. Different approaches (one-shot deep dive vs compounding wiki) but both in the research synthesis domain.)

---

## research/llm-wiki

### Relations
- `similar` → `research/arxiv`
  (source: Both are research/knowledge tools — arxiv discovers academic papers, llm-wiki compiles knowledge from sources including papers. Complementary: arxiv findings are natural inputs for wiki ingestion.)
- `similar` → `research/deep-research`
  (source: Both synthesize multi-source knowledge. Llm-wiki builds a persistent, constantly updated KB; deep-research produces one-shot depth reports. Different time horizons but same research synthesis domain.)
- `uses` → `note-taking/obsidian`
  (source: The wiki is designed as an Obsidian vault. Llm-wiki SKILL.md has an "Obsidian Integration" section detailing how the wiki works with Obsidian's Graph View, Dataview, and wikilinks. Suggests setting `OBSIDIAN_VAULT_PATH` to the wiki directory.)
