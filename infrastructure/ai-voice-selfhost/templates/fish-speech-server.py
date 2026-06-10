#!/usr/bin/env python3
"""FastAPI server wrapping s2.cpp (Fish Audio S2 Pro GGUF) — multi-quant.

Template for Pattern B — C++ Native Inference via subprocess.
Copy to selfhost/<project>/server/server.py and adapt.

Supports multiple GGUF quantizations via the `model` field in the request.
Also supports voice cloning via `prompt_audio` + `prompt_text` fields.

Endpoints:
  GET  /health                — health check with per-model status
  POST /v1/audio/speech       — OpenAI-compatible TTS + voice cloning
  GET  /v1/models             — available quantizations
"""

import os
import subprocess
import tempfile
import time
import logging
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
logger = logging.getLogger("s2-server")

S2_BIN = os.environ.get("S2_BIN", "/app/s2.bin")
TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", "/app/models/tokenizer.json")
MODELS_DIR = os.environ.get("MODELS_DIR", "/app/models")
INFERENCE_TIMEOUT = int(os.environ.get("INFERENCE_TIMEOUT", "600"))

# ── Multi-quant model registry ────────────────────────────────────────
MODEL_REGISTRY = {
    "s2-pro-q8_0": {
        "path": os.environ.get("MODEL_Q8_0", f"{MODELS_DIR}/s2-pro-q8_0.gguf"),
        "quant": "q8_0", "size_gb": 5.3,
    },
    "s2-pro-q6_k": {
        "path": os.environ.get("MODEL_Q6_K", f"{MODELS_DIR}/s2-pro-q6_k.gguf"),
        "quant": "q6_k", "size_gb": 4.5,
    },
    "s2-pro-q5_k_m": {
        "path": os.environ.get("MODEL_Q5_K_M", f"{MODELS_DIR}/s2-pro-q5_k_m.gguf"),
        "quant": "q5_k_m", "size_gb": 3.8,
    },
}

DEFAULT_MODEL = "s2-pro-q8_0"

app = FastAPI(title="Fish Speech S2 Pro (GGUF)", version="2.1.0")


class SpeechRequest(BaseModel):
    model: str = "s2-pro"
    input: str
    voice: str = "0"
    response_format: str = "wav"
    prompt_audio: Optional[str] = None   # path inside container for voice cloning
    prompt_text: Optional[str] = None    # exact transcription of the reference audio


def _resolve_model(model_id: str) -> tuple[str, dict]:
    """Resolve model_id to (path, metadata). Falls back to default."""
    if model_id in MODEL_REGISTRY:
        info = MODEL_REGISTRY[model_id]
        if os.path.exists(info["path"]):
            return info["path"], info
    fallback_path = os.path.join(MODELS_DIR, f"{model_id}.gguf")
    if os.path.exists(fallback_path):
        return fallback_path, {"quant": model_id, "size_gb": 0}
    fallback_info = MODEL_REGISTRY[DEFAULT_MODEL]
    if not os.path.exists(fallback_info["path"]):
        raise HTTPException(503, f"Default model {DEFAULT_MODEL} not found")
    return fallback_info["path"], fallback_info


@app.get("/health")
async def health():
    models_status = {}
    for mid, info in MODEL_REGISTRY.items():
        models_status[mid] = {"exists": os.path.exists(info["path"])}
    return {
        "status": "ok",
        "s2_binary": os.path.exists(S2_BIN) and os.access(S2_BIN, os.X_OK),
        "tokenizer": os.path.exists(TOKENIZER_PATH),
        "default_model": DEFAULT_MODEL,
        "models": models_status,
    }


@app.post("/v1/audio/speech")
async def synthesize(req: SpeechRequest):
    for name, path in [("s2 binary", S2_BIN), ("tokenizer", TOKENIZER_PATH)]:
        if not os.path.exists(path):
            raise HTTPException(503, f"{name} not found at {path}")

    model_path, model_info = _resolve_model(req.model)

    t0 = time.time()
    text = req.input

    if req.voice and req.voice not in ("0", "auto", ""):
        text = f"[{req.voice}] {text}"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_path = tmp.name

    try:
        # Build s2 args — voice cloning via --prompt-audio if provided
        s2_args = [S2_BIN, "-m", model_path, "-t", TOKENIZER_PATH,
                   "--text", text, "-o", output_path]
        # ⚠️ prompt_text is REQUIRED when prompt_audio is set.
        # s2.cpp returns "prompt audio was provided without prompt text"
        # if -pa is passed without -pt. Always provide both together.
        if req.prompt_audio:
            if not os.path.exists(req.prompt_audio):
                raise HTTPException(400, f"prompt_audio not found: {req.prompt_audio}")
            pt = req.prompt_text or "Default reference text for voice cloning."
            s2_args.extend(["-pa", req.prompt_audio, "-pt", pt])

        result = subprocess.run(
            s2_args,
            capture_output=True,
            timeout=INFERENCE_TIMEOUT,
        )

        if result.returncode != 0:
            raise HTTPException(
                500, f"s2 error (code {result.returncode}): {result.stderr.decode()[:500]}"
            )

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
            raise HTTPException(500, "s2 produced empty output")

        elapsed = time.time() - t0
        with open(output_path, "rb") as f:
            data = f.read()

        logger.info(f"OK {len(data)}B in {elapsed:.1f}s [{model_info['quant']}]")
        return Response(
            content=data,
            media_type="audio/wav",
            headers={
                "X-Gen-Time": f"{elapsed:.1f}",
                "X-Model": model_info["quant"],
            },
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"s2 timed out after {INFERENCE_TIMEOUT}s")
    except Exception as e:
        logger.exception("inference failed")
        raise HTTPException(500, str(e))
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


@app.get("/v1/models")
async def list_models():
    available = []
    for mid, info in MODEL_REGISTRY.items():
        available.append({
            "id": mid, "object": "model",
            "quant": info["quant"], "size_gb": info["size_gb"],
            "available": os.path.exists(info["path"]),
        })
    return {"object": "list", "data": available}
