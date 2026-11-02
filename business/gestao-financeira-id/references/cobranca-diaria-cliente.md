# Cobrança recorrente de cliente com parcela em atraso

Receita para transformar "esta parcela venceu e não pagaram" em uma rotina que insiste sozinha,
sem cobrar quem pagou e sem repetir texto. Vale para qualquer cliente/parcela da ID: o que muda
por caso é o JSON de configuração, não o código.

## Ordem dos passos

1. **Estabelecer o fato antes de cobrar.** Três fontes: aba `recebimentos` da Symplexis
   (parcela/valor/vencimento/status), a NFS-e enviada (número, data, thread do e-mail) e o extrato
   do Inter (o crédito existe?). Sem os três, não se escreve ao cliente.
2. **Identificar a thread certa.** A cobrança vive na conversa da NFS-e, não em e-mail novo: é ali
   que o financeiro do cliente olha. Achar pelo assunto da nota (busca no Gmail por
   `"Nota Fiscal"` + domínio do cliente) e ler `Message-ID`/`References` da última mensagem.
3. **Configurar em JSON** (`work/cobranca-<cliente>/config.json`): parcela, valor em centavos,
   vencimento ISO, número da NFS-e, data de envio da nota, `thread_id`, destinatários base
   (`to`/`cc`), bloco de escalonamento (`a_partir_do_dia`, `to`, `cc`), chave Pix,
   `valor_min_credito` e a assinatura.
4. **Gate financeiro antes do envio.** Verificador de extrato com a janela começando no
   **vencimento** e `valor_min_credito`. Três saídas: `PAGO` → encerra e avisa uma vez; `ERRO` →
   **não cobra**; `NAO_PAGO` → monta e envia.
5. **Dia útil de cobrança = dias úteis decorridos após o vencimento, contando hoje** (seg–sex).
   Vencimento em domingo → o primeiro dia útil é a segunda seguinte. Feriado não está no
   calendário: em atraso longo, conferir à mão.
6. **Rotação de texto.** 8 corpos distintos (cobrança objetiva, destravar liquidação, número do
   atraso, rotina declarada, pedido de calendário, o que a parcela sustenta, compromisso por
   escrito, revisão de cronograma), índice `(dia-1) % 8`. O **dia da escalada força** o texto que
   explica o que a parcela sustenta — é o argumento de continuidade que o dono pede ao escalar.
7. **Escalonamento.** Base: financeiro do cliente. A partir do dia definido, o dono da empresa
   entra no `To` e o financeiro fica em cópia; uma nota de cópia entra no corpo ("levo ao seu
   nível porque passou do ponto que se resolve na operação").
8. **Enviar e provar.** `messages().send(body={"raw": raw, "threadId": <thread>})`; reler com
   `messages().get` e exigir `SENT` + mesmo `threadId`; reler a thread e conferir que ganhou a
   mensagem. "O send retornou ok" não é prova.
9. **Registrar e deduplicar.** `estado.json` com os envios por data (um e-mail por dia, mesmo se o
   cron rodar duas vezes) e `log/<data>-diaN.json` com ids/labels/destinatários.

## Antes de ligar o cron

- **Dry-run obrigatório** e **simulação do dia da escalada** com override de dia
  (`--dia 3 --dry-run`), conferindo destinatários, assunto, template e assinatura no texto
  impresso.
- Disparar o job uma vez pelo próprio agendador: o dedupe do dia faz o script sair com "já houve
  cobrança hoje" — prova o caminho cron→script→venv sem mandar e-mail extra.
- Cron em `no_agent` (o stdout é o relatório entregue ao dono), dias úteis, ~09h BRT.

## Pitfalls

- **Janela de verificação larga casa o crédito da parcela ANTERIOR** e a cobrança nunca sai —
  a janela começa sempre no vencimento da parcela cobrada.
- **Cobrar depois de falha de leitura do banco** é o erro que queima relação: `ERRO` nunca envia.
- **Não inventar cláusula de multa/juros** que o contrato não cita: o texto cobra o principal e
  pede posição e data. Consequência dita é só a que a ID decidiu (revisar cronograma, levar à
  direção).
- **Destinatário só o autorizado.** Herdar da NFS-e e escalar apenas quem o dono mandou; não
  incluir diretor/vice "para pressionar" por conta própria.
- **Dois venvs no mesmo wrapper**: extrato pelo venv do motor do Inter, e-mail pelo venv com
  `googleapiclient`; o wrapper lê vencimento/valor do JSON (nunca digitados no `.sh`).
- **Neste host, `.sh` com shebang `#!/usr/bin/env bash` não executa direto** (`bad interpreter`):
  rodar à mão com `bash script.sh`. O cron chama via bash e não tem esse problema.
- **Assinatura dos e-mails** (ordem do dono): `ID Consultoria` / `Mercúrio — IA assistente
  administrativa da ID` / contato.
