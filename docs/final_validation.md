# UrbanSafe CABA — Validación final y entrega

**Hito:** Paso 12  
**Estado:** aprobado por el responsable el 2026-11-10. Cerrado, con las condiciones P1, P2 y P4 pendientes de la sección 5  
**Fecha:** 2026-11-10  
**Skills aplicadas:** `validate-data`, `ml-scientific-reviewer` y `colab-reproducibility-audit`  
**Evidencia:** [docs/evidence/paso12/](evidence/paso12/), [`scripts/check_traceability.py`](../scripts/check_traceability.py) y [`scripts/export_models.py`](../scripts/export_models.py)

---

## 1. Reproducción desde un entorno limpio

**Procedimiento.**
- Se copiaron a una carpeta nueva solo los archivos versionables (`git ls-files`, 93 archivos), sin datos, salidas ni modelos.
- Se creó un entorno virtual nuevo, instalado únicamente desde `requirements.txt` (Python 3.13.7).
- Se ejecutaron en orden los pasos del [README](../README.md).

| Paso | Resultado |
|---|---|
| `python -m src.data_processing --download` (descarga del CDN oficial) | ✔ Los 10 archivos fuente se verificaron por SHA-256 |
| Hashes de los 5 datos procesados frente a [processed_sha256.txt](evidence/paso04/processed_sha256.txt) | ✔ 5 de 5 idénticos |
| `python -m src.features` | ✔ 4.032 filas; 2.880 completas en desarrollo y 576 en test |
| `python -m pytest -q tests` | ✔ **55 de 55** |
| Notebooks `00` → `07` en orden (`nbconvert --execute`) | ✔ Los 8 corrieron sin errores (alrededor de 13 minutos) |
| `python scripts/export_models.py` | ✔ Modelos con el **mismo SHA-256** que en la versión de trabajo; sus predicciones de 2025 coinciden con las de los notebooks |

**Estado: reproducido.** Se trata de una reproducción en Jupyter local, no en Colab.

## 2. Comparación de salidas: sala limpia frente a versión de trabajo

Todas las salidas de `reports/` se compararon. Los CSV se compararon con tolerancia relativa de 10⁻⁶. Los JSON también, sin contar las marcas de tiempo. Las figuras se compararon píxel a píxel.

| Tipo | Idénticos | Con diferencias |
|---|---|---|
| Tablas CSV | 68 | 4: **solo orden** de columnas o filas |
| Métricas JSON | 7 | 2: **solo orden** de una lista |
| Figuras PNG | **31** | 0 |

**Causa y corrección.** Los notebooks 03 y 04 recorrían los "mejores modelos por familia" con un `set()`, cuyo orden depende de la semilla de hash de Python. Los valores eran idénticos al alinear por modelo o por barrio-mes; la única diferencia restante era `NaN` frente a `NaN`. Se cambió a `sorted(set(...))` y se volvieron a ejecutar ambos notebooks. Una nueva ejecución del notebook 03 con otra semilla (`PYTHONHASHSEED=999`) produjo archivos **idénticos byte a byte**. El detalle está en [comparacion_sala_limpia.json](evidence/paso12/comparacion_sala_limpia.json).

## 3. Trazabilidad de fuentes, decisiones y cifras

- **Enlaces.** Los **122 enlaces** relativos del README, de `docs/` (incluido este informe) y de `presentation/` resuelven a archivos existentes ([trazabilidad.json](evidence/paso12/trazabilidad.json)).
- **Cifras de comunicación.** Las **16 cifras clave** del informe final y de la presentación coinciden con los artefactos que las generan, dentro del redondeo informado: hechos y víctimas, 81 % de mortales, persistencia del 68 %, coberturas del 42,7 %, 43,1 % y 44,6 %, 92 % de la ganancia, MAE, P@10, *silhouette*, 43 % de cambio de cuartil y equidad del borde.
- **Recálculo independiente** desde la fuente cruda y el panel, sin artefactos intermedios:
  - hechos 65.818;
  - mortales moto o peatón 81,0 %;
  - cobertura del top 10 por media de 12 meses en 2025: 42,73 % (oráculo 44,62 %);
  - MAE de la media de 12 meses en 2025: 4,0622.

  Todo coincide.
- **Cadena de decisiones.**
  1. Las fuentes ([source_register.csv](source_register.csv)) tienen hashes.
  2. La viabilidad ([feasibility_report.md](feasibility_report.md)) fija las decisiones D1–D11.
  3. El protocolo ([experimental_protocol.md](experimental_protocol.md)) fija las reglas a priori y registra las desviaciones.
  4. Las selecciones de los Pasos 07 y 08 están congeladas en JSON.
  5. Los informes de cada paso tienen dictamen.
  6. El [informe final](final_report.md) integra los resultados.

## 4. Matriz de cumplimiento académico (plan, sección 4)

