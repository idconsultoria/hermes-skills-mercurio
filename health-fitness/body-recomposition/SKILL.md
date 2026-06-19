---
name: body-recomposition
description: Tracking de métricas corporais (peso, BF, composição) + cálculos de TDEE/BMR, déficit calórico e timeline para recomposição. Cobre setup de CSVs, cálculo de métricas e geração de gráficos de evolução.
category: health-fitness
---

# Body Recomposition — Projetos de tracking & cálculo

Skill de classe para qualquer projeto de recomposição corporal (perda de gordura preservando massa magra). Abrange desde o setup dos CSVs de tracking até os cálculos de déficit e timeline.

## Trigger conditions

Use esta skill quando o usuário:
- Iniciar um projeto de tracking de peso/BF/gorduras
- Pedir cálculo de déficit calórico, TDEE, BMR
- Quiser saber quanto tempo leva pra chegar a X% de BF
- Pedir gráfico de evolução de peso, BF ou composição
- Mencionar "projeto" + nome grego/de mitologia + saúde

## Estrutura de arquivos

```
projeto-ares/              # Nome do projeto — algo que remeta ao objetivo
├── peso.csv               # Pesagem diária (jejum, manhã)
│   data,peso_kg,horario,observacao
├── composicao.csv         # Gordura corporal (medidas menos frequentes)
│   data,gordura_corporal_pct,metodo,observacao
```

**Regra:** métricas diferentes vão em CSVs separados — não juntar tudo num mesmo arquivo. Frequências de coleta diferentes justificam arquivos diferentes.

## Tracking diário

O usuário pesa em jejum quase todo dia. Registrar com:

```
data,peso_kg,horario,observacao
YYYY-MM-DD,XX.X,jejum,
```

Para BF (quando houver medida):

```
data,gordura_corporal_pct,metodo,observacao
YYYY-MM-DD,XX,Gemini Live/Bioimpedancia/etc,
```

## Cálculo de déficit calórico

Passos para responder "quanto déficit pra chegar a X% de BF?":

### 1. Coletar dados

- Peso atual (kg) — do CSV ou do usuário
- BF atual (%) — do CSV ou do usuário
- BF alvo (%)
- Idade, altura (cm), sexo
- Frequência de treino (resistência x/sem, cardio x/sem)
- Nível de atividade sexual (se relevante, ~200-300 kcal/h)
- Ocupação (sedentário/ativo)

### 2. Composição atual

```python
massa_gorda = peso * bf_percent
massa_magra = peso - massa_gorda
```

### 3. Peso alvo (preservando massa magra)

```python
peso_alvo = massa_magra / (1 - bf_alvo)
gordura_a_perder = massa_gorda - (peso_alvo * bf_alvo)
```

### 4. BMR — Mifflin-St Jeor

**Homens:**
BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade + 5

**Mulheres:**
BMR = 10 × peso(kg) + 6.25 × altura(cm) - 5 × idade - 161

### 5. TDEE estimado

- Base sedentária: BMR × 1.2
- Adicionar gasto médio diário de exercícios:
  - Resistência: ~250-350 kcal/sessão
  - Cardio moderado: ~300-400 kcal/sessão
  - Sexo moderado-intenso: ~200-300 kcal/h
- Dividir total semanal por 7 para média diária
- TDEE = base sedentária + média diária de exercícios

### 6. Déficit recomendado

- **Seguro e sustentável:** 300-400 kcal/dia
- **Limite para preservar músculo:** até 500 kcal/dia (exige proteína alta + treino pesado)
- Acima de 500 kcal/dia → risco alto de perda muscular

### 7. Timeline

- 1 kg de gordura ≈ 7.700 kcal
- Total de calorias a queimar = gordura_a_perder × 7700
- Dias = total_calorias / deficit_diario

### 8. Proteína

- Mínimo: 1.6 g/kg de peso atual
- Ideal: 2.0-2.2 g/kg
- Distribuir em 4-5 refeições

### 9. Documentação de treinos

Quando o usuário fornecer uma programação de treinos, estruturar em
arquivo separado (`treinos.md`) no diretório do projeto.

**Formato recomendado:**

- Tabela da semana (dia → manhã → tarde) mostrando o ciclo
- Cada treino nomeado (A/B/C/D) com:
  - Lista de exercícios em ordem de execução
  - Séries, repetições e notas de execução
- Cardio separado por tipo:
  - Zona 2 (esteira inclinada, 115-130 bpm, 20-30 min) — pós treino
  - Natação (roteiro: aquecimento + tiros + volta calma)
- Seção de volume semanal consolidado (sessões por tipo)

