---
name: deep-research
description: "Multi-agent deep research: decompose, dispatch agents, cross-validate, synthesize.

Load this skill when you need thorough research on complex topics. Inspired by GPT-Researcher, this pipeline decomposes questions into sub-queries, dispatches parallel research agents across web, GitHub, news, and academic sources, runs independent reviewers, then cross-validates and synthesizes. Produces cited reports with confidence-graded findings across three depth levels."
category: research
---

# Deep Research Skill

基于 GPT-Researcher 架构，适配 Hermes delegate_task 的多 agent 深度调研流水线。

## Pipeline Overview

```
用户问题
   │
   ▼
[Phase 0] 问题分析 & 子问题分解 (Hermes 自身)
   │
   ▼
[Phase 1] 并行调研 agents (delegate_task batch, 4 agents)
   │         ├─ Web 调研 agent
   │         ├─ GitHub/代码 调研 agent
   │         ├─ 新闻/时事 调研 agent
   │         └─ 学术/论文 调研 agent
   │
   ▼
[Phase 2] 并行审核 agents (delegate_task batch, 4 reviewers)
   │         ├─ Web reviewer     ── 核实来源可信度 & 事实准确性
   │         ├─ GitHub reviewer  ── 验证仓库活跃度 & 代码质量
   │         ├─ News reviewer    ── 检查时效性 & 多源交叉
   │         └─ Academic reviewer── 验证引用 & 方法论
   │
   ▼
[Phase 3] 交叉验证 + 圆桌会议 (delegate_task, 1 orchestrator agent)
   │         ├─ 找出各源矛盾点
   │         ├─ 对有争议观点进行辩论
   │         └─ 形成共识或标注分歧
   │
   ▼
[Phase 4] 报告生成 (Hermes 自身)
   │         ├─ 综合所有审核后的调研结果
   │         ├─ 按置信度分级 (HIGH/MEDIUM/LOW/CONTESTED)
   │         └─ 输出最终报告 (含引用来源)
```

## Phase 0: 问题分析 & 子问题分解

Hermes 自身完成，不需要 delegate。

1. 分析用户问题，确定调研范围和深度
2. 生成 4-8 个子问题，覆盖不同维度
3. 为每个调研 agent 分配相关子问题
4. 确定调研语言（跟随用户偏好，默认中文报告）

生成子问题时的 prompt 模板：

```
分析以下问题，生成 4-8 个聚焦的子问题，用于从不同角度调研：
- 每个子问题应独立可查
- 覆盖：背景/现状、技术细节、对比/替代方案、趋势/前景
- 标注每个子问题适合的调研渠道（web/github/news/academic）

问题：{user_question}
```

## Phase 1: 并行调研 Agents

使用 delegate_task 的 batch 模式，4 个 agent 并行执行：

### Agent 分配

