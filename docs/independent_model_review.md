# UrbanSafe CABA — Revisión científica independiente del modelado (Pasos 06 a 10)

**Tipo de revisión:** revisión independiente, hecha por un agente distinto del que implementó el modelado. El revisor no participó en la implementación ni en las autoauditorías anteriores.  
**Fecha:** 2026-11-13  
**Skills aplicadas:** `ml-scientific-reviewer`, `colab-ml-validation`, `spatiotemporal-ml` y `clustering-research`  
**Alcance:**
- Notebooks `02_feature_engineering`, `03_regression`, `04_classification`, `05_clustering` y `06_integrated_evaluation`, incluidas las celdas `guia-docente`. El `07_storytelling` se revisó solo para detectar conclusiones exageradas.
- Código: `src/features.py`, `src/labels.py`, `src/regression.py`, `src/evaluation.py`, `src/classification.py`, `src/profiles.py` y `scripts/export_models.py`.
- Documentos: `experimental_protocol.md`, `feasibility_report.md` (D1–D11), `regression_report.md`, `classification_report.md`, `clustering_report.md`, `robustness_report.md`, `final_report.md` y `final_validation.md`.
- Tablas de `reports/tables/`.

**Qué se ejecutó.** No se modificó ningún archivo del repositorio. Los scripts de la revisión están fuera del repositorio.
1. `python -m pytest -q tests`: **66 de 66** pruebas pasan.
2. **Control de fuga independiente.** Se hizo con un método distinto del control C3. Para 6 meses objetivo T (2021-01 a 2025-12) y para gap 0 y 1, el panel se truncó en T y se reemplazaron con ruido todos los meses posteriores a L = T − 1 − gap. Luego se reconstruyeron las variables. **Las 12 comparaciones coinciden.**
3. **Reproducción desde `predicciones_test.csv`**, sin usar las funciones del proyecto:
   - MAE del Poisson 4,0708, de la media de 12 meses 4,0622 y de la persistencia 5,0677;
   - IC por bloques de ΔMAE [−0,1272; +0,1422];
   - P@10 con `nlargest`: 0,8083 frente a 0,7917;
   - cobertura con K = 10: 0,4305 (clasificador), 0,4273 (historial) y 0,4462 (oráculo). La ganancia captada sobre el azar es **92,0 %**.
   
   Todo coincide con las tablas y con los informes.
4. **Modelos sencillos alternativos en validación** (V2022–V2024), para comprobar si el resultado negativo se debe a un *tuning* pobre. Ninguno supera a la media de 12 meses (MAE medio 3,850):
   - media de 6 meses: 3,913;
   - media de 12 meses × índice estacional estimado en el entrenamiento: cociente 1,02 en V2023–V2024;
   - GLM Poisson con *offset* log(ma12), mes y tendencia: 4,228.
   
   También se inspeccionaron los coeficientes del Poisson seleccionado: log ma12 ≈ 0,52–0,63 y log ma3 ≈ 0,40–0,48, que suman alrededor de 1. El modelo replica una media móvil ponderada.
5. **Clustering.** Se reprodujo K-Means con k = 2 desde `atributos_barrio.csv` (ARI 1,0 y *silhouette* 0,330). Se comparó con reglas de una sola variable.
6. **Datos crudos de conteos vehiculares** (`conteo_vehicular_2024.xlsx`). Se tabularon el sentido y el tipo de circulación de cada sensor, y se recalcularon las métricas de H8 por subgrupos.
7. **Comprobaciones puntuales en las tablas:**
   - empates en 2025;
   - selecciones del perfil de borde;
   - densidad por perfil;
   - Brier con y sin ponderación de clases;
   - MAE con y sin exclusión de la pandemia por familia.

Lo que en las tablas siguientes figura como *Evidencia: ejecutado* se comprobó con código. Lo marcado *por lectura* es una inferencia a partir del código o del texto.

---

## 1. Hallazgos

