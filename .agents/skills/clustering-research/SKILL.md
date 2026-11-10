---
name: clustering-research
description: Compara y evalúa agrupamientos de perfiles históricos de zonas de CABA en el paso 09.
---

# clustering-research

- Fija período y cobertura mínima antes de calcular atributos de frecuencia, estacionalidad, horarios y composición. Distingue perfiles de volumen absoluto y perfiles relativos. Registra el tratamiento de zonas con pocos eventos y de denominadores nulos.
- Compara K-Means y jerárquico con un preprocesamiento comparable. Evalúa DBSCAN o HDBSCAN cuando la estructura de densidad lo justifique. Inspecciona sensibilidad a escalado, atributos, semillas y períodos. Para métodos con ruido, informa el porcentaje excluido al calcular métricas.
- Combina silhouette con estabilidad, tamaños de grupos e interpretación en unidades originales. Si la evidencia de separación es débil, documéntalo. Conserva los resultados futuros fuera de los atributos.
- Entrega el notebook previsto con alternativas, métricas, perfiles y justificación de la solución seleccionada.
