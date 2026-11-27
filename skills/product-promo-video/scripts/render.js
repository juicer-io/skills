// Frame-by-frame renderer for a seek(t)-driven HTML animation.
// The page must define window.seek(t), window.DURATION (s), optionally window.FPS,
// and set window.ready = true once fonts are loaded and layout is measured. The frame size comes
// from <meta name="video-size" content="WxH"> in the page (default 1920x1080).
//
//   node render.js <page.html> stills <out-dir> 1.5,4.5,11      -> PNG stills at those seconds
//   node render.js <page.html> video  <out.mp4>                 -> silent H.264 MP4
//
// Needs: npm install puppeteer-core ffmpeg-static (in the working folder), Chrome or Edge installed
// (or CHROME_PATH pointing at a Chromium-based browser).
const puppeteer = require('puppeteer-core'), ff = require('ffmpeg-static');
const { spawn } = require('child_process'), path = require('path'), fs = require('fs'), url = require('url');
const CHROME = [process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium'].find(p => p && fs.existsSync(p));
if (!CHROME) { console.error('No Chrome found. Set CHROME_PATH.'); process.exit(1); }
const [page, mode = 'stills', out = 'stills', times] = process.argv.slice(2);
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: true,
    args: ['--allow-file-access-from-files', '--force-device-scale-factor=1', '--hide-scrollbars', '--font-render-hinting=none'] });
  const p = await b.newPage();
  // Frame size from <meta name="video-size" content="1080x1920"> in the page, default 1920x1080.
  const size = (fs.readFileSync(page, 'utf8').match(/name="video-size" content="(\d+)x(\d+)"/) || [0, 1920, 1080]).slice(1).map(Number);
  await p.setViewport({ width: size[0], height: size[1], deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.goto(url.pathToFileURL(path.resolve(page)).href);
  await p.waitForFunction('window.ready===true', { timeout: 30000 });
  const DUR = await p.evaluate(() => window.DURATION), FPS = await p.evaluate(() => window.FPS || 30);
  // The brand font is declared as family "G" in the page; if none of its faces loaded, text is in a fallback font.
  const fontOk = await p.evaluate(async () => {
    const faces = [...document.fonts].filter(f => f.family.replace(/["']/g, '') === 'G');
    await Promise.all(faces.map(f => f.load().catch(() => null)));
    return faces.length > 0 && faces.some(f => f.status === 'loaded');
  });
  if (!fontOk) console.log('WARNING: brand font not loaded, the render uses a fallback font. Not deliverable.');
  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    const ts = (times || '1,5,10,20,30,40,50').split(',').map(Number);
    for (const t of ts) {
      await p.evaluate(t => seek(t), t);
      await p.screenshot({ path: path.join(out, `t${String(t).replace('.', '_')}.png`) });
    }
  } else {
    const f = spawn(ff, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'ignore', 'inherit'] });
    const fail = e => { console.error('ffmpeg failed:', e.message); process.exit(1); };
    f.on('error', fail); f.stdin.on('error', fail);
    const closed = new Promise(r => f.on('close', r));
    const n = Math.round(FPS * DUR);
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => seek(t), i / FPS);
      const buf = await p.screenshot({ type: 'jpeg', quality: 97 });
      if (!f.stdin.write(buf)) await new Promise(r => f.stdin.once('drain', r));
      if (i % 300 === 0) console.log('frame', i, '/', n);
    }
    f.stdin.end();
    const code = await closed;
    if (code !== 0) { console.error(`ffmpeg exited with code ${code}; ${out} is incomplete`); process.exit(1); }
  }
  await b.close();
})();
