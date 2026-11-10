// Auditoría de la salida estática antes de una vista previa o publicación.
// Uso desde web/: `npm run audit:dist` (tras `npm run build`); `-- --report RUTA` escribe un resumen JSON.
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, relative, dirname, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { gzipSync } from 'node:zlib';

const root = resolve(import.meta.dirname, '..');
const dist = join(root, 'dist'), publicData = join(root, 'public/data/v1');
const DATA = ['barrios.geojson', 'cobertura.json', 'manifest.json', 'panel-mensual.json', 'perfiles.json', 'priorizacion-2025.json'];
const ALLOWED = [/^index\.html$/, /^404\.html$/, /^favicon\.svg$/, /^_astro\/[\w.-]+\.(js|css)$/, ...DATA.map(f => new RegExp(`^data/v1/${f.replace(/[.-]/g, '\\$&')}$`))];
const EXTERNAL_LINKS = new Set(['data.buenosaires.gob.ar']);
const BUDGET = { initialJsBytes: 60_000, totalBytes: 8_000_000 };
const SECRET = [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, /\bAKIA[0-9A-Z]{16}\b/, /\bgh[pousr]_[A-Za-z0-9]{36}\b/, /\bsk-[A-Za-z0-9_-]{20,}\b/, /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/];
const LOCAL_PATH = /[A-Za-z]:\\\\?Users|\/Users\/[A-Za-z]|\/home\/[A-Za-z]|OneDrive/;

const errors = [];
const fail = (msg) => errors.push(msg);
const sha = (buf) => createHash('sha256').update(buf).digest('hex');
const walk = (dir) => readdirSync(dir).flatMap(name => { const p = join(dir, name); return statSync(p).isDirectory() ? walk(p) : [p]; });
const files = walk(dist).map(p => ({ path: relative(dist, p).replaceAll('\\', '/'), bytes: readFileSync(p) }));

// 1. Solo archivos esperados: sin mapas de código, CSV, modelos, notebooks ni configuraciones.
for (const f of files) if (!ALLOWED.some(rx => rx.test(f.path))) fail(`Archivo no permitido en dist: ${f.path}`);
for (const f of DATA) if (!files.some(x => x.path === `data/v1/${f}`)) fail(`Falta data/v1/${f}`);

// 2. Datos idénticos al paquete versionado y a los hashes del manifiesto.
const manifest = JSON.parse(readFileSync(join(dist, 'data/v1/manifest.json'), 'utf8'));
if (manifest.schema_version !== '1.0.0') fail(`Esquema inesperado: ${manifest.schema_version}`);
for (const name of DATA) {
  const served = files.find(x => x.path === `data/v1/${name}`)?.bytes;
  if (!served) continue;
  if (!served.equals(readFileSync(join(publicData, name)))) fail(`${name} difiere de public/data/v1`);
  const entry = manifest.archivos[name];
  if (name !== 'manifest.json' && (!entry || entry.sha256 !== sha(served) || entry.bytes !== served.length)) fail(`${name} no coincide con el manifiesto`);
}

// 3. Granularidad: solo agregados barrio-mes, barrio-mes objetivo y barrio.
const readData = (name) => JSON.parse(readFileSync(join(dist, 'data/v1', name), 'utf8'));
const keysOf = (rows, expected, label, count) => {
  if (rows.length !== count) fail(`${label}: ${rows.length} filas, se esperaban ${count}`);
  const want = [...expected].sort().join(',');
  const bad = rows.find(r => Object.keys(r).sort().join(',') !== want);
  if (bad) fail(`${label}: campos inesperados ${Object.keys(bad).join(',')}`);
};
keysOf(readData('panel-mensual.json'), ['anomalia_mes', 'area_km2', 'composicion_modo', 'hechos', 'hechos_por_km2', 'id_barrio', 'mes'], 'panel', 4032);
keysOf(readData('priorizacion-2025.json'), ['gap_meses', 'horizonte_meses', 'id_barrio', 'mes_objetivo', 'mes_observable', 'puntajes', 'resultado_posterior', 'selecciones'], 'priorizacion', 576);
keysOf(readData('perfiles.json'), ['grupo', 'id_barrio', 'k3', 'perfil_k3'], 'perfiles', 48);
const geo = readData('barrios.geojson');
keysOf(geo.features.map(f => f.properties), ['comuna', 'id_barrio', 'nombre'], 'geometrías', 48);

