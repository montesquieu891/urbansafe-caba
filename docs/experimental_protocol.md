# UrbanSafe CABA — Protocolo experimental

**Hito:** Paso 06. Feature engineering y diseño experimental  
**Estado:** revisado, apto para cierre  
**Fecha:** 2026-11-10  
**Código:** [`src/features.py`](../src/features.py), [`src/labels.py`](../src/labels.py) y [`tests/test_features.py`](../tests/test_features.py)  
**Evidencia:** [notebooks/02_feature_engineering.ipynb](../notebooks/02_feature_engineering.ipynb) y [reports/tables/02_feature_engineering/](../reports/tables/02_feature_engineering/)

> Este protocolo se fija **antes** de entrenar cualquier modelo y antes de consultar el test. Los Pasos 07, 08 y 10 deben seguirlo. Cualquier desviación se registra con fecha y justificación en la sección 11.

---

## 1. Tarea y unidad

| Elemento | Definición | Fundamento |
|---|---|---|
| Unidad | Barrio (48) × mes | D1 y D2 del informe de viabilidad |
| Horizonte | h = 1 mes | D4 |
| Fila | (barrio, mes objetivo T) | — |
| Corte | c = T − h. Último mes observable: L = T − h − gap | — |
| Objetivo de regresión | `y_target`: hechos con víctimas del barrio en T | D5 |
| Objetivo de clasificación | `top10_target`: el barrio está entre los 10 de mayor `y_target` en T, con desempate R0 | D6 y D6.1 |
| Período utilizable | Meses objetivo 2020-01 a 2025-12 con gap = 0 y 2020-02 a 2025-12 con gap = 1. El primer mes completo depende de la ventana de 12 meses. | Paso 06 |

## 2. Disponibilidad de la información y latencia

- **Supuesto principal (gap = 0).** Al cierre del mes T−1 se conocen los hechos de ese mes y de todos los anteriores. Esto describe un uso **interno**, con acceso a la base policial actualizada. La base **abierta** se publica una vez por año, así que con datos públicos la latencia real sería mayor.
- **Sensibilidad (gap = 1).** Solo se conoce hasta T−2 (`features_barrio_mes_h1_g1.csv`). Se informa en el Paso 10.
- **Revisiones de la fuente.** La base no publica versiones fechadas, así que no se puede reconstruir qué se sabía exactamente en cada corte. Por eso **se excluye la gravedad** de las variables: puede cambiar después del corte, porque un hecho es mortal si la víctima fallece dentro de los 30 días, y el relevamiento hospitalario varía entre años (E9). Los conteos de hechos se consideran estables. Este es un supuesto no verificable (sección 10).

## 3. Variables

El catálogo completo, con su definición y su ventana, está en [catalogo_variables.csv](../reports/tables/02_feature_engineering/catalogo_variables.csv). Todas las variables dinámicas usan una ventana que termina en L.

| Familia | Variables | Nota |
|---|---|---|
| Histórica | Hechos en L, L−1, L−2 y en T−12; medias de 3, 6 y 12 meses; tendencia ma3/ma12 | Plan, Paso 06 |
| Histórica relativa | Participación en la ciudad (L y 12 meses), puesto (L y media de 12 meses), frecuencia en el top 10 en 12 meses | Robustas a cambios de nivel (E8) |
| Nivel ciudad | Total de la ciudad en L, media de 12 meses y en T−12 | Capturan el nivel general (E1) |
| Temporal | Seno y coseno del mes de T; meses de pandemia en la ventana de L | El calendario de T se conoce de antemano |
| Territorial | Superficie (km²), comuna (one-hot), densidad de 12 meses | Límites oficiales, supuestos estables |
| Vecindad | Media de los vecinos *queen* de ma3 y de la participación de 12 meses | Autocorrelación espacial (E6) |
| Composición | Proporción de 12 meses por modo de la víctima, con **SD explícito** | E3 y E4 |

**Excluidas.**

