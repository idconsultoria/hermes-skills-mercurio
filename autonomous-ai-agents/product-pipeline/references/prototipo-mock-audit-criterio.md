# Auditoria de Protótipo F4a — Critério Mock (rastreabilidade)

> Padrão validado no CFP IA (ago/2026): auditoria de rastreabilidade em DOIS PASSOS.
> Erro da 1ª auditoria: marcar "PARCIAL" para tudo porque o protótipo não chamava a API.
> Correção do usuário: mock data é ESPERADO em protótipo de alta fidelidade (F4a) — o critério
> certo é se cada passo do fluxo é REPRODUZÍVEL na tela com mock.

## Classificação (critério revisado)

- **DEMONSTRADO** — a demo reproduz o comportamento com mock (navegação, estados, copy).
- **DEMONSTRÁVEL PARCIAL** — reproduz parcialmente; falta um pedaço reproduzível.
- **NÃO DEMONSTRÁVEL** — não há como reproduzir na tela, nem com mock (ex.: Fluxo 4 inteiro ausente).

## O que NÃO é gap nesta revisão

- Não usar a API / não persistir / não ter backend conectado — **aceito** (fase de demonstração).
- Componentes sem callback para backend — só é gap se o fluxo de DEMONSTRAÇÃO não consegue
  reproduzir o passo (ex.: botão que não muda nada na tela E o flow espera mudança visível).

## Dois passos da auditoria

1. **v1 (critério backend):** tudo sai "PARCIAL" — útil como inventário, enganoso como veredito.
2. **v2 (critério mock):** reclassifica e isola os gaps REAIS de demonstração:
   - gaps de fluxo (passos sem tela, ex.: recuperação de sessão, trava de segurança, canais)
   - gaps de completude (tela existe mas faltam campos/cards/ações — ex.: botões sem `onAcao`)
   - gaps de consistência narrativa (mock contraditório — ex.: badge conquistada com data futura vs missão atual)

## Auditoria card-a-card do Dashboard

Para o dashboard, tabela: **card que o flow/PRD pede** | **card renderizado** | completo? | observação.
Identificar: cards ausentes (ex.: painel de alternativas da preditiva), cards extras justificados,
déficits funcionais (ex.: card com botões inertes), inconsistências numéricas (ex.: delta hardcoded
que não bate com os números do mock).

## Veredito útil

"Conta a história como storyboard vs como sistema" — a demo trava onde o produto promete
comportamento (botões de decisão). Listar os 3 ajustes de demo mais valiosos que NÃO dependem de
backend (ex.: preditiva viva com `onAcao`, conformidade FPSB no chat, perfil que reage aos dados).

## Execução prática (Pi Cost)

- Prompt auto-contido em `prompts/` do repo: lista de arquivos a ler, o que NÃO fazer (não editar),
  estrutura do relatório (matrizes, gaps com evidência `arquivo:linha`, backend pronto para conectar).
- Entrega: `product/engineering/auditoria-rastreabilidade[-v2].md` com `<!-- PHASE_COMPLETE: ... -->`.
- Custo típico: $0.02–0.04 por auditoria completa (v4-flash, 90%+ cache hit).
- **Continuar a MESMA sessão é requisito comum do usuário** — usar `pi --session <caminho-do-jsonl>`
  (append na mesma JSONL; verificar por crescimento do arquivo + ausência de sessão nova).

## Verificação de leitura (pi-session-audit)

O heurístico "cat/read_file vs ls" pode dar FALSO NEGATIVO: Pi Cost produz relatório substancial
(cita `arquivo:linha` exatas) mesmo quando o JSONL mostra só `ls`. Julgar pela QUALIDADE do artefato,
não só pelo grep.
