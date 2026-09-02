# Biotechse — fatos da marca (design system v1–v3)

**Cliente**: Biotechse — biotecnologia agroindustrial (biodefensivos / biofábrica).
Sócio/designer responsável na ID: **Tácio**. Slogan: *"projetando as sementes da nova era"*.

## Paleta oficial (manual da marca)
| Cor | Papel | HEX | RGB | CMYK |
|---|---|---|---|---|
| abyss teal | primária | `#029190` | 2 145 144 | 81 20 45 4 |
| mint green | primária | `#00ffa3` | 0 255 163 | 61 0 58 0 |
| cream | apoio | `#f7eadf` | 247 234 223 | 3 10 13 0 |
| charcoal | apoio/contraste | `#2d2d2d` | 45 45 45 | 71 61 57 70 |
| off white | apoio/contraste | `#f2f1f0` | 242 241 240 | 6 5 6 0 |

Senha de uso (do manual): primárias = integralidade/frontier science (teal) + frescor/natureza
(mint); cream/charcoal/off white = trindade humanística + fins técnicos.

## Tipografia
- **Clash Display** (títulos) — gratuita, **Fontshare/CDN**, pesos oficiais **400/500**.
- **Tomato Grotesk** (corpo) — The Designers Foundry (ex-Grilli Type), **LICENCIADA**,
  NÃO está no Fontshare. Self-host em `assets/fonts/tomato-grotesk-{400,500,800}.woff2`.
  Regra: **negrito em texto = Tomato ExtraBold (800)**, nunca bolder sintético.
  Proxy gratuito até os arquivos chegarem: **Hanken Grotesk** (Google).

## Conceito do símbolo (pg3 do manual)
Símbolo = **"B" grotesk + dupla fita de DNA + folha** (os três pilares da marca).

## Manifesto (pg2)
> somos uma empresa com o agro no coração. o nordeste em nossas veias. e sergipe em nossa alma.

## Logo / lockup
- Wordmark "Biotechse" com **sufixo "se" em mint**; assinatura "Biotecnologia Agroindustrial".
- Aplicações: fundo claro (teal/símbolo), negativo sobre fundo escuro, símbolo isolado (pin/badge).
- **O manual NÃO traz malha de construção numérica nem área de proteção com medidas** —
  padronizar como regra operacional: margem mínima = altura do símbolo.

## Material visual
- **Liquid glass forte** (glassmorfismo colorido/flutuante), não glass neutro.
- Ícones **Solar Icons** (480 Design), variante **Linear/outline arredondado**, grid 24px,
  traço 1.5, pontas 100% arredondadas, CC BY 4.0.

## Contraste (calculado, WCAG)
charcoal sobre cream/off-white = **11–12:1** (AAA). teal puro como texto = **~3.2:1** (use teal-deep
`#01706f`). branco sobre teal #029190 = **3.85:1** (aprofunde botão p/ `#01807f`+).

## Entregas
- `biotechse-design-system-v1/v2/v3.html` em `/opt/mercurio-data/deliverables/`.
- v3 = contraste corrigido + identidade (motivo orgânico DNA/folha). Fonte Tomato ainda pendente
  (aguardando woff2 licenciados do cliente).