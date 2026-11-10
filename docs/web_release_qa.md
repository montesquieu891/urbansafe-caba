# QA integral y vista previa — fase 4

Fase 4 del [plan web](web_implementation_plan.md), 2026-11-10. Vista previa **local** de la compilación estática; no se creó ninguna vista previa remota ni se publicó nada (fase 5, requiere autorización expresa). Autoauditoría de implementación en Claude Code; no se tocaron modelos ni el paquete de datos v1.

## Comando único de verificación

Desde `web/`, con dependencias instaladas (`npm ci`) y Chromium de Playwright:

```powershell
npm run test:release
```

Encadena `astro check`, `astro build`, `npm run audit:dist` y las pruebas E2E. Para registrar la auditoría: `npm run audit:dist -- --report ../docs/evidence/web_phase4/dist-audit.json`. Vista previa local de la compilación: `npm run preview -- --port 4324`. Astro admite un solo `astro preview` por proyecto: deténgalo antes de las pruebas E2E, que levantan el suyo en 4321. Del lado de Python siguen vigentes `python scripts/export_web_data.py --check` y las pruebas de `tests/test_web_data_export.py`.

## Auditoría de la salida (`web/scripts/audit-dist.mjs`)

Revisa `web/dist/` tal como se serviría y falla ante cualquiera de estos casos:

- **Archivos fuera de la lista permitida:** `index.html`, `404.html`, `favicon.svg`, recursos `_astro/*.js|css` y los seis archivos de `data/v1/`. Así quedan excluidos CSV, notebooks, modelos, mapas de código y configuraciones.
- **Datos alterados:** cada archivo de datos debe ser idéntico byte a byte a `web/public/data/v1/` y coincidir en SHA-256 y tamaño con `manifest.json` (esquema 1.0.0).
- **Granularidad:** panel con 4.032 registros barrio-mes, priorización con 576 barrio-mes objetivo, perfiles y geometrías con 48 barrios, cada uno con exactamente los campos del contrato. No se admite ningún registro individual.
- **Recursos de terceros:** ningún `script`, `link`, `img` ni `iframe` externo. Los enlaces externos se limitan a `data.buenosaires.gob.ar` (fuentes atribuidas) y la atribución CC-BY-2.5-AR debe estar presente.
- **Filtraciones:** patrones de claves privadas o tokens, rutas locales (`C:\Users`, `/home/`, OneDrive) y `sourceMappingURL`.
- **Presupuestos:** JS inicial ≤ 60 kB y salida total ≤ 8 MB.

Se comprobó que falla de verdad: con un CSV agregado, un script de un CDN y una ruta local, los tres casos se reportaron y el comando terminó con código 1.

Resultado: 14 archivos; 7,18 MB sin comprimir, unos 823 kB con gzip. La geometría completa sin simplificar (decisión del contrato) es el archivo comprimido más pesado, con unos 261 kB. Hashes por archivo, commit y versión de datos: [dist-audit.json](evidence/web_phase4/dist-audit.json). Se generó antes de confirmar los cambios de esta fase, así que registra el commit base `02680c6` con `arbol_con_cambios: true`. Para la fase 5 debe regenerarse sobre el commit que se publique.

## Cambios de la fase

- **Carga diferida de MapLibre.** El JS inicial pasó de 1,08 MB a unos 22 kB. MapLibre (~1,1 MB, ~290 kB gzip) se descarga después de los datos, cuando la lista, la ficha y los filtros ya funcionan. Si el chunk no carga, aparece la alternativa de lista y el resto sigue operativo (probado). El límite de aviso de Vite se fijó en 1.200 kB para ese chunk conocido: la compilación ya no emite advertencias y el presupuesto real lo controla `audit:dist`.
- **Accesibilidad (WCAG 2.5.3).** axe detectó que el nombre accesible de los botones de barrio («Seleccionar Palermo») no contenía el texto visible (valor y categoría), y que el `aria-label` del logotipo difería de su texto. Ahora el prefijo «Seleccionar» es texto solo para lectores de pantalla y el nombre incluye lo visible; el ícono del logotipo se oculta a tecnologías asistivas.
- **Página 404** propia, con regreso al atlas y enlace al manifiesto. **Favicon** local, que evita una solicitud fallida a `/favicon.ico` en cada visita.

## Pruebas E2E

Las pruebas nuevas están en `web/tests/e2e/release.spec.ts` y se suman a las del atlas y el simulador. Todas corren en escritorio y en móvil emulado:

| Recorrido | Comprobación |
|---|---|
| Atlas → simulador → perfiles | Todas las solicitudes van al mismo origen; ninguna respuesta ≥ 400, ningún fallo de red ni error de consola o de página. |
| Accesibilidad de las tres vistas | Sin violaciones de axe-core WCAG 2.0/2.1 A y AA. Se excluye el lienzo del mapa, cuya alternativa es la lista de barrios. |
| Manifiesto y descarga | El manifiesto responde, su versión coincide con la de la página, el panel se descarga y la atribución y la licencia están visibles. |
| Ruta inexistente | Responde 404, muestra la página propia y vuelve al atlas. |
| MapLibre bloqueado | Se muestra la alternativa; quedan 48 botones y las 10 selecciones, y la ficha responde. |
| Sin JavaScript | Se ofrecen los enlaces al panel y al manifiesto. |

Los criterios ya cubiertos por las fases 2 y 3 siguen en la suite: cero observado, mes sin datos, URL con filtros tras recargar y Atrás, teclado, ausencia de desbordamiento horizontal, cifras 42,73 % y 43,05 %, IC, 180 selecciones con empates y perfiles.

Resultado: **36/36 aprobadas** (18 recorridos × escritorio y móvil). Se revisó también la compilación servida con `astro preview`: 48 polígonos dibujados, cifras correctas y orden de carga datos → MapLibre.

## Criterios de aceptación de la fase 4

| Criterio | Estado |
|---|---|
| Recorridos de escritorio y móvil | Cumplido: 18 recorridos × 2 proyectos. |
| Casos cero y sin datos | Cumplido: Agronomia 2019-10 = 0; 2026-01 y meses sin evaluación retrospectiva. |
| URL con filtros | Cumplido: atlas, simulador y perfiles con recarga y Atrás. |
| Comprobación de cifras | Cumplido: referencias independientes de Python para el panel y las selecciones. |
| Solo datos agregados, atribuciones y recursos públicos | Cumplido: `audit:dist` más la prueba de red de origen único. |
| Compilación revisable | Cumplido en local (`astro preview`). La vista previa remota (Cloudflare Pages u otra) requiere cuenta y autorización: queda para la fase 5. |

## Limitaciones

- La revisión automática con axe cubre solo una parte de WCAG. No reemplaza una prueba con lectores de pantalla reales.
- Las pruebas usan solo Chromium; no se verificó en Safari/iOS ni en Firefox.
- Los presupuestos de tamaño son límites del proyecto, no mediciones de rendimiento en redes reales.
- La compresión gzip depende del alojamiento.
