# UrbanSafe CABA — Propuesta de investigación

**Hito:** Paso 01. Delimitación científica y definición del problema  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Documentos de referencia:** [plan de implementación](../UrbanSafe_CABA_Implementation_Plan.md), [AGENTS.md](../AGENTS.md) y [bibliografía local](../bibliografia/)

> **Alcance.** Este documento define el problema, las preguntas, los objetivos y las hipótesis. No inventaría fuentes de datos (Paso 02). Tampoco audita su viabilidad (Paso 03) ni elige modelos o hiperparámetros (Pasos 06–09). Las afirmaciones sobre los datos de CABA son **supuestos pendientes** hasta su verificación (sección 9).

---

## 1. Problema público

La siniestralidad vial es un problema de salud pública con costos humanos, sanitarios y económicos. La OMS documentó 1,19 millones de muertes por siniestros viales en 2021. Peatones, ciclistas y motociclistas representan el 53 % de esas muertes (WHO, 2024, citado en Kotsyubynska et al., 2026, p. 47). En una ciudad densa como CABA, la prevención compite por recursos finitos: auditorías de seguridad vial, rediseño de intersecciones, control, señalización y campañas. Por eso no alcanza con saber **dónde ocurrieron** los siniestros. También importa saber **dónde es razonable esperar que se concentren en el período siguiente** y si esa anticipación **mejora la priorización** frente a mirar el historial.

La gestión reactiva interviene después de que una zona acumula siniestros. Esto expone a un sesgo conocido. Las zonas elegidas por un pico de siniestros tienden a registrar menos en el período siguiente aunque no se intervenga (**regresión a la media**). En consecuencia, una selección ingenua puede sobrestimar el problema o atribuir mejoras inexistentes a una intervención. La literatura de identificación de puntos críticos usa métodos como el Bayes empírico para corregir este fenómeno (Affou et al., 2026, p. 13). Este proyecto no estima efectos de intervenciones. Sin embargo, el sesgo justifica comparar toda priorización propuesta contra un baseline basado solo en el historial y evaluarla fuera de muestra.

**Problema de investigación.** No está establecido si los datos abiertos de CABA permiten anticipar, fuera de muestra y a escala zonal, la concentración futura de siniestros viales mejor que una regla basada solo en el historial de cada zona. Tampoco está claro si una anticipación así aportaría información útil para priorizar la prevención.

## 2. Destinatarios y decisiones que podría informar

| Destinatario | Decisión que podría informar | Qué **no** debería decidir con este sistema |
|---|---|---|
| Planificación vial y gestión pública de movilidad (organismos del GCBA) | Ordenar zonas para auditorías de seguridad vial o inspecciones con capacidad limitada (top-*K*); elegir dónde profundizar diagnósticos por corredor o intersección | Atribuir causas a una zona o afirmar que una intervención "funcionó" |
| Gestión operativa (control, campañas, comunicación) | Focalizar campañas por perfil territorial: horario, actores viales predominantes y estacionalidad | Asignar recursos solo por un pronóstico puntual sin incertidumbre |
| Observatorio y equipos técnicos | Comparar la priorización actual con una alternativa reproducible; detectar zonas con cambio de comportamiento | Reemplazar la metodología oficial sin validación institucional |
| Investigación académica | Evidencia reproducible sobre predictibilidad territorial, escala y baselines en una ciudad latinoamericana | Generalizar resultados a otras ciudades sin revalidar (transferibilidad limitada; Affou et al., 2026, p. 39) |

**Utilidad esperada.** El sistema funciona como un **instrumento de cribado y priorización territorial**. Ordena zonas y describe perfiles con métricas de desempeño e incertidumbre explícitas. Su valor se juzgará con una pregunta operativa: ¿qué proporción de los siniestros del período siguiente cae en las *K* zonas seleccionadas, frente a la selección por historial? Un resultado negativo también tiene utilidad. Si el modelo no supera al historial, la recomendación será priorizar con el historial y documentar por qué.

## 3. Delimitación

### 3.1 Territorio

