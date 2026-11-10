import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// QA de fase 4: origen único, consola limpia, accesibilidad automática, enlaces publicados y degradación.
function watch(page: Page) {
 const issues: string[] = [], origins = new Set<string>();
 page.on('request', r => { const u = new URL(r.url()); if (u.protocol.startsWith('http')) origins.add(u.origin); });
 page.on('response', r => { if (r.status() >= 400) issues.push(`HTTP ${r.status()} ${r.url()}`); });
 page.on('requestfailed', r => issues.push(`Fallo de red ${r.url()} ${r.failure()?.errorText}`));
 page.on('pageerror', e => issues.push(`Error de página: ${e.message}`));
 page.on('console', m => { if (m.type() === 'error') issues.push(`Consola: ${m.text()}`); });
 return { issues, origins };
}

test('recorrido completo sin recursos de terceros ni errores', async ({ page, baseURL }) => {
 const { issues, origins } = watch(page);
 await page.goto('/?mes=2025-12&barrio=21&metrica=hechos');
 await expect(page.locator('#map')).toHaveAttribute('data-ready', 'true');
 await page.getByLabel('Métrica', { exact: true }).selectOption('densidad');
 await page.getByRole('button', { name: 'Simulador 2025', exact: true }).click();
 await expect(page.locator('#annual-strategy')).toHaveText('43,05 %');
 await page.getByLabel('Cantidad de barrios K').selectOption('5');
 await page.getByRole('button', { name: 'Perfiles barriales', exact: true }).click();
 await expect(page.locator('#profile-summary')).toContainText('barrios de borde');
 await expect(page.locator('#map')).toHaveAttribute('data-view', 'perfiles');
 expect([...origins]).toEqual([new URL(baseURL!).origin]);
 expect(issues).toEqual([]);
});

for (const [view, url] of [
 ['atlas', '/?mes=2025-12&barrio=21&metrica=hechos'],
 ['simulador', '/?vista=simulador&mes=2025-03&barrio=21&estrategia=clasificador&k=10'],
 ['perfiles', '/?vista=perfiles&mes=2025-07&barrio=15&nivel=3'],
] as const) {
 test(`accesibilidad automática WCAG A/AA: ${view}`, async ({ page }) => {
  await page.goto(url);
  await expect(page.locator('#map')).toHaveAttribute('data-ready', 'true');
  // El lienzo de MapLibre no es contenido textual; su alternativa es la lista de barrios.
  const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).exclude('#map canvas').analyze();
  expect(result.violations.map(v => `${v.id}: ${v.nodes.map(n => n.target.join(' ')).slice(0, 5).join(' | ')}`)).toEqual([]);
 });
}

test('manifiesto, descarga y atribuciones publicadas', async ({ page, request }) => {
 const manifest = await request.get('/data/v1/manifest.json');
 expect(manifest.ok()).toBe(true);
 const body = await manifest.json();
 expect(body.schema_version).toBe('1.0.0');
 await page.goto('/');
 await expect(page.locator('#version')).toContainText(body.data_version);
 const download = page.getByRole('link', { name: /Descargar panel mensual/ });
 await expect(download).toHaveAttribute('download', '');
 expect((await request.get((await download.getAttribute('href'))!)).ok()).toBe(true);
 await expect(page.getByRole('link', { name: /Manifiesto y trazabilidad/ })).toHaveAttribute('href', '/data/v1/manifest.json');
 await expect(page.locator('#method')).toContainText('CC-BY-2.5-AR');
 await expect(page.locator('#method')).toContainText('versión no indicada');
});

test('ruta inexistente devuelve 404 con regreso al atlas', async ({ page }) => {
 const response = await page.goto('/no-existe');
 expect(response?.status()).toBe(404);
 await expect(page.getByRole('heading', { name: 'Esta página no existe.' })).toBeVisible();
 await page.getByRole('link', { name: 'Volver al atlas' }).click();
 await expect(page.locator('#value')).toHaveText('68');
});

test('si MapLibre no carga, la lista y la ficha siguen operativas', async ({ page }) => {
 await page.route(/maplibre-gl[^/]*\.js$/, r => r.abort());
 await page.goto('/?vista=simulador&mes=2025-01&barrio=21&k=10');
 await expect(page.locator('#map-fallback')).toBeVisible();
 await expect(page.locator('#neighborhood-list button')).toHaveCount(48);
 await expect(page.locator('#neighborhood-list button[data-selected-strategy="true"]')).toHaveCount(10);
 await page.getByRole('button', { name: /^Seleccionar Flores\b/ }).click();
 await expect(page.locator('#neighborhood')).toHaveText('Flores');
});

test('la CSP de public/_headers no bloquea el sitio', async ({ page, request }) => {
 // Local: `astro preview` sirve _headers como archivo sin aplicarlo, así que se inyecta esa política.
 // Publicado: Cloudflare consume _headers y aplica la cabecera real, que debe estar presente.
 const headersFile = await request.get('/_headers');
 if (headersFile.ok()) {
  const csp = (await headersFile.text()).match(/Content-Security-Policy: (.+)/)![1].trim();
  await page.route(url => url.pathname === '/', async route => { const response = await route.fetch(); await route.fulfill({ response, headers: { ...response.headers(), 'content-security-policy': csp } }); });
 }
 const { issues } = watch(page);
 const response = await page.goto('/?vista=simulador&mes=2025-03&barrio=21&k=10');
 expect(response?.headers()['content-security-policy']).toContain("script-src 'self'");
 await expect(page.locator('#map')).toHaveAttribute('data-ready', 'true');
 await expect(page.locator('#annual-strategy')).toHaveText('43,05 %');
 await expect(page.locator('#legend-items .swatch').first()).toHaveCSS('background-color', 'rgb(65, 109, 101)');
 await page.getByRole('button', { name: 'Perfiles barriales', exact: true }).click();
 await expect(page.locator('#map')).toHaveAttribute('data-view', 'perfiles');
 expect(issues).toEqual([]);
});

test('sin JavaScript se ofrecen los datos', async ({ browser, baseURL }) => {
 const context = await browser.newContext({ javaScriptEnabled: false, baseURL });
 const page = await context.newPage();
 await page.goto('/');
 await expect(page.getByRole('link', { name: 'panel mensual' }).first()).toHaveAttribute('href', '/data/v1/panel-mensual.json');
 await expect(page.getByRole('link', { name: 'manifiesto', exact: true })).toBeVisible();
 await context.close();
});
