# MBB Executive Summary — Prompt Template

Use este template ao pedir para agy (ou outro agente) gerar a primeira página/capa de um relatório executivo no padrão McKinsey/BCG/Bain.

## Template de prompt

```markdown
REESCREVA A PRIMEIRA PÁGINA (header id="summary") de [caminho/para/arquivo.html] no estilo MBB (McKinsey/BCG/Bain).

## Estrutura obrigatória

### Capa — minimalista, branca, informacional

- Fundo: #FFFFFF (branco puro)
- Zero gradientes, zero glassmorphism, zero backdrop-filter, zero sombras
- Badge: "Relatório-Síntese Executivo" (uppercase, 12px, cinza, borda sutil)
- Título: 48px, bold, tracking negativo, cor #0C0E12
- Subtítulo: 20px, medium, cor #3E4250
- Metadados: "Preparado para: [cliente]" | "Julho 2026" | "Confidencial — Fase: [fase]"
- Grid 2x2 com métricas-chave: número grande (32px, bold, #0C0E12) + descrição (14px, #3E4250), divisórias com borda #B4B8C4

### Framework SCR

**SITUAÇÃO** (1-2 frases):
[Contexto. O que o leitor precisa saber. Ex: "O Brasil tem 78,3% das famílias endividadas..."]

**COMPLICAÇÃO** (1-2 frases):
[O que mudou. Por que agir. Ex: "Apps financeiros existentes são passivos..."]

**RESOLUÇÃO** (60-70% do espaço). Use bold-bullet:
- **Claim principal em negrito (sentença declarativa completa)**
  - Bullet com evidência de suporte (dados, números)
  - Bullet com evidência complementar
- **Segunda claim em negrito**
  - Evidência correspondente
- **Terceira claim em negrito**
  - Evidência correspondente

## Regras de conteúdo

- NÃO use "nível", "status", "projeto" ou "data" em lugar nenhum
- NÃO use "nós analisamos" ou "nossa pesquisa encontrou" — só findings
- Toda claim precisa de dado de suporte
- A bold sentence deve contar a história completa sozinha
- Zero jargão de consultoria — linguagem de líder de negócio

## Regras técnicas para PDF

- Use hex absoluto em inline styles (#FFFFFF, #0C0E12) — nunca var(--n-xxx)
- Use min-height em px (nunca vh)
- Inclua page-break-after: always no header
- NÃO use backdrop-filter: blur() — ele não renderiza em PDF
- Mantenha o resto do arquivo intacto
```

## SCR examples (extraídos de sessão CFP IA)

**SITUAÇÃO exemplo:**
"O Brasil tem 78,3% das famílias endividadas e mais de 72 milhões de CPFs negativados. Apenas 0,5% tem acesso a planejamento financeiro certificado (CFP®), devido ao custo de R$300-R$1.500/hora dos consultores humanos."

**COMPLICAÇÃO exemplo:**
"Apps financeiros existentes (Mobills, Organizze, GuiaBolso) são passivos — rastreiam despesas sem orientar. Nenhum oferece IA conversacional + gamificação + metodologia CFP®."

**RESOLUÇÃO exemplo (bold-bullet):**
- **CFP IA ocupa uma cadeira vazia: coach financeiro com IA que une gamificação, educação certificada e Open Finance — por R$19,90 a R$49,90/mês.**
  - Concorrência direta inexistente: Mobills e Organizze não têm IA orientativa nem trilhas CFP
  - Mercado validado por Albert (20M+ usuários) e Cleo (UK) — mas nenhum adaptado ao Brasil
- **TAM de R$4,2B com modelo freemium e ARR projetada de R$322K no ano 1, escalando para R$2,88M no ano 3.**
  - SAM de R$840M (20% do TAM), SOM de R$100M com penetração de 2,4%
- **MVP viável com infraestrutura existente: Open Finance (15M consentimentos), APIs Pluggy/Belvo.**
  - Checklist de conformidade LGPD + Lei do Superendividamento + diretrizes FPSB mapeado
  - Risco regulatório CVM mitigado por posicionamento educacional (não robo-advisor)

## Silent Read Test

Antes de entregar, leia APENAS as bold sentences em sequência. Se não contarem uma história coerente, reescreva.
