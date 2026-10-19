# Escala global da UI, prova visual e verificação sem senha

Três tarefas de frontend que se repetem em app SPA da ID (Vite + Tailwind + PWA) e que
consumiram tempo por tentativa e erro. Não dependem de um projeto específico.

## 1. Encolher/ampliar a interface inteira

| Abordagem | Resultado |
|---|---|
| `html { zoom: var(--ui-scale) }` | ✅ único jeito de encolher **tudo**, inclusive px absolutos de classes arbitrárias (`text-[44px]`, `w-[22px]`). Reflui o layout — diferente de `transform` |
| `transform: scale()` no root | ❌ não reflui: quebra scroll, `fixed` e blur; texto borrado |
| reduzir só tokens `rem` / `font-size` do html | ❌ px arbitrários ficam fora de escala (UI mista em px e rem) |

Bloco pronto (o valor é o único ponto de ajuste):

```css
:root { --ui-scale: 0.66667; }            /* "-1,5x" */
html { zoom: var(--ui-scale); }
/* o zoom também escala as medidas de viewport → shell de tela cheia compensa */
.h-screen { height: calc(100vh / var(--ui-scale)); }
.min-h-screen { min-height: calc(100vh / var(--ui-scale)); }
```

## 2. Semântica do `zoom` no Chrome (medido, viewport 1214×2254)

- `getBoundingClientRect()` devolve **px visuais** (já multiplicados pela escala); `offsetHeight`
  devolve px de layout. Medir os dois para não se enganar.
- `100vh` → `offsetHeight` = **viewport real**, mas desenha `viewport × escala` → qualquer shell
  de tela cheia fica menor que a tela. Correção: `calc(100vh / var(--ui-scale))`.
- `html, body { height: calc(100% / escala) }` ❌ **não usar**: o `100%` do `html` já resolve
  contra o viewport escalado, e o documento fica maior que a tela (rolável e vazio).
- `position: fixed` com `inset-0` / `left-1/2` resolve contra o viewport **já escalado** → modal,
  overlay e elemento flutuante ficam certos sem ajuste.
- **Media queries não mudam** (breakpoints seguem o viewport real): a tela fica menor, não vira
  outro layout.
- Utilitárias do Tailwind v4 podem ser sobrescritas no CSS do projeto **fora** de `@layer` —
  regra sem camada vence a camada `utilities`. Foi assim que `.h-screen`/`.min-h-screen`
  ganharam a compensação em um único lugar.

Conferir depois do deploy medindo o shell e um elemento de referência (ex.: a pill de navegação
passou de 504×75 para 337×51 px, centrada, a 16 px da borda).

## 3. Provar mudança visual sem credencial (e sem depender do acaso)

1. Pegar o CSS **do build em produção** (`dist/assets/index-*.css` do host) e a marcação real do
   shell (DOM colado pelo usuário + componentes de layout do repo).
2. Montar um HTML com esse CSS inline e injetar na aba via `document.write`. O CDP limita
   ~64 KB por `Runtime.evaluate`: mandar o HTML em **base64 fatiado**
   (`window.__b64 += '...'` a cada ~20 KB) e depois `atob`/`decodeURIComponent`.
3. Medir com o próprio DOM: `getBoundingClientRect()` dos elementos-chave e
   `document.elementFromPoint(x, y)` para saber **quem pinta** a região suspeita.
4. Provar faixa/emenda por pixel: `capture_screenshot()` + PIL amostrando linhas acima e abaixo
   da fronteira (salto nas médias RGB = emenda; deltas ~0 = resolvido).
5. `vision_analyze` com `region=[x1,y1,x2,y2]` na região recortada para o parecer visual.

Pitfalls do caminho:
- Servir o harness pelo container do frontend (`docker cp ... /usr/share/nginx/html/qa-*.html`)
  funciona, mas o **service worker** do app pode devolver o shell antigo em navegações; o
  caminho confiável é o `document.write` (nenhuma navegação envolvida). Reconstruir a imagem
  remove os arquivos copiados para o container.
- Antes de atribuir um visual estranho ao CSS novo, checar em que build o cliente está: versão do
  `CACHE` em `sw.js` e os assets em `performance.getEntriesByType('resource')`.
- Sessões de navegador do harness podem compartilhar perfil/cache: "sessão nova" não garante
  cache limpo.

## 4. Abrir a superfície autenticada sem digitar senha (sessão efêmera)

Onde a sessão é **token opaco em tabela** (ex.: `public.sessoes(token, usuario_id, expira_em)`),
não há JWT a forjar — e não é preciso senha para inspecionar a tela logada ou a API:

```bash
# 1) sessão curta para um usuário existente
docker exec <db> psql -U app -d <base> -tAc "insert into sessoes (token, usuario_id, expira_em)
  select md5(random()::text || clock_timestamp()::text), id, now() + interval '40 minutes'
  from usuarios where email='<email>'; returning token;"

# 2) conferir a API direto do host (o container do agente pode não resolver o domínio)
curl -sk --resolve <dominio>:443:127.0.0.1 -H 'Authorization: Bearer <token>' \
  'https://<dominio>/api/<rota>?limit=3'

# 3) no navegador: gravar o token e o usuário no localStorage nas chaves que o app lê
#    (ex.: 'app_token' + 'app_usuario' com id/email/nome/papel/permissoes) e, se houver
#    tela de carregamento por sessão, marcar a flag de sessionStorage que a pula; recarregar.

# 4) SEMPRE apagar no fim: delete from sessoes where token = '<token>';
```

Regras: é escrita em banco de produção — TTL curto, apagar ao terminar e avisar o sócio que foi
feito. Nunca digitar senha em formulário (usar ferramentas de vault quando for inevitável); esta
receita existe justamente para não precisar. Se o objetivo é só conferir dados, preferir
consulta direta (`psql`) e o log do proxy.
