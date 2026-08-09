# SQL com aspas aninhadas — pipe via stdin (fix robusto)

## Problema

Queries do Moodle com `TO_CHAR(...,'DD/MM HH24:MI')`, `LIKE '%config_log_created%'`,
`INTERVAL '26 hours'` ou concatenação de strings quebram com **syntax error** quando
passadas inline via ssh:

```bash
# ❌ Falha — aspas simples do TO_CHAR/LIKE colidem com o quoting do ssh
ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -At -c "SELECT ... TO_CHAR(x,'DD/MM HH24:MI') ..."'
```

Tentativas de escape (chr(39) etc.) também falham — o psql não aceita `chr()` onde
espera literal de string.

## Fix: pipe via stdin

1. Escreva o SQL num arquivo sob `/opt/data/` — ⚠️ `write_file` **bloqueia `/tmp/`**
   (fora de HERMES_WRITE_SAFE_ROOT=/opt/data); use ex. `/opt/data/tmp_query.sql` e
   apague depois.
2. Faça pipe direto pro psql:

```bash
cat /opt/data/tmp_query.sql | ssh oracle-host 'docker exec -i moodle-postgres psql -U moodle -d moodle -At -F "|"'
rm -f /opt/data/tmp_query.sql
```

Sem escaping manual. O psql lê o SQL puro do stdin.

## Caso real (08/08/2026)

Query de atividade de alunos nas últimas 26h — precisava de `TO_CHAR` com formato
`DD/MM HH24:MI`, `NOT LIKE '%config_log_created%'` e `NOT LIKE '%capability_assigned%'`.
Inline: 2 tentativas com syntax error. Via stdin-pipe: funcionou de primeira.

```sql
SELECT u.firstname || ' ' || u.lastname AS aluno,
  COUNT(l.id) AS eventos,
  COUNT(DISTINCT l.courseid) AS cursos,
  TO_CHAR(MAX(TO_TIMESTAMP(l.timecreated)),'DD/MM HH24:MI') AS ultima_atv
FROM mdl_logstore_standard_log l
JOIN mdl_user u ON u.id = l.userid
WHERE l.timecreated >= EXTRACT(EPOCH FROM NOW() - INTERVAL '26 hours')::int
  AND u.deleted = 0 AND u.id > 2
  AND l.eventname NOT LIKE '%config_log_created%'
  AND l.eventname NOT LIKE '%capability_assigned%'
GROUP BY u.id, u.firstname, u.lastname
ORDER BY eventos DESC;
```

## Pitfall relacionado

Para query de navegação de um usuário específico, o email NÃO é o primeiro nome —
liste usuários primeiro (`SELECT id, email, firstname, lastname FROM mdl_user WHERE
deleted=0 AND id>2`) e use o `userid` na query de navegação.
