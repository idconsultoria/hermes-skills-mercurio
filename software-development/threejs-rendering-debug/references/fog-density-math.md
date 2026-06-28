# FogExp2 Visibility Math

## Formula
```
fogFactor = 1 - exp(-density × distance²)
```

Where `distance` is the Euclidean distance from camera to fragment in world units.

## Reference table

| Density | Distance 5u | Distance 9u | Distance 12u | Visual |
|---------|-------------|-------------|--------------|--------|
| 0.005   | 11.8% fog   | 33.2% fog   | 51.3% fog    | Subtle depth cue |
| 0.010   | 22.1% fog   | 55.5% fog   | 76.3% fog    | Atmospheric |
| 0.012   | 25.9% fog   | 63.0% fog   | 82.2% fog    | Visible with atmosphere |
| 0.015   | 31.3% fog   | 71.0% fog   | 88.4% fog    | Heavy atmosphere |
| 0.020   | 39.3% fog   | 80.2% fog   | 94.4% fog    | Very foggy |
| 0.040   | 63.2% fog   | **96.6% fog** | 99.7% fog   | Near-invisible |
| 0.060   | 77.7% fog   | 99.3% fog   | 99.9% fog    | Effectively opaque |

## Sergipetec case study (2026-06-21)

- Scene: PlaneGeometry(44,44) terrain + cube, camera at (0, 4.6, 9.2)
- Camera-to-terrain distance: ~9.2u
- Original fog: `FogExp2(0x050a0f, 0.045)` → 97.8% fogged
- CSS body background: `#050A0F`
- Rendered pixel: `rgba(3, 8, 14, 255)` — indistinguishable from CSS `#050A0F`
- Fix: reduced to `FogExp2(0x050a0f, 0.012)` → 63% fogged, visible
- Also reduced terrain base color from `#02080C` to `#0C2A40`, exposure from 1.05 to 1.5

## Selection heuristic

For a dark-themed site (background #050A0F):
- Camera at 6-10u → density 0.008-0.015
- Camera at 10-15u → density 0.005-0.010
- Camera at 2-5u → density 0.015-0.025

Never exceed 0.02 for cameras that stay within 10u of the subject.
