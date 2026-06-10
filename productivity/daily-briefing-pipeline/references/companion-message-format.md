# Companion Message Format (WhatsApp / Telegram Text)

After delivering the main PDF report, provide a short text companion that can be copied and shared on messaging platforms.

## Format Rules (refined through IAF user feedback)

- **Emoji header** before the newsletter name
- **Bold first sentence** of the editorial
- **Section emojis** before each section header
- **Score-based selection**: bullets = top N scores from ranking, regardless of content type
- **Code block** for copy-paste preservation

## Canonical Template

```text
📰 *NEWSLETTER NAME* · DD/MM/AAAA

*[BOLD HOOK SENTENCE]* Remaining editorial paragraph. Opinionated, data-backed, tight.

🔥 *Destaques do dia*
• [Top 1 do ranking — bullet impactante + contexto]
• [Top 2 do ranking — bullet impactante + contexto]
• [Top 3 do ranking — bullet impactante + contexto]

🎯 *Aplicação prática de hoje:* [1 linha — spoiler da aplicação prática]
```

## Variable Parts

| Element | Rule |
|---------|------|
| 📰 emoji | Always before newsletter name |
| 🔥 emoji | Before "Destaques do dia" |
| 🎯 emoji | Before "Aplicação prática" |
| Bold hook | First sentence of editorial, ** in markdown |
| 3 bullets | Top N scores from the ranking (any content type) |
| Aplicação prática | Single line, benefit-focused |

## Verification Checklist

**Known issue**: autonomous cron agents frequently drop formatting elements even when the prompt specifies them exactly. Always verify the delivered message against this checklist:

| Element | Expected | Actual |
|---------|----------|--------|
| 📰 before title | ✅ Present | Check |
| 🔥 *Destaques do dia* header | ✅ Present before bullets | Check |
| 🎯 header | ✅ Present | Check |
| 3 bullets format | `• [title] — [desc]` | Check |
| No extra text | No ranking table, no signature | Check |

**Most commonly dropped**: 📰 emoji and the 🔥 *Destaques do dia* section header — the bullets end up floating without a header.
