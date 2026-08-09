<?php
/**
 * set-user-picture.php — define a foto de perfil de um usuário Moodle a partir de um draft.
 *
 * Uso (via pipe no container, padrão add_aula.php):
 *   cat set-user-picture.php | ssh oracle-host 'docker exec -i moodle-app sh -c "cat > /tmp/set-user-picture.php && php /tmp/set-user-picture.php --userid=10 --fileid=5528"'
 *
 * --userid: id do usuário em mdl_user (ex.: admin=10)
 * --fileid: id do arquivo em mdl_files (filearea 'draft') — o draft criado quando o upload
 *           pela UI "falhou silenciosamente" continua no banco; reaproveite-o.
 *
 * Por que existe: Moodle 5.2 NÃO tem user_update_picture(). O fluxo de referência é o do
 * auth/lti: copy_content_to_temp() -> process_new_icon() -> set_field(user, picture).
 * GIF animado/otimizado quebra process_new_icon com "imagecolorsforindex(): Argument #2
 * out of range" — este script converte o 1º frame para PNG truecolor antes de processar.
 */
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->libdir . '/filelib.php');
require_once($CFG->libdir . '/gdlib.php');

$opts = getopt('', array('userid:', 'fileid:'));
$userid = isset($opts['userid']) ? (int)$opts['userid'] : 0;
$fileid = isset($opts['fileid']) ? (int)$opts['fileid'] : 0;
if (!$userid || !$fileid) {
    fwrite(STDERR, "Uso: php set-user-picture.php --userid=N --fileid=M\n");
    exit(1);
}

$fs = get_file_storage();
$file = $fs->get_file_by_id($fileid);
if (!$file) {
    fwrite(STDERR, "FILE_NOT_FOUND\n");
    exit(2);
}

$temp = $file->copy_content_to_temp();
if (!$temp) {
    fwrite(STDERR, "COPY_TEMP_FAILED\n");
    exit(3);
}

// GIF: GD lê só o 1º frame; converte para PNG truecolor para evitar erro de paleta indexada.
$input = $temp;
$png = null;
if ($file->get_mimetype() === 'image/gif') {
    $src = @imagecreatefromgif($temp);
    if ($src) {
        $w = imagesx($src);
        $h = imagesy($src);
        $rgb = imagecreatetruecolor($w, $h);
        imagealphablending($rgb, false);
        imagesavealpha($rgb, true);
        $transparent = imagecolorallocatealpha($rgb, 0, 0, 0, 127);
        imagefilledrectangle($rgb, 0, 0, $w, $h, $transparent);
        imagecopy($rgb, $src, 0, 0, 0, 0, $w, $h);
        $png = tempnam(sys_get_temp_dir(), 'pic') . '.png';
        if (imagepng($rgb, $png)) {
            $input = $png;
        }
        imagedestroy($src);
        imagedestroy($rgb);
    }
    unlink($temp);
}

$context = context_user::instance($userid, MUST_EXIST);
$newpicture = (int) process_new_icon($context, 'user', 'icon', 0, $input);
if ($png) {
    @unlink($png);
}

if (!$newpicture) {
    fwrite(STDERR, "PROCESS_FAILED\n");
    exit(4);
}

$DB->set_field('user', 'picture', $newpicture, array('id' => $userid));
echo "PICTURE_OK picture={$newpicture}\n";
