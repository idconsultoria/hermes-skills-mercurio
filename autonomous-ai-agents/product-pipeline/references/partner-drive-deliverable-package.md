# Pacote de Entregáveis para Parceiro Externo (Google Drive)

## Quando usar

Um parceiro de domínio (CFP certificado, especialista, consultor) tem disponibilidade limitada e precisa completar tarefas do pipeline (validar perfis, escrever recomendações, definir trilhas, validar tom). **Ele NÃO lê `.md` nem código.** Todo o contexto que for para ele deve estar em **Google Docs, Google Sheets ou PDF exportado de HTML bonito** (construído com o design system do projeto). Padrão validado no CFP IA (parceiro Igor, ciclo Q2+Q3).

## Padrão (7 passos)

1. **Mapear a pasta do projeto no Drive** primeiro:
   ```bash
   GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
   $GAPI drive search "'<FOLDER_ID>' in parents" --raw-query --max 30
   ```
   Identificar subpastas existentes (Fontes, Produto, Diretrizes, etc.) antes de criar novas.

2. **Criar uma subpasta numerada por entrega**, com o prazo no nome:
   `01 - Validar Perfis (14/08)`, `02 - Recomendacoes (18/08)`, `03 - Trilhas (16/08)`...
   ```bash
   $GAPI drive create-folder "01 - Nome (prazo)" --parent "$BASE"
   ```
   Numerar na ordem do guia mestre para o parceiro saber por onde começar.

3. **Criar um Google Doc TEMPLATE por entrega preenchível**, com o corpo contendo:
   - Dados do caso resumidos (renda, dívidas, perfil calculado)
   - Seções: `O QUE É / O QUE ENTREGAR / POR QUE IMPORTA / O QUE DESTRAVA`
   - Campos em branco com `[Escreva aqui]` para o parceiro preencher
   - Formato: `docs create --title "TEMPLATE — ... (preencher)" --body "$(cat arquivo.txt)"`
   - Para 3+ templates, gerar programaticamente via Python com subprocess.

4. **Exportar docs ricos como PDF**: guia de tom e voz, casos completos — gerar HTML single-file com o design system via Pi cost, depois WeasyPrint (ARM64 não tem Chromium):
   ```python
   # remover <link fonts.googleapis>, trocar Inter→DejaVu Sans, adicionar print-color-adjust
   doc = weasyprint.HTML(filename='x-weasy.html'); doc.write_pdf('x.pdf')
   ```
   Upload: `$GAPI drive upload x.pdf --name "..." --parent <subpasta>`.

5. **Mover arquivos entre pastas** via PATCH na API (o google_api.py não tem `move`):
   - GET `files/{id}?fields=parents` → PATCH `files/{id}?addParents={target}&removeParents={current}`
   - Token OAuth em `/opt/data/google_token.json` (campo `token`).
   - Script reutilizável: `scripts/drive_move.py` no repo do projeto (ou recriar).

6. **Reescrever o guia mestre (v2)** com links diretos por entrega e por documento, e **mover o guia antigo para a lixeira** (`drive delete` → trashed, reversível). Compartilhar docs como `--type anyone --role writer` para o parceiro responder inline.

7. **Verificar a estrutura final** com `drive search ... and trashed=false` — o search SEM filtro inclui lixeira e confunde o inventário.

## Pitfalls

- `drive search` sem `trashed=false` lista arquivos na lixeira → usar `'<folder>' in parents and trashed=false`.
- `drive delete` retorna `trashed` (não permanent) — o arquivo some do search filtrado, mas ainda existe.
- O script de move precisa do PATCH com `method="PATCH"` no urllib e headers `Authorization: Bearer` + `Content-Type`.
- Google Docs criados via API nascem na raiz do Drive do dono — mover para a pasta do parceiro logo após criar (passo 5).
- PDF via WeasyPrint: remover Google Fonts links ANTES (senão tenta rede), trocar fontes web por DejaVu, `print-color-adjust: exact` para preservar cores.
- O guia antigo trashed continua aparecendo em busca sem filtro — não esquecer de filtrar ao reportar estrutura.

## Checklist do pacote completo

- [ ] Guia mestre com links (v2) na raiz da pasta do parceiro
- [ ] Subpastas numeradas 01..N cobrindo TODAS as entregas do guia
- [ ] Template preenchível (Google Doc) para cada entrega que exige produção do parceiro
- [ ] PDFs dos documentos ricos (tom, casos) exportados com design system
- [ ] Artefatos brutos (extratos, faturas, contratos simulados) — "os mesmos que o usuário subiria no app"
- [ ] Docs compartilhados com role writer
- [ ] Nenhum `.md` ou código na pasta do parceiro
