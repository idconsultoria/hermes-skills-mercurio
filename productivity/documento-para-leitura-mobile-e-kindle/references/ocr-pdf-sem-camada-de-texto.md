# OCR de PDF sem camada de texto

## Como saber que é o caso

`pdftotext -layout` devolve praticamente só `\f` (poucos bytes para dezenas de páginas) e `pdffonts`
lista **zero** fontes: o texto virou curvas (Illustrator, InDesign, arte-final). Não há atalho — é OCR
página por página.

## Instalação (Termux)

```bash
pkg install -y tesseract
mkdir -p ~/tmp/tessdata
curl -sL -o ~/tmp/tessdata/por.traineddata \
  https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata
TESSDATA_PREFIX=$HOME/tmp/tessdata tesseract --list-langs   # deve listar 'por'
```

- `tesseract-data-por` **não** existe no repositório do Termux; o traineddata vem do GitHub.
- Use **`tessdata_best`**, não `tessdata_fast`: no mesmo texto o `best` acertou `§ 3º` onde o `fast` leu `§ 5º`.
  Custa ~18 s por página — pague, é documento com valor legal.

## Render e OCR

```bash
pdftoppm -r 300 -gray -png doc.pdf ~/tmp/pg/p          # 300 dpi é o ponto de equilíbrio
for f in ~/tmp/pg/p-*.png; do
  b=$(basename "$f" .png)
  TESSDATA_PREFIX=$HOME/tmp/tessdata tesseract "$f" "~/tmp/txt/$b" -l por --psm 4
done
```

- **`--psm 4`** (coluna única com tamanhos variados) é o padrão certo para documento diagramado. Com `--psm 3`
  o Tesseract **descarta a coluna da direita** — numa lista "Cargo: Nome" saíram só os cargos, sem os nomes;
  `--psm 4` e `--psm 6` devolvem as linhas completas.
- Rode em background (`background=true`, `notify=true`): 40 páginas ≈ 12 min. Cinza a 300 dpi basta e segura o disco.
- **Guarde as imagens**: são a fonte de verdade para conferir qualquer numeral duvidoso.

## Ruído sistemático e correções seguras

Aplique como dicionário de substituições no script, nunca à mão:

| OCR | Correto | Onde |
|---|---|---|
| `8`, `$`, `&`, `£`, `8§`, `&£` + número + `º` | `§ Nº` | início de parágrafo |
| `\|`, `l`, `1` no início do item | `I` | incisos |
| `Il`, `Ill`, `HI`, `IM`, `II!` | `II`, `III` | incisos |
| `Vl`, `Vll`, `XXIl` | `VI`, `VII`, `XXII` | incisos |
| `Art.2º.0` / `Art.59.0` | `Art. 2º. O` / `Art. 59. O` | início de artigo |
| `urna` | `uma` | corpo |
| `filhados` | `filiados` | corpo |
| `O5` | `05` | datas |
| `palavra- palavra`, `Vice- Presidente` | `palavra-palavra` | hifenização partida no salto de linha |

Corrija acento perdido (`Etica` → `Ética`) e palavra colada (`Orepresentado` → `O representado`), mas
**não** "conserte" o que parece erro do autor: crase estranha, concordância, numeral repetido e remissão a
artigo errado são do documento. Confira na imagem e, se for do original, preserve.

## Conferência por página

1. Peça `vision_analyze(region=[...])` na faixa dos incisos e instrua **não corrigir a numeração**.
2. Páginas em branco são comuns (respiro de projeto): `Image.open(...).convert('L')` com `frac_escuro ≈ 0`
   confirma folha vazia sem gastar chamada de visão.
3. Compare as duas passagens de OCR (`fast` × `best`) linha a linha nos tokens numéricos: as divergências
   apontam onde a leitura está frágil (percentuais, prazos, número de artigo).
