# Atlas web — fase 2

Implementación local de la fase 2, 2026-11-10. Se conserva el paquete público v1 sin modificaciones. El simulador y los perfiles interactivos corresponden a la fase 3; no hay despliegue.

## Ejecutar

Desde la raíz, con Node.js y npm disponibles:

```powershell
npm --prefix web ci
npm --prefix web run dev -- --port 4322
```

Abrir `http://127.0.0.1:4322/`. Para validar la compilación estática:

```powershell
npm --prefix web run check
npm --prefix web run build
npm --prefix web exec -- playwright install chromium
npm --prefix web run test:e2e
```

Las pruebas levantan y cierran su propio servidor de la compilación en 4321. El servidor de desarrollo usa 4322. `package-lock.json` fija dependencias. Referencias técnicas consultadas: [Astro](https://docs.astro.build/install-and-setup/) y [capas GeoJSON de MapLibre](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-geojson-polygon/).

## Implementación y decisiones

- Astro estático, TypeScript y MapLibre. GeoJSON y panel locales; no se solicitan teselas, tipografías ni estilos de terceros. Worker de MapLibre empaquetado explícitamente mediante Vite.
- Mes, barrio, métrica y búsqueda comparten estado. URL con `mes`, `barrio`, `metrica` y `buscar`; recarga y botón Atrás restauran filtros. Los parámetros inválidos vuelven a diciembre de 2025, Palermo y conteo. Una fecha válida fuera de cobertura conserva el período y presenta ausencia.
- Mapa, ficha, lista, serie y leyenda muestran el mismo corte. Clic en polígono o botón de barrio actualiza la selección. La búsqueda ignora acentos, conserva los nombres originales y no cambia el barrio elegido hasta seleccionarlo.
- Escalas cartográficas fijas entre meses: conteo con cortes 10/25/50/75 hechos; densidad con cortes 5/10/20/30 hechos por km². Son intervalos de visualización, no umbrales de riesgo. Cero blanco, ausencia gris, positivos verdes y contorno oscuro para selección.
- Serie de 84 meses con tabla accesible equivalente. La escala vertical de la serie se ajusta al barrio y métrica; el mapa conserva los cortes fijos. Los modos son conteos por hecho, incluyen SD y no representan todas las víctimas individuales.
- Lista de 48 botones accesibles, foco visible y conservado después de seleccionar, filtros etiquetados, enlace para saltar al contenido, estados anunciados y diseño móvil. El mapa tiene alternativa de lista ante falta de WebGL. Sin JavaScript se ofrecen enlaces a los datos.
- Fuentes, licencias, fecha de corte, versión y limitaciones visibles. Se distingue carga registrada de riesgo por exposición.

## Evidencia de aceptación

- `astro check`: sin errores, advertencias ni sugerencias.
- `astro build`: compilación estática correcta. Advertencia de tamaño de bundle de MapLibre (>500 kB); optimización pendiente para la fase 4, sin bloquear funcionalidad local.
- Playwright: **12 pruebas aprobadas**, seis recorridos en escritorio y en móvil emulado Chromium. No equivale a validación en Safari/iOS físico.
- Se comprueba que se dibujen los **48 barrios**, no solo que se inicialice el mapa. Se verifica clic en polígono, selección por teclado, foco, búsqueda, mes, métrica, URL, recarga, historial Atrás, tabla de 84 valores, error HTTP y ausencia de desbordamiento horizontal.
- Referencias independientes del frontend, obtenidas del panel CSV con pandas: Palermo diciembre 2025 = 68; enero 2025 = 63 y superficie 15,9216 km²; Agronomia octubre 2019 = 0, incluidos los siete modos. Enero de 2026 se prueba como período ausente sin generar datos de ese año.
- `python scripts/export_web_data.py --check`: paquete original idéntico, validación aprobada.
- Revisión visual de escritorio y móvil. Capturas: [escritorio](evidence/web_phase2/desktop.png), [móvil](evidence/web_phase2/mobile.png). Regeneración con servidor 4322 activo: desde `web`, `node tests/capture-preview.mjs`.

La revisión visual inicial detectó un worker que no cargaba y dejaba el mapa vacío pese a inicializar controles. Se corrigió el empaquetado y se añadió el control de polígonos renderizados y clic real. Esta es una autoauditoría de implementación; no se entrenaron ni revisaron de nuevo los modelos científicos.