| Id | Severidad | Ubicación | Descripción | Evidencia | Impacto en las conclusiones | Corrección sugerida |
|---|---|---|---|---|---|---|
| R1 | **Mayor** | `06_integrated_evaluation`, celdas 29 y 31; `robustness_report.md:66-71`; `final_report.md` (resumen y H8); `07_storytelling` §6 | **El denominador de exposición (H8) no es homogéneo entre sensores.** Cada ubicación registra **un solo sentido**: el máximo es 1 sentido por ubicación. Sin embargo, 47 de los 95 sensores están en vías de **doble** circulación (34 calles y avenidas, 9 carriles exclusivos y las 4 autopistas). Los hechos a 150 m incluyen ambos sentidos y las transversales. El notebook afirma que la exposición es la "suma de sentidos por fecha", y no es así. Además, los carriles exclusivos tienen un volumen mediano de 5.938 vehículos por día, frente a 12.631 de calles y avenidas, con hechos comparables (11 frente a 10). Es compatible con que se cuente solo el carril exclusivo. La unidad "por millón de vehículos-día" también es incorrecta: la tasa es hechos / (veh/día × 365) × 10⁶, es decir, por millón de pasadas en el año. | Ejecutado: tabla cruzada de tipo de vía por circulación y sentidos por ubicación; medianas por tipo | Las cifras "43 % cambia de cuartil", "4 de 10 coincidencias" y "tasa mayor en carriles exclusivos (5,4)" mezclan denominadores que no son comparables. Dentro de calle/avenida el reordenamiento persiste (42,6 % cambia de cuartil), pero ese subgrupo también mezcla vías de mano única y de doble mano. **H8 "respaldada" no está sustentada como "riesgo por exposición".** La comparación por tipo de vía no es válida. No afecta a las conclusiones principales (H2, H4 y H5) | Restringir a sensores homogéneos (mismo tipo, mano única) o normalizar por sentido o carril. Corregir la unidad y retirar la comparación entre tipos de vía. Rebajar H8 a "indicativa o no concluyente" en el informe final, el storytelling y la web |
| R2 | **Mayor** | `05_clustering` §3–§5; `clustering_report.md:26`; `final_report.md` (perfiles) | **El perfil "de borde" equivale a un umbral sobre una sola variable.** La partición seleccionada coincide **exactamente** con la regla `pct_autopista_gralpaz > 0,20` (ARI 1,0). Con esa sola variable, la *silhouette* de la partición es 0,81. `pct_avenida` y `pct_autopista_gralpaz` son proporciones complementarias de la misma composición por tipo de vía y, al estandarizarlas, esa dimensión pesa doble. Núñez (0,175, limítrofe con la General Paz) queda justo bajo el corte. Las diferencias de modo (más autos, menos peatones) son en parte mecánicas: en una autopista no hay peatones. | Ejecutado: reproducción, reglas de umbral (ARI 0,905 con 0,10–0,15 y 1,0 con 0,20) y *silhouette* univariada | El perfil es **estable, pero casi tautológico**: separa los barrios que tienen autopista o General Paz. No es un artefacto del algoritmo, pero no aporta una tipología multivariada de siniestralidad. La asignación de los barrios cercanos al corte es arbitraria. H6 "parcialmente respaldada" se debilita; la recomendación de "prevención en vías rápidas para el borde" se deduce de la propia variable | Presentarlo como una partición geográfica explicada por una variable. Informar la regla univariada equivalente. Probar con una sola variable de vía (o con proporciones log-ratio) y mostrar la estructura que queda sin vía (*silhouette* ≤ 0,23, débil), que es el resultado multivariado real |
| R3 | Menor | `06_integrated_evaluation`, celda 28; `robustness_report.md:61`; `final_report.md:71` | Afirmaciones erróneas o no medidas sobre la "subrepresentación del borde": (a) "ninguno entra al top por conteo" es falso: Saavedra entra con la media de 12 meses en 10 de los 12 meses de 2025, y Liniers y Villa Lugano, una vez cada uno; (b) se sugiere usar la **densidad**, pero el borde tiene la menor densidad (log 3,63 frente a 3,77–3,94), así que esa alternativa lo desfavorecería más; (c) "subrepresenta las vías rápidas" no se midió: se midió la participación del grupo de barrios, no la de los hechos en vías rápidas | Ejecutado (a y b); por lectura (c) | La interpretación de equidad está sobreafirmada. No cambia los resultados principales | Corregir el texto. Medir la cobertura de los hechos en vías rápidas o reformular. Retirar la sugerencia de la densidad |
| R4 | Menor | `regression_report.md:40` y `:49`; `03_regression`, celdas 25 y 34 | (a) "Excluir la pandemia fue decisivo en las tres familias": en la NB2 del protocolo, excluirla **empeora** el MAE (22,57 frente a 5,06, por la inestabilidad de V2022). (b) "Todos los GLM subestiman (−0,87 a −1,46)": −0,87 es el sesgo del baseline de media de 12 meses; los GLM van de −1,22 a −1,46. El HGB **sobreestima** (+0,95) y eso no se menciona | Ejecutado (`grilla_validacion.csv` y `metricas_test.csv`) | Solo afecta a la redacción | Corregir las cifras y el texto |
| R5 | Menor | `06_integrated_evaluation`, celdas 10 y 12; `robustness_report.md:47` | El intervalo de desempate de la cobertura usa **200** semillas (`tie_cov(..., seeds=200)`), pero el informe y el notebook dicen 500 | Por lectura del código | Ninguno sustantivo: la amplitud es ≤ 0,05 pp | Igualar el código o el texto |
| R6 | Menor | `04_classification`, celdas 1, 27 y 38 (guía y lectura) | Se afirma que las probabilidades "están bien calibradas y se pueden leer como chances" a partir de **un solo año de test**. Contradice la cautela del informe y la sobreestimación en el borde (0,146 frente a 0,102). La celda 38 atribuye la ganancia marginal a "la composición por modo y el territorio", pero el SHAP no mide un aporte incremental. Solo la ablación sin composición respalda ese aporte, y solo en V2022. El territorio no se probó | Por lectura; cifras ejecutadas en la tabla de equidad | Sobreafirmación interpretativa | Alinear las celdas guía con el informe |
| R7 | Menor | `classification_report.md`, tablas de §1 y §2; `robustness_report.md` §2 | En el test se compara la P@10 **esperada** del modelo y de la media de 12 meses con la P@10 **R0** de la persistencia (0,733; la esperada es 0,746). La ventaja sobre la persistencia es menor que la informada (0,062 frente a 0,075) | Ejecutado (`metricas_test.csv`) | No cambia la conclusión | Usar la misma métrica en todas las filas |
| R8 | Menor | `classification_report.md:28`; `04_classification`, celda 16; `robustness_report.md:27` | Efecto del ganador: la ventaja de validación del logit seleccionado (+0,016) se eligió entre 56 configuraciones con diferencias de milésimas, así que es una estimación optimista. Describirla como "pequeña y **estable**" la sobrevalora. Con K = 15, el clasificador es **significativamente peor** en el test (IC por bloques [−0,84; −0,15] pp), y el informe de robustez (línea 27) lo resume como "resta 0,4 pp" sin el IC | Ejecutado (`cobertura_diferencias_vs_historial.csv`) | Refuerza la conclusión negativa; la redacción es algo favorable al modelo | Mencionar el sesgo de selección y el IC con K = 15 |
| R9 | Menor | `06_integrated_evaluation`, celda 12; `robustness_report.md` §1 | El oráculo es el top-K **realizado**, que incluye ruido de Poisson irreducible. "El margen que queda para cualquier modelo es de unos 1,9 pp" es una cota superior laxa: el techo alcanzable es menor. Además, el 92 % está dominado por el núcleo persistente de 5 barrios | Por lectura | Refuerza la conclusión principal; solo es un matiz de interpretación | Llamarlo "cota superior" y explicar que el techo alcanzable es menor |
| R10 | Menor | `src/profiles.py:51`; `clustering_report.md:32`; `05_clustering`, celda 2 | `pct_fin_de_semana` usa como denominador **todos** los hechos, aunque se documenta "sobre los hechos con hora". `bootstrap_ari` (`profiles.py:81`) aplica `np.unique` y en la práctica es un submuestreo sin repetición del 63 % de los barrios, no un *bootstrap* | Por lectura | Ninguno sustantivo | Corregir la documentación |
| R11 | Menor | `final_validation.md:4`, `:23` y `:101` | La cabecera dice que quedan pendientes P1, P2 y P4, y el dictamen dice P1, P4 y P6 (P6 figura como resuelto). Las pruebas son ahora 66, no 55 | Ejecutado (pytest) | Solo documentación | Actualizar |
| R12 | Menor | `07_storytelling`, mensajes finales y §1 | "El historial reciente **es el mejor predictor**": solo se mostró que los modelos probados no lo superan de forma relevante. También se afirma como un hecho que la caída de fines de 2019 "corresponde a un cambio de registro", aunque la consulta institucional no se envió | Por lectura | Leve exageración | Reformular: "ningún modelo probado lo supera de forma relevante" y "probable cambio de registro" |
| R13 | Menor | `06_integrated_evaluation` §4; `robustness_report.md` §3 (H7) | "La comuna es menos predecible" confunde la estabilidad del **orden** con la predictibilidad: son 15 unidades de tamaño parecido, con K = 3. La grilla de 1 km usa solo hechos geocodificados, con un faltante diferencial de los graves | Por lectura | Matiz sobre H7 "parcialmente respaldada" | Formularlo como "estabilidad del ranking" y mencionar el sesgo de geocodificación |
| R14 | Menor | `03_regression` §3; protocolo §4 | Con la exclusión de la pandemia (hiperparámetro elegido), V2022 entrena con solo **9 meses objetivo** (2020-01, 2020-02 y 2021-06 a 2021-12) y sin meses de marzo a mayo. Eso explica la inestabilidad de V2022 y de los GLM. Solo se documenta para gap = 1 | Ejecutado (máscaras de las particiones) | Ninguno sobre la conclusión. V2022 pesa un tercio en la selección con poca información | Declararlo en el informe de regresión |

