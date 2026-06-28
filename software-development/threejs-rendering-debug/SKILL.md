---
name: threejs-rendering-debug
description: "Debug invisible 3D WebGL/Three.js scenes — shaders, fog, visibility, and asset loading issues.

Load this skill when a Three.js scene is rendering (triangles > 0) but appears invisible. Provides a diagnostic protocol covering renderer setup, fog, lighting, material visibility, shader compilation, and asset loading verification."
version: 1.0.0
category: software-development
related_skills: [agy, html-report-hermes]
---

# Three.js Rendering Debug

Load this skill when a Three.js WebGL scene renders (confirmed by `renderer.info.render.triangles > 0`)
but appears invisible — all-black, blending with CSS background, or "assets not loading."

## Diagnostic Protocol (in order)

### 1. Confirm rendering vs. visibility
```js
const mgr = window.__app.manager;
mgr.renderer.render(mgr.scene, mgr.camera);
console.log('tris:', mgr.renderer.info.render.triangles);
```
If triangles > 0, the GPU IS drawing. The problem is visibility, not loading.

### 2. Check pixel value
```js
const gl = renderer.getContext();
const p = new Uint8Array(4);
gl.readPixels(viewportW/2, viewportH/2, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, p);
console.log(`rgba(${p[0]},${p[1]},${p[2]},${p[3]})`);
```
Compare with CSS body background. If within ±5 of background, scene is invisible due to color match.

### 3. Hide HTML overlay
```js
document.getElementById('scroll-root').style.display = 'none';
```
If 3D appears, the scene is correct but obscured by overlay. If still black, continue.

### 4. Boost to MAX (confirm scene integrity)
```js
mgr.terrainMat.uniforms.uColorBase.value.set('#2080a0');
mgr.renderer.toneMappingExposure = 1.8;
mgr.scene.fog.density = 0; // kill fog temporarily
```
If scene appears, progressively reduce to find the threshold. If still black, shader is broken.

### 5. Toggle individual meshes
```js
mgr.terrain.visible = false;
mgr.renderer.render(mgr.scene, mgr.camera);
const diff = mgr.renderer.info.render.triangles;
mgr.terrain.visible = true;
```
Repeat for each suspect mesh. Tri count diff reveals which meshes render.

## Common Root Causes

### A. ShaderMaterial GLSL version (⛳ #1 pitfall)
**Symptom:** ShaderMaterial renders black/transparent, `material.program` is falsy.
**Cause:** Three.js r152+ uses WebGL2 with GLSL 300 es by default. Custom shaders with `texture2D`, `varying`, `gl_FragColor` fail silently.

**Fix:** Add `glslVersion: 1` to ShaderMaterial:
```js
new THREE.ShaderMaterial({
  glslVersion: 1, // ← forces GLSL 1.00 syntax
  vertexShader: `varying vec2 vUv; ...`,  // keep original GLSL1 code
  fragmentShader: `... gl_FragColor = ...;`,
  uniforms: { ... },
});
```
Do NOT convert shaders to GLSL 300 es manually — `glslVersion: 1` is simpler and Three.js handles all pragma injection.

### B. FogExp2 density too high (⛳ #2 pitfall)
**Symptom:** Scene renders but is indistinguishable from CSS background. Pixel values match background within ±3.
**Cause:** `FogExp2` with density 0.04 at camera distance 9u: `fogFactor = 1 - exp(-0.04 × 9.2²) = 0.966`. 96.6% of color is fog, which matches the CSS body background.

**Fix:** Reduce fog density 3-4× from initial instinct:
```
0.04-0.06 → completely fogged at 8-10u
0.012-0.018 → visible with atmosphere
0.005-0.01 → subtle depth cue
```

### C. Terrain/background color match
**Symptom:** Terrain renders but pixel value equals body `background-color`.
**Fix:** Ensure terrain base color is at least 2-3× brighter (in perceived luminance) than CSS background. E.g., `#0C2A40` terrain vs `#050A0F` body.

## Pitfalls

1. **Don't trust `material.program`** — In Three.js r161+, ShaderMaterial may not populate `.program` even when compiled. Use triangle count diff or pixel check instead.

2. **Console errors may be silent** — WebGL shader compilation failures often produce empty error messages in `console.error`. Don't rely on console for shader debugging.

3. **Fog density is exponential** — A small change (0.04→0.012) has a massive visual effect. `FogExp2` formula: `fogFactor = 1 - exp(-density × distance²)`.

4. **RGBELoader needs PMREMGenerator** — Loading an `.hdr` file gives a DataTexture. For `scene.environment`, convert via `PMREMGenerator.fromEquirectangular(hdrTex)`.

5. **MeshPhysicalMaterial needs envMap** — GLB models with PhysicalMaterial appear black without environment map. Set `scene.environment` or `material.envMap`.

## Verification Checklist
- [ ] `renderer.info.render.triangles > 0`
- [ ] Pixel at viewport center differs from CSS background by ≥ 10 in at least one channel
- [ ] Hide HTML overlay → 3D scene visible
- [ ] Boost colors to max → scene appears → progressive reduce to find sweet spot
- [ ] ShaderMaterial has `glslVersion: 1` OR uses GLSL 300 es syntax throughout
- [ ] Fog density ≤ 0.02 for camera distances > 5u
- [ ] Terrain base color is visibly distinct from body background (diff ≥ 15 in blue channel)

## Histórico de atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-06-21 | Hermes (Sergipetec etapa-4-site) | Criação — diagnostic protocol, GLSL version pitfall, FogExp2 pitfall, 4 root causes, verification checklist. |
