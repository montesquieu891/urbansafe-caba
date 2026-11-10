# UrbanSafe CABA — Síntesis de hallazgos del AED

**Hito:** Paso 05. AED y análisis territorial  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:** [notebooks/01_EDA.ipynb](../notebooks/01_EDA.ipynb) (ejecutado de punta a punta), figuras en [reports/figures/01_EDA/](../reports/figures/01_EDA/), tablas en [reports/tables/01_EDA/](../reports/tables/01_EDA/) y métricas en [eda_metrics.json](../reports/tables/01_EDA/eda_metrics.json)

**Alcance.**
- **Período:** 2019-01 a 2024-12. El test provisorio de 2025 no se usó (D3).
- **Población:** siniestros **con víctimas** registrados por sumario policial: 54.066 hechos y 62.078 víctimas.
- **Unidades:** barrios (51.688 hechos asignados según D9) y meses.
- **Interpretación:** los conteos son **carga registrada**, no riesgo (no hay exposición, D8). La infraestructura solo se describe (D11). Los contrastes son exploratorios, con dependencia temporal y espacial y sin corrección por comparaciones múltiples.

---

## Hallazgos

Cada hallazgo indica la sección del notebook (§) donde está su evidencia.

### E1. La serie se recuperó del shock pandémico y tiene estacionalidad marcada (§1, `f1_temporal.png`)
- **Evidencia.**
  - Hechos por año: 10.155 (2019), 6.061 (2020; −40 %), 7.818, 9.536, 9.927 y 10.569 (2024).
  - Tendencia STL: unos 738 hechos por mes a comienzos de 2022 y unos 894 a fines de 2024, comparable al nivel de mediados de 2019.
  - Índice estacional 2022–2024: mínimo en **enero (0,75)** y máximo en **octubre (1,10)**.
  - Hechos por día: 32,3 los viernes y 17,3 los domingos.
- **Interpretación.** Para pronosticar el mes siguiente, el nivel reciente y el mes calendario son señales necesarias. Enero es sistemáticamente bajo (receso de verano).
- **Limitaciones.** El índice estacional usa solo 3 años. No se puede distinguir si la recuperación es de movilidad o de registro (E9).
- **Implicancia.** Paso 06: incluir rezagos (1, 2, 3 y 12 meses), medias móviles y mes calendario.

### E2. El conteo por barrio mezcla tamaño e intensidad (§2, `f2_mapas_barrio.png`)
- **Evidencia.**
  - Palermo tiene el mayor conteo (4.059 hechos; 7,9 %), pero ocupa el **puesto 21 en densidad**.
  - Las mayores densidades están en el centro y el centro-sur: Constitución 118,5, Balvanera 106,2 y Monserrat 101,6 hechos por km² y año.
  - El conteo se correlaciona con la superficie (Spearman 0,66) más que con la densidad (0,52).
- **Interpretación.** El top 10 por conteo, que es el objetivo D6, refleja la carga operativa, pero en parte también el tamaño del barrio.
- **Limitaciones.** La densidad por superficie no es riesgo, porque no hay exposición.
- **Implicancia.** Usar la superficie como atributo territorial. Presentar siempre la densidad junto al conteo (Pasos 10 y 11).

### E3. Motociclistas y peatones dominan la frecuencia y la gravedad (§3, `f3_actores.png`)
- **Evidencia.**
  - Participación entre los hechos con modo informado: moto 43–46 %, peatón 16–18 %, auto 12–15 %, bicicleta 11–13 % (17 % en 2020–2021) y transporte público 4–7 %.
  - Proporción KSI: peatón 10,7 %, moto 7,2 %, auto 4,2 %, bicicleta 3,8 % y transporte público 2,0 %.
  - Moto y peatón suman el **81 % de los hechos mortales**.
- **Interpretación.** La gravedad recae sobre los usuarios vulnerables.
- **Limitaciones.** Sin exposición por modo, una mayor participación no implica mayor riesgo por viaje. El modo es un atributo del hecho.
- **Implicancia.** Los perfiles del Paso 09 deberían separar la composición moto o peatón del resto.

