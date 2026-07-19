"""
Cliente HTTP Python para o servico Baileys (WhatsApp Web).

Substitui a integracao Z-API por um bridge local Node.js usando Baileys.
O servico Baileys expoe uma REST API compativel com a Z-API,
facilitando a migracao sem alterar a logica de negocio.

Endpoints esperados no servico Baileys:
    GET  /health                  → {"status": "connected", ...}
    GET  /phone-exists/{telefone}  → {"exists": bool, "lid": str}
    POST /send-text                → {"phone": str, "message": str}
    POST /send-document/pdf       → {"phone": str, "document": "data:...base64", "fileName": str}
"""

import base64
import requests
from typing import Optional


class BaileysClient:
    """Cliente HTTP para o servico Baileys (substituto da Z-API)."""

    def __init__(self, base_url: str = "http://localhost:3100", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _get(self, path: str) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict) -> dict:
        resp = self.session.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict:
        """Verifica status da conexao WhatsApp."""
        return self._get("/health")

    def phone_exists(self, telefone: str) -> Optional[str]:
        """
        Verifica se o numero tem WhatsApp e retorna o @lid.
        Retorna None se o numero nao existir no WhatsApp.

        Args:
            telefone: Numero no formato DDI+DDD+Numero (ex: 5511999999999)

        Returns:
            @lid do WhatsApp ou None
        """
        try:
            dados = self._get(f"/phone-exists/{telefone}")
            if dados.get("exists"):
                lid = dados.get("lid")
                if lid:
                    return lid
                return telefone
            return None
        except Exception as e:
            print(f"[-] Erro ao verificar numero {telefone}: {e}")
            return None

    def send_text(self, phone: str, message: str) -> bool:
        """Envia mensagem de texto via WhatsApp."""
        try:
            self._post("/send-text", {"phone": phone, "message": message})
            return True
        except Exception as e:
            print(f"[-] Erro ao enviar mensagem: {e}")
            return False

    def send_pdf_document(self, phone: str, pdf_path: str, file_name: str) -> bool:
        """Envia documento PDF via WhatsApp."""
        try:
            with open(pdf_path, "rb") as f:
                pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
            self._post("/send-document/pdf", {
                "phone": phone,
                "document": f"data:application/pdf;base64,{pdf_base64}",
                "fileName": file_name,
            })
            return True
        except Exception as e:
            print(f"[-] Erro ao enviar PDF: {e}")
            return False

    def send_pdf_and_text(self, telefone: str, pdf_path: str, pdf_name: str, message: str) -> bool:
        """Fluxo completo: valida numero, envia PDF, envia mensagem de texto."""
        identificador = self.phone_exists(telefone)
        if not identificador:
            print(f"[-] Numero {telefone} nao validado. Envio cancelado.")
            return False
        if not self.send_pdf_document(identificador, pdf_path, pdf_name):
            return False
        return self.send_text(identificador, message)
