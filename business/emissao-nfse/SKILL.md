---
name: emissao-nfse
description: "Emitir NFS-e/NF-e da ID via motor nfelib e encaminhá-la ao cliente (cobrança)."
category: business
type: ToolIntegration
timestamp: 2026-09-27T02:00:00Z
---

# Emissão de NFS-e / NF-e (ID Consultoria)

Emissão de **nota fiscal eletrônica de serviço (NFS-e)** da ID, via motor open source
(`nfelib`+`xsdata`) no padrão **NFS-e Nacional**. Contém o enquadramento fiscal da ID, a
decisão de arquitetura (Aracaju = protocolo NACIONAL, não conector municipal), o uso da CLI
do motor e a lista de pendências fiscais reais.

## Quando usar
- Emitir NFS-e da ID para um cliente (serviço/treinamento/consultoria).
- Integrar emissão no próprio produto/automação da ID.
- Retomar/validar o motor (build da imagem, assinatura, homologação).

## Enquadramento fiscal da ID (confirmado na base)
- **ID.TEAL CONSULTORIA EM GESTÃO ORGANIZACIONAL LTDA** · CNPJ 54.569.818/0001-59
- LTDA **Microempresa** (LC 123/2006) → **Simples Nacional** (`opSimpNac=2`)
- Atividade principal 85.99-6-04 (treinamento/consultoria) → **serviço (ISS, NFS-e)**.
  NF-e (ICMS/estadual) só se vender mercadoria física.
- Município de prestação dominante: **Aracaju/SE (IBGE 2800308)** — presta serviço em
  múltiplos municípios; emitir no município do serviço.

## Decisão de arquitetura (a mais importante)
- **Aracaju (2800308) está no Ambiente NFS-e NACIONAL** (confirmado: "Amb. Nacional = Sim",
  Emissor Nacional UI = Não). O "Webiss" é só a interface municipal por cima do padrão
  nacional.
- → **Motor usa o padrão NFS-e Nacional (DPS via `nfelib`)**, NÃO conector municipal
  (Betha/Ginfes/DSF/etc.). Escala para outros municípios aderentes e já segue a reforma
  tributária (IBS/CBS, CNPJ alfanumérico). Conector municipal = reserva, nunca default.

## Motor
- **Local:** `/data/data/com.termux/files/home/capitolium/id-nfse-motor/`
  - `emitir_nfse.py` — CLI que monta a DPS (nfelib) e serializa XML (xsdata), round-trip valida.
  - `requirements.txt` — stack pinada (nfelib 2.5.2, pynfse-nacional 0.9.5, erpbrasil.*,
    xsdata, signxml, zeep, lxml).
  - `Dockerfile` — multi-stage otimizado, ARM64, runtime `python:3.13-slim`, não-root, HEALTHCHECK.
  - `DEPLOY.md` — build/uso/pendências.
- **Uso:**
  ```
  ./emitir_nfse.py emit --tom-nome "X Ltda" --tom-cnpj 01234567000189 \
    --tom-cep 49020090 --tom-logradouro "Av. Rio Branco" --tom-nro 250 --tom-bairro Centro \
    --servico "Consultoria em gestão e aumentação de processos" \
    --valor 4850.00 --serie 00001 --ndps 1            # default tpAmb=2 (homologação)
  ```
- Build da imagem: o daemon Docker **não é acessível do container do Mercúrio** — o Hermes
  canônico builda no Oracle host (`docker build -t id-nfse-motor:1.0.0 .`, ver DEPLOY.md).

## Canal manual — portal WebISS de Aracaju (emissão quando o motor está bloqueado)

Emissão de NFS-e da ID **não depende só do motor**: o WebISS entra por **usuário/senha**, não por
certificado. Enquanto o A1 não está em mãos, o canal operativo é o portal — mesmo gate, mesmo rigor.
Detalhe operacional em `references/portal-webiss-aracaju.md`.

1. **Portal:** `https://aracajuse.webiss.com.br` (o `/inicio` cai em `/autenticacao/entrar`).
   Formulário: `#Login` (CPF/CNPJ ou usuário), `#Senha`, botão `#botao-logar`.