- **Ámbito:** Ciudad Autónoma de Buenos Aires, dentro de su límite jurisdiccional. Los siniestros ubicados fuera del polígono de CABA o sin georreferenciación válida no se asignan a zonas. Su tratamiento (exclusión, asignación a la comuna informada o análisis aparte) se decidirá en los Pasos 03–04, con trazabilidad.
- **Zonas candidatas:** barrios y comunas oficiales (Paso 03). La cantidad de unidades se confirmará con las capas oficiales en el Paso 02. Una grilla regular solo se considerará si la densidad de eventos lo justifica (plan, Paso 03).
- **Fuera de alcance:** el Área Metropolitana (AMBA), la red de autopistas como sistema propio si la fuente no la distingue y el nivel de segmento o intersección. Este último podrá usarse en un análisis complementario por corredor (Paso 10).

### 3.2 Período

Se delimitará con la cobertura efectiva de la fuente (Paso 03). Se anticipan dos problemas. El primero es la **pandemia de COVID-19**, que alteró la movilidad. Ahmed et al. (2023, p. 7) observan una caída marcada de siniestros durante el confinamiento en Nueva Zelanda. El segundo son los posibles **cambios metodológicos de registro** entre años. Ambos condicionan el diseño de las particiones temporales.

### 3.3 Distinciones conceptuales

| Concepto | Definición operativa en UrbanSafe | Medida típica | Qué permite afirmar | Qué **no** permite afirmar |
|---|---|---|---|---|
| **Ocurrencia** | Que se registre al menos un siniestro en una zona y un período | Indicador binario por zona y período | Presencia o ausencia de eventos registrados | Magnitud ni riesgo |
| **Frecuencia** | Cantidad de siniestros (o víctimas, según la auditoría) registrados en una zona y un período | Conteo; variable objetivo de la regresión (Paso 07) | Carga absoluta de siniestralidad registrada | Que la zona sea "más peligrosa" por unidad de uso |
| **Gravedad** | Consecuencia del siniestro sobre las personas: lesiones leves, graves o víctimas fatales | Proporción o conteo de siniestros graves o fatales; ponderación por gravedad | Severidad de la carga | Probabilidad de ocurrencia de nuevos siniestros |
| **Concentración territorial** | Grado en que la frecuencia se acumula en pocas zonas y persiste entre períodos | Participación del top-*K*, curvas de concentración, superación de umbral (Paso 08) | Dónde se acumula la carga registrada | Riesgo ajustado ni causas |
| **Exposición** | Cantidad de uso del espacio vial: vehículos, peatones, kilómetros recorridos | Conteos vehiculares o peatonales comparables | Denominador para normalizar | Nada por sí sola sobre seguridad |
| **Riesgo ajustado por exposición** | Frecuencia por unidad de exposición | Tasa = siniestros / exposición, solo donde la exposición sea medida y comparable | Peligrosidad relativa por unidad de uso | Extrapolación a zonas sin medición (el plan prohíbe extrapolar sensores aislados a toda CABA) |
| **Efecto causal** | Cambio en la siniestralidad atribuible a un factor o a una intervención | Requiere diseño causal: grupo de comparación, corrección de regresión a la media y registros fechados de intervenciones | Impacto de una política | — Fuera del alcance predictivo del proyecto |

**Consecuencias para el proyecto.**

1. El objetivo principal es **frecuencia y concentración**, no riesgo ajustado. Una zona puede concentrar siniestros porque concentra tránsito. Los rankings por conteo se presentarán como **carga registrada** y no como peligrosidad.
2. El **riesgo ajustado por exposición** es una extensión condicionada. Solo se calculará en corredores o puntos con conteos comparables y en un análisis separado (Paso 10).
3. La **gravedad** es una dimensión descriptiva y una posible variable objetivo alternativa, según la auditoría. **No** se construirá un clasificador de gravedad de siniestros individuales, porque responde a otra pregunta (sección 7).
4. La importancia de variables y los valores SHAP describen **patrones predictivos**, no efectos causales (plan, Paso 08; Affou et al., 2026, p. 39).

## 4. Preguntas de investigación

### 4.1 Pregunta principal

> **¿En qué medida la información histórica, temporal, territorial y de infraestructura vial disponible en fuentes abiertas permite anticipar, fuera de muestra, la frecuencia y la concentración de siniestros viales por zona de CABA en el período siguiente, y mejorar la priorización territorial frente a una estrategia basada solo en el historial de cada zona?**

### 4.2 Preguntas secundarias

