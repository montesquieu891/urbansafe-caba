---
name: spatiotemporal-ml
description: Diseña variables, regresión de conteos y clasificación temporal para anticipar concentración de siniestros en UrbanSafe CABA en los pasos 06–08.
---

# spatiotemporal-ml

- Define unidad, horizonte, fecha de corte y disponibilidad real de cada predictor. Genera rezagos y ventanas por zona ordenada, con desplazamiento previo a la agregación. Excluye registros publicados después del corte, incluso si corresponden a fechas anteriores.
- Congela un test cronológico. Comparte fechas de partición entre zonas y tareas cuando el horizonte coincida. Usa validación expansiva con separación suficiente si las ventanas objetivo se solapan. Ajusta imputación, escalado, selección, remuestreo, calibración, hiperparámetros y umbrales solo con datos permitidos por el fold y sin consultar test.
- Prueba que cambiar datos posteriores al corte deja intactas las features previas, que los lags no cruzan zonas y que los períodos objetivo de entrenamiento no invaden la evaluación. Comprueba cobertura y unicidad del panel.
- Compara con persistencia e historial estacional según disponibilidad. Para conteos, evalúa Poisson y binomial negativa si hay sobredispersión, además del modelo de árboles del plan. Para clasificación, mide PR-AUC, calibración y Precision@K junto con las métricas del plan.
- Entrega protocolo, notebooks y resultados fuera de muestra, con estabilidad temporal y territorial y criterios de selección trazables.
