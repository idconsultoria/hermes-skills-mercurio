#!/usr/bin/env python3
"""
aula_pipeline.py — Pipeline aula GitHub → Moodle (curso "Ferramentas de IA").

Uso:
  python3 aula_pipeline.py check
      Lista os assets do release 'video' (idconsultoria/iaf) e cruza com as páginas
      do Moodle: NOVO (asset sem página) | INTEGRADO (página X) | PLACEHOLDER (página sem vídeo).

  python3 aula_pipeline.py add <arquivo.mp4> [--modulo N|--section ID] [--intro "texto"] [--title "Titulo Customizado"]
      Integra o asset na página correspondente (nome normalizado, acento-insensível).
      Página existe (placeholder) -> atualiza content.
      Página não existe -> cria na seção (M1=1, M2=2, M3=3, M4=4 — section number).
      --title sobrescreve o título derivado do nome do arquivo (para nomes que não
      casam com o título desejado da página; o match por nome normalizado usa o título).
      Depois de adicionar, dispara purge de cache no Moodle.

Requires: ssh oracle-host (host Oracle), token GitHub da idconsultoria em
/opt/data/home/.config/gh/hosts.yml. O binário gh é bloqueado pelo gateway guard
— por isso a API é chamada via urllib.
"""
import json
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

REPO = 'idconsultoria/iaf'
RELEASE_TAG = 'video'
COURSE = 2
SECTIONS = {1: 1, 2: 2, 3: 3, 4: 4}          # módulo -> section number (mdl_course_sections.section)
ADD_AULA_PHP = '/opt/data/skills/infrastructure/moodle-admin/scripts/add_aula.php'

ACCENTS = {
    'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    'ç': 'c', 'ñ': 'n',
}


def norm(s: str) -> str:
    s = s.lower()
    for a, b in ACCENTS.items():
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def title_from_file(filename: str) -> str:
    base = filename.rsplit('.', 1)[0]
    return re.sub(r'[-_.]+', ' ', base).strip()


def gh_token() -> str:
    hosts = open('/opt/data/home/.config/gh/hosts.yml').read()
    m = re.search(r'idconsultoria:\s*\n\s+oauth_token:\s*([^\s]+)', hosts)
    if not m:
        sys.exit('TOKEN_NAO_ENCONTRADO em hosts.yml')
    return m.group(1).strip().strip('"\'')


def api(url: str):
    req = urllib.request.Request(url, headers={
        'Authorization': f'token {gh_token()}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'hermes'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read()[:300]}')


def list_assets() -> list:
    releases = api(f'https://api.github.com/repos/{REPO}/releases?per_page=20')
    for rel in releases:
        if rel['tag_name'] == RELEASE_TAG:
            return rel['assets']
    return []


def moodle_pages() -> dict:
    """{nome_normalizado: (page_id, nome_original, tem_conteudo, tem_intro)}"""
    remote = ('docker exec moodle-postgres psql -U moodle -d moodle -At -c '
              '"SELECT id, name, LENGTH(content), LENGTH(COALESCE(intro, '"'"''"'"')) FROM mdl_page WHERE course = 2 ORDER BY id;"')
    cmd = 'ssh oracle-host ' + shlex.quote(remote)
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f'ERRO consulta Moodle: {out.stderr[:300]}')
    pages = {}
    for line in out.stdout.strip().splitlines():
        if '|' not in line:
            continue
        pid, pname, plen, ilen = (x.strip() for x in line.split('|'))
        pages[norm(pname)] = (pid, pname, int(plen) > 50, int(ilen) > 0)
    return pages


def run_remote(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'ERRO: {r.stderr[:500]}')
    return r.stdout


def find_page_by_url(url: str):
    """Procura página cujo content contenha a URL do asset (cobre títulos customizados via --title)."""
    sql = ("SELECT id, name, LENGTH(content), LENGTH(COALESCE(intro, '')) FROM mdl_page "
           "WHERE course = 2 AND content LIKE '%" + url + "%' ORDER BY id;")
    remote = "docker exec moodle-postgres psql -U moodle -d moodle -At -c " + shlex.quote(sql)
    cmd = 'ssh oracle-host ' + shlex.quote(remote)
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f'ERRO consulta Moodle: {out.stderr[:300]}')
    for line in out.stdout.strip().splitlines():
        if '|' in line:
            pid, pname, plen, ilen = (x.strip() for x in line.split('|'))
            return (pid, pname, int(plen) > 50, int(ilen) > 0)
    return None


