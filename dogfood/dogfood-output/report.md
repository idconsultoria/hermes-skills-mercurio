# Dogfood QA Report

**Target:** TaskFlow (test stack) — http://129.146.163.107:8001 (API), http://129.146.163.107:8082 (Nginx)
**Date:** 2026-06-07
**Scope:** API endpoints (26 routes), auth flows, CRUD operations, edge cases, error handling
**Tester:** Hermes Agent (automated exploratory QA)

---

## Executive Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 1 |
| 🟠 High | 3 |
| 🟡 Medium | 4 |
| 🔵 Low | 2 |
| **Total** | **10** |

**Overall Assessment:** API funcional e estável, com boa cobertura de endpoints e respostas em português. Falta validação rigorosa de payloads e tratamento inconsistente no endpoint `/auth/me` (GET vs POST). Alguns endpoints aceitam dados inválidos sem erro.

---

## Issues

### Issue #1: `/api/v1/auth/me` responde 405 em GET (documentado como GET)

| Field | Value |
|-------|-------|
| **Severity** | 🔴 Critical |
| **Category** | Functional |
| **URL** | `GET /api/v1/auth/me` |

**Description:**
O endpoint `/api/v1/auth/me` está documentado na OpenAPI como aceitando GET, mas retorna `405 Method Not Allowed`. Na prática, funciona apenas via POST. Quebra qualquer cliente REST padrão que siga a OpenAPI.

**Steps to Reproduce:**
1. Fazer GET em `/api/v1/auth/me` com token válido
2. Receber `405 Method Not Allowed` em vez do perfil do usuário
3. Fazer POST em `/api/v1/auth/me` com mesmo token → funciona

**Expected Behavior:**
GET com token válido deve retornar perfil do usuário (ou ao menos a OpenAPI deve refletir POST)

**Actual Behavior:**
HTTP 405 "Method Not Allowed"

---

### Issue #2: Campo `priority` aceita apenas inteiro (OpenAPI omite tipo)

| Field | Value |
|-------|-------|
| **Severity** | 🟠 High |
| **Category** | Documentation / Functional |
| **URL** | `POST /api/v1/tasks/` |

**Description:**
Ao criar uma task, o campo `priority` espera um inteiro, não string. A OpenAPI lista `priority` como string no schema, causando erro de parsing quando clientes usam valores como `"high"` ou `"low"`.

**Steps to Reproduce:**
1. POST em `/api/v1/tasks/` com `{"priority": "high"}`
2. Erro: `"Input should be a valid integer, unable to parse string as an integer"`
3. POST com `{"priority": 3}` → funciona

**Expected Behavior:**
Ou aceitar strings mapeando para inteiros (high=3, medium=2, low=1), ou documentar corretamente como inteiro

**Actual Behavior:**
Erro de validação com string, mas interface espera inteiro sem documentar

---

### Issue #3: Login usa `email` em vez de `username` (incomum e não documentado)

| Field | Value |
|-------|-------|
| **Severity** | 🟠 High |
| **Category** | Documentation / UX |
| **URL** | `POST /api/v1/auth/token` |

**Description:**
O endpoint `/api/v1/auth/token` espera `email` e `password` como JSON body, não o padrão OAuth2 `username`/`password` via form-urlencoded. Clientes que seguem RFC 6749 (ex: Swagger UI, axios, Postman OAuth2) não funcionam.

**Steps to Reproduce:**
1. POST em `/api/v1/auth/token` com `Content-Type: application/x-www-form-urlencoded` e `username=qa@example.com` → erro
2. POST com `Content-Type: application/json` e `{"email": "...", "password": "..."}` → funciona

**Expected Behavior:**
Suportar ambos os formatos (form-urlencoded padrão OAuth2 + JSON)

**Actual Behavior:**
Apenas JSON com campo `email`

---

### Issue #4: Validator de email rejeita TLDs de teste válidos

| Field | Value |
|-------|-------|
| **Severity** | 🟠 High |
| **Category** | Functional |
| **URL** | `POST /api/v1/auth/register` |

