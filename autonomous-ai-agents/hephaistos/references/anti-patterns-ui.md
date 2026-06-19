# Anti-Patterns de UI Descobertos em Sessão

> Padrões que parecem corretos mas QUEBRAM a experiência. Documentados aqui para evitar repetição.

## clip-path: circle(0%) em sections com blur gate

**O que parece:** Efeito cinematográfico de reveal circular quando o usuário desbloqueia conteúdo.

**O que acontece:** `clip-path: circle(0%)` colapsa a área visual do elemento para zero. O IntersectionObserver não detecta o elemento como visível (threshold 0.05 não é atingido). O `is-visible` nunca é adicionado. Sections ficam permanentemente invisíveis.

**Causa raiz:** IntersectionObserver usa o bounding box (não a área visual clipada). Mas o threshold exige que X% do elemento esteja visualmente intersectando — com clip-path zero, isso nunca acontece.

**Correção:** Usar apenas transições de `filter` (blur → clear) ou `opacity` para gated content. Nunca clip-path em sections que começam escondidas.

**Validado:** Projeto Desconsultor, 2026-06-16.

---

## Emojis na UI

**Regra absoluta:** NUNCA usar emojis como ícones visuais na interface. Usar componentes Lucide (`<Star/>`, `<AlertTriangle/>`, `<Sparkles/>`, etc.).

**Por quê:** Emojis têm aparência inconsistente entre SOs/browsers. Lucide icons são vetoriais, acessíveis, e consistentes com o design system.

**Se o emoji estiver em um mapa de strings:** Converter o mapa para `Record<string, LucideIcon>` e renderizar com JSX:
```tsx
const glyphMap: Record<string, LucideIcon> = {
  "Arquétipo A": Leaf,
  "Arquétipo B": Zap,
};
const Icon = glyphMap[title] || Brain;
<Icon className="h-8 w-8" />
```

**Validado:** Projeto Desconsultor, 2026-06-16.

---

## git stash como "backup"

**O que parece:** Salvar o estado atual antes de mudanças arriscadas.

**O que acontece:** `git stash` LIMPA o working tree, revertendo tudo para o último commit. O usuário perde a visualização das mudanças.

**Correção:** Usar `git add -A && git commit -m "backup: descrição"` — cria um commit que preserva tudo e pode ser revertido com `git revert HEAD`.

**Validado:** Projeto Desconsultor, 2026-06-16.

---

## git checkout de arquivos específicos

**O que parece:** Reverter apenas o arquivo que o Biome quebrou.

**O que acontece:** `git checkout -- <arquivo>` reverte TODAS as mudanças nesse arquivo — incluindo edições manuais feitas antes do Biome. Todas as mudanças perdidas precisam ser refeitas.

**Correção:** Antes de `git checkout`, verificar se o arquivo tem mudanças manuais que precisam ser preservadas. Se sim, fazer commit parcial das mudanças boas antes de reverter.

**Validado:** Projeto Desconsultor, 2026-06-16.
