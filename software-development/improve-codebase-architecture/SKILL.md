---
name: improve-codebase-architecture
description: "Scan a codebase for deepening opportunities and present them as a structured HTML report with prioritized recommendations.

Load this skill when you need to identify architectural friction and deepening opportunities in a codebase. Covers design vocabulary, domain modeling, ADR workflows, and grilling through selected opportunities — all self-contained with zero external skill dependencies."
category: software-development
type: Orchestrator
timestamp: 2026-06-28T05:11:55Z
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This skill is fully self-contained. All design vocabulary, deepening strategies, domain modeling workflows, and report templates are included below or in the `references/` directory. No external skills required.

---

## Architecture Vocabulary

Use these terms exactly — don't substitute "component," "service," "API," or "boundary." Consistent language is the whole point.

### Glossary

**Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. _Avoid_: unit, component, service.

**Interface** — everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. _Avoid_: API, signature (too narrow — they refer only to the type-level surface).

**Implementation** — what's inside a module, its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth** — leverage at the interface: the amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Seam** _(Michael Feathers)_ — a place where you can alter behaviour without editing in that place; the _location_ at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes _role_ (what slot it fills), not substance (what's inside).

**Leverage** — what callers get from depth: more capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere.

### Deep vs shallow

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

**Deep module** = small interface + lots of implementation.

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid).

When designing an interface, ask:
- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

### Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, mockable, swappable parts — they just aren't part of the interface. A module can have **internal seams** (private to its implementation, used by its own tests) as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test _past_ the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a seam unless something actually varies across it.

### Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them.**
   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, don't produce side effects.**
   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test setup.

### Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

### Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.

---

## Deepening Guide

How to deepen a cluster of shallow modules safely, given its dependencies. See also `references/DEEPENING.md` for the full reference.

### Dependency categories

When assessing a candidate for deepening, classify its dependencies:

| Category | Description | Test Strategy |
|----------|-------------|---------------|
| **In-process** | Pure computation, in-memory state, no I/O | Always deepenable. Merge modules, test through the new interface directly. No adapter needed. |
| **Local-substitutable** | Dependencies with local test stand-ins (PGLite for Postgres, in-memory filesystem) | Deepenable if stand-in exists. Test with stand-in running in suite. Seam is internal. |
| **Ports & Adapters** | Your own services across a network (microservices, internal APIs) | Define a port (interface) at the seam. Inject transport as adapter. Tests use in-memory adapter. |
| **True external (Mock)** | Third-party services (Stripe, Twilio) you don't control | Inject as port. Tests provide mock adapter. |

### Seam discipline

- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation) as well as the external seam. Don't expose internal seams through the interface just because tests use them.
- **One adapter means hypothetical. Two means real.** Don't introduce a port unless at least two adapters are justified (production + test).

### Testing strategy: replace, don't layer

- Old unit tests on shallow modules become waste once tests at the deepened module's interface exist — delete them.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation.

---

## Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the _active_ discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions the moment they crystallise.

### File structure

Most repos have a single context:
```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives. Create files lazily — only when you have something to write.

### CONTEXT.md format

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

Rules:
- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include domain-specific terms.** General programming concepts don't belong.
- CONTEXT.md should be totally devoid of implementation details. It is a glossary and nothing else.

See `references/CONTEXT-FORMAT.md` for multi-context repos and full rules.

### ADR format

ADRs live in `docs/adr/` with sequential numbering: `0001-slug.md`, `0002-slug.md`.

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

An ADR can be a single paragraph. The value is in recording _that_ a decision was made and _why_ — not in filling out sections.

**Only offer to create an ADR when all three are true:**
1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

See `references/ADR-FORMAT.md` for full template, optional sections, and what qualifies.

---

## Process

### 1. Explore

Read the project's domain glossary (`CONTEXT.md`) and any ADRs in the area you're touching first.

Then walk the codebase organically. Don't follow rigid heuristics — explore and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals for more editorial diagrams (mass diagrams, cross-sections, collapse animations).

For each candidate, render a card with:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength** — one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and the architecture vocabulary from this skill for the architecture.** If CONTEXT.md defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card with a warning callout: _"contradicts ADR-0007 — but worth reopening because…"_. Don't list every theoretical refactor an ADR forbids.

See `references/HTML-REPORT.md` for the full HTML scaffold, diagram patterns, and styling guidance.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, walk the design tree with them:

#### Challenge against the glossary
When the user uses a term that conflicts with the existing language in CONTEXT.md, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

#### Sharpen fuzzy language
When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User?"

#### Discuss concrete scenarios
Stress-test domain relationships with specific edge-case scenarios. Invent scenarios that force precision about boundaries between concepts.

#### Cross-reference with code
When the user states how something works, check whether the code agrees. "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

#### Update CONTEXT.md inline
When a term is resolved, update `CONTEXT.md` right there. Don't batch — capture as they happen.

#### Offer ADRs sparingly
Only offer an ADR when the three criteria are met (hard to reverse, surprising, real trade-off):
- **Naming a deepened module after a concept not in CONTEXT.md?** Add the term.
- **Sharpening a fuzzy term?** Update CONTEXT.md right there.
- **User rejects a candidate with a load-bearing reason?** Offer an ADR: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer.
- **Want to explore alternative interfaces?** See `references/DESIGN-IT-TWICE.md` — spin up parallel sub-agents to design the interface several radically different ways, then compare on depth, locality, and seam placement.

---

## Tone & Vocabulary Rules

- Use exactly: **module**, **interface**, **implementation**, **depth**, **deep**, **shallow**, **seam**, **adapter**, **leverage**, **locality**.
- Never substitute: component, service, unit (for module) · API, signature (for interface) · boundary (for seam) · layer, wrapper (for module, when you mean module).
- Phrasings that fit: "Order intake module is shallow — interface nearly matches the implementation." / "Pricing leaks across the seam." / "Deepen: one interface, one place to test."
- Benefits bullets name the gain in glossary terms: _"locality: bugs concentrate in one module"_, _"leverage: one interface, N call sites"_.
- No hedging, no throat-clearing, no "it's worth noting that…".

---

## Reference Files

All in `references/` within this skill's directory:

| File | Content |
|------|---------|
| `DEEPENING.md` | Full deepening guide: dependency categories, seam discipline, testing strategy |
| `DESIGN-IT-TWICE.md` | Parallel sub-agent pattern for exploring alternative interfaces |
| `CONTEXT-FORMAT.md` | CONTEXT.md format, single vs multi-context repos |
| `ADR-FORMAT.md` | ADR template, numbering, when to offer |
| `HTML-REPORT.md` | HTML scaffold, diagram patterns, style guidance for architecture review reports |

Load any reference with `skill_view(name='improve-codebase-architecture', file_path='references/<name>')`.
