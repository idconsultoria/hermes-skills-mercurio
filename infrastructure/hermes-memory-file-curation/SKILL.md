---
name: hermes-memory-file-curation
description: "Use ao compactar MEMORY.md/USER.md acima do limite."
category: infrastructure
type: Reference
timestamp: 2026-10-14T00:00:00Z
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [memória, MEMORY.md, USER.md, limite, compactação, perfis]
    related_skills: [hermes-session-forensics, id-comunicacao-multiusuario]
---

# Curar e compactar os arquivos de memória do Hermes

Carregar quando: aparece no log `USER.md exceeds its char limit on load: N/M chars. Entries stay
loaded; further additions are blocked until it is back under the limit.` (o mesmo vale para `MEMORY.md`);
quando o agente não consegue mais gravar memória; ou quando o dono pede para "corrigir/compactar"
um arquivo de memória.

## O que o limite faz (e por que o sintoma é silencioso)

- Limites em `config.yaml` da raiz do `HERMES_HOME`: `memory.memory_char_limit` (default **2200**)
e `memory.user_char_limit` (default **1375**).
- O loader **nunca trunca**: o arquivo estourado entra inteiro no prompt e apenas as gravações
(subsequentes) são recusadas. Por isso ninguém percebe até um add falhar.
- Arquivos: `$HERMES_HOME/memories/{MEMORY.md,USER.md}` (perfil da raiz) e
`$HERMES_HOME/profiles/<nome>/memories/{MEMORY.md,USER.md}`. Entradas separadas por uma linha `§`.

## Procedimento

1. **Inventarie antes de mexer** — tamanho em chars de todos os arquivos de memória da instalação
   (raiz + perfis), ordenado do maior para o menor. Sem esse mapa, você compacta o que não estoura.
2. **Leia o arquivo inteiro** e liste mentalmente as regras que ele carrega (cada bullet é uma
   regra de trabalho, não texto decorativo).
3. **Reescreva em blocos separados por `§`**, mantendo **todas** as regras e cortando só a redação.
   Se algo não couber, **pare e pergunte**: apertar mais ou subir `memory.user_char_limit`.
4. **Meça ANTES de gravar**, em Python, com `assert len(novo) <= limite` e folga real (não 1 char).
   Itere o texto até fechar — é mais rápido que gravar e remedir.
5. **Backup versionado** ao lado (`USER.md.bak-<YYYYMMDD-HHMM>`), nunca reaproveitando nome.
6. **Grave** e **verifique com o carregador real** — não com estimativa: `scripts/check_memory_limits.py`
   instancia o `MemoryStore` do Hermes contra o disco e mostra `chars/limite`, nº de entradas,
   caminho do arquivo e se há bloqueio. O sucesso é **não** ver o aviso de estouro.
7. **Leia de volta** o arquivo gravado e confirme que nenhum bloco foi truncado.

## Como comprimir sem perder regra

- **Telégrafo**: cortar artigos, "por favor", repetições e conectivos; bullets longos viram linhas
  densas. O ganho típico é de 55–60% em relação ao original.
- **Preservar os discriminantes**, cortar os exemplos redundantes: regra que evita erro real
  (ex.: identificador de chat de sócio cujo nickname ≠ nome) fica; lista de três exemplos do mesmo
  padrão vira um.
- **Nunca resolver estouro removendo regra.** Regra removida não volta e o erro volta em silêncio.
- Manter o cabeçalho curto (1 linha) e agrupar por assunto — cabeçalho ocupa orçamento igual.

## Pitfalls

- **Usar `len()` do arquivo como prova de sucesso.** Meça pelo `MemoryStore`: ele deduplica
  entradas (primeira ocorrência vence) e é quem decide o bloqueio.
- **Tentar reescrever tudo com a tool `memory`.** Ela é de `add`/`replace` de entradas, não de
  reescrita integral — para compactar, edite o arquivo e valide pelo store.
- **Deixar folga de poucos chars.** Com 5 chars de folga o próximo add falha igual; combine com o
  dono subir o limite ou apertar mais.
- **Editar memória de perfil alheio sem ok.** Ler é livre; escrever exige ok explícito do dono
  daquele perfil (e backup + leitura de volta).
- **Confundir os dois arquivos**: `USER.md` = quem é o interlocutor e como falar com ele;
  `MEMORY.md` = notas de ambiente/convenção do agente. Limites diferentes, públicos diferentes.

## Acesso e escrita

Leitura de qualquer `memories/` é parte da apuração. Escrita no próprio perfil é rotina (com backup);
na raiz e em perfis alheios, só com ok explícito.

## Scripts

- `scripts/check_memory_limits.py` — verificação re-executável dos limites via `MemoryStore` real
  (exit 1 se algum alvo estiver estourado).
