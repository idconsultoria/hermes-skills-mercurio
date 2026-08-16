// Renderiza o HTML da proposta em PDF via Playwright/Chromium.
// Uso: node render_pdf.mjs <entrada.html> <saida.pdf>
// Pré-requisito: chromium do Playwright instalado:
//   mkdir -p /opt/data/.playwright && PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright npx playwright install chromium
// (O caminho /opt/hermes/.playwright não tem permissão de escrita.)
if (!process.env.PLAYWRIGHT_BROWSERS_PATH) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.playwright';
}
import { chromium } from 'playwright';
import path from 'path';

(async () => {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    console.error('Uso: node render_pdf.mjs <entrada.html> <saida.pdf>');
    process.exit(1);
  }

  const browser = await chromium.launch();
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
