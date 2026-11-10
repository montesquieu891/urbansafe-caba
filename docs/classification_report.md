# UrbanSafe CABA — Informe de clasificación supervisada

**Hito:** Paso 08  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:**
- Notebook: [notebooks/04_classification.ipynb](../notebooks/04_classification.ipynb), ejecutado de punta a punta.
- Código: [`src/classification.py`](../src/classification.py).
- Tablas y predicciones: [reports/tables/04_classification/](../reports/tables/04_classification/).
- Selección y umbral congelados: [seleccion_congelada.json](../reports/tables/04_classification/seleccion_congelada.json).
- Protocolo: [experimental_protocol.md](experimental_protocol.md), con la aclaración sobre la métrica de selección registrada antes de modelar (sección 11).

**Pregunta.** ¿Qué barrios estarán entre los 10 con más siniestros con víctimas el mes siguiente?

---

## 1. Resumen

| | Validación (media V2022–V2024) | Test 2025 |
|---|---|---|
| **Modelo seleccionado:** regresión logística L2, C = 0,01, sin ponderación de clases ni meses de pandemia | P@10 esperada 0,795 | P@10 0,808; PR-AUC 0,909; Brier 0,055 |
| Mejor baseline: ranking por la media de 12 meses | 0,779 | P@10 0,792; PR-AUC 0,900 |
| ΔP@10 (modelo − baseline) | +0,016 (≥ 0,02 en 1 de 3 *folds*) | +0,017: 2 aciertos más en 120 selecciones |
| Sensibilidad al desempate (500 semillas pareadas) | [0,014; 0,019], excluye el 0 | [0,017; 0,017], excluye el 0 |
| Incertidumbre entre meses (bloques de 3 meses) | — | IC 95 % [−0,017; +0,058], **incluye el 0** |
| ¿Cumple el criterio de mejora? | **No** (umbral de relevancia: 0,02) | **No** (el IC por bloques incluye el 0) |

**Conclusión (H4 y la parte de H5 que se evalúa aquí).** El clasificador supera de forma **pequeña y estable** al ranking por la media de 12 meses, y esa ventaja no depende del desempate. Pero queda **por debajo del umbral de relevancia fijado a priori** y **no es significativa entre meses** en el test. La ventaja se concentra en las plazas inciertas del top 10: 65 % de aciertos del modelo frente a 62 % del baseline fuera del núcleo persistente. Frente a la persistencia, la mejora es clara (0,808 frente a 0,733).

## 2. Modelos comparados

Se probaron 56 configuraciones con la misma validación expansiva y la misma regla de selección.

| Familia | Configuraciones | Mejor configuración | P@10 esperada en validación | ΔP@10 frente al baseline | P@10 en test (no se usó para decidir) |
|---|---|---|---|---|---|
| **Regresión logística L2** | 16 | C = 0,01, sin ponderación, sin pandemia | **0,795** | +0,016 | 0,808 |
| *Random forest* | 24 | Profundidad 8, hoja mínima 20, `balanced_subsample`, sin pandemia | 0,789 | +0,010 | 0,808 |
| HGB | 16 | 7 hojas, hoja mínima 20, `balanced` | 0,776 | −0,003 | 0,800 |
| Baselines: media de 12 meses / persistencia | — | — | 0,779 / 0,728 | — | 0,792 / 0,733 |

- **Ninguna** de las 56 configuraciones alcanza ΔP@10 ≥ 0,02 en la media de validación.
- **Ponderación de clases.** Empeora la calibración: Brier medio de 0,089 frente a 0,069. En la logística seleccionada, 0,095 frente a 0,066. No mejora el ranking.
- **SMOTE.** No se aplicó: la prevalencia es fija (20,8 %) y la ponderación ya se evaluó.

**Justificación de la selección.** Se aplicó la regla registrada antes de modelar: mayor Precision@10 esperada media, con desempate por PR-AUC. La logística obtiene la mayor Precision@10 esperada media.

## 3. Evaluación principal en 2025 (gap = 0)

