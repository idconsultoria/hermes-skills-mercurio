---
name: dns-dominios-id
description: "Use quando um nome/domínio da ID não resolve no DNS.

Carregue esta skill quando um nome da ID não abrir, servir versão antiga ou parecer banco perdido — diagnóstico NXDOMAIN vs serviço, inventário de registros Hostinger e procedimento de verificação em dois provedores."
category: infrastructure
type: Reference
timestamp: 2026-10-10
metadata:
  hermes:
    tags: [dns, hostinger, hostname, diagnostico, oracle-host, vercel, cache-pwa]
    related_skills: [devops-artemishub, cicd-oracle-preview, stack2-mesh-failback]
---

# DNS dos domínios da ID — verificar, diagnosticar, corrigir

## When to Use

Carregue quando um nome da ID **não abre** ("o site sumiu", "abre versão antiga", "o banco
sumiu", "o link não funciona"), quando alguém pergunta se um subdomínio existe/foi removido,
ou quando um registro precisa ser criado/restaurado e o Mercúrio **não tem acesso ao painel
da zona**. Caso real: `artemis.idconsultoria.ai` e `treinamentos.idconsultoria.ai` (Moodle)
perderam o registro na mesma edição de zona e o usuário só recebia o cache do PWA — parecia
"banco perdido", com os serviços sãos no host.

## 1. Regra de ouro

**NXDOMAIN ≠ serviço fora.** Sem registro, quem já visitou o nome é atendido pelo **cache do
PWA/site antigo** — o sintoma chega como "build velho", "sem dados" ou "banco perdido"
enquanto o host está servindo normalmente. Sempre resolva a camada de nome **antes** de
investigar aplicação, banco ou deploy.

## 2. Inventário — nomes que devem resolver para `129.146.163.107`

| Nome | Serviço | Registro esperado |
|---|---|---|
| `artemis.idconsultoria.ai` | ArtemisHub (produção) | A → 129.146.163.107, TTL 300 |
| `*.artemis.idconsultoria.ai` | preview por PR | A → 129.146.163.107, TTL 300 |
| `treinamentos.idconsultoria.ai` | Moodle da ID | A → 129.146.163.107, TTL 300 |

- Zona `idconsultoria.ai` na **Hostinger** (`ns1/ns2.dns-parking.com`). O Mercúrio **não tem
  acesso** ao painel: o entregável é o **pedido exato** ao dono da conta.
- Apex e `www` apontam para a **Vercel** — não mexer.
- **Apex na Vercel em OUTRO escopo:** o nome resolve para a Vercel (cabeçalho `X-Vercel-Id` no
  `curl -I https://<apex>/`), mas o domínio pertence a outra conta: `vercel domains add
  <sub>.<apex> <projeto>` responde `403 Not authorized to use …`. Subdomínio só se anexa a
  projeto da conta que controla o domínio. Antes de prometer URL bonita, rode `vercel domains ls`
  para ver o que o escopo atual controla. Saídas: (a) anexar o domínio na conta dona, (b) ser
  convidado para essa conta / mover o projeto para ela, (c) usar a URL
  `<projeto>-<hash>.vercel.app`. O nome do projeto também é global: nome já usado por outra conta
  vira `<projeto>-<sufixo>.vercel.app` e a URL limpa não pode ser reivindicada.
- Subdomínio apontando para a Vercel (quando o domínio é do dono): **CNAME · nome `sub` · valor
  `cname.vercel-dns.com` · TTL 300**.
- Nomes que já apareceram em certificados (`atlas`, `dashboard`, `evento`, `manifesto`) **não
  são** registros vivos por isso; só recriar se alguém confirmar que o serviço existe.

## 3. Procedimento

1. **Rodar** `scripts/verificar-dns-id.py` (ou consultar DoH em 2 provedores — snippet em
   `references/dns-e-nomes-do-host.md`). `Status: 3` = NXDOMAIN. Um provedor só não basta:
   caches divergem por minutos.
2. **Separar DNS de serviço**, furando o DNS e falando direto com o proxy do host:
   `curl -sk --resolve <nome>:443:129.146.163.107 -o /dev/null -w '%{http_code}\n' https://<nome>/`
   → `200`/`303` com o nome sem registro = proxy host e certificado intactos; falta só o
   registro. Reserve o diagnóstico de app para depois disso.
3. **Montar o pedido de correção** com os campos exatos, um registro por linha
   (tipo A · nome · valor · TTL 300), mais o caminho no painel e o comando de conferência.
   Pedir junto ao suporte Hostinger o **histórico de alterações da zona** — o DNS não
   registra quem mudou, e essa é a única forma de saber quem apagou.
4. **Verificar depois da mudança** (é o que autoriza dizer "resolvido"): resolução nos 2
   provedores após alguns minutos (cache negativo do NXDOMAIN dura o SOA minimum, ~600 s),
   HTTP 200 + `/api/health`, hash do asset servido igual ao do container, Moodle/login
   respondendo, e preview `<n>.artemis` — erro de TLS sem PR aberto é esperado.
5. **Encerrar avisando do cache**: recarga forçada (Ctrl+Shift+R; no celular, fechar e
   reabrir o app). Sem isso o usuário continua vendo a versão antiga e reabre o chamado.
6. **Registrar** o achado na KB (`kb_note`, proposta) quando o fato for novo: nome removido,
   quem foi avisado, o que falta. E se outro sócio/cliente depende do nome, mandar o recado
   (skill `id-comunicacao-multiusuario`, seção de relay), sem encanamento para não-Gustavo.

## 4. Formato da resposta ao dono da zona

- **Correção primeiro.** Se uma afirmação anterior sua se provou errada (ex.: apresentar
  nomes de certificado como "conteúdo da zona"), corrija em uma linha antes dos passos e diga
  o que a verificação mudou. Admissão vale mais que aparência de impecabilidade.
- **Passo a passo numerado, um passo = uma ação**, com o valor exato a digitar em cada campo
  (`Tipo: A` · `Nome: artemis` · `Aponta para: 129.146.163.107` · `TTL: 300`) — sem "configure
  o DNS" genérico, sem pré-requisito implícito.
- Diga **o que não fazer** (não mexer em nameservers nem no apex/`www`) e o que o TTL muda
  (só a velocidade de propagação).
- Feche com o **comando de conferência** e uma oferta única de próximo passo ("me avise quando
  criar que eu confirmo a resolução").

## 5. Pitfalls

- **Lista de certificados (crt.sh) não é lista de registros.** Transparência de certificado
  guarda nomes que tiveram cert — inclusive de registros já removidos e projetos encerrados.
  Só a consulta de resolução vale como prova: conferir antes de afirmar que um subdomínio
  existe ou foi apagado.
- **Wildcard em certificado antigo** (`*.idconsultoria.ai`) não implica wildcard na zona, e o
  wildcard **não cobre o nome puro**: `artemis` e `*.artemis` são registros distintos.
- **Não declarar falha no minuto seguinte à criação.** O NXDOMAIN fica em cache negativo
  (~600 s); um provedor passa a resolver antes do outro. Reconferir após alguns minutos, em
  dois provedores.
- **Teste com DNS quebrado ainda "passa"** se você usar `--resolve`: esse truque prova o host,
  não a zona. Só a resolução limpa fecha o caso.
- **Cache do usuário mascara o resultado** — sem recarga forçada/relançar o app, o "ainda está
  quebrado" pode ser PWA.
- **Atualizar a URL de deploy "daquele" projeto exige credencial do escopo que publicou.**
  Projeto publicado por CLI pertence à conta que rodou o comando: de outro escopo nem aparece em
  `vercel project ls`, e o deploy novo vai para um projeto novo (URL nova). Para manter a URL
  antiga, reconecte o repositório na conta dona do projeto e redeploye de lá, ou traga o projeto
  para o escopo atual. Diga isso ao usuário como bloqueio com caminho, não como "não dá".

## 6. Arquivos de apoio

- `references/dns-e-nomes-do-host.md` — inventário, snippets DoH, `--resolve`, comparação de
  hash do build servido, campos do painel Hostinger e roteiro de verificação pós-mudança.
- `scripts/verificar-dns-id.py` — checagem re-executável do inventário (2 provedores, sai com
  código ≠ 0 no primeiro nome sem o IP esperado). Bom para rodar após qualquer edição de zona
  e em varredura periódica, para pegar registro sumido no mesmo dia.
