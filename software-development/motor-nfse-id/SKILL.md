---
name: motor-nfse-id
description: "Resume/update the ID NFS-e emission motor (living state)."
version: 1.0.0
author: Mercúrio (ID Consultoria)
license: ID-Interno
category: software-development
type: Orchestrator
timestamp: 2026-08-18T00:00:00Z
metadata:
  hermes:
    tags: [nfse, nfelib, id, fiscal, emissao, aracaju]
    related_skills: [deep-research, google-workspace, product-pipeline]
---

# Motor NFS-e Nacional — ID Consultoria (estado vivo)

> Esta skill é o **estado atual da implantação do motor de emissão de NFS-e da ID**.
> É um **documento vivo**: a cada avanço/retomada, ATUALIZE o "ESTADO ATUAL (data)" e as
> pendências. SEMPRE carregue esta skill antes de tocar no motor.

## When to Use
- Carregar SEMPRE que o assunto for emitir/criar NFS-e da ID, o motor `id-nfse-motor`,
  o cron da alíquota ISS, o certificado A1/e-CNPJ, ou retomar a implementação.
- Ao concluir/avançar uma etapa do motor, atualizar o "ESTADO ATUAL" e as pendências aqui.

## ESTADO ATUAL (2026-08-30) — RECRIADO (código-fonte perdido na migração)
**Status geral: motor recriado em `/opt/mercurio-data/id-nfse-motor/` (Fase 1 gera DPS).
Pausado para emissão em produção até A1 renovado.**

- **Motivo do replay:** na migração `/opt/data → /opt/mercurio-data` o código-fonte do
  motor (e do iData) NÃO veio — só restaram os `.venv` e `__pycache__`, nos dois lados
  (container atual e host Oracle). O repo `idconsultoria/iData` existe no GitHub e foi
  re-clonado; o motor NFS-e **não está em nenhum repo da org** → foi **recriado** a partir
  desta skill + `emissao-nfse`/`dps-nfelib-mapping.md`.
- Arquivos recriados: `emitir_nfse.py` (gerador DPS fiel ao binding v1_0), `requirements.txt`
  (signxml>=4.0.0 — resolvido conflito c/ pynfse-nacional 0.9.5), `Dockerfile`, `DEPLOY.md`,
  `dados/aliquota_iss.json` (exemplo), `scripts/buscar_aliquota_iss.py` (backend do cron ISS).
- **Build da imagem Docker: PENDENTE** (daemon Docker não acessível do container → Hermes
  canônico no Oracle host, `docker build -t id-nfse-motor:1.0.0 .`).
- Emissão real depende de **A1 válido** para assinar + transmitir (Fase 2, atrás de gate).
- **Instalação no Termux (aprendido 30/08):** `uv` baixa CPython genérico e compila pandas
  do sdist (lento, >1000s). Usar o **Python do próprio Termux** (`/data/data/com.termux/
  files/usr/bin/python`, 3.14) com venv — pega wheels e instala em segundos. Ou `pip` do
  Termux. Não confiar em wheel manylinux p/ `aarch64-linux-android`.

## Pendências (ordem de desbloqueio)
1. **[BLOQUEADOR] Certificado A1 (e-CNPJ):** EXPIrado em 25/04/2026; renovação ~R$180/ano.
   Renovação passa pela **AAD/contabilidade** (boleto + validação). Senha NUNCA em chat →
   env/volume seguro. Principal pediu **pausa até ter o certificado**.
2. **Build da imagem:** `docker build -t id-nfse-motor:1.0.0 .` no Oracle host (via Hermes canônico).
3. **Dados fiscais p/ 1ª nota:** Inscrição Municipal (IM) do ISS em Aracaju + cNBS do 85.99-6-04.
4. **Fase 2 (assinatura+transmissão):** habilitar `erpbrasil.assinatura` (A1) +
   `pynfse-nacional` (webservice). Atrás do **gate de aprovação** — emissão é ato fiscal irreversível.