- **Ranking.** P@10 de 0,808 (R0 y esperada coinciden). PR-AUC 0,909 y ROC-AUC 0,966.
- **Umbral histórico congelado (0,46).** Dio el mayor F1 (0,7983) en una grilla de 91 cortes de 0,05 a 0,95 aplicada a la validación agrupada. Una auditoría posterior obtuvo F1 = 0,8006 en el corte 0,444245 al revisar todos los cortes distintos de validación. Las métricas siguientes corresponden al umbral histórico de 0,46.
  - *Precision* 0,893, *recall* 0,767 y F1 0,825.
  - Matriz de confusión: 92 verdaderos positivos, 11 falsos positivos, 28 falsos negativos y 445 verdaderos negativos.
  - Con el umbral, el modelo marca en promedio 8,6 barrios por mes. La decisión top-K, en cambio, siempre elige 10.
- **Calibración.** Brier 0,055 y curva de confiabilidad cercana a la diagonal ([figura](../reports/figures/04_classification/test_p10_calibracion_confusion.png)). La curva y el Brier describen el desempeño probabilístico observado en 2025. Para validar su uso operativo se requiere un período independiente y un criterio de calibración fijado de antemano.
- **Por mes.** El modelo iguala o supera al baseline en 11 de 12 meses; febrero es la excepción (0,8 frente a 0,9).
- **Plazas inciertas.** El núcleo, calculado con el entrenamiento final, son Balvanera, Caballito, Flores, Palermo y Recoleta. Fuera de él, el modelo acierta 39 de 60 selecciones (65,0 %) y el baseline 37 de 60 (61,7 %).

## 4. Interpretabilidad (SHAP)

Se calculó **SHAP lineal exacto** en log-odds para la logística seleccionada (variables estandarizadas, contribución de cada una respecto de la media del entrenamiento). Se agrega por familias, por la colinealidad.

| Familia | % de la importancia media |SHAP| |
|---|---|
| Historial del barrio (rezagos, medias, densidad) | 40,9 |
| Historial relativo (frecuencia en el top 10, puesto, participación) | 34,4 |
| Composición modal | 8,1 |
| Territorio (superficie, comuna) | 6,5 |
| Nivel de la ciudad | 5,5 |
| Vecindad | 2,9 |
| Calendario y pandemia | 1,8 |

Las variables individuales más influyentes son `top10_freq12`, `rank_ma12`, `share_ma12` y las medias de 12, 6 y 3 meses. **Interpretación:** el modelo es, sobre todo, una **persistencia refinada**, lo que explica que solo supere marginalmente a la media de 12 meses (E6). Son **patrones predictivos**: no se afirma que la composición modal ni el territorio causen la concentración.

## 5. Sensibilidad exploratoria a la latencia (gap = 1)

La sensibilidad conserva la configuración congelada y reutiliza 2025 con fines exploratorios. Se usaron particiones con etiquetas disponibles al inicio de cada evaluación (C13). ΔP@10 esperada frente al baseline recalculado con T−2: +0,050 (V2022), +0,013 (V2023), −0,006 (V2024) y +0,008 (test). La ventaja **no es sistemática** con mayor latencia.

