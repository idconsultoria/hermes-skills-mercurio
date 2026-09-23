# Fontes de marca para render fiel (headless / Office / WeasyPrint)

O CSS do deck carrega webfonts de CDN. O Chromium headless com rede resolve isso, mas **qualquer outro renderizador** — LibreOffice/Office (ao abrir o PPTX), WeasyPrint, screenshot fora do navegador — usa o que está instalado na máquina. Sem as fontes instaladas, o render de conferência mente (troca de métrica, quebra de linha diferente, texto que parece "transbordar") e a auditoria vira ruído.

## Instalar

```bash
mkdir -p /root/.fonts && cd /tmp

# Fontshare (Clash Display etc.) — as URLs .ttf estão no CSS da API
curl -sL "https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600&display=swap" \
  | grep -o "https://[^)]*\.ttf" | sort -u | xargs -n1 curl -sLO

# Google Fonts (Hanken Grotesk etc.) — o UA padrão recebe URLs .ttf;
# UA de navegador legado devolve links "kit" que não baixam arquivo
curl -sL -A "curl" "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;800&display=swap" \
  | grep -o "https://[^)]*\.ttf" | sort -u | xargs -n1 curl -sLO

mv *.ttf /root/.fonts/ && fc-cache -f && fc-list | grep -iE "clash|hanken"
```

Só trate como apto depois de o `fc-list` listar as famílias. Os pesos importam: sem o ExtraBold/800 o título não quebra nem ocupa a mesma largura, e a auditoria acusa erro onde não há.

## Limite do formato

PPTX gerado por python-pptx **não embute fontes**. Mantenha os nomes reais das famílias nos runs e **entregue os .ttf junto ao .pptx**, avisando o cliente de que sem instalá-los o Office substitui a fonte (troque a mensagem se preferir: dá para embutir só salvando pelo PowerPoint — opção "Incorporar fontes no arquivo").

## Verificação de fidelidade (obrigatória em material de cliente)

1. Mesmo tamanho de página na referência aprovada e no novo render.
2. `pdfinfo arquivo.pdf | grep Pages` — páginas têm de bater com o esperado.
3. `pdftoppm -r 150 -png arquivo.pdf /tmp/pp/ref` e `/tmp/pp/novo`.
4. Composição lado a lado **referência | novo** por página (PIL) e auditoria com visão em **todas** as páginas: texto duplicado, texto cortado, cor inundada e selo ausente aparecem em páginas específicas — conferência pontual deixa passar.
