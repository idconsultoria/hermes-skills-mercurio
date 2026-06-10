# Report Template — Codebase Architecture Diagnostic

Use this template to structure diagnostic reports. Populate each section by working through the 6 layers in the SKILL.md.

---

# 🏗️ Diagnóstico Crítico de Arquitetura — `<project-name>`

## 📊 Ficha Técnica

| Atributo | Valor |
|---|---|
| **Repositório** | `owner/repo` (public/private) |
| **Criado em** | YYYY-MM-DD |
| **Último push** | YYYY-MM-DD |
| **Linguagem** | Primary (N% code), Secondary |
| **Tamanho (Git)** | ~X MB |
| **Linhas de código** | N (código) + N (comentários) = N total |
| **Arquivos** | N total (N Python, N texto, N JSON...) |
| **Commits** | N (branch topology) |
| **Colaboradores** | User (N), User (N) |
| **Licença** | ✅ MIT / ❌ **Nenhuma** |
| **Testes** | ✅ pytest / ❌ **Zero** |

## 🧩 O Que Esse Repositório FAZ (Mapeamento de Subsistemas)

### N. `<Subsystem Name>` — pipeline diagram
```
input → component1 → component2 → component3 → output
```
**Clientes/Destinatários**: description
**Entrypoint**: path/to/file.py (N lines)

_[Repeat for each subsystem]_

## 🔴 PROBLEMAS CRÍTICOS (Prioridade Máxima)

### 🔴 N. `<Title>` (SEVERITY)
**Localização**: path/to/file.py:line
**Problema**: description
**Impacto**: what can go wrong
**Correção**: recommended action

## 🟡 PROBLEMAS ESTRUTURAIS (Média Prioridade)

### 🟡 N. `<Title>`
**Problema**: description

## ⚠️ PROBLEMAS OPERACIONAIS

### ⚠️ N. `<Title>`
**Problema**: description

## 📈 Métricas de Saúde

| Indicador | Nota | Justificativa |
|---|---|---|
| **Segurança** | 🟤 X/10 | ... |
| **Testabilidade** | 🟤 X/10 | ... |
| **Modularidade** | 🟡 X/10 | ... |
| **Manutenibilidade** | 🟡 X/10 | ... |
| **Documentação** | 🟢 X/10 | ... |
| **Configuração** | 🟤 X/10 | ... |
| **Infraestrutura** | 🟡 X/10 | ... |

**Nota geral: 🟤 X.X/10 — classification**
- 🟢 7-10: Saudável
- 🟡 4-6: Necessita atenção
- 🟤 0-3: Crítico, requer reestruturação

## 🎯 Recomendações Imediatas (Top 5)

1. **🔥 TITLE** — action description
2. **🧪 TITLE** — action description
3. **🔧 TITLE** — action description
4. **🏗️ TITLE** — action description
5. **🤖 TITLE** — action description
