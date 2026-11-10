# UrbanSafe CABA — Informe de viabilidad empírica

**Hito:** Paso 03. Auditoría de viabilidad empírica  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:** [notebooks/00_data_audit.ipynb](../notebooks/00_data_audit.ipynb) (ejecutado de punta a punta con kernel limpio), tablas en [reports/tables/00_data_audit/](../reports/tables/00_data_audit/), figuras en [reports/figures/00_data_audit/](../reports/figures/00_data_audit/) y métricas en [feasibility_metrics.json](../reports/tables/00_data_audit/feasibility_metrics.json)

---

## 1. Resumen

Los datos abiertos de CABA **permiten responder el núcleo de la propuesta** a escala **barrio × mes**: pronóstico de la frecuencia y de la concentración territorial en el mes siguiente, comparado contra la persistencia histórica. **No permiten** estimar riesgo ajustado por exposición por zona ni efectos causales. La gravedad territorial (KSI) solo admite un análisis descriptivo.

| Decisión | Elección |
|---|---|
| Unidad espacial | Barrio (48). Robustez: comuna (15) y, opcionalmente, grilla de 1 km |
| Período de agregación | Mes. Sensibilidad: trimestre |
| Período de estudio | 2019-01 a 2025-12. Desarrollo: 2019–2024. **Test provisorio: 2025** |
| Horizonte | t+1 mes. Sensibilidad: t+3 |
| Objetivo de regresión | Hechos (siniestros con víctimas) por barrio-mes |
| Objetivo de clasificación | El barrio está entre los **10 de 48 con más hechos** del mes t+1. Siempre hay exactamente 10 positivos; los empates se resuelven con la regla explícita **R0**. |
| *K* para la priorización | 10. Además, 5 y 15 |
| Exposición | Excluida como covariable zonal; H8 se limita a 2024 por corredor |
| Infraestructura vial | **Excluida de la evaluación predictiva principal.** Solo se usa para describir el territorio. Su aporte predictivo queda condicionado a conseguir datos con vigencia verificable. |

## 2. Protocolo de la auditoría

- **Regla anti-fuga.** Antes de calcular cualquier diagnóstico de concentración se reservó **2025** como test provisorio. Los diagnósticos que orientan decisiones de modelado (controles 6–8 y 10) usan solo **2019–2024**. Los controles de integridad (1–5 y 9) describen la fuente y usan todos los años. El gráfico C1 muestra 2025 solo como cobertura; ninguna decisión depende de su nivel.
- **Entorno.** Python 3.13.7, pandas 3.1.1, GeoPandas 1.2.0, shapely 2.2.0 y numpy 2.5.4, en un entorno virtual fuera de la carpeta sincronizada (`~/.venvs/urbansafe`). El `requirements.txt` formal corresponde al Paso 04.
- **Entradas.** Copias en `data/raw/` de F01, F02, F04, F05 y F07, con SHA-256 idéntico al registrado en el Paso 02 ([sha256.txt](evidence/paso02/sha256.txt)).
- **CRS.** Lat/lon en WGS84 (EPSG:4326). Para distancias y áreas se usa Gauss-Krüger BA con datum Campo Inchauspe (`+proj=tmerc +lat_0=-34.6297166 +lon_0=-58.4627 +k=1 +x_0=100000 +y_0=100000 +ellps=intl +towgs84=-148,136,90`). Es el CRS de `geocodificacion_plana`, identificado empíricamente: mediana de 0,05 m frente a lat/lon.

## 3. Resultados por control

