# Deck / Presentation Generation from Newsletter Content

## Use Case

Generate a multi-slide HTML presentation deck from newsletter or report content, using agy + brand identity.

## Pipeline

### 1. Extract newsletter content

The newsletter is stored as HTML at paths like `/opt/data/cron/history/iaf_YYYY-MM-DD.html`. Extract key sections.

### 2. Write deck prompt

Structure the prompt with:
- Brand identity (colors, fonts, logo SVG spec)
- Slide-by-slide outline (10 slides is a good default count)
- Newsletter content for each slide
- Design rules (anti-slop, navigation style, animations)

**Slide structure that works for daily newsletters:**
1. Title (newsletter name + date + tagline + logo)
2. Hot take (big stat + brief + quote)
3-4. Analysis (key insight + stat + implication)
5-7. Radar (grouped by theme: models, market, security)
8. Community pulse (2-3 discussion cards)
9. Practical application (tool demo)
10. Closing (brand + links)

### 3. Generate with agy

```bash
cat > /tmp/deck-prompt.txt << 'PROMPT'
[full prompt with ALL content inline — agy cannot read files]
PROMPT

scp -F ~/.ssh/config /tmp/deck-prompt.txt oracle-host:/tmp/
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --dangerously-skip-permissions --print "$(cat /tmp/deck-prompt.txt)"'
```

### 4. Delivery

```bash
ssh oracle-host 'sudo cp /home/ubuntu/output.html /home/ubuntu/selfhost/hermes/data/'
```

### 5. Editing an existing deck (faster than regenerating)

When a deck exists and needs fixes (emoji replacement, add interactivity, fix navigation):

```bash
# 1. Copy existing file to host
scp -F ~/.ssh/config /opt/data/slides.html oracle-host:/home/ubuntu/slides.html

# 2. Write edit prompt with exact instructions
cat > /tmp/edit-prompt.txt << 'PROMPT'
Edite /home/ubuntu/slides.html para:
[List specific changes with code blocks to inject]
PROMPT

# 3. Run with LONG timeout — existing files are 500KB+
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 600 agy --print "$(cat /tmp/edit-prompt.txt)"'

# 4. Copy back
ssh oracle-host 'sudo cp /home/ubuntu/slides.html /home/ubuntu/selfhost/hermes/data/'
```

## Interactive Deck Features (for meeting-use presentations)

When generating a deck the user will use DURING a meeting (not just view), include these features:

### Editable cards (contenteditable)

- Cards on project/opportunity slides should be editable via `contenteditable`
- Each card gets a remove button (SVG "X" icon, 14x14, stroke="#00f2c3") in the top-right corner, positioned absolutely
- An "Add" button at the end of each card group (ghost style, SVG "+" icon)
- New cards clone the template card and clear text fields
- All DOM manipulation wrapped in try-catch

### localStorage persistence

- Save all edits automatically via `input` event listeners
- Use separate keys per data set: `id_projetos_data`, `id_oportunidades_data`, `id_table_data`, `id_todo_data`, `id_next_meeting`
- Store as JSON arrays for card data, plain text for single fields
- Restore saved data on page load by parsing JSON and rebuilding card content

### Checklist (slide 6)

- Interactive checklist with add/remove/checkmark
- Checked items get strikethrough styling (text-decoration: line-through, opacity: 0.6)
- Each item has a checkbox input + remove button
- New items added via text input + "Add" button

### DOMContentLoaded safeguard

Every interactive slide deck MUST use the `readyState` pattern (see Pitfalls in SKILL.md):
```javascript
function init() {
  try { restoreData(); } catch(e) {}
  showSlide(0);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else { init(); }
```

## Key Design Rules for Newsletter Decks

- **10 slides** is ideal — covers all content without being too long
- **Numbers/statistics** displayed large in Fira Code with amber/warm accent color
- **Quotes** in serif italic with left border in brand accent color
- **Cards** for community discussions with border-left accent
- **Navigation**: horizontal swiper (arrows + keyboard + mobile swipe), slide counter (N/10)
- **Mascot logo** as SVG inline — include detailed SVG spec in prompt
- **No gradient text, no glassmorphism, no decorative borders**
- **No emojis** — use inline SVG icons instead (pre-define SVGs in prompt)
- **Logo optimization** — store base64 in single JS variable, reference dynamically via querySelectorAll

## IAF Example

See output at `/opt/data/iaf-newsletter-deck-2026-06-07.html` (10 slides, 20.8KB, dark theme).
