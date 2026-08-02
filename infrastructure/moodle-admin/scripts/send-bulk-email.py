#!/usr/bin/env python3
"""
send-bulk-email.py — Send personalized HTML emails to Moodle students via Google API.

Usage:
  /opt/data/venvs/google/bin/python send-bulk-email.py \
    --template /path/to/template.html \
    --students "email1,email2,email3" \
    --subject "Subject" \
    --from "Name <email>" \
    [--placeholder EMAIL_DO_ALUNO]

Handles:
  - Token swapping (user → admin → user) per student
  - Template personalization (replaces placeholder with student email)
  - Error recovery (restores token even on failure)
  - Per-student result reporting
"""
import argparse
import os
import shutil
import subprocess
import sys

TOKEN_FILE = "/opt/data/google_token.json"
TOKEN_ADMIN_FILE = "/opt/data/google_token_admin.json"
TOKEN_BACKUP = "/opt/data/google_token_bkp.json"
GAPI_SCRIPT = "/opt/data/skills/productivity/google-workspace/scripts/google_api.py"
GAPI_PYTHON = "/opt/data/venvs/google/bin/python"


def parse_args():
    parser = argparse.ArgumentParser(description="Send bulk HTML emails to students")
    parser.add_argument("--template", required=True, help="Path to HTML template file")
    parser.add_argument("--students", required=True, help="Comma-separated list of student emails")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--from", dest="from_addr", required=True, help="Sender (Name <email>)")
    parser.add_argument("--placeholder", default="EMAIL_DO_ALUNO", help="Placeholder in template (default: EMAIL_DO_ALUNO)")
    return parser.parse_args()


def read_template(path):
    with open(path) as f:
        return f.read()


def personalize(template_html, placeholder, email):
    return template_html.replace(f"[{placeholder}]", email)


def swap_to_admin():
    if os.path.exists(TOKEN_FILE):
        shutil.copy2(TOKEN_FILE, TOKEN_BACKUP)
    shutil.copy2(TOKEN_ADMIN_FILE, TOKEN_FILE)


def restore_token():
    if os.path.exists(TOKEN_BACKUP):
        shutil.copy2(TOKEN_BACKUP, TOKEN_FILE)
        os.remove(TOKEN_BACKUP)


def send_email(to_addr, from_addr, subject, html_body):
    cmd = [
        GAPI_PYTHON, GAPI_SCRIPT,
        "gmail", "send",
        "--to", to_addr,
        "--from", from_addr,
        "--subject", subject,
        "--body", html_body,
        "--html",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def main():
    args = parse_args()

    template_html = read_template(args.template)
    students = [s.strip() for s in args.students.split(",") if s.strip()]

    results = []
    success_count = 0
    fail_count = 0

    print(f"Enviando para {len(students)} alunos...")
    print()

    for email in students:
        print(f"  {email}...", end=" ", flush=True)

        personal_html = personalize(template_html, args.placeholder, email)

        try:
            swap_to_admin()
            rc, out, err = send_email(email, args.from_addr, args.subject, personal_html)
        except Exception as e:
            rc = -1
            err = str(e)
        finally:
            restore_token()

        if rc == 0:
            print("✅")
            results.append(f"✅ {email} — enviado")
            success_count += 1
        else:
            print("❌")
            reason = err[:120] if err else f"exit code {rc}"
            print(f"     falha: {reason}")
            results.append(f"❌ {email} — {reason}")
            fail_count += 1

    print()
    print(f"=== RESUMO ===")
    print(f"Total: {len(students)} | Sucesso: {success_count} | Falha: {fail_count}")
    for r in results:
        print(r)

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
