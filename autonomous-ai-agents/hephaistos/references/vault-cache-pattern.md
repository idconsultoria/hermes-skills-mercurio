# Vault Cache Pattern

## Script de Cache Automatico

O script `scripts/update-cache.sh` atualiza o cache de contexto do vault automaticamente.

### Localizacao
```
~/vaults/hephaistos/scripts/update-cache.sh
```

### Uso
```bash
bash ~/vaults/hephaistos/scripts/update-cache.sh
```

### O que faz
1. Conta arquivos por dominio
2. Gera metricas atualizadas
3. Atualiza `_compact/cache-contexto.md`
4. Inclui timestamp da ultima modificacao

### Output
O arquivo `_compact/cache-contexto.md` contem:
- Total de arquivos
- Engramas por dominio
- Estrutura do vault
- Modos da pipeline
- Regras de ouro
- Arquivos importantes

### Quando usar
- Apos criar/deletar engramas
- Apos migrar projetos
- Apos limpeza de vault
- Periodicamente (semanalmente)

### Integracao com Cron
Pode ser executado via cron job:
```bash
# Atualizar cache toda segunda-feira as 9h
0 9 * * 1 bash ~/vaults/hephaistos/scripts/update-cache.sh
```