| # | Control | Resultado principal | Implicancia |
|---|---|---|---|
| 1 | Registros por año y mes | 84 meses continuos; 65.818 hechos. Meses atípicos (más de ±30 % frente a la mediana del mismo mes): **2019-11 (−40 %) y 2019-12 (−44 %)**, la pandemia (2020-03 a 2020-10, 2021-02 y 2021-05), y 2024-12 y 2025-12 (+30 % y +37 %) | Marcar las anomalías; no eliminarlas (D3) |
| 2 | Duplicados y relación hecho-víctima | Clave única; 0 huérfanos; los conteos coinciden con las filas en el 100 %; la gravedad del hecho coincide con el máximo de sus víctimas en el 99,95 %; `HC` equivale a mortal. **274 hechos (134 grupos) comparten fecha, hora y lugar.** Hay 1.439 filas de víctimas idénticas, pero no existe id de víctima. | Relación 1:N íntegra. Conservar los duplicados probables con una marca (D10). |
| 3 | Coordenadas | 3.031 sin coordenada (4,6 %); **15,1 % de los graves** frente a 4,2 % de los leves. Hay 286 puntos fuera del polígono, todos a 160 m o menos (mediana de 7,7 m), sobre avenidas límite o la costa. **472 puntos difieren más de 500 m** de su coordenada plana, sobre todo en 2022. | Faltante no aleatorio por gravedad; lat/lon como coordenada principal |
| 4 | Barrios y comunas | No hay coincidencias múltiples. 287 puntos se asignan por cercanía (200 m o menos). La comuna de la fuente coincide con la geometría en el 96,2 % (2.296 de 2.329 discordancias están a menos de 100 m de un límite). Con la coordenada plana cambiaría el barrio del 1,3 %. **Asignables: 95,4 % a barrio y 96,0 % a comuna.** | Regla de asignación D9. El 21 % de los hechos está a menos de 25 m de un límite de barrio. |
| 5 | Cambios metodológicos | `tipo_de_via` falta en el 95 % de 2019. `modo_victima` es SD entre 9,7 % y 29,5 % según el año; `contraparte`, entre 10 % y 37 %. `numero_total_de_victimas` es SD en el 28 % de 2025. Los graves varían entre 2,4 % y 5,9 % según el año; los mortales se mantienen cerca del 1 %. En nov-dic de 2019, el nivel cae al 61 %, mientras la participación por comuna cambia 2,6 pp como máximo (χ², p = 0,0004). | Caída de registro en toda la ciudad con cambio de composición menor. Restricciones de variables (sección 5). |
| 6 | Distribución territorial (2019–2024) | Barrio: el 20 % superior reúne el **42,3 %** de los hechos (32,1 % esperado por superficie); Gini 0,36. **Spearman entre años: 0,955–0,976**; entre meses consecutivos: mediana de 0,82 (rango 0,55–0,89). Comuna: Gini 0,14. | La concentración y la persistencia son altas, así que el baseline de persistencia será exigente. La persistencia mensual deja margen para mejorar. |
| 7 | *Zero inflation* (2019–2024) | Hechos, barrio × mes: **1,2 % de ceros**, media de 14,9. Grilla de 1 km × mes: 25,6 %. Grilla de 500 m × mes: 56 %. KSI, barrio × mes: 55,7 % de ceros (54,1 % esperado bajo Poisson), es decir, sin exceso de ceros, pero con un conteo bajo. | Barrio × mes no tiene *zero inflation*. Las grillas finas no se justifican como escala principal. |
| 8 | Desbalance y dispersión | C-a (P75 = 20 hechos): prevalencia anual entre 11,5 % y 31,4 %, inestable. **C-b (quintil superior por mes): 20,8 % fijo.** C-c (al menos un KSI): entre 27 % y 53 % según el año. Sobredispersión: α NB2 ≈ 0,07; LR NB frente a Poisson ≈ 1.650; dispersión residual 2,2 (barrio × mes). **Empates (8.1):** en 23 de 72 meses los puestos 10 y 11 empatan (2 a 5 barrios en el corte; 33 plazas en disputa en total). | C-b como objetivo principal, con la regla de desempate R0; la binomial negativa es necesaria en el Paso 07 |
| 9 | Conteos vehiculares | 95 sensores, **solo 2024** y solo miércoles; están en 29 de 48 barrios; el 12,8 % de los hechos de 2024 ocurre a 200 m o menos de un sensor | No sirven como exposición zonal (D8) |
| 10 | Observaciones efectivas | Barrio × mes: 3.456 en el desarrollo; 2.880 con un rezago de 12 meses; unas 1.728 en el primer *fold*; 576 en el test. Comuna × mes: 1.080, 540 y 180, respectivamente. Hechos de desarrollo asignados a barrio: 51.688 de 54.066. | Tamaño suficiente para Poisson, binomial negativa y árboles con pocas variables |

## 4. Decisiones y justificación

