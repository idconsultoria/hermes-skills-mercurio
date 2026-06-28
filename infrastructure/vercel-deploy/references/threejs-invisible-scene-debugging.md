# Three.js Invisible Scene Debugging

When a Three.js 3D scene renders correctly (triangles are drawn, no JS errors)
but appears as a flat black/dark background in the browser — indistinguishable
from the CSS `body` background.

## Quick diagnostic (browser console)

```javascript
// 1. Confirm rendering IS happening
const info = window.__app.manager.renderer.info;
console.log('draw calls:', info.render.calls, 'triangles:', info.render.triangles);
// If triangles > 0, the GPU is drawing — the issue is visibility, not rendering.

// 2. Read a pixel to see the actual output color
const gl = document.getElementById('scene-canvas').getContext('webgl2');
const p = new Uint8Array(4);
gl.readPixels(640, 360, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, p);
console.log(`rgba(${p[0]},${p[1]},${p[2]},${p[3]})`);
// Compare with CSS body background. If they match (< 10 apart per channel),
// the scene is invisible due to contrast matching.

// 3. Force-hide HTML overlay to isolate 3D canvas
document.getElementById('scroll-root').style.display = 'none';
// If the 3D scene becomes visible, the issue was contrast, not rendering.
```

## Root causes and fixes

### 1. Exponential fog too dense (most common)

**Symptom:** Scene is there but completely fogged to the background color.
At fog density 0.04 with camera 9 units away:
`fogFactor = 1 - exp(-0.04 × 9²) ≈ 0.96` — 96% fogged.

**Fix:** Reduce `FogExp2` density. For scenes with camera 7–10 units from
subjects, use density 0.01–0.015:
```javascript
scene.fog = new THREE.FogExp2(0x050a0f, 0.012); // was 0.04+
```

### 2. ShaderMaterial GLSL version mismatch (WebGL2)

**Symptom:** Custom `ShaderMaterial` renders black or not at all.
`material.program` is `null`/falsy. No console errors.

**Root cause:** Three.js r152+ defaults to GLSL 300 es in WebGL2 contexts.
GLSL 1.00 syntax (`texture2D`, `varying`, `gl_FragColor`) fails silently.

**Fix:** Add `glslVersion: 1` to the ShaderMaterial:
```javascript
new THREE.ShaderMaterial({
  glslVersion: 1,  // ← force GLSL 1.00 syntax
  uniforms: { ... },
  vertexShader: `varying vec2 vUv; void main() { vUv = uv; ... }`,
  fragmentShader: `varying vec2 vUv; void main() { gl_FragColor = ...; }`,
});
```

Alternatively, convert shaders to GLSL 300 es (`texture` instead of
`texture2D`, `in`/`out` instead of `varying`, `out vec4 fragColor`
instead of `gl_FragColor`).

### 3. Canvas output matches CSS background

**Symptom:** Scene renders correctly but the canvas pixels have the same
color as the CSS `body { background-color: ... }`.

**Fix:** Either (a) make the scene brighter than the CSS background, or
(b) make the CSS background transparent and let the canvas provide it.

For dark themes: increase `toneMappingExposure`, ambient light, and
terrain/surface base colors so they're visibly different from the CSS
background. A difference of at least 15 per channel (out of 255) is
needed for visibility.

```javascript
// Terrain ShaderMaterial base color
// ❌ #02080C — indistinguishable from #050A0F body background
// ✅ #0C2A40 — visible contrast against dark background
uColorBase: { value: new THREE.Color('#0C2A40') }
```

### 4. GLTFLoader models with MeshPhysicalMaterial

When loading GLB models that use `MeshPhysicalMaterial`, they need an
environment map for proper lighting. Without it, they appear nearly black.

**Fix:** Load an HDR environment map via RGBELoader + PMREMGenerator:
```javascript
const pmrem = new THREE.PMREMGenerator(renderer);
const hdrTex = await new RGBELoader().loadAsync('environment.hdr');
const envMap = pmrem.fromEquirectangular(hdrTex).texture;
scene.environment = envMap;

// Also update any already-loaded PhysicalMaterials:
scene.traverse(c => {
  if (c.isMesh && c.material.isMeshPhysicalMaterial) {
    c.material.envMap = envMap;
    c.material.needsUpdate = true;
  }
});
```

### 5. Network: confirm assets load

Check in browser devtools Network tab or via Performance API:
```javascript
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('assets/'))
  .map(r => r.name.split('/').pop() + ' ' + (r.transferSize > 0 ? '✓' : '✗'));
```

## Debugging workflow (in order)

1. **Check if rendering at all:** `renderer.info.render.triangles > 0`
2. **Check fog:** `scene.fog.density` — should be ≤ 0.015 for scenes
   with subjects within 10 units
3. **Check shader:** `material.program` should be truthy
4. **Check pixel color:** `gl.readPixels()` — compare with CSS body bg
5. **Isolate canvas:** hide HTML overlays temporarily
6. **Force brighten:** set `renderer.toneMappingExposure = 1.8` and
   terrain colors to bright teal temporarily — if scene appears, the
   issue is contrast/brightness

## Real-world example (Sergipetec site)

- Terrain + cube rendering 51k triangles ✓
- All 19 assets loading HTTP 200 ✓
- Fog at 0.04 → 96% fogged at 9.2u distance ✗
- Terrain pixel rgba(2,5,7) vs body bg #050A0F — indistinguishable ✗
- Fix: fog → 0.012, terrain base → #0C2A40, exposure → 1.5
- Result: 3D scene visible with teal contour lines and glowing cube
