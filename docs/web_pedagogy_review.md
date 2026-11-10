# Revisión pedagógica del simulador y los perfiles

Fecha: 2026-11-10. Revisión del contenido, jerarquía visual e interacción de las dos vistas a pedido del responsable. Cambios preparados en la web local; este trabajo no publica una nueva versión.

## Diagnóstico

Las vistas presentaban resultados antes de establecer su pregunta. «Clasificador», «cobertura», «oráculo» y «K» exigían conocimiento previo. El encabezado del atlas seguía describiendo observación histórica en todas las vistas. En perfiles, los nombres de grupos no explicaban sus rasgos ni por qué seguían iguales al cambiar el mes. Los conteos de la ficha podían confundirse con la variable que define el grupo. El selector de mes del simulador aparecía después de sus resultados.

## Cambios

| Vista | Pregunta | Lectura propuesta |
|---|---|---|
| Simulador 2025 | ¿Un modelo elige mejor que el historial? | Elegir un mes y un cupo de barrios → comparar las selecciones con el historial → comprobar qué parte de los hechos posteriores ocurrió en esos barrios. |
| Perfiles barriales | ¿Qué barrios comparten un perfil vial? | Identificar rasgos comunes de los registros históricos → explorar los grupos → formular preguntas de diagnóstico, sin interpretarlos como niveles de peligrosidad. |

El simulador incorpora tres pasos, definiciones en contexto y una explicación dinámica con numerador, denominador, porcentaje y diferencia de hechos frente al historial para el mes elegido. Se explicita que cubrir hechos no significa evitarlos. El mes objetivo precede a los resultados. Los conceptos azar, oráculo y fracción de ganancia del 92 % se explican en un desplegable, sin competir con la primera lectura. Las estrategias tienen nombres acompañados por su tarea y una explicación específica.

Los perfiles incorporan tarjetas con rasgos, preguntas de exploración y una ficha contextual del grupo. Se diferencia el grupo principal de borde de la subdivisión débil del interior. Las descripciones cualitativas provienen de `docs/clustering_report.md`, sección 5, y sus tablas de perfiles; no se inventaron nuevos indicadores. Se aclara que son rasgos del grupo, no afirmaciones causales sobre cada barrio. Los conteos de la ficha quedan rotulados como contexto observado del mes, separado del perfil histórico fijo.

Ambas vistas tienen encabezados propios y una guía para leer el mapa. El mapa del simulador muestra pertenencia a listas; el de perfiles, semejanza histórica. Ninguno usa los colores como escala de peligrosidad. Se conserva el estado compartido, los datos y las selecciones congeladas.

## Verificación

Revisión visual de ambas vistas en escritorio y móvil; capturas en `docs/evidence/web_phase3/`. TypeScript y compilación estática aprobados. Se mantuvieron las pruebas de cifras, selecciones, empates, URL, navegación y accesibilidad. Se añadió un recorrido que comprueba la pregunta guía, la interpretación mensual, las tarjetas y que cambiar el mes no cambia el perfil.

No se hizo una prueba de comprensión con lectores externos. La revisión mejora la explicitación del propósito y la lectura, pero no demuestra por sí sola que todas las audiencias comprendan la herramienta. Una próxima evaluación útil sería pedir a un lector que explique con sus palabras qué significa una cobertura del 43 % y qué representa el color de un barrio en la vista de perfiles.

## Reconciliación de la procedencia

El `--check` estricto detectó una diferencia en `manifest.json`. La causa: el manifiesto publicado registró el hash del exportador **antes** de que Git normalizara sus finales de línea (`.gitattributes` fija `eol=lf`). Después de un checkout, la copia de trabajo quedó con LF y su hash cambió aunque el código fuera el mismo. `docs/source_register.csv` tenía el mismo problema latente: en esta máquina está con CRLF, pero un clon nuevo lo trae con LF, y `--check` fallaría en otra computadora.

Corrección: `scripts/export_web_data.py` calcula el hash de los insumos de texto (`.py`, `.md`, `.csv`, `.json`, `.geojson`) tras normalizar CRLF a LF, y deja esa regla en `manifest.definiciones.hash_insumos`. Una prueba nueva comprueba que la procedencia no cambia con los finales de línea y que los binarios no se alteran.

