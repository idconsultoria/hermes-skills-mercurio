# F4e Review Loop — Sync Sequence

> Capturado da experiência VERO (Jul 2026): agy reprovou iteração 2 não por bugs no código, mas porque o shared volume estava stale.

## O problema

Pi salva arquivos em `/opt/data/<projeto>/product/` (clone local). agy SEMPRE lê de `/home/ubuntu/selfhost/shared/code/workstation/<projeto>/product/` (shared volume). Se a sincronização for feita só no deploy, agy vê código antigo e reporta "NÃO RESOLVIDO".

## Sequência correta por iteração do loop de revisão

### ITERAÇÃO 1: agy revisa → Pi corrige

```bash
# 1. agy revisa (lê shared volume)
ssh oracle-host '/home/ubuntu/.local/bin/agy --print "$(cat /tmp/agy-review.md)" --dangerously-skip-permissions'

# 2. Pi corrige (salva no path local)
pi --name "projeto-fix" -p "$(cat prompts/pi-fix.md)" --provider opencode-go --model deepseek-v4-pro

# 3. Sincronizar local → shared volume (CRÍTICO)
cp /opt/data/<projeto>/product/design/js/app.js /opt/data/code/workstation/<projeto>/product/design/js/app.js
cp /opt/data/<projeto>/product/design/js/router.js /opt/data/code/workstation/<projeto>/product/design/js/router.js
cp /opt/data/<projeto>/product/design/js/views/*.js /opt/data/code/workstation/<projeto>/product/design/js/views/

# 4. Build (do path local) + deploy
cd /opt/data/<projeto>/product/design && bash build.sh
cd /opt/data/<projeto> && vercel build --prod --yes && vercel deploy --prebuilt --prod --yes
```

### ITERAÇÃO 2: agy re-revisa

```bash
# Agora o shared volume tem o código corrigido → agy vê as correções
ssh oracle-host '/home/ubuntu/.local/bin/agy --print "$(cat /tmp/agy-confirm.md)" --dangerously-skip-permissions'
```

## Checklist pós-Pi (antes de invocar agy)

```bash
# Verificar que cada arquivo modificado pelo Pi está em AMBOS os paths
for f in app.js router.js views/compras.js views/admin.js; do
  local_mtime=$(stat -c %Y /opt/data/<projeto>/product/design/js/$f 2>/dev/null)
  shared_mtime=$(stat -c %Y /opt/data/code/workstation/<projeto>/product/design/js/$f 2>/dev/null)
  if [ "$local_mtime" -gt "$shared_mtime" ]; then
    echo "⚠️  $f: local mais recente que shared — sincronizar!"
  fi
done
```

## Por que isso importa

Sem essa sincronização, cada iteração do loop agy→Pi→agy perde uma rodada:
- Iteração 1: agy encontra issues → Pi corrige → shared volume NÃO atualizado
- Iteração 2: agy vê código antigo → reporta "NÃO RESOLVIDO" → Pi corrige de novo (desnecessário)
- Iteração 3: agora compartilhado → agy aprova

Resultado: 3 iterações em vez de 2, ~5-8 minutos extras de tokens.
