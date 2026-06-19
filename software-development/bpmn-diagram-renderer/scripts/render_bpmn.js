#!/usr/bin/env node
/**
 * render_bpmn.js — Converte BPMN 2.0 XML → PNG usando bpmn-js + Chromium headless.
 *
 * Uso: node render_bpmn.js <input.bpmn> [output.png]
 *      ou pipe: cat diagram.bpmn | node render_bpmn.js - output.png
 *
 * Chromium: auto-detecta (Debian extraído → Puppeteer built-in → env vars).
 * Dependências: npm install bpmn-js puppeteer
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// --- Config ---
const VIEWPORT_WIDTH = 1400;
const VIEWPORT_HEIGHT = 900;
const SCALE_FACTOR = 2; // Retina

// --- Argument parsing ---
let inputFile = null;
let outputFile = null;

if (process.argv.length >= 4) {
  inputFile = process.argv[2];
  outputFile = process.argv[3];
} else if (process.argv.length === 3 && process.argv[2] !== '-') {
  inputFile = process.argv[2];
  outputFile = inputFile.replace(/\.(bpmn|xml)$/, '.png');
} else {
  console.error('Uso: node render_bpmn.js <input.bpmn> [output.png]');
  console.error('  ou: cat input.bpmn | node render_bpmn.js - output.png');
  process.exit(1);
}

// --- Resolve Chromium ---
function findChromium() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH && fs.existsSync(process.env.PUPPETEER_EXECUTABLE_PATH)) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }
  if (process.env.CHROMIUM_PATH && fs.existsSync(process.env.CHROMIUM_PATH)) {
    return process.env.CHROMIUM_PATH;
  }
  const debianPath = '/tmp/chromium-extracted/usr/lib/chromium/chromium';
  if (fs.existsSync(debianPath)) {
    return debianPath;
  }
  try {
    const builtin = puppeteer.executablePath();
    if (builtin && fs.existsSync(builtin)) {
      return builtin;
    }
  } catch (e) { /* fallthrough */ }
  return null;
}

// --- Read input ---
let bpmnXML;
if (inputFile === '-') {
  bpmnXML = fs.readFileSync(0, 'utf8');
} else {
  if (!fs.existsSync(inputFile)) {
    console.error(`Arquivo não encontrado: ${inputFile}`);
    process.exit(1);
  }
  bpmnXML = fs.readFileSync(inputFile, 'utf8');
}

if (!bpmnXML || bpmnXML.trim().length === 0) {
  console.error('BPMN XML vazio');
  process.exit(1);
}

// --- Locate bpmn-js ---
const bpmnJSPath = path.join(__dirname, 'node_modules', 'bpmn-js', 'dist', 'bpmn-viewer.production.min.js');
if (!fs.existsSync(bpmnJSPath)) {
  console.error('bpmn-js não encontrado. Execute: npm install');
  process.exit(1);
}
const bpmnJS = fs.readFileSync(bpmnJSPath, 'utf8');

// --- Build HTML ---
const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #fff; }
  #canvas { width: ${VIEWPORT_WIDTH}px; height: ${VIEWPORT_HEIGHT}px; }
</style>
</head>
<body>
<div id="canvas"></div>
<script>${bpmnJS}</script>
<script>
  var viewer = new BpmnJS({ container: '#canvas' });
  var xml = ${JSON.stringify(bpmnXML)};
  viewer.importXML(xml).then(function() {
    var canvas = viewer.get('canvas');
    canvas.zoom('fit-viewport');
    window.__BPMN_READY__ = true;
  }).catch(function(err) {
    document.body.textContent = 'BPMN Error: ' + err.message;
    console.error(err);
    window.__BPMN_ERROR__ = err.message;
  });
</script>
</body>
</html>`;

const htmlPath = path.join('/tmp', `bpmn-render-${Date.now()}.html`);
fs.writeFileSync(htmlPath, html);

// --- Render ---
(async () => {
  const chromiumPath = findChromium();
  if (!chromiumPath) {
    console.error('Chromium não encontrado. Instale: apt-get install chromium-browser');
    process.exit(1);
  }

  console.error(`Chromium: ${chromiumPath}`);

  const browser = await puppeteer.launch({
    executablePath: chromiumPath,
    args: [
      '--no-sandbox',
      '--disable-gpu',
      '--disable-software-rasterizer',
      '--disable-dev-shm-usage'
    ],
    headless: true,
    env: {
      ...process.env,
      LD_LIBRARY_PATH: [
        process.env.LD_LIBRARY_PATH,
        '/tmp/chromium-extracted/usr/lib/chromium',
        '/tmp/chromium-extracted/usr/lib/aarch64-linux-gnu',
      ].filter(Boolean).join(':')
    }
  });

  const page = await browser.newPage();
  await page.setViewport({
    width: VIEWPORT_WIDTH,
    height: VIEWPORT_HEIGHT,
    deviceScaleFactor: SCALE_FACTOR
  });

  const fileUrl = 'file://' + htmlPath;
  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 20000 });

  try {
    await page.waitForFunction('window.__BPMN_READY__ === true', { timeout: 10000 });
  } catch (e) {
    const error = await page.evaluate(() => window.__BPMN_ERROR__ || 'timeout');
    console.error('Falha ao renderizar BPMN:', error);
    await browser.close();
    process.exit(1);
  }

  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: outputFile, fullPage: true });

  await browser.close();
  fs.unlinkSync(htmlPath);

  const stats = fs.statSync(outputFile);
  console.log(outputFile);
  console.error(`OK: ${outputFile} (${(stats.size / 1024).toFixed(1)} KB)`);
})().catch(err => {
  console.error('Erro:', err.message);
  process.exit(1);
});
