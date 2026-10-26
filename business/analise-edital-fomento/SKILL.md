---
name: analise-edital-fomento
description: "Use ao analisar edital de fomento e montar checklist."

Carregue esta skill quando a ID avaliar edital de fomento e precisar do checklist de submissão: leitura do edital, exigências de elegibilidade, documentação obrigatória, prazos e aderência ao portfólio.
category: business
type: Orchestrator
timestamp: 2026-10-22T21:27:05-03:00
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [edital, fomento, chamada, fapesp, cnpq, finep, nfrf, subvencao, elegibilidade, documentos]
    scopes: [id]
---

# Analisar edital de fomento e preparar a submissão

Carregar quando chega uma chamada/edital (CNPq, FINEP, FAPESP, FAPITEC, cooperação internacional,
ICT) e o pedido é "analise este edital", "o que dá para preparar", "conseguimos submeter?".

A entrega é dupla: **(1) o veredito de elegibilidade** — quem pode submeter, quem pode receber,
onde a ID se encaixa — e **(2) o checklist de documentos por etapa**, com o que dá para produzir
antes do prazo. Sem o item 1, o checklist é trabalho perdido.

## Ordem de trabalho (não inverter)

1. **Ler o cronograma inteiro antes de tudo** e dizer em que etapa a chamada está hoje: aviso de
   interesse → carta de intenção → proposta completa → resultado → início. Comparar com a **data
   real de fonte externa** (cabeçalho HTTP `Date`, API do Telegram) — nunca com o relógio do
   container. **Prazo vencido é pergunta, nunca afirmação**: pode haver equipe já habilitada numa
   etapa anterior, e isso muda todo o diagnóstico.
2. **Gate de elegibilidade, antes de qualquer lista de documentos.** Quem pode **receber** recurso
   ≠ quem pode **participar** da equipe. Regra recorrente: a fundação paga a pesquisador com
   **vínculo em instituição de pesquisa do território dela** (doutor + instituição sede); empresa
   ou instituição de outro estado/país entra como **Pesquisador Associado, stakeholder ou parte
   contratada** — assento e legitimidade na equipe, **sem receber daquela agência**.
3. **Sair da página da chamada e ir às normas da modalidade.** A lista de documentos quase nunca
   está na chamada: ela vive na **norma da modalidade de apoio** (seção "Formato para apresentação
   de propostas"), com subseções separadas para *enquadramento* e *proposta completa*, mais uma de
   *documentos adicionais* — e cada fase tem lista própria.
4. **Anexo do financiador parceiro + FAQ.** O anexo nacional traz valores, itens financiáveis e
   contrapartidas; o FAQ decide elegibilidade (modelo de currículo, vinculação exigida, quem
   assina/submete em cada sistema).
5. **Checklist por etapa**, com três decisões por item: **quem produz** (ID, ICT, instituição sede,
   doutor coordenador), **quando** (fase) e **o que a ID adianta**.
6. **Entregar em duas camadas:** veredito curto + checklist escaneável na conversa; análise longa
   em anexo ou DM. Não despejar 30 itens no grupo.

## Pitfalls

- **Listar documentos sem dizer a fase.** Parte dos itens pertence à proposta completa e só é
  exigível de quem passou pela intenção; entregar tudo junto faz o time achar que está atrasado
  todo dia.
- **Tratar "fora do território" como impedimento.** Fora da unidade federativa/país, a ID não fica
  de fora — muda de papel (associada, stakeholder, parceira contratada). Dizer o papel, não a
  exclusão.
- **Procurar o checklist só na página da chamada.** Se a página traz "orientações resumidas", os
  requisitos completos estão na norma da modalidade e na norma do parceiro — e prevalece a versão
  original (em geral em inglês, em cooperação internacional).
- **Supor que documentos de fases diferentes se reaproveitam.** O projeto submetido às duas
  agências tem de ser **o mesmo projeto**; o orçamento pode diferir por agência (itens financiáveis
  diferentes) — variação de valor é legítima, divergência de escopo não.
- **Prometer "nós submetemos" sem o vínculo exigido.** Coordenação exige doutor com vínculo na
  instituição sede elegível, e há **conflito de interesse** quando o coordenador é da própria ICT
  parceira que receberia o contrato: registrar o conflito e pedir anuência do dirigente.
- **Redigir do zero o que a casa já tem.** O conjunto de declarações e anexos já usado em contrato
  com ICT (currículos, anuência de dirigente, declarações de vínculo/natureza exclusiva) é molde
  reutilizável — conferir a base antes.

## Extração das páginas (fonte institucional longa)

- Páginas de fundação e de agência internacional renderizam bem por **leitura do texto no
  navegador** (`document.querySelector('main') || document.body` → `innerText`), listando ao lado
  os **links da própria página** para achar normas, anexos e FAQ.
- **Salvar o texto extraído em arquivo** e recortar as seções por título numerado: as listas de
  documentos são longas, e reler o todo a cada passo custa mais do que reler o trecho.
- Toda afirmação de prazo, valor ou exigência sai **do documento lido**, com a fonte nomeada
  (chamada, norma da modalidade, anexo, FAQ). Não completar lacuna com o edital "parecido" de
  outra agência.

## Arquivos desta skill

- `references/checklist-edital-fomento.md` — checklist por etapa (equipe, projeto, orçamento,
  anexos institucionais) e notas de financiadores já lidos (FAPESP Regular/Temático, cooperação
  FAPESP↔NFRF, subvenção via ICT).