| Código | Pregunta | Pregunta central del plan | Paso |
|---|---|---|---|
| PS1 | ¿Cómo se distribuye la siniestralidad registrada en el espacio y en el tiempo (tendencia, estacionalidad, horario, actores viales)? ¿Cuán concentrada y persistente es entre períodos, incluida la pandemia? | ¿Podemos anticipar concentraciones territoriales? | 05 |
| PS2 | ¿Con qué error se pronostica la cantidad de siniestros por zona en el período siguiente? ¿Supera ese error al baseline de persistencia histórica? | ¿Podemos anticipar concentraciones territoriales? | 06–07 |
| PS3 | ¿Con qué precisión, *recall* y calibración se identifican las zonas que superarán un umbral de concentración en el período siguiente? | ¿Podemos anticipar concentraciones territoriales? | 06, 08 |
| PS4 | ¿Qué información predictiva **incremental** aporta la infraestructura vial (longitud de vías, proporción de avenidas, intersecciones) sobre el historial y la estructura temporal? *(Condicionada tras el Paso 03: requiere infraestructura con vigencia verificable en cada fecha de corte; ver D11 del informe de viabilidad.)* | ¿Qué información aporta la infraestructura vial? | 06–08 |
| PS5 | ¿Existen perfiles territoriales de siniestralidad diferenciados, interpretables y estables (frecuencia, estacionalidad, distribución horaria y composición de actores)? | ¿Existen perfiles territoriales diferenciados? | 09 |
| PS6 | ¿Cuánto cambia la cobertura de siniestros futuros en las *K* zonas priorizadas por un modelo frente a las priorizadas por su historial? ¿Es robusta esa diferencia ante cambios de período, escala espacial y conjunto de variables? | ¿Cuánto mejora la selección respecto del historial? | 10 |
| PS7 *(condicional)* | Donde existan conteos de tránsito comparables, ¿difiere el ordenamiento por frecuencia del ordenamiento por riesgo ajustado por exposición? | Distinción concentración / exposición | 10 |

## 5. Objetivos

**Objetivo general.** Desarrollar y evaluar fuera de muestra un sistema reproducible de inteligencia territorial para CABA. El sistema describirá la siniestralidad vial, anticipará su frecuencia y su concentración por zona, identificará perfiles territoriales y cuantificará si mejora la priorización preventiva frente a métodos sencillos basados en el historial.

**Objetivos específicos.**

| Código | Objetivo específico | Pregunta | Evidencia de cumplimiento (plan) |
|---|---|---|---|
| OE1 | Relevar las fuentes y auditar su viabilidad para elegir, con evidencia, la escala espacial, el período, el horizonte, la variable objetivo y el umbral | Habilita todas | `docs/data_inventory.md`, `notebooks/00_data_audit.ipynb` e informe de viabilidad |
| OE2 | Construir un panel zona-período completo y reproducible desde las fuentes, con trazabilidad de exclusiones e imputaciones | Habilita todas | `src/data_processing.py`, diccionario de datos y README |
| OE3 | Caracterizar patrones temporales, territoriales y por actor vial, con su concentración, persistencia y posibles sesgos de registro | PS1 | `notebooks/01_EDA.ipynb` |
| OE4 | Diseñar variables conocidas al momento del pronóstico y particiones temporales con controles de fuga | PS2–PS4 | `notebooks/02_feature_engineering.ipynb` y protocolo experimental |
| OE5 | Comparar modelos de conteo y clasificación contra baselines de persistencia, con métricas apropiadas para conteos y clases desbalanceadas | PS2–PS4 | `notebooks/03_regression.ipynb` y `04_classification.ipynb` |
| OE6 | Identificar y validar perfiles territoriales sin usar información futura | PS5 | `notebooks/05_clustering.ipynb` |
| OE7 | Evaluar la priorización top-*K*, su robustez y su incertidumbre, y documentar cuándo supera al historial y cuándo no | PS6–PS7 | `notebooks/06_integrated_evaluation.ipynb` e informe de robustez |
| OE8 | Comunicar los resultados y sus límites a audiencias técnicas y no técnicas | Todas | `notebooks/07_storytelling.ipynb`, presentación e informe final |

## 6. Hipótesis contrastables

Las hipótesis se formulan **sin anticipar resultados**. Cada una se contrasta con una alternativa nula explícita. Los umbrales de "mejora relevante" y los criterios estadísticos exactos se fijarán en el protocolo experimental (Paso 06) **antes** de consultar el conjunto de test.