| Variable | Motivo |
|---|---|
| Infraestructura vial (callejero, semáforos) | No tiene vigencia verificable (D11) |
| Exposición vehicular | Solo hay datos de 2024 y en corredores (D8) |
| Gravedad o KSI | Revisiones posteriores al corte y registro cambiante (E9) |
| Anomalía del mes objetivo | No se conoce en el corte |
| Marca de registro 2019-11/12 | Es una anotación hecha después, en la auditoría |

## 4. Particiones y procedimiento

| Fold | Evaluación | Entrenamiento con gap = 0 | Entrenamiento con gap = 1 | Filas de entrenamiento (gap 0 / gap 1) |
|---|---|---|---|---:|
| V2022 | Validación retrospectiva 2022 | 2020-01 a 2021-12 | 2020-02 a 2021-11 | 1.152 / 1.056 |
| V2023 | Validación retrospectiva 2023 | 2020-01 a 2022-12 | 2020-02 a 2022-11 | 1.728 / 1.632 |
| V2024 | Validación retrospectiva 2024 | 2020-01 a 2023-12 | 2020-02 a 2023-11 | 2.304 / 2.208 |
| **Final** | **Test reservado 2025** | 2020-01 a 2024-12 | 2020-02 a 2024-11 | 2.880 / 2.784 |

Cada bloque de evaluación tiene 576 filas para ambos gaps.

1. **Validación retrospectiva expansiva** con origen rodante. Dentro del año de evaluación, cada mes usa los datos observados hasta L. Se ajusta una vez por bloque, con etiquetas cuyo mes objetivo es como máximo el último mes observable al inicio de enero. Con gap = 0 el límite es diciembre; con gap = 1 es noviembre. El ajuste final aplica la misma regla al inicio de 2025.
2. **Mismas filas y fechas** para la regresión y la clasificación.
3. **Todo ajuste ocurre dentro del fold y solo con el entrenamiento:** imputación, escalado y codificación (`make_preprocessor`, dentro de un `Pipeline`), selección de variables, regularización, remuestreo, calibración, hiperparámetros y umbral de decisión.
4. **Selección.** Se elige el modelo y los hiperparámetros por la métrica principal **promediada sobre los tres *folds***. Las grillas se limitan a un máximo de 30 combinaciones por familia de modelos, con semilla 20261110, para no sobreajustar la validación.
5. **Meses de pandemia en el entrenamiento.** Excluir de la pérdida de entrenamiento los objetivos marcados como anómalos se trata como un **hiperparámetro** (sí o no) elegido en validación. Esto es legítimo porque son meses de entrenamiento ya ocurridos.
6. **Test.** Se reajusta el modelo seleccionado en el entrenamiento final y se evalúa **una sola vez** en 2025. Ninguna decisión posterior puede usar resultados del test. Si 2025 resulta provisorio (consulta institucional), se informa además el resultado de V2024 en el Paso 10 como validación retrospectiva. V2024 forma parte de la selección.

## 5. Baselines, métricas y criterios de mejora (fijados a priori)

### 5.1 Baselines (sin ajuste)

| Tarea | Baseline | Definición |
|---|---|---|
| Regresión | Persistencia | ŷ = hechos en L |
| | Estacional | ŷ = hechos en T−12 |
| | Media de 12 meses | ŷ = media de 12 meses que termina en L |
| Clasificación y priorización | Ranking por persistencia | Top 10 por hechos en L (desempate R0) |
| | Ranking por media de 12 meses | Top 10 por la media de 12 meses |

El **mejor baseline** de cada tarea se identifica en la validación (media de los *folds*) y es la referencia de los criterios de mejora.

### 5.2 Métricas

- **Regresión.**
  - Principal: **MAE**.
  - Secundarias: devianza de Poisson media, sesgo (error medio), MAE por barrio y por año de validación.
  - Si el modelo lo permite (binomial negativa), cobertura de los intervalos de predicción al 80 % y al 95 %.