| Requisito del curso | Evidencia | Estado |
|---|---|---|
| Elección del tema y objetivo | [research_proposal.md](research_proposal.md) (preguntas, objetivos, H1–H8) | ✔ |
| Investigación y selección de datasets | [data_inventory.md](data_inventory.md), [source_register.csv](source_register.csv), [feasibility_report.md](feasibility_report.md) y `notebooks/00_data_audit.ipynb` | ✔ |
| Repositorio y ambiente | Repo privado en GitHub; `requirements.txt` con versiones fijas; README reproducido en una sala limpia (§1) | ✔ |
| AED, transformación y visualización con pandas | `src/data_processing.py`, `notebooks/01_EDA.ipynb` y [eda_findings.md](eda_findings.md) | ✔ |
| Feature engineering | `src/features.py`, `notebooks/02_feature_engineering.ipynb` y [experimental_protocol.md](experimental_protocol.md) (13 controles de fuga) | ✔ |
| Modelo de regresión supervisada | `notebooks/03_regression.ipynb`, [regression_report.md](regression_report.md) y `models/regresion_final.joblib` | ✔ |
| Modelo de clasificación supervisada | `notebooks/04_classification.ipynb`, [classification_report.md](classification_report.md) y `models/clasificacion_final.joblib` | ✔ |
| Tuning y prevención del sobreajuste | Validación temporal expansiva, grillas acotadas, selección y umbral congelados antes del test, test usado una vez | ✔ |
| Clustering y mejora | `notebooks/05_clustering.ipynb` y [clustering_report.md](clustering_report.md) (alternativas, estabilidad, selección a priori) | ✔ |
| Storytelling y presentación | `notebooks/07_storytelling.ipynb`, [final_report.md](final_report.md) y [presentation/](../presentation/) (deck de 13 diapositivas) | ✔ |

**Entregables del Paso 12.**

| Entregable | Estado |
|---|---|
| Repositorio | ✔ |
| Documentación (13 documentos en `docs/`) | ✔ |
| 8 notebooks | ✔ |
| Modelos (`models/`) | ✔ |
| Figuras (31 en `reports/figures/`) | ✔ |
| Presentación | ✔ |

## 5. Pendientes y limitaciones conocidas

| # | Tema | Impacto | Acción sugerida |
|---|---|---|---|
| P1 | **Sin revisión independiente del modelado.** Los dictámenes de los Pasos 06 a 10 son autoauditorías; una revisión externa ya encontró una fuga (corregida) | Medio | Encargar una revisión independiente antes de presentar (AGENTS.md: un agente distinto, si se autoriza la delegación) |
| P2 | Consulta institucional **no enviada** | Bajo; no bloquea | Enviarla para confirmar la provisionalidad de 2025 y la caída de 2019 |
| P3 | 2025 posiblemente provisorio | Medio para el test | V2024 retrospectiva da la misma conclusión |
| P4 | La presentación es un artifact **privado** | Bajo | Compartirla o exportarla a PPTX o PDF desde *Share* para la entrega |
| P5 | El archivo del plan tiene finales de línea solo CR (cambio externo) | Bajo: dificulta los diffs | Volver a guardarlo con LF |
| P6 | ~~Los cambios de los Pasos 05 a 12 no estaban commiteados~~ | — | **Resuelto:** PR #1 fusionado en `main` (commit `36d4078`) |

## 6. Dictamen final

**Tipo de revisión.** **Autoauditoría** de validación de datos y de reproducibilidad. Se hizo con ejecución real en un entorno limpio, no solo por lectura.

**Dictamen: apto para la entrega, con las condiciones P1, P4 y P6.**
- El proyecto **se reproduce desde las fuentes oficiales** siguiendo el README: los datos procesados quedan idénticos por hash, las 55 pruebas pasan, los 8 notebooks corren en orden y las 31 figuras son idénticas píxel a píxel.
- Las métricas coinciden, y la única fuente de no determinismo encontrada (el orden) quedó corregida.
- Las cifras comunicadas se pueden rastrear hasta su artefacto y, para las centrales, recalcular desde la fuente cruda.
- Las conclusiones están respaldadas por la evidencia y acotadas por sus límites: el historial es casi óptimo, los modelos no lo superan de forma relevante, hay un perfil de borde robusto y no se hacen afirmaciones causales ni de riesgo por exposición.

## 7. Verificación del criterio de aceptación del Paso 12

Criterio del plan: *"cumplimiento completo de la consigna, reproducibilidad y conclusiones respaldadas por evidencia"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Ejecutar el proyecto desde un entorno limpio | ✔ | §1 |
| Verificar la trazabilidad de fuentes y decisiones | ✔ | §3 |
| Reproducir métricas y figuras | ✔ | §2 (68 + 7 + 31 idénticos; el orden quedó corregido) |
| Los notebooks funcionan en orden | ✔ | §1 |
| README suficiente | ✔ | Es el único insumo de la sala limpia (§1) |
| Cumplimiento de la consigna | ✔ | §4 |
| Conclusiones respaldadas por evidencia | ✔ | §3 y §6 |
