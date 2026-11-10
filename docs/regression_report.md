# UrbanSafe CABA — Informe de regresión supervisada

**Hito:** Paso 07  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:**
- Notebook: [notebooks/03_regression.ipynb](../notebooks/03_regression.ipynb), ejecutado de punta a punta.
- Código: [`src/regression.py`](../src/regression.py) y [`src/evaluation.py`](../src/evaluation.py).
- Tablas y predicciones: [reports/tables/03_regression/](../reports/tables/03_regression/).
- Selección congelada antes del test: [seleccion_congelada.json](../reports/tables/03_regression/seleccion_congelada.json).
- Protocolo: [experimental_protocol.md](experimental_protocol.md).

**Pregunta.** ¿Cuántos siniestros con víctimas ocurrirán en cada barrio el mes siguiente?

---

## 1. Resumen

| | Validación (media V2022–V2024) | Test 2025 |
|---|---|---|
| **Modelo seleccionado:** Poisson L2, conjunto compacto, α = 0,1, sin meses de pandemia en el entrenamiento | MAE 3,863 | MAE 4,071 |
| Mejor baseline: media de 12 meses | MAE 3,850 | MAE 4,062 |
| ΔMAE (modelo − baseline) | Cociente 1,0035; 2 de 3 *folds* ganados | +0,009, IC 95 % [−0,127; +0,142] |
| ¿Cumple el criterio de mejora del protocolo? | **No** (umbral: cociente ≤ 0,97) | **No** (el IC incluye el 0) |

**Conclusión (H2).** Ningún modelo predice la cantidad de hechos del mes siguiente mejor que la **media de los 12 meses previos del barrio**. Sí mejoran con claridad a la persistencia (ΔMAE −1,00; IC [−1,44; −0,58]) y al baseline estacional (−1,42; IC [−1,80; −1,09]). Este resultado es negativo pero informativo: con historial, calendario, vecindad y composición disponibles, el nivel medio reciente del barrio ya captura casi toda la señal predecible a un mes.

## 2. Modelos comparados

Se probaron 38 configuraciones, fijadas en el protocolo, más 8 post hoc. Todas siguieron la misma validación expansiva.

| Familia | Configuraciones | Mejor configuración | MAE validación | *Folds* ganados al baseline | MAE test (no se usó para decidir) |
|---|---|---|---|---|---|
| Poisson GLM L2 | 20 | Compacto, α = 0,1, sin pandemia | **3,863** | 2 | 4,071 |
| HGB con pérdida Poisson | 16 | lr 0,03, 7 hojas | 4,043 | 1 | 4,066 |
| Binomial negativa NB2 (protocolo) | 2 | Sin exclusión | 5,059 | 1 | 4,120 |
| *NB2 con L2 (post hoc, §5)* | *8* | *λ = 0,1, sin pandemia* | *3,864* | — | *4,088* |
| Baselines: media de 12 meses / persistencia / estacional | — | — | 3,850 / 4,823 / 5,157 | — | 4,062 / 5,068 / 5,486 |

**Justificación de la selección.** El protocolo fija la regla de antemano: gana el menor MAE medio en validación. El Poisson compacto regularizado gana esa comparación, tiene la menor devianza (1,59) y un sesgo moderado. Además, es el más simple e interpretable de los candidatos. Excluir de la pérdida los meses de pandemia fue decisivo en las tres familias.

**Recomendación de uso.**
- **Pronóstico puntual.** La media de 12 meses es la referencia operativa porque el Poisson no cumplió el criterio de mejora.
- **Modelo Poisson seleccionado:** aporta la captación de la estacionalidad (reproduce el bajo nivel de enero y febrero de 2025) y es la entrada de la evaluación integrada del Paso 10.
- **Incertidumbre por barrio.** La NB2 regularizada queda como candidata exploratoria. Su uso requiere verificar la cobertura en un período independiente con un criterio fijado de antemano.

## 3. Evaluación principal en el test 2025 (gap = 0)