**D1. Unidad espacial: barrio.** Es la escala más fina con densidad suficiente: 1,2 % de ceros y 14,9 hechos por barrio-mes. Tiene significado administrativo, y sus 48 unidades permiten una priorización top-K y un clustering con sentido. La comuna tiene solo 15 unidades: el quintil superior serían 3 comunas, y el test solo tendría 180 observaciones. Queda como escala de robustez. La grilla de 1 km es viable (25,6 % de ceros) pero más ruidosa; queda como sensibilidad opcional en el Paso 10. La grilla de 500 m se descarta. *Riesgo:* las avenidas que sirven de límite concentran hechos sobre la frontera entre barrios, lo que vuelve arbitraria su asignación. Se evaluará la sensibilidad en el Paso 10.

**D2. Agregación mensual.** Ofrece 72 períodos de desarrollo y 12 de test, frente a 24 y 4 trimestrales. Con el mes ya hay pocos ceros, así que el trimestre no aporta estabilidad relevante y reduce la evaluación fuera de muestra. El trimestre queda como sensibilidad.

**D3. Período y particiones.** El estudio abarca 2019-01 a 2025-12, con 2025 como test provisorio. Los meses de 2019-11/12 y de la pandemia se **marcan** y no se eliminan, para conservar la continuidad de los rezagos. El Paso 06 fijará los *folds* de validación expansiva en 2022–2024 (posteriores a la pandemia) y el tratamiento de los rezagos contaminados. *Riesgo:* 2025 podría ser provisorio. Se lo preguntamos al organismo. *(Actualización del Paso 06: como 2024 es un fold de validación usado para seleccionar, no puede servir de test. Si se confirma la provisionalidad, el Paso 10 informará V2024 como validación retrospectiva.)*

**D4. Horizonte t+1 mes.** Corresponde a una decisión de priorización mensual. La persistencia anual (0,97) es mucho mayor que la mensual (0,82): el ruido mes a mes deja espacio para que un modelo mejore al historial, pero no lo garantiza.

**D5. Regresión: hechos por barrio-mes (Y1).** La clave y los conteos son íntegros. Las víctimas (Y2) quedan como objetivo secundario. **KSI no es principal**: el porcentaje de graves depende del relevamiento hospitalario y varía entre años, a los graves les falta la coordenada con mucha más frecuencia (15 %) y el conteo es bajo (media de 0,72). Hay sobredispersión, así que la **binomial negativa es obligatoria** en el Paso 07.

**D6. Clasificación: top 10 del mes t+1 (C-b).** El umbral se define de forma relativa dentro de cada mes, sin consultar el test. Su prevalencia es estable (20,8 %) y su positivo coincide con la decisión operativa (las K = 10 zonas prioritarias). Además, es inmune a los cambios de nivel por pandemia, registro o provisionalidad. El umbral absoluto (C-a) queda como sensibilidad porque su prevalencia anual varía casi al triple. *Advertencia:* con una persistencia tan alta, el baseline de persistencia será difícil de superar. Ese resultado también es informativo para H4 y H5.

**D6.1. Regla de desempate en el corte del top 10.** Los conteos son enteros: en **23 de los 72 meses** de desarrollo, los puestos 10 y 11 tienen el mismo conteo. Hay entre 2 y 5 barrios empatados en el corte y 33 plazas en disputa en total. La versión anterior del notebook desempataba por el orden de las filas (`rank(method="first")`), así que el orden del archivo decidía la etiqueta. Se corrige así:

- **Regla principal R0.** Exactamente 10 positivos por mes. Se ordena por conteo descendente, y los empates se resuelven con una clave pseudoaleatoria uniforme generada con `numpy.random.default_rng([20261110, ordinal del mes])` sobre los barrios ordenados por nombre. La regla es reproducible y no favorece de forma sistemática a ningún barrio. Tampoco usa el historial, que beneficiaría artificialmente al baseline de persistencia.
- **Dos preguntas distintas.** (a) **Sensibilidad al desempate:** se mantienen exactamente 10 positivos y solo cambia cómo se resuelven los empates (R0, R-id y 500 semillas). (b) **Cambio de definición de positivo:** deja de exigirse 10 positivos (R-incl, R-excl-empates y R-estricta).
- **Ilustración.** Se usan dos rankings de referencia sin ajuste: la persistencia en t−1, como *baseline*, y la media de los 12 meses previos, como *candidato* ilustrativo. Se evalúan en 2020-01 a 2024-12 (60 meses), **sin 2025**. Las tablas son [c08_sensibilidad_empates.csv](../reports/tables/00_data_audit/c08_sensibilidad_empates.csv), [c08_intervalo_sensibilidad_desempate.csv](../reports/tables/00_data_audit/c08_intervalo_sensibilidad_desempate.csv) y [c08_semillas_diferencia_pareada.csv](../reports/tables/00_data_audit/c08_semillas_diferencia_pareada.csv).

