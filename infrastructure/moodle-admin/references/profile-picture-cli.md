# Foto de perfil de usuário no Moodle 5.2 via CLI

Fluxo validado 04/08/2026: Gustavo tentou trocar a foto do admin pela UI e "não funcionou"
(silenciosamente). Diagnóstico e correção via CLI.

## Como a falha se apresenta

- Upload pela UI cria o arquivo como **draft** (evento `\core\event\draft_file_added` no
  logstore), mas a foto **nunca é salva**: `mdl_user.picture` continua `0`.
- Nenhum erro na tela, nenhum erro no `php_errors.log` do container — falha silenciosa.
- Causa raiz comum: **GIF animado/otimizado** (ex.: 480x480, 8.6 MB, paleta por frame).
  `process_new_icon()` quebra com `imagecolorsforindex(): Argument #2 ($color) is out of range`
  porque GD não converte GIF de paleta indexada direto.

## Diagnóstico (nesta ordem)

1. Estado da foto no banco:
   ```sql
   SELECT id, username, picture, imagealt FROM mdl_user WHERE id = 10;  -- picture=0 => falhou
   ```
2. Drafts órfãos (o upload chegou mas não foi processado):
   ```sql
   SELECT id, component, filearea, itemid, filename, filesize, mimetype, userid
   FROM mdl_files WHERE userid = 10 AND filearea = 'draft' ORDER BY timecreated DESC;
   ```
   — note o `fileid` do arquivo (ex.: 5528): é o que o script reusa.
3. Eventos recentes do usuário (draft_file_added = upload chegou; ausência de user_updated = não salvou):
   ```sql
   SELECT TO_CHAR(TO_TIMESTAMP(l.timecreated),'DD/MM/YYYY HH24:MI:SS'), l.eventname, l.other
   FROM mdl_logstore_standard_log l WHERE l.userid = 10 ORDER BY l.timecreated DESC LIMIT 15;
   ```
4. Erros PHP do container: `ssh oracle-host 'docker exec moodle-app cat /var/log/php_errors.log'`

## API do Moodle 5.2 (MUDOU vs versões antigas)

- **`user_update_picture()` NÃO existe mais** no Moodle 5.2 (procurei em todo o codebase — não está).
- O padrão atual é o do `auth/lti/auth.php`:
  `copy_content_to_temp()` → `process_new_icon($context, 'user', 'icon', 0, $tempfile)` →
  `$DB->set_field('user', 'picture', $newpicture, ['id' => $userid])`.
- `process_new_icon` precisa de `require_once($CFG->libdir.'/gdlib.php')` e `filelib.php`.
- A foto final fica em `mdl_files` com `component='user'`, `filearea='icon'`, `itemid=0`:
  arquivos `f1.png`, `f2.png`, `f3.png` (miniaturas geradas pelo processamento).
- Web root do Moodle 5 é `public/`: libs em `/var/www/html/public/lib/` (moodlelib.php,
  gdlib.php, filelib.php). O `config.php` do container fica em `/var/www/html/config.php`.

## Correção

Script pronto e reutilizável: `scripts/set-user-picture.php` no diretório da skill.

```bash
cat /opt/data/skills/infrastructure/moodle-admin/scripts/set-user-picture.php | \
  ssh oracle-host 'docker exec -i moodle-app sh -c "cat > /tmp/set-user-picture.php && php /tmp/set-user-picture.php --userid=10 --fileid=5528"'
```

- `--fileid` = id do draft em `mdl_files` (item 2 do diagnóstico). Reaproveitar o draft
  existente evita re-enviar arquivo.
- O script converte GIF → PNG truecolor (1º frame) automaticamente antes de processar.
- Sucesso imprime `PICTURE_OK picture=<id>`; o `picture` passa a apontar para o `f1.png`.

## Verificação

```sql
SELECT picture FROM mdl_user WHERE id = 10;  -- > 0 = ok
SELECT filename, filesize FROM mdl_files WHERE component='user' AND filearea='icon'
  AND itemid=0 AND contextid=46;  -- f1.png / f2.png / f3.png
```

Dica UX: o usuário pode precisar de Ctrl+F5 para ver a foto nova na UI.

## Pitfalls

- GIF é o suspeito nº 1 de falha silenciosa; PNG/JPEG normais costumam processar direto.
- Se `process_new_icon` retornar 0, o `set_field` não deve rodar — o script sai com
  `PROCESS_FAILED` sem corromper o usuário.
- `imagecolorsforindex` out of range é mensagem do GD sobre paleta indexada do GIF — não é
  problema de permissão nem de tamanho.
