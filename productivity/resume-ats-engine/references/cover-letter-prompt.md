# Carta de Apresentação — agy → HTML → PDF

Carta de apresentação premium, estética, 1 página, gerada pelo **agy** (Google
Antigravity CLI) como HTML autônomo e renderizada para PDF via WeasyPrint.

## Quando usar

- Usuário pede "carta de apresentação", "cover letter", "carta de motivação" junto com o currículo
- Verdict da avaliação indicou "aplicar com cover letter forte" (match 60-74%)
- **Profissional de área criativa** → a carta DEVE ser caprichada: ver `references/carta-criativa.md`

## Pré-requisitos

- agy instalado e autenticado no host (`agy doctor` → "All checks passed") — ver skill `agy`
- Invocação SEMPRE como `terminal(background=true, notify_on_complete=true)`, sem timeout
- Renderer local: `/opt/data/.venvs/resume-ats/bin/python scripts/render_html_to_pdf.py`

## Dados a embutir no prompt (do JSON/currículo + vaga)

1. **Nome e cargo-alvo** + contato (email, telefone, LinkedIn/Instagram)
2. **Empresa e vaga** (nome exato do cargo, setor, diferencial da empresa se pesquisado na Fase 2)
3. **2-3 conquistas-chave com métricas** (as mais relevantes à vaga — mesmas do currículo)
4. **2-3 motivos de fit**: por que a vaga + por que a empresa (se soubermos algo concreto da pesquisa, citar)
5. **Ações que você quer provocar**: entrevista, conversa, "conversar sobre a oportunidade"

## Template de prompt (montar com dados reais; manter < 25KB)

```
Gere um HTML autônomo de CARTA DE APRESENTAÇÃO premium, pronta para impressão em A4, 1 página.

## Conteúdo (exato, não invente nada)
- Remetente: [NOME] — [CARGO-ALVO] — [EMAIL] · [TELEFONE] · linkedin.com/in/[USER]
- Destinatário: [EMPRESA] — [CARGO DA VAGA]
- Data: [DATA ATUAL]
- Corpo (4-5 parágrafos curtos, PT-BR, tom profissional e direto, sem clichê):
  1. Abertura: interesse na vaga [CARGO] na [EMPRESA] + 1 frase de contexto (por que agora)
  2. Fit técnico: 2-3 conquistas com métricas reais: [CONQUISTA 1], [CONQUISTA 2], [CONQUISTA 3]
  3. Fit cultural/estratégico: [1-2 motivos concretos sobre a empresa/vaga]
  4. Encerramento: convite para conversa + disponibilidade
- Assinatura: [NOME]

## Design (obrigatório)
- Estilo "padrão consultoria premium": fundo off-white suave (#F8F9FA), card branco com sombra sutil, cores sóbrias (verde escuro / azul acinzentado / âmbar), NUNCA fundo escuro
- Header elegante: nome em destaque, linha fina divisória, contato em uma linha discreta
- Tipografia: fontes do sistema (Georgia/serif para nome, sans-serif para corpo) — SEM Google Fonts, SEM CDN
- Espaçamento generoso, margens de impressão confortáveis (0.75in)
- SEM emojis (ícones só como SVG inline se necessário), SEM gradientes chamativos, SEM pizza/donut
- Print-ready: todo o conteúdo em 1 página A4

## Regras
- HTML autônomo (CSS inline no <style>), sem dependência externa, sem JavaScript
- Salve o arquivo em /home/ubuntu/carta_<nome>.html
```

## Fluxo de execução

```bash
# 1. Escrever prompt local e enviar ao host
cat > /opt/data/tmp/carta_prompt.md << 'PROMPT'
[... prompt montado acima ...]
PROMPT
scp -F ~/.ssh/config /opt/data/tmp/carta_prompt.md oracle-host:/tmp/carta_prompt.md

# 2. Executar agy em background (nunca com timeout)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  agy --dangerously-skip-permissions --print "$(cat /tmp/carta_prompt.md)"'
# → terminal(background=true, notify_on_complete=true); acompanhar com process(action='poll')

# 3. Trazer o HTML gerado (agy lê/escreve arquivos no host — conferir o caminho pedido)
ssh oracle-host 'ls -la /home/ubuntu/carta_*.html'
ssh oracle-host 'sudo cp /home/ubuntu/carta_<nome>.html /home/ubuntu/selfhost/hermes/data/carta_<nome>.html'

# 4. Renderizar localmente para PDF (WeasyPrint, sanitiza Google Fonts + auto-fix)
/opt/data/.venvs/resume-ats/bin/python \
  /opt/data/skills/productivity/resume-ats-engine/scripts/render_html_to_pdf.py \
  /opt/data/carta_<nome>.html /opt/data/tmp/carta_<nome>.pdf

# 5. Verificar e entregar
# PDF via MEDIA. Se o usuário quiser o HTML: ZIPAR (Telegram descarta .html silenciosamente).
```

## Fallbacks (quando agy falhar — cota, timeout, sem auth)

1. **Prompt fracionado** — esqueleto curto (~800B) + edição do arquivo existente com segundo prompt (~4-5KB)
2. **HTML manual com tokens** — replicar o design acima em HTML/CSS à mão (tokens documentados aqui)
3. **Pi best (GLM 5.2)** — `pi -p "prompt" --provider opencode-go --model glm-5.2`, prompts muito focados

Sempre renderizar com `render_html_to_pdf.py` e validar: 1 página, texto extraível.

## Pitfalls

- **agy NÃO aceita .html no Telegram** (descartado silenciosamente) — entregar PDF; HTML só zipado
- agy pode **truncar output** >75KB — carta é pequena, mas se vier cortada, re-executar com prompt menor
- **Verificar o arquivo no host** após execução (agy às vezes grava direto no disco, não no stdout)
- Google Fonts quebram no WeasyPrint — o script sanitiza; não confiar só nisso, pedir "sem Google Fonts" no prompt
- Carta em português para vaga BR; inglês para vaga gringa — seguir idioma da vaga
- **Carta com .letter-card min-height fixo quebra em 2 páginas** — o render_html_to_pdf.py injeta AGY_LETTER_FIX automaticamente; conferir contagem e visual
