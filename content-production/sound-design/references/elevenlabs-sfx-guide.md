# ElevenLabs SFX Guide — Prompts Otimizados para UI Sound Design

> Baseado na documentação oficial ElevenLabs (SFX V2, 48kHz, 30s max),
> guia Promptomania, AIProductivity e boas práticas da comunidade (Jun 2026).

---

## 1. Visão Geral da Plataforma

- **Modelo:** ElevenLabs SFX V2 — saída em 48kHz (padrão broadcast/filme)
- **Gera 4 variações** por geração
- **Duração:** auto ou manual (0.1–30s)
- **Looping toggle:** para ambientes contínuos
- **Prompt Influence slider:** default 30% — controle de aderência ao prompt (mais alto = mais literal)
- **Export:** MP3 (44.1kHz) ou WAV (48kHz) — **sempre baixe WAV como master**, converta para MP3 só na entrega
- **Créditos:** 40 créditos/s quando duração é especificada (vs. custo menor em auto)
- **Licença:** uso comercial inclusa em planos pagos (Starter $5/mo+)

---

## 2. Framework de Prompt Engineering

### Fórmula

```
[Fonte/Objeto] + [Ação] + [Ambiente/Contexto] + [Modificador de Caráter/Mood]
```

### Princípios

1. **Material específico:** "metal", "cerâmica", "cristal", "madeira" — não genérico
2. **Ambiente acústico:** "sala pequena seca" ≠ "catedral com reverberação"
3. **Ação precisa:** "tick curto ataque rápido" > "som"
4. **Tempo/duração:** explicite se importante — "0.08s", "fade out em 0.3s"
5. **Mood ao final:** "cinematográfico", "frio", "tecnológico", "orgânico"
6. **Sem contradições:** "suave mas agressivo" confunde o modelo
7. **Onomatopeia + descrição:** "tick metálico agudo como um cristal" funciona melhor que só "tick"

### Ajuste fino (pós-escuta)

| Problema | Solução no prompt |
|---|---|
| Muito longo | Adicione `under 0.5 seconds`, `tight transient, minimal tail` |
| Muito cheio | Adicione `clean`, `minimal layers`, `no background ambience` |
| Sem impacto | Adicione `high impact`, `deep body`, `punchy attack` |
| Agudo demais | Adicione `warm`, `no piercing highs`, `rounded` |
| Sem personalidade | Adicione `cold`, `technological`, `crystal clear`, `dark` |

---

## 3. Prompt Influence

| Setting | Quando usar |
|---|---|
| **Alto (70–100%)** | UI ticks, clicks, one-shots — precisa ser exato |
| **Médio (30–50%)** | Default. Variação natural é bem-vinda |
| **Baixo (10–20%)** | Ambientes, texturas — surpresa é desejável |

**Para UI SFX:** use **Prompt Influence = Alto (80%)** — consistência entre variações更重要 que criatividade. Sempre especifique **duração manualmente**.

---

## 4. Prompts Otimizados — 5 UI SFX

### 4.1 hover (0.1s) — Tick cristalino curto

**Prompt 1 — Pureza máxima:**
```
Crystal clear short tick, single transient, ultrashort attack 2ms, no sustain, no reverb tail, dry and tight, tiny glass resonance at 8kHz, clean digital interface sound, 0.08 seconds, precise, minimal
```

**Prompt 2 — Metálico frio:**
```
Short metallic tick, cold steel, single hit, fast attack, no reverb, dry studio recording, precision UI interface sound, extremely short, high frequency ping, sub-100ms
```

**Settings:** Duration=0.1s, Influence=80%, Looping=off

### 4.2 click (0.15s) — Toc seco de cerâmica/metal leve

**Prompt 1 — Cerâmica:**
```
Dry ceramic pot click, small glazed clay, light percussive tap, clean attack, minimal resonance, no reverb, warm mid-range click, modern UI sound design, under 0.15 seconds, tactile, satisfying
```

**Prompt 2 — Metal leve:**
```
Light metal click, small aluminum component, precision mechanical switch, crisp attack, clean release, no reverb, dry studio acoustic, premium UI button sound, 0.12 seconds
```

**Settings:** Duration=0.15s, Influence=80%, Looping=off

### 4.3 open (0.25s) — Riser ascendente brilho

**Prompt 1 — Brilho puro:**
```
Short rising shimmer, bright ascending tone, clean sine wave pitch glide up, increasing intensity over 0.2 seconds, soft sparkle at the peak, no reverb, cold digital interface open sound, smooth fade out, futuristic UI
```

