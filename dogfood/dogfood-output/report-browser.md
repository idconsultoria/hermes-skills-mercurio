# Dogfood QA Report — Frontend (Browser)

**Target:** TaskFlow frontend — http://172.19.0.1:8080  
**Date:** 2026-06-07  
**Scope:** UI/UX, navigation, form flows, NLP parsing, empty states, error handling  
**Tester:** Hermes Agent (browser-based exploratory QA)

---

## Executive Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 0 |
| 🟠 High | 1 |
| 🟡 Medium | 3 |
| 🔵 Low | 3 |
| **Total** | **7** |

**Overall Assessment:** Frontend está bem construído — design limpo, navegação fluida, sem erros de console. Destaque para o parsing de linguagem natural que funciona muito bem (contextos via `@tag` e prioridade via `pN`). O principal problema é a página de relatórios que não carrega dados.

---

## Issues

### Issue #B1: Página de Relatórios não carrega

| Field | Value |
|-------|-------|
| **Severity** | 🟠 High |
| **Category** | Functional |
| **URL** | `/relatorios` (via sidebar) |

**Description:**
Ao navegar para a página de Relatórios, o frontend exibe um erro genérico: *"Não foi possível carregar o relatório. Tente recarregar a página."* Nenhum erro no console do navegador. A API de reports retorna erro — a rota exata que o frontend chama precisa ser investigada.

**Steps to Reproduce:**
1. Fazer login
2. Clicar em "Relatórios" na sidebar
3. Ver mensagem de erro no centro da tela

**Expected Behavior:**
Exibir o relatório diário com stats ou ao menos um empty state amigável ("Nenhum relatório disponível ainda").

**Actual Behavior:**
Erro genérico sem detalhes, UX quebrada.

**Screenshots:**
MEDIA:/opt/data/cache/screenshots/browser_screenshot_cca7242459874a4683877c00e5d56cc0.png

---

### Issue #B2: Empty states sem call-to-action para criar dados

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | UX |
| **URL** | Entrada, Hoje, Próximos, Projetos |

**Description:**
Todas as páginas com empty state exibem mensagens informativas mas sem botão de ação rápida para criar o primeiro item. Ex: "Sua entrada está vazia" e "Nada planejado para hoje" são apenas textos — o usuário precisa saber que deve usar o campo de input no topo.

**Steps to Reproduce:**
1. Criar conta nova
2. Navegar entre todas as views
3. Observar que empty states são apenas texto

**Expected Behavior:**
Adicionar CTA como "Criar primeira tarefa" ou um tour rápido para novos usuários.

**Actual Behavior:**
Apenas texto descritivo, sem ação.

---

### Issue #B3: Campos de formulário sem feedback visual de validação

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | UX |
| **URL** | Login e Cadastro |

**Description:**
Os formulários de login e cadastro usam o atributo HTML5 `required` mas não mostram feedback visual customizado quando o usuário tenta submeter campos vazios. O navegador exibe o tooltip padrão ("Preencha este campo"), que varia entre browsers.

**Steps to Reproduce:**
1. Ir para página de login
2. Clicar em "ENTRAR" sem preencher campos
3. Observar tooltip nativo do browser

**Expected Behavior:**
Feedback visual inline com styling consistente com o design do app.

**Actual Behavior:**
Validação nativa HTML5, sem customização.

---

### Issue #B4: Contexto "@ design" criado automaticamente via NLP funciona bem

| Field | Value |
|-------|-------|
| **Severity** | 🔵 Low |
| **Category** | Content |
| **URL** | Contextos |

**Description:**
Ao digitar `@design p3` no campo de input rápido, o sistema criou automaticamente um contexto "@design" e associou a task a ele com prioridade P3. Isso é um recurso excelente, mas a label "P3" aparece como "P3" em vez de algo mais descritivo como "Prioridade: Alta".

---

### Issue #B5: Botão "Excluir" contexto sem confirmação