## 6. Reproducibilidad

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 04_classification.ipynb
```

La ejecución tarda unos 3 minutos y la grilla, unos 2. Hay 50 pruebas automatizadas y todas pasan.

---

## 7. Dictamen científico del Paso 08 (autoauditoría)

**Tipo de revisión.** **Autoauditoría** con las skills `ml-scientific-reviewer` y `colab-ml-validation`. El revisor es el mismo agente que implementó. No hubo un revisor independiente: la delegación no fue autorizada.

**Comprobaciones ejecutadas.**
1. **Reproducción independiente desde `predicciones_test.csv`.** El top 10 por puntaje se calculó con `nlargest`, sin la función del proyecto. Dio P@10 de 0,8083 (modelo) y 0,7917 (media de 12 meses), y PR-AUC de 0,9094 y 0,8996. Coinciden con `metricas_test.csv`. No hay empates de probabilidad en las selecciones del modelo.
2. **Etiquetas.** Hay exactamente 10 positivos por mes, y todos tienen un conteo mayor o igual que los negativos.
3. **Particiones.** Son las del Paso 06, con disponibilidad de etiquetas (C13). Para gap = 0 son idénticas a las de la regresión.
4. **Ajustes dentro del *fold*.** El escalado, la codificación y la ponderación están dentro del `Pipeline`. El umbral se eligió con predicciones de validación. La selección y el umbral se congelaron antes del test.
5. **Comparación pareada.** El intervalo de desempate usa las mismas etiquetas y los mismos meses para el modelo y el baseline en cada repetición. La incertidumbre entre meses se calcula aparte.

| # | Hallazgo | Evidencia | Severidad | Tratamiento | Condición |
|---|---|---|---|---|---|
| C1 | La métrica de selección era ambigua en el protocolo (PR-AUC y P@10 eran ambas "principales") | Protocolo 5.2 | Media | Se aclaró y registró **antes** de entrenar (sección 11) | ✔ |
| C2 | Baja potencia del test: 12 meses y 120 selecciones; la ventaja observada son 2 aciertos | IC por bloques [−0,017; 0,058] | Media, inherente | Se informa "mejora pequeña, no significativa ni relevante" | ✔ Redacción ajustada |
| C3 | Intervalo pareado degenerado en el test ([0,017; 0,017]) | Los empates de 2025 no cambian la diferencia | Baja | Se verificó que no hay empates de probabilidad y que las etiquetas son coherentes; es un resultado legítimo | ✔ |
| C4 | El umbral F1 (0,46) marca unos 8,6 barrios por mes y no coincide con la decisión top-10 | Matriz de confusión | Baja | Se informan ambas lecturas; la decisión operativa es top-K | ✔ |
| C5 | SHAP con variables colineales | 6 pares con Spearman > 0,95 | Media para la interpretación | Agregación por familias; SHAP lineal exacto bajo independencia; sin lectura causal | ✔ |
| C6 | Número de configuraciones (56) y riesgo de sobreajustar la validación | Grilla | Baja | ≤ 30 por familia; métrica promediada en 3 *folds*; criterios a priori | ✔ |
| C7 | Posible provisionalidad de 2025 | Consulta pendiente | Media | V2024 se informará como validación retrospectiva en el Paso 10 | Paso 10 |

**Alcance de las afirmaciones.**
- Las probabilidades y SHAP son **predictivos**.
- El top 10 por conteo es carga registrada, no riesgo (D8).
- No hay infraestructura (D11) ni exposición.

**Dictamen: aprobado.** No hay hallazgos que invaliden la evaluación. El clasificador se seleccionó con métricas fijadas a priori, es estable entre *folds* (supera al baseline en los tres, aunque por menos de 0,02 en dos) y la calibración se describe para el período evaluado. Su utilidad territorial es **marginal** frente a la media de 12 meses. Se recomienda una revisión independiente antes de cerrar el Paso 10.

## 8. Verificación del criterio de aceptación del Paso 08

Criterio del plan: *"clasificador seleccionado por métricas, estabilidad y utilidad territorial"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Umbral de concentración definido sin consultar el test | ✔ | Top 10 con R0 (D6 y D6.1); umbral de decisión congelado con validación |
| Baseline, regresión logística, *random forest* y *gradient boosting* | ✔ | §2 (HGB como *gradient boosting* del plan) |
| Ponderación de clases examinada; SMOTE solo si es pertinente | ✔ | §2: ponderación evaluada; SMOTE no pertinente |
| Matriz de confusión, *precision*, *recall*, F1, PR-AUC, calibración y Precision@K | ✔ | §3 |
| Hiperparámetros y umbral optimizados sin usar el test | ✔ | Selección congelada (§7, punto 4) |
| SHAP sin afirmaciones causales | ✔ | §4 |
| Selección por métricas, estabilidad y utilidad territorial | ✔ | §1–§3; plazas inciertas; por *fold* y por mes |
| Dictamen científico registrado | ✔ | §7 |
