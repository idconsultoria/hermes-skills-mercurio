# Boletim Matinal Áudio — cron 646249678e11 (08:00 BRT)

Cron diário que consome a edição IAF do dia + TaskFlow + Moodle e entrega um **áudio de
~2 min** via `text_to_speech` (hermes-tts — a MESMA ferramenta de voz usada para
responder ao Gustavo com voz). Criado em 08/08/2026; substituiu os crons
"Panorama Diário TaskFlow" e "relatorio-atividade-alunos-moodle".

## Configuração

- **Schedule:** `0 11 * * *` (08:00 BRT / 11:00 UTC) — roda DEPOIS do Cron #3 da IAF
  (07:40 BRT / 10:40 UTC), então o HTML da edição do dia já existe em
  `/opt/data/cron/history/iaf_*.html`. O cron sempre pega a edição fresca.
- **Deliver:** origin (Telegram)
- **Skills:** taskflow-mcp-rules + moodle-admin
- **Job ID:** `646249678e11`

## Formato do áudio (aprovado pelo Gustavo em 08/08/2026)

> **Roteiro canônico:** `/opt/data/cron/boletim_matinal_referencia.txt` — o prompt do
> cron MANDA ler esse arquivo e seguir a estrutura. É a referência canônica; nunca
> improvise formato diferente.

Estrutura fixa de 5 blocos (~300 palavras PT-BR, ritmo de rádio):
1. **Abertura** — "Bom dia, Gustavo. [dia da semana], [data]. Resumo do seu dia em dois minutos."
2. **Notícias** — 4 destaques mais relevantes da newsletter do dia (2-3 frases cada:
   título em 1 frase + contexto/porquê importa)
3. **TaskFlow** — atrasadas (título + dias de atraso), pendentes de hoje, inbox não
   processado, 1 sugestão de foco ("Sugestão: ataque X primeiro — ...")
4. **Moodle** — atividade digna de nota nas últimas 24-26h (quem, nº logins, horários,
   o que viu); se quase ninguém acessou, alertar + sugerir lembrete
5. **Fechamento** — "Era isso. Bom [dia], e [frase curta de estímulo]."

Regras de tom: boletim de rádio matinal (claro, ritmo de notícia, entusiasmo moderado);
datas/horas **por extenso** ("vinte e uma e cinquenta e seis"); zero jargão corporativo;
PT-BR natural.

Instrução de voz TTS padrão: "Apresentador de boletim matinal: voz clara, ritmo de
notícia de rádio, entusiasmo moderado, pausas naturais entre blocos. Português do Brasil."

## Fontes de dados (ordem de coleta)

1. **Newsletter:** liste `/opt/data/cron/history/iaf_*.html`, escolha o MAIS RECENTE
   (edição do dia; se só houver de ontem, use a mais recente e ajuste o texto). Extraia
   títulos h1-h3 + resumos/descrições; selecione os 4 mais relevantes para um
   profissional de consultoria/IA.
2. **TaskFlow:** `taskflow_panorama_report` + `taskflow_get_next_actions` (limit 8).
   Converter datas UTC → BRT (UTC-3) antes de mencionar. Anotar: atrasadas + dias,
   pendentes de hoje, inbox.
3. **Moodle:** atividade últimas 26h via stdin-pipe do psql (ver skill moodle-admin),
   excluindo `%config_log_created%` e `%capability_assigned%`. Se alguém acessou,
   detalhar navegação pelo userid. Anotar: quem, quantos logins/eventos, horário, o que viu.

## Entrega

A resposta final do cron deve incluir `MEDIA:<caminho do .ogg gerado>` — sem isso o
áudio não chega ao Gustavo. Escrever também um resumo curto em texto do que foi coberto.

## Exemplo real (08/08/2026)

Notícias: OpenAI desacelera Astra/GPT-6 (limiar "critical" do Preparedness Framework);
Cloudflare Kitesurf (navegador para agentes); Canva corta 1/3 da projeção de receita
(custo por token de modelos terceiros); alerta prompt injection (extrato bancário quase
enviado). TaskFlow: 3 atrasadas (Gravar aulas 11d, Oficinas pré-turma 11d, Revisão GTD
12d), 1 inbox, 0 pendentes. Moodle: só Matheus (userid 11) acessou — 2 logins 21:56 e
23:26, páginas do Módulo 1; 6 alunos inativos 26h.