| Código | Hipótesis | Evidencia que la respaldaría | Resultado que la debilitaría | Paso |
|---|---|---|---|---|
| **H1. Concentración y persistencia** | La siniestralidad registrada se concentra en una fracción minoritaria de zonas, y el orden de las zonas persiste entre períodos consecutivos | Participación del top-*K* mayor que la esperada bajo una distribución de referencia (proporcional a superficie o uniforme); correlación de rangos entre períodos positiva y estable, incluso excluyendo la pandemia | Concentración similar a la referencia; correlaciones de rango cercanas a cero o que dependen de un solo subperíodo | 05 |
| **H2. Predictibilidad sobre persistencia** | Un modelo con historial, estacionalidad y atributos territoriales pronostica la frecuencia del período siguiente con menor error que el baseline de persistencia | Menor MAE y devianza en test temporal; mejora consistente en la mayoría de los *folds* y subperíodos; intervalo de incertidumbre de la diferencia que excluye cero | Mejora nula, inconsistente entre *folds* o subperíodos, o dentro del ruido; empeoramiento en zonas de baja frecuencia | 07 |
| **H3. Aporte de la infraestructura** *(condicionada, D11)* | Las variables de infraestructura vial aportan información predictiva **incremental** sobre el historial | Mejora de las métricas fuera de muestra al agregarlas a un modelo que ya incluye historial y temporalidad (comparación anidada) | Sin mejora; o mejora que desaparece al controlar por superficie o volumen histórico, lo que indicaría un proxy de tamaño o exposición | 06–08 |
| **H4. Detección de concentración** | La superación del umbral de concentración en el período siguiente se clasifica mejor que con la regla de persistencia | PR-AUC, *recall* y Precision@K superiores al baseline en validación temporal; calibración aceptable | Desempeño equivalente o inferior al baseline; ventaja que depende del umbral elegido | 08 |
| **H5. Valor para la priorización** | La selección de *K* zonas por modelo captura una proporción mayor de los siniestros del período siguiente que la selección por historial | Cobertura top-*K* superior en la mayoría de los períodos de test y para varios valores de *K*; diferencia robusta a escala y período | Cobertura igual o menor; ventaja limitada a un *K*, una escala o un subperíodo | 10 |
| **H6. Perfiles territoriales** | Existen grupos de zonas con perfiles de siniestralidad diferenciados (horario, actores, estacionalidad) que no se reducen al volumen total | *Silhouette* aceptable; alta concordancia entre corridas con remuestreo (p. ej., ARI); perfiles interpretables y robustos al escalado | Grupos inestables; separación débil; grupos que solo ordenan las zonas por volumen | 09 |
| **H7. Dependencia de la escala** | La predictibilidad y la estabilidad de los rankings dependen de la escala espacio-temporal: las unidades más finas aumentan la proporción de ceros y reducen la estabilidad | Mayor *zero inflation* y menor correlación de rangos en barrio que en comuna, o en mes que en trimestre; degradación de métricas en unidades finas | Proporción de ceros y estabilidad similares entre escalas | 03, 10 |
| **H8. Exposición** *(condicional)* | En corredores con conteos comparables, el ordenamiento por frecuencia difiere del ordenamiento por riesgo ajustado por exposición | Correlación de rangos moderada o baja entre ambos ordenamientos; zonas que cambian de cuartil | Correlación de rangos alta; ordenamientos prácticamente iguales | 10 |

**Notas.**

- H2–H5 son **predictivas**. Su confirmación no implica que el historial, la infraestructura o el perfil *causen* la siniestralidad.
- H7 se apoya en un patrón que la literatura señala: el problema de exceso de ceros se agrava al aumentar la resolución espacio-temporal (Affou et al., 2026, pp. 31 y 38). Debe verificarse en CABA.
- H3 queda **condicionada** tras el Paso 03 (D11). El callejero y los semáforos disponibles reflejan solo el estado actual, sin vigencia verificable, así que no entran en la evaluación predictiva principal. H3 se contrastará solo si se consiguen datos de infraestructura vigentes en cada fecha de corte. De lo contrario, se registrará como no contrastable.
- H8 se contrastará solo si el Paso 03 confirma que hay conteos comparables. De lo contrario, se registrará como no contrastable y no se reemplazará con extrapolaciones.

## 7. Fundamentación bibliográfica

