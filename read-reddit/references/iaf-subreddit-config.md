# IAF Subreddit Configuration

Subreddits monitored for the "IAF — Manhã Aumentada" daily AI report pipeline.

## General AI

| Subreddit | Sort | Limit | Notes |
|-----------|------|-------|-------|
| r/artificial | hot + top/day | 5 | High activity. Best source for general AI discussion. |
| r/Singularity | hot | 5 | Moderate activity. Filter out low-effort posts. |
| r/ChatGPTPro | hot + top/day | 5 | Good quality. Some posts are weeks old on top/day. |

## Technical / Developer

| Subreddit | Sort | Limit | Notes |
|-----------|------|-------|-------|
| r/LocalLLaMa | hot + top/day | 5 | Very active. Hardware, open models, quantization. |
| r/LLMDevs | hot | 5 | Low-moderate activity. Technical dev content. |
| r/MachineLearning | hot | 5 | Structured (weekly threads). Filter for [R] and [D] posts. |

## Applied AI

| Subreddit | Sort | Limit | Notes |
|-----------|------|-------|-------|
| r/AIAssisted | hot | 5 | Low activity. Keep as supplement. |
| r/SaaS | hot | 5 | Good for AI-in-business discussion. |

## Data & Ethics

| Subreddit | Sort | Limit | Notes |
|-----------|------|-------|-------|
| r/datascience | hot | 5 | Low AI signal. Mostly career questions. |
| r/AIethics | hot | 3 | Very low activity. May return 0 posts. Consider dropping if consistently empty. |

## Multi-Reddit URL (for manual testing)

```
https://www.reddit.com/r/artificial+LocalLLaMa+ChatGPTPro+AIAssisted+LLMDevs+SaaS+Singularity+datascience+MachineLearning+AIethics/hot/.rss?limit=5
```

## Fetch Script

Use the companion script at `scripts/reddit_rss_parser.py` with:

```bash
python3 scripts/reddit_rss_parser.py --all --sort hot --limit 5
python3 scripts/reddit_rss_parser.py --all --sort top --time day --limit 5
```

Combine both outputs — `hot` catches what's trending now, `top/day` catches what was best in the last 24 hours.
