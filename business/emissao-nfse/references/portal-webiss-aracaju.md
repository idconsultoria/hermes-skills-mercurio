# Emissão manual de NFS-e no portal WebISS (Aracaju) — operação

Profundidade sob demanda da skill `emissao-nfse` (seção "Canal manual"). Usar quando a demanda
for "emita a nota no portal" e o motor local não estiver disponível.

## 1 · Portal e formulário

- URL: `https://aracajuse.webiss.com.br` — `/inicio` resolve para `/autenticacao/entrar`.
  Página de autenticação em HTML simples: não exige app nem certificado.
- Campos: `#Login` (CPF/CNPJ ou usuário), `#Senha`, `#botao-logar`; há também a via
  "Acessar com Certificado Digital" (não usar enquanto o A1 estiver pendente).
- Menu lateral, depois do login: **NFS-e → Criar** (emissão) e **Consultar/Imprimir NFS-e**
  (histórico — é onde se lê a última nota do tomador e se conferem as já emitidas).
- Aviso do próprio portal: a obrigatoriedade de IBS/CBS na NFS-e está suspensa/teste — **não é
  preciso preencher IBS/CBS** para emitir hoje.

## 2 · Credencial — a parte que não se improvisa

| Passo | Como |
|---|---|
| Identificador | `fill_input('#Login', '<CPF/usuário>')` — identificador não é segredo |
| Senha | `browser_vault_fill` com o handle do cofre, **nunca** `fill_input` |
| Item ausente | `browser_vault_save_login` só funciona em sessão com UI; no Telegram/API/cron volta `prompt_unavailable` |
| Saída | pedir ao principal `hermes vault add --kind login` (origem exata `https://aracajuse.webiss.com.br`, identificador = CPF) ou Desktop → Settings → Passwords & Logins |

- A origem do item do cofre é **verificada no momento do preenchimento**: salvar em
  `webiss.com.br` não serve para `aracajuse.webiss.com.br`.
- Uma vez salvo, as notas seguintes da mesma sessão saem sem nova intervenção do principal.
- Senha recebida em chat é registro exposto: conclua as notas e **recomende a troca no portal**
  (uma linha, sem drama). Não repita a senha, não a use em comando.
- **Cofre da casa errada:** o principal pode salvar o item em outro `HERMES_HOME` (ex.: o Hermes
  default em `~/.hermes/vault` em vez de `$HERMES_HOME/vault`). Sintoma: `browser_vault_list`
  segue vazio. Correção: copiar `vault.json.enc` **e** `vault.key` do cofre de origem para
  `$HERMES_HOME/vault/` (o par é o que permite decifrar; só o `.enc` não serve), `chmod 600` e
  conferir com `browser_vault_list` — o item aparece com origem e identificador.

## 3 · De onde vêm os dados de cada nota (ordem de confiança)

1. **Planilha `[ID] Gestão de Symplexis`** — aba `recebimentos`: `iD`, `iD.contrato`,
   `Discriminação`, `Valor`, `Status`, `Data prevista`. Define **parcela (n/total)**, valor e
   vencimento. Aba `contratos`: valor total, data de assinatura, oferta do catálogo.
   Use `scripts/parcelas_symplexis.py <iD do cliente>`.
2. **Objeto do contrato** — para discriminação e código de serviço em contrato novo: exportar o
   Google Doc do contrato em texto (`files().export(fileId=..., mimeType='text/plain')`) e ler a
   cláusula **OBJETO (2.1)** e a de remuneração (6.x). É a redação que descreve o serviço.
3. **Última NFS-e do tomador no próprio portal** — tomador, código de serviço e endereço vêm
   preenchidos; confira antes de aceitar (o cadastro é atalho, o escopo pode ter mudado).
4. KB do cliente (`kb_search`) para o nome que vai no assunto/discriminação e para saber se há
   contrato anterior no mesmo tomador com numeração de parcelas já em curso.

O número da NFS-e da prefeitura é **sequencial anual** — jamais deduza a parcela dele.

