# Registro de la consulta institucional

**Hito:** Paso 02  
**Destinatario:** Observatorio de Movilidad y Seguridad Vial (OMSV), Dirección General de Seguridad Vial, Secretaría de Transporte del GCBA

## Estado

| Campo | Valor |
|---|---|
| Estado | **Borrador. No enviado.** |
| Fecha de redacción | 2026-11-10 |
| Responsable del envío | Responsable del proyecto. El envío no se hace desde el entorno automatizado. |
| Canales posibles | Los formularios de contacto que figuran en los metadatos CKAN del conjunto `victimas-siniestros-viales`: `encontacto.buenosaires.gob.ar` y `bacolaborativa.buenosaires.gob.ar`. Hay que confirmar cuál corresponde al OMSV antes de enviar. |
| Fecha de envío | — |
| Respuesta | — |
| Efecto sobre el plan | Ninguno bloqueante. La respuesta no es un requisito para continuar (plan, Paso 02). |

Si hay respuesta, se registrará aquí con su fecha y su contenido, y se actualizarán el [inventario](data_inventory.md) y el [registro de fuentes](source_register.csv).

## Texto propuesto

> **Asunto:** Consulta académica sobre las bases de siniestros viales 2019–2025
>
> Estimado equipo del Observatorio de Movilidad y Seguridad Vial:
>
> Desarrollo un proyecto académico de ciencia de datos sobre la distribución territorial de la siniestralidad vial en la Ciudad. Utilizo las bases abiertas "Siniestros viales" (hechos y víctimas, 2019–2025) publicadas en BA Data y su documento de notas metodológicas. Quisiera hacerles algunas consultas para interpretar correctamente los datos:
>
> 1. **Series anteriores.** ¿Existe una serie comparable anterior a 2019, o una forma recomendada de empalmar la base 2010–2016 de la PFA con la actual?
> 2. **Inclusión y exclusión.** ¿Hubo cambios en los criterios de inclusión, en la clasificación de gravedad o en el relevamiento hospitalario entre 2019 y 2025? En particular, ¿hay alguna explicación para la menor cantidad de hechos de noviembre y diciembre de 2019 y para el nivel de 2025? ¿Los datos de 2025 son definitivos?
> 3. **Geocodificación.** ¿Cómo se geocodifican los hechos? ¿Por qué cerca del 15 % de los siniestros graves no tiene coordenadas? ¿En qué sistema de referencia está el campo `geocodificacion_plana`?
> 4. **Diccionarios.** Las notas mencionan solapas "Diccionario Hechos" y "Diccionario Víctimas", pero no aparecen en los archivos publicados. ¿Podrían compartirlas?
> 5. **Tránsito.** ¿Hay series históricas de volumen vehicular, por sensor o por corredor, para 2019–2023, comparables con la base 2024 publicada?
> 6. **Zonas críticas.** ¿Qué metodología utiliza el Observatorio para identificar zonas o puntos críticos?
> 7. **Intervenciones.** ¿Existen registros georreferenciados y fechados de intervenciones viales (por ejemplo, ciclovías, áreas de prioridad peatonal o cambios de semaforización) entre 2019 y 2025?
> 8. **Infraestructura.** ¿Hay versiones históricas del callejero o de la red de cruces semaforizados?
>
> El uso será exclusivamente académico. Se citará la fuente según la licencia de los datos.
>
> Muchas gracias.

## Origen de cada pregunta

| Pregunta | Origen |
|---|---|
| 1, 6, 7 | Consultas previstas en el plan (Paso 02) |
| 2 | Irregularidades de la serie mensual y anual (inventario, sección 3.1) |
| 3 | Faltante de coordenadas no aleatorio por gravedad (inventario, sección 3.1) |
| 4 | Discrepancia entre las notas metodológicas y los archivos publicados |
| 5 | Exposición limitada a 2024 (inventario, sección 5) |
| 8 | Riesgo de fuga temporal por usar infraestructura estática (supuesto S7) |
