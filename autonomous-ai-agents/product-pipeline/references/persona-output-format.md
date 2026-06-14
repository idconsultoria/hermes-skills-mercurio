# Persona Output Format — Template & Regras

> Formato aprovado pelo usuário ID Consultoria para documentos `user-personas.md`.
> Baseado no proto-persona template do Pi Agent e na correção de formato solicitada.

## Template

```markdown
### Nome Real — "Persona Name"

> *Quote principal — frase real que define a persona*

### Bio & Demographics
- **Idade:** N anos
- **Naturalidade:** Cidade, Estado
- **Residência:** Cidade, Estado
- **Formação:** Curso (Universidade), Especializações
- **Premiação:** 🏆 Prêmio (se houver)
- **Cargo:** Cargo | Empresa
- **Empresas:** Lista de empresas e vínculos
- **Perfil online:** GitHub, LinkedIn, Instagram, Behance — só os que existem
- **Stack técnica:** Tecnologias que domina
- **Sistema visual pessoal:** Paleta, tipografia, estilo (se designer)

### Perfil neurodivergente
1 linha descrevendo o perfil (TDAH, superdotação, dupla excepcionalidade) e o que isso significa no contexto do produto.

### Quotes
- *"[Frase real 1]"*
- *"[Frase real 2]"*
- *"[Frase real 3]"*

### Pains
- **Dor nomeada:** Descrição em 1-2 linhas. Máximo 3-4 dores.

### What is This Person Trying to Accomplish?
- 2-3 bullets concisos. O que ela quer poder fazer.

### Goals
- **Alpha/X.X:** Meta específica para cada fase do produto

### Attitudes & Influences
- **Autoridade de decisão:** Quanto poder ela tem sobre o produto
- **Influenciadores:** Quem/que referências moldam suas decisões
- **Crenças:** 1-2 crenças centrais que impactam o produto
```

## Regras Obrigatórias

1. **Sem fontes inline** — nenhum `[FONTE: ...]` no corpo do documento
2. **Sem tabelas resumo** de atributos no final da persona
3. **Mapa de cobertura** — no máximo 8 linhas, fora das personas individuais
4. **Histórico** — tabela simples (Data | Autor | Mudança) ao final
5. **Clone digital é rascunho** — dados do clone alimentam, mas correção do usuário vence

## ⚠️ Exemplo Real: O Caso "O Método é a Jaula"

Na prática com a ID Consultoria, o clone digital do Tácio Brito atribuiu a ele a crença **"o método é a jaula"** (schema fixo como princípio fundador do Delfos). O usuário corrigiu:

> *"Essa parte do SCHEMA fixo não é algo que Tácio se importa não. Foi só algo que o clone digital dele disse. Remova essa parte."*

**Lição:** O clone digital pode inferir filosofias, crenças ou citações que a pessoa real não endossa. O LLM vê um padrão (ex: "é designer neurodivergente") e constrói uma narrativa consistente mas falsa.

**Regra de ouro:** Clone digital gera **hipóteses**. Usuário confirma ou descarta. A correção do usuário é o documento final — o clone digital é só rascunho. Se o usuário disser "isso não é algo que [pessoa] se importa", remover imediatamente de TODAS as seções afetadas (quote principal, quotes, attitudes, mapa de cobertura, perfil).
6. **Idades** — verificar com usuário se houver dúvida. Não inferir de faixa etária

## Referência do Pi Agent

O template original do Pi Agent está em:
```
~/.pi/agent/skills/pm-skills/skills/proto-persona/template.md
```

E o exemplo de boa persona:
```
~/.pi/agent/skills/pm-skills/skills/proto-persona/examples/sample.md
```