**(a) Sensibilidad al desempate: diferencia pareada.** En cada una de las 500 repeticiones, las etiquetas y las selecciones se generan **una sola vez**, con la semilla de esa repetición. El candidato y el baseline se evalúan con **las mismas etiquetas y los mismos meses**, y se calcula ΔP@10 = P@10(candidato) − P@10(baseline). El intervalo de sensibilidad de la ventaja está formado por los percentiles 2,5 y 97,5 de ΔP@10. No se obtiene comparando intervalos marginales.

| Métrica (500 repeticiones) | p2,5 | Mediana | p97,5 |
|---|---|---|---|
| P@10, media de 12 meses | 0,745 | 0,750 | 0,757 |
| P@10, persistencia | 0,673 | 0,682 | 0,690 |
| **ΔP@10 pareada** | **0,060** | **0,068** | **0,077** |

Con R0 (semilla fija), ΔP@10 = 0,063. Con R-id, 0,065. Con la versión esperada invariante a empates, 0,069. En este ejemplo, el intervalo pareado excluye el 0: la ventaja ilustrativa no depende del desempate.

**Incertidumbre entre períodos.** Es otra fuente de incertidumbre y no se mezcla con el intervalo anterior. Como referencia, la ΔP@10 mensual con R0 tiene una media de 0,063 y un desvío de 0,119 entre los 60 meses. En los Pasos 08 y 10 se evaluará con un método que respete la dependencia temporal, por ejemplo un *bootstrap* por bloques de meses.

**(b) Cambio en la definición de positivo.**

| Regla | Qué mide | Positivos por mes | Etiquetas distintas de R0 (en meses sin empate) | P@10, persistencia | P@10, media de 12 meses | ΔP@10 |
|---|---|---|---|---|---|---|
| R-incl | Todos los empatados en el corte son positivos | 10–13 | 36 (0) | 0,710 | 0,772 | 0,062 |
| R-excl-empates | En los meses con empate, solo los que superan el corte; en el resto, los 10 habituales | 7–10 | 33 (0) | 0,665 | 0,728 | 0,063 |
| R-estricta (antes R-excl) | Umbral estricto y > conteo del décimo **en todos los meses** | 7–9 | 102 (**69**) | 0,623 | 0,678 | 0,055 |

**Qué mide R-estricta.** Excluye al décimo barrio, y a quienes comparten su conteo, **aunque su puesto sea inequívoco**: en los 49 meses sin empate, quita 69 positivos que R0 no discute. Por eso la brecha R-incl − R-estricta (**0,087** en persistencia y **0,093** en la media de 12 meses) mezcla el efecto del desempate con un cambio en la definición de positivo. **No es una medida de sensibilidad al desempate.** La anterior versión de este informe la presentaba así ("hasta 0,06"), y la afirmación se retira. La comparación de definiciones restringida a los empates es R-incl frente a R-excl-empates. El efecto puro del desempate, con diez positivos, lo aíslan las 500 semillas.

**Regla para los Pasos 08 y 10.** Se informará:
1. P@K con R0;
2. la P@K esperada invariante a empates, Σᵢ P(i∈S)·P(i∈P)/K;
3. el intervalo de sensibilidad al desempate de ΔP@K = P@K(modelo) − P@K(baseline): percentiles 2,5–97,5 de 500 repeticiones pareadas, con las mismas etiquetas y los mismos meses;
4. la incertidumbre entre períodos, por separado;
5. ΔP@K con R-incl y R-excl-empates, como sensibilidad de definición.

