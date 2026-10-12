// Render A4 com rodape numerado pelo Chromium — documento de solucoes (ente publico)
// uso: /opt/mercurio-data/node/bin/node render_doc.cjs <in.html> <out.pdf> "<titulo do rodape>"
const { chromium } = require('/opt/mercurio-data/node_modules/playwright');

const CHROMIUM = '/opt/data/.playwright/chromium-1129/chrome'; // copia ARM64 unica do proot

(async () => {
  const [, , INPUT, OUT, TITULO] = process.argv;
  if (!INPUT || !OUT) {
    console.error('uso: node render_doc.cjs <in.html> <out.pdf> "<titulo do rodape>"');
    process.exit(1);
  }
  const rodape = TITULO || 'ID Consultoria';
  const browser = await chromium.launch({
    executablePath: CHROMIUM,
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.goto('file://' + INPUT, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready); // sem isso a fonte tardia desalinha a pagina
  await page.pdf({
    path: OUT,
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      '<div style="width:100%;font-family:Arial,sans-serif;font-size:7pt;color:#7b8c9c;' +
      'padding:0 12mm;display:flex;justify-content:space-between;">' +
      '<span>' + rodape + '</span><span class="pageNumber"></span></div>',
    margin: { top: '11mm', bottom: '13mm', left: '12mm', right: '12mm' },
  });
  await browser.close();
  console.log('ok ->', OUT);
})().catch((e) => {
  console.error('FALHOU:', e && e.message);
  process.exit(1);
});
