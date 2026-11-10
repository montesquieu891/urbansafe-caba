# Registro de publicación web — fase 5

## Historial

| # | Fecha (UTC) | Versión de producción | Vista previa | Commit | Datos | Cambio |
|---|---|---|---|---|---|---|
| 2 | 2026-11-10 | `247ce276-3066-4add-8da2-c4ac73963a73` (vigente) | `8e1686f7-9446-4d63-9938-b8bb6262f6d0` | `8dc8184` (PR #6) | `2019-2025-692728914e40` | Revisión pedagógica del simulador y los perfiles; procedencia con finales de línea normalizados. Datos idénticos. |
| 1 | 2026-11-10 21:21 | `f6889653-5182-4034-acf7-749742da76e2` | `640eef13-6d22-4b3b-a315-f78639326928` | `75393cf` | `2019-2025-5685c2f9c0a0` | Primera publicación (fases 0–4). |

Para volver a la versión 1: `npx wrangler rollback f6889653-5182-4034-acf7-749742da76e2` (desde `web/`).

### Versión 2 — revisión pedagógica

Autorizada expresamente después de revisar los cambios. El commit `8dc8184` incluye la fusión del PR #6, con el árbol limpio.

Verificación:

- **Local:** `npm run release:preview` ejecutó `test:release` (40/40 E2E y auditoría aprobada, JS inicial 27 kB) antes de subir. `export_web_data.py --check` sin discrepancias en la copia normalizada a LF.
- **Vista previa:** 12/12 archivos servidos idénticos a `dist/`, CSP activa, manifiesto con la versión `692728914e40` y **40/40 E2E remotas**.
- **Producción:** los mismos controles, con resultado igual (12/12 idénticos y 40/40 E2E remotas).

Los informes de `docs/evidence/web_phase5/` corresponden a esta versión; los de la versión 1 están en el historial de Git (commit `bba2992`). Los datos tienen caché de una hora, así que un navegador que ya visitó el sitio puede mostrar hasta una hora la versión anterior del manifiesto. Las cifras no cambian.

## Versión 1 — primera publicación

| Campo | Valor |
|---|---|
| URL pública | **https://urbansafe-caba.urbansafe-atlas.workers.dev** |
| Fecha | 2026-11-10, 21:21 UTC |
| Autorización | Pedida expresamente en la sesión, después de revisar la vista previa |
| Alojamiento | Cloudflare Workers con recursos estáticos (Pages integrado en Workers), sin código de servidor |
| Worker de producción | `urbansafe-caba` · versión `f6889653-5182-4034-acf7-749742da76e2` (reemplazada por la versión 2) |
| Worker de vista previa | `urbansafe-caba-preview` · versión `640eef13-6d22-4b3b-a315-f78639326928` · https://urbansafe-caba-preview.urbansafe-atlas.workers.dev |
| Código fuente | Commit `75393cf`. `web/src`, `web/public` y `astro.config.mjs` no cambiaron después, así que la compilación publicada corresponde a ese commit. |
| Datos | Esquema `1.0.0`, versión `2019-2025-5685c2f9c0a0`, corte de observaciones 2025-12-31 |
| Salida | 15 archivos en `dist/` (14 servidos más `_headers`, que Cloudflare usa como configuración), 7,18 MB, ~823 kB gzip, JS inicial 21,7 kB |
| Auditoría | [vista previa](evidence/web_phase5/dist-audit-preview.json) y [producción](evidence/web_phase5/dist-audit-production.json), con hashes idénticos por archivo |
| Herramientas | wrangler 4.160.0 · Astro 7 · Playwright con Chromium |

La primera opción era Cloudflare Pages clásico (`*.pages.dev`). Wrangler 4.160 redirige los proyectos de Pages a Workers, y el usuario eligió ese modelo actual en lugar de forzar el producto anterior. El subdominio de cuenta `urbansafe-atlas` no expone datos personales.

### Verificación de la versión 1

Se hizo antes de promover a producción, en la vista previa, y se repitió en producción con los mismos resultados:

- `npm run test:release` en local: check, compilación, `audit:dist` y 38/38 E2E.
- Contenido servido idéntico, por SHA-256, a `dist/`: los seis archivos de datos, todo `_astro/` y el favicon. `/` sirve `index.html`; `/index.html` redirige a `/`; las rutas inexistentes y `/_headers` devuelven 404 con la página propia.
- Cabeceras aplicadas: CSP (`script-src 'self'`, `frame-ancestors 'none'`), `nosniff`, `Referrer-Policy`, `Permissions-Policy` y `X-Frame-Options: DENY`. Caché inmutable para `_astro/` y de una hora para `data/v1/`; compresión Brotli.
- **38/38 E2E contra la URL publicada** (`E2E_BASE_URL=…`), en escritorio y en móvil emulado:
  - cifras de cobertura (42,73 % y 43,05 %), IC, 180 selecciones y empates;
  - perfiles;
  - cero observado y meses sin datos;
  - URL con filtros, recarga y Atrás;
  - accesibilidad automática WCAG A/AA;
  - CSP real sin bloqueos;
  - todas las solicitudes al mismo origen;
  - 404, mapa bloqueado y página sin JavaScript.

## Reversión y mantenimiento

Desde `web/`, con sesión de Wrangler (`npx wrangler login`):

```powershell
npx wrangler deployments list                  # versiones activas e identificadores
npx wrangler rollback <id-de-version-anterior> # volver a una versión anterior en segundos
npm run release:preview                        # verificar y publicar en el Worker de vista previa
npm run release:production                     # verificar y publicar en producción
```

Los scripts de publicación ejecutan primero `test:release` y no publican si algo falla. Para verificar una URL publicada: `$env:E2E_BASE_URL='https://…'; npx playwright test`.

Si hubiera que retirar el sitio: `npx wrangler delete` (producción) o `npx wrangler delete --env preview` (vista previa). Antes de cada nueva publicación, registrar aquí el identificador de la versión vigente.

## Limitaciones

- El Worker de vista previa es accesible para cualquiera con el enlace y no envía `noindex`. Puede eliminarse si no se va a usar.
- Las pruebas usan Chromium; no hubo prueba manual en Safari/iOS ni con lectores de pantalla.
- Siguen vigentes las limitaciones metodológicas: datos de 2025 posiblemente provisorios, carga registrada sin ajuste por exposición y una sola temporada de evaluación. La cobertura mide concentración, no siniestros evitados.
- AUSA 2026 sigue fuera del alcance.