Una ventaja se considera **dependiente del desempate** si su intervalo pareado incluye el 0. Si la conclusión cambia entre R-incl y R-excl-empates, se declara sensible a la definición de positivo en los empates.

Los valores de referencia de esta tabla describen la sensibilidad de la etiqueta. No son resultados de modelado y no usan el test.

**D7. K = 10**, con K = 5 y K = 15 como sensibilidad.

**D8. Exposición.** Los conteos cubren un solo año, un día por semana, en corredores, y solo el 12,8 % de los hechos de 2024 ocurre cerca de un sensor. El riesgo ajustado por exposición **no es estimable** por zona y período. H8 se limita a un análisis transversal de 2024 por corredor, como extensión.

**D9. Asignación espacial (regla para el ETL del Paso 04).**
1. Lat/lon dentro del polígono del barrio (`within`).
2. Si cae fuera, el barrio más cercano a 200 m o menos (287 hechos).
3. Si no hay coordenada, la comuna de la fuente, válida solo para la escala comuna (371 hechos).
4. Si no hay coordenada ni comuna, se excluye del panel zonal con una marca (2.660 hechos, 4,0 %), pero se conserva en los totales de la ciudad.

En caso de discordancia, prevalece la geometría y la discordancia se registra.

**D10. Duplicados.** Se conservan con una marca los 274 hechos con igual fecha, hora y lugar, y las víctimas idénticas. La sensibilidad se evaluará en el Paso 04.

**D11. Infraestructura vial excluida de la evaluación predictiva principal.** El callejero (F06) y los cruces semaforizados (F13) reflejan el **estado actual** y no tienen fechas de vigencia verificables: F13 casi no registra fechas de inauguración, y F06 no tiene historial. Usarlos como atributos fijos en pronósticos con fecha de corte entre 2019 y 2024 podría introducir infraestructura posterior al período pronosticado. Por eso:
- **Ningún modelo** de la evaluación predictiva principal (Pasos 06–08 y 10) incluye variables derivadas de F06 o F13.
- F06 y F13 se usan solo para **describir el territorio**: caracterización de barrios en el AED (Paso 05), interpretación de perfiles en el clustering (Paso 09, sin que entren como atributos de agrupamiento predictivo) y comunicación (Paso 11). Se aclarará siempre que describen el estado vigente.
- El **aporte predictivo de la infraestructura (PS4/H3) queda condicionado** a conseguir datos con vigencia verificable en cada fecha de corte: versiones históricas del callejero, fechas de alta y baja de los semáforos o de las ciclovías. La pregunta 8 de la consulta institucional apunta a eso. Si se obtienen, se evaluará en una comparación anidada separada, construyendo las variables solo con la infraestructura vigente en cada fecha de corte.
- La **superficie y la vecindad** de los barrios derivan de los límites oficiales que definen la unidad del panel. No describen la red vial y se mantienen, bajo el supuesto de límites estables entre 2019 y 2025.

## 5. Restricciones para las etapas siguientes

- **Variables no comparables en el tiempo.** `tipo_de_via` (2019). `modo_victima` y `contraparte`: SD variable; si se usan, SD debe ser una categoría explícita y debe evaluarse la sensibilidad. `numero_total_de_victimas` (2025): usar la suma de leves, graves y mortales.
- **Infraestructura sin vigencia verificable.** El callejero y los cruces semaforizados reflejan solo el estado actual. **Quedan fuera de la evaluación predictiva principal** y se usan solo para describir el territorio (D11).
- **Sesgo de registro.** El faltante de coordenadas es mayor en los graves y en algunos años (2021). Las conclusiones territoriales sobre gravedad son descriptivas.
- **Anomalías.** Hay que incluir indicadores de anomalía, o justificar su exclusión, en los Pasos 05–07.
- **Interpretación.** Los conteos por barrio son **carga registrada**, no riesgo. El barrio más extenso de la ciudad concentra el mayor conteo (C6).

## 6. Preguntas respondibles

