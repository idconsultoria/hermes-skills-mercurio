---
name: nda-confidencialidade-id
description: "Use ao redigir NDA/sigilo da ID (código de cliente)."
version: 1.0.0
author: Mercúrio · ID Consultoria
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [nda, confidencialidade, sigilo, contratos, id-consultoria, lgpd, propriedade-intelectual]
    related_skills: [contratos-justos-id, direito-empresarial-brasileiro, analise-contratual, md-to-timbrado-id, formalizacao-acordo-cliente]
type: Orchestrator
timestamp: 2026-10-30T00:00:00Z
---

# NDA e confidencialidade — contratos de sigilo da ID

## Quando usar

Sempre que a ID **recebe** ativo sensível de terceiro e precisa de segurança jurídica para olhar:
código-fonte de cliente (iOS/Android, web, firmware), repositórios, credenciais e certificados de
loja, bases de dados, documentação técnica, planilhas financeiras — em análise técnica, diagnóstico,
auditoria, due diligence ou processo de publicação/atualização em App Store e Google Play.

Também quando o cliente pede "um contrato de confidencialidade" antes de abrir o material, ou quando
o principal já está com o acesso prometido e precisa do papel **rápido**.

**Não é** substituto de: `contratos-justos-id` (regras gerais do contrato justo da ID),
`analise-contratual` (quando a ID recebe minuta alheia), `formalizacao-acordo-cliente` (envio).
É o esqueleto do instrumento de sigilo e o jeito de entregá-lo rápido.

## Regime: unilateral, e isso é a favor da ID

Num NDA de acesso a código de cliente, **só o cliente divulga e só a ID se obriga**. Chame as partes
de CONTRATANTE / PARTE DIVULGADORA e CONTRATADA / PARTE RECEPTORA, deixe claro no objeto que o
acesso é **exclusivo** para a finalidade nomeada (ex.: avaliar o app e conduzir a publicação nas
lojas), e inclua a cláusula de que o NDA **não obriga a executar o serviço** — escopo, prazo e preço
virão em contrato próprio. Sem isso o cliente presume que o NDA já é o contrato de serviço.

Fundamento a citar: arts. 421, 422 e 425 do Código Civil e Lei 9.279/1996 (concorrência desleal).

## Esqueleto de cláusulas (ordem que funciona na leitura)

1. **PARTES** — qualificação completa das duas, CNPJ da ID 54.569.818/0001-59, sócio-administrador
   que assina e tem poderes.
2. **EM RESUMO** (box de 1 parágrafo) — o que o cliente entrega, o que a ID pode e não pode fazer,
   quem fica com a propriedade, por quanto tempo o sigilo dura. É o que faz o cliente assinar sem
   advogado.
3. **OBJETO** — lista fechada do material (código-fonte das versões, dependências e configs de
   build, contas/credenciais de publicação, certificados e chaves de assinatura, fichas de loja,
   documentação, relatórios de falha) + finalidade exclusiva + não obrigação de prestar o serviço.
4. **INFORMAÇÃO CONFIDENCIAL** — definição ampla por suporte/meio e extensão aos derivados
   (anotações, diagnósticos, cópias produzidos pela CONTRATADA).
5. **OBRIGAÇÕES** — sigilo com padrão próprio; uso só para a finalidade; acesso restrito a
   profissionais vinculados a dever equivalente (com responsabilidade da ID por eles); não copiar
   além do necessário; vedação de engenharia reversa salvo o necessário à análise autorizada; não
   divulgar/ceder/portfólio/case/palestra; não explorar comercialmente nem registrar PI; **vedação de
   subir a informação em IA pública ou de terceiros que retenha/treine**; incidente em **24 h**;
   controle de acesso e devolução/revogação de credenciais.
6. **EXCLUSÕES** — domínio público sem culpa, conhecimento anterior comprovado, terceiro legítimo,
   desenvolvimento independente, ordem legal/judicial com aviso prévio quando possível.
7. **PROPRIEDADE INTELECTUAL** — tudo permanece do cliente; nenhuma licença; a ID pode usar
   método/know-how próprio **sem revelar** informação confidencial; e a cláusula que mais protege a
   ID: **material recebido "no estado em que se encontra"**, análise não é auditoria de segurança,
   conformidade ou licenciamento — achados são comunicados como observação, sem obrigação de corrigir.
8. **LGPD** — ID como **operadora**, cliente como controladora; vedada extração/retenção de bases
   mesmo em ambiente de teste; incidente em 24 h; eliminação ao final.
9. **PRAZO** — vigência declarada (recomendar 12 meses) + sigilo de **5 anos** após o término e
   **prazo indeterminado** para código-fonte, segredos de negócio e credenciais enquanto não forem
   públicos.
10. **DEVOLUÇÃO/ELIMINAÇÃO** — 10 dias, incluindo repositórios locais, builds e backups, com
    certificação por escrito; troca das credenciais pelo cliente.
11. **RESPONSABILIDADE** — perdas e danos na medida da culpa + multa por evento não compensatória
    (sugerir R$ 20.000, ou 2x o valor do serviço quando houver), respeitado o teto do art. 412 do CC;
    fortuito/força maior ressalvados.
