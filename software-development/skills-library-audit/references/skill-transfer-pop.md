# POP — transferência de skills entre instâncias Hermes

Plano completo por trás da auditoria. Aplicar quando o pedido é levar skills para outra
instalação/cliente, não só listar. Marcadores de varredura: `portability-markers.md` (não
duplicar aqui).

## Objetivo

Transferir sem levar dado sensível, marca de cliente ou acoplamento à infraestrutura do dono.
A decisão do que entra precisa ser **regra, não impressão**: quem executar depois chega ao mesmo
resultado.

## Fases (passo → saída → aceite)

**F0 · Inventário** — listar as skills do disco, incluindo as que não aparecem no catálogo.
Saída: arquivo de triagem com nome, categoria, tamanho, ocorrências por família e densidade.
Aceite: 100% inventariado; nada fica fora por estar "escondida".

**F1 · Classificação** — aplicar as 3 faixas (T1/T2/T3), uma skill por vez, registrando
justificativa. Aceite: nenhuma skill sem faixa; duvidosas viram T2.

**F2 · Sanitização (só T2)** — substituir identificador por equivalente genérico:
caminho interno → caminho padrão da instalação; nome de cliente → "Cliente A"; cor/fonte de marca
→ token de exemplo; segredo → marcador de posição. Preservar o porquê e as armadilhas. Proibido:
reescrever método, apagar pitfall, alterar frontmatter. Aceite: zero segredo, método intacto.

Dois ajustes que a execução real exige:

- **Edição em lote avisa, não aborta.** Script de substituição deve contar cada troca
  (`str.count`/`re.subn`) e imprimir as de contagem zero como aviso — o mesmo boilerplate repetido
  em várias versões de template casa numa e não na outra, e abortar na primeira perda a rodada.
  Quem decide o que ficou é o portão (F3), não o editor. Ainda assim: falha dura para item crítico
  (credencial, caminho de conta), aviso para boilerplate.
- **Nomes de pessoa viram papel** ("designer responsável pela marca", "responsável pela proposta") e
  o autor no frontmatter vira o time/empresa — nome próprio em skill transferida não tem função.

### Execução do passe em escala

Método que sustenta F2 quando são dezenas de skills: cópia de estágio + **um script por fase,
numerado, re-executável**, e o aceite sempre pelo portão (F3), nunca pelo olho de quem editou.

1. **Dicionário canônico** em arquivo de texto, como fonte única da substituição, agrupado por
   família: pessoa, casa, cliente, ambiente/caminho, credencial. Ordem das trocas: **string longa
   antes da curta** (o composto captura o caso geral; a sigla solta depois só pega o que sobrou).
2. **Antes de substituir, mascarar blocos base64** (`@font-face`, payload de template): a troca
   dentro do blob corrompe o arquivo embutido e o defeito não aparece no diff de texto.
3. **Limite de palavra e caixa exata para sigla curta** — sem isso o portão vira ruído (`ID` casa
   *session ID*). Falso positivo se resolve no dicionário, não ignorando o achado.
4. **Passe de reparo** logo após as trocas: artigo duplo, concordância, citação órfã de arquivo
   removido, linha de índice apontando para pasta que não veio. Depois, portão de artefato.
5. **Frontmatter:** mexer **só** no que `yaml.safe_load` recusa. Para consertar, colher o texto entre
   a chave `description:` e a próxima chave do bloco e reemitir como bloco `>-`; ao final, validar
   **todos** os arquivos exigindo `name` + `description`, e deduplicar descrição repetida por
   **frase normalizada**, não por parágrafo (passes anteriores colapsam o texto numa linha só).
6. **Fechar com um pacote só:** portão em zero ⇒ reempacotar uma vez e entregar. Enquanto o portão
   acusa, iterar; depois dele, polir não muda o aceite e consome a rodada do sócio.

**F2b · Consolidação (drop + resgate)** — quando a skill é o pipeline da casa do doador (modelo da
própria marca + repositório/portfólio próprio), ela **sai** do pacote. Antes de remover:

1. **Resgatar o que é genérico** para dentro de uma skill que fica — renderizador, receitas,
   referências de método — e repontar as citações (inclusive o caminho do script dentro dos
   templates, que costuma citar a skill removida).
2. **Justificar a saída por byte, não por impressão:** comparar os arquivos duplicados com
   `diff`/hash. Idênticos ⇒ não se perde nada e a remoção vira argumento defensável; parecidos ⇒
   fundir o que falta antes de descartar.
3. Script resgatado volta **portátil**: binário do Chromium por variável de ambiente
   (`CHROME_PATH`) em vez de caminho absoluto, e nome genérico de entrada/saída.

**F3 · Validação (portão)** — re-varrer exigindo zero menções
(`scripts/portao_poluicao.py`); conferir frontmatter, existência dos arquivos citados
(`references/`, `scripts/`, `templates/`) e teste de fumaça nos scripts. Aceite: **uma menção já
barra** e devolve à F2.

