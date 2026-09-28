---
name: skills-library-audit
description: "Use ao triar skills: quais servem em qualquer Hermes."
category: software-development
type: Research
timestamp: 2026-09-13T00:00:00Z
---

# Auditoria do acervo de skills (portabilidade e higiene do catálogo)

**Quando:** o usuário quer selecionar o que é universal ("quais dessas skills servem para
qualquer Hermes?", "gostaria de selecionar as que seriam universalmente boas"), montar um
pacote portátil para outra instalação/cliente, saber por que uma skill existe no disco e
não no catálogo ativo, ou **consolidar o acervo de skills de um perfil** — herdar, deduplicar,
purgar de escopo e dar estrutura de gerenciamento a um acervo que nunca foi curado.

**Princípio:** classificar por **evidência lida**, nunca por nome de skill. Varra o conteúdo
real de cada `SKILL.md` e dos arquivos de apoio — a contagem sozinha mente.

Para a receita completa de consolidação de acervo alheio (dossiê, herança, purga de escopo,
cluster que parece duplicata e não é) ver `references/consolidacao-de-acervo-alheio.md`.

## Procedimento

1. **Enumerar o disco, não o catálogo.** `find $SKILLS_DIR -name SKILL.md`; o caminho relativo
do diretório pai é `categoria/nome`. O disco pode ter MAIS skills do que o `skills_list` mostra.
2. **Varredura por marcadores.** Escrever um script `.py` com `write_file` e rodar com
`python3 script.py`. Nunca `python3 -c` inline, heredoc, nem one-liner com vários `grep`
encadeados entre aspas: o guard do gateway bloqueia payload inline grande ou não parseável e a
rodada se perde (recuperação: o comando bloqueado é salvo em `cache/blocked-scripts/` — melhor
reescrevê-lo como arquivo). Para leitura pontual, usar `search_files`/`read_file` em vez de
`grep`/`cat` no terminal. **Escopar toda varredura ao diretório de skills** — `find /` a partir
da raiz estoura o timeout. Para cada skill: ler `SKILL.md` + os arquivos
de texto em `references/`, `scripts/`, `templates/`; contar ocorrências **por categoria** e a
**densidade** (ocorrências / 10k chars), que separa "cita de passagem" de "depende disso".
3. **Ler os trechos que casaram.** Imprimir, por skill, os termos distintos que casaram (não só
o total) — é o que decide entre "exemplo ilustrativo" e "dependência real", em uma passada.
4. **Tiering:**
   - **T1 — universal:** nenhum marcador do dono, ou só convenções genéricas do Hermes.
     Método puro; levar como está.
   - **T2 — universal com limpeza:** método genérico, mas com exemplos, caminhos internos, marca
     ou nomes do dono embutidos. Declarar o que sai antes de levar.
   - **T3 — só com o dono:** depende de dados, contas, clientes, marca ou infra do dono.
5. **Reconciliar os totais antes de entregar.** O arquivo de triagem é a fonte da verdade: comparar
em código as listas que serão declaradas (T1/T2/T3) contra o resultado da varredura, exigindo que
**toda skill do disco apareça exatamente uma vez**. Total declarado é afirmação dura — soma que não
fecha é erro, não arredondamento; a skill que falta é a que foi classificada de memória em vez de
pela varredura.
6. **Entregar** em três blocos (ver Formato) e oferecer o empacotamento — não empacotar sem o ok.
7. **Empacotar** (quando pedido) **sob o POP aprovado** — plano primeiro, arquivo depois
(ver `## POP de transferência`); `zipfile` do Python, sem credenciais, e conferir o conteúdo do
zip contra a lista entregue antes de declarar pronto.

A tabela de marcadores, os falsos positivos e as receitas de empacotamento estão em
`references/portability-markers.md`; o plano de transferência completo (fases, portões, ordem de
execução) em `references/skill-transfer-pop.md`; a receita de consolidação de acervo alheio
(dossiê de evidências, herança, purga de escopo, dissolução de pasta) em
`references/consolidacao-de-acervo-alheio.md`; o portão reutilizável em
`scripts/portao_poluicao.py` (`<pasta> --termos termos.txt`, exit 1 se achar resíduo).

## POP de transferência (plano antes do pacote)

Pedido de transferência/empacotamento ⇒ **entregar o POP primeiro e aguardar ok**. O usuário quer
ler o critério e o fluxo antes de ver arquivo; executar direto queima a rodada. Essencial:

- Regra de elegibilidade em **3 faixas + densidade** decide tudo; na dúvida a skill **cai** para
  T2 — nunca sobe por otimismo.
- **Portão de validação:** re-varredura depois da limpeza exigindo **zero** menções; **uma só já
  barra** a skill e devolve para a sanitização. Divergência não avança de fase.
- **Sanitização** troca identificador por equivalente genérico e **preserva o porquê e as
  armadilhas** (é o valor da skill); proibido reescrever o método ou mexer no frontmatter.
- **Executa-se sobre cópia de estágio, nunca sobre a árvore de skills do doador**, com um script por
  fase, numerado e re-rodável: a origem fica intacta para recompor a rodada e para separar defeito
  novo de herdado. Receita do passe em `references/skill-transfer-pop.md` (F2).
- **Ordem econômica:** Passe 1 = T1 as-is (rápido, já útil); Passe 2 = T2 uma a uma, com decisão
  explícita de limpeza; Passe 3 = higiene do catálogo (disco > catálogo ativo).
- **Verificação antes de declarar pronto:** contagem de arquivos contra o manifesto + extração em
  pasta limpa; relatar também o que ficou de fora e por quê.
- **Credencial nunca entra** — nem em comentário, nem em arquivo de exemplo, nem "temporariamente".
- **Anexo de triagem que viaja sai sem os termos encontrados** — só contagem por família e faixa. A
  lista de termos nomeia exatamente o que se está excluindo (cliente, conta, caminho) e vira o
  vazamento que o pacote existe para evitar; a triagem completa, com termos, fica interna.
- **Duas vias do POP:** a interna pode citar nome de cliente como exemplo de marcador; a que
  acompanha o pacote para fora sai sem esses nomes. Dizer qual das duas está sendo entregue.
- **Auditoria de segredo se responde com varredura, não com memória** — padrões e classificação dos
  achados em `references/portability-markers.md` (seção de segredos).
- O POP é entregável de verdade, não conversa: gerar em **HTML com a identidade da ID**
  (teal/navy, Neulis Neue + Nunito Sans) → PDF, **nome versionado**, e conferir página por página
  (contagem + `vision_analyze`) antes de mandar. As fontes da marca saem do template de proposta
  da ID — receita em `html-pdf-fidelity`.

## Formato da entrega (preferência do usuário)

- Pedido de seleção ⇒ **três blocos de nomes** (T1/T2/T3), agrupados por área, **o critério de
  julgamento em UMA linha**, e **uma** pergunta de próximo passo no fim. Lista de nomes vence
tabela longa; nada de parágrafo explicando o método.
- Pedido explícito de formato vence o padrão: "faça apenas a lista" ⇒ só a lista, sem preâmbulo
  nem oferta.
- Trabalho pode ser minucioso (critério, o que achei e como usei); o **encanamento** (comandos,
  caminhos, nomes de ferramenta) não entra na resposta para Maxwell/Cleverton/Tácio — só com o
  Gustavo.
- **Aceite atingido é fim da linha.** Quando o portão fecha em zero, reempacotar e entregar na mesma
  resposta. Refino posterior que não muda o aceite (renormalizar texto, reauditar o já auditado,
  redocumentar) é ruído: o sócio corta com "está complicando, simplifique". Entregar o arquivo e o
  resultado em poucas linhas — a descrição do processo só se for pedida.
- **Redefinir o portão depois de fechá-lo reinicia o trabalho sem autorização.** Tendo o aceite
  atingido, um receio novo (formatação, estética do frontmatter, "e se o YAML não parsear?") não abre
  fase: pergunta se aquilo muda o que o destinatário recebe. Se não muda, vai para a lista do que não
  foi feito, não para outra rodada de script.
- **Cada script de batch-edit roda o validador de aceite na mesma rodada, antes do próximo script.**
  Script corretivo escrito sobre o output do anterior sem revalidar quebra o que o anterior
  consertou, e a pilha de scripts cresce enquanto o arquivo fica pior. O ciclo que trava é sempre o
  mesmo: um validador (o portão de poluição, `yaml.safe_load`, a checagem de referência) executado
  depois de cada escrita, não só no fim da fase. Se a validação já estava no script anterior, ela
  precisa estar no próximo também.
- **Snapshot antes de qualquer remoção em árvore sem controle de versão.** Se o alvo não tem git,
  `git init` + um commit de baseline é o que torna a rodada reversível; sem ele, apagar diretório
  de skill é irreversível e a única saída passa a ser reconstruir. Ignorar o diretório de
  versionamento (locks, cache, telemetria de uso, blob de backup) no primeiro commit, ou o
  baseline carrega lixo e ruído de diff. Guardar o commit de baseline **antes** do primeiro merge:
  restore posterior devolve também as pastas de origem, criando duplicatas nos destinos — a
  correção é reaplicar os movimentos logo depois do restore, não tentar dissolver o estado à mão.

## Pitfalls

- **Destino com marca própria inverte o critério de limpeza.** Para empresa irmã/cliente, a marca do
  destino **fica** e sai o doador e os terceiros — a pergunta é "o que deixaria o material do destino
  com a cara errada", não "o que é secreto". Sem isso, a limpeza remove justamente o que o destino
  mais precisa.
- **Portão roda duas vezes: na pasta e no conteúdo extraído do zip.** O aceite é sobre o que chegou;
  zipar não limpa nada.
- **Consolidação se decide por byte, não por impressão.** Antes de tirar uma skill do pacote
  alegando duplicação, comparar os arquivos com `diff`/hash — idênticos sustentam a remoção, e o que
  é parecido se funde em vez de descartar.
- **Sigla curta casa dentro do base64** e transforma o portão em ruído: mascarar payload antes de
  varrer (receita em `references/portability-markers.md`).
- **`GITHUB_TOKEN`, `HERMES_HOME` e `/opt/data` são convenção do Hermes**, não dado do dono: skill
de GitHub que só cita `GITHUB_TOKEN` continua T1. Julgar o termo pelo contexto, não pelo match.
- **Termos casam por acidente:** `Inter` (banco) casa *internal/interface*; usar o composto
(`Banco Inter`). **Handle ≠ nome** (o designer da ID aparece como `@n0ztr`, não "Tácio") — varrer
os dois, senão a skill some da triagem.
- **Disco > catálogo ativo.** Skills que o `find` acha e o `skills_list` não mostra costumam ter
frontmatter inválido (description com bloco repetido / aspa de fechamento perdida) ou requisito
de ambiente não satisfeito (`required_environment_variables` / `required_commands`, ex.: ambiente
kanban). `skill_view(name)` devolve `readiness_status` e `missing_*`; conferir o frontmatter com
`head -14 SKILL.md`. Não anunciar skill inativa como "pronta" — declarar a pendência.
- **`skills-repo-curator` é user-owned:** patch/`write_file` do curador autônomo nela é recusado
(`created_by=None`). Não insistir nem tentar variações — recomendar
`hermes curator adopt skills-repo-curator` ao usuário e registrar o procedimento em skill própria
(esta). O mesmo vale para qualquer skill criada à mão pelo usuário.
- **Frontmatter só se toca no que está inválido.** Se a descrição passa em `yaml.safe_load`, está
certa: descrição multilinha entre aspas é YAML válido, não defeito. Passes de "normalização"
redistribuem texto e **corrompem arquivo que estava bom** — o conserto vira mais trabalho que o
problema. Sintoma de frontmatter quebrado é a skill existir no disco e sumir do catálogo.
- **Campo YAML multilinha: parseia, não aplica patch por linha.** O modo de falha que corrompe
  catálogo inteiro é editar só a linha da chave: as linhas de continuação do valor antigo ficam
  órfãs e o arquivo quebra com `while scanning a simple key`. O caminho seguro é
  `yaml.safe_load` → alterar o **valor** no dict → reemitir o frontmatter → `yaml.safe_load` do
  texto novo **na mesma rodada**. Dois modos específicos que custam a rodada: (a) em
  `^description:[ \t]*(.*)$` o indicador `|-` cai em `group(1)`, não no resto do match — testar
  block scalar sobre `match.end()` nunca casa e a conversão roda sem efeito; (b) recarregar o
  próprio output do passo anterior e reparsear faz o sumario absorver o parágrafo no ciclo
  seguinte, porque o valor já foi alterado quando é lido de volta.
- **Validador que reprova uma categoria inteira de uma vez é o suspeito, não o acervo.**
  Antes de agir em lote sobre a saída do validador, reproduza **um** caso à mão. Três
  verificadores recorrentes que fabricam falha onde o arquivo está bom: conferir presença de
  campo só nos primeiros N chars do frontmatter (o `type:` de um frontmatter longo passa
  despercebido), ancorar a captura de descrição exigindo `\n` + letra seguinte (quebra quando a
  chave é a última do bloco) e contar skills percorrendo a árvore sem excluir o diretório de
  arquivo (conta o que você acabou de retirar). Confirmar por leitura antes de reescrever: versão
  restaurada de um campo é trabalho jogado fora.
- **Substituição mecânica quebra a gramática.** Trocar o termo do dono pelo genérico gera
"da a consultoria", artigo duplo e citação órfã de skill/arquivo que ficou fora do pacote. Rodar um
passe de reparo depois do dicionário e um portão de artefato (regex dos defeitos, não só dos termos)
— texto meio-consertado é pior que o original, porque parece revisado.
- **Nomes de arquivo e de pasta são chave de referência:** renomear invalida link relativo,
`related_skills` e linha do índice. Depois de qualquer renome, re-rodar a checagem de referência e
consertar só o que ela acusa; separar quebra nova de herdada comparando com a árvore do doador.
- **Nunca reconstruir de memória a lista de marcadores do dono:** ela vive em
  `references/portability-markers.md` — reler antes de varrer.

## Ferramenta de edição e o guard do gateway

- **`rm -rf` em lote e `git clean` exigem autorização explícita.** O guard bloqueia e a
  rodada para; o silêncio não é consentimento. Peça autorização antes, e **não reformule o
  comando para contornar** — a tentativa alternativa é a mesma ação. Quando o usuário já
  autorizou uma vez, a autorização vale para o comando **exatamente como ele pediu**;
  qualquer variação precisa de nova autorização.
- **Edição de conteúdo é sempre `read_file`/`patch`/`write_file`, um arquivo por vez.** O
  usuário pede isso explicitamente quando o acervo é grande: revisar N skills por script é
  rápido e cego, e arquivo por arquivo a revisão é o que produz merge com justificativa.
  Script fica para o que é mecânico e conferível (hash, contagem, varredura) — nunca para
  decidir o que entra e o que sai.
- **Apagar pasta tem alternativa que não apaga nada:** esvaziar o `SKILL.md` com `write_file`
  tira a skill do catálogo com o mesmo efeito, deixa a pasta presente para inspeção e não
  dispara o guard. Ofereça as duas e deixe a escolha com o usuário.

## Quando o pedido é "instale a estrutura e o cron"

- **Consolidação recorrente é executada por quem é dona do acervo**, não por quem está
  ajudando. O pedido de "ciclo disparado por cron" para o perfil de outra agente significa
  cron **no perfil dela**, com prompt que a faça rodar com a identidade dela. Instalar o
  cron no perfil errado cria dois donos do mesmo acervo.
- **Estrutura mínima antes do cron:** `AGENTS.md` (regras do acervo), `index.md` (catálogo
  com relações), `log.md` (diário append-only), `scripts/` de auditoria. Sem isso o cron
  roda às cegas e o acervo volta a inflar.
- **`consolidate: false` no config do perfil desliga a curadoria nativa** — verificar antes
  de instalar ciclo próprio, para não haver duas agendas brigando pelo mesmo acervo.

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e visual local): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/opt/mercurio-data/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
