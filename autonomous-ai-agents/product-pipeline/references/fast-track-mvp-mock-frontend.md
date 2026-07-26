# Fast-Track MVP: Frontend com Mock Data → Vercel

> Variante leve do pipeline. Use quando o PRD já existe e o objetivo é
> um demo funcional com dados mockados, sem backend.

## Quando usar este padrão

- PRD já escrito (usuário trouxe o documento)
- Ideação concluída (não precisa de F1)
- Objetivo é **demo visual**, não app completo
- Zero backend — tudo mockado no frontend
- Deploy rápido (Vercel, Netlify, GitHub Pages)

**NÃO use quando:** precisa de backend real, autenticação, persistência,
ou o design system ainda não foi definido.

## Fluxo (4 passos)

### 1. Clone + leitura do PRD

```bash
git clone <repo> && cd <repo>
cat docs/PRD*.md          # ou onde estiver
```

Ler também docs de UI de referência se existirem (wireframes, specs de tela).

### 2. Pesquisa breve de concorrentes (2-3 queries)

Pesquisa direta com `web_search`, sem delegate_task. Objetivo: mapear
2-3 concorrentes diretos e posicionar o produto. Suficiente para contexto.

```python
web_search(query="<produto> concorrentes Brasil SaaS 2024 2025", limit=5)
web_search(query="<mercado> software gestão <nicho>", limit=5)
```

### 3. Construir SPA single-file

Um arquivo HTML autossuficiente com:

**Estrutura:**
- CSS custom properties no `:root` (design system)
- Navegação SPA via JavaScript vanilla (sem framework)
- Views renderizadas como innerHTML
- Modais como overlay + innerHTML dinâmico
- Gráficos via Chart.js CDN (`chart.js@4.4.0`)

**Mock data:** arrays/objetos JavaScript no topo do script. Suficiente para
povoar todas as views. Dados realistas, não aleatórios.

**Responsividade:** `@media (max-width: 768px)` com sidebar colapsável,
grid adaptável, formulários single-column.

**Padrão de navegação:**
```js
function navigate(view) {
  document.querySelectorAll('.nav-item').forEach(el =>
    el.classList.toggle('active', el.dataset.view === view));
  render(view);
}

function render(view) {
  destroyCharts();
  switch(view) {
    case 'dashboard': renderDashboard(c); break;
    // ... uma função por view
  }
}
```

**Padrão de modal:**
```js
function openModal(html) {
  document.getElementById('modalBox').innerHTML = html;
  document.getElementById('modalOverlay').classList.add('show');
}
function closeModal() { ... }
```

**Tamanho típico:** 40-60KB para 8-12 views com 3-5 modais cada.

### 4. Deploy no Vercel

Arquivos necessários na raiz do projeto:

**`vercel.json`:**
```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": "public",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**`.vercelignore`:**
```
.git
docs
*.md
.gitignore
```

**Comandos de deploy (prebuilt — mais confiável):**
```bash
export PATH="/opt/data/.npm-global/bin:$PATH"
cd /opt/data/<projeto>
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

**Pós-deploy — desabilitar SSO protection:**
```bash
TOKEN="$(python3 -c "import json; print(json.load(open('/opt/data/home/.local/share/com.vercel.cli/auth.json'))['token'])")"
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"ssoProtection": null}'
```

**Habilitar analytics:**
```bash
vercel project web-analytics <project-name>
```

**Verificar:**
```bash
curl -s -o /dev/null -w "%{http_code}" "https://<projeto>.vercel.app/"
```

## Pitfalls específicos

⚠️ **SSO Protection bloqueia acesso público** — Projetos sob team account
herdam `ssoProtection: {deploymentType: "all_except_custom_domains"}`.
Resultado: `.vercel.app` retorna 401. Desabilitar via API (ver passo 4).

⚠️ **Vercel CLI auth token location** — Em alguns Linux, o token fica em
`~/.local/share/com.vercel.cli/auth.json`, não em `~/.vercel/auth.json`.
Sempre verificar ambos.

⚠️ **Deploy sem `--prebuilt` serve conteúdo stale** — O `vercel deploy --prod --yes`
padrão pode ignorar arquivos locais e usar cache do build server-side.
Sempre usar `vercel build --prod --yes` + `vercel deploy --prebuilt --prod --yes`.

⚠️ **Chart.js destrói charts ao navegar** — Sempre chamar `destroyCharts()`
antes de renderizar nova view para evitar memory leak de canvas.

## Exemplo real: VERO (gestão agrícola)

- PRD de 7 épicos + UI reference doc com 15 modais detalhados
- Pesquisa: 2 queries (concorrentes BR + agtech SaaS)
- SPA: 55KB, 12 views, 8 modais, 4 gráficos, 20+ variáveis CSS
- Deploy: https://vero-plum.vercel.app (~8s build)
- Tempo total: ~15min do clone ao deploy
