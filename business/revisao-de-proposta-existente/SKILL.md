---
name: revisao-de-proposta-existente
description: "Use ao revisar proposta já entregue, preservando o resto."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [proposta, revisao, comercial, google-docs, drive, pdf]
    related_skills: [elaboracao-proposta-comercial, google-docs-formatting, google-workspace]
type: Orchestrator
timestamp: 2026-09-17T00:00:00Z
---

# Revisão de proposta que já existe

Pedido típico: "reestruture a proposta X" / "troca o pacote Y dessa proposta". Não é
criar do zero — muda um pacote, um valor, um escopo ou uma seção, e **todo o resto tem de
ficar idêntico** (texto, tabelas, cores, quebras, formatação). Cobre proposta comercial,
orçamento e documento comercial já entregue ou em negociação.

## Regra-mãe

**Copiar o documento e editar por cirurgia. Nunca regenerar de markdown/HTML.**
Regenerar troca fontes, perde tabelas/estilos e produz um documento que já não é "a mesma
proposta com uma parte diferente" — que é exatamente o que foi pedido.

## Recebimento, sequência e retomada

- **Respeitar o gate de anexos:** se o usuário condicionou o início ao recebimento de
  documentos, apenas confirmar o briefing até que todos cheguem. Incorporar correções
  posteriores antes de executar, sem reabrir decisões já esclarecidas.
- **Conferir a fonte mais recente no arquivo:** ao receber uma transcrição substitutiva,
  verificar títulos dos documentos, continuidade das seções, tabelas e encerramentos;
  não declarar completude só porque o texto se apresenta como integral. Usar o anexo
  completo para evitar cortes da mensagem e deixar a versão anterior fora da edição.
- **Recuperar trabalho interrompido antes de refazer pesquisa:** ler os artefatos e os
  resultados preservados; logs resumidos são pistas, não comprovação de fatos omitidos.
  Consolidar fontes, achados confirmados e lacunas num checkpoint do trabalho. Se o
  usuário pedir continuação sequencial na sessão principal, terminar uma frente por vez,
  sem novas delegações nem exploração prolongada de logs.
- **Separar pendência de bloqueio:** um currículo ou comprovante indisponível fica marcado
  como pendente; não abandonar as partes independentes nem apresentar o conjunto como
  pronto. Informar brevemente o bloqueio real, não cada tentativa de ferramenta.
- **Relatar somente a etapa comprovada:** distinguir conteúdo inserido, formatação em
  revisão e entrega verificada. Não anunciar conclusão antes das provas do passo 6.

## Procedimento

1. **Identificar o alvo autorizado e as versões relacionadas antes de editar.** Procurar
no Drive (`drive search`) e conferir título, destinatário e pasta do cliente. Se o usuário
indicou um documento específico, revisar somente esse alvo; informar sobre versões irmãs
sem alterá-las por iniciativa. A existência de outro documento não amplia a autorização.
2. **Congelar o original** como linha de base do diff:
`$GAPI drive download DOC_ID --export-mime text/plain --output /tmp/antes.txt`.
3. **Copiar, nunca editar no lugar:** `drive.files().copy(fileId=ID, body={"name": "<nome>
— v2 <descrição curta>", "parents": [PASTA]})`. A versão vive no NOME; o arquivo que o
cliente já recebeu fica intacto. Guardar `id` e `webViewLink` para a entrega.
4. **Editar por cirurgia via Docs API** — conteúdo e estilo em batches SEPARADOS, sempre
partindo de um GET fresco para os índices (receita e pitfalls em
`references/troca-pontual-docs-api.md`).
5. **Fechar o ciclo em todas as seções** que citavam o item alterado: plano de trabalho,
responsabilidades, exclusões, resumo executivo, nota operacional e tabela de investimento.
Item que sai do escopo não pode reaparecer como prestação em outra página.
6. **Verificar** com três provas independentes — diff do `text/plain` exportado contra o
congelado, dump de estilos por parágrafo, e PDF com contagem de páginas + inspeção visual
da página alterada. Leitura de texto sozinha não atesta estilo.
7. **Entregar** o link do Doc novo + PDF versionado (`..._v4_<descrição>.pdf`), listando em
bullets **o que mudou e o que permaneceu igual**.

## Identidade institucional e anexos de qualificação

- **Aplicar a marca do destinatário institucional quando solicitada, sem mistura com a
  identidade da ID:** reutilizar logo, tipografia e elementos do documento aprovado;
  conferir também capas, cabeçalhos, rodapés e currículos anexos. Não criar um design
  system novo para uma revisão documental.
