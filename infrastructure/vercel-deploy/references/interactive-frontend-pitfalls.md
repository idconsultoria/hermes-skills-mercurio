# Interactive Frontend Pitfalls — Lenis + GSAP + Three.js

Common issues when building complex interactive sites (3D, smooth scroll,
animations) that get deployed to Vercel. These are frontend bugs, not
deployment bugs — but they surface during pre-deploy verification.

## Lenis Smooth Scroll + `height: 100%` on html/body

**Symptom:** Page loads, content is present in the DOM, but scroll is
completely locked. `window.scrollY` stays 0. `document.body.scrollTop`
stays 0. Lenis `scrollTo()` does nothing. Native `window.scrollTo()`
does nothing. The page appears frozen.

**Root cause:** `height: 100%` on `html, body` constrains the document
to the viewport height. Lenis (and native scroll) cannot scroll beyond
the viewport because the document has no overflow.

**Fix:** Change `height: 100%` to `min-height: 100%` on html/body:
```css
html, body {
  /* ❌ WRONG — locks scroll when combined with Lenis */
  /* height: 100%; */

  /* ✅ CORRECT — allows document to grow, scroll works */
  min-height: 100%;
}
```

Also remove `scroll-behavior: smooth` from html/body when using Lenis
— Lenis handles smooth scroll internally; the CSS property conflicts.

## GSAP ScrollTrigger.from() + Lenis layout interference

**Symptom:** Elements animated with `gsap.from()` (opacity: 0, y: 60)
via ScrollTrigger remain invisible or cause scroll height miscalculation.
The page scroll height may be wrong, or elements never become visible
even when scrolled into view.

**Root cause:** `gsap.from()` sets initial inline styles (opacity: 0,
transform) that affect layout. ScrollTrigger calculates trigger positions
based on layout, but the animations change layout, creating a feedback
loop. With Lenis managing scroll, the timing mismatch causes triggers
to fire incorrectly or not at all.

**Fix:** Use IntersectionObserver for simple fade-in/slide-in animations
instead of ScrollTrigger. Save ScrollTrigger for screen-level transitions
(where the trigger is the section itself, not animated content within it).

```javascript
// ❌ WRONG — ScrollTrigger.from() on individual cards
gsap.utils.toArray('.card').forEach((card, i) => {
  gsap.from(card, {
    opacity: 0, y: 60, duration: 0.8, delay: i * 0.15,
    scrollTrigger: { trigger: card, start: 'top 80%' }
  });
});

// ✅ CORRECT — IntersectionObserver for card fade-ins
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(40px)';
  el.style.transition = 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
  observer.observe(el);
});
```

ScrollTrigger is fine for screen-level triggers (detecting which section
is in view) — just don't use it for animating content within sections
when Lenis is active.

## ScrollTrigger.refresh() after content settles

After page load, dynamic content population (JS-generated tables, cards,
SVGs) changes the document height. ScrollTrigger may have calculated
trigger positions before the content was injected.

**Fix:** Call `ScrollTrigger.refresh()` after content is populated:
```javascript
setTimeout(() => {
  if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.refresh();
  if (lenis && lenis.resize) lenis.resize();
}, 2500); // After loader hides and content settles
```

## Three.js + GSAP ticker integration with Lenis

The standard integration pattern works but requires correct ordering:
```javascript
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

If Lenis scroll is not responding, check that `gsap.ticker.add` is
actually running (gsap must be loaded before this line executes).

## Browser verification tip

When verifying scroll behaviour in headless/browser automation:
- Lenis controls `document.body.scrollTop`, not `window.scrollY`
- `window.scrollTo()` may not work when Lenis is active
- Use `lenis.scrollTo(element, { duration: N })` or click nav links
- Expose the Lenis instance: `window.__lenis = lenis` for debugging
