---
name: web-data-export
description: Diseña, genera y verifica las exportaciones agregadas de UrbanSafe para el mapa y el simulador web.
---

# Exportación de datos para la web

- Usa las salidas auditadas de los notebooks. Consulta `docs/web_implementation_plan.md` para el contrato. Regenera el paquete mediante un comando reproducible y conserva los archivos de investigación como insumos.
- Usa `id_barrio` como clave estable. Si una tabla o el GeoJSON trae nombres, crea una correspondencia verificada. Rechaza duplicados, claves sin correspondencia y pérdidas de filas al unir.
- Separa los conteos observados, los puntajes de cada estrategia y los resultados retrospectivos. Conserva mes objetivo, mes observable, horizonte y gap donde correspondan. Distingue cero observado y dato ausente.
- Exporta geometrías y agregados permitidos para publicación. Registra versión del esquema, fuentes, licencias, fecha de corte y hashes de los insumos en el manifiesto. Excluye filas individuales, modelos serializados y archivos de trabajo.
- Reconcilia el panel, las selecciones por mes y las coberturas con las fuentes. Revisa empates y la diferencia entre media de coberturas mensuales y cobertura agregada. Interrumpe la exportación ante discrepancias.
