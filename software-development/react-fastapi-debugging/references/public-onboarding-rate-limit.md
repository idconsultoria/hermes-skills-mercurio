# Recurso público sem login + slowapi crash no boot — 24/08/2026

Dois learnings novos (além de `artemis-2026-08-24.md`), do caso real do cadastro externo
de empresas no ArtemisHub.

## A. `@limiter.limit` sem `request: Request` → crash-loop no boot

Situação: adicionar `@limiter.limit("10/hour")` num endpoint `POST /api/empresas` que
antes era público, para mitigar spam.

Sintoma em produção depois do deploy:
- `docker compose ps` → `artemishub-backend Restarting (1)`
- `curl https://.../api/health` → **502 Bad Gateway** (nginx não alcança upstream)
- `docker logs artemishub-backend` → repetido:
  `Exception: No "request" or "websocket" argument on function "<function create_empresa at ...>"`
  (traceback de **uvicorn na carga da app**, não por-request)

Causa: o **slowapi** exige que todo endpoint decorado por `@limiter.limit` declare
`request: Request` como primeiro parâmetro da assinatura. Sem ele, o uvicorn falha ao
importar a aplicação → crash-loop.

Correção (o mesmo valeria para qualquer endpoint que ganhe rate-limit):
```python
@app.post("/api/empresas")
@limiter.limit("10/hour")
def create_empresa(request: Request, emp: EmpresaIn):   # request OBRIGATÓRIO p/ slowapi
    ...
```

Ponto cego do CI: o `ci.yml` (build + up -d) passa, mas o boot quebra. **Sempre, após tocar
decorators/middleware do backend, re-verificar `docker compose ps` + `health`** pós-deploy.

## B. Cadastro público sem login: criação aberta, leitura/edição protegidas

Requisito do parque: enviar o link `https://artemis.idconsultoria.ai/cadastro-empresa` e a
empresa cadastra sem sessão (sem criar conta).

Bloqueios corrigidos:
1. Backend exigia credencial em tudo (middleware `enforce_api_key`) → `POST` retornava 401.
2. Front, deslogado, era **expulso** para `/auth` porque `AppDataProvider` disparava fetch de
   dados no mount → 401 → `_tratarSessaoExpirada` fazia `window.location.replace('/auth')`.

Correção backend — allowlist pública, método-por-método (só criação; jamais GET de
listagem, senão vaza o diretório):
```python
_PUBLIC_ONBOARDING_PATTERNS = [
    ("POST", r"^/api/empresas$"),                  # criar empresa (onboarding)
    ("PUT", r"^/api/empresas/[^/]+/complemento$"), # etapas 3-10
]
def _is_public_onboarding(path, method):
    return any(m == method and re.match(p, path) for m, p in _PUBLIC_ONBOARDING_PATTERNS)
# no middleware enforce_api_key:
if path == "/api/health" or path == "/api/auth/login" or _is_public_onboarding(path, request.method):
    return await call_next(request)
```
+ `request: Request` e `@limiter.limit` nos endpoints públicos (anti-spam). Validação por
  Pydantic mantida (tipos/injeção).

Correção frontend:
- `src/lib/public-routes.ts`: `ROTAS_PUBLICAS = ['/cadastro-empresa']` e
  `export function isPublicRoute(path) { return ROTAS_PUBLICAS.some(r => path === r || path.startsWith(r + '/')) }`.
- `offline-api.ts` `_tratarSessaoExpirada`: não redirecionar se `isPublicRoute(pathname)`.
- `app-data-context.tsx` `AppDataProvider`: se `isPublicRoute(location.pathname)`, `setLoading(false)` + return (pula fetch).

Validação de ponta a ponta em produção (sem sessão):
- `GET /cadastro-empresa` abre o form (sem redirect p/ auth), 26 inputs.
- `POST /api/empresas` (body real) → **200**, grava com `status_cadastro='pendente'`,
  `origem_cadastro='onboarding'`.
- `GET /api/empresas` sem auth → **401** (listagem protegida — não vaza).

Limpar dados de teste: `DELETE FROM public.empresas WHERE ...` e `public.empresas_parque`
(empresa do onboarding é espelhada em `empresas_parque`).

## Reconciliar
- `devops-artemishub` (user-owned) tem o `host` e a chave `references/deploy_key.pem`;
  confira lá para acesso SSH ao Oracle host por dentro do container do Mercúrio.