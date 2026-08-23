---
name: emissao-nfse
description: "Emitir NFS-e/NF-e da ID via motor nfelib (NFS-e Nacional)."
category: business
type: ToolIntegration
timestamp: 2026-08-18T00:00:00Z
---

# Emissão de NFS-e / NF-e (ID Consultoria)

Emissão de **nota fiscal eletrônica de serviço (NFS-e)** da ID, via motor open source
(`nfelib`+`xsdata`) no padrão **NFS-e Nacional**. Contém o enquadramento fiscal da ID, a
decisão de arquitetura (Aracaju = protocolo NACIONAL, não conector municipal), o uso da CLI
do motor e a lista de pendências fiscais reais.

## Quando usar
- Emitir NFS-e da ID para um cliente (serviço/treinamento/consultoria).
- Integrar emissão no próprio produto/automação da ID.
- Retomar/validar o motor (build da imagem, assinatura, homologação).

## Enquadramento fiscal da ID (confirmado na base)
- **ID.TEAL CONSULTORIA EM GESTÃO ORGANIZACIONAL LTDA** · CNPJ 54.569.818/0001-59
- LTDA **Microempresa** (LC 123/2006) → **Simples Nacional** (`opSimpNac=2`)
- Atividade principal 85.99-6-04 (treinamento/consultoria) → **serviço (ISS, NFS-e)**.
  NF-e (ICMS/estadual) só se vender mercadoria física.
- Município de prestação dominante: **Aracaju/SE (IBGE 2800308)** — presta serviço em
  múltiplos municípios; emitir no município do serviço.

## Decisão de arquitetura (a mais importante)
- **Aracaju (2800308) está no Ambiente NFS-e NACIONAL** (confirmado: "Amb. Nacional = Sim",
  Emissor Nacional UI = Não). O "Webiss" é só a interface municipal por cima do padrão
  nacional.
- → **Motor usa o padrão NFS-e Nacional (DPS via `nfelib`)**, NÃO conector municipal
  (Betha/Ginfes/DSF/etc.). Escala para outros municípios aderentes e já segue a reforma
  tributária (IBS/CBS, CNPJ alfanumérico). Conector municipal = reserva, nunca default.

## Motor
- **Local:** `/opt/data/id-nfse-motor/`
  - `emitir_nfse.py` — CLI que monta a DPS (nfelib) e serializa XML (xsdata), round-trip valida.
  - `requirements.txt` — stack pinada (nfelib 2.5.2, pynfse-nacional 0.9.5, erpbrasil.*,
    xsdata, signxml, zeep, lxml).
  - `Dockerfile` — multi-stage otimizado, ARM64, runtime `python:3.13-slim`, não-root, HEALTHCHECK.
  - `DEPLOY.md` — build/uso/pendências.
- **Uso:**
  ```
  ./emitir_nfse.py emit --tom-nome "X Ltda" --tom-cnpj 01234567000189 \
    --tom-cep 49020090 --tom-logradouro "Av. Rio Branco" --tom-nro 250 --tom-bairro Centro \
    --servico "Consultoria em gestão e aumentação de processos" \
    --valor 4850.00 --serie 00001 --ndps 1            # default tpAmb=2 (homologação)
  ```
- Build da imagem: o daemon Docker **não é acessível do container do Mercúrio** — o Hermes
  canônico builda no Oracle host (`docker build -t id-nfse-motor:1.0.0 .`, ver DEPLOY.md).

## Fluxo de emissão (gate obrigatório)
1. Coletar tomador, serviço, valor, competência, série/nDPS.
2. Validar contra perfil fiscal ID (serviço/ISS) e, se aplicável, KB do cliente.
3. **Gate:** apresentar resumo e exigir ok explícito antes de homologação/produção.
   Homologação (`tpAmb=2`) por padrão.
4. Gerar DPS → (Fase 2, com A1) assinar via `erpbrasil.assinatura` + transmitir via
   `pynfse-nacional` → arquivar XML autorizado + protocolo.

## Pendências reais (bloqueam a 1ª nota em produção)
1. **Certificado A1 (e-CNPJ)**: NÃO está em email/Drive da ID — está num PC pessoal do
   principal. Guardar a **senha** em env/volume seguro, **nunca em chat/texto plano**.
2. **Inscrição Municipal (IM)** do ISS de Aracaju — não está na base.
3. **cNBS / cTribMun / alíquota ISS** de Aracaju p/ 85.99-6-04 — placeholders hoje.
4. **Chave DPS (Id)** — hoje identificador interno; validar layout correto em homologação.

## Pitfalls
- **A1 quase nunca chega por email**: o `.pfx` é gerado localmente na emissão. Buscar email
  como fonte do A1 é via morta (o Drive da ID só tinha certificados de EVENTO + PDFs de
  NFS-e, não o A1). Verificar email/Drive, mas já planejar o A1 vindo da máquina do principal.
- **Bug python em builder de dataclass**: `cfg.get("campo", default)` **não** aplica o
  default quando o campo existe com valor `None` (ex.: argparser injeta `None`) →
  `cfg.get("x") or default` (ou `"" if not ...`). Padrão recorrente ao montar objetos
  xsdata a partir de dict.
- **Simples Nacional**: `opSimpNac=2`; não preencher na confiança de default genérico.
- Senha do certificado nunca em arquivo de config versionado nem em relatório.

## Referências
- `references/dps-nfelib-mapping.md` — árvore de classes/campos do binding NFS-e Nacional
  (`dps_v1_00`, `tipos_complexos_v1_00`) + DPS de exemplo, para estender o motor sem
  redescobrir.