// 4. HTML: ningún recurso de terceros; enlaces externos solo a las fuentes atribuidas.
for (const page of files.filter(f => f.path.endsWith('.html'))) {
  const html = page.bytes.toString('utf8');
  for (const [, attr, url] of html.matchAll(/<(?:script|link|img|iframe|source|video|audio)\b[^>]*?\b(src|href)="([^"]+)"/g))
    if (/^(https?:)?\/\//.test(url)) fail(`${page.path}: recurso externo ${attr}=${url}`);
  for (const [, url] of html.matchAll(/<a\b[^>]*?href="(https?:\/\/[^"]+)"/g))
    if (!EXTERNAL_LINKS.has(new URL(url).hostname)) fail(`${page.path}: enlace externo no previsto ${url}`);
  if (page.path === 'index.html' && !html.includes('CC-BY-2.5-AR')) fail('index.html: falta la atribución de Barrios');
}

// 5. Secretos, rutas locales y mapas de código.
for (const f of files) {
  const text = f.bytes.toString('utf8');
  for (const rx of SECRET) if (rx.test(text)) fail(`${f.path}: posible secreto (${rx})`);
  if (LOCAL_PATH.test(text)) fail(`${f.path}: contiene una ruta local`);
  if (/sourceMappingURL=/.test(text)) fail(`${f.path}: referencia a mapa de código`);
}

// 6. Presupuestos: JS inicial (scripts enlazados por index.html) y tamaño total.
const index = files.find(f => f.path === 'index.html').bytes.toString('utf8');
const initial = [...index.matchAll(/<script\b[^>]*src="\/([^"]+)"/g)].map(m => m[1]);
const initialBytes = initial.reduce((n, p) => n + (files.find(f => f.path === p)?.bytes.length ?? 0), 0);
const totalBytes = files.reduce((n, f) => n + f.bytes.length, 0);
if (initialBytes > BUDGET.initialJsBytes) fail(`JS inicial ${initialBytes} B supera ${BUDGET.initialJsBytes} B`);
if (totalBytes > BUDGET.totalBytes) fail(`Salida ${totalBytes} B supera ${BUDGET.totalBytes} B`);

const git = (...args) => { try { return execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim(); } catch { return null; } };
const summary = {
  resultado: errors.length ? 'fallido' : 'aprobado',
  commit: git('rev-parse', 'HEAD'),
  arbol_con_cambios: git('status', '--porcelain') !== '',
  schema_version: manifest.schema_version, data_version: manifest.data_version, fecha_corte: manifest.fecha_corte,
  js_inicial_bytes: initialBytes, total_bytes: totalBytes,
  total_gzip_bytes: files.reduce((n, f) => n + gzipSync(f.bytes, { level: 9 }).length, 0),
  archivos: files.map(f => ({ ruta: f.path, bytes: f.bytes.length, sha256: sha(f.bytes) })).sort((a, b) => a.ruta.localeCompare(b.ruta)),
  errores: errors,
};
const reportIndex = process.argv.indexOf('--report');
if (reportIndex > 0) { const out = resolve(process.argv[reportIndex + 1]); mkdirSync(dirname(out), { recursive: true }); writeFileSync(out, JSON.stringify(summary, null, 2) + '\n'); }
console.log(`Auditoría de dist: ${summary.resultado} · ${files.length} archivos · ${totalBytes} B (${summary.total_gzip_bytes} B gzip) · JS inicial ${initialBytes} B · datos ${manifest.data_version}`);
for (const e of errors) console.error(`  ✗ ${e}`);
process.exit(errors.length ? 1 : 0);
