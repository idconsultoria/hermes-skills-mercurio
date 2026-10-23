# Espelhamento de docs para o Drive — idempotência (CFP IA, ago/2026)

Bug real encontrado ao fechar quinzena: scripts de espelhamento usavam
`--parent <folder>` (cria doc NOVO) para documentos que **já existiam** na pasta
— rodar o script de novo criava DUPLICATAS no Drive.

## Regra: `--doc-id`, nunca `--parent`, em re-execuções

| Flag | Efeito | Quando usar |
|------|--------|-------------|
| `--parent <folder_id>` | Cria doc novo na pasta | SOMENTE na primeira criação; anotar o ID retornado |
| `--doc-id <doc_id>` | Atualiza o doc existente (preserva ID) | Toda re-execução / espelhamento quinzenal |

## Procedimento antes do espelhamento (anti-duplicata)

1. **Listar a pasta-alvo** e mapear docs existentes → IDs:
   ```bash
   python3 -c "
   import json, urllib.request, urllib.parse, importlib.util
   spec = importlib.util.spec_from_file_location('md', '/opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py')
   md = importlib.util.module_from_spec(spec); spec.loader.exec_module(md)
   tok = md.get_token()
   q = urllib.parse.quote(f\"'<FOLDER_ID>' in parents and trashed=false\")
   req = urllib.request.Request(f'https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name)&pageSize=100',
                                headers={'Authorization': f'Bearer {tok}'})
   for f in json.load(urllib.request.urlopen(req)).get('files', []):
       print(f\"  {f['name']} | {f['id']}\")
   "
   ```
2. **Construir o script com `--doc-id`** para tudo que já existe.
3. Rodar em background (anti-429: `sleep 6-8` entre docs).
4. **Verificar zero duplicatas** após o run (mesma listagem, comparar nomes).

## Scripts canônicos do CFP IA

`/opt/data/igor-docs-md/espelhar_gestao.sh`, `espelhar_engenharia.sh`,
`espelhar_design_v2.sh` — corrigidos para `--doc-id` (idempotentes). Rodar os 3
em sequência no fechamento de quinzena; o design v2 também re-renderiza mermaids.

IDs das pastas (Produto no Drive): Gestão `1KKYtedSpNDYTVJENjRk42yHdBB0scHMJ`,
Engenharia `17lBPefqbH4CcbnwFZkJYSeXTLzMIcK-j`, Design
`12J-LRtfjOwErYQzRERl1PkJb8iFghStD`. Conversor:
`/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py`.
