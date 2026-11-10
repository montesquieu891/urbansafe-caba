# Paquete público de UrbanSafe CABA — fases web 0 y 1

Estado: **validado**, 2026-11-10. Autoauditoría del exportador y reconciliación con artefactos existentes; no constituye una nueva revisión ni entrenamiento de modelos. Alcance terminado en datos públicos. Interfaz, AUSA 2026 y despliegue pendientes.

## Reproducción

Desde la raíz del repositorio, con el entorno del proyecto activado:

```powershell
python scripts/export_web_data.py
python scripts/export_web_data.py --check
python -m pytest -q tests/test_web_data_export.py tests/test_labels.py tests/test_evaluation_regression.py
```

En esta máquina se utilizó `C:/Users/Usuario/.venvs/urbansafe/Scripts/python.exe`. El Python predeterminado no tiene Shapely. Se requieren pandas, NumPy y Shapely, ya incluidos en `requirements.txt`. No se necesitan red, microdatos, modelos serializados ni ejecución de notebooks. Los insumos procesados ignorados por Git deben estar disponibles como indica el README.

La salida predeterminada es `web/public/data/v1/`. `--output RUTA` permite una salida alternativa; se rechazan directorios con archivos ajenos y las rutas de investigación del repositorio. Toda reconciliación ocurre antes de escribir. `--check` reconstruye en memoria y compara los seis archivos byte a byte; falla si el paquete fue alterado o quedó desactualizado. Ante cualquier error no debe consumirse un paquete anterior como validación de insumos nuevos. El manifiesto se escribe al final y sus hashes permiten detectar archivos incompletos tras una interrupción de E/S.

El manifiesto identifica el esquema `1.0.0` y una versión de datos derivada de los hashes de insumos, código y documentación metodológica. Con iguales insumos y entorno la salida es determinista; no incluye una hora variable de ejecución. `fecha_corte=2025-12-31` corresponde a observaciones; la extracción de fuentes fue el 2026-11-10. No confundirlas con el mes observable de cada pronóstico.

## Inventario y diferencias respecto del contrato propuesto

| Uso | Insumo existente | Correspondencia y decisión |
|---|---|---|
| Atlas | `data/processed/panel_barrio_mes.csv` | Clave `id_barrio, mes`; 4.032 filas. `y_hechos` pasa a `hechos.valor`. `area_km2` se conserva; densidad derivada = hechos/superficie. |
| Geometrías | `data/raw/limites/barrios.geojson` | `properties.id` pasa a `id_barrio`. Se verifican nombre exacto y comuna contra el diccionario único del panel; 48 relaciones uno a uno. CRS84, geometrías completas sin simplificación. |
| Historial y regresión | `reports/tables/03_regression/predicciones_test.csv` y `seleccion_congelada.json` del mismo directorio | Clave original `barrio, mes_objetivo`. Nombre exacto → id del panel. Puntajes `y_ma12`, `y_lag1` y columna Poisson indicada en la selección congelada. |
| Clasificador | `reports/tables/04_classification/predicciones_test.csv` y `seleccion_congelada.json` | Misma clave original; se usa la columna logística seleccionada. Las otras configuraciones no se exportan. Se reconcilian objetivo e historial de ambos archivos. |
| Perfiles | `reports/tables/05_clustering/asignacion_barrios.csv` | Clave original `barrio` → id. Se conservan `grupo`, `k3`, `perfil_k3`; no se inventa una nueva clasificación. |
| Cobertura | `reports/tables/06_integrated_evaluation/cobertura_topk.csv` | Se reconcilian las 18 cifras TEST2025. El detalle mensual y las selecciones se calculan desde puntajes congelados, porque no están en esta tabla. |
| Incertidumbre | `reports/tables/06_integrated_evaluation/cobertura_diferencias_vs_historial.csv` | Se conservan diferencias e intervalos disponibles. Se reproducen seis medias e IC por bloques. Los percentiles de sensibilidad al desempate se trasladan de la tabla auditada y se distinguen del IC temporal. |
| Atribución | `docs/source_register.csv` | Se incluyen F01 (hechos), F03 (metodología) y F04 (barrios), licencias textuales, responsables, URLs, extracción y hashes originales registrados. |

