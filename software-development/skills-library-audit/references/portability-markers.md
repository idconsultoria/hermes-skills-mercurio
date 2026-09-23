# Marcadores, falsos positivos e empacotamento (ID Consultoria)

Complemento operacional de `skills-library-audit`. Estes são os sinais que separam "método
universal" de "só funciona com os dados do dono".

## Marcadores do dono

- **Marca / produto próprio:** `ID Consultoria`, `ID\.TEAL`, `BiotechSe`, `Biotech-Se`, `Mercúrio`,
  `Neulis`, `Clash Display`, `Tomato Grotesk`, `timbrado`, hexes da marca (`#14b8a6`, `#0a1929`).
- **Sócios:** `Gustavo`, `Maxwell`, `Cleverton`, `Tácio`, `n0ztr`.
- **Clientes / projetos internos:** `Famosa`, `El Niño`, `SEMAC`, `SergipeTec`, `Olimpo`, `Odigeí`,
  `ArtemisHub`, `Vulcano`, `Dédalo`, `Hephaistos`, `Axia`, `Alithea`, `Moodle`.
- **Caminhos internos:** `/opt/mercurio-data`, `mercurio_id_bot`, `context-kb`.
- **Credenciais / contas:** `google_token`, `GITHUB_TOKEN`, `admin@idconsultoria`, `\.env`,
  `refresh_token`, `client_secret`.
- **Identificadores de nuvem e conta (família fácil de esquecer):** id de projeto em nuvem
  (`idata-421319`), `service_account`, `service_account.json`, nome de bucket, domínio interno
  (`idconsultoria.ai`, `treinamentos.idconsultoria`), id longo de pasta do Drive, `@idteal`.
  Sem essa família na varredura, uma skill que cita conta de serviço e domínio interno passa como
  T1 — o id de projeto **é** dado do dono, mesmo sem ser segredo.

## Falsos positivos (não rebaixar a skill por isso)

- **`GITHUB_TOKEN`, `HERMES_HOME`, `/opt/data`** aparecem em skills genéricas como convenção do
  Hermes — não são dado do dono. Skill de GitHub que só cita `GITHUB_TOKEN` é **T1**.
- **Termos que casam por acidente:** `Inter` casa *internal/interface* (usar `Banco Inter`),
  `Familia` casa bairro. Preferir o termo composto.
- **Nome ≠ handle:** `Tácio` = `@n0ztr` no Telegram — varrer os dois.
- **Skill escrita em inglês** é indício forte de origem comunitária (upstream) → candidata natural a T1.
- **Achado que não muda a faixa, mas muda o arquivo:** skill de plataforma que cita `HERMES_HOME` e
  o caminho desta máquina (`/opt/data`) segue T1, porém o caminho local sai na normalização leve do
  empacotamento — o pacote não deve carregar o layout de disco daqui.

## Portão automatizado (script pronto)

`scripts/portao_poluicao.py <pasta> --termos termos.txt` — varre só arquivos de texto, agrupa por
família, imprime `arquivo:linha [termo] trecho` e sai com código **1** em qualquer acerto, para
encadear como portão. As famílias saem do arquivo de termos (formato no cabeçalho do script).

Três regras do matcher — sem elas o portão mente:

- **Mascarar base64 antes de varrer.** Template de deck com fonte/logo embutidos tem megabytes de
  `base64,...`: sigla em caixa alta casa dentro do payload e uma família inteira de falso positivo
  aparece (medido: centenas de acertos da mesma sigla em payload de imagem). Trocar
  `base64,[A-Za-z0-9+/=\s]{40,}` por `base64,<IMG>` preserva o resto da linha e zera o ruído.
- **Sigla CAIXA ALTA e caminho absoluto casam case-sensitive e com fronteira de palavra**
  (`\bIAF\b`, `/opt/data`); nome próprio casa com `re.I`. Sigla curta sem fronteira acha texto no
  meio de palavra e a triagem manual engole a rodada.
- **Convenção do Hermes fica fora da lista de termos:** `HERMES_HOME`, `GITHUB_TOKEN`, `~/.cache`.
  O LEIA-ME do pacote instala as skills em `<HERMES_HOME>/skills/...`; com o termo na lista, a
  própria entrega reprova no portão.

**O portão roda duas vezes:** na pasta de trabalho e **de novo no conteúdo extraído do zip**. Zipar
não limpa — o que vale é o que chegou, não o que estava na pasta.

## Varredura de segredos (responder a "isso vaza credencial?")

Duas passadas, escopadas ao diretório de skills:

1. **Enumerar candidatos** com busca em modo contagem, somando o padrão de valor real:
   `ghp_[A-Za-z0-9]{20,}`, `github_pat_[A-Za-z0-9_]{20,}`, `sk-[A-Za-z0-9]{24,}`,
   `AIza[0-9A-Za-z_-]{30,}`, `-----BEGIN [A-Z ]*PRIVATE KEY`, `password\s*[:=]\s*\S{8,}`,
   `token\s*[:=]\s*["'][A-Za-z0-9_-]{20,}`.
2. **Classificar cada acerto** — é a classificação que a resposta ao usuário precisa declarar, não o
   total:
   - **nome de variável** do padrão da plataforma ⇒ não é segredo, não rebaixa a skill;
   - **placeholder já mascarado** (`"redacted:ghp_…"`) ⇒ ok, quem escreveu já tratou;
   - **exemplo com valor truncado** (`MIIEvQ...`) ⇒ ok como exemplo — mas se o texto cita o *arquivo*
     da credencial (`service_account.json`) ou o id da conta, isso **é** dado do dono e entra como
     marcador de nuvem;
   - **valor real** ⇒ bloqueia: não sai no pacote, e avisar o dono para rotacionar.

Regra de ouro: **nome de variável não é segredo; valor é.** Nunca afirmar "não há segredo no acervo"
sem ter rodado a passada 1 e classificado cada acerto.

## Como separar "cita" de "depende"

- Densidade baixa (1–3 ocorrências em 40k chars) e termos que aparecem em **exemplo, template ou
  nota de rodapé** ⇒ T2: o método é genérico, o exemplo é que é local.
- Densidade alta, ou termos em **caminho de arquivo, comando, conta, id de recurso, seção de
  configuração** ⇒ T3: sem o ambiente do dono a skill não roda.
- Marcador só no `references/` (e não no `SKILL.md`) costuma ser detalhe removível ⇒ ler o trecho
  antes de rebaixar para T3.

## Empacotamento do pacote portátil

- Gerar o `.zip` com `zipfile.ZipFile` em Python: o host não tem o binário `zip` e travar a entrega
  por causa disso é desnecessário.
- Incluir `SKILL.md` + `references/` + `scripts/` + `templates/` + um `LEIA-ME.md` com origem,
  critério de seleção e o ajuste necessário (caminhos, contas, marca).
- **Nunca** incluir arquivo de credencial (token, `.env`, `client_secret`) nem deixar caminho
  absoluto do dono como obrigatório — o pacote existe para rodar em outra máquina.
- Nomear com versão e salvar em `/opt/mercurio-data/deliverables/`.
- Conferir depois: listar o zip (contagem de arquivos + nomes de skill presentes) contra a lista
  prometida ao usuário.