- **Checagem de referência quebrada:** extrair de cada `SKILL.md` todo `references/*.md`,
  `scripts/*` e `templates/*` citado e testar existência **relativa à raiz de skills**, não à pasta
  da skill — caminho de skill irmã (`business/outra-skill/templates/x.html`) é legítimo e não é
  quebra.
- **Renomear pasta ou arquivo de skill invalida o ponteiro** (link relativo, `related_skills`, linha
  do índice): re-rodar a checagem depois de todo renome e comparar com a árvore do doador para
  separar quebra nova de herdada — a herdada já vinha quebrada e não bloqueia a entrega.
- **Rodar o portão também no conteúdo extraído do zip.** Zipar não limpa; o aceite é sobre o que
  chegou.

**F4 · Empacotamento** — pasta raiz versionada + LEIA-ME com índice (o que é cada skill,
dependências, como instalar) + triagem anexa **sem os termos encontrados** (só contagem por família e
faixa — a lista de termos nomeia exatamente o que se está excluindo). Nome com versão, nunca
reutilizado.

- **O relatório de limpeza não entra no zip:** ele nomeia o que foi removido (cliente, pessoa,
  pasta) e vira a contaminação que documenta. Entrega-se ao lado do pacote.
- **Descartar não é apagar em silêncio:** o relatório lista, item por item, o que saiu e o motivo —
  é o que o dono confere depois para saber que nada de útil se perdeu.

**F4b · Destino com marca própria (empresa irmã, cliente, outra unidade)** — o critério de limpeza
**inverte**: a marca do destino **fica** (é dele, e é o material que ele mais usa) e sai tudo que é
do doador **e** de terceiros. A pergunta não é "o que é secreto" — é "o que faria o material do
destino sair com a cara errada". Consequências práticas: logo/portfólio/cliente de terceiro e nome
de pessoa do doador saem; a identidade, os modelos e os assets do destino ficam intactos; a marca do
destino sai da lista de termos do portão.

**F5 · Verificação da entrega** — abrir o pacote, contar arquivos contra o manifesto, conferir
uma skill por pasta com seu arquivo principal, extrair em pasta limpa. Saída: pacote + relatório
do que ficou de fora e por quê. Aceite: contagem bate com o manifesto.

**F6 · Registro** — guardar a triagem e as exceções encontradas (skills no disco fora do catálogo)
para a próxima transferência começar do inventário pronto, não do zero.

## Ordem de execução

- Passe 1: T1 as-is — entrega rápida e já útil.
- Passe 2: T2 uma a uma, com decisão explícita de limpeza (cada uma pode exigir julgamento).
- Passe 3 (opcional): higiene do catálogo — corrigir/validar as skills fora do catálogo ativo
  antes de anunciá-las como parte do pacote.

## Fora de escopo (sempre)

Dado de cliente, contas e credenciais, marca de cliente, projetos internos em andamento.
Nenhum segredo é copiado — nem em comentário, nem em exemplo, nem "temporariamente".

## Formato do POP entregue

Documento real, não resumo em chat: HTML com a identidade da ID → PDF, nome versionado,
validado página por página antes de enviar. Anexar o resultado da triagem para quem recebe poder
auditar. Estrutura que funcionou: objetivo → regra de elegibilidade (tabela das 3 faixas) →
famílias de marcadores em cards → fases com Passo/Saída/Aceite → ordem de execução → fora de
escopo → anexos.

Receita do documento A4 corrido (serve para POP, relatório, parecer):

- `@page { size: A4; margin: 17mm 15mm 16mm }` no CSS e `Page.printToPDF` com
  `preferCSSPageSize: True`, `printBackground: True` e margens 0 — a margem vem do CSS.
- `break-inside: avoid` em cada bloco (fase, card, tabela) e `break-after: avoid` no título de
  seção: o defeito típico de fluxo é bloco partido e título órfão no pé da página — não é corte
  grosso que salte à vista, só aparece conferindo.
- Conferir depois de gerar: contagem de páginas do PDF **e** `vision_analyze` em cada página,
  perguntando explicitamente por texto cortado, transbordo de margem e título órfão. Só então
  entregar.
- **Contagem certa ≠ documento bem composto.** O defeito que passa é a **página final quase vazia**
  (10–25% de ocupação): perguntar à visão a **proporção ocupada de cada página**, não só se há texto
  cortado.
- **Última página se resolve por arquitetura, não por encolhimento:** `break-before: page` no título
  do bloco mais longo (o anexo grande ganha a última folha) ou redistribuir conteúdo — mexer em
  corpo/entrelinha recupera poucas linhas e não fecha o vazio. Depois da quebra, **medir também a
  página anterior**: a quebra troca o vazio de lugar (medido: 100%/12% → 30%/87% → 50%/78% — a
  última composição é a que se entrega).
- **A quebra fica no CSS** (classe no `h2`), não em `div` espaçador: HTML e PDF entregues ficam
  coerentes e a próxima edição não desfaz a paginação.
- Tipografia da ID sem caçar arquivo de fonte: o script `extrair_fontes.py` de
  `brand-design-system-html` tira Neulis Neue + Nunito Sans do template de proposta aprovado e
  grava em `fonts/` para uso com `url()` relativo.