- Los cinco archivos de datos públicos quedan **idénticos byte a byte**; no cambia ninguna cifra, selección ni geometría.
- Solo cambia `manifest.json`: los hashes de `panel`, `fuentes` y `exportador`, y con ellos la versión derivada, de `2019-2025-5685c2f9c0a0` (publicada) a `2019-2025-692728914e40`.
- `--check` aprobado sin discrepancias; pytest de exportador, etiquetas y evaluación: 20 aprobadas.

## Resultado de pruebas

`npm run test:release`: `astro check` sin errores, compilación sin advertencias, `audit:dist` aprobado (JS inicial 27 kB, dentro del límite de 60 kB) y **40/40 E2E** (20 recorridos × escritorio y móvil). Se suman dos recorridos pedagógicos nuevos, uno de los cuales contrasta la lectura del mes con la referencia independiente de Python. La lectura mensual nombra el mes («En enero de 2025») en lugar de la clave `2025-01`.

Las descripciones de los perfiles se contrastaron con la tabla de §5 de `docs/clustering_report.md`:

- **Borde:** vías rápidas 35 % frente a 2 %, auto 19 % frente a 12 %, moto 49 % frente a 44 %; menos peatones (12 % frente a 18 %) y bicicletas (8 % frente a 13 %).
- **Residencial:** más moto (47 % frente a 41 %) y bicicleta (15 % frente a 11 %) que el central-denso.
- **Central-denso:** más peatones (20 % frente a 16 %) y transporte público (8,5 % frente a 5,5 %) que el residencial.

El encabezado («modos, tipos de vía y momentos de ocurrencia») coincide con los atributos del agrupamiento, que excluyen volumen y densidad (§2).

La implementación comenzó en Codex y la revisión y reconciliación se hicieron en Claude Code: es una autoauditoría. Estos cambios todavía no están publicados.

## Segunda revisión: propuesta antes que método (simulador)

Pedido del responsable: el bloque inicial «parecía una clase de estadística». Debía dejar claros la propuesta, el problema, la pregunta y cómo el mapa ayuda a entender la realidad.

Cambios:

- **Orden de lectura.** Primero la pregunta («¿Qué barrios conviene atender primero cada mes?»). Después tres tarjetas: *El problema* (recursos para pocos barrios), *La pregunta* (¿un modelo elige mejor que mirar el último año?) y *La respuesta con datos de 2025*. Más abajo, *Cómo usarlo*, con cuatro acciones, y el límite de alcance.
- **Respuesta calculada, no escrita a mano.** «Prácticamente empatados» y las cifras de 42,7 % y 43,1 % salen de `cobertura.json` (10 barrios, modelo de clasificación frente al historial). El veredicto depende de si el IC por bloques incluye el cero. «Casi toda la ventaja posible frente al azar» traduce la fracción de ganancia del 92 % y solo se muestra si es al menos 0,85.
- **Sin jerga en el texto visible.** K → «barrios a atender»; cobertura → «porcentaje de siniestros dentro de la elección»; gap → «datos hasta el mes anterior»; IC → «margen de incertidumbre»; estrategias → «métodos», con nombres llanos. Los términos técnicos siguen definidos en el desplegable «Detalle técnico». Una prueba E2E comprueba que el texto visible del simulador no contenga «K =», «cobertura» ni «gap».
- **Mapa y ficha.** La leyenda dice quién eligió cada barrio («Elegido por los dos», «Solo por el método», «Solo por el historial», «No elegido»). La ficha traduce el puntaje de cada método a su significado, por ejemplo «probabilidad estimada de estar entre los 10 con más siniestros».

No cambian datos, selecciones ni cifras. Verificación: `npm run test:release` con 40/40 E2E (escritorio y móvil, incluida la accesibilidad automática de los colores nuevos) y auditoría aprobada (JS inicial 28,8 kB). Revisión visual en escritorio y móvil con capturas en `docs/evidence/web_phase3/`. Sigue pendiente una prueba de comprensión con lectores externos.
