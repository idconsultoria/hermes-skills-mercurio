# SVG arrowhead marker — anchor at the POINT (and headless-screenshot recipe)

## The bug (observed in the field, 2026-08)
In a BPMN/Swimlane SVG, the `<marker>` defines a triangle. `refX`/`refY` say
WHICH marker coordinate sits EXACTLY on the end point of the line (`marker-end`).
If `refX` points at the middle of the triangle instead of the leading tip, the
base of the triangle lags BEHIND the line's end → a visible gap between the line
and the arrowhead. The user flagged it: "a linha da seta precisa estar conectada
atrás da ponta da flecha".

## Working marker (connect the line BEHIND the arrowhead tip, tip ends on target edge)
```html
<marker id="arrowhead" viewBox="0 0 12 10" refX="11.5" refY="5"
  markerWidth="12" markerHeight="9.2" orient="auto-start-reverse" overflow="visible">
  <!-- hastes at x≈0.5 COVER the incoming line behind the tip; tip at 11.5 = target edge -->
  <path d="M 0.5 0.8 L 11.5 5 L 0.5 9.2 z" fill="#0d9488"/>
</marker>
```
`refX="11.5"` = the leading tip sits on the line's end; the base (x=0.5) is drawn
BACKWARD over the line, so the line visually disappears behind the arrowhead and
connects cleanly. The tip lands exactly on the next block's edge (no float, no
invasion into the card).

Why the first attempt failed: `refX="8.5"` with triangle base at `x=0` left the
point ~11 units ahead of the line end → the shaft didn't reach the point.

## Orthogonal (90°) arrow routing — connect BLOCKS, not columns
```js
// coords are relative to the swimlane container (subtract its getBoundingClientRect)
const X0 = sr.right - sx + 2;              // exit from right edge of block N
const Y0 = sr.top + sr.height/2 - sy;
const X1 = dr.left  - sx - 1;              // enter left edge of block N+1
const Y1 = dr.top + dr.height/2 - sy;
const elbowX = Math.min(X0 + 18, X1 - 8);
const d = Math.abs(Y1 - Y0) < 10
  ? `M ${X0} ${Y0} L ${X1} ${Y1}`                      // same lane: straight
  : `M ${X0} ${Y0} L ${elbowX} ${Y0} L ${elbowX} ${Y1} L ${X1} ${Y1}`; // 90° elbow
```
Because the swimlane renders exactly ONE block per column, the vertical segment
drops down empty cells and never crosses a card.

## Responsive redraw (so arrows re-pin after fonts/reflow)
```js
function scheduleDraw(){ clearTimeout(scheduleDraw._t); scheduleDraw._t = setTimeout(drawArrows, 90); }
if (window.ResizeObserver){ try{ new ResizeObserver(scheduleDraw).observe(document.getElementById("swimlane")); }catch(e){} }
window.addEventListener("resize", scheduleDraw);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(()=> setTimeout(drawArrows, 250));
window.addEventListener("load", ()=> setTimeout(drawArrows, 300));
```

## Headless screenshot RECIPE (validate before delivering)
Pitfall: the debounced `ResizeObserver` + `setTimeout` redraw LOOPS under Chromium's
`--virtual-time-budget` — the headless capture never stabilizes and the process
hangs past its timeout. Fix: render a temp variant with observers disabled, or
shoot fast without the virtual-time flag.

```bash
# 1) make a screenshot-only variant: null out the ResizeObserver
sed 's/if(window.ResizeObserver){/if(false){/'  map-v7.html > /tmp/map_screenshot.html
# 2) capture (this Chromium lives under the Playwright cache)
CH=/opt/data/.playwright/chromium-1234/chrome-linux/chrome
"$CH" --headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage \
  --user-data-dir=/tmp/cf-shot --hide-scrollbars \
  --window-size=1700,1400 --virtual-time-budget=5000 \
  --screenshot=/opt/data/map-v7.png "file:///tmp/map_screenshot.html"
```
Then inspect with `vision_analyze` on the PNG (check: arrows connect blocks, 90°
corners, nothing crosses a card, spacing). On a headless box, a stale/broken
`--virtual-time-budget` run can wedge Chromium — kill leftovers with
`pgrep -x chrome | xargs -r kill -9` (match exact process name `chrome`, NOT the
shell command, to avoid self-termination).

Notes:
- Validate JS syntax first: extract `<script>…</script>` to a file, `node --check`.
- The VPN/fonts must be loaded before judging arrow alignment; a shot taken too
  early shows blocks in provisional width.