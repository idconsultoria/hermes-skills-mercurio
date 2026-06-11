# Vertical 9:16 Video Patterns

## Resolution

```html
<div id="root" data-composition-id="main"
     data-width="768" data-height="1280"
     data-start="0" data-duration="30">
```

Set `html, body { width: 768px; height: 1280px; }` in CSS.

## Layout Rules

- Every scene: `position:absolute; inset:0; width:768px; height:1280px; display:flex; flex-direction:column; align-items:center; justify-content:center;`
- Elements positioned with `position:absolute; left:50%; top:XX%; transform:translate(-50%,-50%)` for centering
- Text: center-aligned, short (2-6 words), bold, 14-36px at 768px wide
- Logos: `max-width:260px` for primary, `max-width:140px` for hero, `max-width:80px` for secondary

## Font Sizes for 768×1280

| Role | Size | Weight |
|------|------|--------|
| Main title | 28-36px | 700-800 |
| Subtitle | 16-20px | 400-600 |
| Body/description | 14-16px | 400 |
| URL/footer | 12-14px | 400 |

## Partículas Pré-calculadas

Since `Math.random()` is forbidden, pre-compute particle positions as inline styles in the HTML, then animate with GSAP using hardcoded `x`/`y` deltas:

```html
<div class="clip particle" data-start="0" data-duration="5" id="p01"
     style="width:3px;height:3px;left:120px;top:200px;"></div>
```

```js
tl.fromTo("#p01", {x:0,y:0,opacity:0.6}, {x:40,y:-80,opacity:0,duration:3}, 0);
```

## GSAP Infinite Repeat Workaround

HyperFrames linter rejects `repeat: -1`. Use finite counts calculated from scene duration / cycle time:

```js
// Wi-Fi pulse: 5s scene / 0.7s cycle = ~7 iterations → repeat:6
tl.fromTo("#wifi", {scale:0.95}, {scale:1.06, duration:0.7, repeat:6, yoyo:true}, 0);
```

## Streaming Logos Grid

For partner/streaming logo displays:
- Hero logos (2): `max-width:140px`, side by side at ~35% and ~65% horizontal
- Secondary logos (3): `max-width:80px`, distributed at ~22%, 50%, 78%
- All with `object-fit:contain` and optional `filter:drop-shadow()` for glow effect
