# UrbanSafe CABA — Inventario de fuentes de datos

**Hito:** Paso 02. Trabajo de campo y relevamiento de fuentes  
**Estado:** borrador para revisión, no cerrado  
**Fecha de extracción:** 2026-11-10T14:41:42Z (UTC)  
**Entregables relacionados:** [registro de fuentes](source_register.csv), [registro de la consulta institucional](institutional_inquiry.md), [evidencia](evidence/paso02/) y [script reproducible](../scripts/paso02_relevamiento.py)

> **Alcance.** Este paso identifica las fuentes y documenta su estructura y sus restricciones. Los perfiles de este documento son **estructurales**: forma, campos, cobertura y faltantes globales. No sustituyen la auditoría de viabilidad del Paso 03 (escala, *zero inflation*, panel efectivo y cambios metodológicos), ni el ETL del Paso 04. Los archivos descargados no se incorporaron al repositorio; su organización en `data/raw/` corresponde al Paso 04.

---

## 1. Método del relevamiento

| Aspecto | Detalle |
|---|---|
| Portal | BA Data (`data.buenosaires.gob.ar`); metadatos por la API CKAN (`package_show`, `package_search`) y archivos desde el CDN oficial (`cdn.buenosaires.gob.ar`) |
| Búsquedas en el catálogo | `siniestro`, `homicidio`, `seguridad vial`, `transito`, `semaforo`, `ciclovia`, `velocidad`, `prioridad peaton`, `metrobus`, `red vial`, `conteo`. Algunas consultas posteriores (`accidente`, `fotomulta`, `intersecciones`, `obras`, `censo`) fueron rechazadas por el firewall del portal y quedan pendientes. |
| Criterio de inclusión | Fuente oficial con relación directa con la siniestralidad, la delimitación territorial, la infraestructura vial o la exposición en CABA |
| Verificación | Se descargaron 17 archivos. Para cada uno se registró el SHA-256 ([sha256.txt](evidence/paso02/sha256.txt)) y se perfiló la estructura ([perfil_estructural.txt](evidence/paso02/perfil_estructural.txt)). Los metadatos CKAN de 9 conjuntos se guardaron en [ckan_metadata/](evidence/paso02/ckan_metadata/). |
| Reproducción | `python scripts/paso02_relevamiento.py --out <dir_descarga>` descarga, calcula los hashes y regenera el perfil. Después, `python scripts/paso02_source_register.py` regenera el registro CSV. |
| Limitación de acceso | Tras unas 25 consultas a la API, el portal devolvió *Request Rejected* (WAF). Los metadatos de F16–F21 quedaron pendientes. El CDN no aplicó ese bloqueo. |

## 2. Resumen de fuentes

| ID | Fuente | Tratamiento (plan) | Período | Unidad | Estado |
|---|---|---|---|---|---|
| F01 | Siniestros viales: hechos | Obligatoria | 2019-01 a 2025-12 | Hecho con víctimas (punto) | Verificada |
| F02 | Siniestros viales: víctimas | Obligatoria | 2019–2025 | Víctima | Verificada |
| F03 | Notas metodológicas 2019–2025 (OMSV) | Obligatoria (metodología) | — | Documento | Leída |
| F04 | Barrios | Obligatoria | Vigente | Polígono (48) | Verificada |
| F05 | Comunas | Obligatoria | Vigente | Polígono (15) | Verificada |
| F06 | Calles (callejero) | Prioritaria | Estado a 2026-11 | Tramo (31.961) | Verificada |
| F07 | Volumen vehicular 2024: base anual | Enriquecimiento | 2024 (52 miércoles) | Sensor × día | Verificada |
| F08 | Volumen vehicular 2024: detalle semanal | Complementaria | 1 semana de marzo de 2024 | Sensor × 15 min × clase | Verificada (estructura) |
| F09 | Ubicación de sensores y diccionario | Enriquecimiento | 2024 | Sensor (95) | Verificada |
| F10 | Conteos peatonales | Complementaria | 2017–2019, fechas puntuales | Intersección (60) | Verificada |
| F11 | Conteo vehicular en cruces | Complementaria | 2018–2019, fechas puntuales | Cruce × hora (257) | Verificada |
| F12 | Sensores de tránsito (inventario) | Complementaria | Instalados 2011–2016 | Sensor (52) | Verificada |
| F13 | Cruces semaforizados | Prioritaria (infraestructura) | Estado vigente | Cruce (3.940) | Verificada |
| F14 | Informes estadísticos del OMSV | Investigación directa | — | Agregado | Identificada |
| F15 | Delitos (Ministerio de Seguridad) | Complementaria | — | Hecho delictivo | Identificada |
| F16–F21 | Ciclovías, prioridad peatonal, cámaras, factores de riesgo, AUSA, semáforos/Metrobus/radares | Candidatas | — | — | Identificadas; metadatos pendientes |
| F22 | Población por barrio (Censo 2010) | Complementaria | 2010 | Barrio | Identificada |

