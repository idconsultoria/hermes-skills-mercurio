# Qwen3-TTS VoiceDesign — Prompt Format

Formatos de `instruct` para o modelo `Qwen3-TTS-12Hz-1.7B-VoiceDesign`, extraídos do [blog oficial de lançamento](https://qwen.ai/blog?id=qwen3tts-0115).

## ⚠️ Regra nº 1: idioma do instruct (DESCOBERTA CRÍTICA — Jun/2026)

O `instruct` (descrição da voz) deve estar em **INGLÊS** (formato estruturado) ou **CHINÊS** (formato parágrafo). 

**O modelo IGNORA instruções em português.** Enviar "Voz masculina, tom grave-médio" faz o modelo reverter ao viés do treino — sotaque chinês. A saída de fala (o texto falado) pode ser português normalmente, mas a instrução de voz em si precisa estar em inglês.

✅ Correto: `"A calm, confident male voice, deep baritone..."` + `language_id: pt`
❌ Errado: `"Voz masculina calma e confiante..."` (vira sotaque chinês)

## Formato A — Estruturado chave:valor (recomendado para PT-BR)

Usado em 4 exemplos oficiais na página de lançamento. Uma dimensão por linha, `chave: valor.\n`:

```
gender: Male.
pitch: Low male pitch with significant upward inflections for emphasis and excitement.
speed: Fast-paced delivery with deliberate pauses for dramatic effect.
volume: Loud and projecting, increasing notably during moments of praise and announcements.
age: Young adult to middle-aged adult.
clarity: Highly articulate and distinct pronunciation.
fluency: Very fluent speech with no hesitations.
accent: British English.
texture: Bright and clear vocal texture.
emotion: Enthusiastic and excited, especially when complimenting.
tone: Upbeat, authoritative, and performative.
personality: Confident, extroverted, and engaging.
```

### Dimensões disponíveis (validadas dos exemplos oficiais)

| Chave | O que descreve | Exemplos de valor |
|---|---|---|
| `gender` | Gênero | Male, Female |
| `pitch` | Altura/tonalidade | Low male pitch, high, deep baritone, steady and controlled |
| `speed` | Velocidade | Fast-paced, deliberate, slow, moderate, slow with pauses |
| `volume` | Volume | Loud, moderate, conversational, projecting |
| `age` | Idade | Young adult, middle-aged, elderly |
| `clarity` | Dicção | Highly articulate, clear, distinct |
| `fluency` | Fluência | Very fluent, fluent, unhurried |
| `accent` | Sotaque (CRÍTICO para PT-BR) | Brazilian Portuguese, American English, British English |
| `texture` | Textura/qualidade vocal | Smooth, warm, velvety, gravelly, bright, resonant, nasal |
| `emotion` | Emoção | Confident, enthusiastic, calm, intense, ironic |
| `tone` | Tom | Direct, laconic, authoritative, upbeat, commanding |
| `personality` | Personalidade | Self-assured, confident, theatrical, performative |

### Exemplo real testado — voz Hermes (Jun/2026)

```
gender: Male.
pitch: Deep, low baritone, steady and controlled.
speed: Moderate pace, deliberate but not dragged.
volume: Moderate, conversational, with quiet authority.
age: Adult.
clarity: Clear and precise articulation.
fluency: Fluent, smooth delivery with natural Brazilian rhythm.
language: Brazilian Portuguese.
accent: Native Brazilian Portuguese, from São Paulo, natural and authentic.
texture: Smooth, warm, velvety quality.
emotion: Confident, with subtle irony.
tone: Direct, laconic, slightly ironic.
personality: Self-assured, no need to prove anything. Bridge between worlds.
```

## Formato B — Parágrafo descritivo (chinês)

Usado quando o texto de saída é chinês. Uma frase contínua:

```
"体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显，营造出黏人、做作又刻意卖萌的听觉效果。"
```

## Formato C — Background Information (personagem completo)

Inclui nome, histórico, características físicas e traços de personalidade:

```
Character Name: Marcus Cole
Voice Profile: A bright, agile male voice with a natural upward lift, delivering lines at a brisk, energetic pace...
Background: Longtime broadcast booth announcer for national television, specializing in live interstitials...
Presence: Late 50s, neatly groomed, dressed in a crisp shirt under studio lights...
Personality: Energetic, precise, inherently engaging...
```

## Mapeamento de parâmetros (nosso FastAPI)

| Parâmetro POST | Função Python | Descrição |
|---|---|---|
| `input` | `text` | Texto a ser falado |
| `voice` | `instruct` | Descrição da voz (use formato A acima) |
| `language_id` | `language` | `"pt"` vira `"Portuguese"` |

O `voice` que enviamos no POST `/v1/audio/speech` vira o `instruct` no `generate_voice_design()`.

## Erros comuns

| Erro | Resultado |
|------|-----------|
| Instruct em português | Sotaque chinês, modelo ignora descrição |
| Apenas "voz masculina" | Genérico, sem controle de timbre |
| "Make it sound like [celebridade]" | Bloqueado pelo modelo (copyright) |
| Repetir adjetivos ("very very deep") | Ignorado — use escala ("low" → "very low") |
| Lista solta de keywords | Funciona menos que frase completa |
