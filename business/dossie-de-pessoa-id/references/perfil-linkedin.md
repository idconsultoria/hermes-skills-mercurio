# LinkedIn — leitura de perfil público para o dossiê

Para "o que ele faz hoje / onde trabalha / como a produção científica circula". Complementa
`verificacao-autoria-cientifica.md`: ali estão os artigos, aqui está o vínculo e o alcance.

## Acesso

1. `web_extract` costuma devolver vazio em perfil do LinkedIn — abrir no `browser_exec`.
2. Nunca pedir senha. Se o perfil exigir sessão, pedir o link e, se for restrito, pedir que
   a pessoa libere a visibilidade pública ou cole a seção.

## Onde está cada seção

A página principal do perfil abre no feed **Atividades**, em rolagem infinita: Experiência,
Formação e afins ficam abaixo e nunca são alcançadas rolando. Ir direto às subpáginas:

```
/in/<slug>/details/experience/
/in/<slug>/details/education/
/in/<slug>/details/publications/
/in/<slug>/details/skills/
```

- **`experience` renderiza bem** e é a fonte mais rica: cargo, empresa, período, local e
  regime. Foi por ali que apareceu vínculo empregatício que a base da ID não tinha — sempre
  comparar com a KB e apontar a lacuna, porque a empresa atual pode não existir na base.
- `education`, `publications`, `skills`, `certifications`, `projects`, `languages`
  frequentemente voltam vazias ("Nenhuma novidade por enquanto"). Isso significa **seção não
  preenchida**, não ausência do fato: não conclua "não tem formação" nem "não tem publicação".

## Produção científica em perfil sem seção de publicações

Seção "Publicações" vazia é o caso comum: o autor divulga os artigos em **posts**, cada um
apontando o DOI, o veículo e a posição de autoria. Ler o feed e extrair por post: tema,
artigo citado, ano e engajamento — é esse conjunto que responde "interação científica".

Cruzamento obrigatório: cada post citando DOI deve bater com a lista de
`verificacao-autoria-cientifica.md`; post sem DOI correspondente é divulgação, não publicação.

## Extração

- Texto por `document.body.innerText`. Seletores de classe do feed (`div.feed-shared-update-v2`
  e afins) mudam sem aviso e devolvem lista vazia — não gaste rodada perseguindo-os.
- A barra social traz números em sequência (**reações · comentários · compartilhamentos**).
  Só rotule cada número se a label estiver visível; sem label, descreva a contagem sem
  atribuir significado.
- Registrar no dossiê: headline, localidade, seguidores/conexões, experiência com datas e os
  3–6 posts técnicos com engajamento.

## Limites de privacidade

Perfil profissional é matéria pública e pode entrar no dossiê; o que estiver fora do perfil
(conversa privada, opinião de terceiro) continua barrado pelo filtro do Passo 6.