```python
delegate_task(tasks=[
    {
        "goal": "Web 综合调研",
        "context": f"""你是 Web 调研专家。针对以下问题进行深度 web 搜索调研：

问题：{user_question}
重点子问题：{web_sub_queries}

要求：
1. 搜索至少 3 个不同搜索引擎/来源
2. 每个发现必须附带来源 URL
3. 提取关键数据点、统计数字、专家观点
4. 标注信息的时效性（发布日期）
5. 区分事实陈述 vs 观点/推测
6. 输出格式：
   ## 发现 N: [标题]
   - 来源: [URL]
   - 日期: [日期]
   - 类型: 事实/观点/数据
   - 内容: [详细描述]
   - 置信度: HIGH/MEDIUM/LOW
""",
        "toolsets": ["web", "browser"]
    },
    {
        "goal": "GitHub/代码生态调研",
        "context": f"""你是 GitHub 和开源生态调研专家。针对以下问题搜索相关代码仓库、技术实现和社区讨论：

问题：{user_question}
重点子问题：{github_sub_queries}

要求：
1. 搜索 GitHub 仓库（star 数、活跃度、最近更新）
2. 查看关键仓库的 README、架构、issues、discussions
3. 查找相关技术实现和最佳实践
4. 对比不同开源方案的优劣
5. 每个发现必须附带仓库 URL 和具体证据
6. 输出格式：
   ## 仓库/发现 N: [名称]
   - URL: [链接]
   - Stars: [数量] | 最近更新: [日期]
   - 核心特点: [描述]
   - 与问题的关联: [分析]
   - 置信度: HIGH/MEDIUM/LOW
""",
        "toolsets": ["web", "browser", "terminal"]
    },
    {
        "goal": "新闻/时事调研",
        "context": f"""你是新闻和时事调研专家。针对以下问题搜索最新新闻报道、行业动态和市场趋势：

问题：{user_question}
重点子问题：{news_sub_queries}

要求：
1. 搜索最近 6 个月内的相关新闻
2. 覆盖不同地区和语言的新闻源（中文+英文）
3. 关注行业报告、融资动态、公司公告
4. 识别趋势和转折点
5. 每条新闻必须附带来源和发布日期
6. 输出格式：
   ## 新闻 N: [标题]
   - 来源: [媒体名 + URL]
   - 日期: [发布日期]
   - 摘要: [核心内容]
   - 影响分析: [与问题的关联]
   - 置信度: HIGH/MEDIUM/LOW
""",
        "toolsets": ["web", "browser"]
    },
    {
        "goal": "学术/论文调研",
        "context": f"""你是学术调研专家。针对以下问题搜索相关学术论文、技术报告和权威文献：

问题：{user_question}
重点子问题：{academic_sub_queries}

要求：
1. 搜索 arXiv、Google Scholar、Semantic Scholar 等学术平台
2. 关注高引用论文和最新发表
3. 提取核心方法论、实验结果、关键结论
4. 对比不同研究团队的观点
5. 每篇论文必须附带标题、作者、年份、链接
6. 输出格式：
   ## 论文 N: [标题]
   - 作者: [作者列表]
   - 年份: [发表年份]
   - 来源: [期刊/会议 + URL]
   - 核心发现: [描述]
   - 方法论: [简述]
   - 与问题的关联: [分析]
   - 置信度: HIGH/MEDIUM/LOW
""",
        "toolsets": ["web", "browser"]
    }
])
```

## Phase 2: 并行审核 Agents

调研结果返回后，启动 4 个独立 reviewer agent 并行审核：

```python
delegate_task(tasks=[
    {
        "goal": "审核 Web 调研结果",
        "context": f"""你是信息验证专家。请审核以下 Web 调研结果的准确性和可信度：

原始问题：{user_question}
调研结果：
{web_research_results}

审核要求：
1. 逐条验证来源 URL 是否可访问、内容是否匹配
2. 交叉检查关键事实（用不同来源验证）
3. 识别潜在偏见（来源是否有利益关联）
4. 检查数据时效性（是否过期）
5. 标注已验证/存疑/已否定的条目
6. 输出格式：
   ## 审核条目 N
   - 原始发现: [引用]
   - 验证状态: ✅已验证 / ⚠️存疑 / ❌已否定
   - 验证依据: [说明]
   - 修正建议: [如有]
""",
        "toolsets": ["web", "browser"]
    },
])
```

每个 reviewer 的 context 中包含：
- 原始用户问题（提供审核上下文）
- 对应 agent 的完整调研结果
- 审核标准和输出格式要求

## Phase 3: 交叉验证 + 圆桌会议

所有审核完成后，启动一个综合 agent：