12. **NÃO EXCLUSIVIDADE E INDEPENDÊNCIA** — sem vínculo empregatício/societário, equipe própria.
13. **DISPOSIÇÕES GERAIS** — e-mails de comunicação, cessão só com anuência, aditivo escrito,
    tolerância não novação, nulidade parcial, assinatura eletrônica válida (MP 2.200-2/2001, art. 10,
    §2º), **foro da Comarca de Aracaju/SE**, 2 testemunhas.

Extensão de prazo, valor de multa e data de assinatura são **decisão do principal** — apresente com
recomendação, não como fato consumado.

## Entrega: rápida, com pendências explícitas

O principal costuma estar no meio de uma conversa com o cliente e com urgência. Entregue **o
documento completo** (nunca pela metade) e, no chat, a lista do que falta, separada por dono:

1. **No documento**, todo dado faltante é placeholder `«...»` nomeado: `«RAZÃO SOCIAL COMPLETA»`,
   `«CNPJ»`, `«ENDEREÇO COMPLETO»`, `«NOME DO REPRESENTANTE LEGAL»`, `«RG/órgão emissor»`,
   `«CPF»`, `«SÓCIO ADMINISTRADOR»`, `«data» de «mês» de «ano»`, `«R$ (valor)»`, `«X» (meses)`.
   Preencha o que a casa já sabe (CNPJ da ID) para reduzir pendência.
2. **Na resposta**, três blocos numerados: o que **pedir ao cliente** (qualificação da empresa +
   representante legal + e-mail oficial); o que o principal **confirma da ID** (razão social
   completa, endereço da sede, sócio que assina + CPF, e-mail de comunicações); o que é **decisão
   dele**, já com recomendação (vigência, multa). Feche oferecendo o texto pronto para colar no
   WhatsApp do cliente.
3. **Formato**: papel timbrado da ID, Google Docs nativo — receita e pitfalls em
   `md-to-timbrado-id` (`scripts/md_to_timbrado_id.py`); para NDA, `--tipo` =
   "CONTRATO DE CONFIDENCIALIDADE E NÃO DIVULGAÇÃO (NDA)", `--titulo-res` curto (ex.:
   "CONFIDENCIALIDADE E NÃO DIVULGAÇÃO") e `--cliente` "<Cliente> × ID Consultoria". Alvo de 4 a 7
   páginas de corpo; capa e contracapa vêm do modelo.
4. **Verifique antes de declarar pronto**: exportar PDF e conferir contagem de páginas e a primeira
   página de corpo (`pdfinfo` + `pdftotext -layout`). Placeholder não é defeito; cláusula sem
   placeholder, sim.

## Pitfalls

- **Marcador de lista na coluna 1 (`1)`, `2)`, `1.`) é engolido pelo preparador de markdown** e
  funde as linhas num parágrafo só (duas linhas de testemunhas viram uma). Escreva o rótulo em prosa:
  `**Testemunha 1** — «Nome» — CPF «CPF».` numa linha e a 2 na seguinte. Vale para qualquer
  documento da ID que passe pelo motor md→gdoc.
- **`prepara_md.py` recebe pares `origem.md=destino.md`**, não arquivo solto; e é o **destino** que
  alimenta o motor. Leia o relatório de "parágrafos curtos" que ele imprime — é onde aparecem as
  linhas juntadas indevidamente.
- **Não prometa que a ID "não vai fazer nada de errado" em prosa solta.** O pedido do cliente vira
  obrigação escrita: cada garantia dada no WhatsApp precisa existir como cláusula (uso exclusivo,
  não cópia, devolução), senão é conversa sem prova.
- **O NDA não autoriza a ID a publicar nada em nome do cliente.** Acesso a código ≠ mandato para
  operar contas de App Store/Google Play: se for preciso, mencione no objeto que a publicação
  ocorrerá por contrato próprio, com acessos e responsabilidades definidos lá.
- **Prazo de sigilo curto destrói o instrumento.** Um ano em app que a ID vai manter não protege
  nada: 5 anos para o geral e indeterminado para código/credenciais.
- **Scripts de apoio e logs vão em `$HERMES_HOME`, não em `/tmp`** — `/tmp` não existe no ambiente
  Termux/proot e o `python` seguinte responde `can't open file`. Grave `$HERMES_HOME/tmp_<funcao>.py`,
  rode redirecionando a saída (`> $HERMES_HOME/build.log 2>&1`) e leia com `read_file`.

## Arquivos desta skill

- Skill de contrato geral da ID: `contratos-justos-id` (princípios, checklist, gate humano).
- Skill de formato: `md-to-timbrado-id` (motor md→gdoc, timbrado, pitfalls de Docs API).
- Skill empresarial: `direito-empresarial-brasileiro` (cláusulas prontas, mapa normativo).

## Disclaimer

> Minuta elaborada pela equipe da ID Consultoria com apoio de assistente de IA. Não substitui
> revisão jurídica profissional, especialmente em propriedade intelectual, LGPD e tributação.
