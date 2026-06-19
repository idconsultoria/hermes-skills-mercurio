# Iteração de Propostas Comerciais

> Padrões para editar, simplificar e iterar propostas em projetos React/Tailwind existentes.

## Estrutura de Orçamento

Usar **3 eixos** — nunca detalhar itens individuais:

| Eixo | Cobre | Exemplo de distribuição |
|------|-------|------------------------|
| Operação | Infra, tokens IA, crawler, banco — o que mantém rodando | ~50% |
| Manutenção | Suporte, segurança, monitoramento, correção de bugs | ~20% |
| Desenvolvimento | Gestão, melhorias, novas features | ~30% |

**Regra:** Total dos 3 eixos = valor mensal cobrado do cliente. Sem gap, sem "desconto early adopter."

## Participação de Resultado

- **Terminologia:** SEMPRE usar "Participação de Resultado", NUNCA "Take Rate" (o usuário rejeitou este termo)
- Percentual fixo (ex: 2%) sobre o valor efetivamente recebido pela empresa
- Zero custo fixo adicional — risco compartilhado
- **O que NÃO incluir:** Qualquer menção a take rate do Parque/SergipeTec. O Parque tem contrato próprio com as empresas incubadas — isso NÃO é gerido pela ID/ArtemisHub e NÃO faz parte da proposta

## Copy

- **Enxuta:** O usuário prefere propostas curtas, diretas, sem filler. Cortar adjetivos, advérbios, e frases longas
- **Co-criação:** Enfatizar que a plataforma é "criada em parceria com o Parque", não um produto de prateleira
- **Tags de valor:** Máximo 5, frases curtas (≤5 palavras)
- **Subtítulos:** 1-2 linhas, sem "A Primeira Run do X é um compromisso de..." — ir direto ao ponto
- **Nota de custo:** "Cobre exatamente os custos. A rentabilidade vem da Participação de Resultado — só ganhamos quando a empresa capta."
- **Aposta:** Incluir mensagem explícita de que a ID está apostando no Parque: "Não é uma venda de software. É uma aposta de longo prazo na prosperidade do ecossistema sergipano."

## Logos e Assets

- Usar arquivos **já existentes** no `src/assets/` do projeto — nunca buscar logos em discos externos (TACIOBRITO, etc.) a menos que explicitamente solicitado
- Se o usuário disser que logos estão "incorretas", verificar primeiro se há outro arquivo no `src/` do projeto
- O arquivo original do Figma Make (hash-nomeado) geralmente é o logo correto

## Build no NTFS

```bash
# Sempre bypassar o .bin symlink
node ./node_modules/vite/bin/vite.js build

# Se esbuild quebrar (version mismatch após deploy remoto):
node -e "console.log(require('esbuild/package.json').version)"  # anotar versão
cd /tmp && npm install esbuild@<VERSAO_EXATA> --no-save
chmod +x /tmp/node_modules/@esbuild/linux-x64/bin/esbuild
ESBUILD_BINARY_PATH=/tmp/node_modules/@esbuild/linux-x64/bin/esbuild \
  node /mnt/ARQUIVOS/Projetos/<projeto>/node_modules/vite/bin/vite.js build
```

## Deploy Vercel

```bash
npx vercel --prod --yes --name <nome-minusculo>
# Ex: --name artemishub-sergipetec
```

O nome do projeto deve ser lowercase. Se o diretório tiver maiúsculas, usar `--name` explícito.

## Revisão de Copy em Propostas Multi-Seção

Quando atualizar uma proposta com múltiplas seções interligadas (cronograma, KPIs, pricing, participação), SEMPRE fazer uma busca reversa por referências aos termos antigos após todas as edições:

```bash
search_files(pattern="Take Rate|3 meses|R\\$ 1\\.924|Parque contratual")
```

Uma única referência não atualizada gera contradição e mina a credibilidade da proposta.

## Simplificação Agressiva de Páginas

Quando o usuário diz "muita informação", "enxuta", "página muito grande":

