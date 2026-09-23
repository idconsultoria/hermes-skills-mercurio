# Dossiê focado em PRODUTO (variante "a oportunidade X")

Quando o pedido inclui "foca muito nisso, e deixa só 1–2 slides sobre a empresa": reorganize o mesmo modelo da ID em torno do produto, não da instituição. Caso de referência: **Dossiê de Parceria ID × Fábrica de Mentores v2** — 16 páginas, 10 delas sobre a Jornada de IA, 2 sobre empresa/resultados.

## Estrutura (16 slides, 1 slide = 1 página)
1. capa co-branded ·
2. resumo do produto em uma página (slide teal): parágrafo + 2 colunas de 3 itens + caixa de promessa central ·
3. **escadinha** das etapas/níveis (slide "Metodologia", 4 fases) ·
4. os níveis lado a lado (slide "Investimento", 3 cards; o antigo "valor" recebe nível + duração) ·
5-7. **um slide por curso/nível** (forma do slide "Entendimento": parágrafo de abertura + coluna de 3 itens + coluna de 2) ·
8. como a turma funciona na prática (slide "Impacto", 3 métricas) ·
9. a plataforma (forma do slide "Garantia") ·
10. **acesso experimental** (clone do slide "Garantia") ·
11. resultados do produto até aqui (slide "Quem já confiou") ·
12. quem conduz (slide "Sobre a ID") ·
13. resultados em clientes (clone do slide "Impacto") ·
14. o que cada lado coloca na mesa (slide "Responsabilidades") ·
15. próximos passos + contato ·
16. contracapa.

Proporção a mirar: 65-70% do dossiê no produto. Proibido incluir preço, condições ou validade — o acesso experimental e a reunião são o próximo passo.

## Técnica de clonagem de slides
- Extrair as seções com `re.findall(r'<section\b.*?</section>', html, re.S)` e remontar na ordem desejada (`head + slides + tail`), em vez de só substituir texto: permite **duplicar** uma forma (Garantia, Impacto) em dois slides diferentes.
- Aplicar substituições **escopadas por slide** (função `fill(s, old, new)` com assert de presença) — nunca no HTML inteiro, senão um mesmo placeholder de formas duplicadas recebe o texto errado.
- Título/subtítulo: trocar via regex no bloco `.slide-head` (`<h2>…</h2>` + `<p>…</p>`), não por string literal.
- ⚠️ **Rótulos `<h3>` das colunas vêm do template** ("Cenário atual", "O que garantimos", "Custo de não agir"…). Sempre reescrevê-los para o novo slide; e localizar o `<h3>` correto pelo placeholder que vem depois dele (`rfind('<h3>', 0, pos_do_placeholder)`), porque a ordem das colunas varia.
- Forma "Entendimento do Desafio" é a única com `<p class="lead">` — é a forma a usar quando o slide precisa de parágrafo de abertura além das colunas.
- A forma "Escopo & Entregáveis" tem 3+2 itens e **não** tem parágrafo de abertura; não use para produto denso.
- Concordância: "Dossiê de Parceria" é masculino → "Preparado por" (o template traz "Preparada por").
- Remover menção a "organização Teal" quando o cliente não deve ver esse traço: `assert html.count('Teal') == 0` antes de entregar.

## Verificação (obrigatória antes de entregar)
1. `python3 build…py`: conferir `placeholders restantes: []`, `slides: N`, nenhuma substituição não encontrada.
2. Render PDF com Chrome headless + CDP `Page.printToPDF` (`preferCSSPageSize=True`, `printBackground=True`) e `@page { size: 1920px 1080px }` → 1 slide por página.
3. Conferir a contagem de páginas do PDF (regex `/Type\s*/Page[^s]`) contra o número de slides.
4. Conferência visual: `pdftocairo -png -r 60 -f N -l N arquivo.pdf saida` (~20s/página) e olhar com visão as páginas de maior risco (slides com texto longo, rótulos novos, capa) — checar corte, sobreposição e quebra de título.
   - ⚠️ Não confiar em captura headless via CDP de página com muitos slides e ~5 MB (SVGs de fundo): o `captureScreenshot` com clip devolve imagem truncada/duplicada. `pdftocairo` sobre o PDF final é o caminho confiável.
   - `pdftoppm` travou nesta máquina; usar `pdftocairo`.