El detalle por campo de cada fuente está en [source_register.csv](source_register.csv): licencia, URL, identificadores, variables, faltantes, frecuencia de actualización, hash y limitaciones.

## 3. Fuentes obligatorias

### 3.1 F01–F03. Siniestros viales (OMSV)

**Origen y definición.** Las bases provienen de los sumarios de la Policía de la Ciudad por **lesiones culposas** y **homicidios culposos**. Desde el segundo cuatrimestre de 2018, esa es la fuente principal del Observatorio. El registro de víctimas mortales se completa con SAME, AUSA, hospitales, la Justicia y medios de comunicación (F03, pp. 1–2). Un *siniestro* es un hecho de tránsito con al menos un vehículo en movimiento y **al menos una persona herida o muerta**. Los hechos con solo daños materiales quedan excluidos (F03, p. 3). La gravedad de las víctimas se define así: *grave*, hospitalización de al menos 24 h; *mortal*, fallecimiento dentro de los 30 días; *leve*, el resto. Cada hecho toma la gravedad máxima de sus víctimas (F03, p. 8).

**Estructura verificada.**

| Elemento | F01 (hechos) | F02 (víctimas) |
|---|---|---|
| Filas | 65.818 | 75.197 |
| Clave | `id_siniestro`, única. Prefijo `LC` (65.129, lesiones) o `HC` (689, homicidio). | `id_siniestro`, clave foránea. No hay identificador de víctima. |
| Período | 2019-01-01 a 2025-12-31; las 84 fechas mensuales tienen registros | 2019–2025 |
| Ubicación | Latitud y longitud WGS84, punto en coordenadas planas, dirección normalizada, comuna y tipo de vía. **No incluye barrio.** | Solo a través de F01 |
| Gravedad | Hecho: 62.174 leves, 2.955 graves y 689 mortales | Víctima: 71.308 leves, 3.182 graves y 703 mortales |
| Actores | Participantes, modo de la víctima y contraparte | Modo, rol, sexo y edad |

**Conciliación hecho-víctima.** Las dos tablas son coherentes: no hay víctimas huérfanas ni hechos sin víctimas. Para cada hecho, la suma de víctimas leves, graves y mortales de F01 coincide con la cantidad de filas de F02 (100 %). Hay 1.439 filas idénticas en F02. Como no existe un identificador de víctima, pueden ser personas distintas con los mismos atributos. Se revisarán en el Paso 03.

**Hechos por año.**

| Año | Hechos | Graves | Mortales | Hechos con coordenada |
|---|---|---|---|---|
| 2019 | 10.155 | 373 | 103 | 94,8 % |
| 2020 | 6.061 | 143 | 79 | 96,7 % |
| 2021 | 7.818 | 358 | 96 | 93,4 % |
| 2022 | 9.536 | 522 | 107 | 95,8 % |
| 2023 | 9.927 | 356 | 104 | 97,1 % |
| 2024 | 10.569 | 516 | 110 | 95,7 % |
| 2025 | 11.752 | 687 | 90 | 94,4 % |

Los conteos mensuales completos están en [perfil_estructural.txt](evidence/paso02/perfil_estructural.txt). Hay **irregularidades a investigar en el Paso 03**, no a interpretar todavía:

- **Noviembre y diciembre de 2019:** caen a 555 y 542 hechos, frente a unos 900 en los meses previos. Puede tratarse de un cambio de registro.
- **2020 y mayo de 2021:** caídas compatibles con las restricciones de movilidad por la pandemia.
- **2025:** máximo de la serie. Puede ser un aumento real o un cambio de cobertura. Además, el dato podría ser provisorio.
- **Hechos graves:** su cantidad oscila mucho entre años (356 en 2023 y 687 en 2025). La gravedad depende del relevamiento hospitalario (F03, p. 2), que podría variar en el tiempo.

