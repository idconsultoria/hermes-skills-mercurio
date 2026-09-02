---
name: moodle-id-operacoes
description: "Operar o Moodle da ID: papéis, aulas estilizadas, fórum."
category: infrastructure
type: Orchestrator
timestamp: 2026-08-26T00:00:00Z
version: 1.0.0
author: "ID Consultoria (Mercúrio / Hermes), 26/08/2026"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [moodle, ead, jornada-de-ia, treinamentos, forum, role-assign, html, identidade-visual, postgres, oracle]
    related_skills: [devops-artemishub, cicd-oracle-preview, google-workspace]
---

# Operações no Moodle da ID — Skill operacional

## When to Use

Carregue quando precisar **operar o Moodle da ID** (`https://treinamentos.idconsultoria.ai`):
criar/corrigir papel de aluno, substituir placeholders de aulas por páginas estilizadas,
criar posts de fórum (avisos / gravações de lives), excluir páginas ou liberar acesso a
pastas do Drive dos cases. Boa para manutenção corrente da *Jornada de IA*.

> ⚠️ **Acesso SSH:** o host é o mesmo do **ArtemisHub** (`129.146.163.107`), e a chave de deploy
> (`references/deploy_key.pem`, escopada ao projeto ArtemisHub) foi **explicitamente autorizada**
> pelo principal para manutenção do Moodle. **Nunca expor a chave** — usar só a conexão.
> Fora desse alcance autorizado, exigir ok explícito do principal.

## 1. Visão geral do ambiente

| Item | Valor |
|---|---|
| URL | `https://treinamentos.idconsultoria.ai` |
| Host | Oracle ARM64 `129.146.163.107`, usuário `ubuntu` |
| Containers | `moodle-app`, `moodle-postgres`, `moodle-nginx`, `moodle-redis`, `moodle-cron` |
| Raiz do código (container) | `/var/www/html/public` (dirroot Moodle) |
| Docroot servido | `/var/www/html/public_web` → simlink para `public` |
| Banco | `moodle` (usuário `moodle`, container `moodle-postgres`) |
| Curso principal | **"Ferramentas de IA"** → `courseid = 2` (contexto de curso `id = 20`) |
| Compose dir (host) | `/home/ubuntu/selfhost/moodle` |
| Backup do banco | `pg_dump -U moodle -d moodle -Fc > backup_moodle_<ts>.dump` em `/home/ubuntu/selfhost/moodle/` |

> Credenciais (admin, DB) vivem em `.env`/env do container — **não reproduzir em chat nem na skill**.

## 2. Executar comandos no host

```bash
K=/opt/mercurio-data/skills/infrastructure/moodle-id-operacoes/references/deploy_key.pem
chmod 600 "$K"
# validar (só a pub, nunca a privada): ssh-keygen -y -f "$K"
timeout 25 ssh -i "$K" -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=15 \
  ubuntu@129.146.163.107 '<comando>'
```

> A chave é **cópia dentro desta skill, ignorada pelo `.gitignore` (`**/references/*.pem`)** —
> nunca comitar. Uso exclusivo em manutenção do Moodle/Jornada de IA.

## 3. Ler / escrever no banco (psql via container)

```bash
docker exec moodle-postgres psql -U moodle -d moodle -Atc "SELECT ..."
```

**Tabelas-chave:** `mdl_course`, `mdl_course_sections`, `mdl_course_modules`,
`mdl_modules`, `mdl_page`, `mdl_forum`, `mdl_forum_discussions` (**plural**!),
`mdl_forum_posts`, `mdl_role_assignments`, `mdl_user_enrolments`, `mdl_user`.

### Mapear módulos de um curso
```sql
SELECT cm.id, m.name AS modname, cm.instance, cm.section
FROM mdl_course_modules cm JOIN mdl_modules m ON m.id=cm.module
WHERE cm.course=2 ORDER BY cm.section, cm.id;
```
- `page` → aulas (placeholders, vídeos, guias estilizados).
- `forum` → comunidades/avisos (ex.: id 1 = "Avisos", id 2 = "Gravações das Lives").

### Alunos matriculados (com email)
```sql
SELECT ue.userid, u.firstname, u.lastname, u.email
FROM mdl_user_enrolments ue JOIN mdl_enrol e ON e.id=ue.enrolid JOIN mdl_user u ON u.id=ue.userid
WHERE e.courseid=2 ORDER BY ue.userid;
```

## 4. ⚠️ Bug recorrente: aluno sem papel (não acessa nada)

