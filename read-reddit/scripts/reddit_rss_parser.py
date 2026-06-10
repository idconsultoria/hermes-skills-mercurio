#!/usr/bin/env python3
"""
Reddit RSS Parser for IAF Pipeline
Fetches and parses Reddit subreddits via RSS feeds.

Usage:
    python3 reddit_rss_parser.py [--subreddits LIST] [--sort hot|new|top] [--limit N] [--days N]
"""

import xml.etree.ElementTree as ET
import re
import subprocess
import html
import json
import sys
import argparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
NS = {'atom': 'http://www.w3.org/2005/Atom'}

# IAF subreddits organized by category
SUBREDDITS_BY_CATEGORY = {
    "general_ai": ["artificial", "singularity", "ChatGPTPro"],
    "technical": ["LocalLLaMa", "LLMDevs", "MachineLearning"],
    "applied": ["AIAssisted", "SaaS"],
    "data_science": ["datascience"],
    "ethics": ["AIethics"],
}


def fetch_reddit_rss(subreddit, sort="hot", limit=5, time_filter=None):
    """Fetch and parse a single subreddit's RSS feed."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}/.rss?limit={limit}"
    if time_filter:
        url += f"&t={time_filter}"

    result = subprocess.run(
        ["curl", "-sL", "--max-time", "15", "-A", UA, url],
        capture_output=True, text=True
    )
    data = result.stdout

    if not data or "blocked" in data[:500].lower():
        return {"subreddit": subreddit, "error": "blocked", "posts": []}

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return {"subreddit": subreddit, "error": "parse_error", "posts": []}

    posts = []
    for entry in root.findall('atom:entry', NS):
        title_el = entry.find('atom:title', NS)
        link_el = entry.find('atom:link', NS)
        author_el = entry.find('atom:author/atom:name', NS)
        published_el = entry.find('atom:published', NS)
        content_el = entry.find('atom:content', NS)
        category_el = entry.find('atom:category', NS)

        title = html.unescape(title_el.text) if title_el is not None else "No title"
        url = link_el.get('href') if link_el is not None else ""
        author = author_el.text if author_el is not None else "unknown"
        published_str = published_el.text if published_el is not None else ""
        sub_name = category_el.get('label') if category_el is not None else subreddit

        # Extract and clean body text
        body = ""
        if content_el is not None and content_el.text:
            raw = html.unescape(content_el.text)
            body = re.sub(r'<[^>]+>', ' ', raw)
            # Remove Reddit artifacts
            body = re.sub(r'\[\s*link\s*\]', '', body, flags=re.IGNORECASE)
            body = re.sub(r'\[\s*comments\s*\]', '', body, flags=re.IGNORECASE)
            body = re.sub(r'\s*submitted by\s*', '', body)
            body = re.sub(r'\s+', ' ', body).strip()

        posts.append({
            "title": title,
            "url": url,
            "author": author,
            "subreddit": sub_name,
            "published": published_str[:19],  # ISO datetime
            "snippet": body[:500] if body else "",
        })

    return {"subreddit": subreddit, "error": None, "posts": posts}


def fetch_all(subreddits, sort="hot", limit=5, time_filter=None):
    """Fetch multiple subreddits sequentially (for cron use)."""
    results = []
    for sub in subreddits:
        result = fetch_reddit_rss(sub, sort=sort, limit=limit, time_filter=time_filter)
        results.append(result)
    return results


def print_report(results):
    """Pretty-print results for terminal/human reading."""
    for r in results:
        sub = r["subreddit"]
        if r.get("error"):
            print(f"\n❌ r/{sub}: {r['error']}")
            continue
        posts = r["posts"]
        if not posts:
            print(f"\n📭 r/{sub}: (vazio)")
            continue
        print(f"\n📌 r/{sub} ({len(posts)} posts):")
        for p in posts:
            pub_date = p["published"][:10] if p["published"] else ""
            print(f"  📍 {p['title']}")
            print(f"     👤 {p['author']} | 🕐 {pub_date}")
            print(f"     🔗 {p['url']}")
            if p["snippet"]:
                print(f"     📝 {p['snippet'][:200]}")
            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reddit RSS Parser")
    parser.add_argument("--subreddits", "-s", nargs="+",
                        help="List of subreddits to fetch")
    parser.add_argument("--sort", default="hot",
                        choices=["hot", "new", "top", "rising"],
                        help="Sort order (default: hot)")
    parser.add_argument("--limit", "-l", type=int, default=5,
                        help="Posts per subreddit (default: 5)")
    parser.add_argument("--time", "-t", choices=["hour", "day", "week", "month", "year", "all"],
                        help="Time filter (for top sort)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--all", action="store_true",
                        help="Fetch all IAF subreddits")

    args = parser.parse_args()

    if args.all:
        # Flatten all subreddits
        subs = []
        for category_list in SUBREDDITS_BY_CATEGORY.values():
            subs.extend(category_list)
        subs = list(dict.fromkeys(subs))  # deduplicate
    elif args.subreddits:
        subs = args.subreddits
    else:
        subs = ["artificial", "LocalLLaMa"]

    results = fetch_all(subs, sort=args.sort, limit=args.limit, time_filter=args.time)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results)
