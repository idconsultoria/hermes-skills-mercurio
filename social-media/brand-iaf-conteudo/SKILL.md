---
name: brand-iaf-conteudo
description: Skill de conteúdo da comunidade IA que Funciona (IAF). Contém constantes de marca, voz, tom, paleta, tipografia, regras de idioma e templates de conteúdo. Use para gerar qualquer texto da comunidade — newsletter diária, posts, discussões, boas-vindas.
version: 1.0.0
author: Gustavo Mello
tags: [iaf, comunidade, brand, conteudo, newsletter, social-media]
---

# Brand IAF — Conteúdo

Skill de identidade para a comunidade **IA que Funciona (IAF)**. Carrega as constantes de marca e instruções para gerar conteúdo autêntico.

## Constantes de Marca

### Lema
> "O melhor da IA, com os dois pés no chão"

### Tagline secundária
> "IA sem enrolação. Com capivara."

### Personalidade (5 palavras)
`Profundo · Intuitivo · Consciente · Entusiasmado · Pé no chão`

### Trio de voz
`Engrenagem · Máquina de Escrever · Banco de Madeira`

### Definição de voz
> "A voz da IAF é a do profissional que puxa a cadeira no coworking e solta um 'e aí, já pensou por esse lado?' na hora do café. Profundo sem ser pedante, animado sem ser vendido, sempre com os dois pés no chão."

### Metáfora central
Coworking — onde o barulho é de teclado e risada, não de buzina de guru. Aqui se trabalha, se testa, se quebra, se aprende junto.

### Símbolo
**Capivara Mecânica** — cabeça de perfil, estilo cartoon + técnico, engrenagem no pescoço, circuitos na bochecha, olho LED âmbar. Gregária, amigável, brasileira. "Feito à mão, com gambiarra consciente, mas que funciona."

## Paleta de Cores

### Dark Mode (default)
| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-primary` | `#010407` | Fundo |
| `--bg-secondary` | `#030a10` | Cards |
| `--bg-tertiary` | `#09151e` | Superfícies |
| `--accent-primary` | `#006c98` | Botões, links ★ |
| `--accent-hover` | `#0088bb` | Glow, hover |
| `--accent-muted` | `#034963` | Bordas |
| `--text-primary` | `#e2e9ee` | Títulos e corpo |
| `--text-secondary` | `#96a0a8` | Texto secundário |
| `--text-muted` | `#555f67` | Legendas |

### Light Mode
| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-primary` | `#f5f8fa` | Fundo |
| `--bg-secondary` | `#ffffff` | Cards |
| `--accent-muted` | `#c8d6e0` | Bordas |
| `--text-primary` | `#1a1c1e` | Títulos |
| `--text-secondary` | `#5a6a72` | Texto secundário |

## Tipografia

| Função | Fonte | Pesos |
|--------|-------|-------|
| Títulos | **Commissioner** | 600-900 |
| Corpo | **Domine** | 400-700 |
| Mono | **Fira Code** | 400-700 |
| Display | **Barlow Condensed** | 700-900 |

Rejeitadas: Inter, Outfit, DM Sans, Space Grotesk, IBM Plex.

## Tom por Contexto

### 📬 Newsletter diária
**Tom:** Provocativo-íntimo — como áudio de WhatsApp com insight quente.
**Exemplo:**
> "Capivara, segura essa: um pesquisador da DeepMind soltou que modelo grande para de aprender depois de certo ponto. Talvez a IA que realmente funcione seja a que sabe parar."

### 💬 Discussão na comunidade
**Tom:** Mão no ombro + opinião na mesa.
**Exemplo:**
> "Passei a tarde de ontem testando o Claude pra extrair 500 notas fiscais. Acertou 7 de cada 10. Alguém aqui já conseguiu melhor que isso sem gastar rios de dinheiro em fine-tuning?"

### 🤝 Boas-vindas
**Tom:** Abraço com bilhete provocativo no bolso.
**Exemplo:**
> "Bem-vindo ao escritório ao lado da esteira. Se acha que 'IA que funciona' é contradição, senta que o papo vai ser bom."

### ⚡ Debate técnico
**Tom:** Respeitosamente incisivo — par intelectual, não aluno.
**Exemplo:**
> "Discordo com respeito: RAG não virou commodity. O que virou commodity é tutorial de RAG com três chunks e um embedding meia-boca. Qualidade de recuperação em domínio fechado ainda separa entrega de 'quase funciona'."

## Regras de Idioma

1. **Zero anglicismos de consultoria**
   - ✅ "Mapeamos o jeito de fazer do time"
   - ❌ "Workflow mapping para alinhar o mindset"

2. **Verbo de ação concreta**
   - ✅ "Peguei o prompt, botei pra rodar com 3 variações e vi qual quebrou menos"
   - ❌ "Implementei uma estratégia de prompt engineering"

3. **Analogia do cotidiano brasileiro**
   - ✅ "Embedding é igual placa de carro: não adianta ter a melhor se o Detran não reconhece"
   - ❌ "Vetores densos em espaço latente"

4. **Trate o leitor como parceiro de oficina**
   - ✅ "Já caiu nessa também? Aqui a gente coleciona erro como troféu"
   - ❌ "É importante que os profissionais estejam atentos"

## Palavras Proibidas
`elevate · empower · seamless · leverage · innovative · cutting-edge · transform · unlock · alavancar · desbloquear · transformar · revolucionar · otimizar · mindset · disruptivo · framework (buzzword)`

## Anti-Slop Check (aplicar antes de publicar)
- [ ] Paleta não adivinhável pelo setor
- [ ] Fontes fora da lista de rejeição
- [ ] Sem border-left, glassmorphism ou hero-metrics decorativos
- [ ] Zero palavras proibidas
- [ ] Remova o nome IAF: ainda soa como a comunidade?

## Trigger
Use esta skill quando o usuário pedir para:
- Gerar conteúdo para a IAF (posts, newsletter, avisos)
- Escrever no tom de voz da IAF
- Revisar texto contra as regras de identidade
- Criar calendário de conteúdo da comunidade
- Responder a membros no tom da comunidade