2. **Identificador pode ser digitado; senha, nunca.** O CPF/usuário entra por
   `fill_input('#Login', ...)`; a senha só pelo cofre (`browser_vault_fill`). Sem item salvo para a
   origem, `browser_vault_save_login` **não consegue pedir em sessão não interativa**
   (Telegram/API/cron devolvem `prompt_unavailable`): peça ao principal, uma vez,
   `hermes vault add --kind login` (origem = origem exata do portal, identificador = CPF) ou
   Desktop → Settings → Passwords & Logins. Depois disso a sessão segue sem nova digitação.
3. **Emissão:** menu lateral **NFS-e → Criar**; havendo nota anterior do tomador, **carregar a
   última NFS-e** (traz tomador, código de serviço e discriminação prontos) e corrigir o que mudou
   de objeto/valor.
4. **Parcela e valor saem da planilha, nunca da memória:** `[ID] Gestão de Symplexis` → aba
   `recebimentos` (`iD.contrato`, `Discriminação`, `Valor`, `Status`, `Data prevista`) + aba
   `contratos` (valor total, datas, oferta). Rodar `scripts/parcelas_symplexis.py <iD>` antes de
   tocar no portal. O número da NFS-e é sequencial anual e **não** diz qual é a parcela.
5. **Gate do rascunho:** conduzir cada nota até o rascunho final e **parar**. Print do rascunho →
   ok do principal → só então emitir. **Uma nota por vez**, na ordem pedida, com os dados da nota
   já conferidos antes de mandar o print.

## Fluxo de emissão (gate obrigatório)
1. Coletar tomador, serviço, valor, competência, série/nDPS.
2. Validar contra perfil fiscal ID (serviço/ISS) e, se aplicável, KB do cliente.
3. **Gate:** apresentar resumo e exigir ok explícito antes de homologação/produção.
   Homologação (`tpAmb=2`) por padrão.
4. Gerar DPS → (Fase 2, com A1) assinar via `erpbrasil.assinatura` + transmitir via
   `pynfse-nacional` → arquivar XML autorizado + protocolo.

## Envio da NFS-e ao cliente (cobrança) — depois de emitida

O ciclo da nota não termina na emissão: a nota é **encaminhada ao setor de compras do
cliente com o pedido de pagamento**, replicando o molde dos envios anteriores.

1. **Ler a NFS-e com `pdftotext -layout <pdf> -`** (extração sem `-layout` embaralha o
   bloco de valores: valor dos serviços, ISS, líquido e total saem fora de ordem).
2. **Buscar os envios anteriores ao mesmo cliente** (Gmail `admin@idconsultoria.ai`) e
   copiar assunto, destinatários e o bloco de dados da nota. Queries e padrão por cliente
   em `references/cobranca-nfse-clientes.md`.
3. **Parcela vem do histórico de e-mails/contrato, nunca do número da NFS-e** (a numeração
   da prefeitura é sequencial anual; o envio anterior traz o ordinal e o total, ex. `(2/3)`).
4. Renomear o anexo no padrão da parcela (`NFS-e_<n>-<total>_<Contrato>.pdf`) e enviar de
   `admin@idconsultoria.ai`, como thread novo, corpo em texto puro.
5. **Enviar com anexo via MIME no Python** — o `gapi gmail send` do CLI não tem flag de
   anexo. Script com `--dry-run` (imprime conta, destinatários, assunto, tamanho do anexo),
   guardado em `$HERMES_HOME/work/nfse-<ano>/` para reuso na parcela seguinte.

> **Gate:** e-mail a cliente externo só sai com **aprovação explícita do principal sobre o
> texto final**. Apresente o rascunho completo (assunto + destinatários + corpo + anexo) e
> espere o ok. Sem resposta (inclusive prompt de aprovação que expira) = **não enviar**.

### Cobrança de parcela vencida

