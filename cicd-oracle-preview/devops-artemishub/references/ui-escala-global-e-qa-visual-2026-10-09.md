# Escala global da UI (-1,5x) e QA visual sem login — 09/10/2026

Pedido do principal: reduzir "a resolução" da plataforma e da pillnav em 1,5x e remover o
"background abaixo da pillnav". Entregue em `src/index.css` + `src/App.tsx`.

## 1. Como encolher a interface inteira (e o que cada caminho faz)

| Abordagem | Resultado |
|---|---|
| `html { zoom: var(--ui-scale) }` | ✅ único jeito de encolher **tudo**, incluindo px absolutos em classes arbitrárias (`text-[44px]`, `w-[22px]`). Reflui o layout (não distorce, diferente de `transform`) |
| `transform: scale()` no root | ❌ não reflui: quebra scroll, `fixed` e blur; texto borrado |
| reduzir só tokens `rem` / `font-size` do html | ❌ px arbitrários ficam fora de escala (a UI mistura px e rem) |

## 2. Semântica do `zoom` no Chrome (medido, viewport 1214×2254)

- `getBoundingClientRect()` devolve **px visuais** (já multiplicados pela escala); `offsetHeight`
  devolve px de layout.
- `100vh` → `offsetHeight` = **viewport real** (2254), mas desenha só `viewport × escala` (1503)
  → shell/botão de tela cheia fica menor que a tela. Correção: `calc(100vh / var(--ui-scale))`
  (desenha 2254 ✓).
- `html, body { height: calc(100% / escala) }` ❌ **não usar**: o `100%` do `html` já resolve
  contra o viewport escalado e o documento fica 1,5x mais alto (rolável e vazio — visto em
  `/auth`, body 5071 px). Com o zoom, o shell não depende dessa cadeia: basta compensar o `vh`.
- `position: fixed` com `inset-0`, `left-1/2` etc. resolve contra o viewport **já escalado**
  → modal/overlay cobrem a tela e a pill fica centrada sem ajuste.
- **Media queries NÃO mudam** (breakpoints seguem o viewport real): a tela fica menor, não vira
  outro layout.
- Utilitárias do Tailwind podem ser sobrescritas no `index.css` **fora** de `@layer` (regra sem
  camada vence a camada `utilities` do Tailwind v4) — foi assim que `.h-screen`/`.min-h-screen`
  ganharam a compensação num lugar só.

Bloco final em `src/index.css`:

```css
:root { --ui-scale: 0.66667; }   /* -1,5x */
html { zoom: var(--ui-scale); }
.h-screen { height: calc(100vh / var(--ui-scale)); }
.min-h-screen { min-height: calc(100vh / var(--ui-scale)); }
```

## 3. A "tarja" abaixo da pillnav (diagnóstico e correção)

O container de conteúdo do `AppLayout` tem `pb-pillnav` (7rem) para a pill não cobrir nada. Essa
faixa (112 px) **não é pintada pela página** (o container de scroll termina antes) e mostrava o
fundo sólido do shell (`bg-surface` = `#fbf9fb`), enquanto o resto da página pinta o mesh
(`background-attachment: fixed`). Daí a barra clara embaixo da pill.

Correção: o shell pinta o **mesmo mesh** sem `background-attachment: fixed` (`.bg-mesh-shell` no
`App.tsx`). Prova por pixel (coluna à esquerda, fronteira do conteúdo em y=2143): antes havia
salto `(228,240,235) → (251,249,251)`; depois, contínuo (deltas ~0).

> Mesma família de bug: `c682d5f` (tarja atrás do header), `f684184` (mesh fixo no root) e
> `9b09d16` (token `pb-pillnav`). Sempre que aparecer "faixa que não acompanha o conteúdo",
> procurar `background-attachment: fixed`.

## 4. QA visual sem credencial de produção (técnica reutilizável)

Produção exige login (senhas só em hash no dump). Para validar mudança de CSS no shell real:

1. Pegar o CSS **do build em produção** (`dist/assets/index-*.css` do host) e a marcação real do
   shell (DOM colado pelo usuário + `src/components/layout/*.tsx`).
2. Montar um HTML com `<style>` inline com esse CSS e injetar na aba via `document.write`. O CDP
   limita ~64 KB por `Runtime.evaluate`: mandar o HTML em **base64 fatiado**
   (`window.__b64 += '...'` a cada ~20 KB) e depois `atob`/`decodeURIComponent`.
3. Medir com o próprio DOM: `getBoundingClientRect()` do shell, da pill e do container de scroll;
   `document.elementFromPoint(x, y)` para saber **quem pinta** a faixa suspeita.
4. Provar a faixa por pixel: `capture_screenshot()` + PIL amostrando linhas acima/abaixo da
   fronteira (salto nas médias RGB = tarja; contínuo = resolvido).
5. `vision_analyze` com `region=[x1,y1,x2,y2]` na região recortada para conferir o visual.

Pitfalls do caminho:
- O browser do harness é **outro host de rede**: `127.0.0.1:porta` e `file://` não abrem, e
  portas arbitrárias do Oracle não são alcançáveis. Servir o harness dentro do container do
  frontend (`docker cp ... /usr/share/nginx/html/qa-*.html`) funciona, mas o **service worker**
  do app pode devolver o shell antigo em navegações — o caminho confiável é o `document.write`
  (nenhuma navegação envolvida).
- Reconstruir a imagem do frontend **remove** os arquivos de QA copiados para o container.
- Depois do deploy, o navegador do usuário pode continuar no build antigo por cache do service
  worker → pedir reload forçado.
