import {test,expect} from '@playwright/test';
import reference from '../fixtures/simulation.json' with {type:'json'};
// Referencia textual independiente de ICU: dos decimales, coma decimal y « %».
const pct=(n:number)=>`${(Math.round(n*10000)/100).toFixed(2).replace('.',',')} %`;
async function ids(page:import('@playwright/test').Page,kind:string){return page.locator(`#neighborhood-list button[data-selected-${kind}="true"]`).evaluateAll(buttons=>buttons.map(b=>Number((b as HTMLElement).dataset.id)).sort((a,b)=>a-b));}
test('coberturas anuales, IC, selecciones y empates de los 12 meses',async({page})=>{
 test.setTimeout(90000);
 await page.goto('/?vista=simulador&mes=2025-01&barrio=21&metrica=hechos');
 await expect(page.locator('#annual-strategy')).toHaveText('43,05 %');
 await expect(page.locator('#annual-baseline')).toHaveText('42,73 %');
 await expect(page.locator('#annual-ci')).toContainText(/[-−]0,07/);
 await expect(page.locator('#annual-ci')).toContainText('+0,80');
 await expect(page.locator('#annual-ci')).toContainText('incluye cero');
 await expect(page.locator('#month-label')).toHaveText('01 / MES OBJETIVO');
 await expect(page.locator('#gain-reference')).toContainText('92 % de la ganancia sobre el azar');
 await expect(page.locator('#cutoff')).toContainText('Información hasta 2024-12');
 await expect(page.locator('#map')).toHaveAttribute('data-ready','true');
 for(const k of [5,10,15]){
  await page.getByLabel('Cantidad de barrios K').selectOption(String(k));
  for(const ref of reference.references.filter(r=>r.k===k&&r.strategy==='clasificador')){
   await page.getByLabel('Mes objetivo').selectOption(ref.month);
   await expect(page.locator('#monthly-coverage')).toHaveText(pct(ref.captured/ref.total));
   await expect(page.locator('#monthly-counts')).toContainText(`${ref.captured} / ${ref.total}`);
   expect(await ids(page,'strategy')).toEqual(ref.ids);
   const base=reference.references.find(r=>r.month===ref.month&&r.k===k&&r.strategy==='historial_media12')!;
   expect(await ids(page,'baseline')).toEqual(base.ids);
   await expect(page.locator('#map')).toHaveAttribute('data-month',ref.month);
  }
 }
 // Paso 10: para K=15 el IC por bloques del clasificador queda enteramente bajo cero.
 await expect(page.locator('#annual-ci')).toContainText('por debajo de cero');
 expect(reference.references.some(r=>r.strategy==='historial_media12'&&r.boundary_tie)).toBe(true);
});
test('estrategias, oráculo, URL y regreso al atlas',async({page})=>{
 await page.goto('/?vista=simulador&mes=2025-01&barrio=21&metrica=densidad&k=10');
 for(const strategy of ['regresion','historial_media12','historial_persistencia','oraculo']){
  await page.getByLabel('Estrategia',{exact:true}).selectOption(strategy);
  const ref=reference.references.find(r=>r.strategy===strategy&&r.month==='2025-01'&&r.k===10)!;
  expect(await ids(page,'strategy')).toEqual(ref.ids);
  await expect(page.locator('#monthly-coverage')).toHaveText(pct(ref.captured/ref.total));
 }
 await expect(page.locator('#strategy-explanation')).toContainText('No es un pronóstico utilizable al corte');
 await page.reload();await expect(page.getByLabel('Estrategia',{exact:true})).toHaveValue('oraculo');
 await page.getByRole('button',{name:'Atlas histórico',exact:true}).click();
 await expect(page.locator('#simulation')).toBeHidden();await expect(page.locator('#value')).toHaveText('4');
 await expect(page.locator('#map')).toHaveAttribute('data-view','atlas');
 await expect(page.getByLabel('Mes observado')).toHaveValue('2025-01');
 await expect(page.locator('#neighborhood-list button[data-selected-strategy]')).toHaveCount(0);
});
test('reproducción mensual, pausa y cambio de vista',async({page})=>{
 await page.goto('/?vista=simulador&mes=2025-01');
 await page.getByRole('button',{name:'Mes siguiente',exact:true}).click();
 await expect(page.getByLabel('Mes objetivo')).toHaveValue('2025-02');
 await page.getByRole('button',{name:'Mes anterior',exact:true}).click();
 await expect(page.getByLabel('Mes objetivo')).toHaveValue('2025-01');
 await page.getByRole('button',{name:'Reproducir meses',exact:true}).click();
 await expect(page.getByLabel('Mes objetivo')).toHaveValue('2025-02',{timeout:5000});
 await page.getByRole('button',{name:'Pausar reproducción',exact:true}).click();
 await expect(page.getByRole('button',{name:'Reproducir meses',exact:true})).toBeVisible();
 await page.getByLabel('Mes objetivo').selectOption('2025-12');
 await expect(page.getByRole('button',{name:'Mes siguiente',exact:true})).toBeDisabled();
 await page.getByLabel('Mes objetivo').selectOption('2024-12');
 await expect(page.locator('#simulation-results')).toBeHidden();
 await expect(page.locator('#cutoff')).toContainText('Sin evaluación retrospectiva');
});
test('perfiles principales y exploratorios, teclado y móvil',async({page},info)=>{
 await page.goto('/?vista=perfiles&mes=2025-07&barrio=15&nivel=2');
 await expect(page.locator('#map')).toHaveAttribute('data-ready','true');
 await expect(page.locator('#profile-summary')).toHaveText('39 barrios de interior · 9 barrios de borde.');
 await expect(page.locator('#neighborhood-list .badge').filter({hasText:'Borde'})).toHaveCount(9);
 await page.getByLabel('Nivel de perfiles').selectOption('3');
 await expect(page.locator('#profile-warning')).toContainText('separación débil');
 await expect(page.locator('#neighborhood-list .badge').filter({hasText:'Interior residencial'})).toHaveCount(22);
 await expect(page.locator('#neighborhood-list .badge').filter({hasText:'Interior central-denso'})).toHaveCount(17);
 await page.reload();await expect(page.getByLabel('Nivel de perfiles')).toHaveValue('3');
 await page.getByLabel('Buscar barrio').fill('Liniers');await page.getByLabel('Buscar barrio').press('Tab');await page.keyboard.press('Enter');
 await expect(page.locator('#feature-detail')).toContainText('Borde');
 await expect(page.getByRole('button',{name:'Seleccionar Liniers'})).toBeFocused();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:`test-results/profiles-${info.project.name}.png`,fullPage:true,scale:'css'});
});

