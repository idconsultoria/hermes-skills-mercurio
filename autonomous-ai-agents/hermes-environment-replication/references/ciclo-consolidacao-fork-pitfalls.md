# Ciclo de consolidação do fork — pitfalls de update/evolve (lições 23/08/2026)

Complementa `skills-repo-curator` (que é user-owned/protegido — estes pitfalls são mantidos
aqui no umbrella curator-managed). Validações feitas no ciclo real de 23/08: +41 skills
(ID-core + apoio) ingressando no fork idconsultoria, index 41→83, 0 órfãos no grafo.

## 1. Grafo do catálogo vs grafo do disco — usar o helper versionado

`scripts/generate_graph.py` faz `os.walk` no **disco**. Num ambiente com dezenas de skills
untracked (overflow do canônico reesemeado — ex.: 140 SKILL.md no disco vs 83 no catálogo),
ele gera nós para TUDO → órfãos fantasma que não existem no index.

**Fix:** para o grafo do catálogo indexado, use o helper versionado
`scripts/generate_catalog_graph.py` (lê skills + relações do apêndice `## Relações entre
skills` no index.md; injeta em `skills-repo-curator/templates/graph.html`; escreve apenas
`skills_graph.html` + `graph_data.json`, nunca o index). Regra: se `find . -name SKILL.md`
contar mais que o total do catálogo, o grafo correto é o do catálogo, não o do disco.

## 2. Stage APÓS editar frontmatter (senão o commit pega a versão antiga)

Se você `git add <skills>` no início do update e DEPOIS corrige frontmatters (type,
timestamp, descrição) das próprias SKILL.md staged, o commit grava a versão **staged antiga**
— os fixes ficam como `M` não incluídos e o index lista `type` que as SKILL.md no repo não têm.

**Procedimento seguro:**
1. editar frontmatters/descrições primeiro;
2. SÓ então `git add`;
3. OU re-add (`git add <path>/SKILL.md`) após qualquer batch-edit.
Verificação antes do commit:
```bash
git show :<path> | grep '^type:'        # == working tree (ex.: type: ToolIntegration)
git status --porcelain | grep '^ M.*SKILL.md$'   # deve ser vazio
git diff --cached --stat
```

## 3. Frontmatter OKF de skills herdadas do canônico ("Hermes Agent" format)

Skills provenientes do repo canônico/Hermes usam:
```yaml
metadata:
  hermes:
    tags: [...]
```
e **não** têm `type:`/`timestamp:` no nível raiz (formato OKF). Ao ingressá-las no fork:
- adicionar `type:` — taxonomia OKF: Orchestrator / ToolIntegration / Reference / Template /
  Research / Method / Media / Creative / Health;
- adicionar `timestamp:` ISO (ex.: `2026-08-23T00:00:00Z`);
- descriptions single-line não-quoted → converter para `description: "..."` quoted.
- auditar com script de apoio que **informa** (lê frontmatter por regex; nunca edita index
  por script); validar YAML (`yaml.safe_load`) de todos os fronts alterados antes do commit.

## 4. Decisão editorial do catálogo do fork (preferência do principal da ID)

Quando o usuário pedir para "as skills novas entrarem no fork", o escopo é: **ID-core + apoio
à ID** (emissao-nfse, inter-api, gestao-financeira, auxiliar-adm, timbrados, motor-nfse,
cicd-oracle-preview/devops-artemishub, sdlc-review, github×7, coding-agents claude-code/codex/
opencode/merge-reconciler/computer-use, software-development×16: baas/dogfood/skill-authoring/
postgres/debug/etc.). **NÃO** incluir genéricas de plataforma do canônico (apple, creative,
smart-home, mlops, media, note-taking, social-media) — violam o prune/isolamento ID. Adicionar
por nome via `git add <path>` explícito, nunca `git add -A`.

## 5. Triagem de duplicatas: quatro assinaturas, quatro decisões

Classificar por **assinatura medida**, nunca por semelhança de nome. A mesma skill pode
cair em três ou quatro dos casos abaixo ao mesmo tempo; decidir por categoria (e não por skill)
é o que mantém a contagem reconciliada.

| Assinatura | Como medir | Decisão |
|---|---|---|
| Corpo idêntico após normalizar whitespace | hash do corpo sem frontmatter | remove a cópia; leva o arquivo de proveniência para o sobrevivente |
| Mesmo nome, corpos diferentes (1–99% de similaridade) | `difflib` no corpo + inventário de apoio dos dois lados | **fusão de mão dupla**: corpo de uma + apoio da outra; colisão de nome com conteúdo diferente vai para `_divergencia/`, nunca se escolhe |
| Mesmo domínio, um é subconjunto do outro | headings exclusivos do menor + linhas substantivas ausentes no maior | absorve no maior; o que fica de pé do menor é escrito como aprendizado, não copiado |
| Skill de outro agente / de outra plataforma | campo `author` + `platforms` + domínio do SOUL.md | retira para `_fora-do-escopo/`, preservando a `SKILL.md` e um README de reativação |

**Inventário de apoio antes de qualquer remoção.** A versão adaptada costuma ser a que tem
`type`/`timestamp`/proveniência, mas perde os scripts e references do upstream — fundir só o
corpo destrói a ferramenta. Listar os dois lados e levar o que falta é o que evita a regressão
silenciosa (a skill continua no catálogo, mas o comando dela parou de existir).

**A favor da fusão só quando os fluxos são realmente distintos.** Cluster temático ≠ duplicata.
Skills de um domínio com **fronteira declarada por escrito no corpo** ("isto aqui não
duplica a regra que pertence a tal skill") foram desenhadas para ficar separadas — fundi-las
apaga a fronteira que o dono construiu. Pack grande vindo de um repo público, com
`evals/evals.json` em todas as skills e sem escopo do dono no corpo, é lacuna de curadoria a
corrigir (precedência no catálogo), não motivo para dissolver.

**Heterogeneidade de proveniência é sinal, não ruído.** Categoria que guarda "versão adaptada"
de várias origens e carrega um arquivo de proveniência como marcador nasceu de curadoria, não
de domínio. Um `find` por todas as categorias lê isso na hora e evita tratar o resíduo como
se fosse um domínio legítimo.

## 6. Referências herdadas de outro repo não são todas o mesmo defeito

`related_skills` apontando para skill inexistente é comum em pacote importado, mas **o nome
morto indica o que fazer**: se existe skill local que cobre o mesmo terreno, repontar; se o
alvo era de outro repo e não tem equivalente aqui, remover a entrada. Remover tudo às cegas
perde a informação; repontar às cegas cria ciclo.

Só o campo `related_skills` conta como referência entre skills. Casar `` `termo` `` no corpo
gera centenas de falsos positivos (flag de shell, nome de campo, palavra em prosa) e leva a
reescrever arquivo que está bom.
