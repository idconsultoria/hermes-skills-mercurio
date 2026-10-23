# Importar skills de um diretório externo (skills.sh) para o acervo da ID

Caso concreto do skills.sh (diretório aberto da Vercel), mas o método vale para qualquer diretório
que exponha busca + repo GitHub por trás.

## 1. Descobrir — API, não página

As páginas do skills.sh são Next.js pesadas e podem passar pelo Firecrawl, que às vezes está
fora. A busca tem endpoint JSON:

```python
import json, urllib.request, urllib.parse
q = "financial modeling"
url = "https://www.skills.sh/api/search?q=" + urllib.parse.quote(q)
req = urllib.request.Request(url, headers={"User-Agent": "curl"})
for s in json.load(urllib.request.urlopen(req, timeout=25))["skills"]:
    print(s["installs"], s["id"])   # só id, source, skillId, name, installs
```

- Rodar 10–20 queries de **domínio** (termo de negócio, não de tecnologia) e deduplicar por `id` em
  Python; `installs` alto não indica relevância.
- A resposta **não traz descrição**: julgar pelo nome é erro. Confirmar lendo o `SKILL.md` (passo 3).

## 2. Listar skills de um repo (CLI, só descoberta)

```bash
DISABLE_TELEMETRY=1 npx -y skills@latest add <owner>/<repo> -l   # lista com descrição
DISABLE_TELEMETRY=1 npx -y skills@latest --help                  # add / use / list / find / update
```

`add` instala em diretórios de agentes (`.claude/skills`, `.cursor/skills`, …) **relativos ao CWD**
— nunca rodar dentro do acervo: não escreve no layout `<categoria>/<skill>/SKILL.md` e espalha
dezenas de pastas de agente. Para instalar de verdade, baixar via GitHub (passo 3).

## 3. Baixar a pasta inteira da skill

`id` = `<owner>/<repo>/<skill>`; o repo é GitHub. Levar `references/`, `scripts/` e `assets/`
junto (é onde mora metade do valor) e pular `evals/`.

```python
# 1) /repos/<owner>/<repo>/git/trees/HEAD?recursive=1  (precisa de GITHUB_TOKEN)
# 2) filtrar paths.startswith('<base>/'), com <base> = caminho da skill dentro do repo
# 3) baixar cada blob: https://raw.githubusercontent.com/<owner>/<repo>/HEAD/<path> (público)
# 4) gravar em <SKILLS_DIR>/<categoria>/<skill>/<path relativo a base>
```

## 4. Normalizar só o frontmatter

O conteúdo upstream não segue as regras do acervo. Ajustar apenas o frontmatter, preservando o
corpo (skill de terceiro é conteúdo, não doutrina):

- `type:` da taxonomia OKF de 8 tipos e `timestamp:` ISO 8601 — sem isso a auditoria do ciclo
  `update` acusa a skill e ela fica fora do catálogo;
- `source: skills.sh/<owner>/<repo>#<base>` — proveniência para rebaixar/atualizar depois;
- **`description: >` / `|` / `>-` vira string quoted com quebra de linha real** — block scalar
  quebra o parser do `generate_graph.py`;
- não traduzir nem reescrever o corpo na importação.

## 5. Registrar e commitar

1. `<categoria>/index.md` — bloco novo, uma linha por skill (sumário curto em PT-BR).
2. `log.md` — `## [YYYY-MM-DD] update | ...` com fonte, `type` atribuído e o critério de curadoria
   (o que entrou e o que foi descartado e por quê).
3. `git add` **só** dos paths novos + `index.md` + `log.md`; `git add -A` contamina o commit com o
   WIP de outras sessões (SKILL.md modificadas, skills untracked).
4. `skill_view(name='<skill-nova>')` para confirmar que o Hermes descobre a skill no layout novo.

## 6. Critério de curadoria

- Entra: cobre o domínio pedido, corpo com procedimento real (passos, fórmulas, tabelas de decisão),
  sem depender de conector proprietário que a ID não tem.
- Fica fora: a variante SaaS/B2C de um framework quando o alvo é outra coisa (ex: métricas de
  assinatura para empresa de serviço intensivo em mão de obra); skill que é só persona/prompt;
  `scripts/` que exigem SDK ou API paga.
- Conflito com decisão da ID: a decisão da ID vence e o conflito é registrado no `log.md`.
