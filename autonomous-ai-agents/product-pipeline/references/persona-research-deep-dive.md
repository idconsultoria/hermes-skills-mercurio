# Persona Research Deep Dive — Referência Técnica

Técnicas avançadas para pesquisar pessoas reais online quando o buscador padrão retorna zero resultados.

## Motivação

O `web_search` pode retornar **0 resultados** mesmo quando a pessoa tem presença digital rica. Isso acontece por:
- Bloqueio CAPTCHA/rate-limit no backend de busca
- Pessoa usa nome profissional diferente do nome civil (ex: @nosterviz)
- Plataformas bloqueiam scrapers (Instagram, LinkedIn demandam login)
- Pessoa tem presença mais técnica (GitHub) do que social (Instagram/LinkedIn)

## Técnicas de Deep Recon

### 1. Navegação Direta por Plataforma

**Nunca confiar só em web_search.** Para cada pessoa, tentar URLs diretas:

```python
urls_to_try = [
    f"https://github.com/search?q=%22{nome}%22&type=users",
    f"https://www.linkedin.com/in/{username_guess}/",
    f"https://www.instagram.com/{username_guess}/",
    f"https://www.behance.net/search?search={nome_encoded}",
    f"https://dribbble.com/search/{username_guess}",
]
```

Usar `browser_navigate` para cada URL. Algumas plataformas (LinkedIn, Instagram) mostram authwall mas confirmam que o perfil existe.

### 2. GitHub API para Perfil e Commits

```bash
# Perfil do usuário
curl -sL "https://api.github.com/users/<username>"
# → name, company, blog, location, bio, created_at, public_repos

# Commits de um repositório
curl -sL "https://api.github.com/repos/<user>/<repo>/commits"
# → author name, message, date — revela vocabulário e estilo de trabalho
```

O campo `commit.author.name` pode ser o nome da empresa (ex: "ID Consultoria") em vez do username da pessoa — sinal de que ela commita profissionalmente.

### 3. Análise de CSS em Produção

Se a pessoa tem deploy em Vercel/Netlify, extrair o CSS para entender o sistema de design:

```bash
# 1. Achar o link do CSS no HTML
curl -sL "https://<projeto>.vercel.app/" | grep -oP 'href="[^"]*\.css"'

# 2. Analisar o CSS
curl -sL "https://<projeto>.vercel.app/assets/<hash>.css" | grep -E '(--tw-|[#][0-9a-fA-F]{6}|font-family|background-color|linear-gradient|glass|blur)'
```

O que extrair:
- **Paleta:** cores de fundo (`bg-\[#...\]`), cores de texto, cores de borda
- **Tipografia:** `font-family` nas fontes carregadas (Google Fonts `preconnect`)
- **Efeitos:** `backdrop-blur`, `glass`, `shadow`, `gradient`
- **Animações:** `@keyframes`, `transition`, `hover:`
- **Layout:** `grid-cols`, `max-width`, gaps, padding patterns

### 4. Commit Messages como Fonte de Persona

Commits revelam:
- **Vocabulário de design:** "cinematic composition", "balance", "premium multi-tone Gold Gradients"
- **Preocupações de estilo:** "Final brand alignment with Abyss Teal and Gold accents"
- **Stack:** TypeScript, React, Vite, Tailwind, Google Apps Script
- **Workflow:** Deploy em Vercel, commit frequente, mensagens descritivas

```bash
curl -sL "https://api.github.com/repos/<user>/<repo>/commits" | python3 -c "
import json, sys
for c in json.load(sys.stdin):
    msg = c['commit']['message'].split(chr(10))[0]
    print(f\"{c['commit']['author']['name']:20} | {c['sha'][:7]} | {msg}\")
"
```

### 5. Browser Vision para Páginas com DOM Truncado

Algumas plataformas (Behance, Bing) renderizam visualmente mas o DOM snapshot vem truncado por Cloudflare/JS. Usar:

```python
browser_vision(question="Mostre todos os títulos e URLs dos resultados visíveis", annotate=True)
```