No se encontraron hallazgos **críticos**.

## 2. Verificado sin problemas

- **Construcción de variables sin fuga.**
  - Todas las ventanas se desplazan s = h + gap antes de agregar. `y_lag12` y `ciudad_lag12` usan T − 12 ≤ L porque h + gap ≤ 12.
  - `top10_freq12` usa etiquetas R0 de meses ≤ L. Su desempate depende solo de la semilla y del ordinal del mes, no del futuro.
  - La composición y la vecindad usan ventanas que terminan en L.
  - *Ejecutado:* control de truncamiento independiente (12 de 12) y suite de pruebas (C3–C13).
- **Etiquetas y particiones.**
  - Hay exactamente 10 positivos por mes.
  - Con gap = 0 y gap = 1, el entrenamiento solo usa etiquetas observables al inicio de cada evaluación (C13).
  - El test 2025 no entra en ninguna partición de desarrollo.
  - Regresión y clasificación comparten filas y fechas.
  - No hace falta separación entre *folds* porque h = 1.
- **Ajuste dentro del *fold*.**
  - Escalado, codificación e imputación están dentro del `Pipeline`. La NB2 estandariza solo con el entrenamiento.
  - La ponderación de clases y la exclusión de la pandemia son hiperparámetros elegidos en validación.
  - El umbral de F1 se eligió con la validación agrupada.
