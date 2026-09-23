#!/usr/bin/env python3
"""Transcreve um audio pelo Gemini com fallback de modelos (apoio ao STT do Hermes).

Quando a transcricao automatica de uma nota de voz falha, a mensagem chega como:
    [voice message could not be transcribed automatically; the audio is available at:
     <HERMES_HOME>/cache/audio/audio_<hash>.ogg]
O audio existe em disco e pode ser transcrito por aqui.

Uso:
    python3 transcrever_audio_com_fallback.py <audio> [--language pt-BR] [--out arquivo.txt]

- Le GOOGLE_API_KEY do ambiente ou de /opt/data/.env (mesmo padrao de
  <HERMES_HOME>/scripts/gemini-stt.py).
- Envia o audio inline (base64, < 20MB) e ITERA pela lista de MODELOS: modelo de
  transcricao fixo e ponto unico de falha (HTTP 503 por alta demanda, timeout).
- Imprime a transcricao no stdout; com --out, grava tambem no arquivo.
- Sai 1 com o erro real no stderr se todos os modelos falharem.

Nunca invente transcricao: a saida e sempre o texto devolvido pela API.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

# 1o = modelo do provider configurado em stt.providers (config.yaml); o resto e a esteira de fallback.
MODELOS = [
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
]
TENTATIVAS = 3
TIMEOUT = 110
SLEEP = 4
ENV_PATH = "/opt/data/.env"

MIME_MAP = {
    ".ogg": "audio/ogg", ".oga": "audio/ogg", ".opus": "audio/ogg",
    ".mp3": "audio/mpeg", ".mpeg": "audio/mpeg", ".mpga": "audio/mpeg",
    ".wav": "audio/wav", ".aiff": "audio/aiff", ".aif": "audio/aiff",
    ".aac": "audio/aac", ".m4a": "audio/mp4", ".mp4": "audio/mp4",
    ".flac": "audio/flac", ".webm": "audio/webm",
}


def load_api_key():
    key = os.environ.get("GOOGLE_API_KEY", "")
    if key:
        return key
    try:
        with open(ENV_PATH) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("GOOGLE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return ""


def guess_mime(path):
    return MIME_MAP.get(os.path.splitext(path)[1].lower(), "audio/ogg")


def transcrever(audio_path, api_key, language):
    with open(audio_path, "rb") as fh:
        audio_b64 = base64.b64encode(fh.read()).decode("ascii")

    lang_hint = (
        f" O idioma provavel e '{language}', mas transcreva no idioma falado."
        if language else ""
    )
    prompt = (
        "Transcreva o audio integralmente, exatamente como falado, sem comentarios, "
        "sem markdown e sem adicionar nada." + lang_hint
    )
    mime = guess_mime(audio_path)

    for modelo in MODELOS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent"
        )
        payload = {
            "contents": [{"parts": [
                {"inline_data": {"mime_type": mime, "data": audio_b64}},
                {"text": prompt},
            ]}],
            "generationConfig": {"temperature": 0},
        }
        for tentativa in range(1, TENTATIVAS + 1):
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
                texto = "".join(p.get("text", "") for p in parts).strip()
                if texto:
                    return texto, modelo
                print(f"{modelo}: resposta sem texto", file=sys.stderr)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")[:200].replace("\n", " ")
                print(f"{modelo} tentativa {tentativa}: HTTP {exc.code} {body}", file=sys.stderr)
            except Exception as exc:  # timeout, rede, JSON invalido
                print(f"{modelo} tentativa {tentativa}: {exc}", file=sys.stderr)
            if tentativa < TENTATIVAS:
                time.sleep(SLEEP)
    return "", None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audio", help="caminho do audio de entrada")
    ap.add_argument("--language", default="pt-BR", help="dica de idioma (opcional)")
    ap.add_argument("--out", default="", help="arquivo para gravar a transcricao")
    args = ap.parse_args()

    if not os.path.exists(args.audio):
        print(f"Audio nao encontrado: {args.audio}", file=sys.stderr)
        return 1

    api_key = load_api_key()
    if not api_key:
        print("GOOGLE_API_KEY nao encontrada (env nem /opt/data/.env)", file=sys.stderr)
        return 1

    texto, modelo = transcrever(args.audio, api_key, args.language)
    if not texto:
        print("Falha ao transcrever: todos os modelos da lista falharam.", file=sys.stderr)
        return 1

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(texto)
        print(f"# transcrito por {modelo} -> {args.out}", file=sys.stderr)
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
