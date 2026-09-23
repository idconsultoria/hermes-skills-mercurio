# Slide da Phronesis — deck HTML da reunião de operações

Gerador: `/opt/mercurio-data/phronesis-slide/montar_slide.py` (+ `assets/`, `saida/`).
Saída: `saida/phronesis-slide-<AAAA-MM-DD>.html` e `saida/ultimo.html`.

## Estrutura (a ordem é o rito)

1. Capa — nome, data, ciclo, facilitador, duração
2. **Revisão de Metas** (abertura obrigatória) — faixa com os números do ciclo + cartões de
   meta com barra, falta e farol
3. **Progresso nas Metas** — o slide gráfico: barra por meta com a **marca vertical de onde
   deveríamos estar hoje** e o comparativo novo × herdado
4. Centramentos · 5. Definição do Facilitador · 6. Registro (o que vira encaminhamento)
7. Pauta (Proskenion / Synaxis / Epilogos) · 8. Extrapauta · 9. Synaxis · 10. Revisão da Ata
11. **Momento ATAH** — Alan Turing, Ateu e Homossexual\* (*e pai da computaria): é o espaço dos
    **projetos internos** da ID (agentes, automações, produto, cultura)
12. Momento Symplexis (projetos com clientes) · 13. Momento Syndesi (conexões/negociações)
14. Funil de Conexões · 15. Consolidação de Encaminhamentos · 16. Descompressão · 17. Fecho

Data padrão = segunda-feira da reunião: se hoje já é segunda, é hoje (o cron roda no dia).
Com `--sem-metas` o deck sai sem a seção de metas em vez de falhar.

## Identidade: de onde saem os assets

O **modelo de proposta comercial** (`elaboracao-proposta-comercial/templates/modelo_proposta.html`)
**não tem imagem raster** — os gráficos dele são `<svg>` inline. Extraia assim:

```python
blocos = re.findall(r'<svg\b.*?</svg>', html, re.S)      # 47 blocos, ~22 únicos
# dedupe por md5; selecione pelo viewBox/class:
#   viewBox="0 0 1920 1080" + class="bg"  -> fundo topográfico (usar o de ~230 KB, não o de 1 MB)
#   class="logo-id"                       -> logotipo ID (branco)
#   class="page-icon"                     -> diamante teal do cabeçalho
#   viewBox="0 0 24 24" class="hicon"/"ricon" -> ícones pequenos
```

- Confirme que o SVG usa `fill` **literal** (`#4ac6d3`, `#3a3a3a`) e não `var(--)`: os do
  modelo usam literal, por isso funcionam fora do CSS.
- Fontes: os dois `@font-face` com `data:font` base64 (Neulis Neue 700 `.otf` + Nunito Sans 400
  `.woff2`) saem do mesmo arquivo para um `fontes-id.css` — cole inline no deck (as duas somam
  ~130 KB) para funcionar offline.
- Retrato de referência (ex.: Turing): extraia do PDF da última reunião com
  `pymupdf.open(pdf)[pagina].get_images()` e embuta como `data:image/jpeg;base64,...`.

## Tokens do modelo (usar exatamente)

Preto `#000`, texto branco, teal `#4AC6D3`, teal escuro `#1AAEBD`, linha `#1B5A63`, mudo
`rgba(255,255,255,.72)`; títulos em **Neulis Neue**, corpo em **Nunito Sans**; slide
1920×1080; `h1` 96px, `h2` 60px, `h3` 28px, métrica 46px; card com borda 1.5px, raio 14,
fundo `rgba(27,90,99,.12)`; capa com bloco de 1090px deslocado para a direita (esquerda fica
como respiro do fundo topográfico).

## Decisões de layout que já custaram tempo

- **Cabeçalho em faixa flex (ícone + título lado a lado)**, não ícone absoluto + título com
  `margin-top`: com margem, o colapso de margem joga o título para cima do ícone e os dois se
  sobrepõem.
- **Fundos topográficos têm 230 KB cada**: colar o SVG inline slide a slide faz um deck de ~5 MB
  e um render de PDF de minutos. Se o deck crescer, o fundo deve ir para um `<img>`/sprite
  compartilhado em vez de repetir o SVG em cada seção.
- **Funil de Conexões**: por decisão do dono, fica com cartões-placeholder ("sem registro na
  semana") até existir processo de CRM funcional — não investir em automatizar colunas que
  ninguém alimenta. Só a coluna *Symplexis* espelha a planilha (carteira em execução).
- Nada de emoji; gráfico em barra, nunca pizza/donut.

## Entrega (sob demanda)

O deck é gerado **quando pedido**, não por cron. Rode o wrapper
(`bash /opt/mercurio-data/scripts/phronesis_slide.sh [AAAA-MM-DD]`), confira o `STATUS=OK` e as
flags de sanidade (`TEM_METAS`, `TEM_GRAFICO`, `TEM_ATAH`) e entregue o HTML no Telegram com a
linha `MEDIA:<caminho>` como a **primeira** da resposta, sozinha. Deck sem a seção de metas só
sai com `--sem-metas` e com aviso explícito no texto — nunca em silêncio.
