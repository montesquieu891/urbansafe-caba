# UrbanSafe CABA — Informe final

**¿Dónde prevenir siniestros viales en la Ciudad de Buenos Aires el mes que viene?**

**Proyecto académico de Data Science · Fecha:** 2026-11-10  
**Repositorio:** `montesquieu891/urbansafe-caba` (privado) · **Reproducción:** [README](../README.md)  
**Narrativa visual:** [notebooks/07_storytelling.ipynb](../notebooks/07_storytelling.ipynb) · figuras en [reports/figures/07_storytelling/](../reports/figures/07_storytelling/)

---

## Resumen ejecutivo

- **Problema.** En CABA ocurren alrededor de 10.000 siniestros con víctimas por año (11.752 en 2025, dato posiblemente provisorio). Moto y peatón explican el **81 % de los siniestros mortales**.
- **Pregunta.** ¿Los datos abiertos permiten anticipar en qué barrios se concentrarán los siniestros del mes siguiente, y mejorar así la priorización frente al historial?
- **Respuesta.** La siniestralidad registrada es **concentrada y persistente**.
  - Priorizar cada mes los **10 barrios con más siniestros en los últimos 12 meses** cubre el **43 %** de los siniestros del mes siguiente. Conociendo el futuro se cubriría el 45 %.
  - **Los modelos de machine learning** (Poisson, binomial negativa, *boosting*, regresión logística, *random forest*) **no superan de forma relevante a ese historial**. Mejoran a "repetir el mes anterior", pero no al promedio de 12 meses.
- **Perfiles.** Un grupo de **barrios de borde** sobre la General Paz y las autopistas tiene un perfil propio: vías rápidas, autos y motos. El interior se divide, de forma más débil, en un perfil central (peatones, transporte público) y otro residencial (motos, bicicletas).
- **Límites.** Contamos **carga registrada**, no riesgo: no hay datos de tránsito para toda la ciudad. Donde existen mediciones (95 corredores en 2024), ajustar por volumen cambia el orden de prioridad del 43 % de los puntos. El análisis es predictivo, **no causal**.

## 1. Problema público y alcance

La prevención vial compite por recursos finitos: auditorías, rediseño de intersecciones, controles y campañas. El proyecto evalúa si un sistema basado en datos abiertos puede **ordenar los barrios** para el mes siguiente mejor que la práctica simple de mirar el historial.

| Aspecto | Definición | Documento |
|---|---|---|
| Propuesta, preguntas e hipótesis H1–H8 | Frecuencia y concentración, no gravedad individual ni causalidad | [research_proposal.md](research_proposal.md) |
| Fuentes | Siniestros viales 2019–2025 (OMSV, 65.818 hechos y 75.197 víctimas), límites, callejero y conteos 2024 | [data_inventory.md](data_inventory.md) y [source_register.csv](source_register.csv) |
| Viabilidad | **Barrio × mes**, t+1, test 2025; objetivo: hechos por barrio-mes y top 10 mensual (D1–D11) | [feasibility_report.md](feasibility_report.md) |
| Datos procesados | ETL reproducible con verificación SHA-256 y 18 invariantes | [data_dictionary.md](data_dictionary.md) |

## 2. Qué muestran los datos (AED)

Hallazgos principales de [eda_findings.md](eda_findings.md):
1. **Tendencia y estacionalidad.** Se recuperó el nivel previo a la pandemia. Enero es el mes más bajo (índice 0,75) y octubre el más alto (1,10).
2. **Usuarios afectados.** Moto (43–46 % de los hechos) y peatón (16–18 %). El peatón tiene la mayor proporción de siniestros graves o mortales (10,7 %).
3. **Horario.** La frecuencia es diurna (pico a las 17 h). La gravedad es nocturna: entre las 0 y las 5 h, la proporción de graves o mortales es 2,1 veces la del resto del día.
4. **Concentración espacial.** Los barrios densos se agrupan en el centro (I de Moran 0,47). **El 68 % del top 10 se repite el mes siguiente.**
5. **Pandemia.** Cambió el nivel y el modo (más bicicleta), pero no la geografía.
6. **Avenidas.** Concentran el 64 % de los hechos con el 23,5 % de los kilómetros.
7. **Calidad del registro.** Los graves pierden la coordenada entre el 6 % y el 28 % de las veces según el año, así que la gravedad territorial solo se usa de forma descriptiva.

## 3. Modelos y validación

**Diseño experimental** ([experimental_protocol.md](experimental_protocol.md)):
- Variables solo con información disponible al momento del pronóstico, incluidas las etiquetas de entrenamiento (control C13).
- Validación temporal expansiva (2022, 2023 y 2024) y test 2025 congelado.
- Criterios de mejora fijados antes de modelar.
- Trece controles de fuga superados. Una fuga de etiquetas en la sensibilidad a la latencia se detectó en una revisión externa, se corrigió y quedó registrada.

| Tarea | Modelo seleccionado | Mejor baseline | Resultado en test 2025 | ¿Mejora relevante? |
|---|---|---|---|---|
| **Regresión**: hechos por barrio el mes siguiente ([regression_report.md](regression_report.md)) | Poisson L2 | Media de 12 meses | MAE 4,07 frente a 4,06 (IC de ΔMAE [−0,13; 0,14]) | **No.** Sí frente a la persistencia (ΔMAE −1,0) |
| **Clasificación**: top 10 del mes siguiente ([classification_report.md](classification_report.md)) | Regresión logística L2 | Ranking por media de 12 meses | P@10 0,808 frente a 0,792 (2 aciertos más en 120; IC [−0,02; 0,06]) | **No** (por debajo del umbral de 0,02) |
| **Clustering** de perfiles ([clustering_report.md](clustering_report.md)) | K-Means, k = 2 (+ nivel k = 3) | — | Borde frente a interior: *silhouette* 0,33, estable | Perfil de borde robusto; subdivisión débil |

