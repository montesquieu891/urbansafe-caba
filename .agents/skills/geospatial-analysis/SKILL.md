---
name: geospatial-analysis
description: Analiza coordenadas, uniones espaciales, mapas y concentración territorial de siniestros de CABA en los pasos 03, 05 y 10.
---

# geospatial-analysis

- Registra CRS de origen, orden de ejes, vigencia de límites oficiales y método de asignación. Usa GeoPandas y un CRS proyectado apropiado para áreas o distancias. Cuantifica puntos inválidos, fuera de CABA, en límites y con múltiples coincidencias. Reconcilia totales antes y después de la unión.
- Compara barrio y comuna antes de proponer grillas. Para hotspots, declara unidad, período y persistencia. Si evalúas autocorrelación, declara vecindad, islas, hipótesis y sensibilidad a escala o pesos.
- Distingue conteos, densidad por superficie y tasas por exposición. Usa denominadores comparables en zona y período. Para sensores parciales, limita el análisis a corredores cubiertos. Representa sin datos y cero observado de forma diferenciada.
- Entrega un notebook reproducible con capas y CRS documentados, controles de asignación, mapas y límites de interpretación.