**Prompt 2 — Riser tecnológico:**
```
Quick ascending technological riser, pure tone gliding upward, crystalline brightness, minimal harmonics, precision sound design, UI open event, short and clean, 0.2 seconds duration, modern app interface
```

**Settings:** Duration=0.25s, Influence=70%, Looping=off

### 4.4 close (0.25s) — Contralto descendente

**Prompt 1 — Contralto puro:**
```
Short descending contralto tone, pitch falling smoothly, warm low mid-range, soft dark timbre, clean sine wave glide down, UI close event, no reverb, dry, 0.2 seconds, subtle and gentle, satisfying resolution
```

**Prompt 2 — Escuro tecnológico:**
```
Descending dark tone, pure low pitch landing, smooth downward glide, warm and cold contrast, technological UI close sound, minimal sustain, clean cutoff, 0.2 seconds, modern interface
```

**Settings:** Duration=0.25s, Influence=70%, Looping=off

### 4.5 whoosh (0.4s) — Movimento de ar com corpo

**Prompt 1 — Cinematográfico:**
```
Cinematic whoosh, air moving fast with body, bandpass filter sweep from low to mid, warm low end, smooth attack and decay, wide stereo, 0.4 seconds, no reverb, dry, transition sound effect, sci-fi interface
```

**Prompt 2 — Frio tecnológico:**
```
Cold technological whoosh, fast air movement, filtered sweep with subsonic body, clean attack, smooth tail, precision sound design, UI transition, 0.35 seconds, dry studio recording, no reverb, minimal
```

**Settings:** Duration=0.4s, Influence=60%, Looping=off

---

## 5. Tabela Resumo

| Sample | Duração | Influence | Tom | Caráter |
|---|---|---|---|---|
| `hover` | 0.1s | 80% | Agudo (8kHz) | Tick cristalino seco |
| `click` | 0.15s | 80% | Médio (cerâmica/metal) | Toque percussivo tátil |
| `open` | 0.25s | 70% | Agudo→médio ascendente | Riser brilho |
| `close` | 0.25s | 70% | Médio→grave descendente | Contralto fechamento |
| `whoosh` | 0.4s | 60% | Sub-grave→médio sweep | Movimento aéreo |

### Consistência de paleta sonora

Para uma família coesa, mantenha em TODOS os prompts:
- ❄️ **Ambiente:** `dry studio recording, no reverb`
- 🧊 **Textura:** `cold`, `clean`, `precision`
- 🎯 **Contexto:** `modern UI interface sound design`

---

## 6. Fluxo de Trabalho

```
1. Gere cada sample com 4 variações
2. Audite → escolha a melhor
3. Refine prompt se necessário, regenere
4. Download WAV (48kHz, 24-bit) — master archive
5. Converta para MP3 320kbps CBR (ffmpeg com loudnorm)
6. Normalize loudness para -18 LUFS
7. Nomeie exatamente: hover.mp3, click.mp3, open.mp3, close.mp3, whoosh.mp3
8. Salve em: assets/audio/sfx/
```

### FFmpeg pós-processamento

```bash
# WAV → normalized MP3 (uma passada só)
ffmpeg -i input.wav -af "loudnorm=I=-18:LRA=7:TP=-1" -b:a 320k output.mp3

# Verificar loudness
ffmpeg -i output.mp3 -af loudnorm=print_format=json -f null - 2>&1 | grep -E 'input_i|input_tp|input_lra'
```

**PowerShell (batch):**
```powershell
Get-ChildItem -Filter "*.wav" | ForEach-Object {
    $out = $_.BaseName + ".mp3"
    ffmpeg -i $_.FullName -af "loudnorm=I=-18:LRA=7:TP=-1" -b:a 320k $out -y
}
```

---

## 7. Referências

- Docs ElevenLabs SFX: https://elevenlabs.io/docs/overview/capabilities/sound-effects
- Guia de produto: https://elevenlabs.io/docs/eleven-creative/playground/sound-effects
- Promptomania: https://promptomania.com/models/elevenlabs/elevenlabs-sfx
- AIProductivity guide (30+ prompts): https://aiproductivity.ai/guides/elevenlabs-sound-effects-guide/
- SFX V2 + Soundboard: https://elevenlabsmagazine.com/elevenlabs-sfx-v2-soundboard-guide-2026/