## Enquadramento da ID (da base)
- **ID.TEAL CONSULTORIA EM GESTÃO ORGANIZACIONAL LTDA** · CNPJ 54.569.818/0001-59 · LTDA Microempresa
  · Simples Nacional (`opSimpNac=2`) · atividade 85.99-6-04 (serviço → ISS/NFS-e).
- **Aracaju/SE (IBGE 2800308) adota protocolo NFS-e NACIONAL** (Ambiente Nacional=Sim) →
  motor usa padrão **DPS via nfelib** (NÃO conector municipal). Webiss entra por
  **usuário/senha, não por certificado** → emissão manual segue ok mesmo com A1 vencido.

## Estrutura / caminhos
- Motor em **`/opt/data/id-nfse-motor/`**:
  - `emitir_nfse.py` — gera DPS (CLI; homologação por padrão `--tpAmb 2`). Validado.
  - `Dockerfile` (multi-stage ARM64, python:3.13-slim, não-root) · `requirements.txt` (pinado) ·
    `DEPLOY.md` (build/uso/pendências) · `dados/` (alíquota) · `scripts/` (buscador ISS).
- **Cron `Alíquota ISS mensal (ID)`** (job `3dfe43219f1b`, dia 5 10h BRT, **job de AGENTE com
  fallback**): busca "ALÍQUOTA DE ISS MM.YYYY" em `gustavo.idteal@gmail.com`, grava
  `/opt/data/id-nfse-motor/dados/aliquota_iss.json` (o motor lê p/ `pAliq`).
  Ex.: 2,01% (08/2026). Script: `/opt/data/scripts/buscar_aliquota_iss.sh`.

## Acessos / infra (para o motor)
- Venv do motor: `/opt/data/id-nfse-motor/.venv` (nfelib 2.5.2, pynfse-nacional 0.9.5,
  erpbrasil.*, xsdata, signxml, zeep, lxml).
- Google: token **`/opt/data/google_token.gustavo_idteal.json`** (conta do ISS/contabilidade);
  primário `google_token.json` = **admin@idconsultoria.ai**. Venv Google: `/opt/data/venvs/google`.
- **Daemon Docker NÃO acessível do container do Mercúrio** → build de imagem no Oracle host.

## Fase 2 — como habilitar (quando houver A1 válido)
1. Disponibilizar `.pfx` + senha como **secret/volume** (nunca em chat/arquivo texto).
2. Carregar `erpbrasil.assinatura` (assinar DPS com A1) e `pynfse-nacional`/`erpbrasil.edoc`
   p/ transmissão ao ambiente nacional; homologar (`tpAmb=2`) com a chave DPS REAL.
3. Validar chave/Id do DPS em homologação (hoje é identificador interno).
4. Manter o **gate**: emissão em produção só com ok explícito do principal.

## Pitfalls (aprendidos)
- `web_search` com aspas em nome próprio trava o backend; usar extração direta (gov.br/GitHub).
- **A1 quase nunca vem por email** — é gerado localmente (não procurar só em caixa de email).
- `cp -n` NÃO sobrescreve (clobber) — usar `-f` ao restaurar token primário.
- Regex do ISS: corpo usa `*agosto*` (marcador) → `mês de[^\w]*(\w+)` na extração.
- Cron `script` deve ser caminho RELATIVO ao dir de scripts (aqui `/opt/data/scripts`), não absoluto.
- OAuth Google: token é de UMA conta por vez; guardar contas em arquivos separados
  (`google_token.<conta>.json`) para não clobber.

## Verificação / retomada
- Conferir `ESTADO ATUAL` (data) no topo antes de agir.
- Se pausado por certificado, o desbloqueio é: principal traz `.pfx` renovado + senha segura.
- Ao retomar e concluir uma etapa, **atualize esta skill** (patche o "ESTADO ATUAL" e pendências).
