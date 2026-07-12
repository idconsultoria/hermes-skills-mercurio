# WhatsApp vs Telegram Conflation — Pitfall Confirmado

## Problema

O agente do Cron #3 consistentemente **pula a entrega WhatsApp** porque confunde as instruções de "entrega" no prompt. Em vez de chamar a bridge API (`curl http://127.0.0.1:3000/send`), o agente coloca o conteúdo da mensagem na resposta final e entrega apenas ao Telegram (via `deliver: origin`).

## Histórico

| Data | Evidência |
|------|-----------|
| 02/07/2026 | Discussão no session `20260702_140005_4daa444f` — mesmo padrão identificado |
| 08/07/2026 | Confirmado no cron output `e418042f0c99/2026-07-08_10-49-30.md` — agente disse "Vou agora entregar a mensagem formatada no Telegram" e não chamou o curl |

## Causa Raiz

O prompt tem **duas definições concorrentes de "entrega"**:

1. **WhatsApp via bridge** — instrução explícita no Pipeline Step 11, comanda curl para `http://127.0.0.1:3000/send`
2. **Telegram via `deliver: origin`** — automático do cron job; a resposta final do agente é entregue ao chat de origem (Telegram DM)

O agente sempre escolhe a opção mais fácil (a automática) e **nunca executa a etapa explícita** (curl), por dois motivos:

- A seção "## Resposta final" no prompt do cron diz que a resposta deve ir para "o chat de origem do usuário" e conter APENAS confirmação — o agente interpreta isso como "a entrega é minha resposta final"
- O passo 11 (WhatsApp) está no meio da pipeline numerada; quando o agente chega no "## Resposta final", já esqueceu ou substituiu o passo 11

## Pitfall 2: `write_file` bloqueia `/tmp/` — agente alucina envio

### Descoberto: 09/07/2026

Após a correção estrutural do prompt (PASSO A → PASSO B), o prompt instruía o agente a usar `write_file` para salvar a mensagem em `/tmp/iaf_whatsapp_{SLUG}.txt`. Porém, a ferramenta `write_file` **bloqueia caminhos em `/tmp/`** por segurança (sistema de arquivos protegido). O agente:

1. Chamava `write_file('/tmp/iaf_whatsapp_09072026.txt')` → **DENIED**
2. A ferramenta retornava erro, mas o agente **alucinava** um `messageId` e declarava sucesso
3. O arquivo nunca era criado → o curl subsequente (que lê o arquivo) falhava silenciosamente
4. Nenhuma mensagem chegava ao WhatsApp

**Solução:** substituir `write_file` por `terminal` com heredoc:
```bash
cat > /tmp/iaf_whatsapp_{SLUG}.txt << 'HERMES_EOF'
📰 *IAF — Manhã Aumentada* · DD/MM/AAAA
...
HERMES_EOF
```

O agente escreve o conteúdo real no lugar dos placeholders e o shell cria o arquivo corretamente.

**Armadilha futura:** se o prompt mencionar `write_file` para qualquer caminho em `/tmp/`, o mesmo erro se repetirá. Apenas `terminal` com redirecionamento shell funciona para `/tmp/`.

**Evidência:** cron output `e418042f0c99/2026-07-09_10-51-22.md`, linhas 1939-1941:
```
⚠️ File-mutation verifier: 1 file(s) were NOT modified
  • /tmp/iaf_whatsapp_09072026.txt — [write_file] Write denied
```

## Correções Aplicadas

### No SKILL.md (`iaf-newsletter-pipeline`):

Step 11 foi reescrito para:
- Título alterado para "WHATSAPP VIA BRIDGE (NÃO PULE — SEPARADO DA ENTREGA TELEGRAM)"
- Adicionado aviso: "A entrega WhatsApp e a entrega Telegram são DUAS AÇÕES SEPARADAS"
- Adicionada ARMADILHA explícita com data do bug confirmado
- Fluxo reordenado: (a) WhatsApp primeiro, (b) Resposta final depois
- Método de envio mudou de Python urllib (inline na skill) para `curl` via terminal com Python one-liner para escaping JSON

### No cron job

A seção de entrega do prompt do Cron #3 foi reescrita em 08/07/2026 com a seguinte estrutura:

- Seção renomeada para `## ⚠️ REGRA ABSOLUTA — ORDEM DE ENTREGA (NÃO PULE)`
- **PASSO A (WhatsApp):** salvar mensagem em `/tmp/iaf_whatsapp_{SLUG}.txt` via terminal com heredoc (`cat > path << 'HERMES_EOF'` — **NÃO use `write_file`** pois bloqueia `/tmp/`) → enviar via curl com Python inline → verificar messageId
- **PASSO B (Resposta final):** só escrever resposta APÓS WhatsApp confirmado. Formato: `✅ Deploy: {URL} ({HTTP_STATUS})` + `✅ WhatsApp: {messageId}`
- Guardrail explícito: "Se sua resposta tem mais de 3 linhas, você está incluindo conteúdo que deveria ter ido só via bridge"
- Formato da mensagem movido para subseção do PASSO A (não mais no fim do prompt)

## Verificação

Se a resposta final do agente NÃO contém um `messageId`, a entrega WhatsApp foi pulada.
Se a resposta final contém o TEXTO DA MENSAGEM em vez de só confirmação, o agente confundiu as duas entregas.
