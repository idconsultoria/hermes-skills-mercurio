# Carta de Apresentação Criativa — design caprichado para profissionais de áreas criativas

A carta de apresentação é **o lugar do design** (o currículo é sempre formal — ver
regra na Fase 3 do SKILL.md). Para profissionais de comunicação, marketing,
jornalismo, design e influência, a carta é a amostra de estilo e o primeiro
impacto: **caprichar é obrigatório.**

## Fluxo com referências visuais

1. **Pesquisar referências** (Pinterest, Dribbble, Behance, Unsplash):
   - Query Pinterest: `cover letter design elegant`, `letterhead design minimal`
   - Query Dribbble: `cover letter`, `letterhead`, `editorial layout`
   - Referências típicas boas: preto/branco tipográfico, minimalismo com serif
     elegante, letterheads com hierarquia editorial, boxes de números/statistics
2. **Baixar 2-4 imagens** (Unsplash funciona via curl; Pinterest/Dribbble podem
   bloquear bot — usar browser e capturar descrição) e enviar ao host:
   ```bash
   mkdir -p /opt/data/tmp/refs && cp ref_*.jpg /opt/data/tmp/refs/
   scp -F ~/.ssh/config -r /opt/data/tmp/refs oracle-host:/home/ubuntu/refs
   ```
3. **Montar o prompt** com:
   - Conteúdo da carta (parágrafos com números/métricas, destinatário, data)
   - **Instrução explícita de caprichar**: "design editorial premium", "capriche
     MUITO no design", "inspire-se nas referências"
   - Descrição do que cada referência ensina (ex.: "ref_letter2: letterhead com
     nome grande em serif e linha fina dourada")
   - Caminhos das imagens: `Analise as imagens de referência em /home/ubuntu/refs/ref_*.jpg antes de desenhar`
   - Identidade do candidato (ex.: paleta do media kit) — a carta deve parecer
     feita pela própria marca do candidato
   - Elementos permitidos AQUI e proibidos no currículo: cards/boxes de números,
     cores de fundo suaves, assinatura estilizada, monograma
4. **Executar agy** em background, renderizar com `render_html_to_pdf.py`,
   **inspecionar visualmente** (vision_analyze) e iterar se a estética ficar
   aquém — o usuário prefere carta bonita, mesmo que custe mais uma rodada.

## Diretrizes de design (combinando referências + identidade)

- **Hierarquia editorial**: nome grande em serif (Georgia), labels em sans caps
  com letter-spacing, corpo limpo — a primeira coisa que o olho encontra é o nome
- **Paleta**: usar a identidade do candidato (ex.: media kit bege #F5EFE6, marrom
  #4A3728, dourado #C9A227) — a carta parece um item da marca pessoal
- **Composição**: header com linha fina, bloco "PARA" (destinatário) destacado,
  corpo com 4-5 parágrafos, números-chave em negrito ou boxes sutis, assinatura
  com linha
- **1 página A4**, print-ready, texto em HTML real (parseável), sem Google
  Fonts/CDN/emoji
- **Evitar**: fundo escuro, gradientes chamativos, fontes decorativas ilegíveis,
  exagero de cores — sofisticação > ruído

## Pitfalls

- Carta com card/min-height fixo quebra em 2 páginas no WeasyPrint — o
  `render_html_to_pdf.py` já injeta o AGY_LETTER_FIX, mas confira a contagem
- Pinterest/Dribbble bloqueiam bots: capture descrições textuais das referências
  como fallback (descrição rica já orienta o agy)
- O agy aceita imagens como input — SEMPRE forneça referências quando o usuário
  pedir "carta bonita/estética"
- Verificar visualmente SEMPRE: a visão do modelo pode achar bonito o que o
  usuário não acha — iterar até o usuário aprovar
