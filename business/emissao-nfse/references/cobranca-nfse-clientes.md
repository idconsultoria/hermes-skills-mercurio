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
| Solution Master | `financeiro@solutionmaster.com.br` (cc `matheus@solutionmaster.com.br`, comercial `Junior Bomfim`) | **SM1 — Mapeamento de Processos Críticos** (6 parcelas) | `NFS-e_<n>-<total> - Mapeamento de Processos Críticos.pdf` | Pagamento: **Matheus Cerqueira** (Coordenador Financeiro) é o interlocutor do Pix; **Junior Bomfim** (Gerente de Negócios) é a escalada comercial. O Pix do cliente entra no Inter do ID como `"Solution Services"`. Padrão declarado pelo financeiro: *pagamento no dia 25 de cada mês* — é o marco de vencimento |

Cliente novo: acrescente a linha (tomador + CNPJ, destinatários, nome do contrato como vai
no assunto, padrão do anexo, ordinal/total de parcelas, interlocutor financeiro e como o
pagante aparece no extrato do banco).

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
- **Assinatura = `ID Consultoria`, seca.** Sem sufixo de papel, sem "— Principal", sem nome
  do sócio. Vale para o corpo e para o cabeçalho `From` (mesma string nos dois, senão o
  e-mail chega assinado diferente do que o principal aprovou).

## 5 · Cobrança de parcela vencida (pós-envio da nota)

O outro lado do mesmo ciclo: a nota foi, o prazo passou, o Pix não caiu. Não é reenvio de
NFS-e — é cobrança. Treat como tarefa de classe, não caso isolado.

### 5.1 Sequência

1. **Localizar a thread da NFS-e** (seção 1) e confirmar os três fatos antes de cobrar:
   destinatário, valor e **data de vencimento**. A `Date:` do e-mail às vezes está em outro
   fuso que a data real de envio — use `internalDate` (ms) do Gmail para o carimbo correto.
2. **Confirmar o atraso em duas fontes independentes**, nunca só no e-mail:
   - **Extrato do banco** (skill `inter-api-id-consultoria`) procurando o crédito do pagante
     no período desde o vencimento; a API do Inter **limita requisições (429)** — reuse a
     mesma consulta para as duas checagens em vez de chamar o extrato várias vezes seguidas.
   - **Planilha de engagements** (`recebimentos`): a parcela deve estar "Por receber" com a
     data prevista = vencimento.
3. **Montar o texto, mostrar ao principal, esperar o ok.** E-mail a cliente externo tem
   gate; cobrança também.
4. **Enviar como reply da thread da NFS-e** (`In-Reply-To` + `References` do cabeçalho da
   nota, destinatários herdados dela), assunto `Re: <assunto da nota> — parcela <n>/<total>
   em atraso`.
5. **Deixar a próxima cobrança agendada** (seção 5.3), com o texto já aprovado.

### 5.2 Trava obrigatória: consultar o extrato ANTES de cobrar

Cobrar sem ler o extrato é o erro caro — sai e-mail pedindo dinheiro que já entrou, e a
perda de credibilidade com o cliente é do tamanho do contrato. Estrutura do verificador
(uma linha por status, para o chamador decidir):

- `PAGO <data> <valor> <descrição>` → **não cobra**; avisar que o dinheiro caiu e que a
  planilha ainda precisa ser atualizada.
- `NAO_PAGO` → cobra.
- `ERRO <motivo>` → **não cobra** e **não conclui nada**: reportar ao principal para
  conferência manual. Falha de leitura não é evidência de inadimplência.

O verificador é read-only e separado do script que envia: assim ele pode ser reexecutado a
qualquer momento (inclusive em teste) sem risco de disparo.

### 5.3 Cobrança programada (cron)

- Agendar em **BRT, com offset explícito** no ISO do one-shot (`2026-09-28T08:00:00-03:00`).
  O host roda em UTC e com `timezone: ''` no config — expressão `0 11 * * *` equivale a 08h
  BRT, mas o ISO com offset não depende dessa conta.
- O job carrega `script` (que checa e envia) e um `prompt` que **apenas relata** o stdout.
  Escreva no prompt: *"NÃO rode o script de novo e NÃO envie e-mails — a cobrança já foi
  tentada pelo script nesta execução"*. Sem essa frase o agente duplica o disparo.
- **Rodar o script agendado com o ambiente mínimo** antes de confiar nele:
  `env -i HOME=/root PATH=/usr/bin:/bin HERMES_HOME=$HERMES_HOME ./script.sh` — é assim que
  se pega dependência de variável que só existe na sessão.
- O `prompt` do cron roda em sessão nova, sem histórico: repetir o contexto essencial
  (cliente, contrato, parcela, valor, vencimento, thread) e a instrução de nunca afirmar
  pagamento sem o que estiver no stdout.
- Prefira one-shot + reagendar conforme a resposta, em vez de loop semanal: o prazo de
  resposta de um financeiro é de dias, e cada semana de silêncio pede um tom diferente.

### 5.4 Molde do texto de cobrança (aprovado pelo principal)

Fiel ao registro dos envios anteriores (mesma frase de tom, sem "Prezados" genérico,
saudação pelo horário do disparo):

```
< Bom dia | Boa tarde | Boa noite >, prezado <nome do financeiro>.

Em <DD de MMMM de AAAA> enviamos a Nota Fiscal da parcela <n>/<total> do contrato <Contrato>, no valor de R$ <valor>, com vencimento em <DD/MM/AAAA>.

Até o momento não localizamos a confirmação do pagamento: o prazo venceu em <DD/MM/AAAA>< com N dias de atraso> e o valor segue sem confirmação no nosso controle.

Para regularizar, segue novamente a chave Pix:
<chave>

Se o pagamento já foi feito ou está em processamento, por favor, envie a comprovação para que lancemos e atualizemos o controle.

Atenciosamente,
ID Consultoria
```

Elementos que o cliente reconhece: a data de envio da nota, o valor, o vencimento, a chave
Pix de novo e o pedido de comprovação. Calcule "N dias de atraso" e a saudação em runtime
(BRT) — a cobrança pode disparar dias depois de montada.

### 5.5 Quando oferecer cobrança automática ao cliente

Antes de mandar, pergunte uma vez qual das três ele quer — e respeite a resposta:

1. aprovar o texto e disparar agora;
2. o cron dispara sozinho, direto na caixa do financeiro do cliente;
3. o cron só lembra o principal, que cobra na hora.

Oferecer "eu agendo e você aprova" como default só é seguro se o principal escolher a 2 —
aprovação do texto **antes** de agendar é o que autoriza o disparo automático.
