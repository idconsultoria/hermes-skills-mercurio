# Matrícula de aluno novo + email de boas-vindas

Fluxo validado 29/07/2026 (criação de 7 alunos) e repetido 04/08/2026 (Matheus).
Gatilho típico: "cheque a planilha de inscrições, verifique que há um aluno novo" → "matricule e envie email de boas-vindas".

## 1. Localizar a planilha de inscrições

- Nome: **"Jornada de IA - Inscrições"**
- Sheet ID: `1TG_SA7SJn5B-cwscT0wW3nUYAXQ3vY18NRwq4MhckEQ`
- Aba única: **"Matrículas"** (998 linhas de grid; ~10 preenchidas)
- Colunas: Data | Nome | Email | Número | Empresa | Curso desejado | Forma de pagamento | Onde conheceu | Dúvidas | Valor | Origem

Busca no Drive (planilha não aparece em busca por "inscri" genérica — filtrar por mimeType):

```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI drive search "mimeType='application/vnd.google-apps.spreadsheet'" --raw-query --max 40
# procurar "Jornada de IA - Inscrições"
```

Ler tudo (não limitar a A1:K100 — o grid tem 998 linhas; usar A1:K1000 e filtrar vazias):

```bash
$GAPI sheets get 1TG_SA7SJn5B-cwscT0wW3nUYAXQ3vY18NRwq4MhckEQ "A1:K1000"
```

⚠️ A planilha pode ter **linhas duplicadas** (Rivaldo aparece 2x em 29/07). Deduplicar por email antes de cruzar.

## 2. Cruzar com o Moodle (achar quem falta)

```sql
-- Alunos já no curso 2 (Ferramentas de IA)
SELECT u.id, u.email, u.firstname, u.lastname
FROM mdl_user u JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE e.courseid = 2 AND u.deleted = 0 AND u.suspended = 0 ORDER BY u.id;
```

Inscrito na planilha + ausente no SELECT = aluno novo.

## 3. Criar usuário + matricular (padrão exato)

- **username = parte antes do `@`** do email (mathysuyama@gmail.com → `mathysuyama`; teteu12212@gmail.com → `teteu12212`)
- **Senha inicial: `FerramentasDeIA@2026`** — gerar hash bcrypt no container:
  ```bash
  ssh oracle-host 'docker exec moodle-app php -r "echo password_hash(\"FerramentasDeIA@2026\", PASSWORD_DEFAULT);"'
  ```
- INSERT em `mdl_user`: auth='manual', confirmed=1, policyagreed=0, deleted=0, suspended=0, mnethostid=1, lang='pt_br', calendartype='gregorian', mailformat=1, maildisplay=2, maildigest=0, trackforums=0, timezone='99', firstaccess=0, lastaccess=0
- INSERT em `mdl_user_enrolments` com **enrolid=1** (instância manual do curso 2), status=0
- **NÃO precisa `mdl_role_assignments`** — os 7 alunos originais não têm role assignment e acessam o curso normalmente (papel student vem do enrol manual). Só gustavo.mello (id=2) tem role (editingteacher).

⚠️ **Quoting do SQL via ssh**: usar `shlex.quote` no comando remoto inteiro — `repr()`/aspas manuais quebram com `\n` e aspas internas (erro `syntax error at or near "\"`). Padrão que funciona:

```python
remote = "docker exec moodle-postgres psql -U moodle -d moodle -At -c " + shlex.quote(sql)
subprocess.run("ssh oracle-host " + shlex.quote(remote), shell=True, ...)
```

Referência de script completo: `/opt/data/tmp/create-matheus.py` (padrão herdado de `create-users-v2.py`).

## 4. Email de boas-vindas

- **Template:** `/opt/data/tmp/email-template-final.html` — HTML escuro (#050a0f) + card branco, SEM cabeçalho/logo (removido a pedido do Gustavo 29/07), botão "Acessar Plataforma", 5 passos, box "Suas Credenciais de Acesso"
- **Placeholder:** `[EMAIL_DO_ALUNO]` (substituir pelo email real). A senha `FerramentasDeIA@2026` já está hardcoded no template.
- **Assunto:** `Bem-vindo(a) à Plataforma de Treinamentos da ID Consultoria 🚀`
- **De:** `ID Consultoria Treinamentos <admin@idconsultoria.ai>` (token admin!)
- **Envio:** swap token admin → gmail send → restore (ver SKILL.md Mass Email). Script de referência: `/opt/data/tmp/send-matheus-welcome.py` (herdado de `send-welcome-emails.py`, que envia para lista).

⚠️ **Confirmar senha ativa antes de criar**: hash original da criação (29/07) era de `IdConsultoria2026!`, mas o template sempre anunciou `FerramentasDeIA@2026` e os hashes atuais (ex.: Rivaldo, que nunca logou) verificam `FerramentasDeIA@2026`. A senha a usar/criar é **sempre a anunciada no template**. Para conferir qual texto bate com um hash: rodar `password_verify()` no container (script PHP via pipe, pois `$2y$` quebra quoting inline).
