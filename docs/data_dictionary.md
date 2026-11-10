# UrbanSafe CABA — Diccionario de datos procesados

**Hito:** Paso 04  
**Generador:** [`src/data_processing.py`](../src/data_processing.py) (`python -m src.data_processing`)  
**Directorio:** `data/processed/` (no versionado; se reconstruye desde las fuentes)  
**Control:** [qa_report.json](evidence/paso04/qa_report.json) y [processed_sha256.txt](evidence/paso04/processed_sha256.txt)

Todos los archivos son CSV UTF-8 con separador `,`. Las fechas tienen formato `AAAA-MM-DD` y los meses, `AAAA-MM`. Los valores booleanos se escriben `True` o `False`, y los faltantes quedan como celda vacía.

## Esquema

| Archivo | Unidad (clave) | Filas | Uso |
|---|---|---|---|
| `hechos_clean.csv` | Hecho (`id_siniestro`) | 65.818 | Tabla limpia y completa. No se elimina ningún hecho. |
| `victimas_clean.csv` | Víctima (`id_victima_etl`) | 75.197 | Relación N:1 con los hechos mediante `id_siniestro` |
| `panel_barrio_mes.csv` | Barrio × mes (`barrio`, `mes`) | 4.032 = 48 × 84 | **Panel principal** (D1, D2) |
| `panel_comuna_mes.csv` | Comuna × mes (`comuna`, `mes`) | 1.260 = 15 × 84 | Panel de robustez |
| `registro_exclusiones.csv` | Registro excluido de un panel | 3.035 | Trazabilidad de las exclusiones |
| `qa_report.json` | — | — | Hashes de las fuentes, conteos y conciliaciones |

Las decisiones referidas como D1–D11 están en el [informe de viabilidad](feasibility_report.md).

## `hechos_clean.csv`

| Columna | Tipo | Descripción | Origen y regla |
|---|---|---|---|
| `id_siniestro` | texto | Identificador original del hecho; único | F01, sin cambios |
| `tipo_sumario` | categoría | `lesiones` (prefijo LC) u `homicidio` (prefijo HC) | Derivado del prefijo; `homicidio` equivale a gravedad MORTAL |
| `fecha` | fecha | Fecha del hecho | `fecha_siniestro`, parseada con formato mixto (9.406 sin ceros a la izquierda en la fuente) |
| `hora` | texto `HH:MM:SS` | Hora del hecho | `hora_siniestro`; vacía si no es parseable |
| `hora_entera` | entero 0–23 | Hora redondeada hacia abajo | Derivada de `hora` |
| `mes`, `anio` | texto, entero | Período del hecho | Derivados de `fecha` |
| `dia_semana` | entero 0–6 | 0 = lunes | Derivado de `fecha` |
| `n_leves`, `n_graves`, `n_mortales` | entero | Víctimas del hecho por gravedad | F01; completos |
| `n_victimas` | entero | Suma de las tres anteriores | Coincide con las filas de víctimas (100 %). Reemplaza a `numero_total_de_victimas`, que tiene 28 % de SD en 2025. |
| `gravedad` | categoría | LEVE, GRAVE o MORTAL: la máxima de sus víctimas | F01 en mayúsculas. Grave = hospitalización de al menos 24 h; mortal = hasta 30 días (F03) |
| `ksi` | booleano | Grave o mortal | Derivado |
| `tipo_de_via` | categoría | AVENIDA, CALLE, AV. GRAL. PAZ, AUTOPISTA o SD | **SD incluye vacíos**: 95 % en 2019, por lo que no es comparable entre años (C5) |
| `modo_victima` | categoría | Modo de desplazamiento de la víctima, informado a nivel de hecho | Mayúsculas. Vacíos y errores de planilla (`#¡REF!`) pasan a SD. No se recodifican categorías semánticas. |
| `contraparte` | categoría | Vehículo de la contraparte | Igual que el anterior. Se conserva `CAMIONETA` tal como figura en la fuente. |
| `participantes` | categoría | Combinación víctima-contraparte | Igual que el anterior |
| `direccion_normalizada` | texto | Dirección normalizada de la fuente | F01, sin cambios (21 % vacía) |
| `comuna_fuente` | entero 1–15 | Comuna informada por la fuente | 34 variantes normalizadas; SD o vacío pasan a faltante |
| `lat`, `lon` | real (WGS84) | Coordenadas del hecho | Faltantes si no son numéricas o están fuera del rango regional. 3.031 faltantes. |
| `x_plana`, `y_plana` | real (m) | Coordenada plana de la fuente (Gauss-Krüger BA, Campo Inchauspe) | Parseada de `geocodificacion_plana`. Los valores mal formados o con otra escala quedan faltantes. |
| `anomalia_mes` | categoría | `registro` (2019-11 y 2019-12), `pandemia` (2020-03 a 2021-05) o `ninguna` | D3: se marca, no se elimina |
| `particion` | categoría | `desarrollo` (2019–2024) o `test` (2025, provisorio) | D3; la partición definitiva se fija en el Paso 06 |
| `dup_grupo`, `posible_duplicado` | entero, booleano | Grupo de hechos con igual fecha, hora y lugar (alrededor de 1 m) | D10: 274 hechos en 134 grupos; se conservan |
| `barrio` | texto | Barrio asignado | D9: `within`; si no, el barrio más cercano a 200 m o menos |
| `comuna_geo` | entero | Comuna del barrio asignado | Capa oficial F04 |
| `metodo_asignacion` | categoría | `within`, `nearest_200m` o `sin_coordenada` | D9 |
| `comuna` | entero | Comuna final: `comuna_geo` o, si no hay coordenada, `comuna_fuente` | D9 |
| `comuna_discordante` | booleano | `comuna_geo` ≠ `comuna_fuente` | Prevalece la geometría (2.329 casos, casi todos a menos de 100 m de un límite) |
| `dist_plana_m`, `discrepancia_plana` | real, booleano | Distancia entre lat/lon y la coordenada plana; marca si supera 500 m | Incertidumbre de geocodificación (472 casos) |
| `en_panel_barrio`, `en_panel_comuna` | booleano | El hecho entra en el panel correspondiente | Los que no entran figuran en el registro de exclusiones |

