# Status Audit Quinzenal (pós-reunião com parceiro)

**Quando usar:** usuário pede "verifique em que ponto estamos" em projeto de pipeline com ciclo quinzenal (ex: CFP IA) após reuniões com sócio/parceiro (ex: Igor, CFP certificado). Produz relatório de status + plano de ação com donos.

## 1. Triangulação de fontes (rodar em paralelo)

- **Repo local:** `git log --oneline -20`, `git status -sb`, `git remote -v`, estrutura via `find . -type f -not -path './.git/*' | sort`
- **Sincronia GitHub:** `git log origin/main --oneline -5` vs local — repo local pode estar atrás do remoto (ou à frente).
- **Sessões passadas:** `session_search(query="<projeto>", sort="newest")` — confirma o último trabalho feito via Hermes. Se não houver sessões recentes, isso É um dado: o avanço aconteceu fora do Hermes (reuniões, Drive, WhatsApp).
- **Google Docs (transcrição de reunião + docs de parceiro):** ver extração abaixo.
- **Cross-reference:** estado do repo vs. decisões da reunião vs. docs do parceiro → lista de lacunas. Repo pode estar semanas/meses atrás das conversas — esse descompasso é o gap central, não um bug.

## 2. Extração de Google Docs (`docs get` retorna JSON)

```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI docs get <DOC_ID> > /opt/data/<projeto>/doc.json
# retorna {"title": ..., "documentId": ..., "body": "..."}
python3 - <<'EOF'
import json
d = json.load(open("doc.json"))
open("doc_body.txt", "w").write(d["body"])
print(d["title"], len(d["body"]))
EOF
```

- **Body grande (>15KB) aparece truncado** no read_file mesmo com `truncated: false` no JSON wrapper — extrair para arquivo separado e ler em blocos (offset/limit).
- Transcrições Fathom vêm com timestamps por falante (`0:00 - Nome`): ler a transcrição INTEIRA antes de listar decisões — decisões-chave costumam estar espalhadas, não só no início/fim.
- Docs do parceiro podem ter título descritivo (`Diretrizes_App_Planejador_Financeiro_v3`) que difere do nome da pasta — usar o título real no relatório.

## 3. Estrutura do relatório de status

Arquivo `.md` salvo NO REPO do projeto + entregue via MEDIA:

- **Onde o projeto está** — tabela por fase/quinzena com status (✅ / ⚠️ / ⏳)
- **Estado do repo** — último commit, o que falta, sincronia GitHub
- **Decisões-chave da reunião** — tabela: tema → decisão (inclusive o que CONTRADIZ o PRD atual)
- **Docs do parceiro** — resumo estruturado (motor de cálculo, perfis, trilhas, regras)
- **Lacunas** — tabela: #, lacuna, ação sugerida
- **Próximos passos**

## 4. Plano de ação pós-reunião (deliverable)

Formato comprovado (`plano-acao-pos-reuniao.md` no CFP IA):

- **Seções por bloco:** A) Fechar ciclo vencido, B) Kickoff próxima fase, C) Ações do parceiro, D) Ações do usuário, E) Conjuntas, F) Updates no repo, G) Ordem de execução
- **Cada item:** `# | tarefa | responsável | tipo | depende de`
- **Seção G:** sequência crítica com dependências explícitas + bloqueadores nomeados (ex: "fluxo de missões travado na entrega X")
- **Item explícito de revisão:** quando o usuário diz "adicione uma revisão minha no doc do parceiro", inserir como item D (ações do usuário) de prioridade máxima ANTES de derivar a sequência.
- Separar "já especificado, pode começar hoje" (ex: motor de cálculo com spec completa) de "travado aguardando terceiro".

## 5. Pitfalls

- **Deliverables .md vão dentro do repo do projeto, NUNCA em /tmp** — `HERMES_WRITE_SAFE_ROOT=/opt/data` bloqueia escrita fora (`Write denied`). Salvar o relatório em `/<projeto>/` e commitar depois.
- **Rodar `$GSETUP --check` antes de `docs get`** — token expira (~7 dias) e `docs get` falha silenciosamente se auth caiu.
- **Distinguir "decidido na reunião" de "implementado no repo"** — decisões de reunião não commitadas são o gap; listá-las explicitamente como lacunas com dono.