- **Clasificación.**
  - Principal sin umbral: **PR-AUC**.
  - Principal operativa: **Precision@10**, con la regla R0, la versión esperada invariante a empates y el intervalo pareado de sensibilidad al desempate sobre 500 semillas (D6.1).
  - Secundarias: *precision*, *recall* y F1 con el umbral elegido en la validación (el que maximiza F1 en los *folds* agrupados; la grilla utilizada en la ejecución histórica del Paso 08 se registra en la sección 11), matriz de confusión, calibración (Brier y curva de confiabilidad) y **Precision@10 en las plazas inciertas**: la métrica restringida a los barrios fuera del núcleo persistente, definido dentro de cada *fold* como los barrios con frecuencia de top 10 mayor que 0,8 en el entrenamiento.
- **Incertidumbre entre períodos.** *Bootstrap* por bloques móviles de 3 meses, con 2.000 réplicas, sobre la diferencia entre modelo y baseline. Se calcula por separado de la sensibilidad al desempate.

### 5.3 Criterios de mejora relevante

| Tarea | En validación (selección) | En test (confirmación) |
|---|---|---|
| Regresión | MAE medio ≤ 0,97 × MAE del mejor baseline **y** mejora en al menos 2 de 3 *folds* | IC 95 % por bloques de la diferencia de MAE (modelo − baseline) < 0 |
| Clasificación | ΔP@10 (modelo − mejor ranking baseline) ≥ 0,02 en la media **y** en al menos 2 de 3 *folds*; el intervalo pareado de desempate excluye el 0 | IC 95 % por bloques de ΔP@10 > 0 **y** el intervalo pareado de desempate excluye el 0 |

Si no se cumplen, la conclusión es que **el modelo no mejora al historial**. La recomendación operativa será entonces el baseline (H2, H4 y H5).

## 6. Modelos candidatos (Pasos 07 y 08)

- **Regresión.** GLM Poisson con regularización; binomial negativa, justificada por la sobredispersión de C8; *gradient boosting* de árboles con pérdida Poisson (`HistGradientBoostingRegressor`).
- **Clasificación.** Regresión logística regularizada, *random forest* y *gradient boosting* (`HistGradientBoostingClassifier`, que no agrega dependencias), con y sin ponderación de clases. **SMOTE** solo si la ponderación no alcanza: con una prevalencia fija del 20,8 % se anticipa que no hará falta.
- **Interpretabilidad (Paso 08).** SHAP sobre el modelo seleccionado, que se interpreta como **patrones predictivos**. Con variables colineales (6 pares con Spearman > 0,95), la atribución se reparte; se informará por familias.

## 7. Controles de fuga e integridad (superados)

| Control | Resultado | Prueba |
|---|---|---|
| C1 Panel único y completo (48 × 84) | ✔ | Notebook §3; `test_panel_y_features_unicos_y_completos` |
| C2 Variables completas desde 2020-01 | ✔ | Ídem |
| C3 Cambiar datos posteriores al corte no altera las variables previas (gap 0 y 1; 4 cortes; 17.760 filas) | ✔ | `test_perturbar_futuro_no_cambia_features_previas` |
| C4 Independencia del orden de las filas | ✔ | `test_rezagos_no_cruzan_barrios_y_son_independientes_del_orden` |
| C5 Los rezagos no cruzan barrios | ✔ | Ídem |
| C6 Objetivos alineados; exactamente 10 positivos por mes | ✔ | `test_objetivos_alineados` |
| C6b La etiqueta de clasificación solo depende del mes objetivo | ✔ | `test_objetivo_de_clasificacion_solo_depende_del_mes_objetivo` |
| C7 Entrenamiento anterior a la validación; test nunca usado | ✔ | `test_folds_cronologicos_y_disjuntos` |
| C8 Variables del entrenamiento observadas antes de la validación | ✔ | Ídem |
| C9 Preprocesador ajustado solo con el entrenamiento | ✔ | `test_preprocesador_se_ajusta_solo_con_entrenamiento` |
| C10 Sin variables excluidas | ✔ | `test_variables_excluidas_no_estan` |
| C11 La latencia (gap) desplaza la información | ✔ | `test_gap_desplaza_la_informacion` |
| C12 Regresión y clasificación comparten las particiones | ✔ | Notebook §3 |
| C13 Etiquetas de entrenamiento disponibles al inicio de cada evaluación (ambos gaps, cuatro ajustes) | ✔ | `test_etiquetas_de_entrenamiento_disponibles_al_inicio` y notebook §3 |