### 7.1 Registro de búsqueda

| Campo | Detalle |
|---|---|
| Pregunta de revisión | ¿Qué enseñan los estudios disponibles sobre la predicción de siniestralidad vial (gravedad individual frente a pronóstico territorial) para delimitar el problema, las métricas y los baselines de UrbanSafe? |
| Bases consultadas | Solo la bibliografía local del proyecto (`bibliografia/`, 3 PDF) y la sección 5 del plan. **No** se hicieron búsquedas en bases externas en este paso. |
| Fecha | 2026-11-10 |
| Criterios de inclusión | Referencias listadas en el plan y disponibles en texto completo |
| Verificación | Título, autores, revista, año y DOI cotejados con el PDF. Cada afirmación citada se cotejó con el texto original e incluye su página. No se comprobó en línea la resolución de los DOI. |
| Exclusiones | Ninguna de las tres referencias. Los trabajos citados *dentro* de estas fuentes no se verificaron en su original y no se citan como evidencia directa. |
| Limitación | Hay tres fuentes, y ninguna estudia CABA ni América Latina en particular. La búsqueda dirigida de estudios de pronóstico territorial urbano queda pendiente (sección 9). |

### 7.2 Tabla de evidencia

| Dimensión | Ahmed et al. (2023) | Kotsyubynska et al. (2026) | Affou et al. (2026) |
|---|---|---|---|
| Tipo | Estudio empírico | Revisión sistemática y metaanálisis (PRISMA 2020, TRIPOD+AI, PROBAST) | Revisión sistemática (*survey*, PRISMA) de 135 artículos (2015–2025) |
| Población | Nueva Zelanda, sistema CAS, 2016–2020 (pp. 1, 5) | 74 estudios con 2.127.059 siniestros (p. 46) | Estudios de predicción de riesgo, frecuencia, gravedad y duración (pp. 2–3, 9) |
| Unidad de análisis | **Siniestro individual** | **Siniestro individual** | Variable: siniestro, segmento, celda de grilla o red |
| Variable objetivo | Gravedad en 4 clases: fatal, grave, leve, sin lesiones (p. 5) | Gravedad de lesiones; excluye explícitamente la predicción de **ocurrencia** (p. 48) | Ocurrencia y riesgo, frecuencia, gravedad y duración (p. 9) |
| Horizonte | No aplica: clasificación posterior al siniestro | No aplica (enfoque transversal; p. 49) | Desde tiempo real hasta series mensuales o anuales |
| Partición y validación | 80/20 y *k-fold* estratificado (*k* = 10), **no temporal** (p. 10) | El 45 % de los estudios valida solo dentro de la misma fuente (p. 50); cerca del 25 % prueba en otras regiones o períodos (p. 56) | Heterogénea; señala la transferibilidad limitada entre ciudades (p. 39) |
| Métricas | *Accuracy*, *precision*, *recall*, F1 (Tabla 6, p. 10) | F1 macro, G-mean, sensibilidad por clase; la *accuracy* sola es engañosa (pp. 46–47) | Clasificación: F1 y AUC; frecuencia: MAE, RMSE, MAPE, R² (pp. 32–34) |
| Baselines | Comparación entre *ensembles*; sin baseline trivial | No aplica | Modelos estadísticos (Poisson, binomial negativa, ARIMA y Bayes empírico) como referencia (pp. 13–14) |
| Interpretabilidad | SHAP global y local (pp. 11–12) | Recomienda interpretabilidad para la adopción práctica (p. 56) | SHAP como puente hacia decisiones; sin transparencia causal (p. 39) |
| Límites señalados | Generalización limitada a NZ; SMOTE puede sobregeneralizar (p. 14); posible sesgo de autoselección en el registro policial (p. 5) | I² = 84 %; el dominio "Análisis" concentra el mayor riesgo de sesgo (p. 50) | Desbalance, exceso de ceros en unidades finas, latencia y transferibilidad (pp. 38–39) |

### 7.3 Estudios sobre gravedad individual

Ahmed et al. (2023) y Kotsyubynska et al. (2026) responden **otra pregunta**: dado que ocurrió un siniestro, qué gravedad tendrá. Por eso **no verifican** que pueda pronosticarse la concentración territorial futura. El plan ya advierte esta limitación (sección 5). Su aporte a UrbanSafe es **metodológico**:

