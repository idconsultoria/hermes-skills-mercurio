# Publicar gravações de lives no Moodle (Fathom)

Fluxo usado no curso Ferramentas de IA (course id 2, fórum "Gravações das Lives", forum id 2).

## 1. Descobrir a gravação no Fathom (API)
- Chave em `$HERMES_HOME/.secrets/fathom.env` (`FATHOM_API_KEY`). **Não** precisa do Hermes do Termux/Redmagic.
- `GET https://api.fathom.ai/external/v1/meetings?limit=50` com header `X-Api-Key`. A página vem com 10 itens e `next_cursor`; pagine passando `cursor=<next_cursor>`. `recorded_by[]` mostra os nomes dos participantes — útil para confirmar que é a live da turma (aulas sem título aparecem como "Impromptu Google Meet Meeting").

## 2. Escolher o link certo (armadilha)
- `url` da API = `fathom.video/calls/<id>` → **exige login no Fathom**; para aluno anônimo redireciona para a tela de entrada (testado com curl e navegador).
- `share_url` da API = `fathom.video/share/<token>` → abre para qualquer pessoa com o link (a página HTML traz `video_url`/`m3u8` embutidos).
- Regra: para aluno usar sempre `share_url`. O histórico do curso ficou com links `/calls/` (posts 1–3 e duas páginas do curso) — quebrados para quem não tem conta Fathom.

## 3. Publicar no fórum
- PHP CLI dentro do container: `forum_add_discussion()` com `$USER` = userid 2 (gustavomelloenciv@gmail.com, o mesmo autor dos posts de live). `mailnow=1` notifica os inscritos.
- Fazer idempotente: checar `forum_discussions` por nome antes de postar.
- Um post por live, com o link no corpo e o módulo/encerramento no título, seguindo o padrão dos anteriores.

## 4. Matricular aluno (papel `student`)
- `user_create_user($user, true, false)` + `enrol_get_plugin('manual')->enrol_user($instance, $uid, 5, $ts, $te, ...)`.
- **Pitfall:** o plugin pode lançar exceção *depois* de criar a matrícula ("Object of class stdClass could not be converted to string"). Envolver em try/catch e validar por SQL (`user_enrolments` + `role_assignments`); a matrícula normalmente existe.
- Validar o acesso de verdade com `authenticate_user_login($user, $senha)` e `get_user_roles(context_course::instance($course), $uid)`.
- E-mail de teste sem caixa real (ex.: `<nome>@idconsultoria.ai`) funciona para login, mas o Moodle tenta enviar e-mails ali — trocar pelo e-mail real quando o sócio confirmar.