```python
delegate_task(
    goal="交叉验证与圆桌讨论",
    context=f"""你是资深调研分析师，负责交叉验证来自不同渠道的调研结果并组织圆桌讨论。

原始问题：{user_question}

任务：

1. 【交叉验证】
   - 找出跨渠道一致的发现（增强置信度 -> HIGH）
   - 找出跨渠道矛盾的发现（标记为 CONTESTED）
   - 找出仅单一渠道提及的发现（标记为 MEDIUM/LOW）

2. 【圆桌会议模拟】
   模拟四位专家的圆桌讨论

3. 【输出】
   ## 交叉验证结果
   ### HIGH 置信度发现（多源印证）
   - ...
   ### MEDIUM 置信度发现（部分印证）
   - ...
   ### LOW 置信度发现（单一来源）
   - ...
   ### CONTESTED 发现（来源矛盾）
   - ...

   ## 圆桌讨论纪要
   [按讨论要点组织]

   ## 信息缺口
   [尚未充分覆盖的方面]

   ## 综合结论
   [最终共识]
""",
    toolsets=["web", "browser"]
)
```

## Phase 4: 报告生成

Hermes 自身完成最终报告整合。

## Execution Notes

### 深度级别

根据问题复杂度选择：

| 级别 | 子问题数 | Phase 1 并发 | Phase 2 审核 | Phase 3 |
|------|---------|-------------|-------------|---------|
| Quick | 2-3 | 2 agents (web+github) | 跳过 | 简化 |
| Standard | 4-6 | 4 agents 全开 | 4 reviewers | 完整 |
| Deep | 6-8 | 4 agents + 递归深挖 | 4 reviewers | 完整+补充搜索 |

默认使用 Standard。

### Hermes 适配要点

1. delegate_task batch supports 3 concurrent → Phase 1 dispatch 3 agents
2. Phase 2 reviewers can be skipped when sources are primarily official docs/GitHub
3. 所有 context 传递必须自包含（subagent 无当前对话记忆）
4. Phase 3 的 roundtable agent 用单个 delegate_task 而非 batch

### Phase 2 Skip Heuristic

当 Phase 1 的 subagent 直接访问了一手来源（browser_navigate 到 GitHub 仓库页、官方文档、arXiv 论文页）时，数据已经是一手验证过的，Phase 2 reviewer 的边际价值很低。可以跳过 Phase 2，直接进 Phase 3 交叉验证。

### 迭代追问模式

用户对第一轮报告不满意是常态。常见模式：
1. 用户给出一个具体参考项目 URL，要求以它为锚点重新搜索
2. 用户否定整个方向，需要换赛道

应对：
- 第一轮报告后预留对话空间，不要假设调研结束
- 用户给参考 URL 时，启动一轮 **聚焦调研**（2 agents）

### Adaptive Depth — When to Skip Phases

**⏱️ AUMENTAR timeout de subagentes — eles precisam de tempo para pesquisar bem.**
Pesquisas com 3 subagentes + web_search frequentemente consomem mais que os 600s de timeout
padrão porque cada chamada de API (web_search, web_extract, browser) leva 20-40s com modelos
como DeepSeek V4 Flash. **Configure o timeout máximo disponível** para que subagentes
consigam completar. O usuário prefere relatórios completos mesmo que demorem.

Quando subagentes timeoutam apesar do timeout máximo:
1. O output intermediário pode ser recuperado do state.db (ver `references/subagent-session-recovery.md`)
2. **Não retentar subagentes** — fazer fallback para pesquisa direta com web_search + web_extract
3. A pesquisa direta costuma ser suficiente para cobrir todos os tópicos
4. Documentar os findings em relatórios .md com fontes e níveis de confiança

**🧠 Instrução para contextos de subagentes (sempre incluir):**
- "Não insista em fontes bloqueadas. Se Google, Reddit ou qualquer site retornar bloqueio/CAPTCHA, troque imediatamente para DuckDuckGo (html.duckduckgo.com), Bing, ou URLs diretas de documentação oficial."
- "Se precisar de conteúdo do Reddit, carregue a skill `read-reddit` (usa RSS feeds, sem bloqueio)."
- "Preferir fontes que funcionam (documentação oficial, GitHub, blogs técnicos, artigos acadêmicos) em vez de ficar tentando contornar bloqueios."

