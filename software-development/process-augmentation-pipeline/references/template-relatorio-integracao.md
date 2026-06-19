# Relatório de Integração — <ORGANIZAÇÃO>

> **Escopo:** análise das interfaces entre TODOS os setores mapeados da organização.
> **Setores analisados:** <SETOR-1>, <SETOR-2>, <SETOR-3>, <SETOR-4>
> **Produzido após:** conclusão dos relatórios de dores setoriais.
> **Alimenta:** `analise-sistemica.html` (diagrama de loop causal global).

---

## 1. Metodologia

Cada integração recebe um código `INT-NN` e é classificada em duas dimensões:

| Dimensão | Valores | Significado |
|----------|---------|-------------|
| **Tipo** | `ENTRADA` / `SAÍDA` / `BIDIRECIONAL` | Direção do fluxo de informação/dependência |
| **Qualidade** | `FLUIDA` / `FRICCIONAL` / `ROMPIDA` | Estado atual da interface |

A análise cruza os relatórios setoriais de dores com as transcrições para identificar:
- Handoffs que geram retrabalho
- Dependências sem SLA ou com SLA ignorado
- Comunicação informal que deveria ser estruturada
- Gargalos de integração que afetam múltiplos setores

---

## 2. Matriz de interfaces

| Código | De | Para | Tipo | Qualidade | Descrição |
|--------|----|-----|------|-----------|-----------|
| INT-01 | <SETOR-A> | <SETOR-B> | ENTRADA | FRICCIONAL | <descrição curta> |
| INT-02 | <SETOR-A> | <SETOR-C> | BIDIRECIONAL | ROMPIDA | <descrição curta> |

---

## 3. Análise por interface

### INT-01 — <título descritivo>

- **Fluxo:** <SETOR-A> → <SETOR-B>
- **Tipo:** ENTRADA | Qualidade: FRICCIONAL
- **Descrição:** <2-3 frases descrevendo o que acontece na prática>
- **Dores relacionadas:** DOR-<SETOR>-XX, DOR-<SETOR>-YY
- **Evidência:** "<citação literal>" (fonte)
- **Impacto:** <como essa fricção reverbera — prazos, qualidade, retrabalho>
- **Causa raiz inferida:** <por que essa interface é problemática>

[Repetir estrutura para cada INT]

---

## 4. Pontos de integração críticos

Interfaces classificadas como `ROMPIDA` ou `FRICCIONAL` com alto impacto (>2 setores afetados):

| Código | Impacto (setores) | Consequência principal |
|--------|:-----------------:|------------------------|
| INT-XX | 3 | |

---

## 5. Recomendações de integração

1. **<Título da recomendação>** — <1-2 frases>. Afeta INT-XX, INT-YY.
2. ...

---

> **Próximo passo:** estas integrações viram arestas no diagrama de loop causal global em `analise-sistemica.html`.
