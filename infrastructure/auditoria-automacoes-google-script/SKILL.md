---
name: auditoria-automacoes-google-script
type: ToolIntegration
timestamp: 2026-10-12T00:00:00Z
description: "Use para auditar/desativar automações de Apps Script."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [google, apps-script, automacao, auditoria, gmail, triggers]
    category: infrastructure
---

# Auditoria de automações legadas em Google Apps Script

Use quando alguém da ID pedir para descobrir de onde vem um email recorrente (ex.: ritual semanal) ou desativar uma automação antiga.

## 1. Achar a origem pelo email (não pelo corpo)

`Message-ID` começando com `<autogen-java-...@google.com>` = envio via Apps Script `MailApp`/`GmailApp` (SMTP comum produz outro padrão). Isso separa "script do Google" de terceiros/cron.

Roteiro: ler a mensagem inteira (headers + body) via Gmail API com o token do destinatário; pegar `From`, `Date` (UTC), `Return-Path`, `Message-ID`; depois contar a série histórica com `users().messages().list(q='from:<remetente>')` + batch de metadata. Consolidar por remetente + assunto e olhar dia/hora (o horário do disparo costuma ser constante, ex. domingo 05:54 BRT).

Usar o venv com googleapiclient: `/data/data/com.termux/files/home/capitolium/id-nfse-motor/.venv/bin/python`.

## 2. Localizar o acionador

O acionador vive na conta **remetente**, não na conta que recebe. Sem credencial dessa conta, usar o navegador já logado:

- `https://script.google.com/home/triggers` — todos os acionadores da conta.
- `https://script.google.com/home/projects/<SCRIPT_ID>/triggers` — do projeto (o ID sai do atributo `data-script-id` da linha).
- A linha mostra projeto, última execução, evento (`De acordo com o horário`), função e taxa de erro; a página de detalhes do projeto traz descrição, criado em, última modificação e escopos OAuth (`script.send_mail` etc.).
- Bater a **hora da última execução** com a hora do email identifica o acionador sem ambiguidade (vários projetos têm nomes parecidos, ex. "Automação de Planilha").

## 3. Ler o código do projeto (sem clicar)

No editor (`/home/projects/<ID>/edit`) o código do Monaco é acessível via JS mesmo sem DOM visível:

```python
js("monaco.editor.getModels().map(m => m.uri + '\\n' + m.getValue())")
```

Isso revela destinatários (`emails = [...]`), assunto e links — essencial para saber quem mais é afetado antes de desativar (um ritual pode disparar para vários sócios, não só para quem pediu).

## 4. Desativar (e o pitfall que custa tempo)

Pitfall medido nesta rama: em `browser_exec` **não há clique real** — `click_at_xy` não gera evento nenhum e `cdp('Input.dispatchMouseEvent', ...)` dá timeout. Menus do Google (Closure/jsaction) ignoram `MouseEvent` sintético, mas aceitam **keydown sintético**: dá para abrir o menu (focus + `KeyboardEvent('keydown', Enter, keyCode 13)`), ver o destaque pela classe `FwR7Pc` e navegar com `ArrowDown`. Ainda assim a ativação do item `Excluir acionador` não dispara (ação destrutiva exige gesto confiável).

- Não insistir em variações de clique. Caminho: (a) identificar tudo, (b) deixar a página de acionadores do projeto aberta, (c) **pedir o clique humano** (1 clique no ⋮ da linha → Excluir acionador), (d) verificar.
- Alternativa de efeito equivalente, sem clique: editar o código para o corpo da função virar no-op + salvar (`Ctrl+S`). Ressalvas: o acionador continua existindo (zumbi que roda sem efeito) e renomear a função gera email de erro ao dono — preferir excluir o acionador.

## 5. Verificar (obrigatório)

Recarregar a página de acionadores do projeto e exigir `Mostrando 0 acionador` / `Nenhum resultado`. Só então declarar desativado. O projeto e o código **permanecem** — reativar = recriar o acionador.

## 6. Fechar o ciclo

Informar a quem pediu: nome/função do projeto, conta dona, horário do disparo, destinatários que param de receber e que a exclusão vale para todos. Formulário/planilha do fluxo continuam existindo (se quiser, fechar respostas do Form).
