# Emoji → Lucide Icon Mapping

> Referência rápida para substituir emojis por Lucide icons em projetos React/Next.js.

## Arquétipos / Conceitos

| Emoji | Lucide | Import |
|-------|--------|--------|
| 🌿 | `Leaf` | `from "lucide-react"` |
| ⚡ | `Zap` | `from "lucide-react"` |
| 🔄 | `RefreshCcw` | `from "lucide-react"` |
| 🏛️ | `Landmark` | `from "lucide-react"` |
| ⚖️ | `Scale` | `from "lucide-react"` |
| ✨ | `Sparkles` | `from "lucide-react"` |
| 🚀 | `Rocket` | `from "lucide-react"` |
| ⚙️ | `Cog` | `from "lucide-react"` |
| 🏗️ | `Building2` | `from "lucide-react"` |
| 🔀 | `Shuffle` | `from "lucide-react"` |
| 🧠 | `Brain` | `from "lucide-react"` |

## UI Feedback

| Emoji | Lucide | Import |
|-------|--------|--------|
| ✦ | `Star` | `from "lucide-react"` |
| ⚠ | `AlertTriangle` | `from "lucide-react"` |
| ✓ | `CheckCircle` | `from "lucide-react"` |
| ✖ | `XCircle` | `from "lucide-react"` |
| 🔒 | `Lock` | `from "lucide-react"` |
| 🔍 | `Search` | `from "lucide-react"` |

## Padrão de Implementação (React)

```tsx
// Em vez de: const glyph = "🌿";
// Usar:
import type { LucideIcon } from "lucide-react";
import { Leaf, Zap, Brain } from "lucide-react";

const glyphMap: Record<string, LucideIcon> = {
  "Nome": Leaf,
  "Outro Nome": Zap,
};

// No JSX:
const GlyphIcon = glyphMap[title] || Brain;
return <GlyphIcon className="h-8 w-8" />;
```
