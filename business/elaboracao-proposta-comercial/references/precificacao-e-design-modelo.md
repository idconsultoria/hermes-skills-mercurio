# Precificação e Design do Modelo — Proposta Comercial ID

Absorvido de `proposta-comercial-consultoria` (merge 24/09/2026). Validado 14/08/2026
com deep-research de 40+ fontes (HBR, VeraSage/Ron Baker, RAIN Group, Win Without
Pitching, Consulting Success, McKinsey/BCG/Bain SCR, Proposify).

## Precificação por valor (nunca hora)

- Preço fixo por projeto (padrão B2B, buffer 1,3-1,5x, change order) evoluindo para
  value-based (ROI ~5x); retainer "Pay for Access" pós-projeto.
- Desconto: 10% off ≈ −33% lucro → desconto só em troca (pacote, antecipação,
  escopo). Negociar escopo, nunca taxa.
- 3 opções Good-Better-Best com fences claras: Better ≈ 1,4-1,8x o Good,
  Best ≈ 2,0-3,0x; médio "Recomendado"; tabela de preços por linha fecha
  35,8% mais (Proposify).

## Estrutura SCR slide a slide

Capa → Resumo executivo (com preço, escrito por último) → Entendimento do desafio
(com custo de não agir) → Escopo & entregáveis (com exclusões explícitas) →
Metodologia/cronograma → ROI antes do preço → Prova social → Investimento
(3 opções) → Condições → Responsabilidades → Sobre nós → Próximos passos + assinatura.

- Discovery antes de propor (nunca proposta fria): qualificar fit, orçamento,
  decisor, prazo; quantificar valor na conversa.
- Condições: validade 14-30 dias, pagamento com entrada + marcos,
  confidencialidade. Follow-up planejado (3-5 dias + antes do vencimento);
  apresentar ao vivo.

## Decisões de design do modelo (preferências do usuário)

- **Capa**: bloco central à direita do escudo (x 810-1900): logo do cliente
  (placeholder `{{CLIENTE_LOGO_URL}}`) ao lado da logo ID com divisor vertical →
  título 96px (Title) + subtítulo 36px → meta em 4 colunas. Nada no canto
  superior esquerdo.
- **Slides padrão**: diamond teal (símbolo da ID) à esquerda do título 60px (H1);
  subtítulo 24px empilhado ABAIXO do título; bullets brancos; ícones estilo
  Lucide (traço fino teal) nos títulos de coluna e cards de ROI — sem exageros.
- **Transição**: slide de fundo teal (contornos claros) com título 96px.
- **Final**: logo ID + "Proposta válida até {{VALIDADE}}" teal `#1AAEBD` + disclaimer.
- Ajustar **um slide de cada vez** com validação do usuário — nunca refazer o
  deck inteiro numa tacada.

## Arquivos de referência (estado da sessão 14/08)

- **Guia de Princípios (12 princípios)**: `/opt/data/Guia_Principios_Propostas_Comerciais.md`
  (entregável canônico; condensado em `references/guia-principios.md`).
- **Modelo HTML (15 slides, marca ID, ~87 placeholders)**:
  `/opt/data/Modelo_Proposta_Comercial_ID.html`
- **Builder Python do modelo**: `/opt/data/work/minuzzo/build_template_v2.py` —
  alterar o modelo é editar o builder e rodar
  `work/minuzzo/.venv/bin/python work/minuzzo/build_template_v2.py`
  (gera o HTML com fontes/assets base64 embutidos).
- **Assets de marca**: `/opt/data/work/minuzzo/logo_id.svg` (logo completa com
  tagline — capa/final), `logo_id_mark.svg` (símbolo + "ID"),
  `logo_id_diamond.svg` (símbolo teal puro — slides padrão),
  `bg_cover.svg` / `bg_content.svg` (fundos do deck), fontes Neulis Neue Bold +
  Nunito Sans em `work/minuzzo/fonts/`.
- **Deck de referência visual** (aprovado pelo usuário):
  `/opt/data/Proposta_Minuzzo_slides_v3.html` — "compare com o v3" = extrair
  posições/cores/estilos reais dele por inspeção programática.

## Pitfalls

- Não recriar assets da marca à mão — extrair do vetor original
  (ver skill `html-pdf-fidelity`).
- `browser_vision` é impreciso para posicionamento — verificar via
  `browser_console` (computed styles/rects).
- Placeholders no padrão `{{NOME}}`; o builder usa f-strings Python (chaves
  duplas escapadas) — cuidado com `{{fn(...)}}` virando literal
  (ver reference do html-pdf-fidelity).
