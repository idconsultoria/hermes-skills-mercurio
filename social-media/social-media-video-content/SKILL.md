---
name: social-media-video-content
description: "Extract subtitles, descriptions, and metadata from social media videos.

Load this skill when the user sends a TikTok, Instagram Reel, or YouTube Shorts URL and needs transcript, summary, or spoken content extraction — especially when the browser can't play the video."
version: 1.0.0
type: ToolIntegration
timestamp: 2026-06-28T19:30:00Z
---

# Social Media Video Content Extraction

Extract text content (subtitles, descriptions, metadata) from social media video platforms — especially when the browser can't play the video (login wall, geo-block, rate limiting).

## Trigger

Use this skill when:
- User sends a TikTok / Instagram Reel / YouTube Shorts URL and asks what the video says
- User wants a list, transcript, or summary of content in a social media video
- A video platform blocks browser playback (login required, "trouble playing this video")

## Workflow

### 1. Try the most direct path — only once

DON'T fight the browser longer than one attempt. If TikTok returns "We're having trouble playing this video" or Instagram demands login, bail immediately and use yt-dlp.

### 2. Extract subtitles with yt-dlp (preferred path)

```bash
yt-dlp --write-subs --sub-lang "por-PT,eng-US" --skip-download --sub-format "vtt" -o "/tmp/video_output" "<VIDEO_URL>"
```

- TikTok usually has both `por-PT` (Portuguese) and `eng-US` (English) auto-generated captions
- VTT files are small (2-3KB) and download in seconds
- Read the Portuguese subtitle as primary source; cross-check with English for clarity

### 3. Read and validate

After getting the transcript:
1. Read the Portuguese VTT file first
2. Compare with English VTT for any unclear segments
3. Search the web to verify platform/brand names — auto-captions often mangle them:
   - "pinte me" → PinchMe (pinchme.com)
   - "bãe bágantil" / "banza gente" → BzzAgent (bzzagent.com)
   - "home test é club" / "nome test é club" → Home Tester Club (hometesterclub.com)
   - "bem saída" → The Insiders (theinsidersnet.com)
   - "influência ter" / "influenster" → Influenster (influenster.com)
   - "eu quero desleir" → Eu Quero Nestlé (euqueronestle.com.br)
   - "smile 360" → verify independently (name may vary)
4. Always include the verified URL/site name in the final answer

### 4. oEmbed metadata (quick check — optional)

```bash
curl -s "https://www.tiktok.com/oembed?url=<VIDEO_URL>&format=json"
```

Returns title (hashtags), author, thumbnail. Use for quick context before subtitle download.

### 4b. Instagram Reels — métricas de print + URL pública

Para pedidos de métricas de Reels (likes, comments, views, legenda) a partir de
screenshot ou URL, ver `references/instagram-reels-metrics.md`. Resumo: o print
(analisado com vision) mostra likes/comments/shares/direct/saves — **views nunca
aparecem no overlay**; a URL pública via curl com user-agent mobile expõe a
`<meta name="description">` com "X likes, Y comments - @handle on <data>: <legenda
completa>". Views exigem dashboard profissional ou Graph API — nunca inventar.

### 5. Fallback: download + transcribe audio

Only if no subtitles exist and content is critical:

```bash
yt-dlp -x --audio-format mp3 -o "/tmp/audio.%(ext)s" "<VIDEO_URL>"
whisper /tmp/audio.mp3 --model tiny --language pt -o /tmp/whisper_output
```

This is SLOW (60-120s) and CPU-heavy. Use ONLY as last resort. If subtitles are available, deliver immediately — don't transcribe.

## Pitfalls

- **Over-engineering**: If subtitles download successfully (step 2), STOP. Do NOT install whisper, do NOT try other transcription. Deliver the result.
- **TikTok browser block**: Shows "We're having trouble playing this video" without login. One attempt, then switch to yt-dlp immediately.
- **TikTok API endpoints** (`/api/item/detail/`): Return empty without auth cookies. Don't waste time.
- **Comments**: Don't load without login. Not a viable source.
- **yt-dlp impersonation warning**: "extractor is attempting impersonation, but no impersonate target" is a harmless WARNING. Subtitles download fine.
- **Whisper CPU mode**: `FP16 is not supported on CPU; using FP32 instead` is normal. Warns but works.

## Verification

- Cross-reference auto-captioned brand names with web search — they're often garbled
- Present the final list with verified URLs, not just names from the transcript
- If a name can't be verified independently (e.g. "Smile 360"), note it explicitly rather than guessing
