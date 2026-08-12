# ATS — Truths vs Myths (adaptado de The Tech Resume Inside Out, Amy Miller ex-Amazon/Google, r/EngineeringResumes, Harvard, MIT CAPD)

## O que ATS realmente é

ATS = **banco de dados + workflow para recrutadores**. NÃO é um robô que rejeita currículo. Funções reais:
- Armazena candidatura e extrai dados estruturados (nome, e-mail, histórico, skills)
- Permite busca/filtro por keywords
- Alguns sistemas ranqueiam relevância contra o JD — **ranqueamento é auxílio, não portão**

**Mitos (não repetir como fato):**
- ❌ "75% dos currículos são rejeitados por ATS" — estatística inventada por vendedores de "ATS-beating"; a rejeição massiva é triagem HUMANA (5-20s por currículo)
- ❌ "Precisa de score ATS mínimo para passar" — na maioria dos sistemas não há auto-rejeição por score
- ❌ "PDF quebra ATS" — Greenhouse, Workday, iCIMS, Lever parseiam PDF corretamente. .docx e .pdf são seguros
- ❌ "Keyword stuffing com texto branco" — fraude detectável e vista como desonestidade
- ⚠️ "Tabelas/colunas são lidas" — ATS legado embaralha conteúdo em layout multi-coluna; single column é o mais seguro

**Conclusão prática: otimize para HUMANO que escaneia em 5-20 segundos.** ATS parsea; humanos decidem.

## Estratégia de keywords (matching language, não stuffing)

1. Leia o JD e liste as tecnologias/metodologias/ferramentas citadas
2. Garanta que apareçam naturalmente no currículo **se você realmente tem a experiência**
3. Use a MESMA terminologia do JD (pedem "CI/CD" → use "CI/CD"; idealmente "CI/CD (continuous integration/continuous delivery)")
4. Soft skills enfatizadas no JD (leadership, collaboration) devem aparecer em bullets, não como lista solta
5. Termos de domínio: B2B, SaaS, fintech, healthtech, ARR, churn, LGPD/GDPR

## Categorias de keywords (tech)

- **Linguagens:** JavaScript/TypeScript, Python, SQL, Java, Go, C#, PHP...
- **Frameworks:** React, Angular, Vue, NestJS, Django, FastAPI, Spring Boot, Laravel...
- **Bancos:** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB...
- **Cloud/Infra:** AWS (S3, Lambda, EC2, RDS), GCP, Azure, Docker, K8s, Terraform, CI/CD
- **Arquitetura (alto valor p/ sênior):** Microservices, Hexagonal, DDD, CQRS, Event-Driven, SOLID, TDD, REST, GraphQL, gRPC
- **Integração:** Kafka, RabbitMQ, SQS, Stripe, Salesforce, WhatsApp Business API, OpenAI API
- **Ferramentas:** Git/GitHub, Jira, Figma, Postman

## Sinais de senioridade (o que a vaga espera de sênior/lead)

- Mentoria de outros devs, code review, definição de padrões
- Decisão de arquitetura, seleção de tecnologia
- Trabalho cross-team, stakeholder management
- Responsabilidade por disponibilidade/custo/segurança de sistemas
- O currículo deve PROVAR esses sinais com bullets específicos, não com o título

## Red flags em vagas (avisar o usuário)

- "We're like a family" / carga elogiada demais → burnout (sinal cultural)
- Salário fora da faixa de mercado → flight risk ou vaga fantasma
- Requisitos contraditórios (ex.: 5+ anos em tecnologia que existe há 2)
- "Urgente" + "múltiplas vagas" → alta rotatividade
- JD genérico demais → possível vaga fantasma/recrutador sem brief

## 5-Second Scan Test

Em 5 segundos o recrutador precisa achar: cargo atual, stack principal, anos de experiência, indício de fit. Se não acha, o currículo falha — por isso skills no topo (tech) e bullets de maior relevância primeiro.
