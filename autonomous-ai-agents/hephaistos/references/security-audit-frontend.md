# Auditoria de Segurança — Front-end

> Padrão reutilizável para auditoria de segurança em projetos React/Next.js/Vite.

## Escopo

Verifica: dependências conhecidas, hardcoded secrets, XSS vectors, Content Security Policy.

## Execução

### 1. Dependências (npm audit)

```bash
cd /mnt/ARQUIVOS/Projetos/<projeto> && npm audit
```

Classificar por severidade. Foco em **High** e **Critical**. Anotar CVSS, via de ataque e se é explorável no contexto do projeto (ex: react-router XSS via SSR não afeta CSR-only).

### 2. Hardcoded Secrets

```bash
search_files(path="src", pattern="api.?key|api.?secret|token|password|cookie|jwt")
```

Falsos positivos comuns: descrições de propostas que mencionam "tokens de IA", cookies de sidebar (shadcn/ui), variáveis de ambiente.

### 3. XSS / DOM Injection

```bash
search_files(path="src", pattern="dangerouslySetInnerHTML|innerHTML|document\\.write|eval\\(|new Function\\(")
```

Se encontrado em componente de biblioteca (shadcn/ui chart, etc.), verificar se o conteúdo é controlado (não vem de input do usuário). Se for, é aceitável.

### 4. Content Security Policy

Verificar:
- Vite config (`vite.config.ts`) — existe `cspNonce`?
- HTML head — existe `<meta http-equiv="Content-Security-Policy">`?
- Se nenhum: recomendar adicionar CSP com nonce.

### 5. Relatório

Formato do output:

```
📊 Visão Geral
  Total de dependências: N
  High: N  Moderate: N  Low: N

🔴 VULNERABILIDADES HIGH
  📦 pacote (vX-Y)
     └─ Título da vulnerabilidade
        Severity: high | CVSS: X.X
        Path: pacote → self

📋 RECOMENDAÇÕES
  1. npm audit fix --force
  2. Adicionar cspNonce no vite.config.ts
  3. Validar dangerouslySetInnerHTML
```

## Quando Executar

- Após mudanças significativas de dependências (package.json alterado)
- Antes de deploy em produção
- Quando o usuário solicitar explicitamente
- Como parte de kanban sprint de segurança
