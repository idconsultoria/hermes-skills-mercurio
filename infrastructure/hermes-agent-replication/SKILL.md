---
name: hermes-agent-replication
description: "Replicar instância Hermes (rama ID) numa VM nova."
category: infrastructure
type: Method
timestamp: 2026-08-22T00:00:00Z
---

# Hermes Agent — replicação de instância (rama na VM nova)

Usar quando o principal pedir para **copiar/portar/subir um agente Hermes** (Mercúrio,
rama canônica, um novo branch ID) numa **máquina virtual diferente**, mantendo as mesmas
tecnologias. Também aplica a qualquer pedido de "me passe a stack/dependências/instruções
do meu agente".

## Regra da ID que governa tudo

> **Replicar processo = conferir base/conhecimento antes; padrão ausente = avisar, não inventar.**

Nunca elabore o guia "de memória" ou de um template genérico. **Levante o ambiente real**
antes de escrever: config.yaml, `.env` (SÓ os nomes das chaves), skills, plugin context-kb,
venvs, scripts, cron, motores. Equivalente só existe se conferido contra o vivo.

## Metodologia (7 passos)

1. **Recon estrutural** — `ls -la` de `$HERMES_HOME`; leia `config.yaml` por inteiro; liste
   `.env` extraindo **apenas os nomes** (`while IFS='=' read -r k v; do case "$k" in ''|\#*) continue;; esac; echo "$k"; done < .env`) — nunca os valores.
2. **Ferramentas próprias** — skills (`skill_view hermes-agent`, `id-design-guide` no caso de
   entrega visual), remotes git de `skills/` e `context-kb/`, `plugins/`, venvs+`pip list`,
   `cron/jobs.json`, motores (ex.: `id-nfse-motor/Dockerfile` + `requirements.txt`). Bata
   `git -C <dir> remote -v` para achar as origens replicáveis.
3. **Decida o produto de entrega**. Para o principal da ID, **entregue SEMPRE em HTML** na
   identidade da ID (`id-design-guide`: teal `#4AC6D3`, navy `#050a0f` gradient, Bricolage
   Grotesque/Nunito, zero emoji — ícones SVG inline). Nome com versão, sem reutilizar nome.
4. **Escreva o guia em blocos** (ver pitfall da chunked-write abaixo).
5. **Segredos como BOM** — liste chaves, não valores; instrua rotacionar na VM nova.
6. **Verifique o arquivo** — `wc -c`, parser HTML, fechamento de tags antes de entregar.
7. **Entregue** via `MEDIA:/path` + resumo enxuto no chat apontando os pontos que exigiram
   decisão do principal.

## Pitfalls

- **write_file gigante estoura o stream.** Escrever um HTML grande numa única chamada causa
  timeout de stream. Fix: escreva o cabeçalho (`<head>`+CSS) numa 1ª `write_file`, depois
  **anexe seções via `patch` sequenciais**, usando como forra o texto final de cada bloco e
  trocando-o por si mesmo + a seção nova. Mantenha cada chamada **< ~8K tokens**. Encerre com
  `</body></html>` no último bloco.
- **Diretório de entrega sem permissão.** No container do Mercúrio, `/opt/data/deliverables`
  é de root e **não é gravável**; use `/opt/data/entregas/` (hermes:hermes). Confirme com
  `ls -la` o dono antes de escrever.
- **Mudanças locais não-commitadas em skills** (working tree ≠ origin/master). Decida — e
  deixe explícito no guia — se replica commitado ou working-tree. Recomendação: sincronizar/commit
  antes de clonar na VM nova.
- **Arquitetura da VM alvo.** Produção é ARM64 (Oracle). Se a VM nova for x86_64, ajustar
  imagens Docker (base/tirith/nfelib) e revalidar build do motor.
- **Daemon Docker fora do alcance** do container de produção — builds de imagem de SO rodam
  no host (via rama canônica). Na VM nova, fundar a imagem antes de subir.
- **Pendências conhecidas do ambiente** (ex.: certificado A1 NFS-e expirado; iData/Inter com
  falha de auth) devem ser registradas como aviso, nunca como "tudo pronto".

## Checklist de validação (VM nova)

- `hermes doctor` sem erros críticos · `hermes config check` limpo · python 3.13 / node v26.
- Gateway Telegram conectado, bot correto, allow-list de DM aplicada.
- Plugin context-kb respondendo (`kb_status` mostra páginas `scope:id`).
- /skill `hermes-agent` e `id-design-guide` carregam · memória persistente ativa.
- Modelo default + fallback respondendo · cron jobs recriados com schedule certo.
- Isolamento: nada fora do ecossistema ID acessível.

## Referências

- `references/mercurio-stack-v1.md` — inventário concreto do ambiente do Mercúrio levantado
  em 22/08/2026 (config chave, chaves .env, skills, cron, motores) — fonte para uma cópia 1:1.