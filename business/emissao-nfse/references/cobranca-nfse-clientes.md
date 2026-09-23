# Envio da NFS-e ao cliente (cobrança) — histórico, molde e receita

Profundidade sob demanda da skill `emissao-nfse` (seção "Envio da NFS-e ao cliente").
Usar quando a demanda for "encaminhe/cobre a nota do <cliente>".

## 1 · Achar os envios anteriores (Gmail, `admin@idconsultoria.ai`)

Interpretador: `$HERMES_HOME/id-nfse-motor/.venv/bin/python` (tem `googleapiclient`);
token `$HERMES_HOME/google_token.json`.

Roteiro: `users().messages().list(q=..., maxResults=30)` → triagem com
`messages().get(format="metadata", metadataHeaders=["From","To","Subject","Date"])` →
leitura com `format="full"`, percorrendo `payload.parts` recursivamente para pegar corpo e
`filename` dos anexos.

Queries que funcionam:

- `<cliente>` (ex. `sergipetec`) — notas, propostas e avisos do cliente misturados.
- `"Nota Fiscal" newer_than:80d` — os envios de nota de qualquer cliente.
- `<dominio>.org.br` — restringe ao domínio do cliente.
- **Ler a última resposta do cliente na thread**: é onde ficam os pedidos do setor de
  compras (dados de Pix, CND Municipal) que o próximo envio já pode antecipar.

## 2 · Molde do e-mail de cobrança (última versão em uso)

- **Assunto:** `Nota Fiscal de <ordinal por extenso> parcela do contrato <Contrato>`
  (ex.: "Nota Fiscal de terceira parcela do contrato Artemishub").
- **Corpo sempre em texto puro, nesta estrutura:**

```
Prezados(as),

Conforme acordado e disposto no contrato, encaminhamos a Nota Fiscal eletrônica referente à <ordinal> parcela (<n>/<total>) do contrato <Contrato>, em anexo.

Dados da Nota Fiscal:
- Parcela: <n>/<total>
- Valor: R$ <valor>
- Competência: <MM/AAAA>
- Serviço: <descrição do serviço> (código <código> · CNAE <CNAE>)
- Município de prestação: Aracaju/SE
- Emitente: ID.TEAL Consultoria em Gestão Organizacional LTDA — CNPJ 54.569.818/0001-59

Dados para pagamento:
- Chave Pix (CNPJ): 54.569.818/0001-59

A NFS-e segue anexa para registro e processamento do pagamento. Ficamos à disposição para qualquer esclarecimento ou documentação adicional que o setor de compras demandar.

Atenciosamente,
ID Consultoria
admin@idconsultoria.ai · (79) 9600-6080
```

- Enviar como **thread novo** (os envios históricos não eram replies), do
  `admin@idconsultoria.ai`; a nota vai **apenas como anexo**.
- Nome do anexo versionado por parcela — nunca reutilizar o arquivo da parcela anterior.

## 3 · Clientes e padrões já usados

| Cliente | Destinatários | Contrato / assunto | Anexo (padrão) | Notas |
|---|---|---|---|---|
| SergipeTec (Sergipe Parque Tecnológico, CNPJ 06.938.508/0001-11) | `compra@sergipetec.org.br`, `asplan.sergipetec@sergipetec.org.br` | **Artemishub** (3 parcelas) | `NFS-e_<n>-<total>_Artemishub.pdf` | Serviço 0802 · CNAE 6204-0/00 ("Gestão do desenvolvimento de produto com IA para procura e seleção de editais de inovação"); o setor de compras pede a **CND Municipal** depois de receber a nota |
| Solution Master | `financeiro@solutionmaster.com.br` | **contrato de processos** (6 parcelas) | `NFS-e_<n>-<total> - Mapeamento de Processos Críticos.pdf` | Copiar contatos do projeto conforme a thread (`leonardo@`, `matheus@`) |

Cliente novo: acrescente a linha (tomador + CNPJ, destinatários, nome do contrato como vai
no assunto, padrão do anexo, ordinal/total de parcelas).

## 4 · Envio com anexo (receita)

O CLI `gapi gmail send` não tem flag de anexo — montar o MIME no Python:

```python
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
msg = MIMEMultipart()
msg["From"] = '"Principal ID Consultoria" <admin@idconsultoria.ai>'
msg["To"] = "compra@sergipetec.org.br, asplan.sergipetec@sergipetec.org.br"
msg["Subject"] = SUBJECT
msg.attach(MIMEText(BODY, "plain", "utf-8"))
part = MIMEApplication(open(PDF, "rb").read(), _subtype="pdf")
part.add_header("Content-Disposition", "attachment", filename="NFS-e_3-3_Artemishub.pdf")
msg.attach(part)
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
service.users().messages().send(userId="me", body={"raw": raw}).execute()
```

Boas práticas que valeram:

- Script com `--dry-run` que imprime `getProfile()`, destinatários, assunto, caminho e
  tamanho do anexo — rodar o dry-run na frente do principal; depois do ok, executar o mesmo
  script sem a flag.
- Guardar script + PDF renomeado em `$HERMES_HOME/work/nfse-<ano>/` — a parcela seguinte
  reaproveita.
- NFS-e do WebISS: PDF de uma página, ~380 KB.
- Ler a nota com `pdftotext -layout` antes de copiar valor/competência para o corpo.