**Interpretabilidad.** El clasificador se apoya en el historial del barrio (41 %) y en el historial relativo (34 %); en la práctica es una "persistencia refinada". La importancia de las variables describe patrones predictivos, no causas.

## 4. Utilidad para la priorización (evaluación integrada)

Ver [robustness_report.md](robustness_report.md).

| K barrios | Azar | **Historial (12 meses)** | Mejor modelo | Techo (oráculo) |
|---|---|---|---|---|
| 5 | 10 % | **26 %** | 26 % | 27 % |
| 10 | 21 % | **43 %** | 43 % | 45 % |
| 15 | 31 % | **56 %** | 56 % | 58 % |

- **El historial capta el 92 % de la ganancia posible sobre el azar.** La conclusión se mantiene con la validación retrospectiva 2024, con otras definiciones de empate, con mayor latencia de los datos y con otras escalas.
- **Escala.** Barrio × trimestre es la más estable. Las escalas finas (grilla de 1 km) tienen más ceros y menos estabilidad.
- **Sesgo del criterio.** Los barrios de borde tienen el 16 % de los hechos pero reciben el 8–10 % de las selecciones del top 10, porque su carga está repartida. Priorizar por conteo de barrio subrepresenta las vías rápidas.

## 5. Veredicto sobre las hipótesis

| Hipótesis | Veredicto |
|---|---|
| H1. Concentración y persistencia | **Respaldada** |
| H2. Predicción mejor que la persistencia | Respaldada frente a la persistencia; **no** frente a la media de 12 meses |
| H3. Aporte de la infraestructura | **No contrastable** (sin infraestructura con vigencia verificable) |
| H4. Detección del top 10 | **No respaldada** frente al mejor baseline |
| H5. Valor para la priorización | **No respaldada** |
| H6. Perfiles territoriales | **Parcialmente respaldada** |
| H7. Dependencia de la escala | **Parcialmente respaldada** |
| H8. Exposición | **Respaldada en los corredores con sensor (2024)** |

## 6. Recomendaciones

1. **Priorización mensual.** Usar el top 10 de barrios por media de 12 meses: es simple, transparente y prácticamente óptimo con estos datos.
2. **Tipo de prevención según el perfil:**
   - barrios de borde: vías rápidas y conductores;
   - barrios centrales: peatones y transporte público en avenidas;
   - barrios residenciales: motociclistas y ciclistas.
3. **No limitar la priorización al conteo por barrio.** Agregar criterios de **corredor** (avenidas y vías rápidas) y, donde haya medición, de **tasa por vehículo**.
4. **Mejorar los datos.** Datos de tránsito con cobertura de toda la ciudad, historial fechado de infraestructura e intervenciones, y geocodificación completa de los siniestros graves. La consulta al Observatorio está redactada pero **no fue enviada** ([institutional_inquiry.md](institutional_inquiry.md)).

## 7. Limitaciones

- **Fuente.** Solo hay siniestros con víctimas de origen policial. Puede haber subregistro y cambios de registro (fines de 2019; gravedad variable entre años). 2025 podría ser provisorio.
- **Exposición.** No hay exposición por zona, así que no se puede hablar de riesgo por persona ni por vehículo.
- **Causalidad.** El diseño es predictivo: no se infieren causas ni efectos de políticas.
- **Potencia.** El test tiene solo 12 meses: las diferencias pequeñas no son concluyentes.
- **Revisiones.** Las de los Pasos 06 a 10 fueron autoauditorías, salvo correcciones externas puntuales. **Se recomienda una revisión independiente** antes de la entrega.

## 8. Trazabilidad

| Paso | Notebook o código | Informe |
|---|---|---|
| 03 Viabilidad | `notebooks/00_data_audit.ipynb` | `docs/feasibility_report.md` |
| 04 ETL | `src/data_processing.py` y `tests/` | `docs/data_dictionary.md` |
| 05 AED | `notebooks/01_EDA.ipynb` | `docs/eda_findings.md` |
| 06 Variables | `notebooks/02_feature_engineering.ipynb` y `src/features.py` | `docs/experimental_protocol.md` |
| 07 Regresión | `notebooks/03_regression.ipynb` y `src/regression.py` | `docs/regression_report.md` |
| 08 Clasificación | `notebooks/04_classification.ipynb` y `src/classification.py` | `docs/classification_report.md` |
| 09 Clustering | `notebooks/05_clustering.ipynb` y `src/profiles.py` | `docs/clustering_report.md` |
| 10 Integración | `notebooks/06_integrated_evaluation.ipynb` | `docs/robustness_report.md` |
| 11 Comunicación | `notebooks/07_storytelling.ipynb` | Este informe y la presentación |

**Bibliografía verificada.**
- Ahmed et al. (2023), *Transportation Research Interdisciplinary Perspectives*, 19, 100814.
- Affou et al. (2026), *Urban Science*, 10(7), 349.
- Kotsyubynska et al. (2026), *Journal of Road Safety*, 37(1), 46–60.

El detalle está en la [propuesta](research_proposal.md).