### E4. El faltante de modo no es aleatorio (§3 y §8)
- **Evidencia.** El modo SD representa entre 9,7 % y 29,5 % según el año. Los hechos con modo SD tienen una proporción KSI de **0,17 %** y ningún mortal.
- **Interpretación.** El SD se concentra en hechos leves. Las participaciones calculadas sin SD describen mejor la gravedad que la frecuencia.
- **Limitaciones.** No se conoce el mecanismo de carga.
- **Implicancia.** Paso 06: tratar SD como una categoría explícita en las variables de composición y evaluar la sensibilidad (restricción del informe de viabilidad).

### E5. La frecuencia es diurna y la severidad es nocturna (§4, `f4_horario.png`)
- **Evidencia.** El pico es a las 17 h en días hábiles. De 0 a 5 h ocurre el 7,9 % de los hechos, con una proporción KSI de **10,5 %**, frente a 4,9 % en el resto del día. El máximo es de alrededor del 15 % a las 3 h (IC de Wilson separado de las horas diurnas).
- **Interpretación.** El patrón es compatible con mayor velocidad y menos tránsito de noche. **No se identifican causas.**
- **Limitaciones.** Hay 77 hechos sin hora. El intervalo de Wilson supone independencia entre hechos.
- **Implicancia.** Aporta a la caracterización de perfiles (Paso 09) y a la comunicación (Paso 11). No es una variable del panel mensual.

### E6. La carga está concentrada, agrupada en el espacio y es muy persistente a escala de barrio (§5, `f5_concentracion_persistencia.png`)
- **Evidencia.**
  - El Gini entre barrios es estable: 0,345–0,370.
  - I de Moran de la **densidad**: 0,47 (p de permutación = 0,0001). De los conteos: 0,21 (p = 0,008).
  - El top 10 anual tiene un Jaccard de 0,82 entre años; **7 barrios están en el top 10 todos los años**.
  - **El 68 % del top 10 mensual se repite el mes siguiente** (rango 40–90 %). Cinco barrios están en el top 10 en más del 86 % de los meses (Balvanera, Palermo, Flores, Caballito y Recoleta). **21 barrios nunca entran.**
- **Interpretación.** El problema de clasificación es, en la práctica, decidir unas **5 plazas inciertas** por mes. Ahí está el margen de un modelo frente a la persistencia, que será un baseline exigente (H2, H4 y H5). La autocorrelación espacial justifica incluir rezagos espaciales.
- **Limitaciones.** Con 48 unidades, el I de Moran tiene poca potencia y depende de la partición en barrios (unidad de área modificable).
- **Implicancia.** Paso 06: rezagos espaciales (media de los vecinos *queen*). Pasos 08 y 10: informar el desempeño también en las plazas inciertas, no solo la Precision@10 global.

### E7. A microescala los hotspots son menos persistentes (§5)
- **Evidencia.** En una grilla de 250 m (3.473 celdas), el 5 % superior reúne el 23,1 % de los hechos. Su superposición entre 2022 y 2024 tiene un Jaccard de 0,33; el orden general de las celdas, un Spearman de 0,72.
- **Interpretación.** La persistencia depende de la escala. Esto es consistente con D1 y con lo que anticipa H7, como observación preliminar.
- **Limitaciones.** Es descriptivo. El contraste formal de H7 corresponde al Paso 10.

### E8. La pandemia cambió el nivel y el modo, no la geografía (§6, `f6_periodos.png`)
- **Evidencia.**
  - Hechos por mes: 905,8 (prepandemia), 486,7 (pandemia; −46 %) y 818,7 (pospandemia).
  - La bicicleta pasa de 10,8 % a 17,9 % y vuelve a 12,7 %; el transporte público baja de 6,5 % a 3,7 %.
  - Spearman de la participación por barrio entre períodos: 0,94–0,96. Ningún barrio cambia más de 0,8 pp.
- **Interpretación.** El shock fue de nivel y de modo. Esto respalda un objetivo relativo por mes (D6) y conservar los meses de pandemia con una marca (D3).
- **Limitaciones.** La prepandemia tiene solo 10 meses. El SD de modo sube en la pandemia.

