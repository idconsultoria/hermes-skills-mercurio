-- moodle-admin: student-queries.sql
-- Common SQL queries for Moodle student management on treinamentos.idconsultoria.ai
-- Run via: ssh oracle-host 'docker exec moodle-postgres psql -U moodle -d moodle -At -c "QUERY"'

-- List all active students (exclude system accounts id <= 2)
SELECT id, email, firstname, lastname
FROM mdl_user
WHERE deleted = 0
  AND suspended = 0
  AND id > 2
ORDER BY id;

-- Students enrolled in a specific course
-- Change e.courseid = N for different courses
-- id=2 = "Ferramentas de IA"
SELECT u.id, u.email, u.firstname, u.lastname
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE e.courseid = 2
  AND u.deleted = 0
  AND u.suspended = 0
ORDER BY u.id;

-- Students enrolled in course with enrolment timestamps
SELECT u.id, u.email, u.firstname, u.lastname,
       to_timestamp(ue.timestart) AS enrolled_at
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE e.courseid = 2
  AND u.deleted = 0
  AND u.suspended = 0
ORDER BY u.id;

-- Total student count (active)
SELECT count(*) AS active_students
FROM mdl_user
WHERE deleted = 0 AND suspended = 0 AND id > 2;

-- Course list
SELECT id, fullname, shortname, visible
FROM mdl_course
ORDER BY id;

-- Get current additionalhtmlhead CSS
SELECT value FROM mdl_config WHERE name = 'additionalhtmlhead';

-- Set additionalhtmlhead CSS (via stdin to avoid quoting issues)
-- echo "NEW_CSS_VALUE" | docker exec -i moodle-postgres psql -U moodle -d moodle -c "UPDATE mdl_config SET value = \$_\$STDIN\$_$ WHERE name = 'additionalhtmlhead';"
