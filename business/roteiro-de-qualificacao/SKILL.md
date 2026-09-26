---
name: roteiro-de-qualificacao
description: "Montar roteiro de perguntas de qualificação: descoberta ou sabatina.

Load this skill when preparing structured question sets for a client engagement, reading the real source document first."
type: Orchestrator
category: business
timestamp: 2026-09-24T00:00:00Z
author: Hermes curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [descoberta, discovery, sabatina, due-diligence, qualificacao, reuniao, proposta]
    related_skills: [analise-contratual, elaboracao-proposta-comercial, user-interview, grounded-citations]
---

# Roteiro de Qualificação (dois lados da mesa)

Conjunto de perguntas estruturadas para um engajamento — montado de **um dos dois lados**.

- **Modo Descoberta** — nós perguntamos ao cliente, para descobrir processo, dado, uso e bloqueio.
- **Modo Sabatina** — o cliente pergunta a nós; entregamos as perguntas que ele vai fazer, a resposta que segura a sala e a exposição que não se pode esconder.

Escolher o modo errado entrega um documento que não serve para a reunião. Antes de escrever qualquer pergunta, definir de qual lado da mesa o roteiro é.

## Procedimento

### 1. Ler a fonte real antes de perguntar

Roteiro genérico é o modo de falha mais comum: perguntas que qualquer pessoa responderia e que nada descobrem. Ler primeiro o que já existe — proposta, contrato, ata, minuta, o documento mais recente no Drive (`google-workspace`: `drive search` por nome do projeto → `docs get` na versão de maior `modifiedTime`).

Extrair do documento: números citados, módulos/entregáveis, exclusões já declaradas, marcos, responsáveis nomeados, dependências de terceiros.

### 2. Definir o contrato do roteiro com o usuário

Confirmar em uma frase: **quantas rodadas, quantas perguntas por rodada, e por qual lado**. Não assumir. "10 por eixo, 8 eixos" e "sequências que aprofundam conforme a resposta" são formatos diferentes — o segundo exige alguém respondendo ao vivo.

### 3. Eixos

Cada eixo é um **bloco independiente**, cabe em 30–45 minutos, e é respondível por uma pessoa diferente. Eixo bom é o que tem dono identificado e resposta que muda uma decisão.

Eixos que quase sempre rendem em projeto de tecnologia para órgão ou empresa:
Técnico e Estrutura · UI/UX e Uso · Acesso à Informação · Integração com Outras Organizações · Relatórios, Captação e Prova · Operação de Campo · Confiança, Limites e Responsabilidade · Evoluções para Futuro Próximo.

Agrupar por eixo, não por ordem de conversa. Quem conduz a rodada só precisa de uma folha.

### 4. Marcar o que o documento já responde (Modo Descoberta)

Toda pergunta que a proposta/ficha já responde por escrito recebe marcação explícita (`[fonte]` + versão). Aí a pergunta deixa de ser de descoberta e passa a ser de **validação** — e vale dizer isso ao usuário, porque muda o objetivo da reunião. Se a resposta na reunião contradizer o documento, a reunião ganha; o documento é corrigido depois.

### 5. No Modo Sabatina, cada pergunta traz dois campos

- **A resposta que segura a sala** — a formulação honesta e defensável, ancorada no que está no contrato.
- **A exposição que não se pode esconder** — a fragilidade real que aquela pergunta toca, dita ao usuário sem eufemismo.

Uma pergunta sem o segundo campo é teatro. Uma pergunta sem o primeiro é crueldade sem propósito.

### 6. Fechar com armadilhas e checklist de sala

O Modo Sabatina não termina na lista. Fechar com: as **armadilhas de sala** (respostas que custam o projeto, com a formulação alternativa correta) e um **checklist do que levar** (documentos, protótipo, números conferidos na fonte primária, lista do que não se sabe responder).

Ver `references/modos-e-armadilhas.md` para os modos em profundidade e o catálogo de armadilhas.

### 7. Conferir antes de entregar

```bash
python3 scripts/scan-integridade-texto.py ROTEIRO.md --esperado-por-secao 10 --sequencia 1-80
```

Confere contagem por rodada, sequência ininterrupta e contaminação de alfabeto. **Rodar sempre** — ver a regra de integridade abaixo.

## Regras sempre ativas

**O roteiro nasce do documento real, não da imaginação.** Se nenhuma fonte foi lida, o roteiro não sai: ler primeiro.

**Integridade de texto gerado — gate obrigatório.** Texto longo gerado em um único sopro pode vazar caractere de outro alfabeto (CJK, cirílico, hangul, fullwidth) e pontuação duplicada, sem erro de sintaxe. O sintoma é invisível na leitura normal e destrui a credibilidade de um documento que vai para a sala do cliente. **Nunca entregar texto gerado sem rodar o scanner** e corrigir até zerar. A falha é silenciosa por natureza: se você não varre, ela é entregue.

**Ao corrigir, reescrever a LINHA inteira, não a palavra.** Substituição pontual de um trecho corrompido costuma deixar resíduo do texto original ao lado. Detectar pelo scanner, substituir a linha completa, rodar o scanner de novo.

**Ao corrigir um item, reexecutar a verificação de estrutura.** Correção pontual pode quebrar a contagem por seção ou a numeração global; o gate final sempre vem depois das correções, nunca antes.

**Contagem declarada é contagem verificada.** Se o documento diz "8 rodadas × 10 perguntas", a checagem é aritmética sobre o arquivo — não confiança no que foi digitado.

## Pontos de armadilha

⚠️ **Pergunta que responde sozinha.** "Vocês conseguem integrar com a Defesa Civil?" pressupõe a resposta. A forma que descobre é "com quem já conversaram sobre isso e o que ficou pendente".

⚠️ **Pergunta de opinião futura.** "Isto resolveria o problema do gestor?" — ninguém sabe. O que revela é o comportamento passado: "da última vez que isso travou, como resolveram?"

⚠️ **Confundir o bloqueador com a pessoa.** Quando existe um gatekeeper individual ou resistência individual, o roteiro descreve a dependência institucional e a estratégia de acesso. Nomear a pessoa como obstáculo em um documento que vai circular destrói a relação que o projeto precisa.

⚠️ **Números de terceiros sem conferência na fonte primária.** Cifras que aparecem no documento e serão citadas em sala (recursos públicos, marcos, prazos) saem com link da fonte oficial e reconferidas antes da reunião. Um número errado derruba a credibilidade de todo o resto, inclusive das entregas técnicas.

⚠️ **Rascunho em etapas.** Entregar o arquivo pela metade e pedir aprovação etapa a etapa é o fluxo certo para proposta comercial; para um roteiro de perguntas, é atrito desnecessário — o documento é autocontido e de leitura rápida, e o usuário pediu as rodadas inteiras.

## References

- `references/modos-e-armadilhas.md` — os dois modos em profundidade, marcação de fonte, e catálogo de armadilhas de sala com a formulação alternativa.
- `scripts/scan-integridade-texto.py` — gate de integridade: contagem por seção, sequência, contaminação de alfabeto e pontuação duplicada. Sai com código ≠ 0 quando há violação.