## 4 · Gate do rascunho (não negociável)

Emitir NFS-e é ato fiscal irreversível. O ciclo por nota:

1. preencher tomador, serviço, valor, competência (mês da prestação) até a tela final;
2. **parar no rascunho** — nada de confirmar;
3. **screenshot** do rascunho e conferência por leitura de imagem (tomador, CNPJ, valor,
   discriminação, competência) antes de enviar ao principal;
4. enviar o print e **esperar o ok**; sem resposta, não emite;
5. só então confirmar e seguir para a nota seguinte.

Uma nota por vez, na ordem pedida. Declarar "emitida" sem o protocolo/número da nota é dito sem
lastro: depois de confirmar, ler a nota emitida no portal e reportar número e valor reais.

## 5 · Onde NÃO procurar

As NFS-e emitidas **não ficam arquivadas no Drive da ID** (o Drive guarda contrato, proposta e
entregável; busca por `name contains 'NFS'` devolve no máximo notas antigas de 2024). O histórico
vive no portal (Consultar/Imprimir) e nos e-mails de cobrança por cliente
(`references/cobranca-nfse-clientes.md`).

## 6 · Assistente de criação — passo a passo e seletores

`/issqn/nfse/criar` é um assistente de 4 passos (Tomador → Serviços → Valores → rascunho).
Avanço pelo botão `#btnProximo`; "Anterior" volta um passo. Seletores que importam:

| O quê | Seletor |
|---|---|
| Carregar última NFS-e emitida | `#botao-carregar-dados-ultima-nota-fiscal` |
| Carregar por número | `#numero-nota-fiscal-anterior` + `#botao-carregar-dados-nota-fiscal-anterior` |
| Carregar por documento do tomador | `#documento` + `#btn-carregar-nota-nome-tomador` |
| Tomador | `#tomador-numero-documento`, `#tomador-inscricao`, `#tomador-razao-social`, `#tomador-email`, `#cepDoEndereco`, `#nomeLogradouroDoEndereco`, `#numeroDoEndereco`, `#complementoDoEndereco` |
| Serviço | `#lista-de-servicos-prestador` (AtividadeNoMunicipio), `#CnaeAtividade_Id` |
| Discriminação | `#discriminacao` (textarea, 10–2000 caracteres, 20 linhas) |
| Valores | `#valores-servico`, `#valores-documento-fiscal-aliquota` (o campo que vale é este) |
| Salvar rascunho | botão com texto `Salvar rascunho` (classe `salvar-rascunho`) |

- **Carregar por documento do tomador falha quando aquele tomador já tem rascunho aberto**
  (a tela volta para `/criar/para/null` com "Tomador não encontrado"). Use **"Última NFS-e
  emitida"** — que traz o mesmo tomador com endereço, IM e serviço preenchidos.
- Selects são controlados por JS: mude com `select.value = '<value>'` **e**
  `dispatchEvent(new Event('change', {bubbles:true}))`, depois confirme lendo
  `options[selectedIndex].text`; a página às vezes re-renderiza o bloco do tomador depois do
  change — recheque antes de avançar.
- Textarea/serviço/valores: setar `value` + `input`/`change` e conferir o valor lido de volta
  (acentos passam íntegros).

### Rascunhos: editar, conferir, imprimir

- Listagem: `/issqn/nfse/notas-fiscais` — filtre situação **Em edição** em
  `#servicos-exigibilidade-iss` com `value='EmEdicao'` (**não** pelo índice da opção) e clique
  `#buscar-por-filtro`. Sem filtro de situação a lista mostra só as notas `Normal`.
- Filtro por tomador: `input[name=DocumentoTomador]` (aceita `00.000.000/0000-00`).
- Rascunho: `/issqn/nfse/editar/<id>` (revisão, com "Anterior"/"Próximo") e
  `/issqn/nfse/emitir/<id>` (tela do documento com o selo **RASCUNHO** e o botão "Emitir").