- **Uso del test.**
  - Por el orden del código, la selección se congela en JSON antes de las celdas de test. *Por lectura:* las marcas de tiempo no se pudieron verificar de forma independiente.
  - Las reutilizaciones de 2025 están declaradas como exploratorias en la sección 11 del protocolo: la NB2-L2 *post hoc*, la sensibilidad gap = 1 y la auditoría del umbral 0,444. No cambian la selección.
  - `export_models.py` reajusta sin volver a seleccionar y verifica que las predicciones coincidan.
- **Baselines justos.**
  - Modelos y baselines ven la misma información (L = T − 1 − gap), en los mismos meses y barrios.
  - El mejor baseline se identificó en validación.
  - El intervalo de desempate es pareado (mismas etiquetas en cada semilla) y la incertidumbre entre meses se calcula aparte.
  - El intervalo degenerado del test ([0,017; 0,017]) es legítimo: el modelo no tiene empates, y solo 2 meses de 2025 tienen empate en el corte (*ejecutado*).
- **Cifras centrales.** Están reproducidas exactamente (sección de ejecución, punto 3), incluida la de **92 %** (92,0 % en test y 92,3 % en validación).
- **Desbalance y calibración.** La prevalencia es fija (20,8 %) y no requiere SMOTE. Las cifras de Brier con y sin ponderación coinciden: 0,069 frente a 0,089 en la media de la grilla, y 0,066 frente a 0,095 en la logística C = 0,01.
- **El resultado negativo no se debe a un *tuning* pobre.** Las alternativas sencillas probadas en validación no superan a la media de 12 meses. Ningún *fold* ni familia supera el umbral del 3 % ni el de ΔP@10 ≥ 0,02.
- **Clustering.**
  - Los atributos excluyen 2025 (hay prueba de perturbación).
  - La selección siguió la regla a priori, y el escalado y las subventanas no alteran la partición.
  - *Ejecutado:* reproducción con ARI 1,0.
- **Alcance de las afirmaciones.**
  - Los informes de los Pasos 07 a 10 distinguen predicción, exposición y causalidad.
  - Tratan los conteos como carga registrada.
  - Declaran que 2025 podría ser provisorio e informan V2024 como validación retrospectiva, que lleva a la misma conclusión.

## 3. Dictamen

**Apto con condiciones.**

**Conclusiones principales que se sostienen.**
- Ni la regresión ni la clasificación superan de forma relevante a la media de 12 meses fuera de muestra (H2 frente al mejor baseline, H4 y H5).
- El historial capta alrededor del 92 % de la ganancia sobre el azar respecto del oráculo realizado. Es una cota conservadora, que favorece todavía más al historial (R9).
- No se encontró fuga temporal ni uso del test para seleccionar.

**Conclusiones que deben acotarse antes de presentar.**
1. **H8 (R1).** El denominador de exposición no es comparable entre sensores. "Respaldada" debe rebajarse a "indicativa" hasta que se homogeneice la medición, y debe retirarse la comparación por tipo de vía.
2. **H6 y el perfil de borde (R2).** Es robusto, pero equivale a un umbral sobre la proporción de hechos en autopista o General Paz. Debe presentarse como una partición geográfica, no como una tipología multivariada de siniestralidad.
3. **Correcciones de redacción** de los hallazgos R3 a R14, ninguna de las cuales altera los resultados centrales.

**Condiciones de aprobación.** Corregir R1 y R2 en el informe de robustez, el informe de clustering, el informe final y el storytelling (y en la web, si reproduce esas cifras). Las correcciones menores pueden hacerse en la misma pasada.