### E9. Gravedad y localización dependen de procesos de registro cambiantes (§8, `f8_faltantes.png`)
- **Evidencia.**
  - Faltan coordenadas en el 2,9–6,6 % del total de hechos, pero en los **graves** el faltante va de 5,9 % (2019) a 27,7 % (2021).
  - Entre años, la proporción de graves registrados y su faltante de coordenadas se correlacionan (Spearman 0,66, con n = 6).
  - Casi todos los hechos sin coordenada tampoco tienen comuna (513 de 516 en 2021): su distribución territorial **no es identificable**.
  - La relación entre noviembre-diciembre y septiembre-octubre es **0,61 en 2019** y 0,93–1,32 en los demás años.
- **Interpretación.** Confirma que la gravedad territorial debe ser **solo descriptiva** (D5) y que la caída de fines de 2019 es un problema de registro (D3). Una hipótesis compatible es que los graves identificados por relevamiento hospitalario lleguen con menos ubicación.
- **Limitaciones.** Es una hipótesis hasta que responda la consulta institucional (preguntas 2 y 3). Los hechos sin ubicación son el 4,0 % del desarrollo, así que, en el peor caso, la participación de un barrio podría estar sesgada hasta unos 4 pp.

### E10. Las avenidas concentran los hechos mucho más que su longitud; la infraestructura actual se asocia con la densidad por centralidad (§7, `f7_infraestructura.png`, solo descriptivo)
- **Evidencia.**
  - El **64,3 % de los hechos** de 2020–2024 ocurrió en avenidas, que son el **23,5 % de los km** de la red: unas 2,7 veces su peso.
  - Por barrio, la densidad de hechos se asocia con la densidad de cruces semaforizados (Spearman 0,77) y con los km de vías por km² (0,36). No se asocia con la proporción de km de avenidas (−0,01).
- **Interpretación.** Los semáforos son un indicador de centralidad y de tránsito no observado, no una causa. **D11 se mantiene:** la infraestructura vigente no se usa para pronosticar.
- **Limitaciones.** Es el estado de 2026 y la comparación es transversal. Hay 106 cruces sin barrio asignable.

---

## Implicancias para los pasos siguientes

| Paso | Implicancia | Hallazgo |
|---|---|---|
| 06 | Rezagos de 1, 2, 3 y 12 meses, medias móviles, mes calendario y marcas de anomalía | E1, E8, E9 |
| 06 | Superficie del barrio y rezago espacial (media de los vecinos *queen*) | E2, E6 |
| 06 | Composición por modo con SD explícito; sensibilidad sin composición | E3, E4 |
| 06 | Ninguna variable de infraestructura vigente (D11) | E10 |
| 07–08 | La persistencia y la media de 12 meses serán baselines fuertes; métricas en las plazas inciertas del top 10 | E6 |
| 07 | La binomial negativa sigue justificada; la variación entre años es en parte de registro | E1, E9 |
| 09 | Perfiles por composición modal, hora y estacionalidad; la severidad nocturna como descriptor | E3, E5 |
| 10 | Sensibilidad a la escala (comuna, grilla) con persistencia diferencial; densidad junto al conteo | E2, E7 |

## Verificación del criterio de aceptación del Paso 05

Criterio del plan: *"cada hallazgo relevante contiene evidencia, interpretación y limitaciones"*.

| Análisis del plan | Sección del notebook | Hallazgo |
|---|---|---|
| 1. Evolución temporal, tendencia y estacionalidad | §1 | E1 |
| 2. Distribución territorial | §2 | E2 |
| 3. Peatones, motociclistas, ciclistas y automovilistas | §3 | E3, E4 |
| 4. Horarios y días | §4 | E5 |
| 5. Concentración espacial y persistencia de hotspots | §5 | E6, E7 |
| 6. Comparación de períodos, incluida la pandemia | §6 | E8 |
| 7. Relaciones con la infraestructura disponible | §7 (descriptivo, D11) | E10 |
| 8. Faltantes y sesgos de registro | §8 | E4, E9 |

- Los diez hallazgos (E1–E10) tienen evidencia cuantitativa con su figura o tabla, interpretación y limitaciones.
- El notebook usa pandas como herramienta central, con Matplotlib y GeoPandas, y se ejecutó con kernel limpio sin errores.
- Los colores siguen la paleta categórica y secuencial validada. Los mapas distinguen conteo, densidad y proporción.

**Dictamen (autoauditoría).** El criterio se cumple. Queda pendiente la revisión del responsable.
