import { test, expect } from '@playwright/test';
// Referencias independientes: data/processed/panel_barrio_mes.csv, leído con pandas.
// Palermo, id=21: 2025-12=68, 2025-01=63, área=15.9216 km².
// Agronomia, id=1: 2019-10=0 hechos; todos sus modos=0.
test('mes, métrica, serie, mapa, lista y URL sincronizados', async ({page},testInfo)=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/?mes=2025-12&barrio=21&metrica=hechos');
 await expect(page.locator('#value')).toHaveText('68');
 await expect(page.locator('#map')).toHaveAttribute('data-ready','true');
 await expect(page.locator('#map')).toHaveAttribute('data-rendered','48');
 await expect(page.locator('#map-fallback')).toBeHidden();
 await expect(page.locator('#neighborhood')).toHaveText('Palermo');
 await expect(page.getByRole('button',{name:'Seleccionar Palermo'})).toHaveAttribute('aria-pressed','true');
 await expect(page.getByRole('button',{name:'Seleccionar Palermo'})).toContainText('68');
 await page.getByLabel('Mes observado').selectOption('2025-01');
 await expect(page.locator('#value')).toHaveText('63');
 await expect(page.locator('#map')).toHaveAttribute('data-month','2025-01');
 await expect(page.locator('#series')).toHaveAttribute('aria-label',/2025-01, 63/);
 await page.getByLabel('Métrica',{exact:true}).selectOption('densidad');
 await expect(page.locator('#value')).toHaveText('4');
 await expect(page.locator('#legend-title')).toHaveText('Densidad · hechos por km²');
 await expect(page.locator('#map')).toHaveAttribute('data-metric','densidad');
 await expect(page).toHaveURL(/mes=2025-01&barrio=21&metrica=densidad/);
 await page.reload();await expect(page.locator('#value')).toHaveText('4');
 await expect(page.locator('#map')).toHaveAttribute('data-ready','true');
 await expect(page.locator('#map-fallback')).toBeHidden();
 await expect(page.getByLabel('Métrica',{exact:true})).toHaveValue('densidad');
 await expect(page.locator('#series-values tr')).toHaveCount(84);
 await page.screenshot({path:`test-results/atlas-${testInfo.project.name}.png`,fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
 expect(errors).toEqual([]);
});
test('búsqueda y selección por teclado conservan foco',async({page})=>{
 await page.goto('/');await expect(page.locator('#value')).toHaveText('68');
 await page.getByLabel('Buscar barrio').fill('Agronomía');
 await expect(page.locator('#neighborhood-list button')).toHaveCount(1);
 await page.getByLabel('Buscar barrio').press('Tab');
 await expect(page.getByRole('button',{name:'Seleccionar Agronomia'})).toBeFocused();
 await page.keyboard.press('Enter');
 await expect(page.locator('#neighborhood')).toHaveText('Agronomia');
 await expect(page.getByRole('button',{name:'Seleccionar Agronomia'})).toBeFocused();
 await expect(page.locator('#map')).toHaveAttribute('data-selected','1');
 await page.getByLabel('Mes observado').selectOption('2019-10');
 await expect(page.locator('#value')).toHaveText('0');
 await expect(page.locator('#observation-note')).toHaveText('Cero hechos registrados en este mes.');
 await expect(page.locator('#modes b')).toHaveText(['0','0','0','0','0','0','0']);
 await page.getByLabel('Buscar barrio').fill('no-existe');
 await expect(page.locator('#empty-search')).toBeVisible();
});
test('fuera de cobertura se muestra ausencia, nunca cero',async({page})=>{
 await page.goto('/?mes=2026-01&barrio=1&metrica=hechos');
 await expect(page.locator('#value')).toHaveText('Sin datos');
 await expect(page.locator('#total')).toHaveText('Sin datos');
 await expect(page.locator('#observation-note')).toHaveText('Sin datos para este período.');
 await expect(page.locator('#map')).toHaveAttribute('data-month','2026-01');
 await expect(page.locator('#neighborhood-list button')).toHaveCount(48);
 await expect(page.locator('#neighborhood-list b').first()).toHaveText('Sin datos');
 await page.reload();await expect(page.locator('#value')).toHaveText('Sin datos');
});
test('atrás restaura filtros y parámetros inválidos se normalizan',async({page})=>{
 await page.goto('/?mes=incorrecto&barrio=999&metrica=otra');
 await expect(page.locator('#value')).toHaveText('68');
 await page.getByLabel('Mes observado').selectOption('2025-01');
 await expect(page.locator('#value')).toHaveText('63');
 await page.goBack();await expect(page.locator('#value')).toHaveText('68');
 await expect(page.getByLabel('Mes observado')).toHaveValue('2025-12');
});
test('error de carga informa y mantiene filtros deshabilitados',async({page})=>{
 await page.route('**/panel-mensual.json',r=>r.fulfill({status:503,body:'Unavailable'}));
 await page.goto('/');
 await expect(page.getByRole('alert')).toContainText('No pudimos cargar el atlas');
 await expect(page.getByLabel('Mes observado')).toBeDisabled();
});

test('clic en polígono actualiza ficha y lista',async({page})=>{
 await page.goto('/?mes=2025-12&barrio=1&metrica=hechos');
 await expect(page.locator('#map')).toHaveAttribute('data-ready','true');
 const canvas=page.locator('#map canvas');
 await canvas.scrollIntoViewIfNeeded();
 const box=await canvas.boundingBox();
 await canvas.click({position:{x:box!.width*.5,y:box!.height*.5}});
 await expect(page.locator('#neighborhood')).not.toHaveText('Agronomia');
 const name=await page.locator('#neighborhood').textContent();
 await expect(page.getByRole('button',{name:`Seleccionar ${name}`})).toHaveAttribute('aria-pressed','true');
 await expect(page.locator('#map-fallback')).toBeHidden();
});