**Sintoma:** aluno matriculado mas "não acessa posts das comunidades" e "não consegue marcar
aulas como concluídas". **Causa-raiz:** está em `mdl_user_enrolments` (matriculado) mas
**sem `mdl_role_assignments`** (papel de aluno) no contexto do curso. Sem o papel, não tem
capacidade alguma — nem vê conteúdo, nem conclui, nem acessa fórum.

Diagnóstico:
```sql
SELECT ra.contextid, ra.roleid, ra.userid, u.email
FROM mdl_role_assignments ra JOIN mdl_user u ON u.id=ra.userid
WHERE ra.userid IN (<userids>) ;
-- vazio => falta o papel
```

Correção (papel de aluno = `roleid 5`, contexto do curso = `20`):
```sql
INSERT INTO mdl_role_assignments (roleid, contextid, userid, timemodified, modifierid, component, itemid, sortorder)
SELECT 5, 20, u.id, EXTRACT(EPOCH FROM now())::int, 2, '', 0, 0
FROM mdl_user u WHERE u.id IN (<userids>);
```
Depois: `purge_all_caches()` (ver §7). **Excluir** a conta Admin e o professor de "aluno".

> ✅ **Prefira a API** via PHP (`role_assign`) quando puder — dispara eventos e limpa caches.

## 5. Conteúdo de aula: substituir placeholders por página estilizada

As páginas de aula (`mdl_page`) armazenam HTML em `content` (`contentformat=1` = FORMAT_HTML).

### 🔑 Gotcha crítico do sanitizador do Moodle
`format_text()`/`clean_text()` (executado na exibição para **alunos**) **remove**:
`<style>`, `@import`, `display:flex`, `gap`, `box-shadow`, `box-sizing`, `overflow`,
`background-image`/`linear-gradient`, `align-items/justify-content/flex-wrap`, `display`.

**Propriedades que SOBREVIVEM**: `background` (cor sólida), `border`, `border-left`,
`border-radius`, `border-top`, `color`, `font-*`, `letter-spacing`, `line-height`, `margin`,
`margin-top`, `max-width`, `min-width`, `padding`, `padding-left`, `padding-top`, `text-align`,
`text-decoration`, `text-transform`, `width`.

⇒ **Use 100% estilos inline** (sem `<style>`/`@import`) e **tabelas** para layout lado a lado
(substituem `flex`). Fundo do herói deve ser **cor sólida** (ex.: `#0a1929`), nunca gradiente —
senão texto branco vira invisível.

**Confirmar o que sobrevive** (rodar no dirroot e checar a saída):
```php
$ctx = context_course::instance(2);
$html = format_text($DB->get_record('page',['id'=>6])->content, FORMAT_HTML, $ctx);
```

### Atualizar conteúdo da página
Via PHP (recomendado, dispara eventos corretamente):
```php
$data = new stdClass();
$data->id = $pageid;  // mdl_page.id
$data->content = $html;            // fragmento com estilos inline
$data->contentformat = 1;          // FORMAT_HTML
$data->timemodified = time();
$DB->update_record('page', $data);
purge_all_caches();
```

### Padrão visual da ID (usar nos guias)
- Paleta: teal `#14b8a6` (primária), `#0d9488`, `#0b3d47`, navy `#0a1929`, claros `#5eead4`,
  `#ccfbf1`, `#f0fdfa`.
- Herói: `background:#0a1929; border-top:5px solid #14b8a6; color:#fff`.
- Cartões (`td` de tabela ou `<div>`): `background:#fff; border:1.5px solid #d3eae4;
  border-radius:14px; padding:16px 18px`.
- Títulos seção: `font-weight:800; color:#0a1929; padding-left:14px; border-left:5px solid #14b8a6`.
- Chamada (objetivo): `background:#e6f5f2; border-left:5px solid #14b8a6`.
- Rodapé: `border-top:1.5px solid #e2efec; color:#5b6b7a`.

## 6. Fórum: criar posts (avisos / gravações de lives)

Usar a API `forum_add_discussion` (em `mod/forum/lib.php`). Assinatura:
`forum_add_discussion($discussion, $mform=null, $unused=null, $userid=null)`.

```php
define('CLI_SCRIPT', true);
require(config.php); require clilib; require_once("$CFG->dirroot/mod/forum/lib.php");
global $DB,$USER;
$author = $DB->get_record('user',['id'=>2]);   // professor Gustavo (editingteacher)
$USER = $author;                                // autor/contexto para eventos
$d = new stdClass();
$d->course = 2;
$d->forum  = 1;                                 // 1="Avisos" · 2="Gravações das Lives"
$d->name   = 'Título da discussão';
$d->groupid = 0; $d->timestart = 0; $d->timeend = 0;
$d->message = '<p>Conteúdo <strong>HTML</strong></p>';   // nowdoc para evitar escape
$d->messageformat = 1;                          // FORMAT_HTML
$d->messagetrust  = 1;
$d->mailnow       = 1;                          // notifica inscritos
$id = forum_add_discussion($d, null, null, $author->id);
```

