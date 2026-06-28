# Delivery Escalation Rules

When processing manga volumes for Kindle, follow this priority order:

## Quality tiers

| Tier | Quality | Delivery | When |
|------|---------|----------|------|
| A | **Q85** | Google Drive (Send-to-Kindle app, 200 MB limit) | Source is good (>=1000px wide), user accepts Drive |
| B | **Q75** | Gmail email (25 MB limit) | 1 chapter, source >=1000px |
| C | **Q65** | Gmail email (25 MB limit) | 1-2 chapters, edge case |
| D | **Q55** | Gmail email (25 MB limit) | Only if source is >=1000px. Check size first |
| E | **Q30-Q25** | Gmail email, absolute floor | Tiny sources (~460px), with user approval |
| F | **Q85** | Google Drive | Sources too large for email even at Q25 |

## Escalation flow

1. Find a high-quality source first (>=1000px wide, EPUB >100 MB)
2. Process at Q85 for Drive delivery
3. If user asks for Gmail delivery, try Q75 then Q65 then Q55
4. If even Q55 exceeds 25 MB, do NOT go below Q50 without user approval
5. Upload to Drive at Q85 and share the link

## Source quality checklist

Before downloading, check:
- File under 30 MB for 200 pages? = Text PDF, skip
- Filename has [LQ]? = Low Quality, warn
- Filename has [MS]? = text-as-separate-image issue
- EPUB >100 MB per 200 pages? = Good quality
- CBZ >400 MB per volume? = Excellent (danke-Empire HD, CM)

## Common sources

| Series | Best source | Collection | File pattern |
|--------|-------------|-----------|--------------|
| One Piece | readonepiece.com (weekly) | N/A - CDN grab | `cdn.readonepiece.com/file/CDN-M-A-N/op_N_nnd_PPP.png` |
| Monster | CM Complete Edition | monster-manga | Monster vNN (CM).epub |
| Berserk | danke-Empire HD | manga_Berserk | !Berserk [danke-Empire]{HD}/Berserk vNN ... .epub |
| Berserk | Hawks (email-friendly) | manga_Berserk | Berserk - XXX-XXX (vNN) [Hawks].epub |