- **Sesgo.** Todos los GLM subestiman (−0,87 a −1,46 hechos por barrio-mes). 2025 es el año con más hechos de la serie, y el salto de octubre a diciembre (más de 1.030 por mes) no se anticipa con información hasta el mes anterior.
- **Por barrio.** El modelo mejora al baseline en 20 de los 48 barrios. El error absoluto crece con el nivel del barrio (Spearman 0,91); los mayores MAE están en Balvanera (10,0), Caballito (8,0) y Saavedra (7,2). Ver [errores_por_barrio_test.csv](../reports/tables/03_regression/errores_por_barrio_test.csv).
- **Gráficos.** [test_ciudad_y_barrios.png](../reports/figures/03_regression/test_ciudad_y_barrios.png) muestra el total de la ciudad y el mapa de la diferencia de error por barrio.

## 4. Incertidumbre

| Modelo | Cobertura en test, 80 % nominal | 95 % nominal | α |
|---|---|---|---|
| NB2 del protocolo, sin regularizar | 85,8 % | 98,3 % | 0,053 |
| NB2 con L2 (post hoc) | **81,8 %** | **96,2 %** | 0,022 |

Los intervalos omiten la incertidumbre de los parámetros. Las coberturas de la NB2 regularizada son descriptivas para 2025. La variante se incorporó después de observar la evaluación principal.

**Entre períodos.** IC 95 % por *bootstrap* de bloques móviles (3 meses, 2.000 réplicas) sobre los 12 meses del test. Con solo 12 meses la potencia es baja: el IC de ΔMAE frente a la media de 12 meses (±0,14, alrededor del 3,5 % del MAE) **no permite afirmar equivalencia estricta**, solo que no hay mejora demostrable.

## 5. Análisis exploratorio post hoc de la binomial negativa con penalización L2

- **Motivo.** Con la validación sola (§2 del notebook) se vio que los GLM sin regularizar, incluida la NB2 del protocolo, son inestables en V2022: ese *fold* entrena con pocos meses y las variables de nivel de ciudad son colineales, y su MAE llega a 60. En V2023 y V2024, en cambio, rinden como el Poisson. La comparación entre familias que pide el plan quedaba sesgada.
- **Acción.** Se agregó la NB2 con L2 (8 configuraciones). La corrección se hizo **después de ver el test**, así que se informa como **no confirmatoria**: no cambia la selección congelada y no habría ganado la selección (3,864 frente a 3,863).
- **Registro.** Protocolo, sección 11.

## 6. Análisis exploratorio de sensibilidad a la latencia (gap = 1)

Con información hasta T−2, y con particiones que excluyen del ajuste las etiquetas aún no observables (control C13 del protocolo), el modelo seleccionado queda **peor** que el baseline, también recalculado con T−2. El cociente de MAE es **1,224** (V2022), 0,980 (V2023), 1,006 (V2024) y **1,027** (test). V2022 entrena con solo 7 meses fuera de la pandemia. En esta sensibilidad, la media de 12 meses obtuvo un MAE menor en dos de los tres folds y en 2025. La selección principal se conserva.

*Nota:* una versión anterior de este informe mostraba cocientes de entre 0,977 y 1,001. Esos valores se obtuvieron con particiones que, con gap = 1, incluían la etiqueta de diciembre del año anterior, que no estaría disponible (fuga de etiquetas). Se retiraron.

## 7. Reproducibilidad

