# Contratos no Drive — Referência de Minuta

## Pasta base

**"1.1.2. Modelos de Contrato"** — folder ID: `11rwdi67Wkx47zM_oqJ9JSKNzstE5CEzS`
- Link: https://drive.google.com/drive/folders/11rwdi67Wkx47zM_oqJ9JSKNzstE5CEzS

## Subpasta de destino das minutas

**"Minutas"** — folder ID: `1f5-0dTKMWZG3z1sHs1Kd2OcUh9GHG5rF`
- Toda minuta criada pela skill vai AQUI (nunca na raiz).

## Contratos-modelo (documentos Google Docs)

| Nome | Doc ID | Uso |
|---|---|---|
| Modelo de Contrato de Consultoria de Escopo Fixo | `1kR2EfV5gpkWfLx5vCogrO8u7nsYqxnfhRVJeFLF5UmA` | **Padrão** para projetos com escopo definido (mais completo: 16 cláusulas) |
| Modelo de Contrato de Consultoria Ágil | `1S45AzsvjRdI1OFUtb8b-2vpkQ9SL6zYqZuFV-1dwDic` | Para retainer/trabalho contínuo (backlog mensal) |
| Diagnóstico de IA - Contrato Sergipetec | `1UujF6qM0Hj7aK7nQraCTQ1447bE22-AvBvpFx42LLQY` | Exemplo real de diagnóstico |
| Implantação de Sistema de Business Intelligence - Contrato Ravello | `13sp6nL7p_mBl2XlgqLqY4yERw3HMkyYE_EYrtJBpLyA` | Exemplo real de implantação |
| Landing Pages - Contrato Emerge | `1LrFWTBEvLCx0JE1rOBCJLFZf23_8MZ2CppdbWnhv0MQ` | Exemplo real de projeto digital |

## Estrutura do modelo de Escopo Fixo (referência de edição)

1. **Capa** (primeira página — NÃO EDITAR)
2. Qualificação das partes: CONTRATANTE (cliente: razão social, CNPJ, endereço, representante) e CONTRATADA (iD.teal Consultoria em Gestao Organizacional LTDA, CNPJ 54.569.818/0001-59, representada pelo sócio-administrador)
3. CONSIDERANDO QUE (motivações)
4. Cláusula 1 — OBJETO
5. Cláusula 2 — ESCOPO DO PROJETO (entregáveis + 2.2 "não estão incluídos")
6. Cláusula 3 — REVISÕES INCLUÍDAS (até 2 por entregável)
7. Cláusula 4 — REVISÕES ADICIONAIS (valor/hora)
8. Cláusula 5 — SERVIÇOS ADICIONAIS (aditivo)
9. Cláusula 6 — CRITÉRIOS DE ACEITE (ata + aprovação formal)
10. Cláusula 7 — PRAZO E VIGÊNCIA (90 dias padrão + multas por atraso)
11. Cláusula 8 — REMUNERAÇÃO (valor total + parcelas: entrada na assinatura, demais em marcos)
12. Cláusula 9 — RESCISÃO (aviso 8 dias, pagamentos proporcionais)
13. Cláusula 10 — OBRIGAÇÕES E RESPONSABILIDADES
14. Cláusula 11 — CONFIDENCIALIDADE (5 anos)
15. Cláusula 12 — PROPRIEDADE INTELECTUAL (bens da CONTRATANTE)
16. Cláusula 13 — FORÇA MAIOR
17. Cláusula 14 — RESOLUÇÃO DE CONFLITOS (Comarca de Aracaju)
18. Cláusula 15 — INDEPENDÊNCIA DAS PARTES
19. Cláusula 16 — DISPOSIÇÕES GERAIS
20. ASSINATURAS + **contracapa** (última página — NÃO EDITAR)

## Como criar a minuta

1. **Copiar** o modelo base para a subpasta Minutas:
   - Drive API `files.copy` com `parents: [1f5-0dTKMWZG3z1sHs1Kd2OcUh9GHG5rF]`
   - Nome: `Minuta <Tipo> - <Cliente>` (ex: "Minuta Diagnóstico de IA - Cliente X")
2. **Editar o corpo** via Docs API batchUpdate (preservar capa e contracapa — primeira e última páginas):
   - Qualificação do cliente (CONTRATANTE)
   - Cláusula 2: escopo/entregáveis do projeto
   - Cláusula 8: valor total e parcelas (espelhar a proposta EXATAMENTE)
   - Cláusula 7: prazo/vigência
   - Outras cláusulas conforme necessidade
3. Confirmar com o usuário antes de modificar.
4. Entregar o link (`https://docs.google.com/document/d/<ID>/edit`).

## Acesso

Via `gws`/`google_api.py` (skill google-workspace):
```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI drive get <FILE_ID>
$GAPI docs get <DOC_ID>
```
