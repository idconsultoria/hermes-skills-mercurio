// Renderiza HTML A4 -> PDF via Playwright/Chromium (mesmo motor da proposta comercial).
// Uso: node render_a4.mjs <entrada.html> <saida.pdf>
// ATENCAO: os env vars precisam ser definidos ANTES do require('playwright').
process.env.PLAYWRIGHT_BROWSERS_PATH ||= '/opt/data/.playwright';
process.env.NODE_PATH ||= '/opt/mercurio-data/node_modules';
import { createRequire } from 'node:module';
import fs from 'fs';
import path from 'path';

const require = createRequire(import.meta.url);

const CANDIDATES = [
  process.env.CHROMIUM_BIN,
  '/opt/data/.playwright/chromium-1129/chrome',
  '/opt/data/.playwright/chromium-1117/chrome-linux/chrome',
].filter(Boolean);
const CHROMIUM = CANDIDATES.find((p) => { try { return fs.existsSync(p); } catch { return false; } });
if (!CHROMIUM) { console.error('Chromium nao encontrado em: ' + CANDIDATES.join(', ')); process.exit(1); }

const { chromium } = require('/opt/mercurio-data/node_modules/playwright');

(async () => {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    console.error('Uso: node render_a4.mjs <entrada.html> <saida.pdf>');
    process.exit(1);
  }
  const browser = await chromium.launch({
    executablePath: CHROMIUM,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--font-render-hinting=none'],
  });
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
  await page.goto('file://' + path.resolve(inputHtml), { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  const warn = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.page').forEach((p, i) => {
      const over = p.scrollHeight - p.clientHeight;
      if (over > 2) out.push(`pagina ${i + 1}: overflow ${over}px`);
    });
    return out;
  });
  if (warn.length) console.warn('ATENCAO ' + warn.join(' | '));
  await page.pdf({ path: outputPdf, format: 'A4', printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
  console.log(`OK: ${outputPdf} (chromium: ${CHROMIUM})`);
})().catch((e) => { console.error('Erro renderizando PDF:', e.message); process.exit(1); });