```bash
python -m src.data_processing --download
```

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 03_regression.ipynb
```

La grilla completa tarda alrededor de 20 s. Hay 38 pruebas automatizadas y todas pasan.

---

## 8. Dictamen científico del Paso 07 (autoauditoría)

**Tipo de revisión.** **Autoauditoría** con la skill `ml-scientific-reviewer`. El revisor es el mismo agente que implementó. No hubo un revisor independiente porque la delegación no fue autorizada.

**Reproducción independiente.**
- A partir de `predicciones_test.csv` se recalcularon el MAE del modelo seleccionado (4,0708), de la media de 12 meses (4,0622) y de la persistencia (5,0677). Coinciden con `metricas_test.csv`.
- También coincide el IC por bloques de ΔMAE ([−0,1272; +0,1422]).
- Para 5 filas al azar, la predicción del baseline de la media de 12 meses se recalculó directamente desde el panel, y coincide.

| # | Hallazgo | Evidencia | Severidad | Corrección o tratamiento | Condición |
|---|---|---|---|---|---|
| R1 | La NB2 del protocolo, sin regularizar, es inestable en V2022 y la comparación entre familias quedaba sesgada | `grilla_validacion.csv` (MAE de V2022 hasta 60) | Media | NB2 con L2 agregada como desviación post hoc, no confirmatoria (§5) | ✔ Registrada; la conclusión no cambia |
| R2 | Riesgo de decidir mirando el test | La selección se congela en un JSON antes de la celda de test; la regla está automatizada | — | La NB2 con L2 y la sensibilidad con gap = 1 reutilizan 2025 como análisis exploratorios y conservan la selección congelada | ✔ |
| R3 | Baja potencia del test (12 meses) | IC de ΔMAE ±0,14 | Media, inherente | Se informa "no hay mejora demostrable", no "equivalencia" | ✔ Redacción ajustada |
| R4 | Subestimación sistemática en 2025 (cambio de nivel) | Sesgo de −0,87 a −1,46 | Media | Se informa; 2025 puede ser provisorio (consulta). En el Paso 10 se informará V2024 como validación retrospectiva (no es un test, porque participó en la selección) | Paso 10 |
| R5 | Número de configuraciones | 38 + 8 post hoc | Baja | Registrado; grillas ≤ 30 por familia | ✔ |
| R6 | Supuesto de disponibilidad (gap = 0) | §6 | Media | La sensibilidad gap = 1 se recalculó con las particiones corregidas (C13); el modelo resulta peor que el baseline (1,03 en test) | ✔ Condición R2 del Paso 06 cumplida; resultado actualizado |
| R7 | Sin intervalos en el modelo seleccionado | §4 | Baja | La NB2 con L2 queda como candidata exploratoria | Confirmar cobertura en un período independiente |
| R8 | El error escala con el nivel del barrio | Spearman 0,91 | Baja | Se informa; en el Paso 10, error relativo por barrio | Paso 10 |
| R9 | Colinealidad (condición R4 del Paso 06) | El conjunto completo rinde peor que el compacto | Baja | Se resolvió con regularización y con el conjunto compacto | ✔ |
| R10 | Fuga de etiquetas en la sensibilidad gap = 1, que esta autoauditoría omitió | Corregida en `src/features.py` fuera de esta revisión (protocolo, sección 11) | Alta para §6; nula para el resultado principal | Se reejecutó el notebook: con gap = 0, las predicciones, las métricas de test y la grilla de validación son idénticas a la versión previa (comparación de archivos); con gap = 1, §6 cambia | ✔ |

**Alcance de las afirmaciones.**
- Los resultados son **predictivos**. No se interpretan coeficientes como efectos.
- Los conteos son carga registrada, no riesgo (D8).
- No hay variables de infraestructura (D11).

**Dictamen: aprobado.** No hay hallazgos que invaliden la evaluación. La comparación es reproducible, el modelo se seleccionó con una regla fijada a priori y la evaluación principal de 2025 se hizo con la selección congelada. Las secciones 5 y 6 documentan la reutilización exploratoria de 2025. La conclusión sustantiva es que **no se demuestra mejora frente a la media de 12 meses** (H2 no respaldada frente al mejor baseline; respaldada frente a la persistencia y al estacional). Se recomienda una revisión independiente antes de cerrar el Paso 10.

## 9. Verificación del criterio de aceptación del Paso 07

Criterio del plan: *"comparación reproducible, modelo seleccionado con justificación y test fuera de muestra"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Baseline de persistencia, Poisson, binomial negativa (con sobredispersión) y árboles | ✔ | §2; α NB2 > 0 en todos los *folds* |
| Hiperparámetros optimizados con validación temporal expansiva | ✔ | 38 configuraciones × 3 *folds* |
| MAE, devianza, sesgo, errores por territorio y estabilidad por subperíodo | ✔ | Notebook §2–§4; tablas por *fold*, por barrio y por mes |
| Incertidumbre | ✔ | Intervalos NB2 y *bootstrap* por bloques |
| Comparación reproducible | ✔ | Notebook ejecutable; predicciones guardadas; reproducción independiente (§8) |
| Modelo seleccionado con justificación | ✔ | §2 y selección congelada |
| Test fuera de muestra | ✔ | §3; evaluado una vez |
| Dictamen científico registrado | ✔ | §8 |
