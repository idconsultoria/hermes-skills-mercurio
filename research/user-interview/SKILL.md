---
name: user-interview
description: "Structured user/proxy interview protocol for product research — plan, frame

Load this skill during the Research phase of the product pipeline to understand user needs. Covers interview planning, question framing, active listening techniques, synthesis of findings, and persona extraction. Can interview real humans or simulate interviews with AI agent profiles."

Load this skill during the Research phase of the product pipeline to understand user needs. Covers interview planning, question framing, active listening techniques, synthesis of findings, and persona extraction. Can interview real humans or simulate interviews with AI agent profiles."
category: research
type: Research
timestamp: 2026-06-12T02:23:22Z
---

# User Interview

> **Core principle:** A good interview is a conversation, not a questionnaire.
> The best insights come from what users *don't* say — hesitation, emotion,
> workarounds, and the stories they tell.

## When to Load This Skill

- During the Research phase (Fase 2) of the product pipeline
- Understanding user needs, pain points, and behaviors
- Before defining personas or user stories
- Testing assumptions about who the user is and what they need
- **Simulating** interviews when real users aren't available

---

## 1. Interview Planning

### 1.1 Types of Interviews

| Type | When | Length | Format |
|------|------|--------|--------|
| **Discovery** | Early, problem space | 30-60min | Open-ended, exploratory |
| **Validation** | Testing a concept | 20-30min | Semi-structured with prototype |
| **Contextual** | In user's environment | 45-90min | Observation + questions |
| **Diary Study** | Over time (days/weeks) | 5min/day | Self-reported, longitudinal |
| **Agent Simulation** | No real users available | 15-30min | Hermes simulates the user |

### 1.2 Recruitment Criteria

Before interviewing, define:

```
User Profile: [Who we need to talk to]
  - Role: [e.g., "Project manager at a 10-50 person agency"]
  - Behavior: [e.g., "Uses at least 3 tools for project tracking"]
  - Pain: [e.g., "Says 'status reports take too long' in screening"]
  - Exclude: [e.g., "People who work alone, no team"]

Minimum participants: 5 per user segment
Ideal: 8-10 per segment
Saturation: When you stop hearing new information (usually 5-8)
```

---

## 2. Question Framing

### 2.1 The Question Ladder

| Level | Question Type | Example |
|-------|--------------|---------|
| **5. Dreams** | Aspirational | "If you could wave a magic wand, what would this look like?" |
| **4. Feelings** | Emotional | "How did you feel the last time this went wrong?" |
| **3. Behaviors** | Past actions | "Tell me about the last time you did X. Walk me through it." |
| **2. Facts** | Concrete | "How often do you do X?" |
| **1. Opinions** | Surface level | "Do you like tool X?" |

**Rule:** Start at level 2-3 (behaviors + facts). Go up for inspiration, down for confirmation. Never stop at level 1.

### 2.2 Good vs. Bad Questions

| ❌ Bad | ✅ Good |
|--------|---------|
| "Would you use a tool that does X?" | "Tell me about the last time you had to do X." |
| "How important is Y to you?" | "What happens when Y doesn't work? Walk me through a specific example." |
| "Do you like feature Z?" | "Tell me about a time when Z was really useful — and a time it let you down." |
| "What features would you want?" | "What does your ideal workflow look like? What's missing from today's?" |
| "Is this easy to use?" | "Show me how you do this. Where do you get stuck?" |

### 2.3 The 5-Why Technique

Start with a behavior, then ask "why" (or "tell me more") 5 times:

```
1. "I use spreadsheets to track projects"
   → "Why spreadsheets instead of a dedicated tool?"
2. "Because I tried tool X and it was too complex"
   → "What specifically was complex about it?"
3. "I had to configure 20 fields before I could create a project"
   → "Why was that a problem for you?"
4. "Because I don't have 2 hours to set up — I need it working in 5 minutes"
   → "And why is 5 minutes the threshold?"
5. "Because by the time I finish setup, I've already found a workaround and lost motivation"
```

**Result:** The real problem isn't "spreadsheets vs tools" — it's "instant gratification vs investment."

---

## 3. Interview Structure (60min)

| Phase | Time | Purpose |
|-------|------|---------|
| **1. Warm-up** | 5min | Build rapport, explain context |
| **2. Background** | 10min | Current role, tools, workflow |
| **3. Deep dive** | 25min | Specific behaviors, pain points, stories |
| **4. Concept test** | 10min | (if applicable) Show idea, get reaction |
| **5. Wrap-up** | 10min | Summary, open floor, thank you |