| Field | Value |
|-------|-------|
| **Severity** | 🟡 Medium |
| **Category** | UX |
| **URL** | Página do contexto @design |

**Description:**
O botão "Excluir" na página de contexto não pede confirmação antes de deletar. Um clique acidental pode remover o contexto e todas as tasks associadas.

**Steps to Reproduce:**
1. Criar um contexto via NLP
2. Clicar em "Excluir"
3. Contexto é removido sem diálogo de confirmação

**Expected Behavior:**
Modal de confirmação: "Tem certeza que deseja excluir este contexto?"

**Actual Behavior:**
Ação destrutiva sem confirmação.

---

### Issue #B6: Webhook "ADICIONAR" button sempre desabilitado

| Field | Value |
|-------|-------|
| **Severity** | 🔵 Low |
| **Category** | Functional |
| **URL** | Configurações > Webhooks |

**Description:**
O botão "ADICIONAR" na seção de webhooks está permanentemente desabilitado (`disabled`), mesmo com URL preenchida. O webhook não pode ser adicionado via frontend.

**Steps to Reproduce:**
1. Ir em Configurações
2. Preencher URL do webhook
3. Botão ADICIONAR continua desabilitado

**Expected Behavior:**
Habilitar quando URL válida for preenchida, ou remover o botão se a feature não está pronta.

**Actual Behavior:**
Botão sempre disabled, funcionalidade inacessível.

---

### Issue #B7: Logout não redireciona para página pública inicial

| Field | Value |
|-------|-------|
| **Severity** | 🔵 Low |
| **Category** | UX |
| **URL** | Logout |

**Description:**
Após clicar "Sair", o usuário é redirecionado para a página de login, que é a página inicial. Funciona, mas não há feedback visual de que o logout foi bem-sucedido (além de ver o formulário de login).

---

## Issues Summary Table

| # | Title | Severity | Category | URL |
|---|-------|----------|----------|-----|
| B1 | Página de Relatórios não carrega | High | Functional | /relatorios |
| B2 | Empty states sem CTA | Medium | UX | Todas as views |
| B3 | Validação HTML5 nativa sem customização | Medium | UX | Login/Cadastro |
| B4 | NLP com @contexto funciona bem (observação) | Low | Content | Input rápido |
| B5 | Botão Excluir contexto sem confirmação | Medium | UX | /contexto/@design |
| B6 | Botão ADICIONAR webhook sempre disabled | Low | Functional | Configurações |
| B7 | Logout sem feedback visual | Low | UX | Logout |

## Testing Coverage

### Páginas Visitadas
- Tela de Login (com e sem credenciais, erro de senha)
- Tela de Cadastro
- Inbox (Entrada) — empty state
- Hoje — empty state
- Próximos 7 Dias — headers de dias
- Contexto @design — com task, complete flow
- Projetos — empty state + botão NOVO PROJETO
- Relatórios — erro de carregamento
- Configurações — perfil, Google Calendar (em breve), webhooks

### Fluxos Testados
- Registro de novo usuário → login automático
- Login com credenciais corretas
- Login com senha errada (erro exibido: "Email ou senha inválidos.")
- Logout
- Navegação sidebar (6 links)
- Criação de task via input rápido com NLP (`@design p3`)
- Conclusão de task (botão "Concluir")
- Visualização de contexto com task completada
- Empty states em 4 views diferentes

### O que funciona excepcionalmente bem ✅
- **NLP parsing** no input rápido: `@tag` cria contexto, `pN` define prioridade
- Sidebar com navegação fluida sem reload
- Empty states com linguagem clara em português
- Task completion com estado visual "concluída"
- Design consistente (dark sidebar + light content)
- Zero erros de console JS em toda a navegação

### Não Testado
- Criação de projeto via botão "NOVO PROJETO" (seria necessário preencher formulário)
- Edição de perfil
- Responsividade mobile
- Performance com muitas tasks
- Acessibilidade (screen readers, tab navigation)