- **El desbalance exige métricas por clase.** Kotsyubynska et al. (2026, pp. 46–47) concluyen que la *accuracy* es engañosa con clases raras y recomiendan F1 macro, G-mean y sensibilidad por clase. En Ahmed et al. (2023), el modelo con mejor desempeño global (RF) tiene un *recall* de 0,24 para la clase fatal en los resultados por clase (Tabla B.8, p. 15). Los promedios macro de esa tabla coinciden aproximadamente con la columna sin rebalanceo de la Tabla 6. → UrbanSafe usará PR-AUC, *recall*, Precision@K y calibración (Paso 08).
- **El rebalanceo puede inflar las métricas.** En Ahmed et al. (2023, Tabla 6, p. 10), la *accuracy* de RF pasa de 52,36 % a 81,45 % tras aplicar SMOTE. El texto no permite confirmar si el conjunto de evaluación conservó la distribución original. Los propios autores advierten que SMOTE puede sobregeneralizar (p. 14). → En UrbanSafe, el rebalanceo solo se aplicará dentro de los *folds* de entrenamiento, y las métricas se calcularán sobre la distribución original.
- **La validación aleatoria no es pronóstico.** Ahmed et al. (2023) usan particiones aleatorias estratificadas. Kotsyubynska et al. (2026, p. 56) informan que los modelos validados en la misma fuente pierden desempeño ante datos externos. → UrbanSafe usará particiones **temporales** y variables conocidas al momento del pronóstico (Paso 06).
- **El metaanálisis presenta inconsistencias de reporte.** Por ejemplo, informa un total de 941 registros identificados junto con un conteo de Google Scholar mayor (p. 50). Sus estimaciones agregadas se usan solo como orientación metodológica, no como valores de referencia de desempeño.

### 7.4 Estudios sobre pronóstico territorial

Affou et al. (2026) es la única fuente local que trata la **frecuencia y el riesgo en ventanas espaciales y temporales**. Distingue tres tareas: predicción de ocurrencia y riesgo, predicción de gravedad y análisis de duración (p. 9). Es un *survey*, por lo que sus conclusiones dependen de los estudios que sintetiza. Aporta tres elementos al planteo:

1. **Regresión a la media y exceso de ceros.** Los métodos de Bayes empírico y los modelos con inflación de ceros se usan para no confundir picos transitorios con riesgo persistente, y para separar las zonas sin siniestros estructurales de las que no los tuvieron por azar (p. 13). Esto sustenta H1, H7 y la exigencia de baselines de persistencia.
2. **Escala.** El desempeño cae al aumentar la resolución espacio-temporal porque se agrava el problema de exceso de ceros (p. 31). Se mencionan celdas menores a 200 m (p. 38). Esto respalda la estrategia del plan: comenzar por barrio o comuna y por mes o trimestre, y considerar grillas solo si la densidad lo justifica.
3. **Métricas de frecuencia y heterogeneidad espacial.** Para la frecuencia predominan MAE y RMSE (p. 34). Según la síntesis, los modelos espaciales reducen el error entre un 12 % y un 45 % frente a los globales (p. 31). → Motiva variables de vecindad y la evaluación del error por territorio (Pasos 06–07). Es un hallazgo secundario: no se verificó en los estudios originales.

**Brecha que aborda UrbanSafe.** Ninguna de las fuentes verificadas evalúa si un modelo **supera la persistencia histórica en la priorización top-*K*** de zonas urbanas con datos abiertos. Ninguna lo hace tampoco en una ciudad latinoamericana. Esta es la contribución empírica que se propone, con alcance local y sin pretensión de generalización.

## 8. Decisiones abiertas hasta la auditoría de viabilidad (Paso 03)

Ninguna de estas decisiones se fija en este documento. Se tomarán con la evidencia del Paso 03 y quedarán registradas con su justificación.

> **Actualización (Paso 03).** Las decisiones de esta tabla se tomaron en el [informe de viabilidad](feasibility_report.md) (D1–D11): barrio × mes, 2019–2025 con 2025 como test provisorio, horizonte t+1, hechos por barrio-mes como objetivo de regresión, top 10 mensual como objetivo de clasificación (con exactamente 10 positivos y la regla de desempate R0) y K = 10. La infraestructura vial queda fuera de la evaluación predictiva principal (D11). La partición definitiva se fija en el Paso 06.

