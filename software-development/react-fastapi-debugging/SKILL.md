---
name: react-fastapi-debugging
type: ToolIntegration
timestamp: 2026-08-24T00:00:00Z
description: "Patch fallback silencioso e bugs de UI em app React+FastAPI.

Carregue esta skill quando um recurso React+FastAPI da ID cair sempre no fallback/modo genérico (IA mostra mock, form não autopreenche) ou um bug de UI reaparecer (modal piscando, rodapé vira tarja, análise vaza entre telas). Padrões de classe com causa raiz e correção testadas — header de auth 401, valor mascarado, autofill CNPJ/CEP, rate-limit de onboarding."
version: 1.0.0
author: "ID Consultoria (Mercúrio / Hermes), 24/08/2026"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [react, fastapi, debugging, auth, modal, portal, rate-limit, autofill, cnpj, cep]
    related_skills: [systematic-debugging, devops-artemishub, dogfood]
---

# React + FastAPI — Debugging de "fallback silencioso" e bugs de UI (ID)

## When to Use

Carregue quando, num app **React (frontend) + FastAPI (backend)** da ID, um recurso
**"sempre cai no modo genérico/fallback"** (ex.: IA mostra um mock, um form não autopreenche)
ou um bug de UI reaparece ("modal piscando", "rodapé vira tarja", "análise vaza entre telas").
Estes padrões **não são exclusivos do ArtemisHub** — reaparecem em qualquer serviço
FastAPI+React com middleware de auth e animações de layout. Cada item abaixo é um padrão
de classe com a causa raiz e a correção testada.

## Pitfalls de classe (todos já mordidos na prática)

### 1. "SEMPRE cai no fallback/mock" quase nunca é a chave/API — é o header de auth
**Sintoma:** um recurso que chama o backend (chat de IA, análise, autofill) devolve sempre
o resultado genérico/local de fallback, mesmo com credenciais corretas.
**Causa raiz (a mais comum):** o frontend chama o endpoint com `fetch()` **sem o header
`Authorization: Bearer <token>`**. O middleware FastAPI exige credencial em todo endpoint
exceto `health`/`login` → devolve `401` → o `catch` cai no fallback local. O erro real é
silenciado.
**Correção:** injetar `Authorization: \`Bearer ${getToken()}\`` em TODA chamada que o
middleware protege. **Antes de diagnosticar chave/API, confira os logs do backend**:
`401` massivo em `/api/...` = bug de header, não de configuração.

### 2. Chave parece setada, mas o valor guardado é máscara ou lixo
**Sintoma:** config de IA "está preenchida" (`sk-fh4…GOcN`) mas a chamada falha.
**Causa:** a UI de config gravou o **valor mascarado** (`sk-…XXXX`, formato de exibição
`v[:7]...v[-4:]`) como se fosse a chave real; ou colou uma **chave no campo de URL**
(`llm.base_url = sk-…`). Vale também conferir **chaves duplicadas em lugares diferentes**
(banco vs `.env`) — o app lê um, o deploy usa outro.
**Correção:** **validar a chave real** contra o provedor (`curl .../chat/completions` com a
chave) ANTES de assumir; e adicionar guard no `PUT /api/config` — `base_url` exige URL
`http/https`, `api_key` rejeita `.` e exige prefixo real.

### 3. Provider autentica mas não responde: opt-in de região + saldo
**Sintoma:** `401` não é de auth mas de `RegionError`/`CreditsError` no corpo.
**Causa:** modelo hospedado em região que exige **opt-in** (ex.: DeepSeek/China), e/ou
**saldo insuficiente** na conta.
**Correção:** fazer opt-in no workspace do provedor (link está no próprio erro da API) +
adicionar créditos. Não confundir "chave autentica" (auth) com "chave responde" (region/saldo).

