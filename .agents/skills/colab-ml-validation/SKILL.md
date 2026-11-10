---
name: colab-ml-validation
description: Audita Colabs de feature engineering, regresión, clasificación, priorización top-K y clustering de UrbanSafe para detectar fuga temporal y validar resultados.
---

# Auditoría de machine learning en Colabs

Lee el plan y, si existe, `docs/experimental_protocol.md`. Registra diferencias entre protocolo, notebook y módulos importados.

- **Cortes y disponibilidad.** Reconstruye objetivo, horizonte, fecha de corte y primer mes de evaluación de cada fold. Comprueba por separado disponibilidad de variables y etiquetas de entrenamiento. Para `gap=1`, pronosticar enero con datos hasta noviembre implica excluir diciembre también del ajuste. Perturba datos posteriores al corte y verifica que los predictores anteriores no cambien. Contrasta fechas de publicación y revisiones cuando haya evidencia.
- **Selección y ajuste.** Verifica que imputación, escalado, selección de variables, remuestreo y calibración respeten los folds. Comprueba que la elección de hiperparámetros y umbral no consulte el test. Distingue validación usada para seleccionar de test reservado. No abras etiquetas de test ni generes métricas nuevas de test antes del momento fijado en el protocolo.
- **Comparaciones.** Reconstruye al menos una métrica desde predicciones guardadas o validación. Alinea meses, barrios, objetivo y horizonte con el baseline. Para top-K compara modelo y baseline con las mismas etiquetas en cada simulación de desempate. Separa esa sensibilidad de la incertidumbre entre períodos. Distingue cobertura de hechos, Precision@K y probabilidades calibradas.
- **Clustering.** Audita ventana de atributos, escalado, efecto de cobertura, estabilidad por semilla o período y tamaño de grupos. Busca perfiles que solo separan por volumen y resultados que dependen de una sola configuración.
- **Dictamen.** Señala hallazgos por severidad con celda o función, evidencia mínima reproducible, impacto y prueba que permitiría cerrar cada punto. Distingue una comprobación que ejecutaste de una inferencia por lectura y registra si fue revisión independiente o autoauditoría.
