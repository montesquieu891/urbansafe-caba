# UrbanSafe CABA — Implementation Plan

**Versión:** 2.0  
**Tipo:** Proyecto académico de Data Science aplicado a seguridad vial  
**Modalidad de avance:** secuencial, por hitos verificables y sin fechas predeterminadas.

## Objetivo general

Desarrollar un sistema de inteligencia territorial que permita analizar la siniestralidad vial en la Ciudad Autónoma de Buenos Aires (CABA), anticipar su concentración futura, identificar perfiles de zonas y evaluar estrategias de priorización para la prevención.

El proyecto integrará análisis exploratorio de datos (AED), feature engineering, regresión, clasificación, clustering, optimización de hiperparámetros, interpretabilidad y storytelling.

## 1. Principios del proyecto

1. **Primero, cumplir la consigna académica.** Cada componente obligatorio tendrá evidencia y un entregable reproducible.
2. **La evidencia determina el modelo.** No fijar algoritmos, granularidad espacial ni variables objetivo definitivas antes de auditar los datos.
3. **Predicción no implica causalidad.** Distinguir concentración de siniestros, riesgo ajustado por exposición y efectos de las intervenciones públicas.
4. **Cada experimento necesita un baseline.** Elegir modelos complejos solo si demuestran mejoras fuera de muestra o ventajas relevantes de interpretabilidad y robustez.
5. **Reproducibilidad desde el inicio.** Registrar fuentes, transformaciones, decisiones y resultados.

## 2. Roadmap

1. Delimitación científica.
2. Trabajo de campo y relevamiento.
3. Auditoría de viabilidad.
4. Repositorio, entorno y ETL.
5. AED y análisis espacial.
6. Feature engineering y diseño experimental.
7. Regresión supervisada.
8. Clasificación supervisada.
9. Clustering no supervisado.
10. Integración y robustez.
11. Storytelling y presentación.
12. Validación final y entrega.

## 3. Desarrollo detallado por etapas

### Paso 01. Delimitación científica y definición del problema

**Propósito:** establecer qué fenómeno se desea explicar o predecir y qué decisiones podrían mejorar con los resultados.

**Actividades:**

1. Formular la pregunta principal y las preguntas secundarias.
2. Diferenciar ocurrencia, frecuencia, gravedad y exposición al tránsito.
3. Delimitar CABA como territorio de estudio.
4. Identificar destinatarios: planificación vial, gestión pública e investigación.
5. Formular hipótesis contrastables sin anticipar resultados.
6. Especificar las decisiones que podría informar el sistema.

**Preguntas centrales:** ¿Podemos anticipar concentraciones territoriales? ¿Qué información aporta la infraestructura vial? ¿Existen perfiles territoriales diferenciados? ¿Cuánto mejora la selección de zonas respecto de usar solamente su historial?

**Entregable:** `docs/research_proposal.md`.

**Criterio de aceptación:** preguntas, objetivos, hipótesis y utilidad claramente definidos.

### Paso 02. Trabajo de campo y relevamiento de fuentes

**Propósito:** construir un inventario de fuentes potencialmente útiles y documentar sus restricciones.

