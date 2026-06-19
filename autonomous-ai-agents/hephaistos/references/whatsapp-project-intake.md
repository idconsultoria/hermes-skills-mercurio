# WhatsApp Project Intake

> Como extrair contexto de projetos recebidos via WhatsApp (texto + áudio PTT) e gerar briefing estruturado no vault Hephaistos.

## Quando Usar

O cliente envia um briefing de projeto via WhatsApp contendo:
- Mensagens de texto descrevendo o escopo
- Áudios PTT (WhatsApp voice notes, formato OGG)
- Conversa longa com informações espalhadas

## Pipeline de Extração

### 1. Transcrever Áudios (OGG → WAV → Whisper)

```bash
# Converter OGG para WAV 16kHz mono
ffmpeg -i "arquivo.ogg" -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.wav

# Transcrever com Whisper (modelo base é suficiente para PT-BR)
python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('/tmp/audio.wav', language='pt')
print(result['text'])
"
```

**Instalação (primeira vez):**
```bash
pip3 install openai-whisper  # ~2GB (torch + dependencies)
```

**Modelos recomendados:**
- `base` (142MB) — suficiente para PT-BR claro, áudio WhatsApp
- `small` (466MB) — para áudios ruidosos ou com sotaque carregado
- `medium` (1.5GB) — precisão máxima, mas lento em CPU

**Aviso FP32 em CPU:** Whisper avisa "FP16 is not supported on CPU; using FP32 instead" — é um warning inofensivo, a transcrição funciona normalmente.

### 2. Extrair Requisitos da Conversa

Percorrer o histórico do WhatsApp extraindo:

| Informação | Onde Encontrar |
|-----------|---------------|
| Nome do projeto/evento | Primeiras mensagens, costuma ser repetido |
| Cliente/organização | Quem está contratando |
| Entregáveis | Lista explícita (logo, camisa, banner, etc.) |
| Direcionamento visual | Áudios costumam conter as pistas mais valiosas |
| Cronograma | Prazos mencionados |
| Condições comerciais | Valor, sinal, recibo, forma de pagamento |
| Restrições | "não faça X", "evite Y", "sem o G no meio" |

### 3. Gerar Mapa de Empatia (obrigatório antes de DESIGN)

Após extrair requisitos, gerar mapa de empatia do cliente. Usar template do `design-research-moodboard` skill:

| Campo | Fonte |
|-------|-------|
| **VÊ** | Concorrência, referências do setor, contexto de mercado |
| **OUVE** | Parceiros, equipe, comunidade (cobranças, expectativas) |
| **PENSA & SENTE** | Quotes reais do áudio + inferências do comportamento |
| **FALA & FAZ** | Comportamento observado (pagou rápido = comprometido; "não faço ideia" = delega confiança) |
| **DORES** | Não sabe briefar, pressão de terceiros, dependência de gabaritos |
| **GANHOS** | Identidade profissional, engajamento, reconhecimento |

Gerar também versão HTML visual (`visao/mapa-de-empatia.html`) para apresentação ao cliente.

### 4. Gerar Briefing no Vault

Criar estrutura de projeto no vault Hephaistos:

```
[projeto]/
├── _contexto/
│   ├── estado-atual.md   → Status, modo pipeline, próximos passos
│   └── fio-do-projeto.md → Timeline, entregáveis, diretrizes, contato
├── visao/
│   └── briefing.md       → Documento completo com todas as seções
├── _compact/
│   └── projeto.md        → Resumo de 1-2 linhas
├── arquivos/             → Assets (logotipos, referências, gabaritos)
└── notas-de-sessao/      → Logs de sessão
```

### 5. Estrutura do Briefing (`visao/briefing.md`)

1. **Contexto do Projeto** — O que é o evento/produto, organizador, natureza
2. **Escopo de Entregáveis** — Tabela com item, descrição, aplicação
3. **Direcionamento Visual** — Elementos obrigatórios, observações do cliente, liberdade criativa
4. **Público-Alvo** — Primário, secundário, tom desejado
5. **Cronograma** — Marcos e datas
6. **Condições Comerciais** — Sinal, recibo, status de pagamento
7. **Observações Técnicas** — Gabaritos, formatos de entrega, templates de gráfica
8. **Referências Visuais** — Sugestões de pesquisa para o designer

### 6. Próximos Passos

Após gerar o briefing:
1. Apresentar ao cliente para validação
2. Solicitar informações faltantes (gabaritos de gráfica, dimensões, etc.)
3. Avançar para o modo DESIGN (pesquisa visual → moodboards → protótipo)

## Exemplo Real

Projeto: **Jogo da Solidariedade** (Maçonaria Paranaense)
- Entregáveis: logo, camisa de futebol, bola personalizada, banner redes sociais
- Diretriz do áudio: "bola de futebol + símbolo maçônico, sem o G no meio"
- Prazo: pós-Copa 2026 (final julho / início agosto)
- Comercial: fechado, sinal via PIX recebido, recibo pendente

## Pitfalls

- **Whisper não instalado** — `pip3 install openai-whisper` instala torch (~2GB), leva alguns minutos. Fazer em background.
- **OGG não reconhecido** — ffmpeg lê OGG nativamente. Se o arquivo estiver corrompido, tentar `ffmpeg -err_detect ignore_err -i arquivo.ogg ...`
- **Transcrição imprecisa** — áudios WhatsApp são comprimidos (OPUS codec). Se a qualidade estiver baixa, usar modelo `small` ou `medium`. Para PT-BR com gírias locais, o modelo `base` já funciona bem.
- **Informação espalhada na conversa** — a conversa pode ter 20+ mensagens com intervalo de dias entre elas. Ler toda a conversa antes de começar a extrair requisitos — informações complementares costumam vir em mensagens separadas.
- **Áudio irrelevante** — verificar se o áudio é realmente sobre o projeto. Clientes podem enviar áudios antigos ou de contexto diferente. Validar comparando data/hora com a conversa.
