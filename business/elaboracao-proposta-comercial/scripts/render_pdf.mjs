// Renderiza o HTML da proposta em PDF via Playwright/Chromium.
// Uso: node render_pdf.mjs <entrada.html> <saida.pdf>
// Runtime único do proot: /opt/mercurio-data/node_modules
// Browser único: /opt/data/.playwright/chromium-1117/chrome-linux/chrome
if (!process.env.PLAYWRIGHT_BROWSERS_PATH) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.playwright';
}
if (!process.env.NODE_PATH) {
  process.env.NODE_PATH = '/opt/mercurio-data/node_modules';
}
import { createRequire } from 'node:module';
import path from 'path';

const require = createRequire(import.meta.url);
const { chromium } = require('/opt/mercurio-data/node_modules/playwright');
const CHROMIUM = '/opt/data/.playwright/chromium-1117/chrome-linux/chrome';

(async () => {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    console.error('Uso: node render_pdf.mjs <entrada.html> <saida.pdf>');
    process.exit(1);
  }

  const browser = await chromium.launch({
    executablePath: CHROMIUM,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(inputHtml), { waitUntil: 'networkidle' });
  // garante 1 página por slide (os .slide já têm page-break-after: always)
  await page.addStyleTag({ content: '@page { size: 1920px 1080px; margin: 0; }' });
  await page.pdf({
    path: outputPdf,
    width: '1920px',
    height: '1080px',
    printBackground: true,
    preferCSSPageSize: true,
  });
  await browser.close();
  console.log(`OK: ${outputPdf}`);
})().catch((e) => {
  console.error('Erro renderizando PDF:', e.message);
  process.exit(1);
});