| Fuente | Información buscada | Tratamiento |
|---|---|---|
| [Siniestros viales de CABA](https://data.buenosaires.gob.ar/ar/dataset/victimas-siniestros-viales) | Hechos, víctimas, fechas y ubicaciones | Obligatoria |
| [Barrios y comunas](https://data.buenosaires.gob.ar/dataset/barrios) | Polígonos geográficos | Obligatoria |
| [Red vial y callejero](https://data.buenosaires.gob.ar/dataset/calles) | Geometría y atributos de las vías | Prioritaria |
| [Volumen vehicular](https://data.buenosaires.gob.ar/es/dataset/volumen_vehicular) | Conteos por ubicación y período | Enriquecimiento |
| [Conteos peatonales](https://data.buenosaires.gob.ar/dataset/conteos-peatonales) | Exposición peatonal | Complementaria |
| Observatorio de Movilidad y Seguridad Vial | Series históricas, metodología e intervenciones | Investigación directa |

Para cada archivo, documentar período, cobertura, granularidad, identificadores, variables, valores faltantes, licencia y actualización.

Contactar al organismo responsable para consultar: series anteriores comparables, criterios de inclusión/exclusión de siniestros, datos históricos de tránsito, metodología de identificación de zonas críticas y registros georreferenciados y fechados de intervenciones viales.

**Entregables:** `docs/data_inventory.md`, `docs/source_register.csv` y registro de la consulta institucional.

**Criterio de aceptación:** fuentes primarias identificadas y limitaciones explícitas. La respuesta institucional no es un requisito para continuar.

### Paso 03. Auditoría de viabilidad empírica

**Propósito:** determinar qué preguntas pueden responderse con los datos disponibles. **Es el hito decisivo antes del modelado.**

**Controles:**

1. Cantidad de registros por año y mes.
2. Duplicados y relaciones entre hechos y víctimas.
3. Coordenadas faltantes e inválidas.
4. Consistencia de barrios y comunas.
5. Cambios metodológicos entre años.
6. Distribución territorial de observaciones.
7. Porcentaje de unidades sin siniestros (zero inflation).
8. Desbalance de variables objetivo candidatas.
9. Cobertura y representatividad de los conteos vehiculares.
10. Cantidad efectiva de observaciones tras construir el panel.

Comparar inicialmente las escalas **barrio × mes** y **comuna × mes**. Considerar grillas más pequeñas únicamente si lo justifica la densidad de eventos. Evaluar también si resulta preferible una agregación trimestral.

**Entregables:** `notebooks/00_data_audit.ipynb` e informe de viabilidad.

**Criterio de aceptación:** unidad de análisis, período, objetivos y restricciones elegidos sobre evidencia.

### Paso 04. Repositorio, ambiente y ETL

**Propósito:** construir una base reproducible para el trabajo posterior.

**Actividades:** configurar GitHub, entorno virtual de Python, dependencias y `.gitignore`; organizar datos brutos y procesados; documentar el esquema; desarrollar ETL que estandarice categorías y fechas, controle duplicados, preserve identificadores de hechos, valide coordenadas y construya el panel completo zona-período.

No eliminar indiscriminadamente registros incompletos. Justificar exclusiones e imputaciones y preservar trazabilidad.

**Entregables:** repositorio, `requirements.txt`, `src/data_processing.py`, dataset procesado y diccionario de datos.

**Criterio de aceptación:** otra persona puede reconstruir los datos procesados desde las fuentes usando el README.

### Paso 05. AED y análisis territorial

**Propósito:** interpretar patrones relevantes, no producir solo gráficos.

**Análisis:**

1. Evolución temporal, tendencias y estacionalidad.
2. Distribución territorial de siniestros.
3. Participación de peatones, motociclistas, ciclistas y automovilistas.
4. Patrones por horarios y días.
5. Concentración espacial y persistencia de hotspots.
6. Comparación de períodos, incluida la pandemia.
7. Relaciones con infraestructura vial disponible.
8. Faltantes y posibles sesgos de registro.

Utilizar **Pandas** como herramienta central para exploración y visualizaciones, complementado por Matplotlib, Seaborn y GeoPandas cuando sea necesario.

**Entregables:** `notebooks/01_EDA.ipynb`, figuras y síntesis de hallazgos.

**Criterio de aceptación:** cada hallazgo relevante contiene evidencia, interpretación y limitaciones.

### Paso 06. Feature engineering y diseño experimental

**Propósito:** crear variables predictoras y definir la evaluación fuera de muestra.

| Familia | Variables candidatas |
|---|---|
| Histórica | Rezagos de 1, 2, 3 y 12 períodos; medias móviles y tendencias |
| Temporal | Mes, trimestre y estacionalidad |
| Territorial | Barrio, superficie, vecindad y densidades históricas |
| Infraestructura | Longitud de vías, proporción de avenidas e intersecciones |
| Composición | Proporciones históricas de actores viales |
| Exposición | Conteos comparables de tránsito, si son válidos |

Definir particiones temporales compartidas por regresión y clasificación. Dentro de cada fold, ajustar transformaciones, imputaciones, selección de variables y escalado **solo con entrenamiento**. Usar exclusivamente variables conocidas al momento del pronóstico.

**Entregables:** `notebooks/02_feature_engineering.ipynb`, `src/features.py` y protocolo experimental.

**Criterio de aceptación:** pruebas de integridad temporal y controles de leakage superados.

### Paso 07. Regresión supervisada

**Pregunta:** ¿cuántos siniestros ocurrirán en una zona durante el próximo período?

Comparar baseline de persistencia histórica, regresión Poisson, binomial negativa (si existe sobredispersión) y un modelo de árboles. Optimizar hiperparámetros con validación temporal expansiva.

**Evaluación:** MAE, devianza adecuada, sesgo, errores por territorio y estabilidad por subperíodo. Incorporar incertidumbre cuando sea factible.

**Entregable:** `notebooks/03_regression.ipynb`.

**Criterio de aceptación:** comparación reproducible, modelo seleccionado con justificación y test fuera de muestra.

### Paso 08. Clasificación supervisada

**Pregunta:** ¿qué zonas superarán un umbral de concentración de siniestros durante el próximo período?

Definir el umbral sin consultar el test. Comparar baseline, regresión logística, Random Forest y Gradient Boosting/XGBoost. Examinar ponderación de clases y, solo cuando sea pertinente, SMOTE dentro de los folds de entrenamiento.

**Evaluación:** matriz de confusión, precision, recall, F1, PR-AUC, calibración y Precision@K. Optimizar hiperparámetros y umbral de decisión con validación, sin utilizar test para decidir.

Aplicar SHAP al modelo seleccionado para explicar patrones predictivos, **sin hacer afirmaciones causales**.

**Entregable:** `notebooks/04_classification.ipynb`.

**Criterio de aceptación:** clasificador seleccionado por métricas, estabilidad y utilidad territorial.

### Paso 09. Clustering no supervisado

**Pregunta:** ¿qué perfiles de siniestralidad distinguen a las zonas de CABA?

Construir atributos históricos de frecuencia, estacionalidad, distribución horaria y composición de los siniestros. Probar K-Means y clustering jerárquico; evaluar DBSCAN/HDBSCAN si el objetivo espacial y los datos lo justifican.

**Evaluación:** silhouette, estabilidad, separación de grupos, sensibilidad al escalado e interpretabilidad. El clustering no debe incorporar resultados futuros como features.

**Entregable:** `notebooks/05_clustering.ipynb`.

**Criterio de aceptación:** grupos caracterizados, alternativas comparadas y selección argumentada.

### Paso 10. Integración, robustez y utilidad pública

**Propósito:** evaluar el sistema como una ayuda para la priorización territorial, no como tres ejercicios aislados.

Comparar la priorización de modelos contra una estrategia basada solo en el historial. Medir cobertura de siniestros futuros entre las K zonas seleccionadas. Evaluar sensibilidad a períodos, granularidad espacial y features. Analizar incertidumbre y sesgos territoriales.

Cuando existan mediciones comparables, incorporar un análisis separado de exposición vehicular por corredor. **No extrapolar sensores aislados a toda CABA.**

**Entregables:** `notebooks/06_integrated_evaluation.ipynb` e informe de robustez.

**Criterio de aceptación:** documentar cuándo supera baselines, cuándo no y qué decisiones puede informar razonablemente.

### Paso 11. Storytelling y presentación

**Narrativa:** problema público → datos → patrones históricos → modelos → validación → perfiles territoriales → priorización → conclusiones y limitaciones.

Generar mapas, comparativas y explicaciones interpretables para audiencias no técnicas. Una aplicación web será **opcional**, posterior a completar la entrega académica.

**Entregables:** `notebooks/07_storytelling.ipynb`, presentación e informe final.

**Criterio de aceptación:** comunicar claramente el problema, la evidencia, los resultados y sus límites.

### Paso 12. Validación final y entrega

Ejecutar el proyecto desde un entorno limpio; verificar trazabilidad de fuentes y decisiones; reproducir métricas y figuras; comprobar que todos los notebooks funcionen en orden y que el README sea suficiente.

**Entregables:** repositorio, documentación, notebooks, modelos, figuras y presentación.

**Criterio de aceptación:** cumplimiento completo de la consigna, reproducibilidad y conclusiones respaldadas por evidencia.

## 4. Matriz de cumplimiento académico

| Requisito del curso | Evidencia prevista |
|---|---|
| Elección del tema y objetivo | Paso 01 — propuesta |
| Investigación y selección de datasets | Pasos 02–03 — inventario y auditoría |
| Repositorio y ambiente | Paso 04 — GitHub, entorno y README |
| AED, transformación y visualización con Pandas | Pasos 04–05 — notebooks y gráficos |
| Feature engineering | Paso 06 — variables documentadas |
| Modelo de regresión supervisada | Paso 07 — entrenamiento y evaluación |
| Modelo de clasificación supervisada | Paso 08 — entrenamiento y evaluación |
| Tuning y prevención del overfitting | Pasos 06–08 — validación temporal y comparación |
| Clustering y mejora | Paso 09 — algoritmos y criterios explícitos |
| Storytelling y presentación de resultados | Pasos 10–11 — informe y exposición |

## 5. Bibliografía de referencia

1. Ahmed et al. (2023). *A study on road accident prediction and contributing factors using explainable machine learning models: analysis and performance*. Transportation Research Interdisciplinary Perspectives. https://doi.org/10.1016/j.trip.2023.100814. **Uso:** ensembles, desbalance e interpretabilidad con SHAP.
2. Affou et al. (2026). *Advances in Traffic Accident Prediction: A Survey of Novel Approaches*. Urban Science. https://doi.org/10.3390/urbansci10070349. **Uso:** predicción temporal/espacio-temporal, variables y metodologías.
3. Kotsyubynska et al. (2026). *Machine Learning and Deep Learning for Predicting Traffic Crash Injury Severity: A Systematic Review and Meta-Analysis (2014–2025)*. Journal of Road Safety. https://doi.org/10.33492/JRS-D-26-1-2721386. **Uso:** métricas para clases minoritarias, riesgo de sesgo y validación.

**Nota:** los estudios centrados en gravedad de accidentes no verifican por sí mismos la capacidad de pronosticar concentración territorial futura; sirven principalmente como referencias metodológicas.

## 6. Priorización y control de alcance

**Núcleo obligatorio:** ETL, AED, feature engineering, regresión, clasificación, clustering, tuning, validación, storytelling y documentación.

**Diferenciadores prioritarios:** análisis geográfico, evaluación temporal, métricas de priorización, interpretabilidad y robustez.

**Extensiones condicionadas:** exposición vehicular, meteorología, SHAP avanzado, dashboard web, simulación presupuestaria y deep learning.

Una extensión se pospone si exige datos no disponibles o compromete el núcleo académico.

### Extensión final. Pronóstico de lluvia y siniestralidad a corto plazo

Implementar después de la entrega académica como una vista del Centro de monitoreo para las próximas 24 horas. El pronóstico principal conserva su escala barrio × mes y su horizonte t+1 mes.

- [ ] **Cruce histórico de lluvia y siniestros.** Empezar con precipitación observada o estimada históricamente en CABA, documentando fuente, resolución y cobertura. Alinear con los hechos con víctimas por fecha, franja horaria y zona compatible. Construir un panel con todas las franjas cubiertas, incluidas las que registran cero hechos. Comparar hechos por hora con y sin lluvia y por intensidad. Informar diferencias absolutas y relativas, número de horas y hechos, e incertidumbre. Comparar franjas equivalentes por horario, día de la semana y estación, y explicitar los límites por cambios de movilidad y cobertura. Interpretar el resultado como asociación en la frecuencia registrada. Para el experimento predictivo posterior, usar pronósticos archivados disponibles al corte.
- [ ] **Capa meteorológica.** Consultar [Open-Meteo](https://open-meteo.com/en/docs) para mostrar por franja la probabilidad de lluvia y la precipitación pronosticada. Indicar la fuente, la fecha de emisión, la vigencia y el estado sin datos.
- [ ] **Viabilidad del cruce.** Verificar cobertura en CABA, resolución espacial, solapamiento con los registros viales y densidad de hechos por barrio y franja. Alinear la fecha y hora en la zona horaria local. Para la evaluación retrospectiva, usar [pronósticos archivados](https://open-meteo.com/en/docs/historical-forecast-api) emitidos antes de cada corte.
- [ ] **Evaluación fuera de muestra.** Comparar un modelo de historial y calendario con una versión que añade la precipitación pronosticada. Usar las mismas particiones temporales y evaluar si el clima mejora la estimación de al menos un siniestro con víctimas en la unidad elegida. Comprobar la calibración.
- [ ] **Presentación en la web.** Mostrar por separado la probabilidad de lluvia y la probabilidad estimada de siniestro. Habilitar esta última si el modelo con clima demuestra una mejora fuera de muestra y una calibración adecuada. Si la evidencia es insuficiente, mantener la lluvia como capa informativa.

## 7. Seguimiento del proyecto

- [x] 01. Delimitación científica. Ver `docs/research_proposal.md`, aprobado por el responsable el 2026-11-10.
- [x] 02. Trabajo de campo y relevamiento. Ver `docs/data_inventory.md`, `docs/source_register.csv` y `docs/institutional_inquiry.md` (consulta en borrador, no enviada). Aprobado por el responsable el 2026-11-10.
- [x] 03. Auditoría de viabilidad. Ver `notebooks/00_data_audit.ipynb` y `docs/feasibility_report.md` (D1–D11), con las correcciones de revisión registradas. Aprobado por el responsable el 2026-11-10.
- [x] 04. Repositorio, entorno y ETL. Ver `README.md`, `src/data_processing.py`, `tests/` y `docs/data_dictionary.md`; repo privado montesquieu891/urbansafe-caba. Aprobado por el responsable el 2026-11-10.
- [x] 05. AED y análisis territorial. Ver `notebooks/01_EDA.ipynb` y `docs/eda_findings.md` (E1–E10). Aprobado por el responsable el 2026-11-10.
- [x] 06. Feature engineering y diseño experimental. Ver `notebooks/02_feature_engineering.ipynb`, `src/features.py` y `docs/experimental_protocol.md` (dictamen: aprobado con condiciones). Aprobado por el responsable el 2026-11-10.
- [x] 07. Regresión supervisada. Ver `notebooks/03_regression.ipynb` y `docs/regression_report.md` (no mejora a la media de 12 meses; dictamen aprobado). Aprobado por el responsable el 2026-11-10.
- [x] 08. Clasificación supervisada. Ver `notebooks/04_classification.ipynb` y `docs/classification_report.md` (mejora marginal no relevante frente a la media de 12 meses; dictamen aprobado). Aprobado por el responsable el 2026-11-10.
- [x] 09. Clustering no supervisado. Ver `notebooks/05_clustering.ipynb` y `docs/clustering_report.md` (perfil robusto de borde; subdivisión interior débil; dictamen aprobado). Aprobado por el responsable el 2026-11-10.
- [x] 10. Integración y robustez. Ver `notebooks/06_integrated_evaluation.ipynb` y `docs/robustness_report.md` (el historial capta el 92 % de la ganancia posible; veredicto H1–H8; dictamen aprobado). Aprobado por el responsable el 2026-11-10.
- [x] 11. Storytelling y presentación. Ver `notebooks/07_storytelling.ipynb`, `docs/final_report.md` y `presentation/` (deck de 13 diapositivas). Aprobado por el responsable el 2026-11-10.
- [x] 12. Validación final y entrega. Ver `docs/final_validation.md` (reproducción en sala limpia; dictamen apto con condiciones), `models/` y PR #1 fusionado en `main`. Aprobado por el responsable el 2026-11-10.

Para marcar un hito como completado deben estar disponibles sus entregables y haberse satisfecho sus criterios de aceptación.

## 8. Primera ejecución

Comenzar por el **Paso 01**, seguido del relevamiento de fuentes y la auditoría de viabilidad. La elección definitiva de escala geográfica, horizonte predictivo y umbral de clasificación depende de la evidencia del **Paso 03**.

**Resultado final esperado:** cumplir íntegramente la consigna y determinar con evaluación fuera de muestra si los datos históricos de CABA permiten mejorar la priorización territorial frente a métodos sencillos.