| Decisión | Opciones candidatas | Evidencia requerida (Paso 03) | Criterio de elección |
|---|---|---|---|
| **Unidad espacial** | Comuna; barrio; grilla regular (solo si la densidad lo justifica) | Coordenadas válidas, consistencia barrio/comuna, eventos por unidad y proporción de ceros | Densidad suficiente para estimar con estabilidad y utilidad para la decisión, sin proporción de ceros excesiva |
| **Período de agregación** | Mes; trimestre | Registros por año y mes, estacionalidad y ceros por zona-período | Equilibrio entre resolución temporal, estabilidad del conteo y cantidad efectiva de observaciones del panel |
| **Período de estudio** | Toda la serie disponible; serie con tratamiento explícito de la pandemia; solo años comparables | Cambios metodológicos entre años, quiebres de nivel y cobertura | Comparabilidad del registro; suficientes períodos para la validación temporal expansiva |
| **Horizonte de pronóstico** | *t*+1 período (por defecto en el plan); horizontes mayores como análisis de sensibilidad | Autocorrelación y persistencia de rankings | Utilidad para planificar frente a degradación del desempeño |
| **Variable objetivo (regresión)** | Conteo de hechos; conteo de víctimas; conteo de hechos con víctimas graves o fatales; conteo ponderado por gravedad | Relación hechos-víctimas, duplicados, completitud de la gravedad y del tipo de actor | Que mida el fenómeno de interés sin doble conteo y con soporte suficiente |
| **Variable objetivo y umbral (clasificación)** | Umbral por percentil de la distribución de entrenamiento; umbral absoluto; umbral relativo al historial de la zona | Distribución de conteos, desbalance resultante y estabilidad entre períodos | Fijado **sin consultar el test**, con desbalance manejable y significado operativo (p. ej., capacidad de intervención) |
| **Valor de *K* para la priorización** | Valores ligados a la capacidad operativa (número o proporción de zonas) | Número de unidades de la escala elegida | Relevancia para la decisión; se informarán varios *K* |
| **Exposición** | Excluirla; análisis separado por corredor; covariable donde sea comparable | Cobertura, continuidad y representatividad de los conteos vehiculares y peatonales | Solo con mediciones comparables; nunca extrapolar sensores aislados |
| **Siniestros sin ubicación válida** | Exclusión documentada; asignación a la comuna informada; análisis de sensibilidad | Porcentaje y patrón de los faltantes | Minimizar el sesgo territorial y preservar la trazabilidad |

## 9. Supuestos pendientes de verificación

| Supuesto | Por qué importa | Se verifica en |
|---|---|---|
| S1. La fuente de siniestros de CABA tiene fecha, ubicación georreferenciable o barrio/comuna, tipo de actor y gravedad | Sin estos campos no se construyen el panel ni los perfiles | 02–03 |
| S2. Se pueden distinguir los **hechos** de las **víctimas** (identificador de hecho) | Evita el doble conteo en la variable objetivo | 03 |
| S3. Los criterios de registro son comparables entre años | Los cambios metodológicos pueden imitar tendencias | 02–03 (consulta institucional) |
| S4. El registro cubre la siniestralidad de manera similar en todo el territorio | Un subregistro diferencial sesgaría la concentración y los rankings. Ahmed et al. (2023, p. 5) señalan sesgos de registro policial análogos. | 03, 05 |
| S5. Hay capas oficiales de barrios, comunas y red vial compatibles con la geometría de los siniestros | Necesarias para la asignación espacial y las variables de infraestructura | 02 |
| S6. Los conteos de tránsito pueden no ser comparables o representativos | Determina si H8 y PS7 son contrastables | 02–03 |
| S7. Las variables de infraestructura disponibles reflejan el estado vial del período analizado | Si son posteriores, pueden filtrar información futura | 02, 06 |
| S8. La serie tiene períodos suficientes para una validación temporal expansiva con test reservado | Condiciona la escala temporal y el horizonte | 03 |
| S9. Literatura adicional sobre pronóstico territorial urbano (incluida América Latina) | La base verificada es de tres fuentes. Las referencias secundarias citadas por Affou et al. (2026) no se revisaron en su original. | Búsqueda complementaria; puede integrarse en el Paso 02 |

## 10. Consideraciones éticas e interpretativas

