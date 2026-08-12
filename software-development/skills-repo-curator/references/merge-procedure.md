# Merge Procedure — fundir duas skills com o mesmo workflow

Procedimento validado no ciclo de 09/08/2026 (merge `messaging/whatsapp-automation` → `infrastructure/whatsapp-baileys-integration`, 102→101 skills).

## Decisão (quando merge é justificado)

Duas skills conectadas (`similar`/`uses`) merecem merge quando **mesmo domínio + mesma orquestração + uma é superset estrito da outra**. Evidências objetivas:
- Comparar seções (`re.findall(r'^#{1,3} (.+)$', c, re.MULTILINE)`) dos dois SKILL.md — se a maior cobre todas as seções da menor + extras, é superset.
- Comparar tamanho: superset com 3-4x o tamanho da menor é sinal forte.
- Conteúdo único da menor: só migration checklists, pitfalls, tabelas de referência — nada de workflow próprio.

**NÃO mergear** quando as skills têm toolchains diferentes ou níveis de abstração distintos (ex: `selfhost-service-deploy` = padrão genérico p/ qualquer serviço × `selfhost-web-apps` = apps PHP/Python/Node com nginx+hardening — workflows distintos, manter separadas).

## Passos de execução

1. **Preservar references únicos da skill menor**: `cp <menor>/references/* <maior>/references/` — os que já existem na maior podem ser sobrescritos (o da maior é o canônico).
2. **Absorver conteúdo único no SKILL.md da maior**: anexar seções novas (Migration Checklist, Limitations, Rate Limiting, tabela References) antes do fim do arquivo. Apontar os arquivos copiados na seção de references do skill maior.
3. **Atualizar frontmatter da maior**: description menciona o merge ("Absorveu X (merge MM/AAAA): ..."), `timestamp` = hoje. Re-sincronizar `Tamanho:` no index.md (mudou).
4. **Deletar a menor**: `rm -rf <menor-dir>/`; se a categoria ficou vazia, `rmdir` também (ex: `messaging/` sumiu).
5. **Atualizar index.md**:
   - Remover a entry da skill deletada (bloco `###` inteiro).
   - Corrigir relações que apontavam para ela (`similar → <menor>` vira dead target).
   - Atualizar Tamanho/Timestamp/descrição da maior.
   - Decrementar `*Total: N skills*`.
6. **Verificar**: parser de órfãos/bad-targets = 0, audit-descriptions 100% compliant, tamanhos batem com disco.
7. **Grafo**: `python3 scripts/generate_graph.py` — nós e arestas mudam.
8. **Log + commit** com prefixo `evolve`, mencionando o que foi absorvido e preservado.

## Pitfalls do merge

- **Size drift**: cada edição no SKILL.md da maior muda o tamanho — re-sincronizar `Tamanho:` no index.md ANTES do commit final, não depois.
- **Dead relations**: usar `grep -rn "<nome-da-deletada>" --include="*.md" . | grep -v reports/ | grep -v log.md` para achar TODAS as referências restantes antes de commitar. A menção na própria skill maior (documentando o merge) é intencional — as do index.md de OUTRAS skills não são.
- **Diretório de categoria órfão**: depois de remover a última skill de uma categoria, o diretório vazio fica tracked como nothing — `rmdir` e pronto.
- **Verificação final**: o script `_verify_index.py` (write_file temporário, depois `rm`) que parseia órfãos + bad-targets + size-mismatch numa passada só é o checkpoint confiável.