### 6a. Escavador (Brasil — Dados Públicos de Pessoa Física)

**URL:** `escavador.com`

Plataforma brasileira que agrega dados públicos de **pessoas físicas**: formação acadêmica, filiação institucional, processos, publicações. Útil para encontrar:

- Nome completo e variações
- Vínculo empregatício (ex: "Designer Gráfico na ALESE")
- Formação acadêmica registrada
- Publicações e artigos

> ⚠️ Escavador indexa por ID numérico + slug. Pode exigir navegação via browser.

### 6b. Alura (Brasil — Perfil de Cursos)

**URL:** `cursos.alura.com.br/user/<username>`

Plataforma brasileira de cursos de tecnologia. O perfil público mostra:

- Cursos concluídos (quantidade e lista)
- Formações (trilhas completas: Product Design, Design System, Figma, etc.)
- Tempo de plataforma e engajamento

Útil para validar o perfil técnico de designers e devs brasileiros.

### 6c. AboutCompany / CNPJ (Brasil — Dados de Empresas)

**URL:** `aboutcompany.com.br`

Agrega dados públicos da Receita Federal (CNPJ). Útil para:

- Confirmar que uma pessoa é sócia de uma empresa
- Data de entrada como sócio
- Outros sócios registrados (para expandir pesquisa)
- Endereço e ramo de atividade

### 6d. Google Sites Portfólios

Portfólios antigos hospedados no Google Sites (`sites.google.com`) podem conter:

- História profissional desde o início da carreira
- Clientes atendidos
- Projetos antigos que não estão mais em portfólios modernos

### 6e. Facebook Business Pages

Páginas profissionais no Facebook de agências/estúdios do passado podem revelar:

- Nome de estúdios que a pessoa fundou ou trabalhou
- Portfólio de serviços oferecidos
- Localização e anos de atuação

> ⚠️ Facebook frequentemente requer login.

### 7. Montagem do Clone Digital

Depois de coletar dados de múltiplas fontes (GitHub, LinkedIn, Instagram, Behance, Escavador, Alura, CSS analysis, commits), **consolidar num único documento de persona** que sirva como referência viva.

#### Estrutura do documento de clone digital

```markdown
# 🧬 Clone Digital: [Nome]

> Persona de IA incorporando a voz, o repertório e a visão de [Nome]

## 📋 Identidade
| Campo | Valor |
| Nome completo | ... |
| Naturalidade | ... |
| Idade | ... |
| Formação | ... |
| Empresas | ... |
| Premiações | ... |

## 🧠 Estrutura de Pensamento
Núcleo filosófico, perguntas favoritas, dialeto de raciocínio

## 🎯 Especialidades
Product Design, Branding, Consultoria, etc.

## 🗣 Voz e Estilo de Comunicação
Regionalidade, registro, humor, padrões de fala

## 🛠 Modos de Ativação
Modo Crítico, Mentor, Criador, Estrategista

## ⚠️ Pitfalls / Anti-persona
O que a pessoa NÃO é / o que NÃO fazer

## 📚 Referências que alimentam o repertório

## 🔗 Links Vivos
Todas as URLs encontradas

## 📝 Histórico da Pesquisa
| Data | Fonte | Achado |
```

#### Uso do Clone Digital

1. **Alimenta** os documentos de produto (PRD, user stories, roadmap) com dados reais da pessoa
2. **Referência para o Pi Agent** — Pi pode consultar o clone para tomar decisões de produto alinhadas com o perfil real
3. **Ativação sob demanda** — Em prompts de produto, ativar o modo relevante

> 📂 **Arquivamento:** Salvar o clone digital em `/opt/data/<nome>-digital-clone.md` para reúso.

#### 8. Output Format — Persona Limpa (sem fontes inline)

Após consolidar o clone digital, o documento de persona final DEVE seguir o formato definido em `references/persona-output-format.md`:

- Bio & Demographics → Quotes → Pains → What/Goals → Attitudes
- **Sem fontes inline** no corpo
- **Sem tabelas resumo**
- **Máximo 8 itens no mapa de cobertura**
- Clone digital é **rascunho** — correção do usuário vence

### 9. ⚠️ Pitfall — Clone Digital Não É Verdade Absoluta

O LLM que gera o clone digital **vai inventar características**. É esperado — o modelo preenche lacunas com inferência. Os erros mais comuns:

- **Filosofia pessoal:** Atribuir crenças ou princípios que a pessoa não endossa
- **Citações inventadas:** Criar frases que "soam como" a pessoa diria
- **Motivações profundas:** Inferir por que a pessoa faz o que faz

**Como mitigar:**

1. Separar no clone digital o que é **dado verificável** do que é **inferência**
2. Apresentar a persona ao usuário com abertura para correção
3. Se o usuário corrigir qualquer traço, **a correção vence imediatamente** em todo o documento
4. Não argumentar contra a correção — o usuário conhece a pessoa real

**Exemplo real:** O clone digital do Tácio Brito atribuiu a ele "o método é a jaula" como filosofia de design. O usuário: "Isso não é algo que Tácio se importa não. Foi só algo que o clone digital dele disse." — a crença foi removida de 5 pontos no documento final.

### 10. Esgotar Antes de Reportar

1. web_search com 3 variações de nome (com acento, sem acento, nome do meio)
2. Browser direto para 5+ plataformas (GitHub, LinkedIn, Instagram, Behance, Dribbble)
3. GitHub API search por nome completo
4. Escavador + AboutCompany (fontes brasileiras de dados públicos)
5. Análise de projetos conhecidos da empresa da pessoa
6. **Pedir link direto ao usuário** — ele pode saber onde a pessoa está

> **Regra:** Não reportar "não encontrado" até ter tentado passos 1-5. O usuário disse "procure melhor" quando a primeira tentativa falhou — ele espera persistência.

## Exemplo Real: Tácio Brito

| Técnica | Resultado |
|---------|-----------|
| web_search (nome completo) | 0 resultados |
| GitHub search | ✅ Usuário `nosterviz`, 1 repo `painel-inscricoes-id` |
| LinkedIn /in/tacio-brito/ | ✅ Perfil existe (authwall) |
| Instagram @taciobrito | ✅ Perfil existe (login wall) |
| GitHub API commits | 14 commits, autor "ID Consultoria", vocab designer |
| CSS do Vercel deploy | Navy #050A0F, Gold #D4AF37, Bricolage+Nunito, glassmorphism |
| Escavador | ✅ Nome completo e vínculo ALESE |
| Alura | ✅ 35 cursos, formações Product Design + Design System |
| AboutCompany | ✅ Sócio ID.TEAL desde 04/2024 |
| Google Sites | ✅ Portfolio "Brito Designer" — design desde os 10 anos |
| Facebook (TB Estudio) | ✅ Estúdio de design em Itabaiana/SE |
| **Clone Digital** | ✅ Consolidado em `/opt/data/tacio-brito-digital-clone.md` |

O clone digital gerou dados que elevaram o nível da persona de **CRÍTICO (sem dados)** para **ALTO (completo)** — e serviu como referência para o Pi gerar documentos de produto alinhados com o perfil real.

## Erro Comum: Confiar no web_search como primeira e única fonte

**Sintoma:** Você pesquisa o nome da pessoa, recebe 0 resultados, e declara que a pessoa "não tem presença pública."

**Correção:** web_search é a fonte MAIS FALHA para encontrar pessoas reais. Motivos:
- CAPTCHA/rate-limit no backend (Google, Bing)
- A pessoa usa handle diferente do nome civil
- A presença dela é concentrada em plataformas que o buscador não indexa bem (Behance, GitHub, Alura)
- O backend de busca pode estar bloqueado para o datacenter Oracle

**Sempre começar com navegação direta por plataforma** em vez de web_search genérico. web_search é o último recurso, não o primeiro.