**Description:**
O validador de email rejeita TLDs `.test`, `.local`, `.localhost` que são válidos pelo RFC e comuns em ambientes de desenvolvimento/teste.

**Steps to Reproduce:**
1. POST `/api/v1/auth/register` com `email: "qa@taskflow.test"`
2. Erro: `"The part after the @-sign is a special-use or reserved name"`
3. Funciona com `.com`, `.dev`, `.io`, `.app`

**Expected Behavior:**
Aceitar TLDs de teste ou ao menos dar um warning em vez de erro fatal

**Actual Behavior:**
Erro de validação bloqueante

---

### Issue #5: Quick Task usa `raw_text` em vez de `title`

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | Documentation / UX |
| **URL** | `POST /api/v1/tasks/quick` |

**Description:**
O endpoint de criação rápida de task espera `raw_text` como campo obrigatório, não `title`. Isso não é óbvio para clientes que esperam consistência com o endpoint `/tasks/`. O Quick Task faz parsing de linguagem natural (ex: "Comprar leite amanhã às 8h" → extrai título, data).

**Steps to Reproduce:**
1. POST `/api/v1/tasks/quick` com `{"title": "Comprar leite"}` → erro "field required: raw_text"
2. POST com `{"raw_text": "Comprar leite amanhã às 8h"}` → funciona, cria task com título "Comprar leite"

**Expected Behavior:**
Documentar claramente que usa `raw_text` ou aceitar ambos

**Actual Behavior:**
Erro confuso para clientes que não leram a documentação específica do quick

---

### Issue #6: Empty string aceito em campos obrigatórios

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | Functional |
| **URL** | `POST /api/v1/tasks/`, `POST /api/v1/projects/` |

**Description:**
Campos como `title` em tasks e `name` em projects aceitam string vazia `""` como valor válido, resultando em registros sem nome.

**Steps to Reproduce:**
1. POST `/api/v1/tasks/` com `{"title": "", "description": "test"}`
2. HTTP 201, task criada com title vazio

**Expected Behavior:**
Validar que campos obrigatórios não sejam vazios (minLength > 0)

**Actual Behavior:**
Aceita string vazia sem erro

---

### Issue #7: Nenhum limite de tamanho em campos string

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | Functional |
| **URL** | `POST /api/v1/projects/`, `POST /api/v1/tasks/` |

**Description:**
Campos como `name` (project) aceitam strings de 500+ caracteres sem truncamento ou erro, o que pode causar problemas de UI e overflow em relatórios.

**Steps to Reproduce:**
1. POST `/api/v1/projects/` com `{"name": "X"*500}`
2. HTTP 201, nome registrado com 500 chars

**Expected Behavior:**
Validar maxLength (ex: 255 chars) ou truncar

**Actual Behavior:**
Aceita qualquer tamanho

---

### Issue #8: Inconsistência HTTP Method em /auth/me

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | UX |
| **URL** | `/api/v1/auth/me` |

**Description:**
GET /auth/me retorna 405. Apenas POST funciona. Quebra consistência REST (GET para leitura de recurso).

**Steps to Reproduce:**
Ver Issue #1

**Expected Behavior:**
GET para leitura, ou documentar apenas POST

**Actual Behavior:**
Apenas POST, sem documentação clara

---

### Issue #9: Dashboard/Metrics endpoint ausente na OpenAPI

| Field | Value |
|-------|-------|
| **Severity** | 🔵 Low |
| **Category** | Documentation |
| **URL** | `GET /api/v1/stats/today`, `/api/v1/stats/weekly` |

**Description:**
Os endpoints de stats funcionam bem mas não têm schemas de response documentados na OpenAPI, dificultando geração de clientes.

---

### Issue #10: webhooks endpoint sem validação de URL

| Field | Value |
|-------|-------|
| **Severity** | 🔵 Low |
| **Category** | Functional |
| **URL** | `POST /api/v1/webhooks/` |

**Description:**
O endpoint de webhooks aceita qualquer URL sem validação de formato. URLs inválidas como `not-a-url` são aceitas sem erro.

