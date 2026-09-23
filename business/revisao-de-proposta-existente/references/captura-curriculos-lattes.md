# Currículos para processo institucional: captura e elaboração

Para processos que exigem currículo (dispensa licitatória, credenciamento, proposta institucional).

## Lattes (buscatextual.cnpq.br) — exige gesto humano

1. Busca: `busca.do` → preencher `#textoBusca` (via `value=`, não `fill_input`, que falha nesse form)
   e clicar `#botaoBuscaFiltros`. Marcar `buscaNome` + `buscarDemais`.
2. O resultado **não** abre por URL direta: `visualizacv.do?id=...` sozinho cai em "Código de
   segurança". O caminho é `abreDetalhe('K...','Nome',id)` do resultado, que abre um **modal**
   com botão `#idbtnabrircurriculo` (`chamarFuncaoAbreCV()`).
3. Esse botão depende de reCAPTCHA: clique por JS e por `Input.dispatchMouseEvent` **não**
   resolvem — a página não navega. **Peça ao usuário para clicar** no modal (ele está na tela).
   Quando ele deixa a guia aberta, capture sem recarregar.
4. Captura: anexar na guia (`Target.attachToTarget`), `document.body.innerText` para o texto e
   `Page.printToPDF` para o PDF. Salvar como `<Nome-Completo>-Lattes-v1.pdf`.
5. Registre do próprio currículo: **ID Lattes** e a linha **"Última atualização do currículo em
   DD/MM/AAAA"**. Nunca diga "atualizado" sem essa data.
6. A busca acha homônimos e o portal pode misturar pessoas: confirme área de atuação e vínculo
   antes de usar (ex.: "UI/UX Designer" para designer; "Fitopatologia" para o agrônomo).

## LinkedIn do próprio operador (perfil logado)

Com a guia do perfil já autenticada: `document.querySelector('main').innerText` após `Page.navigate`
para `linkedin.com/in/<handle>` e alguns `window.scrollTo` — traz Resumo, Experiência, Formação,
Certificações, Projetos e Competências. `web_extract` no LinkedIn devolve vazio (authwall).

**Cuidado com o que o perfil não afirma:** data final aberta (ex.: "2016 – o momento") **não**
prova conclusão de curso. Escreva a formação sem afirmar conclusão e sinalize a lacuna na entrega.
Se o sócio confirmar que não concluiu, registre "curso não concluído" no currículo **e** onde a
mesma afirmação apareça em outros documentos da entrega.

## Fontes alternativas

Espelho tipo Escavador serve como **alternativa rotulada**, com a data de coleta dele ("Informações
coletadas do Lattes em DD/MM/AAAA") — nunca como Lattes oficial atualizado. Se o PDF oficial está
bloqueado, diga qual fonte foi usada.

## Elaborar o currículo e entregar

- **Identidade:** aplicar **somente a do contratado/destinatário** quando solicitado — baixar o
  logo oficial do site institucional e amostrar a paleta real dele; nada da marca da ID nem de
  parceiras. Não inventar paleta, tipografia ou motivo gráfico que não exista na fonte; sem
  material oficial, usar neutro. Não criar design system para isso.
- **Entregáveis:** PDF individual por especialista (para anexar ao processo) **e** um anexo dentro
  da proposta, com síntese de cada um, função no projeto e o ID/link do Lattes. Currículo dos
  sócios é elaborado a partir do histórico (LinkedIn + base); dos demais, o Lattes oficial é o
  anexo.
- **Ocultar o executor, não o profissional:** quando a proposta não nomeia empresas parceiras, o
  currículo descreve o trabalho sem citar a razão social da consultoria própria nem produtos
  proprietários que permitam rastreá-la. Descreva o projeto pelo conteúdo (instituição, dado,
  resultado) e sinalize a escolha para o sócio poder nomear, se preferir.
- **Render e conferência:** HTML A4 → PDF por Chromium headless, com `.job{page-break-inside:avoid}`
  para não deixar título órfão no pé da página; validar com `pdfinfo` e leitura visual das páginas
  (logo renderizado, alinhamento das datas à direita, nada cortado). Versionar o arquivo (`-v2`,
  `-v3`) a cada correção, nunca sobrescrever.
- **Modelo único para a equipe:** gerar todos os currículos a partir do **mesmo template**
  (`templates/curriculo-profissional-identidade-cliente.html`), preenchendo os dados por pessoa.
  Layout uniforme é parte da entrega; currículo redesenhado por especialista parece documento de
  outra instituição.
- **Conferir vazamento de repr de linguagem no HTML gerado:** ao preencher template com
  `str.format`, um valor que ficou como **lista** em vez de string sai impresso literalmente
  (`['Competência 1', 'Competência 2']`) e vai para o PDF. Depois de gerar, rode uma busca por
  `['` (e `', '`) no texto do PDF — sintoma barato de detectar, caro de descobrir na entrega.
- **Número publicado em documento se conta por chave única:** patentes, cultivares e registros
  repetem o mesmo identificador em seções diferentes (Patentes e registros × Inovação). Conte com
  deduplicação (`grep -o … | sort -u | wc -l`) e imprima o número antes de escrevê-lo; `grep -c`
  cru deu 26 onde havia 13 registros distintos — e o número vai para as mãos do procurador.
- **Rodapé com a cadeia de verificação:** cada PDF traz `Síntese curricular elaborada a partir do
  Currículo Lattes de <nome> — ID Lattes <id>, atualizado em <data>` e a informação de que o PDF
  integral acompanha o processo. Substitui a assinatura de quem elaborou e sustenta o dado.
- **Seção "Atuação no projeto" espelhando a proposta:** cada currículo fecha com o papel daquele
  especialista no objeto, com a mesma redação da seção de equipe técnica da proposta.
