# Executive Summary — Prompt Template para Agy

Quando o usuário pedir **sumário executivo** no relatório de custos, use este prompt para o agy.

## Instruções

1. Copiar o HTML base (relatório sem sumário) para o host via SCP
2. Criar um prompt.md com o conteúdo abaixo, personalizado com os dados do projeto
3. SCP o prompt e executar: `ssh oracle-host 'cat /tmp/prompt-exec.md | timeout 300 agy 2>&1'`
4. SCP o resultado de volta

## Template do Prompt

```
# Adicionar Sumário Executivo ao Relatório de Custos

## Contexto

O arquivo /home/ubuntu/relatorio-base.html é um relatório técnico de custos.
A tarefa é APENAS adicionar um Sumário Executivo entre o fechamento da 
`<div class="hero">` e a abertura de `<h2>1. Introdução e Escopo</h2>`.
NÃO altere absolutamente nada do conteúdo existente.

## Bloco a Inserir

<div class="executive-summary">
  <h2>📌 Sumário Executivo</h2>

  <!-- 4 KPI Cards (grid 4 colunas) -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0;">
    <div style="background:var(--white);border:1px solid var(--blue-border);border-radius:10px;padding:20px;">
      <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);font-weight:600;margin-bottom:6px;">Custo Total MVP</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;color:var(--primary);">$X.XX</div>
    </div>
    <div style="background:var(--white);border:1px solid var(--blue-border);border-radius:10px;padding:20px;">
      <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);font-weight:600;margin-bottom:6px;">Tokens Processados</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;color:var(--primary);">279,0 M</div>
    </div>
    <div style="background:var(--white);border:1px solid var(--blue-border);border-radius:10px;padding:20px;">
      <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);font-weight:600;margin-bottom:6px;">Economia com Cache</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;color:var(--green-accent);">~36×</div>
    </div>
    <div style="background:var(--white);border:1px solid var(--blue-border);border-radius:10px;padding:20px;">
      <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-muted);font-weight:600;margin-bottom:6px;">Maior Gasto</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;color:#d97706;">$X.XX</div>
    </div>
  </div>

  <!-- Tabela de Tokens por Modelo -->
  <h3 style="font-size:1rem;font-weight:600;color:var(--blue-text);margin:24px 0 12px;">Tokens por Modelo</h3>
  <table>
    <thead>
      <tr>
        <th>Agente / Modelo</th>
        <th class="num">Cache Hit (input)</th>
        <th class="num">Cache Miss (input)</th>
        <th class="num">Output (gerado)</th>
        <th class="num">Total Tokens</th>
        <th class="num">Hit Rate</th>
        <th class="num">Custo</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>Hermes</strong> — DS V4 Flash</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">~99%</td><td class="num">$X.XX</td></tr>
      <tr><td><strong>Pi Agent</strong> — DS V4 Pro</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">~97%</td><td class="num">$X.XX</td></tr>
      <tr><td><strong>Pi Agent</strong> — DS V4 Flash</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">~99%</td><td class="num">$X.XX</td></tr>
      <tr><td><strong>Grátis</strong> — Gemini + MiniMax</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">[N]</td><td class="num">—</td><td class="num">$0,00</td></tr>
    </tbody>
    <tfoot>
      <tr style="font-weight:700;background:var(--blue-bg);">
        <td><strong>TOTAL GERAL</strong></td>
        <td class="num"><strong>[N]</strong></td>
        <td class="num"><strong>[N]</strong></td>
        <td class="num"><strong>[N]</strong></td>
        <td class="num"><strong>[N]</strong></td>
        <td class="num"><strong>~99%</strong></td>
        <td class="num"><strong>$X.XX</strong></td>
      </tr>
    </tfoot>
  </table>

  <!-- Callout de Total de Tokens -->
  <div class="callout blue" style="margin-top:20px;">
    <p style="font-family:'Space Mono',monospace;font-size:0.9rem;">
      Cache Hit:   <strong>[N]</strong> tokens  (98,98% do total)<br>
      Cache Miss:   <strong>[N]</strong> tokens  (1,02% do total)<br>
      Output:       <strong>[N]</strong> tokens<br>
      <strong style="font-size:1rem;">─────────────────────────────────</strong><br>
      <strong style="font-size:1.2rem;">Total: [N] tokens</strong>
    </p>
    <p style="margin-top:8px;">99% dos tokens de input vieram do cache — sem ele, o custo total saltaria de <strong>$X.XX</strong> para aproximadamente <strong>$XX</strong>.</p>
  </div>

  <!-- 4 Key Insights (grid 2x2) -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:24px 0 0;">
    <div class="callout green" style="margin:0;">
      <strong>✅ MVP por $X.XX</strong><br>
      Custo total: mais barato que um café.
    </div>
    <div class="callout blue" style="margin:0;border-left-color:var(--primary);">
      <strong>🧠 Cache é o Herói Invisível</strong><br>
      98,98% dos tokens vieram do cache.
    </div>
    <div class="callout" style="margin:0;background:#fef3c7;border-left-color:#d97706;">
      <strong>⚠️ Hermes é X% do Custo</strong><br>
      Agente orquestrador: maior parte do gasto.
    </div>
    <div class="callout green" style="margin:0;">
      <strong>🆓 Agentes Grátis</strong><br>
      MiniMax + Gemini Free: $0,00.
    </div>
  </div>
</div>

<style>
  .executive-summary {
    background: var(--blue-bg);
    border: 2px solid var(--blue-border);
    border-radius: 16px;
    padding: 36px;
    margin: -40px auto 40px;
    max-width: 960px;
    position: relative;
    z-index: 2;
    box-shadow: 0 8px 24px rgba(0,0,255,0.06);
  }
  .executive-summary h2 {
    font-family: 'Spectral', Georgia, serif;
    font-size: 1.5rem;
    color: var(--primary);
    margin-top: 0;
    border-bottom: none;
  }
</style>
```

## Entrega

O HTML final deve ser zipado antes de enviar ao Telegram:
```bash
python3 -c "import shutil, os; os.chdir('/opt/data/code/workstation'); shutil.make_archive('relatorio', 'zip', '.', 'relatorio.html')"
```