- Para corrigir um rascunho salvo: abrir `/issqn/nfse/editar/<id>` → **Anterior** (volta ao passo
  de valores) → ajustar `#valores-servico` / `#valores-documento-fiscal-aliquota` → **Salvar
  rascunho** → reconferir na listagem.
- O `<id>` do rascunho é interno (`/emitir/<id>`), **não** é o número da NFS-e — número só existe
  depois de emitir. Não cite o id como "número da nota".

## 7 · Alíquota do mês — sempre conferir antes de salvar

O campo `#valores-documento-fiscal-aliquota` abre com **5,00%** (ou herda o valor da nota
anterior) e é ele que define o ISS do rascunho. A alíquota correta do Simples do mês está em
`$HERMES_HOME/id-nfse-motor/dados/aliquota_iss.json` (`aliquota_iss` + `competencia`), alimentada
pelo cron do dia 5 a partir do e-mail "ALÍQUOTA DE ISS MM.AAAA".

- Ajustar **antes** de salvar o rascunho: `#valores-servico` e
  `#valores-documento-fiscal-aliquota` (formato `1.000,00` e `2,01`).
- Conferir em **dois lugares**: no espelho do rascunho (`Alíquota ISS (%): 2,0100`) e na
  listagem de rascunhos, coluna `Alíq.(%)` e `ISSQN(R$)` (o espelho mascara o valor do ISS com
  `*****`; a listagem é a fonte do número).
- Ordem de grandeza para sanidade: 2,01% sobre R$ 2.500,00 = R$ 50,25. Alíquota 5,00% é sempre
  sinal de campo não ajustado.

## 8 · Serviço e CNAE por tipo de objeto

O portal só oferece as atividades e CNAEs do cadastro da ID; escolha pelo **objeto do contrato**,
não pelo que veio carregado:

| Objeto | Atividade | CNAE |
|---|---|---|
| Mapeamento/consultoria de processos, assessoria em gestão | `1701` — Assessoria ou consultoria de qualquer natureza | `7020400` — consultoria em gestão empresarial |
| Desenvolvimento de sistema / software (credenciais, produto digital) | `0101` — Análise e desenvolvimento de sistemas | `6204000` — consultoria em TI |
| Treinamento / capacitação in company | `0802` — Instrução, treinamento, orientação pedagógica e educacional | `8599604` — treinamento em desenvolvimento profissional e gerencial |

`options` do select de atividade usam índices internos (0101 → `1`, 0802 → `72`, 1701 → `143`) e
o de CNAE outro conjunto (6204000 → `988`, 7020400 → `1301`, 8599604 → `1182`); resolva sempre
lendo as `options`, não memorizando o number. Código de serviço é decisão fiscal de escopo:
presente a escolha ao principal junto do print e ofereça trocar antes de emitir.

## 9 · Mecânica do navegador (evita retrabalho)

- **Abas/`js()` podem divergir da aba certa**: antes de cada leitura/preenchimento, chame
  `ensure_real_tab()`; se aparecerem `about:blank` acumuladas, feche-as por CDP
  (`Target.getTargets` + `Target.closeTarget`) e siga com a aba do portal. Sem isso, um `js()`
  pode ler outra aba e devolver campo vazio ou `null`.
- **Sessão do portal expira (~30 min de contador visível)**: se `/inicio` voltar para
  `/autenticacao/entrar` no meio do trabalho, refaça o login (`#Login` + cofre) e siga — o
  rascunho salvo **permanece** no sistema e se recupera pela listagem "Em edição".
- **Print do rascunho**: `Emulation.setDeviceMetricsOverride(width=1280, height≈2600)` +
  `Page.captureScreenshot(captureBeyondViewport=True)`, salvar em
  `$HERMES_HOME/work/nfse-<ano>/rascunho_<contrato>_<parcela>.png` e limpar o override depois.
- **Conferir o print antes de enviar** com leitura de imagem (selo RASCUNHO, tomador, valor,
  alíquota, competência, sem corte) — é o artefato que o principal aprova.