Depois que a nota foi aceita e o prazo passou, a demanda muda de natureza: não é reenvio de
NFS-e, é cobrança. Os passos, a trava do extrato, o molde do texto e o agendamento com cron
estão em `references/cobranca-nfse-clientes.md` (seção 5). Regra que não se negocia: **só
cobra depois de confirmar, no extrato, que o valor não entrou** — e se a consulta ao banco
falhar, reporta ao principal em vez de concluir que o cliente não pagou. **Cliente que
respondeu com prazo sai da cadência automática** (§5.6): nada até o prazo, verificação muda no
dia do prazo e escalada ao dono no primeiro dia útil seguinte.

## Emissão manual no WebISS de Aracaju (quando não há A1 válido)

Rota operacional enquanto o certificado A1 não é renovado: emitir pelo portal
**https://aracajuse.webiss.com.br** (login CPF/CNPJ + senha).

1. **Login pela vault**, nunca digitando a senha: `fill_input('#Login', <CPF>)` + `browser_vault_fill`
   (o item precisa estar no `HERMES_HOME` do perfil certo — vault do Olimpo não vale para o Mercúrio;
   copiar `vault.json.enc` + `vault.key` resolve). A sessão cai em ~30 min → refazer o login.
2. **Criar** (`/issqn/nfse/criar`) → bloco "Carregar dados de uma nota anterior":
   *Última NFS-e emitida* (traz tomador, serviço, descrição e valores da nota anterior) ou
   *Por documento do tomador*. Preencha e clique Carregar; depois `#btnProximo` → Passo 2 → Passo 3.
   Carregar por documento falha se o tomador tem rascunho aberto (`criar/para/null`) — use a última nota.
3. **Passo 3 — a armadilha**: `#valores-documento-fiscal-aliquota` ("Alíquota % (Simples Nacional)")
   volta **5,00** em boa parte das vezes. Corrigir para a alíquota do mês antes de salvar
   (`id-nfse-motor/dados/aliquota_iss.json`, cron do dia 5) — conferir o resultado em
   Consultar › situação *Em edição* (Alíq. e ISSQN).
4. **Salvar rascunho** (`salvar-rascunho`) → confere em *Em edição* → `#botao-emitir-nota-fiscal`
   emite e devolve a **Chave de Acesso** (o número sequencial sai na Consultar).
5. **PDF para o cliente**: o botão Imprimir do portal é `window.print()`. Gerar o PDF com
   `Page.printToPDF` injetando CSS `body * {visibility:hidden} #nota-eletronica-html, … * {visibility:visible}`
   + `scale=0.92`, A4 → **1 página**, igual aos envios anteriores (a página inteira gera 2 páginas).
6. **Enquadramento** (ficha cadastral da ID): CNAEs 8599604 (principal), 5819100, 6204000, 7020400.
   Item de serviço: 1701 (consultoria/mapeamento), 0101 (análise e desenvolvimento de sistemas),
   0802 (instrução/treinamento). Todo par item+CNAE novo deve existir na ficha; o precedente de
   cada contrato manda (Sergipetec/Artemishub = 0802 + 6204000).

### Pitfalls do portal
- O browser daemon abre abas internas `about:blank`; `js()` pode avaliar na aba errada. Chamar
  `ensure_real_tab()` no início de **cada** `browser_exec` (e fechar as `about:blank` via
  `Target.closeTarget`) antes de ler/escrever.
- Clique só via `js(...).click()`; `click_at_xy`/mouse CDP não chegam à página.
- A nota emitida avisa que o tomador **recebe automaticamente** o link — o e-mail de cobrança
  da ID é adicional, não substitui nem é substituído por isso.

## Pendências reais (bloqueiam a 1ª nota em produção)
1. **Certificado A1 (e-CNPJ)**: NÃO está em email/Drive da ID — está num PC pessoal do
   principal. Guardar a **senha** em env/volume seguro, **nunca em chat/texto plano**.
2. **Inscrição Municipal (IM)** do ISS de Aracaju — não está na base.
3. **cNBS / cTribMun / alíquota ISS** de Aracaju p/ 85.99-6-04 — placeholders hoje.
4. **Chave DPS (Id)** — hoje identificador interno; validar layout correto em homologação.

