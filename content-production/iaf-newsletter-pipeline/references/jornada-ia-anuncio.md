# Jornada de IA — Snippet de Anúncio (HTML + CSS)

Copie este bloco para o template `iaf_v3_reference.html`. O CSS vai dentro da tag `<style>`, o teaser após `</header>` e antes de `<!-- HOT TAKE -->`, o card após `</section>` da Análise e antes de `<!-- RADAR -->`.

## CSS (adicionar dentro da tag `<style>`)

```css
/* ===== ANÚNCIO JORNADA DE IA ===== */
/* Teaser no topo — texto-destaque clicável que rola até o card */
.promo-teaser {
  display: block;
  text-decoration: none;
  background: linear-gradient(135deg, rgba(199,91,62,0.06) 0%, rgba(184,134,11,0.04) 100%);
  border: 1px solid rgba(184,134,11,0.2);
  border-radius: var(--border-radius-sm);
  padding: 10px 16px;
  margin-bottom: 24px;
  font-family: var(--font-body);
  font-size: 12px;
  color: #5a4a1f;
  transition: background 0.2s, border-color 0.2s;
}
.promo-teaser:hover {
  background: linear-gradient(135deg, rgba(199,91,62,0.1) 0%, rgba(184,134,11,0.07) 100%);
  border-color: rgba(184,134,11,0.4);
}
.promo-teaser-icon {
  display: inline-block;
  margin-right: 6px;
  font-size: 13px;
}
.promo-teaser strong {
  color: var(--accent-amber);
  font-weight: 700;
}
.promo-teaser .teaser-arrow {
  float: right;
  color: var(--accent-amber);
  font-family: var(--font-code);
  font-size: 10px;
  font-weight: 700;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.promo-teaser:hover .teaser-arrow { opacity: 1; }

/* Card de anúncio entre Análise e Radar */
.promo-card {
  background: linear-gradient(135deg, rgba(199,91,62,0.03) 0%, rgba(184,134,11,0.04) 100%);
  border: 1px solid rgba(184,134,11,0.22);
  border-left: 3px solid var(--accent-amber);
  border-radius: 0 var(--border-radius-lg) var(--border-radius-lg) 0;
  padding: 20px 24px;
  margin-bottom: 36px;
  scroll-margin-top: 40px;
}
.promo-card-label {
  font-family: var(--font-code);
  font-size: 8.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--accent-amber);
  margin-bottom: 8px;
}
.promo-card-title {
  font-family: var(--font-title);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.3;
}
.promo-card-desc {
  font-size: 12.5px;
  color: #4a555d;
  line-height: 1.65;
  margin-bottom: 10px;
}
.promo-card-desc strong { color: var(--accent-primary); }
.promo-card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}
.promo-card-feature {
  font-family: var(--font-code);
  font-size: 10px;
  color: #5a6b72;
  display: flex;
  align-items: center;
  gap: 5px;
}
.promo-card-feature .feat-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--accent-amber);
  flex-shrink: 0;
}
.promo-card-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-code);
  font-size: 10.5px;
  font-weight: 600;
  color: var(--accent-amber);
  text-decoration: none;
  border-bottom: 1px dashed rgba(184,134,11,0.3);
  padding-bottom: 1px;
  transition: color 0.2s, border-color 0.2s;
}
.promo-card-link:hover { color: #9a6f09; border-color: rgba(184,134,11,0.6); }
```

Adicione também `scroll-behavior: smooth;` ao `body`:

```css
body {
  /* ... propriedades existentes ... */
  scroll-behavior: smooth;
}
```

## HTML — Teaser (após `</header>`, antes de `<!-- HOT TAKE -->`)

```html
<!-- ▓▓▓ ANÚNCIO TEASER — antes do Editorial ▓▓▓ -->
<a href="#anuncio-jornada" class="promo-teaser">
  <span class="promo-teaser-icon">⚡</span>
  <strong>Domine IA do zero ao agente autônomo</strong> — 3 cursos práticos, lives semanais com o instrutor, zero assinatura.
  <span class="teaser-arrow">↓ ver</span>
</a>
```

## HTML — Card (entre `</section>` da Análise e `<!-- RADAR -->`)

```html
<!-- ▓▓▓ ANÚNCIO — Jornada de IA · ID Consultoria ▓▓▓ -->
<!-- ⚠️ ANÚNCIO FIXO — NÃO REMOVER. Presente em todas as edições. -->
<section class="section" id="anuncio-jornada">
  <div class="promo-card">
    <div class="promo-card-label">Jornada de IA · ID Consultoria</div>
    <div class="promo-card-title">Do zero ao agente autônomo em 3 cursos práticos</div>
    <div class="promo-card-desc">
      A trilha mais direta para dominar IA no Brasil. Lives semanais com o instrutor ao vivo,
      comunidade ativa no WhatsApp e <strong>zero exigência de assinatura paga</strong>.
      Inscrições abertas — comece pelo nível certo para você.
    </div>
    <div class="promo-card-features">
      <span class="promo-card-feature"><span class="feat-dot"></span> C1 Ferramentas → R$597</span>
      <span class="promo-card-feature"><span class="feat-dot"></span> C2 Assistentes → R$1.497</span>
      <span class="promo-card-feature"><span class="feat-dot"></span> C3 Agentes → R$2.497</span>
      <span class="promo-card-feature"><span class="feat-dot"></span> 30 dias de garantia</span>
    </div>
    <a class="promo-card-link" href="https://idconsultoria.ai/jornada-ia">↗ Ver cursos e preços completos</a>
  </div>
</section>
```

## Preview funcional

Arquivo: `/opt/data/cron/history/iaf_2026-07-17_preview_anuncio.html`

Abra no navegador para ver o teaser + card integrados a uma edição real.
