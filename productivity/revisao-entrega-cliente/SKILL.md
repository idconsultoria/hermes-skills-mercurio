---
name: revisao-entrega-cliente
description: "Use ao revisar entrega de cliente antes de apresentar."
trigger: Pedido para revisar, auditar ou opinar sobre um artefato antes de entregar/apresentar ao cliente (documento de processo, especificação operacional, diagrama, deck, PDF).
related_skills: [reunioes-diarizadas, identidade-visual-id]
type: Orchestrator
timestamp: 2026-09-21T12:00:00Z
---

# Revisão de entrega ao cliente

Revisar é **ler e reportar**, não consertar. O material pertence ao cliente e ao dono do projeto: aponta-se o problema, pergunta-se o que fazer, e só então se altera — item por item, com OK explícito.

## Quando usar

- "Revise esses documentos, estão completos?"
- "Algo que você adicionaria?"
- Conferência final de peça que vai a cliente (especificação, diagrama, proposta, PDF).

## Procedimento

### 1. Inventariar e medir antes de opinar

Liste os arquivos com tamanho e estrutura (`wc -l -c`; cabeçalhos). Diga o que está lá — o inventário já mostra se algo prometido não veio (o pacote pode ter 2 arquivos e faltar o terceiro). Se o material chegou compactado, extraia para pasta própria antes de ler.

### 2. Verificar que a peça **abre** de verdade

Peça visual não se julga pela descrição do autor: conte os elementos. Em SVG/HTML de diagrama, confirme `viewBox`, nº de tarefas e nº de gateways e **compare com o texto que o acompanha**. Contagem que não bate = trecho cortado ou peça de outra versão.

### 3. Conferir imprimibilidade (o erro mais silencioso)

- Fator de escala = largura útil da página ÷ largura do canvas; multiplique o corpo da fonte. Abaixo de ~6pt a peça não serve impressa.
- Canvas fixo em px **sem `@media print`** cai em 1 página A4: canvas de 3740px dá fator ~0,16 → corpo de 11,5px vira ~1,8pt. Saída: paisagem pré-dimensionada, tiling em páginas, ou exportar PNG/PDF em resolução nativa.

### 4. Conferir identidade da ID

Peça de cliente sai em teal `#14b8a6` + navy `#0a1929`, Neulis Neue nos títulos e Nunito Sans no corpo. Cor de template genérico (azul de sistema, roxo de dashboard) destoa da marca — aponte.

### 5. Cruzar artefato × decisão registrada

O erro que mais custa: o documento está bonito e **contradiz o que foi decidido**. Compare nomes de dono/supervisor, metas numéricas, papéis e prazos com a última decisão registrada (ata, base de conhecimento). Divergência **se reporta e se pergunta** — não se resolve por conta própria.

### 6. Reportar em quatro blocos

1. **O que está completo** — diga primeiro e com honestidade; na maioria dos casos a maior parte está boa, e começar pelo defeito queima credibilidade.
2. **Lacunas por tema**, cada uma com o motivo prático de importar (não só "falta seção X").
3. **Conflitos a confirmar com o dono**, em bloco separado, pedindo a resposta.
4. **Sugestões numeradas**, pedindo OK antes de tocar em qualquer arquivo.

Checklists temáticos (diagrama de processo, especificação operacional, renderização/impressão,
documento no timbrado gerado a partir de markdown): `references/checklists-revisao.md`.

## Pitfalls

- **"Já que estou aqui, vou corrigir"** — alterar material do cliente sem OK é o pior erro possível neste trabalho, mesmo quando a correção é óbvia e a divergência é factual.
- **Opinar sem abrir a peça.** Renderize/leia e conte elementos; impressão visual de descrição de terceiro não é revisão.
- **Julgar layout sem testar a conversão.** SVG estilizado só por custom property CSS (`var(--x)`) vira mancha preta em conversor que não é navegador — a variável não resolve e o default do SVG é preto. Para PDF, cor literal no SVG (atributo `fill` ou `<style>` interno com hex) ou geração pelo próprio navegador.
- **Ignorar dependência de rede.** Fonte por `<link>` do Google Fonts = tipografia perdida offline; em peça arquivável, embuta ou defina fallback.
- **Supor que a ferramenta está instalada porque o gerenciador de pacotes disse sim.** Confirme com um render real (ou screenshot de HTML trivial) antes de construir o fluxo em cima dela — sucesso de instalação não prova binário funcional.
- **Avaliar diagrama de processo só pela estética.** Gate sem ramo "não/reprovado" não é gate; ciclo de melhoria prometido no texto sem seta de retorno no desenho é lacuna; e SVG desenhado à mão rotulado "BPMN 2.0" não abre em bpmn.io/Camunda nem versiona diff.
- **Confundir ausência com falha.** Artefato que não existe no pacote é lacuna de conteúdo; artefato que existe e está incompleto é lacuna de profundidade. Separe os dois ao reportar.

## Verificação

- [ ] Inventário completo do pacote, com tamanhos, antes de qualquer juízo.
- [ ] Peça visual aberta/contada, com números conferidos contra o texto que a acompanha.
- [ ] Imprimibilidade e identidade conferidas.
- [ ] Cruzamento com a decisão registrada feito; conflitos isolados para confirmação.
- [ ] Nenhum arquivo alterado; sugestões numeradas e submetidas à aprovação.
- [ ] Retorno em quatro blocos (completo / lacunas / conflitos / sugestões).
