# Copywriting + Humanizer Quality Pipeline for IAF

This reference defines how the synthesis cron applies the quality pipeline for the IAF report. The goal is "redação gostosa e impecável" (delightful and impeccable writing) with "facilitação visual" (visual facilitation).

## Three-Pass System

### Pass 1: Copywriting Principles (coreyhaines31 copywriting)

Apply before prose generation — these are the design constraints for the writer:

1. **Clarity over cleverness**: If a sentence is hard to parse, rewrite it. No wordplay that obscures meaning.
2. **Benefits over features**: Don't say "Model X has 128K context." Say "Model X can read your entire codebase at once."
3. **Specificity over vagueness**: "Cut reporting from 4h to 15min" not "Save time."
4. **Customer language**: Use the words practitioners actually use (from forum scraping). Don't invent terminology.
5. **One idea per section**: Each paragraph makes one point. No kitchen-sink paragraphs.
6. **Active voice**: "OpenAI released GPT-5" not "GPT-5 was released by OpenAI."
7. **Confident tone**: Remove "almost", "very", "really", "quite". Say what you mean.
8. **Simple over complex**: "Use" not "utilize." "Help" not "facilitate." "Show" not "demonstrate."
9. **No exclamation points**: They cheapen the prose. Let the content be exciting, not the punctuation.

### Pass 2: Humanizer (Humanizer skill — blader/humanizer)

Run AFTER the first draft. Target these patterns specifically:

**HIGH PRIORITY (remove all instances):**
- 🚫 "stands/serves as a testament" → just say what it is
- 🚫 "in today's rapidly evolving [X] landscape" → delete, start with the fact
- 🚫 "underscores/highlights the importance" → the fact itself should show importance
- 🚫 "it's not just about X, it's about Y" (negative parallelism) → rewrite
- 🚫 "-ing" signposting: "highlighting how...", "showcasing why...", "underscoring that..." → delete the -ing clause
- 🚫 "Let's dive in / explore / break this down" → just start writing
- 🚫 "Here's what you need to know" → delete, show instead
- 🚫 Em dash overuse (—) — max 1 per paragraph, use periods or commas instead
- 🚫 Rule of three (everything in groups of three) — break it, vary it
- 🚫 Vague attributions: "Industry experts say", "Observers have noted" → either name the source or cut it
- 🚫 "As of [date]" / "Up to my knowledge cutoff" → remove
- 🚫 "It is important to note that" → just say the thing

**MEDIUM PRIORITY (reduce):**
- ⚠️ Synonym cycling (calling the same thing "model", "LLM", "system", "AI" in adjacent sentences) — pick one and stick with it
- ⚠️ Hyphenated compound overuse: "data-driven", "real-time", "high-quality" — remove hyphens where natural
- ⚠️ Boldface overuse — only bold what genuinely needs emphasis
- ⚠️ Title Case in headings — use Sentence case

**PERSONALITY INJECTION (add):**
- Vary sentence length. Short. Then long and winding. Then punchy again.
- Use "I" when giving an opinion: "I keep coming back to this because..."
- Acknowledge complexity: "This is genuinely impressive but also kind of unsettling."
- Be specific about reactions: not "this is concerning" but "there's something sobering about watching models debate each other."
- Use rhetorical questions: "What does this mean for someone building with LangChain today?"
- Add transition with voice: "Here's the part that surprised me." / "What the thread below gets right is..."

### Pass 3: IAF Voice Calibration

After Pass 2, reread the report and ask:

1. **Would this pass the "café" test?** — If you were telling a smart colleague about this over coffee, would you sound like this?
2. **Is there too much distance?** — If it reads like a wire report, add more opinion and reaction.
3. **Is there too much personality for the topic?** — If a story is genuinely serious (regulation, job displacement, ethics), respect that weight. Don't crack jokes about layoffs.
4. **Is the Portuguese natural?** — Mix of formal and colloquial. Use Portuguese idiom where it fits. Keep English terms only when they're the standard industry term (LLM, fine-tuning, RAG, agent).
5. **Is the visual flow good?** — Short section intros, clean spacing, emoji headers for scannability. The reader should be able to get the gist by reading only the bold text and section headers.

## Copywriting + Humanizer + IAF Voice: Quick Reference

| Layer | What it does | Applied when |
|-------|-------------|-------------|
| Copywriting | Structure, clarity, specificity | Before drafting |
| Humanizer | Strip AI-isms, add voice | After draft 1 |
| IAF Voice | Brazilian Portuguese calibration, technical English mix, café test | After Humanizer |
