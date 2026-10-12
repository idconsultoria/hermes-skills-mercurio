#!/data/data/com.termux/files/usr/bin/bash
# Checagem de densidade/paginas do documento A4 para ente publico.
# uso: checar_paginas.sh <arquivo.pdf> [piso]
set -euo pipefail
PDF="${1:?uso: checar_paginas.sh <arquivo.pdf> [piso]}"
PISO="${2:-1400}"
if [ ! -f "$PDF" ]; then echo "nao encontrado: $PDF"; exit 1; fi

PAGS=$(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')
TOK=$(pdftotext "$PDF" - | wc -c)
TEMP=$(pdfinfo "$PDF" | awk '/^Page size:/{print $3" x "$5}')
echo "arquivo : $PDF"
echo "paginas : $PAGS"
echo "chars   : $TOK (media $((TOK / PAGS)))"
echo "tamanho : $TEMP"
echo "-----------------------------------------------"
for i in $(seq 1 "$PAGS"); do
  C=$(pdftotext -f "$i" -l "$i" "$PDF" - | wc -c)
  ABRE=$(pdftotext -f "$i" -l "$i" "$PDF" - | tr -s '\n' ' ' | cut -c1-70)
  FLAG=""
  if [ "$i" -gt 1 ] && [ "$C" -lt "$PISO" ]; then FLAG="  <== PAGINA ORFA"; fi
  printf 'p%-3s %6s chars  %s%s\n' "$i" "$C" "$ABRE" "$FLAG"
done
echo "-----------------------------------------------"
R=$(pdftotext "$PDF" - | grep -c 'R\$' || true)
P=$(pdftotext "$PDF" - | grep -c '{{' || true)
echo "R\$ (deve ser 0)  : $R"
echo "{{ (deve ser 0)  : $P"
if [ "$R" -ne 0 ] || [ "$P" -ne 0 ]; then echo "ATENCAO: preco ou placeholder no documento do orgao"; exit 2; fi
echo "ok"
