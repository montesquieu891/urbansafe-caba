# Simulador y perfiles web — fase 3

Implementación local de la fase 3, 2026-11-10. Se conserva el paquete público v1 sin cambios (`export_web_data.py --check` aprobado). No hay despliegue. Autoauditoría de implementación: la implementación comenzó en Codex y se completó y revisó en Claude Code; no se entrenaron ni reevaluaron modelos científicos.

## Ejecutar y verificar

Desde la raíz, con Node.js y el entorno Python del proyecto:

```powershell
python scripts/generate_web_test_references.py   # regenera web/tests/fixtures/simulation.json
python scripts/export_web_data.py --check
npm --prefix web run check
npm --prefix web run build
npm --prefix web run test:e2e
```

Vista local: `npm --prefix web run dev -- --port 4322` y abrir `http://127.0.0.1:4322/?vista=simulador`. Capturas: con ese servidor activo, desde `web`, `node tests/capture-preview.mjs phase3`.

## Qué se implementó

- **Vistas** `atlas`, `simulador` y `perfiles` sobre el mismo estado (mes, barrio, métrica, estrategia, K, nivel). La URL conserva `vista`, `estrategia`, `k` y `nivel`; recarga y Atrás los restauran. Valores inválidos vuelven a clasificador, K=10 y nivel 2.
- **Simulador 2025.** Estrategias: clasificador, regresión, historial de 12 meses, último mes observado y oráculo retrospectivo; K = 5, 10 o 15. En el simulador el selector de mes se rotula **«Mes objetivo»** y el corte muestra «Información hasta [mes observable] → mes objetivo · horizonte 1 mes · gap 0», con la aclaración de que es un supuesto retrospectivo. Fuera de 2025 se informa «Sin evaluación retrospectiva» y se ocultan resultados.
- **Selecciones y empates.** El frontend no resuelve empates: consume las selecciones exportadas (regla del Paso 10, semilla 20261111) y, al cargar, verifica para las 180 combinaciones mes × K × estrategia que haya exactamente K barrios y que hechos cubiertos, denominador, cobertura e ids coincidan con `cobertura.json`. Si no reconcilian, la página falla con error visible en lugar de mostrar cifras.
- **Comparación.** Cada mes muestra la cobertura de la estrategia y del historial con su denominador (hechos cubiertos / hechos del mes), barrios compartidos y exclusivos. Mapa: relleno por categoría (ambas, solo estrategia, solo historial, fuera), contorno azul continuo de la estrategia y ocre punteado del historial; la lista repite la categoría como texto. Anual: **media de coberturas mensuales** (mismo peso por mes), diferencia en puntos porcentuales e IC 95 % por bloques publicado. El texto distingue tres casos: IC que incluye cero (sin mejora concluyente), IC enteramente negativo y enteramente positivo.
- **Referencias.** Azar esperado K/48 y oráculo como referencia retrospectiva con conocimiento del resultado. El 92 % se presenta como fracción de la ganancia sobre el azar para K=10, aclarando que no es el porcentaje de hechos cubiertos. El puntaje del clasificador se describe como probabilidad estimada de pertenecer al top-10, no de sufrir un siniestro.
- **Reproducción mensual** con anterior/siguiente, reproducir/pausar; se detiene al cambiar de vista, mes, estrategia, K, al ocultar la pestaña o navegar.
- **Perfiles.** K=2 principal (interior / borde) y K=3 exploratorio anidado (interior residencial, interior central-denso, borde), con la advertencia de separación débil (silhouette 0,195, de `reports/tables/05_clustering/comparacion_metodos.csv`). Los conteos del resumen se calculan desde `perfiles.json`, y la carga verifica que el borde de K=3 coincida con el de K=2.

## Evidencia de aceptación

| Criterio del plan (fase 3) | Evidencia |
|---|---|
| K = 5, 10 o 15 | E2E recorre los tres K en los 12 meses. |
| Selecciones mensuales con la regla de desempate del proyecto | `web/tests/fixtures/simulation.json`: 180 referencias generadas con `src.labels.top_k_labels` directamente desde las predicciones congeladas (no desde el paquete web), 36 con empate en el corte. Regenerado en esta sesión: byte a byte idéntico. E2E compara ids seleccionados por clasificador e historial en 36 meses×K y las demás estrategias en enero con K=10. |
| K=10: 42,73 % historial y 43,05 % clasificador | E2E: `#annual-baseline` = «42,73 %», `#annual-strategy` = «43,05 %». |
| Intervalo de la diferencia | E2E: IC −0,07 a +0,80 pp, «incluye cero» (K=10); para K=15 el IC del clasificador queda bajo cero y la interfaz lo dice. |
| Oráculo etiquetado como referencia retrospectiva | E2E: «No es un pronóstico utilizable al corte». |
| Perfiles | E2E: 39/9 con K=2; 22/17/9 con K=3; advertencia de separación débil; persistencia en URL; teclado y móvil sin desborde horizontal. |

Resultados: `astro check` sin errores ni advertencias; `astro build` correcto (persiste la advertencia de tamaño del bundle de MapLibre, pendiente para la fase 4); **Playwright 20/20 aprobadas** (10 recorridos × escritorio y móvil emulado Chromium); `pytest` 19 aprobadas (exportador, etiquetas y evaluación). Capturas: [simulador escritorio](evidence/web_phase3/simulator-desktop.png), [simulador móvil](evidence/web_phase3/simulator-mobile.png), [perfiles escritorio](evidence/web_phase3/profiles-desktop.png), [perfiles móvil](evidence/web_phase3/profiles-mobile.png).

## Correcciones de la revisión

- Formato porcentual: Chromium con ICU actual produce «43,05%» sin espacio; la interfaz y la prueba usan ahora un formato fijo «43,05 %» independiente de ICU.
- El import del fixture JSON en Playwright requería `with {type:'json'}`.
- Mes objetivo: el selector decía «Mes observado» también en el simulador; ahora distingue mes objetivo de mes observable.
- IC K=15 del clasificador (−0,84 a −0,15 pp) se mostraba sin interpretación; ahora se indica cobertura inferior al historial.
- Resumen de perfiles calculado desde los datos en lugar de cifras fijas.

## Limitaciones

Una sola temporada de prueba (2025), datos de 2025 posiblemente provisorios y disponibilidad operativa al cierre de cada mes no acreditada. La cobertura mide concentración registrada, no siniestros evitados ni riesgo ajustado por exposición. Las pruebas usan Chromium (escritorio y móvil emulado); no equivalen a Safari/iOS físico. Las claves de `inputs` del fixture usan separador de rutas de Windows; no afecta las pruebas.

## Revisión pedagógica posterior

Se revisaron el propósito de ambas vistas, la secuencia de lectura, las definiciones en contexto y la separación entre perfil histórico y conteo mensual. Ver [web_pedagogy_review.md](web_pedagogy_review.md). Cambios locales, sin nueva publicación en esta revisión.
