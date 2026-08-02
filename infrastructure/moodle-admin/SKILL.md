---
name: moodle-admin
description: "Administer Moodle — DB, students, mass email.

Carregue esta skill quando precisar administrar o Moodle 5.2 de treinamentos.idconsultoria.ai — consultas SQL no Postgres via docker exec, gestão de estudantes, envio de email em massa personalizado e operações de manutenção. Cobre arquitetura Docker Compose (app, nginx, postgres, redis, cron) no host Oracle via SSH."
category: infrastructure
type: ToolIntegration
timestamp: 2026-07-29T00:00:00Z
author: Hermes (curator)
metadata:
  hermes:
    tags: [moodle, postgres, email, admin, google-workspace]
    related_skills: [oracle-host-access, google-workspace, production-deployment]
---

# Moodle Administration — treinamentos.idconsultoria.ai

## Architecture

Moodle 5.2 self-hosted on Oracle ARM64 via Docker Compose:

| Service | Container | DB | Port |
|---------|-----------|----|------|
| App | `moodle-app` (moodle-moodle) | — | internal |
| Nginx | `moodle-nginx` (nginx:stable) | — | proxy |
| Postgres | `moodle-postgres` (postgres:16) | moodle | internal |
| Redis | `moodle-redis` | — | internal |
| Cron | `moodle-cron` | — | internal |

All containers on the Oracle host (SSH from Hermes container). Postgres not exposed externally — query via `docker exec`.

## References

- `references/student-queries.sql` — common SQL queries
- `scripts/send-bulk-email.py` — reusable Python script for sending personalized emails to a list of students

## DB Access

```bash
# Single query
ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -At -c "SQL"'

# CSV export
ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -At -F "," -c "SQL"'

# Interactive
ssh oracle-host 'docker exec -it moodle-postgres psql -U moodle -d moodle'
```

### Key Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `mdl_user` | All users | id, email, firstname, lastname, confirmed, suspended, deleted |
| `mdl_user_enrolments` | Enrolments | userid, enrolid, timestart, timeend, status |
| `mdl_enrol` | Enrolment instances | id, courseid, enrol (method), status |
| `mdl_course` | Courses | id, fullname, shortname, visible |
| `mdl_config` | Site config | name, value |

### Useful Queries

```sql
-- Active students
SELECT id, email, firstname, lastname FROM mdl_user
WHERE deleted = 0 AND suspended = 0 AND id > 2;

-- Enrolled in course id=2 ("Ferramentas de IA")
SELECT u.id, u.email, u.firstname, u.lastname
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE e.courseid = 2 AND u.deleted = 0 AND u.suspended = 0;

-- Get CSS config
SELECT value FROM mdl_config WHERE name = 'additionalhtmlhead';
```

## Mass Email Workflow

### Token Management

Two token files:

| File | Identity | Use |
|------|----------|-----|
| `/opt/data/google_token.json` | Gustavo (user) | Regular operations |
| `/opt/data/google_token_admin.json` | admin@idconsultoria.ai | Transactional emails |

**Swap to send as admin:**

```bash
# Backup → activate admin → send → restore
cp /opt/data/google_token.json /opt/data/google_token_bkp.json
cp /opt/data/google_token_admin.json /opt/data/google_token.json

GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI gmail send \
  --to "$EMAIL" \
  --from "ID Consultoria Treinamentos <admin@idconsultoria.ai>" \
  --subject "Subject" \
  --body "<html>..." \
  --html

cp /opt/data/google_token_bkp.json /opt/data/google_token.json
rm -f /opt/data/google_token_bkp.json
```

### GAPI Python Binary

google_api.py requires the venv python — system python3 raises `ModuleNotFoundError: No module named 'googleapiclient'`:

```bash
# ✅ Correct
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"

# ❌ Wrong
GAPI="python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
```

Verify before bulk sending:
```bash
$GAPI gmail labels
```

### Bulk Send Script

For sending personalized HTML emails to many students, use `scripts/send-bulk-email.py`:

```bash
/opt/data/venvs/google/bin/python /opt/data/skills/infrastructure/moodle-admin/scripts/send-bulk-email.py \
  --template /path/to/template.html \
  --students "email1,email2,email3" \
  --subject "Subject" \
  --from "ID Consultoria Treinamentos <admin@idconsultoria.ai>"
```

The script handles token swapping, template personalization (replaces `[EMAIL_DO_ALUNO]`), error recovery, and reports per-student results.

## Student Password

Course "Ferramentas de IA" (id=2) initial password: `FerramentasDeIA@2026`

Students are advised to reset via "Perdeu a senha?" on first login.

## Enrolling Students

```sql
-- Find enrol instance for course id=2
SELECT id FROM mdl_enrol WHERE courseid = 2 AND enrol = 'manual';

-- Insert enrolment
INSERT INTO mdl_user_enrolments (status, enrolid, userid, timestart, timeend, modifierid, timecreated, timemodified)
VALUES (0, :enrolid, :userid, EXTRACT(EPOCH FROM NOW())::int, 0, 10, EXTRACT(EPOCH FROM NOW())::int, EXTRACT(EPOCH FROM NOW())::int);

-- Assign student role (roleid=5)
SELECT id FROM mdl_context WHERE instanceid = 2 AND contextlevel = 50;  -- 50 = course
INSERT INTO mdl_role_assignments (roleid, contextid, userid, timestart, timeend, modifierid, timecreated, timemodified)
VALUES (5, :contextid, :userid, EXTRACT(EPOCH FROM NOW())::int, 0, 10, EXTRACT(EPOCH FROM NOW())::int, EXTRACT(EPOCH FROM NOW())::int);
```

## Pitfalls

⚠️ **SSH quoting with SQL** — Single-quote the outer SSH command, double-quotes inside for SQL:
```bash
# ✅
ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -c "SELECT * FROM mdl_user LIMIT 5;"'
# ❌
ssh oracle-host "docker exec moodle-postgres psql -U moodle -d moodle -c \"SELECT * FROM mdl_user LIMIT 5;\""
```

⚠️ **Docker daemon down locally** — Docker may not run in the Hermes container. Always SSH to the host.

⚠️ **Token swap crash** — If the sending script crashes mid-swap (admin token active, user token in backup), subsequent Google calls fail. Always restore token even on error. Use `try/finally` in scripts.

⚠️ **google_api.py needs +x** — `chmod +x /opt/data/skills/productivity/google-workspace/scripts/google_api.py` if Permission denied.

⚠️ **ModuleNotFoundError** — Means system python3 was used instead of the venv python.

## Verification

```bash
# DB
ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -At -c "SELECT count(*) FROM mdl_user WHERE deleted=0;"'

# Email (single test)
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
cp /opt/data/google_token_admin.json /opt/data/google_token.json
$GAPI gmail send --to "test@example.com" --from "admin@idconsultoria.ai" --subject "Test" --body "<p>OK</p>" --html
```
