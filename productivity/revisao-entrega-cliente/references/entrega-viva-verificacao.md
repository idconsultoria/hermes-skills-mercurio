# Verificar a entrega viva (site/deploy) contra a fonte de verdade

Receitas para a etapa 6 da revisão. Tudo read-only.

## 1. Inventariar os deploys já publicados

Sessões e notas guardam as URLs. Extraia **todas** e compare com o que o repo atual publica:

```sql
-- no state.db do perfil que tocou o projeto (ver skill hermes-session-forensics)
SELECT session_id, count(*), min(timestamp) FROM messages
 WHERE content LIKE '%vercel.app%' GROUP BY 1 ORDER BY 2 DESC;
```

Em Python, colha os domínios distintos com `re.findall(r'[a-z0-9\-\.]+\.vercel\.app', texto)`.
Sinal de alerta: dois domínios para o mesmo projeto = protótipo e versão final; confirme qual
é o atual (o de dados reais, com o número de itens do escopo) antes de apresentar.

## 2. Hash do vivo × HEAD do repo

```python
import hashlib, urllib.request
tok = <GITHUB_TOKEN do .env>
hdr = {'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github.raw'}
def get(url, h=None):
    return urllib.request.urlopen(urllib.request.Request(url, headers=h or {'User-Agent':'Mozilla/5.0'}), timeout=60).read()
for f in ['index.html', 'js/main.js', 'js/data.js', 'css/tokens.css', '<um asset pesado>']:
    vivo = get(f'https://<dominio-final>/' + f)
    repo = get(f'https://api.github.com/repos/<owner>/<repo>/contents/<pasta-site>/' + f, hdr)
    print(f, hashlib.sha256(vivo).hexdigest() == hashlib.sha256(repo).hexdigest())
```

Confira também que cada asset responde 200 (não só a home) e, quando as telas são renderizadas
por JS, que o arquivo de **dados** (`js/data.js` ou equivalente) e não só o HTML é o mesmo.

## 3. Entregável contratual presente no artefato vivo

Para cada item do contrato, procure no vivo a marca do conteúdo (título da seção, chave do
objeto de dados, nome do relatório). Ausência ali é lacuna de entrega, mesmo que o arquivo
exista no repo — e vale dizer explicitamente o que o cliente não vai ver na tela.

```python
vivo = get('https://<dominio-final>/js/data.js').decode('utf-8', 'replace')
print('EAI' in vivo, vivo.count('130'))   # exemplos de marcas do conteúdo
```

## 4. Entrega formal (Drive + Gmail)

Tokens e regras de qual conta usar: skill `auxiliar-adm-id` (§1 e §5). Read-only:

- **Drive:** `files.get(fileId, fields='id,name,mimeType,modifiedTime,trashed,size')` na pasta do
  contrato e nos filhos (`'<pasta>' in parents and trashed=false`) — a estrutura esperada é uma
  subpasta por entregável.
- **Gmail:** `messages.list(q='subject:"<assunto da entrega>"')` + `messages.get(format='metadata',
  metadataHeaders=['From','To','Subject','Date'])` em cada resultado. A thread conta a história:
  envio original → reencaminhamento → resposta do cliente → liberação de link.

O que reportar é **a sequência com datas**, não "email enviado": enviado, para quem,
reencaminhado quando, respondido quando, e se algum entregável não aparece na pasta.

## 5. Contexto de projeto

Quando o pedido é "em que pé está o projeto X", junte a verificação do artefato com o
histórico de sessões (skill `hermes-session-forensics`) e com a página do cliente na base de
conhecimento — contrato encerrado, entrega de encerramento agendada e situação da frente
comercial são fatos distintos e não se deduzem do site.
