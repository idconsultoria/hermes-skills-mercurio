# Caso real: Projeto Ares (Gustavo) — v2

## Perfil

Idade: 27 anos
Altura: 178 cm
Sexo: Masculino
Ocupacao: Sedentario (escritorio/consultoria IA, WFH + reunioes + visitas)
Resistencia: 4x/sem (Push/Pull/Legs/Misto)
Cardio Z2: 3x/sem (20-30 min esteira inclinada pos-treino)
Natacao: 2x/sem (1.000m, terc/qui 08h, zonas 3-6)
Sexo: ~4h/semana, moderado a intenso

Peso inicial: 79.3 kg (13/06/2026, jejum)
BF inicial: 20% (medido por Gemini Live)
BF alvo: 14%

## Setup de tracking

/opt/data/projeto-ares/
├── peso.csv           # Pesagem diaria em jejum
│   data,peso_kg,horario,observacao
│   2026-06-13,79.3,jejum,Projeto Ares - primeira medida
├── composicao.csv     # Gordura corporal (medidas esporadicas)
│   data,gordura_corporal_pct,metodo,observacao
│   2026-06-13,20,Gemini Live,avaliacao inicial
├── perfil.md          # Perfil + TDEE + objetivo consolidado
├── treinos.md         # Programacao completa A/B/C/D + cardio + natacao
└── dieta.md           # Plano alimentar 2.100 kcal, 1 marmita/dia

## Calculo de deficit

### Composicao
Massa gorda: 79.3 x 0.20 = 15.86 kg
Massa magra: 79.3 - 15.86 = 63.44 kg

### Peso alvo (14% BF, sem perda muscular)
63.44 / (1 - 0.14) = 73.77 kg
Gordura a perder: 15.86 - (73.77 x 0.14) = 5.53 kg

### BMR (Mifflin-St Jeor, homem)
BMR = 10 x 79.3 + 6.25 x 178 - 5 x 27 + 5
BMR = 793 + 1112.5 - 135 + 5 = 1.776 kcal/dia

### TDEE (versao corrigida com 4x resistencia + natacao)
Base sedentaria (BMR x 1.2): 2.131 kcal/dia
Resistencia 4x/sem (4 x 300): +171 kcal/dia
Cardio Z2 3x/sem (3 x 300): +129 kcal/dia
Natacao 2x/sem (2 x 350): +100 kcal/dia
Sexo 4h/sem (4 x 300): +171 kcal/dia
TDEE total: ~2.700 kcal/dia

### Deficit adotado
Alvo: 2.100 kcal/dia (deficit ~600 kcal)
Proteina: 160g/dia (2.0 g/kg)

### Dieta pratica (1 marmita/dia)
Cafe (5 min): 514 kcal | 27g P | 33g F | 28g C
  3 ovos + 2 pao integral + pasta amendoim + manteiga + cafe

Almoco (marmita): 664 kcal | 53g P | 20g F | 64g C
  150g frango + 200g arroz + vegetais + 15ml azeite

Pre-treino: 110 kcal | 1g P | 0g F | 27g C
  1 banana + cafe

Jantar (8 min): 564 kcal | 47g P | 21g F | 45g C
  2 ovos + 1 lata atum + cuscuz 150g + 10ml azeite

Ceia (opcional): 250 kcal | 31g P | 8g F | 13g C
  30g whey + 200ml leite integral

Total c/ ceia: 2.102 kcal | 159g P | 82g F | 177g C

### Licoes aprendidas
- Altura real (178cm) vs estimativa (175cm) muda BMR em apenas ~20 kcal — baixo impacto
- Adicionar natacao 2x/sem ao TDEE foi um ajuste relevante (+100 kcal/dia)
- Usuario prefere texto puro (sem markdown tables) no WhatsApp
- Usuario e preciso com macros ("sou chato com isso") — mostrar soma manual
- 1 marmita vs 2 marmitas muda completamente a estrategia do jantar