### 4. `API 500: Internal Server Error` num endpoint com rate limit
**Sintoma:** "Testar chamada real"/login devolve 500 após algumas tentativas rápidas.
**Causa:** handler de `RateLimitExceeded` faz `raise HTTPException(429)` **dentro de um
exception handler**. Em Starlette moderno, lançar exceção dentro de handler vira **500** —
o handler deve **retornar** uma `Response`.
**Correção:**
```python
@app.exception_handler(RateLimitExceeded)
async def _rl(request, exc):
    return JSONResponse(status_code=429, content={"detail": "rate limit — tente mais tarde"})
```
O contador é em memória — `docker compose restart <backend>` zera.

### 5. Modal `position:fixed` "pisca" entre viewport e container ao mover o mouse
**Sintoma:** modal (termo/LGPD) oscila entre ocupar a página toda e ficar preso num
container, piorando com hover.
**Causa raiz:** um ancestral com `transform`/`backdrop-filter` (ex.: `motion.div` animado,
framer-motion `initial={{y:…}}`) cria um **containing block** que prende o `position:fixed`
ao container, não à viewport.
**Correção:** renderizar o modal via **`createPortal(<ModalJSX/>, document.body)`** em
`react-dom` — tira o fixed do containing block de vez.

### 6. Rodapé de marca vira "tarja" fixa sobre o conteúdo/pill
**Sintoma:** rodapé (créditos) vira faixa fixa que sobrepõe conteúdo e a pill de navegação.
**Causa:** montar o rodapé num layout fixo (`h-screen overflow-hidden`), no mesmo nível
dos elementos `position:fixed`.
**Correção (preferência do principal da ID):** o **único elemento fixo** deve ser a pill de
navegação; rodapé/créditos **rolam com o conteúdo** (fim de cada página). Espaço para a pill
não sobrepor o conteúdo (ex.: chat) = **token global de padding** (`.pb-pillnav`) em vez de
hardcode espalhado.

### 7. Análise/estado "vaza" do registro anterior ao trocar de rota `:id`
**Sintoma:** navega entre itens (ex.: editais) e dados (análise, chat, favorito) do item
anterior permanecem.
**Causa:** React Router **reutiliza o componente** quando só o param `:id` muda (não
remonta) → `useState` não reseta.
**Correção:** `useEffect(() => { /* setAnalise(null); setMessages([]); ... */ }, [id])` —
reset explícito por mudança de `id`. Não confiar no "remount".

### 8. Autofill por CNPJ não traz representante/endereço
**Sintoma:** form com busca de CNPJ preenche razão mas responsável/endereço/contatos vazios.
**Causa (usual):** o mapper usa campos errados da API. Ex.: a API Minha Receita usa
`nome_socio`, `qualificacao_socio`, `cnpj_cpf_do_socio`, `nome_representante_legal`,
`cpf_representante_legal` — **não** `nome`/`qualificacao`/`cargo`.
**Correção:** conferir o **schema real** da API antes de mapear (não assumir). Fallbacks
gratuitos: "Minha Receita" (`minhareceita.org/<cnpj>`) e ViaCEP (`viacep.com.br/ws/<cep>/json`).

## Fluxo de diagnóstico recomendado
1. **Confira os logs do backend** (401 vs 500 vs timeout) antes de tudo — separa bug de
   auth/header de bug de config.
2. **Valide a credencial real** contra o provedor (não a mascarada).
3. **Separe "auth" de "region/saldo"** lendo o corpo do erro, não só o status code.
4. Para bugs de UI com `position:fixed` → procure **containing block** (transform/filter
   em ancestral) e use portal.
5. Para estado que persiste entre `:id` → reset em `useEffect([id])`.

## Verificação
- `curl` real contra o endpoint autenticado retorna 200 e dados reais (não fallback).
- Log do backend sem 401/500 inesperado após a correção.
- `tsc` / build do frontend limpo após edições de portal/reset.

## Referência
- `references/artemis-2026-08-24.md` — caso real que originou estes padrões (diagnóstico
  do ArtemisHub: auth IA, tarja de rodapé, modal portal, autofill CNPJ).