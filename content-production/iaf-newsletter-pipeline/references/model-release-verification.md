# Model Release Verification — Point Releases (0813, 0731, etc.)

How to verify what actually changed when a model gets a dated point-release (GA,
official build) — and avoid treating it as "the same model relabeled".

Trigger: special edition or news item about a model version with a date in the
name (DeepSeek-V4-Pro-0813, V4-Flash-0731, ...) or a "GA / official" label after
a preview period.

## The trap (proven 12/08/2026)

The DeepSeek V4 Pro 0813 GA edition was initially written using April preview-era
sources (Unite.AI, Hugging Face model card) and concluded the GA was "the same
preview, just relabeled". The user corrected: the GA is a NEW checkpoint
(re-post-trained), with massive agentic gains (DeepSWE 12.8 → 62.7, Terminal
Bench 2.1 72.1 → 87.9). Lesson: **a version bump can change everything even when
architecture and parameter count are unchanged.** Never assert "same model" from
specs alone — check the build's own benchmark deltas.

## Primary-source checks (fast, no tokens for articles)

```bash
# 1. Hugging Face: newest repos by the org (see if a -0813/-0731 repo appeared)
curl -s "https://huggingface.co/api/models?author=<org>&sort=lastModified&direction=-1&limit=15"

# 2. HF repo info + last commits (did the existing repo get updated today?)
curl -s "https://huggingface.co/api/models/<org>/<Model-Name>"
curl -s "https://huggingface.co/api/models/<org>/<Model-Name>/commits/main?limit=8"

# 3. HF global search for the version string (mirrors/quants?)
curl -s "https://huggingface.co/api/models?search=V4-Pro-0813&limit=10"

# 4. ModelScope (Chinese orgs often publish there too)
curl -s "https://modelscope.cn/api/v1/models/<org>/<Model-Name>"   # check LastUpdatedTime (epoch)

# 5. Official changelog RAW (web_extract may serve stale cache; grep the HTML directly)
curl -s "https://api-docs.deepseek.com/updates" | grep -o -i "0813\|2026-08-1[0-9]" | sort -u

# 6. OpenRouter model page for the EXACT build string
#    https://openrouter.ai/<org>/<model>-<build>
```

Interpretation:
- New repo or updated repo for the build = weights published.
- Changelog line = official announcement. If absent, the release can still be
  real: check the pricing-page model-version string + third-party trackers +
  leaked tables (e.g. official WeChat group) — then say "sem comunicado oficial"
  rather than "não houve release".
- Search strictly for the version string in web_search; preview-era articles
  describe the OLD build and will mislead you.

## Always include (launch <24h old)

- Benchmarks are vendor-reported.
- Which harness they were run with (may be proprietary / unreleased — e.g.
  DeepSeek Harness) and whether any independent evaluator replicated them yet.
- Community hands-on tests (HN/Reddit) — often mixed vs. the headline table.
- What is NOT published yet (official announcement, updated tech report, open
  weights) — frame as "API-first pattern", not as a thesis.