No hay divergencias de nombres ni claves sin correspondencia. Los nombres se mantienen tal como aparecen en las fuentes (por ejemplo, `Agronomia`); no se normalizan acentos para unir. Se rechazan nombres desconocidos, duplicados y pérdidas de filas.

Los archivos de predicciones no incluyen mes observable, horizonte ni gap. Se explicitan conforme al protocolo h=1/gap=0: mes observable = mes objetivo − 1. Se comprueba además que persistencia y media de doce meses coincidan con el panel previo. Esto describe un supuesto retrospectivo; no acredita que el organismo publicara los datos al cierre de cada mes.

El contrato propuesto no especificaba el esquema interno de disponibilidad. V1 usa `{valor: entero, estado: "observado"}` y `{valor: null, estado: "sin_datos"}`. Hay 45 ceros observados y ningún faltante de hechos en las 4.032 celdas actuales. No se crean filas ficticias ausentes ni se imputan faltantes; un faltante nuevo en este panel completo interrumpe la exportación. Fuera del período del paquete, la interfaz deberá mostrar sin datos, nunca cero. `composicion_modo.sd` cuenta hechos con modo no informado y no indica una celda temporal ausente.

## Contrato público v1

Los JSON de panel, priorización y perfiles son listas de registros. GeoJSON es una FeatureCollection. Todos los id son enteros oficiales; meses son cadenas `AAAA-MM`; proporciones están en escala 0–1.

| Archivo | Clave / contenido |
|---|---|
| `barrios.geojson` | 48 features: `id=id_barrio`, propiedades `id_barrio,nombre,comuna`, geometría poligonal CRS84. |
| `panel-mensual.json` | 4.032 claves `id_barrio,mes`: `hechos`, `area_km2`, `hechos_por_km2`, `composicion_modo` (auto, bicicleta, moto, otros, peaton, sd, transporte_publico), `anomalia_mes`. Los modos suman hechos. |
| `priorizacion-2025.json` | 576 claves `id_barrio,mes_objetivo`: `mes_observable,horizonte_meses,gap_meses`; `puntajes` de historial_media12, historial_persistencia, regresion y clasificador; `resultado_posterior` con hechos y puntaje_oraculo; `selecciones[estrategia][K]` booleanas, K como cadena 5/10/15. |
| `cobertura.json` | `mensual`: estrategia×K×mes, hechos cubiertos, denominador, cobertura e ids seleccionados. `anual`: media mensual y cobertura agregada por separado. `diferencias_vs_historial`: IC y sensibilidad existentes, siempre diferencias contra media12. `fraccion_ganancia_sobre_azar_K10` e información del bootstrap. |
| `perfiles.json` | 48 ids: `grupo` (0 interior, 1 borde), `k3` (0 residencial, 1 borde, 2 central-denso), `perfil_k3`. K=2 es principal; K=3 es exploratorio y anidado. |
| `manifest.json` | Esquema, versión de datos, corte, fuentes, licencias, hashes SHA-256 de cada insumo y de los cinco archivos de datos, tamaños, modelos seleccionados, regla de desempate, definiciones, límites, entorno y resultados de validación. No contiene hash de sí mismo. |

Los puntajes de historial y regresión representan conteos; el del clasificador es su probabilidad estimada de pertenecer al top-10, usada también para ordenar K=5/15. No debe presentarse como probabilidad de sufrir un siniestro. El oráculo usa hechos observados posteriores y aparece separado de los puntajes predictivos. El azar esperado es K/48, no una selección simulada particular; se exporta como referencia anual, válida para cada mes.

