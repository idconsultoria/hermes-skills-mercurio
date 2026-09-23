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
pacote portátil para outra instalação/cliente, ou saber por que uma skill existe no disco e
não no catálogo ativo.

**Princípio:** classificar por **evidência lida**, nunca por nome de skill. Varra o conteúdo
real de cada `SKILL.md` e dos arquivos de apoio — a contagem sozinha mente.

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
execução) em `references/skill-transfer-pop.md`; o portão reutilizável em
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
- **Substituição mecânica quebra a gramática.** Trocar o termo do dono pelo genérico gera
"da a consultoria", artigo duplo e citação órfã de skill/arquivo que ficou fora do pacote. Rodar um
passe de reparo depois do dicionário e um portão de artefato (regex dos defeitos, não só dos termos)
— texto meio-consertado é pior que o original, porque parece revisado.
- **Nomes de arquivo e de pasta são chave de referência:** renomear invalida link relativo,
`related_skills` e linha do índice. Depois de qualquer renome, re-rodar a checagem de referência e
consertar só o que ela acusa; separar quebra nova de herdada comparando com a árvore do doador.
- **Nunca reconstruir de memória a lista de marcadores do dono:** ela vive em
`references/portability-markers.md` — reler antes de varrer.