Los ocho casos del control C13 cubren los tres folds y el ajuste final. Antes de corregir las máscaras fallaban los cuatro casos de gap = 1.

## 8. Análisis de sensibilidad previstos (Paso 10)

- Latencia: gap = 1.
- K = 5 y K = 15.
- Definición de positivo en empates: R-incl y R-excl-empates.
- Escala: comuna × mes, barrio × trimestre y, opcionalmente, grilla de 1 km.
- Resultado de la validación retrospectiva V2024 si se confirma que los datos de 2025 son provisorios.
- Exclusión de los meses de pandemia del entrenamiento.
- Conjunto de variables sin composición, para medir el efecto del faltante SD.

## 9. Reproducción

```bash
python -m src.data_processing --download
```

```bash
python -m src.features
```

```bash
python -m pytest -q tests
```

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 02_feature_engineering.ipynb
```

## 10. Supuestos y limitaciones

1. **Disponibilidad de los datos al corte (gap = 0).** Es optimista para un uso con datos abiertos. Se mitiga con la sensibilidad gap = 1.
2. **No hay versiones fechadas de la base.** Los conteos históricos pueden haberse revisado después del corte (por ejemplo, hechos cargados tarde). No es verificable.
3. **Límites de barrio estables entre 2019 y 2025.** La superficie y la vecindad se derivan de los límites actuales.
4. **La marca de registro de 2019-11/12 queda fuera de las variables.** Esos meses entran sin corrección en `y_lag12` y en las ventanas de 12 meses de los objetivos de 2020. Afecta solo al entrenamiento.
5. **Colinealidad alta** entre las variables históricas. Requiere regularización y una interpretación por familias.
6. **Test 2025 posiblemente provisorio** (consulta institucional pendiente).

## 11. Registro de desviaciones

| Fecha | Desviación | Justificación |
|---|---|---|
| 2026-11-10 | Particiones: con gap > 0, el entrenamiento se limita a las etiquetas observables al inicio de cada evaluación (`temporal_folds`, `final_split`; control C13) | Corrige una fuga de etiquetas en la sensibilidad gap = 1 que la autoauditoría original del Paso 06 no había detectado. Se detectó y corrigió fuera de esa revisión. No altera los resultados con gap = 0, como se verificó en el Paso 07 con predicciones, métricas y grilla idénticas. |
| 2026-11-10 | Paso 08, **aclaración previa al modelado** (registrada antes de entrenar clasificadores): la métrica de **selección** en clasificación es la **Precision@10 esperada invariante a empates**, promediada en los tres *folds*. El desempate de la selección se hace por PR-AUC media. El umbral de F1 se elige con las predicciones de validación agrupadas. SMOTE no se aplica (prevalencia fija del 20,8 %); la ponderación de clases es un hiperparámetro | La sección 5.2 nombraba dos métricas principales (PR-AUC y Precision@10) sin decir cuál decide. Se elige la que coincide con el criterio de mejora (5.3) y no depende de semillas. |
| 2026-11-10 | Paso 08, desviación de implementación detectada en auditoría: se congeló el umbral 0,46 (F1 = 0,7983) mediante una grilla de 91 cortes entre 0,05 y 0,95 en V2022–V2024. El máximo sobre todos los cortes distintos de esas predicciones fue F1 = 0,8006 en 0,444245. | Se conserva 0,46 para mantener la trazabilidad de las métricas históricas de 2025. El ranking top-10 se calcula a partir de los puntajes. La sensibilidad con gap = 1 reutiliza 2025 como análisis exploratorio y conserva la configuración congelada. |
| 2026-11-10 | Paso 07: se agregó la NB2 con penalización L2 (8 configuraciones, `grid_posthoc`) **después de ver el test** | La validación sola mostró que los GLM sin regularizar, incluida la NB2 del protocolo, son inestables en V2022 (pocos meses de entrenamiento; variables de ciudad colineales). Se informa como no confirmatoria; la selección congelada no cambia y la NB2 con L2 no habría ganado (3,864 frente a 3,863). Ver [regression_report.md](regression_report.md), §5. |

---

## 12. Dictamen científico del Paso 06 (autoauditoría)

**Tipo de revisión.** **Autoauditoría**: la revisión la hizo el mismo agente que implementó, aplicando la skill `ml-scientific-reviewer`. No hubo un revisor independiente porque la delegación no fue autorizada en esta sesión. Se recomienda una revisión independiente antes de cerrar el Paso 08.

**Alcance.** Se reconstruyeron el corte temporal, la definición de los objetivos y el origen de cada variable a partir del código (`src/features.py`) y de los artefactos (catálogo, controles y particiones). Todavía no hay modelos ni predicciones que revisar.

| # | Hallazgo | Evidencia | Severidad | Corrección | Condición de aprobación |
|---|---|---|---|---|---|
| R1 | La vecindad se calculaba como *rook* (límite con longitud > 0) aunque estaba documentada como *queen*, y era inconsistente con el AED (5,21 frente a 4,96 vecinos) | `queen_neighbors`; media de vecinos | Media (inconsistencia metodológica, sin fuga) | Corregida: contacto en al menos un punto. Ahora tiene 5,21 vecinos de media, igual que el AED. Se reejecutaron los tests y el notebook. | ✔ Cumplida |
| R2 | El supuesto gap = 0 no es verificable con la base abierta, que se publica una vez por año | Sección 2 | Media | Sensibilidad gap = 1 construida y probada (C3 y C11); se informará en el Paso 10 | Informar gap = 1 junto al resultado principal |
| R3 | Las revisiones posteriores al corte no son observables | Sección 2 | Media, no corregible | Gravedad excluida; supuesto declarado | Mantener la advertencia en los resultados |
| R4 | Colinealidad alta (6 pares con Spearman > 0,95) | Notebook §4 | Baja para la predicción; media para la interpretación | Regularización dentro del *fold*; SHAP por familias | Verificar en los Pasos 07 y 08 |
| R5 | Riesgo de sobreajustar la validación al probar muchas configuraciones | Sección 4.4 | Media | Grillas acotadas (≤ 30), métrica promediada en 3 *folds*, criterios fijados a priori | Registrar el número de configuraciones probadas |
| R6 | La exploración del notebook §4 usa todo el desarrollo (2020–2024) | Notebook §4 | Baja | No se seleccionaron variables a partir de ella; el conjunto está fijado a priori | ✔ Cumplida |
| R7 | Los meses de pandemia y de registro anómalo están en el entrenamiento | Secciones 4.5 y 10.4 | Baja | Exclusión opcional como hiperparámetro; *folds* de validación posteriores a la pandemia | Informar la decisión tomada en validación |
| R8 | El test 2025 puede ser provisorio | Informe de viabilidad, D3 | Media | V2024 disponible como validación retrospectiva | Identificar la provisionalidad del test 2025 y reportar V2024 como validación si corresponde |

**Dictamen.** **Apto para cerrar el Paso 06.** Se corrigió el desfase de etiquetas con gap = 1 y se incorporó C13 para verificar ambos gaps. V2024 queda identificado como validación retrospectiva y 2025 sigue reservado para la evaluación final. Las condiciones R2, R4, R5, R7 y R8 se verifican en los Pasos 07, 08 y 10.

## 13. Verificación del criterio de aceptación del Paso 06

Criterio del plan: *"pruebas de integridad temporal y controles de leakage superados"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| `notebooks/02_feature_engineering.ipynb` | ✔ | Ejecutado de punta a punta sin errores; 13 controles con resultado SUPERADO |
| `src/features.py` | ✔ | Variables, objetivos, particiones, preprocesador por *fold* y CLI |
| Protocolo experimental | ✔ | Este documento |
| Particiones temporales compartidas por regresión y clasificación | ✔ | Sección 4; C12 |
| Transformaciones ajustadas solo con el entrenamiento | ✔ | `make_preprocessor`; C9 |
| Solo variables conocidas al momento del pronóstico | ✔ | Secciones 2 y 3; C3 y C10 |
| Dictamen científico registrado | ✔ | Sección 12 (autoauditoría) |