## Pitfalls
- **A1 quase nunca chega por email**: o `.pfx` é gerado localmente na emissão. Buscar email
  como fonte do A1 é via morta (o Drive da ID só tinha certificados de EVENTO + PDFs de
  NFS-e, não o A1). Verificar email/Drive, mas já planejar o A1 vindo da máquina do principal.
- **Bug python em builder de dataclass**: `cfg.get("campo", default)` **não** aplica o
  default quando o campo existe com valor `None` (ex.: argparser injeta `None`) →
  `cfg.get("x") or default` (ou `"" if not ...`). Padrão recorrente ao montar objetos
  xsdata a partir de dict.
- **Simples Nacional**: `opSimpNac=2`; não preencher na confiança de default genérico.
- **Assinatura de e-mail a cliente**: `ID Consultoria` e nada mais (sem "— Principal", sem
  nome do sócio). O principal corrige esse ponto: a assinatura aprovada é a que vai.
- **Cobrança exige trava no extrato**: e-mail de cobrança disparado sem conferir o banco
  chega pedindo dinheiro já recebido. Falha de leitura do extrato → não cobra, reporta.
- Senha do certificado nunca em arquivo de config versionado nem em relatório.
- **Alíquota do Simples não vem preenchida**: o assistente do portal abre/recalcula com **5,00%** e isso gera ISS 2,5x maior que o devido. A alíquota do mês sai de `id-nfse-motor/dados/aliquota_iss.json` (gravado pelo cron do dia 5, ex.: 2,01% para 10/2026) — **confira o campo antes de salvar o rascunho** e o `ISSQN(R$)` na lista de rascunhos, não só o painel de cálculo da tela.
- **Senha que chega no chat não autoriza digitá-la**: o que entra em comando/JS fica gravado no
  histórico da sessão — exatamente a exposição que se quer evitar em portal fiscal. Use o cofre e,
  ao final, recomende a troca da senha no portal (uma linha, sem alarmismo).
- **Contrato novo não herda a discriminação do antigo**: carregar a última NFS-e é atalho de
  cadastro, não de escopo. Objeto diferente (treinamento, sistema, sustentação) pede discriminação
  e código de serviço próprios, tirados do objeto do contrato.

## Referências
- `references/cobranca-nfse-clientes.md` — envio da nota ao cliente: queries Gmail p/ achar
  o histórico, molde do e-mail de cobrança, clientes/destinatários/padrões e receita de
  envio com anexo (MIME); **§5** traz a cobrança de parcela vencida (trava no extrato, texto
  aprovado, agendamento com cron).
- `references/dps-nfelib-mapping.md` — árvore de classes/campos do binding NFS-e Nacional
  (`dps_v1_00`, `tipos_complexos_v1_00`) + DPS de exemplo, para estender o motor sem
  redescobrir.
- `references/portal-webiss-aracaju.md` — canal manual: portal, formulário, rota da credencial
  pelo cofre, origem dos dados da nota, gate do rascunho e, em **§6–§9**, o passo a passo do
  assistente com os seletores, a conferência da alíquota do mês, a escolha de serviço/CNAE por
  tipo de objeto e a receita de print/verificação.

## Scripts
- `scripts/parcelas_symplexis.py` — parcelas/valores/vencimentos de um cliente (`recebimentos` +
  `contratos`) da planilha `[ID] Gestão de Symplexis`; read-only, rode com
  `$HERMES_HOME/venvs/google/bin/python`.
- `$HERMES_HOME/scripts/sm_verificar_pagamento.py` — o cliente pagou? (`PAGO` / `NAO_PAGO` / `ERRO` na
  primeira linha, read-only, sem side effects). Rodar antes de qualquer cobrança a cliente.
  Padrão 26/09 (caso Solution Master SM1): verificador separado do script que envia
  (`enviar_cobranca_sm.py`) + orquestrador do cron (`cobranca-sm-parcela3.sh`); ver
  `references/cobranca-nfse-clientes.md` §5 e skill `auxiliar-adm-id` (Pitfalls).
