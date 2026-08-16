# Métodos de Valuation — fórmulas, quando usar, críticas

Referência técnica para a skill `valuation-consultivo`. Para cada método: fórmula, inputs, quando usar, críticas. Fontes: Damodaran (younggrowth 2009), IPEV Guidelines (2022), Stewart/Allison/Johnson (2001), Kellogg & Charnes (1999), Cassimon et al. (2003/2011), Wikipedia (Startup valuation; First Chicago Method).

## 1. rNPV — Risk-Adjusted Net Present Value (MOTOR para pré-receita com pipeline)

**Fonte:** Stewart, Allison & Johnson (2001), "Putting a price on biotechnology", Nature Biotechnology, doi 10.1038/nbt0901-813. Padrão da indústria para biotech.

**Fórmula:**
```
rNPV = Σ_t [ (Receita_t × P_acum(t)) − (Custo_t × P_acum(t)) ] / (1 + r)^t
```
- `P_acum(t)` = probabilidade acumulada de sucesso até o período t (produto das transições fase a fase).
- `r` = custo de capital do estágio (early-stage biotech/deeptech: 15–25%).
- Inclui: custos por fase (P&D, CAPEX de laboratório, clínica/regulatório), receita pós-lançamento (pico × rampa × declínio por expiração de patente).

**Passos para a conversa:**
1. Mapear fases (pré-clínica → clínica → registro → lançamento) e duração de cada uma.
2. POS por fase: tabela pública por área (ver `dados-pos-e-benchmarks.md`) — agri-biotech: probabilidades regulatórias próprias.
3. Receita pós-lançamento: mercado total × preço × penetração no pico × anos de exclusividade.
4. Custos por fase e investimento de capital.
5. Descontar a r (15–25%) e somar.

**Crítica/limitações:** ignora flexibilidade gerencial (ver Real Options); sensível à POS e ao pico — por isso a skill pede ranges e cenários.

## 2. DCF ajustado para young companies (Damodaran)

**Fonte:** Damodaran, "Valuing Young, Start-up and Growth Companies" (2009) — texto completo analisado.

**Ajustes vs DCF tradicional:**
1. **Total beta** = market beta ÷ correlação com o mercado → captura risco total do investidor não diversificado; custo de equity 25–35%+ nos primeiros anos, caindo conforme atrai VC diversificado e converge no IPO.
2. **Probabilidade de sobrevivência:** base Knaup/Piazza — só ~25% das software firms sobrevivem 5 anos; avaliador ajusta (exemplo Secure Mail: 60%).
3. **Valor esperado dos ativos:**
   `EV = V(going concern) × (1 − p_fail) + V(distress sale) × p_fail`
   Exemplo do paper: US$177,56M × 0,6 + US$0 × 0,4 = **US$106,54M** (vs US$202M do VC Method).
4. Projeções bottom-up (TAM × participação × preço), margens convergindo para pares maduros.

**Uso na skill:** empresas com receita inicial; nunca WACC tradicional puro em early-stage.

## 3. Venture Capital Method

**Fórmula:**
```
post-money = exit value ÷ (1 + r)^n
pre-money  = post-money − investimento
```
- `r` = retorno-alvo do investidor (anjo/seed 50%+; early VC 30–40%; late 25–30% — domínio, validar).
- Exit value = múltiplo ou DCF no ano de saída.

**Crítica (Damodaran):** retorno-alvo fixo ignora risco, tempo e diferenças entre empresas — "flawed and should be replaced" como método principal. Usar como **cross-check** rápido, nunca como motor.

## 4. Berkus Method

**Fonte:** Dave Berkus; consolidado em Wikipedia Startup valuation.

**Valor por fator (US$ 500k–2M cada, cap pre-money ~US$ 2–2,5M):**
1. Ideia sólida (valor básico)
2. Protótipo (reduz risco de tecnologia)
3. Equipe de gestão de qualidade
4. Relacionamentos estratégicos
5. Lançamento/vendas

**Uso:** seed pré-produto. Fraco para biotech com CAPEX de laboratório (o valor do ativo de laboratório não aparece nos fatores).

## 5. Scorecard (Bill Payne)

**Fonte:** Bill Payne (angel investor); consolidado em Wikipedia/CFI.

```
valor = baseline × Σ(peso_i × score_i)
```
- Baseline: valuation mediano de rodada anjo da região (típico US$ 1–2M pre-money).
- Pesos: equipe 30% · oportunidade/tamanho 25% · produto/tecnologia 15% · concorrência 10% · canais/parcerias 10% · necessidade de capital adicional 5% · outros 5%.
- Cada fator pontua 0–2x vs baseline.

**Uso:** seed/anjo; cross-check em estágios mais avançados.

## 6. First Chicago Method (PWERM)

**Fonte:** Wikipedia First Chicago Method; IPEV (PWERM).

**Fórmula:**
```
valor = Σ(cenário_i × prob_i)
```
- Cenários típicos: downside / base / case, cada um com seu valuation (DCF, múltiplo ou rNPV).
- Probabilidades somam 100%; cenários precisam ser mutuamente exclusivos.

**Uso na skill:** obrigatório como camada de cenários — mostra consciência de downside (persuasivo para investidor).

## 7. Real Options (avançado)

**Fontes:** Kellogg & Charnes (1999), "Valuation of a Biotechnology Firm: An application of real-options methodologies" (decision tree + binomial); Cassimon et al. (2003), "The valuation of a NDA using a 6-fold compound option" (doi 10.1016/S0048-7333(03)00089-1); Cassimon et al. (2011), "Incorporating technical risk in compound real option models to value a pharmaceutical R&D licensing opportunity" (Research Policy, doi 10.1016/j.respol.2011.05.020); Loch & Bode-Greuel (2001), doi 10.1111/1467-9310.00212.

**Ideia:** valor inclui flexibilidade (abandonar, adiar, expandir, licenciar). Compound options modelam decisões sequenciais (continuar/parar a cada fase).

**Uso na skill:** opcional, quando o usuário quer capturar valor de flexibilidade além do rNPV linear. Avisar que é mais complexo de explicar — subir de nível só se o usuário pedir.

## 8. Alocação entre classes de ações (IPEV)

**Fonte:** IPEV Valuation Guidelines (Dez/2022), seção early-stage.

Quando há preferred vs common (ou SAFE), o "headline value" (fully diluted × preço da última rodada) raramente reflete direitos/preferências. Métodos de alocação:
- **PWERM** — cenários de saída com probabilidades;
- **OPM** (option pricing method) — aloca o valor atual entre classes via distribuição contínua de outcomes;
- **CVM** (current value method) — valoriza como se vendesse hoje;
- **Hybrid** — mistura cenários + OPM.

**Fatores qualitativos a checar a cada data de medição (IPEV):** performance vs expectativas; burn rate; aceitação de mercado; pivôs; timing/preço da próxima rodada; condições de mercado; tipo/proximidade de exit.

## 9. Comparables de deal (âncora de mercado)

**Estrutura típica de licenciamento:**
- **Upfront** — pagamento na assinatura (sinaliza valor da tecnologia validada).
- **Milestones** — pagamentos por marcos (clínicos, regulatórios, comerciais).
- **Royalties** — % sobre vendas pós-lançamento (típico em pharma ~2–15% com medianas ~5–8% — domínio, validar por deal; agri-biotech: % sobre venda de sementes ou $/hectare, validar).
- **Equity/colaboração** — participação ou co-desenvolvimento.

**Implied platform value:** somar upfront + VP dos milestones + VP dos royalties do deal → compara com o valuation da empresa. Ver `dados-pos-e-benchmarks.md` para exemplos reais.
