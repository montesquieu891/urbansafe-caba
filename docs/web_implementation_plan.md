# UrbanSafe CABA · Plan de implementación web

## Objetivo y alcance

Construir un atlas para explorar la carga registrada de siniestros con víctimas en CABA y un simulador para comparar estrategias de priorización barrial. La primera versión está pensada para la presentación académica y para lectores que quieran reproducir las decisiones con datos públicos agregados.

El atlas cubre 2019–2025. El simulador usa pronósticos retrospectivos de 2025 con horizonte de un mes y gap = 0. La vista de perfiles distingue el agrupamiento de dos grupos y la subdivisión exploratoria del interior. La extensión AUSA 2026 se evalúa por separado tras el MVP.

## Arquitectura propuesta

- **Python** prepara un paquete público a partir del panel procesado, las geometrías, las predicciones congeladas y las tablas auditadas. Un exportador reproducible valida las uniones y genera un manifiesto.
- **Astro y TypeScript** construyen el sitio estático. **MapLibre** dibuja el mapa de barrios con GeoJSON local. El simulador carga los datos necesarios y actualiza la vista en el navegador.
- **Playwright** verifica recorridos, cifras y navegación con la compilación local. **Cloudflare Pages** queda como opción de alojamiento para una vista previa y una publicación autorizada.
- Rutas propuestas en el repositorio: `web/` para el sitio, `scripts/export_web_data.py` para la exportación, y `web/tests/e2e/` para las pruebas de navegador.

## Fases y criterios de aceptación

| Fase | Entregable | Criterio de aceptación |
|---|---|---|
| 0. Alcance y copy | Inventario de artefactos, recorridos y textos de la interfaz | El 92 % se presenta como fracción de la ganancia sobre el azar para K = 10. Se distingue observación histórica, pronóstico retrospectivo y resultado posterior. |
| 1. Datos públicos | Exportador, contrato y paquete de datos versionado | Se conservan 48 barrios y 4.032 claves barrio-mes del panel. Se validan las 576 filas de evaluación de 2025 y la correspondencia uno a uno de las geometrías. |
| 2. Atlas | Mapa, búsqueda, selector de mes y ficha con serie | Mapa, ficha y lista responden al mismo estado. Conteo y densidad tienen unidades y leyendas distintas. Se puede explorar con teclado y en móvil. |
| 3. Simulador y perfiles | Reproducción mensual, comparación de estrategias y mapa de perfiles | K = 5, 10 o 15. Las selecciones mensuales coinciden con la regla de desempate del proyecto. Para K = 10, la media mensual de cobertura en 2025 es 42,73 % para el historial y 43,05 % para el clasificador. Se muestra el intervalo de la diferencia y se etiqueta el oráculo como referencia retrospectiva. |
| 4. QA y vista previa | Pruebas E2E y compilación revisable | Pasan los recorridos de escritorio y móvil, los casos cero y sin datos, las URL con filtros y la comprobación de cifras. La salida contiene solo datos agregados, atribuciones y recursos públicos. |
| 5. Publicación | Versión estática con manifiesto y registro de release | Con autorización expresa, publicar la versión revisada. Verificar la URL, el manifiesto, las rutas y el procedimiento de reversión. |

## Contrato de datos del MVP

| Archivo propuesto | Grano y campos esenciales | Insumo |
|---|---|---|
| `barrios.geojson` | Un objeto por `id_barrio`. Nombre, comuna y geometría. | `data/raw/limites/barrios.geojson` y diccionario de claves del panel |
| `panel-mensual.json` | `id_barrio` × mes. Hechos, superficie y composición registrada por modo, con estado de disponibilidad. | `data/processed/panel_barrio_mes.csv` |
| `priorizacion-2025.json` | Mes objetivo, mes observable, horizonte, gap, puntajes o selecciones por estrategia, y hechos observados agregados. | Predicciones congeladas de regresión y clasificación |
| `cobertura.json` | Estrategia × K × período, cobertura e intervalos disponibles. | Tablas del Paso 10 |
| `perfiles.json` | `id_barrio`, grupo principal y subdivisión exploratoria. | Tabla de asignaciones del Paso 09 |
| `manifest.json` | Versión del esquema y de los datos, fecha de corte, fuentes, licencias, hashes y definiciones. | Registro de fuentes y exportador |

La cobertura anual del simulador es la media de las coberturas mensuales, con el mismo peso por mes. El detalle mensual muestra el denominador de la cobertura. Las reglas de desempate y los cortes temporales se calculan con los módulos de Python o se exportan ya resueltos.

## Orden de trabajo

Primero, cerrar el contrato y las pruebas de reconciliación. Después, construir una sección vertical del atlas con un barrio y un mes reales, y completar el simulador sobre el mismo estado. Finalmente, añadir perfiles, atribución, accesibilidad y la vista previa. La primera revisión de producto debe poder recorrer el flujo **mes → barrio → estrategia → resultado observado**.

AUSA 2026 queda como fase posterior. Primero se comprueba el último mes completo y se compara con los mismos meses históricos. Cualquier indicador por volumen requiere correspondencia verificable de tramo, sentido y período.

## Skills del proyecto

- [web-data-export](../.agents/skills/web-data-export/SKILL.md)
- [interactive-map-ux](../.agents/skills/interactive-map-ux/SKILL.md)
- [dashboard-e2e](../.agents/skills/dashboard-e2e/SKILL.md)
- [static-web-release](../.agents/skills/static-web-release/SKILL.md)

## Estado de ejecución — fases 0 a 3

- [x] Fase 0: inventario, diferencias de contrato, recorridos y textos documentados en [web_data_contract.md](web_data_contract.md), incluido el significado del 92 %.
- [x] Fase 1: `scripts/export_web_data.py`, paquete público `web/public/data/v1/` y manifiesto con reconciliación de 48 barrios, 4.032 claves y 576 filas de evaluación. Evidencia y comandos en [web_data_contract.md](web_data_contract.md).
- [x] Fase 2: atlas Astro/TypeScript/MapLibre, filtros y ficha sincronizados, navegación accesible y móvil. Evidencia: [web_atlas_validation.md](web_atlas_validation.md).
- [x] Fase 3: simulador 2025 (cinco estrategias, K = 5/10/15, reproducción mensual, IC de la diferencia, oráculo como referencia retrospectiva) y perfiles K=2/K=3 sobre el estado compartido. Evidencia: [web_simulator_validation.md](web_simulator_validation.md).
- [ ] Fases 4–5: QA integral, vista previa de release y publicación. AUSA 2026 sigue fuera del MVP.
