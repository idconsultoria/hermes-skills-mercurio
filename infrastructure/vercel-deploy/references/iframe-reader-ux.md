# Iframe Reader + Sidebar UX — PostMessage Pattern

## When to use this

Static archive sites (newsletter editions, documentation collections, report archives) where:
- A **landing page** lists available items (cards with title + date + excerpt)
- Clicking an item opens it in a **full-screen reader overlay** (iframe)
- The reader has its own **navigation bar** (prev/next, close, hamburger menu)

## Architecture

```
Landing Page (index.html)
├── Hero / sidebar with cards
├── Edition Reader overlay (z-index: 200)
│   └── <iframe src="/slug">           ← edition page served by same domain
│       └── Edition page with navbar
│           ├── ≡ hamburger (button)
│           ├── ← date → (prev/next arrows)
│           └── ✕ close (button)
└── Sidebar panel (z-index: 101)
```

## PostMessage Communication

The reader overlay (parent page) hosts an iframe showing the edition page (child).  
The child's navbar buttons need to control the parent's overlay — **postMessage** is the cleanest approach.

### Parent (index.html) — Message Listener

```javascript
window.addEventListener('message', (e) => {
  if (e.data && e.data.action === 'closeEdition') {
    closeEdition();            // fade out reader
  } else if (e.data && e.data.action === 'openSidebar') {
    openSidebar();             // slide in edition list
  } else if (e.data && e.data.action === 'closeAndSidebar') {
    closeEdition();            // close reader first
    setTimeout(function() {
      openSidebar();           // then open sidebar (after fade-out)
    }, 380);                   // match transition duration
  }
});
```

### Child (edition page) — Senders

```javascript
// Close button
document.getElementById('closeBtn').addEventListener('click', function() {
  if (window.parent && window.parent !== window) {
    window.parent.postMessage({action: 'closeEdition'}, '*');
  } else {
    window.location.href = '/';    // fallback when viewed directly
  }
});

// Hamburger menu
document.getElementById('menuBtn').addEventListener('click', function() {
  if (window.parent && window.parent !== window) {
    window.parent.postMessage({action: 'closeAndSidebar'}, '*');
  } else {
    window.location.href = '/';
  }
});
```

### Key details

- **`window.parent !== window`** — detects if running inside an iframe.  
- **Fallback to `window.location.href = '/'`** — when the page is viewed directly (not in iframe), the buttons navigate to home instead of failing silently.  
- **`closeAndSidebar` vs `close` then `open`** — the sidebar has `z-index: 101`, the reader has `z-index: 200`, so the reader MUST fade out before the sidebar can be visible. The `closeEdition()` call starts the fade-out, then a `setTimeout` (matching the CSS transition duration) opens the sidebar.  
- **`e.preventDefault()` is NOT needed** on `<button>` elements (they have no default action). On `<a>` elements, use `e.preventDefault()`.

## Reader Transitions (smooth close)

Instead of `display: none/flex` (which can't animate), use opacity + pointer-events:

```css
.reader {
  display: flex;
  opacity: 0;
  pointer-events: none;
  visibility: hidden;
  transition: opacity 0.35s ease, visibility 0.35s ease;
  z-index: 200;
}
.reader.active {
  opacity: 1;
  pointer-events: auto;
  visibility: visible;
}
```

When closing, remove the `active` class and delay clearing the iframe `src` to allow the animation to complete:

```javascript
function closeEdition() {
  const reader = document.getElementById('reader');
  reader.classList.remove('active');
  document.body.style.overflow = '';
  history.pushState({}, '', '/');    // restore URL
  // Clear iframe after animation finishes
  setTimeout(() => {
    if (!reader.classList.contains('active')) {
      document.getElementById('iframe').src = '';
    }
  }, 400);
}
```

## CSS Grid Cards (no badge overlap)

When each card has a title + badge (e.g., "DIÁRIA", "EXTRAORDINÁRIA") that must not overlap:

```css
.card-top {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2px 10px;
  padding: 14px 16px 4px;
  overflow: hidden;                 /* clip content that exceeds grid cell */
}

.card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  /* goes to column 1 (flexible) */
}

.card-label {
  justify-self: end;
  align-self: start;
  white-space: nowrap;
  /* goes to column 2 (auto = badge width) */
}

.card-meta {
  grid-column: 1 / -1;
  /* spans both columns in row 2 */
}
```

The `minmax(0, 1fr)` on the first column is critical — without `minmax(0, ...)`, the grid column defaults to `minmax(auto, 1fr)`, which prevents the column from shrinking below the text's inherent width (even with `overflow: hidden` on the item). The `minmax(0, 1fr)` forces the column to be able to shrink to 0, allowing the `auto` column to take its natural badge width.
