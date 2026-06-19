# Visual Research via Browser — Pinterest + Dribbble

> Workflow para pesquisa visual usando o Hermes browser tool com contas logadas.

## Contas

- **Pinterest:** hermes.hephaistos.id@proton.me / H3phaist0s!
- **Dribbble:** mesma conta (reCAPTCHA no login — usar acesso direto sem login)

## Pinterest (via browser)

### Login
```
browser_navigate(url="https://br.pinterest.com/login/")
browser_type(ref="@e16", text="hermes.hephaistos.id@proton.me")
browser_type(ref="@e18", text="H3phaist0s!")
browser_click(ref="@e12")  # botão Entrar
```

### Busca
```
browser_navigate(url="https://br.pinterest.com/search/pins/?q=SEARCH_TERM&rs=typed")
browser_scroll(direction="down")  # carregar mais resultados
browser_get_images()  # capturar URLs das imagens
```

### Resolução de imagens Pinterest
- `/236x/` — miniatura (resultados de busca)
- `/736x/` — HD (closeup do pin)
- `/1200x/` — máxima resolução

Para obter URL em alta: trocar `/236x/` por `/1200x/` na URL da imagem.

## Dribbble (sem login)

### Busca direta
```
browser_navigate(url="https://dribbble.com/search/shots/SEARCH_TERM")
browser_get_images()
```

Dribbble funciona sem login para buscas. O login tem reCAPTCHA e não funciona via browser tool.

## Fluxo paralelo com agy

Para projetos de design/branding, executar em paralelo:
1. **agy** — pesquisa, gera conceitos, cria rascunhos visuais (`generate_image`)
2. **Browser** — pesquisa Pinterest/Dribbble para referências reais

Após pesquisa, consolidar em `visao/pesquisa-visual-consolidada.md` com:
- Referências por categoria (logo, camisa, bola, banner)
- URLs das imagens encontradas
- Descrições de cada referência
- Direcionamento de design (paleta, tipografia, anti-padrões)
