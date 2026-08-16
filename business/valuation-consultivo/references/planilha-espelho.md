# Planilha-espelho — mapa de abas, fórmulas e convenções

Referência para a skill `valuation-consultivo`. A planilha é o **espelho das 7 camadas** da metodologia. Seguir a skill `xlsx` para geração (openpyxl + recalc via LibreOffice).

## Abas (9)

| Aba | Camada | Conteúdo |
|---|---|---|
| `Resumo` | 6–7 | Football field, posicionamento da rodada, múltiplo do investidor, 3 frases de narrativa |
| `Premissas` | 1–3 | Todos os inputs em ranges + fonte + confiança |
| `Mercado` | 3 | TAM/SAM/SOM (pacientes/hectares × preço × penetração) |
| `Modelo` | 3 | rNPV (ou DCF) — o motor, com fórmulas vivas |
| `Cenários` | — | First Chicago: downside/base/case + probabilidades + valor ponderado |
| `Comparables` | 4 | Tabela de deals (upfront/milestones/royalty) + tabela de rounds |
| `Reverse` | 5 | "O que precisa ser verdade" — pico/POS implícitos vs base rates |
| `CapTable` | 7 | Pre/post, investimento, option pool, % investidor, múltiplo de saída |
| `Fontes` | — | Registro: premissa \| valor \| fonte \| URL/DOI \| data \| confiança \| status |

## Convenções (skill xlsx)

- **Cores:** input/hardcode = azul (0,0,255) · fórmula = preto · link entre abas = verde (0,128,0) · link externo = vermelho · premissa-chave = fundo amarelo (255,255,0).
- **Números:** moeda `$#,##0` com unidade no cabeçalho (ex: `Receita (R$ mm)`) · zeros como `-` · negativos em parênteses · % `0.0%` armazenado como fração (0,15 → 15,0%) · múltiplos `0.0x` · anos como texto ("2026").
- **Estrutura:** toda premissa em célula própria rotulada, referenciada por fórmula (`=B5*(1+$B$6)`), nunca `=B5*1.05`. Fórmulas consistentes na linha toda.
- **Recalc:** `python scripts/recalc.py output.xlsx` → `status: success`, `total_errors: 0`. **Um recalc verde prova que as fórmulas avaliam, não que estão certas** — conferir 2–3 células contra valores esperados.
- **Gráficos:** barras horizontais/stacked. **NUNCA pizza/donut** (preferência do usuário).

## Fórmulas-chave

### Modelo — rNPV (anos 0..N, linhas por fase)
```
P_acum(t)     = produto das transições até t        ex: =PRODUCT($B$8:C8)  (transições por linha)
Fluxo líq.(t) = Receita(t) − Custo(t)                ex: =C10-C11
Fluxo ajust.(t) = Fluxo líq.(t) × P_acum(t)          ex: =C12*C9
VP(t)         = Fluxo ajust.(t) / (1+r)^t            ex: =C13/(1+$B$6)^C$2   (r na Premissas)
rNPV          = SOMA dos VP                          ex: =SUM(C14:N14)
```
- `r` vem da aba `Premissas` (link verde).
- POS por fase vem de tabela pública (ver `dados-pos-e-benchmarks.md`) — para agri-biotech, probabilidades regulatórias próprias.

### Cenários (First Chicago)
```
valor_ponderado = SOMA(Cenário_i × Prob_i)   ex: =SUMPRODUCT($B$5:$B$7,C5:C7)
```
- Probabilidades somam 100% (célula de checagem: =SUM($B$5:$B$7) deve dar 1,00).

### Reverse ("o que precisa ser verdade")
- Pico implícito: colocar o valor-alvo X como input e inverter o rNPV → célula com fórmula que isola o pico (ex: pico = alvo ÷ (fator agregado calculado no Modelo)).
- Tabela comparativa: pico implícito | pico de pares | base rate (POS) | veredito (plausível? sim/não/ajustar).

### CapTable
```
post-money   = pre-money + investimento
% investidor = investimento ÷ post-money
% diluição   = (novas ações) ÷ (total após rodada)
múltiplo investidor = (valor de saída × % pós-diluição) ÷ investimento
```
- Checagem: pre = post − investimento; soma dos % = 100%.
- Incluir option pool e rodadas futuras (diluição projetada).

### Resumo — football field
- Tabela: método | pior | melhor | ponto central (rNPV, deals, rounds, cenários) — barras horizontais lado a lado.
- Célula de posicionamento: valor recomendado da rodada (limite inferior do meio da faixa) + justificativa em célula de texto.
- Múltiplo do investidor nos 3 cenários.

## Nomenclatura

- Arquivo: `Valuation_<Empresa>_v<N>.xlsx` — **nunca reutilizar nome** (entregas com versão).
- Abas em PT-BR, sem acento em nomes de aba se preferir evitar `'` (nomes com espaço exigem aspas em referências entre abas: `='Premissas Inputs'!$B$5`).

## Verificação pós-geração

1. `recalc.py` → success, 0 erros.
2. Conferir 2–3 células calculadas (ex: rNPV total, % investidor) vs valor esperado à mão.
3. `markitdown output.xlsx` — abas presentes, sem placeholder.
4. Zero pizza/donut; barras horizontais OK.
5. `Fontes` preenchida para toda premissa sem fonte marcada como "a validar".
