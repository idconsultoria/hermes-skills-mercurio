-- ============================================================
-- Moodle login & usage audit queries
-- treinamentos.idconsultoria.ai · Moodle 5.2 · Postgres via docker exec
-- Run: ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -c "SQL"'
-- NOTE: timestamp 0 = never (renders 01/01/1970). lastlogin updates only
-- from the 2nd login onward; first session shows in currentlogin.
-- ============================================================

-- 1. Login history per user (mdl_user)
SELECT id, email, firstname, lastname,
  TO_CHAR(TO_TIMESTAMP(firstaccess),'DD/MM/YYYY HH24:MI') AS primeiro_acesso,
  TO_CHAR(TO_TIMESTAMP(lastlogin),'DD/MM/YYYY HH24:MI')   AS ultimo_login,
  TO_CHAR(TO_TIMESTAMP(currentlogin),'DD/MM/YYYY HH24:MI')AS login_atual,
  lastip, suspended, deleted
FROM mdl_user WHERE deleted = 0 ORDER BY lastlogin DESC NULLS LAST;

-- 2. Activity per user (logstore_standard_log)
SELECT u.id, u.firstname || ' ' || u.lastname AS usuario,
  COUNT(l.id) AS eventos, COUNT(DISTINCT l.courseid) AS cursos,
  TO_CHAR(MAX(TO_TIMESTAMP(l.timecreated)),'DD/MM/YYYY HH24:MI') AS ultima_atividade
FROM mdl_logstore_standard_log l JOIN mdl_user u ON u.id = l.userid
GROUP BY u.id, u.firstname, u.lastname ORDER BY eventos DESC;

-- 3. Event type breakdown
SELECT eventname, COUNT(*) FROM mdl_logstore_standard_log
GROUP BY eventname ORDER BY COUNT(*) DESC LIMIT 15;

-- 4. Logins per user
SELECT u.email, COUNT(*) AS logins FROM mdl_logstore_standard_log l
JOIN mdl_user u ON u.id = l.userid
WHERE l.eventname LIKE '%loggedin%' GROUP BY u.email ORDER BY logins DESC;

-- 5. Content pages viewed (course_module_viewed -> page names)
SELECT p.name AS pagina, COUNT(*) AS vezes FROM mdl_logstore_standard_log l
LEFT JOIN mdl_course_modules cm ON cm.id = l.contextinstanceid
LEFT JOIN mdl_page p ON p.id = cm.instance
WHERE l.eventname LIKE '%course_module_viewed%' GROUP BY p.name ORDER BY vezes DESC;

-- 6. Full navigation trail for specific users
SELECT TO_CHAR(TO_TIMESTAMP(l.timecreated),'DD/MM/YYYY HH24:MI') AS quando,
  l.userid, l.eventname, COALESCE(c.shortname,'-') AS curso, l.ip
FROM mdl_logstore_standard_log l LEFT JOIN mdl_course c ON c.id = l.courseid
WHERE l.userid IN (4,9,5) ORDER BY l.timecreated;

-- 7. Failed emails (mail function broken -> reset links never delivered)
SELECT TO_CHAR(TO_TIMESTAMP(timecreated),'DD/MM/YYYY HH24:MI') AS quando, other
FROM mdl_logstore_standard_log WHERE eventname LIKE '%email_failed%' ORDER BY timecreated;

-- Context: course id=1 = site course (portal front page); id=2 = "Ferramentas de IA".
-- gradereport_overview = user opened own grade overview report.
