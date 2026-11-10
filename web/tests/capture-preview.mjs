// Capturas de revisión visual. Requiere el servidor de desarrollo en 4322.
// Uso desde web/: `node tests/capture-preview.mjs` (fase 2) o `node tests/capture-preview.mjs phase3`.
import {chromium,devices} from '@playwright/test';
const phase=process.argv[2]==='phase3'?'phase3':'phase2';
const views=phase==='phase2'
 ?[['','/?mes=2025-12&barrio=21&metrica=hechos']]
 :[['simulator-','/?vista=simulador&mes=2025-03&barrio=21&metrica=hechos&estrategia=clasificador&k=10'],['profiles-','/?vista=perfiles&mes=2025-07&barrio=15&metrica=hechos&nivel=3']];
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
for (const [name,options] of [['desktop',{viewport:{width:1440,height:1000}}],['mobile',{...devices['iPhone 13'],deviceScaleFactor:1}]]) {
 for (const [prefix,path] of views) {
  const page=await browser.newPage(options);
  await page.goto(`http://127.0.0.1:4322${path}`);
  await page.waitForSelector('#map[data-ready="true"]');
  await page.screenshot({path:`../docs/evidence/web_${phase}/${prefix}${name}.png`,fullPage:true,scale:'css'});
  await page.close();
 }
}
await browser.close();
