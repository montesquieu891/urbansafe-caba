---
name: colab-data-audit
description: Audita la integridad de los datos, las transformaciones, los cálculos y las conclusiones descriptivas en Colabs de ETL y análisis exploratorio de UrbanSafe.
---

# Auditoría de ciencia de datos en Colabs

1. Reconstruye la trazabilidad desde las fuentes hasta las tablas y gráficas. Para cada entrada o cruce clave, identifica versión, cobertura, unidad, clave, cardinalidad y recuentos antes y después. En UrbanSafe, un hecho puede tener varias víctimas. Comprueba que los conteos de hechos no se multipliquen al unir ambos archivos.
2. Contrasta el panel de barrio × mes con los totales de origen. Separa cero observado, dato faltante y período sin cobertura. Cuantifica exclusiones, duplicados, cambios de registro y cobertura espacial y temporal. Para joins geográficos, verifica CRS, asignación por cercanía, límites y coincidencias múltiples.
3. Recalcula independientemente una cifra central desde la tabla de menor granularidad disponible. Contrasta el valor, el denominador y los filtros con el notebook, las gráficas y el informe. Si comparas lluvia con horas secas, incluye las horas cubiertas sin hechos y compara horarios y períodos equivalentes.
4. Clasifica los resultados como conteo, densidad, tasa por exposición o asociación. Verifica que los denominadores sean compatibles y que la conclusión tenga el mismo alcance que el cálculo.
5. Entrega hallazgos con celda, recuentos o cifras verificables, efecto sobre la conclusión y corrección propuesta. Identifica qué insumos faltantes limitan la auditoría.
