# Auditoria de rastreabilidade produto ↔ design ↔ código

Quando o usuário pergunta "se fizéssemos uma reunião entre PM, designer e
engenharia, eles concordariam que tudo segue uma direção única e está
corretamente encadeado?" (ou "as user stories e user flows estão
implementados?"), a resposta NÃO é opinião — é uma **auditoria de
rastreabilidade** com evidências reais do repo.

## Método (validado em CFP IA, ago/2026)

1. **Inventariar o código** (terminal, não suposição):
   - `find src api agente web -type f` — estrutura de pastas
   - Endpoints: `grep -rn "@router\.\(get\|post\|put\|patch\|delete\)" api/routers/*.py`
   - Funções do motor: `grep -n "def \|class " src/*.py`
   - Telas do frontend: `ls web/app/\(app\)/`
2. **Inventariar os requisitos**: IDs das user stories
   (`grep -oE "US-[0-9]{3}" product/management/user-stories.md | sort -u`) e
   flows (`grep -c "Fluxo [0-9]" product/design/user-flows.md`).
3. **Rodar os testes** — nunca auditar sem `pytest -q` verde (CFP IA: 92/92).
   Achar o venv do projeto: `.venv/bin/python -m pytest tests/ -q` (o python
   global pode não ter pytest).
4. **Detectar a descontinuidade frontend↔API** — o gap mais comum:
   ```bash
   # Tela usa mock ou API real?
   grep -q "mock-data\|userDemo" "web/app/(app)/$tela/page.tsx" && echo MOCK
   grep -q "fetch(\|axios\|lib/api" "web/app/(app)/$tela/page.tsx" && echo API-REAL
   ```
   Protótipo de alta fidelidade (F4a) legítimamente usa mock data — o contrato
   do pipeline diz que a integração é fase separada (F4d). NÃO tratar como bug:
   reportar como "descontinuidade conhecida do pipeline".
5. **Verificar features-chave no código real** (não no frontend):
   - Chat usa LLM real? `grep -n "llm\|model" agente/llm.py`
   - Regras de negócio (ex: notificação 1/dia)? `grep -n "COTA_TIPO_DIA\|1" api/services/*.py`
   - Tom de voz? `grep -n "julgad\|acolhedor" agente/prompts.py`
6. **Entregar como tabela de rastreabilidade**: por camada (Diretrizes →
   Motor → API → Núcleo/MCP → Telas → Testes), com evidência concreta
   (nomes de funções/endpoints/arquivos), ✅/⚠️ e a resposta direta à
   pergunta do usuário ("Sim, tudo implementado" vs "Back-end sim, frontend
   é maquete").

## Critério mock — aprendizado crítico (re-auditoria, CFP IA ago/2026)

A 1ª auditoria marcou tudo "PARCIAL" porque o protótipo usava mock em vez de API — **isso
estava errado para a fase**: em demonstração (F4a), mock é ESPERADO e desejável. Na
re-auditoria (mesma sessão Pi, `pi --session <jsonl>`), o critério correto passou a
classificar: **DEMONSTRADO** (demo reproduz com mock) / **DEMONSTRÁVEL PARCIAL** /
**NÃO DEMONSTRÁVEL** (não dá para reproduzir nem com mock). Gaps reais viram: botões sem
`onClick`, painéis que não abrem, conformidade ausente (FPSB), telas inexistentes — não a
ausência de backend.

**Sempre re-auditar com o critério da fase ANTES de gerar code-tasks de demo** — senão o
backlog vira "conectar backend" em vez de "fechar demonstração". O usuário pediu isso
explicitamente: "o protótipo deve demonstrar os fluxos com dados mockados mesmo".

## Auditoria via Pi Cost (prompt auto-contido)

Para auditorias profundas (matriz US×critérios Gherkin, fluxo a fluxo, gaps com
arquivo:linha, backend pronto para conectar), delegar ao Pi Cost com prompt auto-contido
que instrui: ler em ordem (user-flows → user-stories → design-system → page.tsx →
mock-data → componentes); regra "componente existe ≠ fluxo implementado"; entregar em
`product/engineering/auditoria-rastreabilidade.md` com 6 seções (matrizes US/fluxos,
gaps priorizados por severidade, componentes órfãos, notas mock, backend pronto com
dificuldade por endpoint) + `<!-- PHASE_COMPLETE -->`. Sessão v1+v2 custou ~$0.03
(2.46M tokens, 94% cache hit). Monitorar com pi-session-audit (Progress Classification),
não só `process wait`; continuar a MESMA sessão via `pi --session /path/exato.jsonl`
(append, custo acumula), nunca `--name`.

## Pitfalls

- **Não confiar em `git log` parado**: repo local pode estar no commit F3
  enquanto os docs/código avançaram — rodar `git status` + `git log` primeiro.
- **Frontend mockado ≠ bug**: o pipeline separa F4a (protótipo mock, aprovação
  visual) de F4d (integração). A auditoria deve dizer isso explicitamente —
  o PM/designer/engenheiro "concordam" porque cada um sabe onde está o gap.
- **Testes verdes não provam integração**: 92/92 testes passam no back-end;
  a auditoria também precisa do grep de fetch/mock no frontend.
- **Verificar o que o usuário perguntou exatamente**: "implementado" pode
  significar (a) existe código para isso, (b) está conectado de ponta a ponta.
  Responder ambos explicitamente.