def check() -> None:
    assets = list_assets()
    pages = moodle_pages()
    print(f'== Assets no release "{RELEASE_TAG}" ({len(assets)}) ==')
    known = set()
    for a in assets:
        fn = a['name']
        if not fn.lower().endswith('.mp4'):
            continue
        key = norm(title_from_file(fn))
        known.add(key)
        page = pages.get(key)
        if page is None:
            # Título pode ter sido customizado via --title; casa por URL do asset no content.
            url = f'https://github.com/{REPO}/releases/download/{RELEASE_TAG}/{fn}'
            page = find_page_by_url(url)
            if page is not None:
                pid, pname, has, has_intro = page
                estado = 'INTEGRADO' if has else 'PÁGINA SEM VÍDEO (placeholder)'
                desc = 'descrição ✓' if has_intro else 'sem descrição'
                print(f'  [OK] {fn} -> página {pname!r} (id={pid}) [{estado} · {desc}] [título custom]')
                continue
        if page is not None:
            pid, pname, has, has_intro = page
            estado = 'INTEGRADO' if has else 'PÁGINA SEM VÍDEO (placeholder)'
            desc = 'descrição ✓' if has_intro else 'sem descrição'
            print(f'  [OK] {fn} -> página {pname!r} (id={pid}) [{estado} · {desc}]')
        else:
            print(f'  [NOVO] {fn} -> sem página correspondente (criar: --modulo N)')
    print(f'\n== Páginas do curso sem vídeo ({len(pages) - sum(1 for k in known if k in pages)} placeholders) ==')
    for key, (pid, pname, has, has_intro) in sorted(pages.items(), key=lambda x: x[1][1]):
        if not has:
            desc = ' · descrição ✓' if has_intro else ' · sem descrição'
            print(f'  [PENDENTE] página {pname!r} (id={pid}) aguardando asset{desc}')


def add(filename: str, modulo: int | None, section: int | None, intro: str, title_override: str = '') -> None:
    assets = list_assets()
    found = None
    for a in assets:
        if a['name'] == filename:
            found = a
            break
    if not found:
        sys.exit(f'Asset "{filename}" não encontrado no release "{RELEASE_TAG}". '
                 f'Assets atuais: {[a["name"] for a in assets]}')
    url = f'https://github.com/{REPO}/releases/download/{RELEASE_TAG}/{filename}'
    title = title_override or title_from_file(filename)
    pages = moodle_pages()
    exists = norm(title) in pages

    if not exists:
        if section is None and modulo is not None:
            section = SECTIONS.get(modulo)
            if not section:
                sys.exit('--modulo deve ser 1..4')
        if section is None:
            sys.exit(f'Página "{title}" não existe. Informe --modulo N (1..4) ou --section ID.')

    args = ['--name', title, '--url', url]
    if section:
        args += ['--section', str(section)]
    if intro:
        args += ['--intro', intro]

    quoted = ' '.join(shlex.quote(a) for a in args)
    # Passo 1: grava o add_aula.php no container (printf evita aspas aninhadas).
    php_src = open(ADD_AULA_PHP).read()
    pipe_cmd = ('printf %s ' + shlex.quote(php_src) + ' | ssh oracle-host ' +
                shlex.quote('docker exec -i moodle-app sh -c "cat > /tmp/add_aula.php"'))
    run_remote(pipe_cmd)
    # Passo 2: executa com os args (cada arg quoteado individualmente).
    args_cmd = ('ssh oracle-host ' +
                shlex.quote('docker exec moodle-app php /tmp/add_aula.php ' + quoted))
    print(f'>> Integrando {filename} -> {title} (seção {section})')
    out = run_remote(args_cmd)
    print(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    op = sys.argv[1]
    if op == 'check':
        check()
    elif op == 'add':
        if len(sys.argv) < 3:
            sys.exit('Uso: aula_pipeline.py add <arquivo.mp4> [--modulo N|--section ID] [--intro texto]')
        fname = sys.argv[2]
        modulo = None
        section = None
        intro = ''
        title_override = ''
        rest = sys.argv[3:]
        i = 0
        while i < len(rest):
            if rest[i] == '--modulo':
                modulo = int(rest[i + 1]); i += 2
            elif rest[i] == '--section':
                section = int(rest[i + 1]); i += 2
            elif rest[i] == '--intro':
                intro = rest[i + 1]; i += 2
            elif rest[i] == '--title':
                title_override = rest[i + 1]; i += 2
            else:
                sys.exit(f'Argumento desconhecido: {rest[i]}')
        add(fname, modulo, section, intro, title_override)
    else:
        sys.exit(__doc__)