- **Distinguir identidade visual de vínculo profissional:** retirar marcas não autoriza
  inventar emprego, titulação ou experiência institucional. Quando também for pedido
  remover nomes de empresas, revisar corpo, tabelas, fecho, assinaturas e propriedade
  intelectual; não transferir direitos preexistentes ou responsabilidades materiais
  por simples substituição de nomes.
- **Tratar currículos como evidência:** separar PDF Lattes oficial, extrato secundário e
  currículo técnico elaborado. Data de coleta de agregador não é data de atualização do
  Lattes; resultado da busca oficial não comprova acesso ao currículo integral. Não
  apresentar um substituto como anexo obrigatório atendido sem aprovação do usuário.

## Regras comerciais da revisão

- **Calcular a validade pela data-base pedida:** converter prazo relativo em data final
  explícita e repetir a mesma condição em todas as ocorrências. Retomadas em outro dia
  não devem deslocar silenciosamente a data-base original.
- **Adequação para contratação pública exige conteúdo, não só rótulo:** carregar
  `analise-contratual`, cruzar o parecer com objeto, entregas, governança, aceite e
  pagamento. Parecer institucional de viabilidade em tese não é autorização da
  contratação concreta. Sinalizar cláusulas comerciais incompatíveis para decisão,
  sem mudar adiantamentos, preços ou responsabilidades silenciosamente.

- **Item que passa a ser mensal não vira total inventado:** publique a linha como
  `R$ X/mês` e pergunte quantos meses (ou a duração da alocação). Não estime prazo nem
  feche total de projeto sem o dono do número.
- **Incoerência herdada se SINALIZA, não se conserta:** divergência que já vinha da versão
  anterior (linha de detalhamento × subtotal, faixa × valor fechado) entra como pergunta
  objetiva na resposta. Número comercial é decisão do sócio.
- **Revisão que toca o preço** obriga a conferir resumo executivo e condições comerciais
  (validade, pagamento) — o documento não pode sair com dois preços.
- **Versão nova = nome novo**, no Drive e no PDF; nunca sobrescrever nem reutilizar nome.
- **Fechar a pendência na base de conhecimento:** se o pedido ficou registrado como
  pendente, propor o fato atualizado (`kb_note`) quando a revisão for entregue.

## Pitfalls

1. **Reescrever do zero "porque é mais rápido".** Perde formatação e a confiança de quem já
   viu a proposta; e preservar o restante pode ser o pedido explícito.
2. **Editar o documento original.** O cliente pode estar com o link aberto; a revisão nasce
   como cópia com nome novo.
3. **Assumir que o documento citado é único.** Conferir a pasta inteira antes de editar.
4. **Declarar pronto sem prova visual.** O texto pode estar certo com estilo/bullet errados,
   e o que o usuário vê é o estilo.
5. **Mexer só no trecho óbvio.** Trocar um pacote sem revisar as seções que o citam deixa a
   proposta contraditória.

## References

- `references/troca-pontual-docs-api.md` — edição cirúrgica no Docs via `batchUpdate`:
  `replaceAllText` com string verbatim, troca de bloco com `deleteContentRange` +
  `insertText`, reaplicação de estilo/bullets, e os erros de índice que aparecem quando
  conteúdo e estilo vão no mesmo batch.
- `references/inserir-tabelas-docs-api.md` — trocar bullets por seções com **tabelas
  nativas**: `insertTable` ancorado no parágrafo seguinte ao subtítulo, preenchimento de
  células de trás para frente, `preventOverflow` por linha, e os artefatos de parágrafo
  vazio / herança de estilo de título que o Docs cria.
- `references/proposta-para-contratacao-direta.md` — adequar a proposta a processo de
  **dispensa de licitação (art. 75, XV)**: as seções que o parecer exige (enquadramento
  P,D&I, delimitação negativa, matriz de enquadramento, equipe/governança/LGPD, matriz de
  riscos), por que os parceiros não aparecem nomeados e onde a substituição de nomes escapa.
- `references/captura-curriculos-lattes.md` — capturar Lattes (que exige clique humano no
  modal do CNPq) e LinkedIn autenticado, elaborar o currículo na identidade do contratado e
  entregar PDF individual + anexo na proposta.
- `templates/curriculo-profissional-identidade-cliente.html` — modelo A4 de currículo em
  identidade do **contratado** (não da ID), com as seções fixas e o rodapé de verificação:
  copiar e preencher um arquivo por especialista, para a equipe inteira sair no mesmo layout.