**Conversão de markdown → HTML:** `*texto*` → `<strong>texto</strong>`; bullets `•` → `<ul><li>`;
nota entre parênteses `*(...)*` → `<em>(...)</em>`.

**Nota de autoria:** os posts originais das lives eram da conta Admin (`userid 10`); para a turma,
atribua ao professor Gustavo (`userid 2`) — que assina as mensagens. Consistência é preferência.

## 7. Purga de caches (sempre após alterar conteúdo/papéis)

```bash
docker exec moodle-app sh -c "cd /var/www/html/public && php admin/cli/purge_caches.php"
```
(ou `purge_all_caches();` no fim do script PHP).

## 8. Liberar acesso às pastas dos cases no Drive

As pastas dos cases ficam sob a pasta "Cases" do Drive da ID. Para os guias de aula, linkar e
compartilhar as pastas **Prática 1** e **Prática 2** com os **emails dos alunos** (papel leitor).

```bash
GAPI="python3 /opt/mercurio-data/skills/productivity/google-workspace/scripts/google_api.py"
export HERMES_HOME=/opt/mercurio-data
$GAPI drive share <FOLDER_ID> --email <aluno> --role reader
```

> ⚠️ **Email sem Conta Google** (ex.: `comercial@...`) → o `drive share` falha com 400
> (`invalidSharingRequest`). Acrescentar `--notify` para convidar via e-mail.

**Conferir as permissões** (o `drive get` do wrapper não devolve o campo `permissions`):
listar via API com `files/<id>/permissions?fields=permissions(emailAddress,role,type)`.

## 9. Excluir uma página/atividade (ex.: análise de dados integrada)

Usar a API nativa — **não** deletar linhas à mão (deixa grade/completion órfãos):
```php
require_once("$CFG->dirroot/course/lib.php");
$cmid = (int)$DB->get_field('course_modules','id',['course'=>2,
  'module'=>(int)$DB->get_field('modules','id',['name'=>'page']),'instance'=>$pageid]);
course_delete_module($cmid);
```

## 10. Pitfalls

| Sintoma | Causa | Correção |
|---|---|---|
| Fundo branco/fonte normal no conteúdo de aula | `<style>`/`@import` removidos pelo sanitizador | usar **estilos inline** + tabelas |
| Título do herói invisível | `background:linear-gradient` removido | fundo **sólido** `#0a1929` |
| Cards não em coluna | `display:flex` removido | **tabela** `<table>`/`<td>` para grid |
| Aluno "não acessa" comunidades/conclusão | falta `mdl_role_assignments` (papel aluno) | INSERT `roleid=5` no contexto do curso |
| `mdl_forum_discussion` não existe | nome da tabela é **plural** `mdl_forum_discussions` | usar o nome correto |
| `drive share` 400 para email sem conta Google | `invalidSharingRequest` | usar `--notify` |
| `pg_restore: unsupported version` | dump de PG17 em PG16 | imagem `postgres:17-alpine` |

## 11. Verificação pós-operação

1. **Papéis:** `SELECT roleid,count(*) FROM mdl_role_assignments WHERE contextid=20 GROUP BY roleid;`
   → deve haver alunos (`5`) além do professor (`3`).
2. **Conteúdo de aula:** render de `format_text` do `content` da página → ausência de `<style>`,
   presença dos `style=` inline e dos links.
3. **Fóruns:** `SELECT fd.id,fd.forum,fd.name,u.email FROM mdl_forum_discussions fd JOIN
   mdl_user u ON u.id=fd.userid ORDER BY fd.id;` → posts e autores corretos.
4. **Drive:** listar `permissions` das pastas → emails dos alunos como `reader`.
5. **Backup** criado antes de alterações reversíveis, ou restauração de `backup_moodle_<ts>.dump` se necessário.

## 12. Nota de governança

- A chave de deploy é do **ArtemisHub**; uso no Moodle foi **autorização explícita do principal**
  (registrada na memória). Voltar a configurar o escopo se o principal revogar.
- **Nunca** imprimir credenciais (admin/DB) nem a chave privada em resposta/chat.
- A cópia da chave nesta skill é gitignorada (`**/references/*.pem`) — nunca commitar.