**Seções que podem ser cortadas:**
- **Pipeline (estágios técnicos)** — detalhe de implementação, não vende
- **Entregáveis** — redundante com o cronograma
- **Equipe** — mover para footer ou cortar totalmente
- **Vantagem Competitiva** — fundir com Valor Entregue
- **Solução (4 promessas)** — condensar em 1-2 linhas no Problema

**Alvo pós-corte:** 7 seções ou menos (Hero, Problema, Cronograma, KPIs, Valor, Resultado, Proposta).

**Ganho real:** Bundle JS cai ~14KB (seções React + ícones não usados). Nav dots mais limpos. Scroll mais curto.

## Separação Visual: Mensalidade vs Participação

O usuário quer ver CLARAMENTE que são coisas diferentes. Padrão:

**Bloco 1 — Valor Mensal:** GlassCard com preço grande, 3 mini-cards de composição (ícone + valor + nome do eixo), barra de total

**Bloco 2 — Participação de Resultado:** GlassCard separado, menor, com ícone TrendingUp, label "Além da mensalidade", e texto "Independente da mensalidade — é a forma como [empresa] rentabiliza sem onerar o [cliente] no custo fixo."

Nunca colocar Participação como uma 4ª pílula dentro do bloco de Mensalidade.

## Servidor Local: Cache

Python `http.server` não envia headers de cache — o navegador pode servir versão antiga mesmo após rebuild. Solução:

```bash
# Servidor com Cache-Control: no-store
python3 -c "
import http.server, socketserver
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-store,no-cache,must-revalidate,max-age=0')
        self.send_header('Pragma','no-cache')
        self.send_header('Expires','0')
        super().end_headers()
socketserver.TCPServer(('',8765),H).serve_forever()
" &
```

Se o usuário relatar que vê versão antiga mesmo em aba anônima, reiniciar o servidor com este script. Ou alternativamente fazer deploy no Vercel para garantir build limpo.

## Soberania: Dados vs Modelos

Correção do usuário (Sergipetec, 2026-06-16): o Parque é dono dos **dados** e tem plataforma sob medida. Mas os **modelos de IA e a tecnologia** são da ArtemisHub — NÃO são do Parque. Escrever sempre:

> "Plataforma desenhada sob medida para o Parque. O SergipeTec é dono dos dados — os modelos e a tecnologia são ArtemisHub."

Nunca escrever "dono dos dados e dos modelos" — a segunda metade é falsa.

## Vercel: Redeploy OBRIGATÓRIO após cada build

**Regra:** Toda vez que houver um build local com mudanças aprovadas, fazer deploy no Vercel IMEDIATAMENTE. O usuário explicitamente exige: "resete o cache do vercel de novo. faça isso sempre que der um novo deploy."

```bash
cd /mnt/ARQUIVOS/Projetos/<projeto> && npx vercel --prod --yes
```

Se o usuário relatar que vê versão antiga no link do Vercel mesmo após deploy:

1. Verificar com `curl -s https://projeto.vercel.app | grep "index-.*\\.js"` — o hash do JS deve ser diferente do anterior
2. Se o hash for igual, refazer `npx vercel --prod --yes` (o cache do Vercel pode ter servido build anterior)
3. O link direto com hash (`projeto-xxxxx.vercel.app`) sempre aponta para o deploy específico — usar para verificação

## GitHub MCP Server — Setup e Armadilhas

### Instalação

```bash
hermes mcp add github --command npx --args -y @modelcontextprotocol/server-github
```

O `--args` DEVE ser o último argumento.

### Autenticação

```yaml
mcp_servers:
  github:
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "seu_token"
```

### ⚠️ Armadilha: `hermes config set` quebra o YAML

`hermes config set mcp_servers.github.env '{"KEY":"val"}'` salva como STRING YAML, não como mapping. O MCP server quebra com erro "dictionary update sequence element #0 has length 1; 2 is required".

Fix: editar `~/.hermes/config.yaml` diretamente e formatar como YAML mapping:

```yaml
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: 'token_aqui'
```

### Verificação

```bash
hermes mcp test github     # ✓ Connected + 26 tools
hermes mcp list            # ✓ enabled
```
