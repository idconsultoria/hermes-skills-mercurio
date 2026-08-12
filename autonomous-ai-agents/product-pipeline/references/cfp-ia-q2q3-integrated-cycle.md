# CFP IA — Ciclo Q2+Q3 Integrado (ago/2026)

Caso de referência do padrão "Workstreams paralelos" + "entregáveis para parceiro não-técnico".

## Decisões do usuário (Gustavo, 10/08/2026)

- **Q2 e Q3 executadas de forma coordenada e simultânea**, culminação em **24/08**. Roadmap original NÃO muda.
- **WS1-1 concluído**: usuário atualizou as Diretrizes v3 e adicionou "Base Técnica" na mesma pasta do Drive (`Diretrizes do App`).
- **WS1-3 (marca CFP + nome)** → responsabilidade do Igor (parceiro CFP). Preparar contexto, não executar.
- **WS1-5 (atualizar roadmap)** → PULAR. Roadmap se mantém.
- **WS2** deve desenhar tudo a partir das **trilhas do documento de diretrizes** (7 perfis/7 trilhas A–G), não das 9 do roadmap antigo.
- **WS3** = bloco único de trabalho do Igor (disponibilidade limitada): UM documento mestre simples, com entregáveis claros, relevância de cada entrega, o que é necessário para prosseguir, todo contexto no Drive formatado. Ele não lê .md/código.
- **WS4** adiantar tudo que não depende do WS3 (ex: motor de cálculo, schema, API, staging, validação de modelo, LGPD, esqueleto do núcleo agêntico+MCP).
- **Pipeline**: Pi cost (DeepSeek v4 Flash) substitui Pi best NESTE projeto.

## Base Técnica (arquitetura CFP IA — do Google Doc, 10/08)

- **IA conversacional = mecanismo principal de interação**; núcleo agêntico (versão leve/adaptada do agente Hermes) com **MCP** como interface para a **mesma API do frontend web**.
- Frontend web = hub de visualização/pequenos ajustes.
- **WhatsApp + Telegram desde o MVP**, gerenciamento e recuperação de sessões (canais ↔ web).
- Web: **Next.js + TypeScript + Tailwind**.
- Dados dos usuários: bancos + processados para LLM via 2 artefatos: (1) conversão para `.md`/`.csv`, (2) **LLM Wiki no padrão OKF (Open Knowledge Format)** indexando docs originais.
- **Knowledge engine**: RAG antiga intermediada por LLM, knowledge graphs, interage com a LLM Wiki OKF.
- Núcleo agêntico NÃO pode burlar o MCP nem tocar bancos diretamente; concilia com regras fixas da gamificação (opera "como um CFP usando o sistema gamificado").
- **LLM: DeepSeek v4 Flash, checkpoint 0731, provedora DeepSeek via chave OpenRouter** (créditos).

## Documentos produzidos no repo

- `product/management/base-tecnica.md` — espelho do Google Doc "Base técnica do CFP IA".
- `product/management/diretrizes-sistema-v3.md` — (a criar) espelho da Diretriz v3 do Igor.
- `AGENTS.md` (raiz) — hierarquia de documentos (reuniões > PRD > diretrizes > demais), regra de sync do Drive (só com sinalização explícita de fim de sprint), design system temporário como referência visual de TODOS os docs.
- `plano-acao-pos-reuniao.md` — plano em workstreams WS-1..WS-4 com checkpoints.
- `product/design-system-temporario.html` — cópia do design system minimal neutro (Notion/Stripe/Linear) para uso como referência de estilo.

## Padrão de trabalho do parceiro (Igor, CFP)

- Não lê `.md` nem código → tudo em Google Docs/Planilha/PDF (HTML do design system).
- Um documento mestre, curto, didático; entregáveis com relevância e dependências.
- Igor escreve roteiros/recomendações em **texto corrido**; Hermes gamifica depois.
- Igor valida personas/trilhas/tom; recruta testadores; é o CFP humano de referência.

## Pitfalls deste ciclo

- **Write denied fora de /opt/data**: salvar arquivos .md do projeto em `/opt/data/code/workstation/<projeto>/`, nunca em /tmp.
- **Google Docs → JSON**: `$GAPI docs get` retorna JSON com `body` — extrair body para arquivo separado antes de ler (read_file em linha única gigante trunca).
- **Drive search "Base Técnica"** achou o doc novo (id 1Jo0R9L6Z3w6t2MUOTxP8wCba3N2e3XJfd9Rv0up6WjU) — verificar `parents` para confirmar que está na mesma pasta das diretrizes (1TXeMUH71yz3f_KJHbHvXViiZxc5Ux-KG).
- Decisões de reunião ≠ PRD: PRD ainda dizia "diagnóstico em 7 dias / 9 trilhas / perfil de risco" enquanto a reunião decidiu diagnóstico imediato / 7 trilhas / 7 perfis determinísticos. A hierarquia do AGENTS.md resolve o conflito a favor da reunião até o PRD ser atualizado.
