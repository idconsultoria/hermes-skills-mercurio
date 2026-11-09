# Fluxo operacional da cobrança (scripts, config, estado)

Detalhe de implementação da política de `SKILL.md`. Nada aqui substitui a regra de texto
aprovado — é o encanamento.

## Onde vive

| peça | caminho |
|---|---|
| verificador de pagamento | `$HERMES_HOME/scripts/sm_verificar_pagamento.py` (imprime `PAGO`/`NAO_PAGO`/`ERRO`) |
| orquestrador | `$HERMES_HOME/scripts/cobranca_sm_diaria.sh` (verifica → decide) |
| texto/envio/estado | `$HERMES_HOME/scripts/cobranca_sm_diaria.py` |
| configuração | `$HERMES_HOME/work/cobranca-<cliente>/config.json` |
| estado | `.../estado.json` (um envio por dia útil) e `.../log/<data>-diaN.json` |
| aprovações | `.../aprovacoes.json` |

`venvs/google/bin/python` tem `googleapiclient` (Gmail/Drive); o venv do motor do Inter fica em
`work/idata/.venv`. Verificador roda com o venv do banco, envio com o do Google.

## config.json — campos que importam

`parcela`, `contrato`, `valor_centavos`, `vencimento`, `nfse`, `nfse_enviada`, `thread_id`,
`destinatarios_base` (to/cc), `escalada` (to/cc do N2), `prazo_prometido` + `promessa_origem`
+ `promessa_texto` + `resposta_recebida_em`, `pix_chave`, `valor_min_credito`, `remetente`,
`assinatura`, `regras_por_dia_semana`.

Trocar de parcela = editar o JSON, não o código. Valor/vencimento/nota **sempre** daqui.

## Janela do extrato

Usar a data de vencimento (ou a da promessa mais recente) como início da janela, nunca uma janela
fixa: janela larga casa o crédito da parcela **anterior** e a cobrança nunca sai.

## Envio na thread certa

Assunto `Re: ` + assunto **original, sem sufixo**, e
`users().messages().send(body={"raw": raw, "threadId": <thread da NFS-e>})`. `In-Reply-To` e
`References` sozinhos não bastam: mudar o assunto cria thread nova e a cobrança fica fora da
conversa da nota, onde o cliente olha.

Releitura: `threads().get` confirma +1 mensagem e o `threadId` do enviado; label esperado `SENT`.

## Assinatura e remetente

Enviar de `admin@idconsultoria.ai` (`$HERMES_HOME/google_token.json`) e assinar
`ID Consultoria` / `Mercúrio — IA assistente administrativa da ID` / contato. Conferir
`getProfile()` antes de enviar.

## Cron

Usar agente (não `no_agent`) quando houver decisão de texto/aprovação, com toolset `terminal` e
entrega na DM do sócio responsável. Fuso: host em UTC — `0 11 * * *` = 08h BRT; para one-shot,
preferir ISO com offset explícito.

## Ler a thread e as respostas do cliente

`scripts/ler_thread_gmail.py <thread_id>` lista remetente, destinatários, assunto e labels de
cada mensagem; `--corpo` traz o texto e `--de <nome>` filtra pelo remetente — é assim que se
confirma se o cliente respondeu antes de cobrar de novo.
