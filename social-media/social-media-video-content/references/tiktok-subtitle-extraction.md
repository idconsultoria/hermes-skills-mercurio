# TikTok Subtitle Extraction — Session Reference

Extracted from session: watching a TikTok video about "7 SITES QUE MANDAM PRODUTOS DE GRAÇA NA SUA CASA"

## Commands Used

### Get oEmbed metadata (works without auth)
```
curl -s "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@USER/VIDEO_ID&format=json"
```

### Download subtitles only (preferred)
```
yt-dlp --write-subs --sub-lang "por-PT,eng-US" --skip-download --sub-format "vtt" -o "/tmp/tiktok_video" "https://www.tiktok.com/@USER/video/VIDEO_ID"
```
Output: `/tmp/tiktok_video.por-PT.vtt` and `/tmp/tiktok_video.eng-US.vtt`

### Download audio only (fallback for transcription)
```
yt-dlp -x --audio-format mp3 -o "/tmp/tiktok_audio.%(ext)s" "https://www.tiktok.com/@USER/video/VIDEO_ID"
```

### Transcribe with Whisper (last resort)
```
whisper /tmp/tiktok_audio.mp3 --model tiny --language pt -o /tmp/whisper_output
```

## Known Limitations

- TikTok requires yt-dlp with proper dependencies; "impersonation" warnings are benign
- Auto-captions mangle brand names (see mappings in main SKILL.md)
- The internal TikTok API (`/api/item/detail/`) returns empty without auth
- Comments don't load via browser without login
- If host IP is blocked by TikTok (rare), even yt-dlp will fail

## Brand Name Corrections from This Session

| Auto-Caption | Actual Name | URL |
|---|---|---|
| "home test é club" / "nome test é club" | Home Tester Club | hometesterclub.com |
| "bem saída" | The Insiders | theinsidersnet.com |
| "influência ter" / "influenster" | Influenster | influenster.com |
| "bãe bágantil" / "banza gente" | BzzAgent | bzzagent.com |
| "eu quero desleir" / "eu quero nestlé" | Eu Quero Nestlé | euqueronestle.com.br |
| "pinte me" / "pinte mil" / "paint me" | PinchMe | pinchme.com |
| "smile 360" / "7,5,370" | Smile 360 (unconfirmed) | smile360.com (exists, rewards platform?) |
