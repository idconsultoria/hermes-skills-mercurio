"""
Configuracao multi-assessor com variaveis de ambiente prefixadas.

Cada assessor tem seu proprio prefixo (ASSESSOR_1_, ASSESSOR_2_, ...).
Isso permite isolar credenciais, URLs de servico, pastas do Drive, etc.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AssessorConfig:
    """Configuracao de um assessor especifico."""

    def __init__(self, prefixo: str):
        self.prefixo = prefixo
        self.nome = self._env("NOME", f"Assessor {prefixo}")
        self.gemini_api_key = self._env("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError(f"[{prefixo}] GEMINI_API_KEY nao definida")
        self.google_credentials_json = os.environ.get(f"{prefixo}_GOOGLE_CREDENTIALS_JSON")
        self.id_pasta_pendentes = self._env("ID_PASTA_PENDENTES")
        self.id_pasta_processados = self._env("ID_PASTA_PROCESSADOS")
        self.id_doc_personalizacao = self._env("ID_DOC_PERSONALIZACAO", "")
        self.id_planilha_clientes = self._env("ID_PLANILHA_CLIENTES")
        self.nome_aba_clientes = self._env("NOME_ABA_CLIENTES", "Clientes")
        self.nome_aba_logs = self._env("NOME_ABA_LOGS", "Registros")
        self.whatsapp_service_url = self._env("WHATSAPP_SERVICE_URL", "http://localhost:3100")
        self.envios_por_execucao = int(os.environ.get("ENVIOS_POR_EXECUCAO", "8"))

    def _env(self, chave: str, default: Optional[str] = None) -> str:
        valor = os.environ.get(f"{self.prefixo}_{chave}")
        if valor is None:
            if default is not None:
                return default
            raise ValueError(f"[{self.prefixo}] {self.prefixo}_{chave} nao definida")
        return valor

    def get_google_credentials(self) -> dict:
        if self.google_credentials_json:
            return json.loads(self.google_credentials_json)
        cred_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "service_account.json")
        if os.path.exists(cred_path):
            with open(cred_path) as f:
                return json.load(f)
        raise FileNotFoundError(f"[{self.prefixo}] Credenciais Google nao encontradas")


def listar_assessores_ativos() -> list[str]:
    ativos = os.environ.get("ASSESSORES_ATIVOS", "1")
    return [a.strip() for a in ativos.split(",") if a.strip()]


def carregar_config(prefixo: str) -> AssessorConfig:
    return AssessorConfig(prefixo)
