<?php
/**
 * add_aula.php — integra vídeo de aula na página correspondente do curso "Ferramentas de IA" (id=2).
 *
 * Uso: php add_aula.php --name="Titulo da Pagina" --url="https://github.com/.../aula.mp4" [--section=ID] [--intro="texto"]
 *
 * - Se a página (nome normalizado, acento-insensível) existir -> atualiza apenas o content (placeholders).
 * - Se não existir -> cria página nova na seção indicada (obrigatório --section).
 *
 * Template video.js idêntico ao da aula de introdução (Boas-vindas ao Ferramentas de IA!).
 * Container: /var/www/html/public (Moodle 5 usa public/ como web root).
 */
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->libdir . '/moodlelib.php');
require_once($CFG->dirroot . '/course/lib.php');

// CLI não tem sessão — assume o admin (id=10) para ter capability de criar/editar módulos.
\core\session\manager::set_user($DB->get_record('user', array('id' => 10, 'deleted' => 0)));

$opts = getopt('', array('name:', 'url:', 'section:', 'intro:'));
if (empty($opts['name']) || empty($opts['url'])) {
    fwrite(STDERR, "Uso: php add_aula.php --name=NOME --url=URL [--section=ID] [--intro=TEXTO]\n");
    exit(1);
}
$name    = trim($opts['name']);
$url     = trim($opts['url']);
$section = isset($opts['section']) ? (int)$opts['section'] : null;
$intro   = isset($opts['intro']) ? trim($opts['intro']) : '';
$courseid = 2;

// Template video.js — replica exato da intro.
$html = "<p>\r\n<script src=\"https://vjs.zencdn.net/8.16.1/video.min.js\"></script>\r\n</p>\r\n"
      . "<p><video id=\"aula-player\" class=\"video-js vjs-big-play-centered\" preload=\"auto\" controls=\"controls\" data-setup=\"{&quot;fluid&quot;: true,&quot;playbackRates&quot;: [0.5, 1, 1.25, 1.5, 2],&quot;controlBar&quot;: {&quot;pictureInPictureToggle&quot;: false}}\">\r\n"
      . "    <source src=\"$url\" type=\"video/mp4\">\r\n  </video></p>";

// Normalização acento-insensível E pontuação-insensível: "Análise de Dados com IA" casa com
// "Analise-de-Dados-com-IA.mp4"; "Boas-vindas ao Ferramentas de IA!" casa com "Boas-vindas-ao-Ferramentas-de-IA.mp4".
function aula_norm($s) {
    $s = mb_strtolower($s, 'UTF-8');
    $map = array('á'=>'a','à'=>'a','â'=>'a','ã'=>'a','ä'=>'a','é'=>'e','è'=>'e','ê'=>'e','ë'=>'e',
                 'í'=>'i','ì'=>'i','î'=>'i','ï'=>'i','ó'=>'o','ò'=>'o','ô'=>'o','õ'=>'o','ö'=>'o',
                 'ú'=>'u','ù'=>'u','û'=>'u','ü'=>'u','ç'=>'c','ñ'=>'n');
    $s = strtr($s, $map);
    $s = preg_replace('/[^a-z0-9]+/', ' ', $s);
    return trim($s);
}

global $DB;
$normname = aula_norm($name);

$pages = $DB->get_records_sql("SELECT id, name FROM {page} WHERE course = ?", array($courseid));
$target = null;
foreach ($pages as $p) {
    if (aula_norm($p->name) === $normname) { $target = $p; break; }
}

if ($target) {
    $data = (object)array('id' => $target->id, 'content' => $html, 'timemodified' => time());
    if ($intro !== '') {
        $data->intro = $intro;
        $data->introformat = FORMAT_HTML;
    }
    // Garante o espaço da descrição (mesmo padrão da intro: printintro=1, sem "última modificação").
    $data->displayoptions = serialize(array('printintro' => '1', 'printlastmodified' => '0'));
    $DB->update_record('page', $data);
    // Completion manual obrigatório: "aluno deve marcar como concluído" (padrão do curso).
    $cm = $DB->get_record('course_modules', array('course' => $courseid, 'instance' => $target->id, 'module' => $DB->get_field('modules', 'id', array('name' => 'page'))));
    if ($cm && (int)$cm->completion !== COMPLETION_TRACKING_MANUAL) {
        $cm->completion = COMPLETION_TRACKING_MANUAL;
        $cm->completionview = 0;
        $cm->completionusegrade = 0;
        $cm->completionexpected = 0;
        $DB->update_record('course_modules', $cm);
        echo "COMPLETION_MANUAL\n";
    }
    echo "ATUALIZADA page_id={$target->id} nome={$target->name}\n";
    if ($intro !== '') {
        echo "INTRO_DEFINIDA\n";
    }
} else {
    if (!$section) {
        fwrite(STDERR, "Pagina '{$name}' nao existe. Informe --section (M1=2, M2=3, M3=4, M4=5 - ids mdl_course_sections).\n");
        exit(2);
    }
    $moduleinfo = new stdClass();
    $moduleinfo->modulename = 'page';
    $moduleinfo->course = $courseid;
    $moduleinfo->section = $section;
    $moduleinfo->visible = 1;
    $moduleinfo->visibleoncoursepage = 1;
    $moduleinfo->groupmode = 0;
    $moduleinfo->groupingid = 0;
    $moduleinfo->cmidnumber = '';
    $moduleinfo->coursemodule = 0;
    $moduleinfo->instance = 0;
    $moduleinfo->name = $name;
    $moduleinfo->content = $html;
    $moduleinfo->contentformat = FORMAT_HTML;
    $moduleinfo->display = 5;                       // mesmo da intro
    $moduleinfo->printintro = 1;
    $moduleinfo->printlastmodified = 0;
    $moduleinfo->intro = $intro;
    $moduleinfo->introformat = FORMAT_HTML;
    $moduleinfo->introeditor = array('text' => $intro, 'format' => FORMAT_HTML, 'itemid' => 0);
    // Completion manual obrigatório: "aluno deve marcar como concluído" (padrão do curso).
    $moduleinfo->completion = COMPLETION_TRACKING_MANUAL;
    $moduleinfo->completionview = 0;
    $moduleinfo->completionusegrade = 0;
    $moduleinfo->completionexpected = 0;
    $cm = create_module($moduleinfo);
    echo "CRIADA cm_id={$cm->id} page_id={$cm->instance} nome={$name} secao={$section}\n";
}

purge_all_caches();
echo "CACHE_PURGADO\n";