**Calidad y faltantes (F01).**

| Problema | Magnitud | Implicancia |
|---|---|---|
| Sin coordenada numérica | 3.031 hechos (4,6 %); **15,1 % de los graves**, 4,2 % de los leves y 0,4 % de los mortales | Faltante **no aleatorio por gravedad**: puede sesgar los análisis territoriales de gravedad |
| Sin comuna | 3.552 (5,4 %) | 2.660 hechos no tienen ni coordenada ni comuna y no pueden asignarse a ninguna zona |
| Etiquetas de comuna | 34 variantes (`Comuna 1`, `1`, `COMUNA 1`, `SD`, vacío) | Normalización en el ETL |
| Barrio | No existe en la fuente | Se asignará por unión espacial con F04 |
| `tipo_de_via_siniestro` | 95 % faltante en 2019; 0–12 % en 2020–2025 | Variable no comparable en 2019 |
| `modo_desplazamiento_victima` = SD | Entre 9,7 % (2019) y 29,5 % (2021) | Composición por actor con cobertura variable |
| Formato de fecha | 9.406 fechas sin ceros a la izquierda (`2025-9-9`) | Parseo explícito en el ETL. Todas se parsean. |
| Valores espurios | `#¡REF!`, mayúsculas y minúsculas mezcladas (`auto`/`AUTO`) | Normalización en el ETL |
| Coordenadas fuera de CABA | 0 en una caja aproximada | Falta la verificación contra el polígono oficial (Paso 03) |

**Discrepancias de metadatos.**

- F03 describe un archivo con cuatro solapas, dos de ellas diccionarios (p. 9). Los XLSX publicados tienen una sola hoja cada uno.
- En CKAN, la descripción del recurso de víctimas dice "Homicidios" y la del de hechos dice "Lesiones", pero ambos archivos contienen las dos clases.
- La fecha de modificación de los recursos en CKAN (2024-08-27) no coincide con la del servidor (2026-06-29) ni con la cobertura declarada (2019–2025).

### 3.2 F04–F05. Barrios y comunas

Se verificaron **48 barrios y 15 comunas** en GeoJSON (CRS84), con área y perímetro. Cada barrio indica su comuna. Así se confirma el supuesto S5 del Paso 01 en cuanto a la disponibilidad de capas compatibles. Queda pendiente verificar que los límites no hayan cambiado entre 2019 y 2025. Los datos de la fuente (coordenadas WGS84) son compatibles con estas capas.

## 4. Infraestructura vial

| Fuente | Aporte posible por zona | Restricción principal |
|---|---|---|
| F06 Callejero | Longitud de vías por tipo (calle, avenida, autopista), jerarquía vial (local, distribuidora, troncal), sentido, bicisenda, cruces ferroviarios. Las intersecciones pueden derivarse de la topología. | **Solo el estado actual.** No hay historial. *Actualización del Paso 03 (D11): queda excluido de la evaluación predictiva principal y se usa solo para describir el territorio.* |
| F13 Cruces semaforizados | Densidad de cruces semaforizados | Coordenadas del CSV mal formateadas (hay que usar GeoJSON o SHP); fecha de inauguración casi siempre faltante. *Paso 03 (D11): solo descripción territorial.* |
| F16, F17, F21 | Ciclovías, prioridad peatonal, Metrobus | Metadatos pendientes; se necesitan fechas de habilitación para usarlos sin fuga |
| F18 Cámaras de control | Fiscalización | Endogeneidad: suelen instalarse donde hubo siniestros. No se usarán como predictor sin análisis previo. |

## 5. Exposición

| Fuente | Cobertura | ¿Permite ajustar por exposición? |
|---|---|---|
| F07–F09 Volumen vehicular | **Solo 2024**: 95 sensores en las 15 comunas, un miércoles por semana, más una semana de detalle en marzo | Solo como **análisis transversal por corredor en 2024** (Paso 10). No cubre la serie 2019–2025 ni representa la exposición zonal. |
| F10 Conteos peatonales | 60 registros puntuales entre 2017 y 2019 | No. Solo sirve como contexto descriptivo. |
| F11 Conteo vehicular | 257 registros horarios entre 2018 y 2019, sin coordenadas | No |
| F12 Sensores | Inventario sin conteos | No |

