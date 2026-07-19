"""BaileysManager — Python-side lifecycle manager for Baileys subprocess.

Drop-in class for orchestrators. Handles:
- Starting Node.js Baileys as subprocess
- Health-check loop until WhatsApp connected
- QR code generation (first run / expired session)
- Graceful shutdown with session save

Usage:
    manager = BaileysManager(session_dir="./sessions/assessor1", porta=3100)
    manager.iniciar()
    client = manager.client
    # ... use client ...
    manager.encerrar()
"""

import os
import subprocess
import time
import signal
import base64
import requests
from typing import Optional


class BaileysManager:
    def __init__(self, session_dir: str = "./sessions/assessor1", porta: int = 3100):
        self.session_dir = session_dir
        self.porta = porta
        self.proc: Optional[subprocess.Popen] = None
        self.client = BaileysClient(base_url=f"http://localhost:{porta}")

    def _health(self) -> dict:
        try:
            r = requests.get(f"http://localhost:{self.porta}/health", timeout=2)
            return r.json()
        except Exception:
            return {"status": "offline"}

    def iniciar(self, timeout: int = 45) -> bool:
        os.makedirs(self.session_dir, exist_ok=True)

        # Resolve baileys_service.js path
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        js_path = os.path.join(script_dir, "baileys_service.js")
        if not os.path.exists(js_path):
            js_path = os.path.join(os.getcwd(), "baileys_service.js")

        # CRÍTICO: usar DEVNULL para stdout — PIPE enche o buffer e mata o Node
        self.proc = subprocess.Popen(
            ["node", js_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            env={
                **os.environ,
                "PORT": str(self.porta),
                "SESSION_DIR": os.path.abspath(self.session_dir),
                "ASSESSOR_NOME": os.environ.get("ASSESSOR_1_NOME", "Assessor"),
            },
        )

        # Aguarda servidor HTTP
        for _ in range(5):
            try:
                requests.get(f"http://localhost:{self.porta}/health", timeout=1)
                break
            except Exception:
                time.sleep(0.5)

        # Aguarda conexão WhatsApp (reutiliza sessão se creds.json existir)
        sessao_existe = os.path.exists(os.path.join(self.session_dir, "creds.json"))
        if sessao_existe:
            print("[BaileysManager] Sessão encontrada. Conectando sem QR...")

        for i in range(timeout):
            health = self._health()
            status = health.get("status", "offline")

            if status == "connected":
                print(f"[BaileysManager] ✅ Conectado em {i+1}s")
                return True

            if status == "awaiting_qr":
                if sessao_existe:
                    print("[BaileysManager] ⚠️ Sessão expirada — precisa de novo QR.")
                else:
                    print("[BaileysManager] 📱 Primeira execução — escaneie o QR.")
                self._salvar_qr(os.path.join(os.getcwd(), "qr_code.png"))
                # Aguarda scan
                for _ in range(timeout - i):
                    if self._health().get("status") == "connected":
                        return True
                    time.sleep(1)
                return False

            time.sleep(1)

        print(f"[BaileysManager] ❌ Timeout ({timeout}s)")
        return False

    def encerrar(self):
        if not self.proc:
            return
        try:
            self.proc.send_signal(signal.SIGTERM)
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()

    def _salvar_qr(self, output_path: str):
        try:
            r = requests.get(f"http://localhost:{self.porta}/qr", timeout=3)
            data = r.json()
            if "qr" in data:
                b64 = data["qr"].split(",", 1)[-1] if "," in data["qr"] else data["qr"]
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(b64))
        except Exception:
            pass

    def __enter__(self):
        self.iniciar()
        return self

    def __exit__(self, *args):
        self.encerrar()