- **No estigmatizar territorios.** Los rankings describen carga registrada, no la "peligrosidad" intrínseca de un barrio ni de su población.
- **Sesgo de registro.** Los patrones pueden reflejar diferencias en la detección o la denuncia. Se analizarán como limitación (Pasos 05 y 10).
- **Incertidumbre visible.** Toda priorización se comunicará con su incertidumbre y con el desempeño del baseline.
- **Datos personales.** Solo se usarán datos abiertos agregados. No se intentará reidentificar víctimas.

## 11. Registro de decisiones del Paso 01

| # | Decisión | Justificación |
|---|---|---|
| D1 | El objeto de estudio es la **frecuencia y concentración territorial** por zona-período, no la gravedad individual | Coherencia con el plan y con la utilidad para la priorización; la literatura de gravedad no responde esta pregunta |
| D2 | Toda evaluación predictiva se compara con un **baseline de persistencia** y se hace **fuera de muestra con particiones temporales** | Regresión a la media; riesgos de la validación aleatoria señalados en la bibliografía |
| D3 | El riesgo ajustado por exposición es una **extensión condicionada** y local (por corredor) | Plan, sección 6; conteos aún no auditados |
| D4 | No se formulan afirmaciones causales | Diseño predictivo; sin registros de intervenciones verificados |
| D5 | Escala, período, horizonte, objetivo, umbral y *K* quedan **abiertos** hasta el Paso 03 | Plan, principio 2 y sección 8 |

## 12. Verificación del criterio de aceptación del Paso 01

Criterio del plan: *"preguntas, objetivos, hipótesis y utilidad claramente definidos"*.

| Elemento | Estado | Evidencia en este documento |
|---|---|---|
| Preguntas | ✔ Definidas | Sección 4: pregunta principal y siete secundarias, vinculadas con las cuatro preguntas centrales del plan y con los pasos |
| Objetivos | ✔ Definidos | Sección 5: objetivo general y ocho específicos, con el entregable del plan que los evidencia |
| Hipótesis | ✔ Definidas | Sección 6: ocho hipótesis, cada una con evidencia a favor, resultado que la debilita y paso de contraste |
| Utilidad | ✔ Definida | Secciones 1–2: problema público, destinatarios, decisiones informables y usos no válidos |
| Actividad 2: ocurrencia, frecuencia, gravedad y exposición | ✔ | Sección 3.3 |
| Actividad 3: delimitar CABA | ✔ | Sección 3.1 |
| Actividad 4: destinatarios | ✔ | Sección 2 |
| Actividad 5: hipótesis sin anticipar resultados | ✔ | Sección 6: alternativas nulas explícitas y umbrales fijados antes del test |
| Actividad 6: decisiones que puede informar | ✔ | Sección 2 |

**Dictamen (autoauditoría).** El criterio de aceptación se cumple en el plano documental. Queda pendiente la revisión del responsable del proyecto. El hito **no se marca como completado** en el plan hasta esa revisión. Las limitaciones que no invalidan el hito están en la sección 9 (supuestos S1–S9), en particular la base bibliográfica acotada.

## Referencias verificadas

- Affou, H., Teso-Fz-Betoño, D., Fernandez-Gamiz, U., Ramos-Hernanz, J. A., Caballero-Martin, D., & Lopez-Guede, J. M. (2026). Advances in traffic accident prediction: A survey of novel approaches. *Urban Science, 10*(7), 349. https://doi.org/10.3390/urbansci10070349
- Ahmed, S., Hossain, M. A., Ray, S. K., Bhuiyan, M. M. I., & Sabuj, S. R. (2023). A study on road accident prediction and contributing factors using explainable machine learning models: Analysis and performance. *Transportation Research Interdisciplinary Perspectives, 19*, 100814. https://doi.org/10.1016/j.trip.2023.100814
- Kotsyubynska, Y., Kozan, N., Chadiuk, V., Kostyshyn, A., Kotsyubynsky, A., & Fentsyk, V. (2026). Machine learning and deep learning for predicting traffic crash injury severity: A systematic review and meta-analysis (2014–2025). *Journal of Road Safety, 37*(1), 46–60. https://doi.org/10.33492/JRS-D-26-1-2721386

*Referencias de segunda mano.* El dato de la OMS (WHO, 2024) se toma de Kotsyubynska et al. (2026, p. 47). No se consultó el informe original.