**Conclusión preliminar.** Con las fuentes relevadas, el riesgo ajustado por exposición **no puede estimarse por zona ni por período**. Esto confirma que es una extensión condicionada, como se previó en el Paso 01 (D3 e H8). Si el Paso 03 lo confirma, H8 solo será contrastable de forma transversal para 2024, en los corredores con sensor. La consulta institucional pide series históricas de tránsito (sección 7).

## 6. Estado de los supuestos del Paso 01

| Supuesto ([research_proposal.md](research_proposal.md), sección 9) | Estado tras el Paso 02 |
|---|---|
| S1. La fuente tiene fecha, ubicación, actor y gravedad | **Confirmado con matices.** Falta el barrio (se resolverá con unión espacial), el 4,6 % no tiene coordenada y el faltante depende de la gravedad. |
| S2. Se distinguen hechos de víctimas | **Confirmado.** La clave `id_siniestro` concilia el 100 % de los registros. |
| S3. Los criterios de registro son comparables entre años | **Abierto.** Hay irregularidades a fines de 2019, en 2025 y en la variable `tipo_de_via` en 2019. Se consulta al organismo. |
| S4. La cobertura territorial es homogénea | **Abierto.** Se evaluará en los Pasos 03 y 05. |
| S5. Hay capas oficiales compatibles | **Confirmado.** 48 barrios y 15 comunas en WGS84. |
| S6. Los conteos de tránsito pueden no ser comparables | **Confirmado.** Solo hay 2024 y en corredores (sección 5). |
| S7. La infraestructura refleja el período analizado | **En riesgo.** El callejero es solo el estado actual. |
| S8. Hay períodos suficientes para la validación temporal | **Plausible.** Hay 84 meses (28 trimestres). El Paso 03 lo evaluará considerando la pandemia. |
| S9. Literatura adicional | Sin cambios. Pendiente. |

## 7. Consulta institucional

La consulta prevista por el plan quedó redactada en [institutional_inquiry.md](institutional_inquiry.md). Agrega las preguntas que surgieron de este relevamiento. **No fue enviada:** el envío lo debe hacer el responsable del proyecto. Según el plan, la respuesta no es un requisito para continuar.

## 8. Limitaciones del relevamiento

1. Varias búsquedas en el catálogo y los metadatos de F16–F21 quedaron sin completar por el bloqueo del WAF. Conviene reintentar desde un navegador o más adelante.
2. No se consultaron las páginas web del OMSV (F14) ni el conjunto Delitos (F15).
3. No se buscaron series anteriores a 2019. F03 menciona una base de la PFA 2010–2016 con otra fuente; no es directamente comparable.
4. Los perfiles son globales. Los desgloses por zona y período corresponden al Paso 03.
5. Los archivos pueden actualizarse en el portal. Los hashes permiten detectar si cambió la versión.

## 9. Verificación del criterio de aceptación del Paso 02

Criterio del plan: *"fuentes primarias identificadas y limitaciones explícitas. La respuesta institucional no es un requisito para continuar"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Fuentes primarias identificadas | ✔ | F01–F05 verificadas; F06 y F13 como infraestructura; F07–F12 como exposición |
| Período, cobertura, granularidad, identificadores, variables, faltantes, licencia y actualización por archivo | ✔ para F01–F13. ◐ para F14–F22: identificadas, con campos "Por verificar". | [source_register.csv](source_register.csv) |
| Limitaciones explícitas | ✔ | Secciones 3–5 y 8; columna `limitaciones` del registro |
| `docs/data_inventory.md` | ✔ | Este documento |
| `docs/source_register.csv` | ✔ | 22 fuentes y 22 campos |
| Registro de la consulta institucional | ✔ como borrador, no enviado | [institutional_inquiry.md](institutional_inquiry.md) |
| Evidencia reproducible | ✔ | Script, hashes, metadatos CKAN y perfil en [evidence/paso02/](evidence/paso02/) |

**Dictamen (autoauditoría).** El criterio se cumple para las fuentes primarias. Las fuentes candidatas F16–F21 no son necesarias para el núcleo académico, y sus metadatos pendientes no bloquean el Paso 03. Queda pendiente la revisión del responsable y el envío de la consulta.
