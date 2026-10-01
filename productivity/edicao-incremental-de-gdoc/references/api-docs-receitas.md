# Receitas de API — editar Doc existente

Recortes prontos para copiar. Token: `$HERMES_HOME/google_token.json` (conta admin), refresh automático;
o venv que tem `googleapiclient` neste host é o do motor de NFS-e.

## 1. Laço de substituição em lote

```python
reqs = [{"replaceAllText": {"containsText": {"text": antes, "matchCase": True},
                          "replaceText": depois}} for antes, depois in PARES]
url = f"https://docs.googleapis.com/v1/documents/{DOC}:batchUpdate"
for i in range(0, len(reqs), 20):
    r = urllib.request.Request(url, data=json.dumps({"requests": reqs[i:i+20]}).encode(),
                               headers={"Content-Type": "application/json",
                                        "Authorization": "Bearer " + creds.token})
    resp = json.load(urllib.request.urlopen(r))
    for k, rep in enumerate(resp["replies"]):
        print(i + k, rep.get("replaceAllText", {}).get("occurrencesChanged", 0))
```

Antes de enviar, valide cada par contra o dump do doc: `if antes not in dump: abortar()`.

## 2. Ler o doc com estrutura (para montar os pares e conferir depois)

Percorra `doc["body"]["content"]` **recursivamente** (parágrafos + tabelas → células → parágrafos):

- heading: `paragraphStyle.namedStyleType` (`HEADING_1..3`)
- bullet: presença de `paragraph.bullet`
- callout: `paragraphStyle.shading.backgroundColor`
- tabela: células concatenadas com ` | ` (é o formato que você usa para achar as cadeias)

A exportação `text/markdown` do Drive **rebaixa** a estrutura (bullets viram `*`, tabelas viram linhas
soltas): serve para conferir conteúdo, não para reconstruir.

## 3. Negrito a partir do markdown

O conversor nem sempre aplica negrito (o doc pode ficar com 0 runs `bold=True`). Corrija por
correspondência de texto:

```python
# do markdown: texto_plano -> [(ini, fim)] das faixas em **
idx = {norm(texto_plano): ranges}
for par in paragrafos_do_doc:
    flat = norm(texto_do_paragrafo)
    if flat in idx:
        for ini, fim in idx[flat]:
            updateTextStyle(range=[par_start + off + ini, par_start + off + fim], bold=True)
```

`off` = deslocamento até o primeiro `textRun` do parágrafo (elementos de imagem contam 1 índice cada).

Na direção inversa (Doc → markdown), **mescle runs adjacentes com o mesmo `bold`** antes de emitir.

## 4. Recuperar conteúdo de uma revisão do Drive

```python
revs = drive.revisions().list(fileId=DOC, fields="revisions(id,modifiedTime)", pageSize=200).execute()
info = drive.revisions().get(fileId=DOC, revisionId=REV,
                             fields="id,modifiedTime,exportLinks").execute()
# exportLinks tem application/pdf, text/plain, text/markdown, rtf, odt
req = urllib.request.Request(info["exportLinks"]["text/plain"],
                             headers={"Authorization": "Bearer " + creds.token})
open("revisao.txt", "wb").write(urllib.request.urlopen(req).read())
```

Devolve o texto íntegro (a formatação, não). `revisions().update` só mexe em publicação — **não existe
"restore" pela API**; recupere o texto e reconstrua, ou peça ao usuário para restaurar pela UI.

## 5. Rodapé institucional em duas chamadas

```python
resp = batch([{"createFooter": {"type": "DEFAULT"}}])   # devolve footerId
fid = resp["replies"][0]["createFooter"]["footerId"]
batch([{"insertText": {"location": {"index": 0, "segmentId": fid}, "text": rotulo}}])
```

Campo de número de página **não** é inserível por API (não existe `insertPageNumber`) — ver SKILL.md.

## 6. Descobrir o fim da capa (para não estilizar a capa)

```python
cover_end = None
for i, el in enumerate(doc["body"]["content"]):
    if "sectionBreak" in el and i > 0:
        cover_end = el["endIndex"]
        break
# estilize apenas parágrafos com startIndex >= cover_end
```

## 7. Estilo: use `end - 1`

Range de estilo que inclui o `\n` final sangra para o parágrafo seguinte e cascateia no documento. Em
toda chamada `updateTextStyle`/`updateParagraphStyle`, use `endIndex = fim_do_paragrafo - 1`.
