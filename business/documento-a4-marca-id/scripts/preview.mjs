// Gera um PNG por .page do HTML (verificacao visual).
// Uso: node preview.mjs <entrada.html> <diretorio-de-saida>
process.env.PLAYWRIGHT_BROWSERS_PATH ||= '/opt/data/.playwright';
process.env.NODE_PATH ||= '/opt/mercurio-data/node_modules';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const CHROMIUM = process.env.CHROMIUM_BIN || '/opt/data/.playwright/chromium-1129/chrome';
const { chromium } = require('/opt/mercurio-data/node_modules/playwright');

(async () => {
  const [inputHtml, outdir] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: CHROMIUM, headless: true, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
  await page.goto('file://' + inputHtml, { waitUntil: 'networkidle' });
  const els = await page.$$('.page');
  for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: `${outdir}/page${i + 1}.png` });
  console.log('paginas:', els.length);
  await browser.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