---

## Issues Summary Table

| # | Title | Severity | Category | URL |
|---|-------|----------|----------|-----|
| 1 | /auth/me responde 405 em GET | Critical | Functional | GET /api/v1/auth/me |
| 2 | priority aceita apenas inteiro (docs inconsistentes) | High | Doc/Functional | POST /api/v1/tasks/ |
| 3 | Login usa email em vez de username | High | Doc/UX | POST /api/v1/auth/token |
| 4 | Validador rejeita TLDs .test .local | High | Functional | POST /api/v1/auth/register |
| 5 | Quick Task usa raw_text não title | Medium | Doc/UX | POST /api/v1/tasks/quick |
| 6 | Empty string aceito em campos obrigatórios | Medium | Functional | POST /api/v1/tasks/ |
| 7 | Sem limite de tamanho em strings | Medium | Functional | POST /api/v1/projects/ |
| 8 | Inconsistência HTTP Method /auth/me | Medium | UX | /api/v1/auth/me |
| 9 | Stats sem schema na OpenAPI | Low | Documentation | /api/v1/stats/ |
| 10 | Webhook URL sem validação | Low | Functional | POST /api/v1/webhooks/ |

## Testing Coverage

### Endpoints Tested (26 total)
- `GET /api/v1/health`
- `POST /api/v1/auth/register` — sucesso, duplicata, campos faltando, octal injection
- `POST /api/v1/auth/token` — sucesso, senha errada
- `GET|POST /api/v1/auth/me`
- `GET|POST /api/v1/projects/` — criação, listagem, nome vazio, nome 500 chars, body vazio
- `GET /api/v1/projects/{id}`
- `GET|POST /api/v1/tasks/` — criação, listagem, string priority, empty title, full fields
- `POST /api/v1/tasks/quick` — raw_text ok, title sem raw_text
- `POST /api/v1/tasks/{id}/complete`
- `POST /api/v1/tasks/{id}/reopen`
- `GET|POST /api/v1/tasks/{id}/subtasks/`
- `POST /api/v1/contexts/` — criação, listagem, get by ID
- `GET /api/v1/stats/today`, `/api/v1/stats/weekly`
- `GET /api/v1/reports/daily`, `/api/v1/reports/weekly`
- `GET|POST /api/v1/webhooks/` — criação, listagem, get by ID

### Features Tested
- Autenticação e autorização (token JWT)
- CRUD completo de tasks, projetos, contextos, webhooks
- Quick task com parsing de linguagem natural
- Complete + reopen de tasks
- Criação de subtasks
- Stats e relatórios diários/semanais
- Validação de payload (campos obrigatórios, tipos)
- SQL injection via query params
- Injeção de caracteres especiais em nomes

### Not Tested / Out of Scope
- Interface frontend (apenas testes de API)
- WebSocket (não exposto no test stack)
- Webhook delivery real (apenas criação/consulta)
- Rate limiting (nginx) — não testado por falta de ferramenta de volume
- Autenticação OAuth2 social

### Blockers
- Nenhum blocker significativo

---

## Notes

### O que funciona bem ✅
- Toda a stack sobe limpa com Docker Compose (produção + teste)
- Migrations rodam automaticamente via entrypoint
- Health check funcional com DB connection check
- Quick task com parsing de linguagem natural em português funciona muito bem
- Stats e relatórios gerados corretamente com dados mock
- Proteção contra SQL injection via query params
- CORS configurado e funcional
- Nginx com rate limiting + compressão gzip

### Recomendações 💡
1. Adicionar suporte GET em `/auth/me` (ou remover do schema OpenAPI)
2. Adicionar validação `minLength` e `maxLength` em campos de string
3. Suportar `application/x-www-form-urlencoded` no `/auth/token` (padrão OAuth2)
4. Relaxar validador de email para aceitar TLDs de teste
5. Mapear string priority `"high"|"medium"|"low"` para inteiros na Task creation
6. Documentar schemas de response nos endpoints de stats/reports
7. Adicionar validação de URL no webhook creation
