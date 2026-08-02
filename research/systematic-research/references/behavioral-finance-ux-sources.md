# Behavioral Finance / Gamified UX Sources

> Research conducted 26 Jul 2026 for CFP IA — a gamified AI financial planner for Brazilian users.
> These URLs were validated to work with `web_extract` and cover behavioral economics, gamification mechanics, nudge theory, and UX for financial apps.

## Behavioral Economics — Encyclopedia Entries

All at `behavioraleconomics.com/resources/mini-encyclopedia-of-be/...`

| Concept | Slug | Key Quote / Data |
|---------|------|------------------|
| Status Quo Bias | `status-quo-bias/` | "Tendency to prefer things to stay the same by doing nothing" — consistent with loss aversion, sunk cost, cognitive dissonance |
| Loss Aversion | `loss-aversion/` | "Pain of losing is psychologically ~2x as powerful as pleasure of gaining" — explains endowment effect, sunk cost fallacy |
| Commitment | `commitment/` | "Greater the cost of breaking a commitment, the more effective" — Dolan et al. 2010 MINDSPACE |
| Precommitment | `precommitment/` | "Save More Tomorrow program: precommit to future savings increases" — Thaler & Benartzi, 2004 |
| Framing Effect | `framing-effect/` | "Choices presented differently lead to different attractiveness" — gains vs losses framing |
| Choice Architecture | `choice-architecture/` | "Organizing the context in which people make decisions" — defaults, framing, decoy |
| Decision Fatigue | `decision-fatigue/` | "Psychological costs to making decisions; long sessions lead to poor choices" |
| (Decision) Inertia | `inertia/` | "Endurance of stable state associated with inaction" — related to status quo bias |
| (Myopic) Procrastination | `myopic-procrastination/` | "People put off decisions due to self-control problems, inertia, complexity" |
| Decision Staging | `decision-staging/` | "Complex decisions → successive exploration of options" — screening alternatives |

## Financial Decision Inertia — Key Research Article

**URL:** `behavioraleconomics.com/nudge-action-overcoming-decision-inertia-in-financial-planning-tools/`

Experiment by Dominik Jung (2019):
- **Control**: 42.1% inertia rate
- **Default nudge**: 29.8% inertia
- **Warning message**: 27.4% inertia
- Warning messages slightly more effective than defaults in financial decisions
- Default nudge triggered **reactance** in some users (deliberately chose opposite)
- Both nudges significantly reduced inertia regardless of financial literacy, risk aversion, age

## Duolingo — Gamification Mechanics (Validated Data)

### Streak Mechanics
**Source:** `blog.duolingo.com/how-duolingo-streak-builds-habit/`
- 6M+ users on streak of 7+ days
- Streak animation on milestones → +1.7% retention at 7 days
- Streak Freeze (up to 2 freezes): +0.38% daily active users
- 7-day streak → 3.6× more likely to complete course
- Loss aversion drives long-streak motivation; novelty drives short-streak motivation

### Friend Streak
**Source:** `blog.duolingo.com/friend-streak/`
- Shared streaks with up to 5 friends
- +22% daily lesson completion with ≥1 Friend Streak
- "Nudge" friends who haven't done their lesson
- Nearly 8M learners with 365+ day streaks

### Motivation Tips
**Source:** `blog.duolingo.com/sticking-with-it-tips-for-staying-motivated/`
- Specific, manageable goals > vague "fluency"
- Daily practice (15-20 min) > cramming
- Link study to existing routine
- Social accountability

## Behavior Models

### Fogg Behavior Model
**Source:** `behaviormodel.org`
- B = MAP (Behavior = Motivation + Ability + Prompt)
- All three must converge at the same moment
- Universal across ages and cultures
- 1,900+ academic publications reference it

### Nudge Theory
**Source:** `en.wikipedia.org/wiki/Nudge_thyme` → `en.wikipedia.org/wiki/Nudge_theory`
- Thaler & Sunstein (2008): "any aspect of choice architecture that alters behavior predictably without forbidding options"
- Controversy: Maier et al. found no significant effect after correcting for publication bias
- Personalized nudges more effective than "one-nudge-for-all"
- Default effect is one of the most robust techniques

### Time Preference / Hyperbolic Discounting
**Source:** `en.wikipedia.org/wiki/Time_preference`
- People value immediate rewards disproportionately more than future ones
- Core mechanism behind overspending and undersaving
- Applications: retirement savings, credit card debt, health decisions

### Gamification
**Source:** `en.wikipedia.org/wiki/Gamification`
- Game elements: points, badges, leaderboards, levels, progress bars, narrative
- Motivations: socializing, mastery, competition, achievement, status
- Leaderboards have mixed motivational potential (Werbach & Hunter)

## UX for Financial / Sensitive Topics

### Design Principles (Synthesized)
1. **Empathy first** — coach tone, not auditor
2. **Progress over perfection** — celebrate small wins
3. **Reduce cognitive load** — IA does calculations, user approves actions
4. **Avoid triggering anxiety** — show installment plans, not total debt
5. **Transparency** — no dark patterns
6. **Accessibility** — simple language, visual calculators, large fonts

### Dark Patterns to Avoid
| Pattern | Description | Alternative |
|---------|-------------|-------------|
| Confirmshaming | "You really want to stay in debt?" | Positive framing |
| Hidden costs | Fees revealed at checkout | All costs upfront |
| Nagging | Excessive notifications | User-controlled frequency |
| Forced continuity | Hard to cancel | 1-click cancel |
| Roofnailing | Hidden costs/terms | Full transparency |

### Cognitive Scarcity (Mullainathan & Shafir)
- Financial stress reduces cognitive bandwidth equivalent to losing a night of sleep
- Users under scarcity make more impulsive, less planned decisions
- Implication: app must do the heavy lifting; user only approves

## General Wikipedia Overview Pages (Reliable)

| Page | URL | Used For |
|------|-----|----------|
| Nudge theory | `en.wikipedia.org/wiki/Nudge_theory` | Core theory, types of nudges, controversy |
| Gamification | `en.wikipedia.org/wiki/Gamification` | Game elements, techniques, applications |
| Behavioral economics | `en.wikipedia.org/wiki/Behavioral_economics` | History, key concepts, development |
| Time preference | `en.wikipedia.org/wiki/Time_preference` | Hyperbolic discounting, present bias |