| Pregunta o hipótesis | Estado | Condición |
|---|---|---|
| PS1 / H1 | Respondible | Con marcas de anomalía |
| PS2–PS3 / H2, H4 | Respondibles | Barrio × mes, t+1, frente a la persistencia |
| PS4 / H3 | **Condicionada** | Solo con datos de infraestructura de vigencia verificable en cada fecha de corte. Con las fuentes actuales, la infraestructura solo sirve para describir el territorio (D11). |
| PS5 / H6 | Respondible | 48 barrios; composición con SD |
| PS6 / H5, H7 | Respondibles | Robustez con comuna, trimestre y grilla de 1 km |
| PS7 / H8 | Parcial | Solo 2024, en corredores con sensor |
| Riesgo ajustado por exposición por zona | **No respondible** | Sin denominador |
| Efectos causales | **No respondible** | Fuera del diseño |

**Observaciones preliminares, sin contraste formal.** C6 muestra que los hechos se concentran por encima de lo esperado por superficie y que la persistencia anual es muy alta, como plantea H1. C7 muestra que los ceros aumentan con la resolución espacial, como anticipa H7. Ambas se contrastarán formalmente en los Pasos 05 y 10.

## 7. Verificación del criterio de aceptación del Paso 03

Criterio del plan: *"unidad de análisis, período, objetivos y restricciones elegidos sobre evidencia"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Los 10 controles del plan | ✔ | Notebook, secciones 1–10 |
| Comparación barrio × mes y comuna × mes | ✔ | C7, C8, C10 y la matriz de la sección 11 del notebook |
| Grillas solo si la densidad lo justifica | ✔ | C7: evaluadas y descartadas como escala principal |
| Evaluación de la agregación trimestral | ✔ | C7, C8 y C10; se descarta como escala principal |
| Unidad de análisis elegida sobre evidencia | ✔ | D1 |
| Período elegido sobre evidencia | ✔ | D2 y D3 |
| Objetivos elegidos sobre evidencia | ✔ | D5 y D6 (umbral sin usar el test) |
| Restricciones explícitas | ✔ | Secciones 5 y 6 |
| `notebooks/00_data_audit.ipynb` ejecutado | ✔ | Ejecución completa con nbconvert (kernel limpio) |
| Informe de viabilidad | ✔ | Este documento |

## 8. Registro de correcciones de la revisión

| Fecha | Hallazgo del revisor | Corrección | Evidencia |
|---|---|---|---|
| 2026-11-10 | La etiqueta top 10 desempataba por el orden de las filas; hay empate entre los puestos 10 y 11 en 23 de 72 meses | Regla explícita R0, con exactamente 10 positivos y desempate pseudoaleatorio con semilla fija. Sensibilidad frente a R-id, R-incl, R-excl, 500 semillas y la Precision@K esperada invariante a empates (D6.1). | Notebook, sección 8.1; `c08_empates_por_mes.csv`, `c08_reglas_empate.csv` y `c08_sensibilidad_empates.csv` |
| 2026-11-10 | Las 500 semillas no comparaban modelo y baseline con las mismas etiquetas. Además, R-excl eliminaba al décimo barrio aunque su puesto fuera inequívoco, así que mezclaba el desempate con un cambio de definición. | ΔP@K pareada por repetición (mismas etiquetas y mismos meses), con intervalo 2,5–97,5; la incertidumbre entre períodos se trata aparte. R-excl pasa a llamarse R-estricta y se documenta como cambio de definición; se agrega R-excl-empates. Se retira la afirmación "hasta 0,06". (D6.1) | Notebook, sección 8.1; `c08_intervalo_sensibilidad_desempate.csv` y `c08_semillas_diferencia_pareada.csv` |
| 2026-11-10 | El informe proponía usar el callejero y los semáforos actuales como atributos fijos en pronósticos históricos | Excluidos de la evaluación predictiva principal; uso solo descriptivo; PS4/H3 condicionadas a datos con vigencia verificable (D11) | Notebook, secciones 11.1, 11.2 y 12; propuesta (H3 y PS4); registro de fuentes (F06 y F13) |

**Dictamen (autoauditoría).** El criterio se cumple. Las decisiones del Paso 01 que estaban abiertas quedan cerradas (sección 8 de la [propuesta](research_proposal.md)), salvo la partición definitiva, que se fija en el Paso 06. Queda pendiente la revisión del responsable. La consulta institucional (provisionalidad de 2025 y caída de 2019) puede modificar D3, pero no bloquea el avance.