Desempate de selecciones: `src.labels.top_k_labels`, R0, semilla **20261111**, nombres ordenados, generador NumPy con `[semilla, ordinal mensual]`. Se conserva la regla del Paso 10, no orden por id ni nombre como desempate final. La etiqueta objetivo congelada `top10_target` usa semilla **20261110**; se verifica pero no se confunde con la semilla de selección de estrategias.

## Fase 0: recorridos y textos acordados para la futura interfaz

Recorrido principal: mes → barrio → estrategia → resultado observado.

1. Atlas: elegir mes de 2019–2025, localizar barrio y consultar conteo, densidad y composición. Textos: **«Hechos registrados con víctimas»**, **«Hechos por km²»**, **«Cero hechos registrados»**, **«Sin datos para este período»**. Conteo y densidad son carga registrada; ninguno mide riesgo ajustado por exposición.
2. Simulador: elegir mes objetivo de 2025 y K; mostrar **«Información hasta [mes observable]»**, **«Pronóstico retrospectivo a un mes · gap 0»**, estrategia y selección. Al revelar el resultado: **«Hechos observados posteriormente»**, hechos cubiertos/total mensual y **«Media de coberturas mensuales de 2025»**.
3. Comparación: **«Historial de 12 meses: 42,73 %»**, **«Clasificador: 43,05 %»** para K=10. Diferencia +0,32 puntos porcentuales, IC95 % por bloques aproximadamente −0,07 a +0,80 puntos; no afirmar mejora concluyente. **«Oráculo: referencia retrospectiva con conocimiento del resultado»**.
4. Mensaje del 92 %: **«Para K=10, el historial recupera aproximadamente el 92 % de la ganancia sobre el azar alcanzable por el oráculo retrospectivo»**. Fórmula `(cobertura_historial − 10/48)/(cobertura_oraculo − 10/48)`. No significa 92 % de hechos cubiertos ni 92 % de exactitud.
5. Perfiles: **«Dos grupos principales: interior y borde»** y **«Subdivisión exploratoria del interior: separación débil»**. Atributos históricos de desarrollo 2019–2024 sin meses anómalos; no describirlos como clusters entrenados con 2025.

## Evidencia y límites

Se verificaron 48 barrios y geometrías válidas, 84 meses completos, 4.032 claves únicas y 576 filas de evaluación; correspondencias uno a uno; composición por modo; objetivos congelados contra observaciones; historial contra meses anteriores; 180 selecciones de K exacto (cinco estrategias × tres K × doce meses), incluidas 36 situaciones con empate al corte, e invariancia al reordenar filas. Las coberturas se contrastan con `src.evaluation.topk_coverage` y con las 18 referencias del Paso 10; seis IC por bloques se reproducen.

Para K=10, medias de las coberturas mensuales:

- Historial de doce meses: **0,42734630326215245 = 42,7346303262 %**.
- Clasificador: **0,43054248057869504 = 43,0542480579 %**.

El paquete también conserva cobertura agregada anual para evitar confundir ambos cálculos. Las pruebas comprueban determinismo, hashes, campos públicos permitidos, cero/ausente y rechazo de panel duplicado o incompleto, nombre desconocido, geometría duplicada, objetivo alterado, cobertura alterada y observación faltante.

No quedan discrepancias numéricas o de claves pendientes. Se mantienen las limitaciones de origen: CC-BY de hechos sin versión indicada, 2025 posiblemente provisorio, límites vigentes sin historial verificado y exclusión del panel de hechos que no pudieron asignarse a un barrio. Las licencias se trasladan del registro auditado; no se atribuye una versión de CC-BY que la fuente no declara. No se reentrenaron modelos, no se alteraron artefactos originales y no se incluyen registros individuales.

### Registro de ejecución

Versión generada: `2019-2025-5685c2f9c0a0`. Entorno: numpy 2.5.4, pandas 3.1.1, python 3.13.7.

Resultado: **19 pruebas aprobadas** (exportador, etiquetas y evaluación); `--check` aprobado con igualdad byte a byte de los seis archivos. Verificación ejecutada el 2026-11-10.
