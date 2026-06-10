# forge_interview — Protocolo de Entrevista de Marca

Protocolo de 3 a 4 rounds de perguntas para extrair a essência da marca do usuário.
Usado quando o agente precisa entender o propósito, personalidade e direção visual
de uma comunidade, produto ou serviço antes de gerar o identity kit.

## Regras de Condução

- **Uma pergunta por vez.** Cada round é um bloco de perguntas relacionadas que o agente faz de uma vez. O usuário responde todas, então o agente prossegue.
- **Síntese a cada round.** Antes de fazer as perguntas do próximo round, resuma o que aprendeu no round anterior — mostra escuta ativa e valida o entendimento.
- **Tom:** Direto, curioso, sem julgamento. O agente não está avaliando as respostas, está extraindo o DNA da marca.
- **Anti-padrão:** Não pular rounds. Não fazer perguntas abertas demais que paralisam o usuário. Não deixar perguntas sem fazer porque o user já deu pistas — confirme explicitamente.
- **Idioma:** Responder no mesmo idioma que o usuário está falando. A entrevista deve soar natural, não traduzida.

## Round 1 — Essência (5 perguntas)

Foco: propósito, valor, persona, personalidade, anti-referências.

1. **Qual o propósito central da [comunidade/produto/marca]?** O que ela resolve na vida de quem participa?
2. **Qual frase define o valor que [ela] entrega?** Ex: "O lugar onde X vira prática, não hype."
3. **Quem é o [membro/cliente] que você mais quer atrair?** O core persona — nome fictício, cargo, nível técnico, o que busca.
4. **Quais palavras descrevem a *personalidade*?** 3-5 adjetivos concretos (nada de "inovador" ou "moderno" — coisas como: franco, denso, provocativo, acolhedor, cirúrgico, bruto, lúdico, pé-no-chão).
5. **O que [ela] não é?** Anti-referências — o que você quer evitar parecer? Se o usuário não sabe, anote como "não definido" e volte depois.

## Round 2 — Visual & DNA (5 perguntas)

Foco: identidade visual, relação com referências, metáfora central.

1. **Relação com [referência/marca existente].** O que você admira visualmente nela que quer trazer? O que não quer replicar?
2. **Cor.** A [referência] usa [cor X]. Quer manter a mesma família cromática ou desvio consciente? Se desvio, pra qual direção?
3. **Metáfora visual.** Se [a marca] fosse uma coisa física, o que seria? Laboratório? Oficina? Fórum? Estúdio? Feira? Coworking? Algo mais? (Dar exemplos ajuda)
4. **Nível de "intimidade" visual.**
   - **Sala limpa** — polido, profissionais, estruturado
   - **Garagem** — raw, artefatos, meio bagunçado, autêntico
   - **Híbrido** — profissional no acabamento, autêntico no conteúdo
5. **Símbolo/ícone/mascote.** Se a marca tivesse um símbolo (tipo pássaro do Twitter, foguete do Product Hunt), o que seria? Pode ser abstrato.

## Round 3 — Direção Visual (4 perguntas)

Foco: refinar paleta, mascote, layout, tom de voz.

1. **Temperatura de cor.** Dentro da família escolhida, qual matiz específico? (Dar opções concretas com hex codes)
2. **Mascote detalhado.** Se o usuário escolheu um mascote/símbolo no round anterior:
   - Estilo: cartoon vs. geométrico/abstrato?
   - Detalhes técnicos visíveis? (parafusos, engrenagens, circuitos ou sutis?)
   - Posição: sentado, andando, perfil?
3. **Layout/metáfora.** Reforçar a metáfora escolhida com perguntas de direção visual:
   - Elementos modulares?
   - Grid visível?
   - Espaço negativo generoso?
   - Sobreposições?
4. **Tom de voz.** Se a marca já tem um canal/veículo existente (ex: newsletter), como a nova marca se diferencia no tom?
   - Conversacional? Provocativo? Acolhedor?
   - Mistura? Em qual proporção?

## Round 4 — (Opcional) Técnico & Entregáveis

Usar quando o usuário pede execução imediata ou tem requisitos de formato específicos.

1. **Formato de entrega.** HTML, SVG, PDF, DESIGN.md, guia de estilo em markdown?
2. **Plataformas alvo.** Web, Telegram, Instagram, LinkedIn, GitHub?
3. **Prazo/urgência.** Precisa de algo funcional hoje ou pode iterar?
4. **Assets existentes.** Logos, cores, fontes que já usa e quer manter?

## Após a entrevista

1. Sintetizar todas as respostas num **BrandProfile JSON** (para uso interno do agente).
2. Carregar no contexto como: `FORGE_PREFLIGHT: context=pass brand=pass mode=identity image_gate=<status> mutation=open`
3. Prosseguir para `forge_forge` — geração do identity kit com 4 subagentes paralelos.