**Boas práticas:**
- Compostos pesados no início de cada treino
- Zonas de repetição mescladas (6-10 força + 10-15 hipertrofia)
- Cardio Z2 pós-treino (não antes) para não drenar glicogênio
- Dia de perna pode ficar livre de cardio para recuperação
- Um dia de descanso absoluto é essencial com 9+ sessões/semana

### 10. Planejamento alimentar

Quando o usuário pedir dieta, criar `dieta.md` no diretório do
projeto com refeição por refeição.

**Passos:**
1. Confirmar TDEE (já calculado ou recalcular)
2. Definir déficit alvo (350-400 kcal é o sweet spot)
3. Distribuir em refeições considerando constraints reais

**Constraints comuns a capturar:**
- Quantas refeições vêm de serviço de marmita (1 ou 2 por dia)
- Nível de esforço aceitável na cozinha (pão com ovo = mínimo,
  cuscuz = máximo, panela = exceção)
- Se tem marmita contratada, especificar exatamente para eles:
  "150g proteína magra + 200g carboidrato + vegetais + 15ml azeite"
- Finais de semana livres ou controlados

**Formatação para WhatsApp (sem markdown tables):**

```
NOME REFEICAO (horario — tempo prep)
XXX kcal | XXg P | XXg F | XXg C
ingredientes separados por linha
```

**Macro verification:**
- Somar manualmente as calorias de cada refeição e verificar
  se fecha no alvo (±10 kcal é aceitável)
- Proteína deve ficar entre 1.6-2.2 g/kg de peso ATUAL
- Se gordura passar de 35% das calorias, ok — o importante é
  caloria total + proteína
- Se carbo ficar abaixo de 35%, verificar se treino não sofre

**Exemplo de jantar minimalista (8 min, 1 panela):**
2 ovos mexidos + 1 lata atum escorrido + cuscuz 150g + 10ml azeite
= ~564 kcal, 47g P, 21g F, 45g C
Preparo: água fervendo no cuscuz + ovos/atum na frigideira simultâneo

### 11. Sono e recuperação

Em déficit com alto volume de treino (9+ sessões/semana), sono
é o principal recurso de recuperação.

**Diretrizes:**
- Mínimo 7h por noite, ideal 8h
- Horário consistente de dormir (variação máxima 1h entre dias)
- Desligar telas / filtrar azul 1h antes de dormir
- Sem cafeína após 15h (cortisol já elevado pelo déficit + treino)
- Quarto escuro e fresco (18-20°C)
- Se acordar de madrugada, não pegar celular

**Adequação ao horário de treino:**
- Natação 08h → acordar 07h → dormir 23h (8h de sono)
- Treino à tarde → pode dormir um pouco mais (23:30-08:00)
- Consistência do horário de dormir importa mais que o de acordar

## Preferências do usuário (Gustavo)

- **Idioma:** pt-BR direto, zero rodeio
- **Formato de saída (arquivos/docs):** markdown com tabelas e maths explícitas, sem gráfico de pizza
- **Formato de saída (WhatsApp):** NUNCA markdown tables — usar texto puro estruturado com
  travessões e quebras de linha. WhatsApp não renderiza tabelas.
- **Macros/precision:** "sou chato com isso" — mostrar a conta explícita (soma manual de
  cada refeição, verificação contra alvo). Não arredondar preguiçosamente.
- **Tracking:** CSV em vez de markdown — CSV é dados de verdade, markdown é só visualização
- **Projeto tem nome simbólico** (ex: Ares, deus grego) e o nome fica como identidade do projeto
- **Altura:** Quando pedir altura não informada, usar estimativa (175cm, média BR) e sinalizar explicitamente no texto

## Pitfalls

- **Não adivinhar altura sem avisar** — usar estimativa mas sinalizar explicitamente
- **Não dar déficit >500 kcal/dia como primeira opção** — sempre começar pelo seguro (300-400)
- **Não mergear métricas diferentes no mesmo CSV** — peso vai num arquivo, BF em outro
- **Não usar execute_code para os cálculos** — o tool pode ser bloqueado; fazer a conta manualmente ou com terminal/python normal
- **Calcular proteína pelo peso ATUAL, não pelo peso alvo** — o tecido magro atual é que precisa de suporte
- **Gasto calórico de sexo** não é piada — 4h/sem de atividade moderada-intensa é relevante (~171 kcal/dia) e deve ser incluído no TDEE
- **Confirmar número de marmitas antes de planejar dieta** — 1 vs 2 marmitas/dia muda completamente a estratégia do jantar. Assumir errado = plano inutilizável.
- **Natação muda o TDEE significativamente** — 2×/semana com tiros de alta intensidade adiciona ~100 kcal/dia ao gasto médio. Não ignorar.

## Referências

- `references/` — estudos de caso e exemplos de cálculo (se aplicável)