## `victimas_clean.csv`

| Columna | Tipo | Descripción | Origen y regla |
|---|---|---|---|
| `id_victima_etl` | entero | Identificador técnico secuencial | **Generado por el ETL**: la fuente no tiene identificador de víctima. Depende del orden de las filas en la fuente. |
| `id_siniestro` | texto | Hecho al que pertenece | F02. 4 filas sin id (se registran como exclusión). |
| `fecha` | fecha | Fecha del hecho | F02 |
| `modo_victima`, `sexo`, `rol` | categoría | Atributos de la víctima | Mayúsculas; vacíos pasan a SD. Faltantes: modo 31 %, sexo 23 % y rol 80 %. |
| `edad` | entero | Edad | Faltante si es SD (31 %) |
| `edad_fuera_de_rango` | booleano | Edad mayor que 105 | Marca para revisión; no se elimina |
| `gravedad` | categoría | LEVE, GRAVE o MORTAL | F02 en mayúsculas (unifica `mortal` y `MORTAL`) |
| `fecha_fallecimiento` | fecha | Fecha de fallecimiento | F02 |
| `fila_identica_en_fuente` | booleano | La fila es idéntica a otra de F02 | Pueden ser personas distintas; no se eliminan (D10) |
| `sin_id_hecho` | booleano | Falta `id_siniestro` | — |

## `panel_barrio_mes.csv` y `panel_comuna_mes.csv`

El panel es completo: todas las combinaciones de unidad y mes entre 2019-01 y 2025-12 están presentes, y un cero es un **cero observado**. Solo cuenta los hechos con `en_panel_<unidad>` verdadero.

| Columna | Tipo | Descripción |
|---|---|---|
| `barrio` o `comuna` | texto o entero | Unidad espacial |
| `mes` | texto `AAAA-MM` | Período |
| `y_hechos` | entero | **Objetivo principal de regresión** (D5): hechos con víctimas |
| `y_victimas` | entero | Víctimas (objetivo secundario) |
| `y_ksi`, `y_graves`, `y_mortales` | entero | Hechos graves o mortales y su desagregación. Solo descriptivos (D5). |
| `n_posible_duplicado` | entero | Hechos de la celda marcados como posibles duplicados |
| `hechos_modo_{auto, bicicleta, moto, peaton, transporte_publico, otros, sd}` | entero | Hechos por modo de la víctima. Suman `y_hechos`. `otros` agrupa TAXI, UTILITARIO, MOVIL, CAMION, MONOPATIN, OTRO y MIXTO. |
| `anio`, `mes_calendario` | entero | Componentes del período |
| `anomalia_mes` | categoría | Igual que en los hechos |
| `particion` | categoría | `desarrollo` o `test` |
| `id_barrio`, `comuna_barrio`, `area_km2` | entero, entero, real | Solo en el panel de barrio: id oficial, comuna y superficie (límites oficiales en el CRS plano) |
| `area_km2` | real | Solo en el panel de comuna: superficie de la comuna |

**Fuera del panel (D11).** No hay variables de infraestructura vial (callejero ni semáforos): se excluyen de la evaluación predictiva principal. Los objetivos desplazados (t+1) y las etiquetas top-K (regla R0) se construyen en el Paso 06.

## `registro_exclusiones.csv`

| Columna | Descripción |
|---|---|
| `tabla` | `hechos` o `victimas` |
| `id` | `id_siniestro` o `id_victima_etl` |
| `motivo` | Causa de la exclusión |
| `alcance` | Paneles o vínculos afectados |

| Motivo | n | Alcance |
|---|---|---|
| Sin coordenada válida ni comuna | 2.660 | Excluido de los paneles de barrio y de comuna; se conserva en `hechos_clean.csv` |
| Sin coordenada válida; comuna informada por la fuente | 371 | Excluido solo del panel de barrio |
| Fila de víctima sin `id_siniestro` | 4 | No vinculable a ningún hecho |
