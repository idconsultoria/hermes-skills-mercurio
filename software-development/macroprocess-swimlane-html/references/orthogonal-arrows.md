# Orthogonal arrow routing + validation pattern

Proven on a real 11-task × 8-lane Telecom macroprocess deliverable (ID Consultoria,
2026-08). This is the section that finally satisfied the user after several blind
iterations — reuse it verbatim.

## Arrow drawing (SVG overlay on a `<table>` swimlane)

Container: `.swimlane` is `position:relative; overflow-x:auto`; inside it an
`<svg class="arrows">` (absolute, `pointer-events:none`), then the table.

```html
<div class="swimlane" id="swimlane">
  <svg class="arrows" id="arrows" xmlns="http://www.w3.org/2000/svg"></svg>
  <table class="sw" id="swim">
    <thead id="swHead"></thead>
    <tbody id="swBody"></tbody>
  </table>
</div>
```

CSS:
```css
.swimlane{position:relative; overflow-x:auto; border:1px solid #cdd7e4; border-radius:14px; background:#fff;}
svg.arrows{position:absolute; top:0; left:0; pointer-events:none; z-index:6; overflow:visible;}
/* wide columns, tall cards (spacing is a user requirement) */
.sw tbody td:not(.lane):not(:last-child){min-width:224px;}
.cell{min-height:118px; padding:13px 15px; border-radius:12px;}
```

```js
function drawArrows(){
  const sw = document.getElementById("swimlane");
  const svg = document.getElementById("arrows");
  if(!sw||!svg) return;
  const rect = sw.getBoundingClientRect();
  const W = sw.scrollWidth, H = sw.scrollHeight;
  const sx = rect.left, sy = rect.top;
  svg.setAttribute("width", W);
  svg.setAttribute("height", H);
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);

  let paths = "";
  for(let i=1;i<ETAPAS.length;i++){
    const src = document.querySelector(`.cell:not(.sec)[data-etapa="${i}"]`);
    const dst = document.querySelector(`.cell:not(.sec)[data-etapa="${i+1}"]`);
    if(!src||!dst) continue;
    const sr = src.getBoundingClientRect();
    const dr = dst.getBoundingClientRect();
    const X0 = sr.right - sx + 2;
    const Y0 = (sr.top + sr.height/2) - sy;
    const X1 = dr.left  - sx - 1;
    const Y1 = (dr.top + dr.height/2) - sy;
    const off = 18;
    const elbowX = Math.min(X0 + off, X1 - 8);
    let d;
    if(Math.abs(Y1 - Y0) < 10){
      d = `M ${X0} ${Y0} L ${X1} ${Y1}`;                 // same lane → straight
    } else {
      d = `M ${X0} ${Y0} L ${elbowX} ${Y0} L ${elbowX} ${Y1} L ${X1} ${Y1}`; // 90° elbow
    }
    paths += `<path d="${d}" fill="none" stroke="#0d9488" stroke-width="2.6"
      stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrowhead)"/>`;
  }
  svg.innerHTML = `<defs>
      <marker id="arrowhead" viewBox="0 0 10 10" refX="8.5" refY="5"
        markerWidth="8" markerHeight="8" orient="auto-start-reverse">
        <path d="M 0 1 L 9 5 L 0 9 z" fill="#0d9488"/>
      </marker>
    </defs>` + paths;
}

/* Robust redraw that survives font loads & layout shifts */
function scheduleDraw(){ clearTimeout(scheduleDraw._t); scheduleDraw._t = setTimeout(drawArrows, 90); }
if(window.ResizeObserver){ try{ new ResizeObserver(scheduleDraw).observe(document.getElementById("swimlane")); }catch(e){} }
window.addEventListener("resize", scheduleDraw);
if(document.fonts && document.fonts.ready) document.fonts.ready.then(()=> setTimeout(drawArrows, 250));
window.addEventListener("load", ()=> setTimeout(drawArrows, 300));
```

Key insight: vertical arrow runs stay inside the **source column**, which contains only
the owner block + empty cells (since 1 task = 1 block), so arrows never cross a card.

## Offline validation before delivering (no browser_exec needed)

1. JS syntax — extract `<script>` and run through Node's parser (not executed):
   ```bash
   python3 -c "import re;h=open('f.html').read();open('/tmp/x.js','w').write(re.search(r'<script>(.*?)</script>',h,re.S).group(1))"
   node --check /tmp/x.js
   ```
2. Data consistency (dept/parceiros in LANES, continuous numbering) and grid column
   parity — short Python regex scripts.
3. Visual proof via local headless Chromium (Playwright ships one):
   ```bash
   CHROME=/opt/data/.playwright/chromium-1234/chrome-linux/chrome
   "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
     --window-size=1700,1400 --virtual-time-budget=6000 \
     --screenshot=/opt/data/page.png "file:///opt/data/f-html"
   ```
   `--virtual-time-budget` fast-forwards timers so Google Fonts load and arrows redraw
   before the capture. Then load `/opt/data/page.png` with `vision_analyze` and ask it
   to confirm arrows are orthogonal, don't cross cards, and spacing is OK.

## Iteration discipline
User gave this sequence of corrections in one session — build for them up front:
dark→light theme → arrows must connect blocks (not live in columns, not curves) →
more breathing room → remove duplicated "participa" blocks (partners = badges in the
owner card) → arrows look bad again → orthogonal 90° routing + robust redraw.
Deliver each round as a versioned file and self-render a screenshot before sending.