### Phase 1: Warm-up Script

```
"Thanks for taking the time. I'm [Name], working on [Project].
We're trying to understand how people currently handle [Problem area].
There are no right or wrong answers — we're learning from you.
I'll be recording notes so I don't miss anything. Any questions before we start?"
```

### Phase 3: Deep Dive Prompts

```
"Walk me through your typical [day/week/month]. Start from the beginning."
"Tell me about the last time [specific pain point] happened."
"What's the part of your workflow that frustrates you most right now?"
"Have you tried to solve this before? What happened?"
"Describe the ideal outcome. What would your day look like if this problem disappeared?"
```

---

## 4. Active Listening Techniques

| Technique | How | Why |
|-----------|-----|-----|
| **Mirroring** | Repeat the last 1-3 words as a question | Encourages elaboration |
| **Paraphrasing** | "So if I understand correctly, you..." | Validates understanding |
| **Pausing** | Stay silent after an answer | User fills the gap with more detail |
| **Probing** | "Tell me more about that" | Deepens surface answers |
| **Emotional labeling** | "That sounds frustrating" | Validates feelings, builds trust |
| **Summarizing** | "Let me make sure I got this right..." | Tests understanding |

---

## 5. Simulation Mode (AI Agent Interviews)

When interviewing an **AI agent persona**, adapt:

### 5.1 For AI Agents as Users

If an AI agent will *use* your product (API, tool, integration):

```
Interview prompt for simulating an AI agent:

"You are [Agent name], an AI assistant specialized in [domain].
You will be a user of [Product], which does [value prop].
[Describe the integration context.]

Answer the following as yourself (the AI agent). Consider:
- What information would you need from this tool?
- What format works best for machine-to-machine interaction?
- What latency, throughput, or reliability constraints matter?
- How would you compose this with other tools in your stack?
- What would make you choose this vs. writing a custom script?
```

### 5.2 For Human User Simulation

When no real users are available:

```
"Simulate a 30-minute user interview with [Persona description].
You are playing the role of [Name], a [role] at [company type].

I will ask questions. Answer as the persona would:
1. Be specific, use concrete examples, mention real tools
2. Show some emotion (frustration, excitement, indifference)
3. Occasionally be contradictory (real users aren't perfectly consistent)
4. Don't give me what you think I want to hear
5. Mention workarounds you've created

Start: 'Tell me about your role and what a typical day looks like.'"
```

---

## 6. Synthesis & Documentation

### 6.1 Individual Interview Summary

After each interview (real or simulated), produce:

```markdown
## Interview Summary: [Persona/Role]

**Date:** [Date]
**Type:** [Real/Simulated]
**Context:** [Brief]

### Key Quotes
> "Quote 1 — reveals [insight]"
> "Quote 2 — reveals [insight]"

### Observed Pain Points
1. [Pain] — [severity/frequency]
2. [Pain] — [severity/frequency]

### Desired Outcomes
1. [What they want to achieve]
2. [What "good" looks like to them]

### Surprises / Non-Obvious Insights
- [Something unexpected that challenges an assumption]

### Emotional Arc
[Brief description of emotional journey during the interview]
```

### 6.2 Cross-Interview Synthesis

After 5+ interviews, synthesize:

```markdown
## Cross-Interview Synthesis: [Topic]

**Participants:** [N] interviews

### Recurring Themes (3-5)
1. [Theme] — mentioned by [N] participants
   - Evidence: [quotes], [observations]
   - Implications: [design direction]

### Persona Cluster
Based on patterns, [N] distinct user profiles emerge:
1. [Persona 1] — [brief, key need]
2. [Persona 2] — [brief, key need]

### Confidence Rating
- High confidence findings (5+ participants): [list]
- Medium confidence (3-4 participants): [list]
- Low confidence (1-2 participants): [list — probe further]

### Open Questions
1. [Question to answer in next round]
```

---

## 7. Interview Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| **Leading questions** | "Don't you think X is useful?" | "Tell me about a time you needed X" |
| **Asking about the future** | Users are bad at predicting | Ask about past behavior |
| **Too many questions** | Fatigue → shallow answers | 5-8 core questions max |
| **Defending the idea** | User won't criticize if you defend | "What would make you NOT use this?" |
| **Confirmation bias** | Only hearing what supports your hypothesis | Actively seek disconfirming evidence |
| **Notes during talking** | Misses non-verbal cues | Record (with permission), write notes after |
| **Interrupting** | Cuts off elaboration | Count to 3 after they finish before speaking |