> 💡 **Por que não retentar:** Cada tentativa de subagente consome 600s+ sem garantia
> de sucesso. O fallback direto produz resultados equivalentes em 2-3 minutos.

Phase 2 (reviewers) can be skipped when:
- Sources are primarily official docs, GitHub repos, or first-party blog posts
- The question is about tooling/products rather than contested claims or statistics
- Time pressure — reviewer round adds 2-4 minutes with limited value on factual topics

Phase 1 agent selection — drop channels that don't fit:
- Academic agent: skip for tooling/ops/devops topics
- News agent: skip for stable/mature topics with no recent developments
- Minimum: 2 agents (web + github) for Quick depth

3 parallel agents in one delegate_task batch works reliably. Use 3-agent batches as default for Standard depth.

### Local Codebase Analysis (Phase 0.5)

When the research involves "how does project X do it + what are the alternatives", add a Phase 0.5 BEFORE external research:
1. Hermes itself (not a subagent) analyzes the local codebase using search_files/read_file
2. Extract architecture patterns, SDK versions, configuration approaches, dependency choices
3. Feed findings into Phase 1 subagent contexts so they search for relevant alternatives

### Posting Results to GitHub Issues

When creating issues with large markdown research reports:
- **Never** use `gh issue create --body "$(cat <<'EOF' ...)"` or heredoc — special characters cause shell parsing failures
- **Always** write the body to a temp file first, then use `gh issue create --body-file /tmp/report.md`
- Same applies to `gh issue comment --body-file`

### Subagent timeout: recovery via state.db

When subagents timeout after 20+ tool calls, their sessions persist in `/opt/data/state.db`.
Use the queries in `references/subagent-session-recovery.md` to extract partial results.
This is especially valuable when subagents collected URLs or extracted pages before timeout.

### Reference Files

- `references/agent-memory-landscape-2026.md` — Agent memory open-source landscape
- `references/research-to-batch-dev-pattern.md` — Research → batch development pattern
- `references/kusto-investigation.md` — Kusto/ADE investigation patterns
- `references/data-to-frontier-chart.md` — Data compilation and frontier charts
- `references/subagent-session-recovery.md` — Recover partial data from state.db when subagents timeout. SQLite queries, examples, pitfalls.

### Pitfalls

- subagent 的 web 搜索可能返回大量内容，context 要控制在合理长度
- GitHub 搜索注意 rate limit，不要短时间大量请求
- 学术搜索 arXiv API 有时不稳定，准备 Google Scholar 作为 fallback
- reviewer agent 验证 URL 时可能遇到付费墙/地区限制，标注而非失败
- Google/DuckDuckGo may block subagent browser with bot detection — Bing tends to work better as fallback
- **web_search tool returning empty arrays** is a distinct failure mode from "site blocked" — when the tool returns `{"data": {"web": []}}` for every query, the search backend itself is broken/unavailable. Do NOT conclude "no results exist". Instead:
  - Switch to browser-based search (`browser_navigate` to Bing, DuckDuckGo, or Google directly)
  - For people/company research, navigate directly to platform URLs (GitHub, LinkedIn, Instagram, Behance)
  - For technical data, use GitHub API or curl to fetch from known endpoints
  - See `skill_view(name='product-pipeline', file_path='references/persona-research-deep-dive.md')` for detailed techniques
- Phase 2 审核可在来源以官方文档/GitHub 为主时跳过（节省时间和 tokens）
- Phase 3 圆桌 agent 不需要 web/browser toolset（纯分析）
- delegate_task goal 参数不能用 XML 属性语法（`goal">text`），必须用正常 JSON key
- delegate_task API 不能同时传 `goal` 和 `tasks` 参数
- Subagent model availability can fail at runtime (`model_not_supported`). When this happens, **don't retry subagents** — fall back to running directly.
