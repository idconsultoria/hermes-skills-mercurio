# Especificação: Análise Sistêmica (HTML)

> **Arquivo:** `analise-sistemica.html`
> **Escopo:** documento ÚNICO para toda a organização, combinando diagrama de loop causal, análise sistêmica e análise de ciclos.
> **Produzido após:** conclusão de TODOS os relatórios de dores setoriais + relatório de integração.

---

## Estrutura do documento

O HTML deve ser autossuficiente (D3.js inline, sem CDN) e conter três seções na seguinte ordem:

### Seção 1 — Diagrama de Loop Causal Global

Grafo D3.js force-directed contendo **todos os nós de todos os setores**:

- Nós coloridos por natureza:
  - `#C9A227` (gold) — Cultural
  - `#4AC6D3` (teal) — Técnica
  - `#1B2A6B` (indigo) — Organizacional
- Numeração dos nós: `S<setor>-<número>` (S1=Jurídico, S2=Inovação, S3=ASP, S4=CVT)
- Arestas direcionadas (setas) entre nós de setores diferentes representando integrações
- Arestas internas ao setor representando relações causais intra-setor
- Tooltips ao hover com: código, descrição, natureza, processos afetados
- Fundo escuro `#050A0F`, tipografia Nunito Sans (corpo) e Bricolage Grotesque (títulos)
- Layout responsivo
- Legenda de cores visível
- Filtro por natureza (Cultural/Técnica/Organizacional) e por setor

### Seção 2 — Análise Sistêmica

Texto analítico (rolagem abaixo ou ao lado do diagrama) cobrindo:

1. **Visão geral do sistema:** como os setores se interligam, quais são os fluxos dominantes, onde estão os pontos de estrangulamento.
2. **Padrões de recorrência:** problemas que aparecem em múltiplos setores com a mesma causa raiz.
3. **Intensificação:** nós onde o problema se agrava ao longo do tempo ou sob carga.
4. **Setores como entes:** como cada setor influencia e é influenciado pelos demais.
5. **Conclusão:** os principais desafios sistêmicos da organização.

### Seção 3 — Análise de Ciclos

Para cada ciclo detectado no grafo:

1. **Nome do ciclo** — título descritivo (ex: "Ciclo do Retrabalho Contratual")
2. **Tipo** — `R` (reforçador/vicioso), `B` (balanceador), `V` (virtuoso)
3. **Sequência causal** — descrição passo a passo do loop
4. **Nós participantes** — lista de códigos
5. **Setores envolvidos** — quais setores participam
6. **Severidade** — Alta/Média/Baixa (quantos processos/setores afeta)

Após listar todos os ciclos:

- **Ranking de nós-alavanca:** tabela ordenada por número de ciclos dos quais o nó participa
- **Top 5 ações de alavancagem:** quais nós, se resolvidos, quebrariam o maior número de ciclos
- **Classificação por hierarquia de Meadows:** identificar pontos de alavancagem (Parâmetros → Feedback → Estrutura → Metas → Paradigma)

---

## Requisitos técnicos do HTML

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise Sistêmica — <ORGANIZAÇÃO></title>
    <style>
        /* Fundo #050A0F, cores gold/teal/indigo */
        /* Tipografia: Bricolage Grotesque (títulos), Nunito Sans (corpo), IBM Plex Mono (códigos) */
        /* Seções com scroll suave, sticky diagrama opcional */
    </style>
</head>
<body>
    <header><!-- Título, subtítulo, data, legenda --></header>
    <section id="diagrama"><!-- D3.js inline --></section>
    <section id="analise-sistemica"><!-- Texto analítico --></section>
    <section id="ciclos"><!-- Tabela e análise de ciclos --></section>
    <script>
        // D3.js v7 completo inline (sem CDN)
        // Dados dos nós e arestas como JSON inline
        // Force simulation com parâmetros ajustados
    </script>
</body>
</html>
```

**Regras:**
- D3.js **obrigatoriamente inline** no `<script>` (nada de CDN)
- Dados como JSON inline (nada de fetch externo)
- Sem jQuery, sem Bootstrap, sem frameworks CSS
- CSS puro com design tokens ID Consultoria
- Mobile-first: diagrama legível em ~420px
