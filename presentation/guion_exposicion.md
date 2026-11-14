# UrbanSafe CABA — Guion de exposición (15 o 30 minutos)

> **Para qué sirve este documento.** Es un guion para hablar, no para leer en voz alta palabra por palabra. Cada bloque tiene un objetivo, un texto sugerido en tono oral, las cifras que conviene tener a mano y una transición al bloque siguiente. Las partes marcadas **[30']** son ampliaciones para la versión larga; si tenés 15 minutos, saltealas.
>
> **Apoyos.** La presentación de 13 diapositivas (`presentation/deck_source`), el sitio web (https://urbansafe-caba.urbansafe-atlas.workers.dev) y el repositorio público (https://github.com/montesquieu891/urbansafe-caba). Todas las cifras de este guion salen de los informes de `docs/` en su versión corregida tras la revisión independiente del 13 de noviembre de 2026.

---

## 0. El mensaje en una frase

**Los siniestros viales con víctimas en CABA se concentran y se repiten tanto en los mismos barrios que el promedio de los últimos 12 meses ya es una guía muy difícil de superar: ninguno de los 94 modelos que probamos lo mejora de forma relevante, y demostrarlo con una evaluación honesta es el principal resultado del proyecto.**

Tres ideas que el público tiene que llevarse:

1. **Concentración y persistencia.** El 20 % de los barrios reúne el 42 % de los siniestros, y el 68 % del top 10 de un mes se repite el mes siguiente.
2. **El historial casi alcanza el techo.** Priorizar cada mes los 10 barrios con más siniestros en el último año cubre el 43 % de los siniestros del mes siguiente; un oráculo que conociera el futuro llegaría al 45 %. El historial capta el 92 % de la ganancia posible sobre elegir al azar.
3. **Contar no es medir riesgo.** Trabajamos con carga registrada, no con riesgo por vehículo o por persona, y el análisis es predictivo, no causal. Saber qué no se puede afirmar es parte del resultado.

---

## 1. Mapa de tiempos

| # | Bloque | Diapositiva | 15 min | 30 min |
|---|---|---|---|---|
| 1 | Apertura | `cover` | 0:45 | 1:30 |
| 2 | El problema público | `problema` | 1:15 | 2:00 |
| 3 | La pregunta y cómo la delimitamos | `pregunta` | 1:30 | 3:00 |
| 4 | Patrones: quiénes y dónde | `quienes`, `donde` | 2:00 | 4:00 |
| 5 | Cómo evaluamos | `metodo` | 1:30 | 3:30 |
| 6 | Resultado central y modelos | `resultado`, `modelos` | 2:30 | 4:00 |
| 7 | Perfiles de barrios | `perfiles` | 1:30 | 2:30 |
| 8 | Límites de la priorización | `exposicion` | 1:00 | 2:00 |
| 9 | Demostración del sitio web | sitio | — | 3:30 |
| 10 | Recomendaciones | `recomendaciones` | 1:00 | 1:30 |
| 11 | Límites y qué haría falta | `limites` | 1:00 | 1:30 |
| 12 | Rigor: qué salió mal y cómo lo corregimos | (oral) | — | 1:30 |
| 13 | Cierre | `cierre` | 0:30 | 1:00 |
| | **Total** | | **≈ 15:00** | **≈ 31:30** |

En la versión de 30 minutos conviene dejar 5 a 8 minutos de preguntas: si el tiempo es estricto, recortá la demostración a 2 minutos y el bloque 4 a 3 minutos.

---

## 2. Guion por bloques

### Bloque 1 · Apertura — diapositiva `cover`

**Objetivo.** Decir qué es el proyecto y adelantar la respuesta. En una presentación de resultados no hay que esconder el final: el público escucha mejor cuando sabe hacia dónde vamos.

**Qué decir.**

> «UrbanSafe CABA es un proyecto de ciencia de datos sobre siniestralidad vial en la Ciudad de Buenos Aires. Partimos de una pregunta muy concreta, de las que se hace un equipo de gestión con presupuesto limitado: si este mes tengo que decidir en qué barrios concentrar la prevención, ¿puedo anticipar dónde se van a concentrar los siniestros del mes que viene?
>
> Les adelanto la respuesta, porque es el corazón del trabajo: los siniestros se concentran y se repiten tanto en los mismos lugares que mirar el historial reciente ya es una guía muy difícil de superar. Probamos 94 configuraciones de modelos de machine learning y ninguna lo mejora de forma relevante. Lo que vamos a mostrar es cómo llegamos a esa conclusión, por qué podemos confiar en ella y qué sirve hacer con eso.»

**[30'] Ampliación.**

> «Todo el trabajo usa datos abiertos del Observatorio de Movilidad y Seguridad Vial de la Ciudad, publicados en BA Data. El proyecto es reproducible de punta a punta: con el repositorio público y siguiendo el README, cualquiera puede descargar las fuentes oficiales, rehacer los datos procesados y obtener exactamente las mismas cifras. Además construimos un sitio web interactivo para explorar los resultados, que vamos a ver más adelante.»

**Transición.** «Empecemos por el problema.»

---

### Bloque 2 · El problema público — diapositiva `problema`

**Objetivo.** Mostrar la magnitud y justificar por qué importa anticipar, no solo describir.

**Qué decir.**

> «En CABA ocurren alrededor de diez mil siniestros con víctimas por año. El gráfico muestra la serie: unos 10.000 en 2019, una caída fuerte en 2020 por la pandemia, a 6.000, y después una recuperación sostenida hasta 11.752 en 2025, el máximo de la serie. Con una salvedad que vamos a repetir: 2025 podría ser un dato provisorio.
>
> ¿Quiénes son las víctimas más graves? El 81 % de los siniestros mortales involucra a motociclistas o peatones.
>
> ¿Por qué no alcanza con saber dónde ocurrieron? Porque la prevención compite por recursos finitos: auditorías viales, rediseño de cruces, controles, campañas. Esos recursos se asignan hacia adelante. Lo que interesa es dónde se van a concentrar los siniestros el mes que viene.»

**Cifras a mano.** 10.155 (2019) · 6.061 (2020) · 7.818 · 9.536 · 9.927 · 10.569 · 11.752 (2025, posiblemente provisorio). Moto y peatón: 81 % de los mortales.

**[30'] Ampliación.**

> «La serie tiene además una caída a fines de 2019 que probablemente corresponde a un cambio en la forma de registrar, no a una mejora real. Redactamos una consulta formal al Observatorio para confirmarlo, junto con el estado provisorio de 2025, pero todavía no fue enviada. Por eso tratamos esos dos puntos como supuestos declarados y no como hechos.»

**Transición.** «Con este problema, formulamos una pregunta que se pudiera responder con datos.»

---

### Bloque 3 · La pregunta y cómo la delimitamos — diapositiva `pregunta`

**Objetivo.** Dejar claro qué se pregunta, qué no, y por qué elegimos barrio por mes.

**Qué decir.**

> «La pregunta es: ¿podemos anticipar en qué barrios se concentrarán los siniestros del mes siguiente mejor que mirando el historial?
>
> Trabajamos con 65.818 siniestros con víctimas y 75.197 víctimas, de 2019 a 2025, con fecha y ubicación. La unidad de análisis son los 48 barrios por mes, y el pronóstico siempre se hace para el mes siguiente con lo observado hasta el mes anterior.
>
> Fue una decisión deliberada delimitar el problema a frecuencia y concentración territorial. No estudiamos la gravedad de cada siniestro individual ni buscamos causas: son otras preguntas, con otros datos y otros diseños.»

**¿Por qué barrio por mes?** (decirlo brevemente en 15 minutos; desarrollarlo en 30)

> «Esa escala no la elegimos por gusto. Antes de modelar hicimos una auditoría de viabilidad: a escala barrio por mes hay densidad suficiente, solo el 1 % de las celdas no tiene siniestros y hay 48 unidades, un número útil para priorizar. Escalas más finas tienen demasiados ceros; escalas más gruesas, como la comuna, diluyen la concentración.»

**[30'] Ampliación: las decisiones D1 a D11.**

> «La auditoría terminó en once decisiones documentadas, de D1 a D11, que fijan la escala, el horizonte, el período de prueba y qué fuentes se usan y cuáles no. Un ejemplo: la infraestructura vial disponible describe solo el estado actual, sin fechas de habilitación. Si la usáramos para predecir el pasado, el modelo estaría viendo el futuro. Por eso quedó fuera de la evaluación predictiva principal. Otro ejemplo: los conteos de tránsito existen solo para 2024 y en corredores, así que no sirven como medida de exposición por barrio.»

**Transición.** «Antes de modelar miramos qué dicen los datos, y lo que encontramos anticipa todo lo demás.»

---

### Bloque 4 · Patrones: quiénes y dónde — diapositivas `quienes` y `donde`

**Objetivo.** Mostrar los dos hallazgos del análisis exploratorio que explican el resultado: la concentración y la persistencia.

**Qué decir — quiénes y cuándo.**

> «Primero, quiénes. Las motos participan en el 43 al 46 % de los siniestros con modo informado. El peatón es el usuario con mayor proporción de casos graves o mortales: 10,7 %. Y en cuanto al horario, los siniestros ocurren sobre todo de día, con un pico a las 17 horas, pero la gravedad es nocturna: entre las 0 y las 5, la proporción de graves o mortales es 2,1 veces la del resto del día.
>
> Una aclaración importante: no tenemos datos de viajes por modo, así que no podemos decir que viajar en moto sea más riesgoso por viaje. Describimos patrones, no causas.»

**Qué decir — dónde.**

> «Segundo, dónde. Este es el hallazgo clave. El 68 % del top 10 de un mes se repite el mes siguiente. Cinco barrios están casi siempre: Balvanera, Palermo, Flores, Caballito y Recoleta. Y 21 barrios nunca entraron al top 10.
>
> La siniestralidad está concentrada: el 20 % de los barrios reúne el 42 % de los siniestros, cuando por superficie le correspondería el 32 %. Está agrupada en el espacio: los barrios densos son vecinos en el centro. Y es muy persistente: la correlación del ranking de barrios entre años va de 0,96 a 0,98.
>
> Si el pasado reciente se repite tanto, el historial va a ser muy difícil de superar. Esa intuición es la que vamos a poner a prueba.»

**Advertencia que conviene decir en voz alta.**

> «Esto es carga registrada, no riesgo. Palermo es el primero en cantidad de siniestros, pero el 21.º en siniestros por kilómetro cuadrado. Un barrio grande y muy transitado acumula más siniestros sin ser necesariamente más peligroso.»

**[30'] Ampliación.**

> «Otros patrones del análisis exploratorio: las avenidas concentran el 64 % de los siniestros con apenas el 23,5 % de los kilómetros de calles; enero es el mes más bajo y octubre el más alto; y la pandemia cambió el nivel y la composición, con más bicicletas, pero no la geografía. También encontramos un problema de calidad: los siniestros graves pierden la coordenada entre el 6 y el 28 % de las veces según el año. Por eso no usamos la gravedad por barrio para priorizar: el faltante no es aleatorio y sesgaría el mapa.»

**Transición.** «Con estos patrones, el desafío era evaluar los modelos de una manera que no nos engañara.»

---

### Bloque 5 · Cómo evaluamos — diapositiva `metodo`

**Objetivo.** Convencer de que el resultado es confiable. Es el bloque que más valora un profesor de ciencia de datos.

**Qué decir.**

> «Fijamos las reglas antes de mirar los resultados. Esto es lo más importante del método, y lo explico con cuatro principios.
>
> Uno: solo información disponible. Cada pronóstico usa datos hasta el mes anterior, nunca del mes que se quiere predecir. Lo verifican 13 controles automáticos de fuga temporal, que corren como pruebas del código.
>
> Dos: validación en el tiempo. Entrenamos con el pasado y validamos en 2022, 2023 y 2024, siempre con datos anteriores al año evaluado. 2025 quedó reservado como prueba final y se usó una sola vez, con los modelos ya elegidos y congelados.
>
> Tres: un rival exigente. No alcanza con ganarle al azar. Los modelos compiten contra referencias simples: repetir el mes anterior y, sobre todo, el promedio de los últimos 12 meses. Y los umbrales de mejora se fijaron de antemano: por ejemplo, en regresión se exigía un error al menos 3 % menor que el mejor baseline y ganar en 2 de los 3 años.
>
> Cuatro: muchos modelos, comparados en igualdad de condiciones. Probamos Poisson, binomial negativa, regresión logística, random forest y gradient boosting: 94 configuraciones en total.»

**Las dos tareas** (decirlo claro, porque ordena todo lo que sigue):

> «Planteamos la pregunta de dos formas. Como regresión: cuántos siniestros tendrá cada barrio el mes siguiente. Y como clasificación: qué barrios estarán en el top 10 del mes siguiente, que es la forma más parecida a una decisión real de priorización.»

**[30'] Ampliación: por qué tanto cuidado.**

> «Con 94 configuraciones, el riesgo es encontrar una que gane por casualidad. Por eso las grillas son acotadas, la métrica se promedia en tres años, los criterios están escritos en el protocolo antes de entrenar y el test se usa una sola vez. Y cuando algo se agregó después de ver el test, lo marcamos como no confirmatorio. La incertidumbre la medimos con intervalos por bloques de tres meses, que respetan que meses consecutivos se parecen entre sí. Si el intervalo incluye el cero, decimos que la diferencia no es concluyente.»

**Transición.** «Con estas reglas, ¿qué pasó?»

---

### Bloque 6 · Resultado central y modelos — diapositivas `resultado` y `modelos`

**Objetivo.** Presentar el hallazgo principal con una cifra que se entienda sin estadística, y después el detalle de los modelos.

**Qué decir — resultado central.**

> «Este es el hallazgo central. Si cada mes priorizamos los 10 barrios con más siniestros en los últimos 12 meses, esos barrios reúnen el 43 % de los siniestros del mes siguiente. Elegir al azar daría el 21 %. Un oráculo que conociera el futuro llegaría al 45 %. Y el mejor modelo de machine learning llega al 43,1 %: apenas 0,3 puntos más que el historial, una diferencia cuyo intervalo de confianza incluye el cero.
>
> Dicho de otra forma: de todo lo que se puede ganar respecto de elegir al azar, el historial ya capta el 92 %. Y ese techo del oráculo es inalcanzable, porque conoce resultados que incluyen variación aleatoria imposible de anticipar. El margen real para cualquier modelo es todavía menor.»

**Cifras a mano (K = 10, test 2025).** Azar 20,8 % · mes anterior 42,2 % · promedio de 12 meses 42,7 % · clasificador 43,1 % · oráculo 44,6 % · ganancia captada 92 %.

**Qué decir — los modelos.**

> «En detalle. En regresión, el modelo elegido es un Poisson regularizado, entrenado sin los meses de pandemia. Comparado con repetir el mes anterior, reduce el error en alrededor de un siniestro por barrio y mes, una mejora clara. Pero comparado con el promedio de 12 meses, empatan: 4,07 contra 4,06 de error medio.
>
> En clasificación, el elegido es una regresión logística regularizada. Acierta el 81 % de los barrios del top 10, contra el 75 % de repetir el mes anterior: mejora clara. Contra el promedio de 12 meses, 81 contra 79: son 2 aciertos más en 120 elecciones, y no es concluyente.
>
> ¿Por qué el modelo no gana? Porque cuando miramos qué usa para decidir, el 75 % de su decisión depende del historial del barrio. Es, en el fondo, una persistencia refinada. La disputa real está en las 5 plazas del top 10 que no ocupan los barrios fijos, y ahí el modelo acierta 65 % contra 62 % del historial: una ventaja muy pequeña.»

**Cómo decir el resultado negativo** (importante para el tono):

> «Un resultado negativo bien demostrado es un resultado. Le dice a un equipo de gestión que no necesita un sistema complejo de machine learning para priorizar: una regla transparente, que cualquiera puede calcular y auditar, rinde prácticamente igual.»

**[30'] Ampliación: robustez.**

> «Pusimos a prueba esta conclusión de muchas formas: con 5 y con 15 barrios en lugar de 10; cambiando cómo se resuelven los empates en el puesto 10; suponiendo un mes más de demora en la publicación de los datos; y usando 2024 como prueba alternativa, por si los datos de 2025 son provisorios. La conclusión se mantiene en todos los casos. Con 15 barrios, el clasificador incluso queda algo peor que el historial. Y con un mes más de demora, los modelos empeoran o quedan iguales.
>
> Una nota sobre la interpretación: la importancia de las variables, medida con SHAP, describe qué patrones usa el modelo. No dice que una variable cause siniestros.»

**Transición.** «Los modelos nos dicen dónde. La siguiente pregunta es de qué tipo son los siniestros en cada lugar.»

---

### Bloque 7 · Perfiles de barrios — diapositiva `perfiles`

**Objetivo.** Mostrar el clustering y, a la vez, su alcance real. Este bloque cambió tras la revisión independiente: decirlo con precisión.

**Qué decir.**

> «Además de cuántos siniestros, nos preguntamos si hay barrios con siniestros de distinto tipo: con otros usuarios involucrados, en otras vías u otros horarios. Para eso agrupamos los barrios por la composición de sus siniestros, no por la cantidad, con datos de 2019 a 2024.
>
> Aparece un grupo claro y estable: 9 barrios de borde, sobre la General Paz y las autopistas, como Liniers, Mataderos, Saavedra, Villa Lugano o Villa Riachuelo. El 35 % de sus siniestros ocurre en autopista o General Paz, contra el 2 % del resto; tienen más autos y motos, y menos peatones y ciclistas. El resto, 39 barrios, es el interior.
>
> Ahora, la precisión importante. Este grupo coincide exactamente con una regla simple: barrios con más del 20 % de sus siniestros en autopista o General Paz. Es decir, es estable, pero es una división geográfica explicada por una sola variable, no un tipo de barrio descubierto por el algoritmo. Si quitamos el tipo de vía, no aparece una estructura clara.
>
> Dentro del interior hay un segundo nivel: un interior central y denso, con más peatones y transporte público, y uno residencial, con más motos y bicicletas. Pero esa división es débil y la tomamos como orientativa.»

**Cifras a mano.** Borde 9 barrios · interior 39 (central 17, residencial 22) · *silhouette* 0,33 en el primer nivel, 0,195 en el segundo (por debajo de 0,25 se considera débil) · volumen similar entre grupos (826 frente a 929 siniestros por barrio en la ventana).

**[30'] Ampliación: cómo elegimos.**

> «Comparamos cuatro métodos de agrupamiento con entre 2 y 8 grupos, con distintas formas de escalar los datos y con y sin volumen. La regla de selección también se fijó antes: estabilidad mínima, al menos 3 barrios por grupo, y entre las soluciones válidas la de mejor separación. Además descartamos atributos cuya variación entre barrios es compatible con el azar: la estacionalidad y las franjas diurnas no distinguen barrios.»

**Transición.** «Y esto nos lleva a dos advertencias sobre la propia priorización.»

---

### Bloque 8 · Límites de la priorización — diapositiva `exposicion`

**Objetivo.** Mostrar madurez crítica: dónde el ranking por conteo puede engañar.

**Qué decir.**

> «Primera advertencia: contar siniestros no es medir riesgo. No hay datos de tránsito para toda la ciudad. Donde sí hay, en 95 puntos con sensores en 2024, ordenar por siniestros por vehículo en lugar de por cantidad de siniestros cambia de cuartil al 43 % de los puntos.
>
> Pero lo presentamos como un resultado indicativo, no como una medición de riesgo, y conviene explicar por qué: cada sensor cuenta un solo sentido de circulación, aunque casi la mitad está en calles de doble mano. El denominador no es comparable entre sensores. Igual, en el grupo más homogéneo, 34 calles y avenidas de mano única, el orden también cambia en el 44 % de los casos. La señal está, pero no alcanza para hablar de riesgo.
>
> Segunda advertencia: los barrios de borde reúnen el 16 % de los siniestros, pero reciben solo el 8 al 10 % de los lugares del top 10. Su carga se reparte entre varios barrios medianos, y con regularidad solo entra Saavedra. No es un defecto de los modelos: es una consecuencia del criterio de priorizar por conteo de barrio.»

**[30'] Ampliación.**

> «Esto tiene una implicancia de política: si se quiere atender el problema de las vías rápidas del borde, hay que usar un criterio propio, por ejemplo por corredor. Priorizar por densidad no lo resolvería, porque el borde es justamente el grupo con menor densidad de siniestros.»

**Transición.** «Todo esto lo pusimos en una herramienta pública para que cualquiera lo explore.» (versión 30) / «¿Qué recomendamos, entonces?» (versión 15)

---

### Bloque 9 · Demostración del sitio web [30'] — sitio publicado

**Objetivo.** Mostrar que el proyecto se puede usar, no solo leer. Llevar el sitio abierto antes de empezar, con conexión probada.

**Recorrido sugerido (3 minutos y medio).**

1. **Atlas** (1 minuto). Mostrar el mapa de barrios, cambiar el mes y la métrica, y seleccionar un barrio para ver su ficha y su serie.
   > «El atlas permite recorrer los siete años mes a mes. Lo que se ve es carga registrada: el sitio lo aclara en cada vista, y distingue los meses sin datos de los meses con cero siniestros.»
2. **Simulador 2025** (1 minuto y medio). Abrir la vista del simulador, que arranca planteando el problema, la pregunta y la respuesta. Cambiar el método a comparar y la cantidad de barrios a atender, y reproducir los meses.
   > «Acá cualquiera puede ponerse en el lugar de quien decide: elijo cuántos barrios atender y con qué criterio, y veo mes a mes qué parte de los siniestros de 2025 habría alcanzado. La comparación entre el modelo y el historial es la misma que mostramos en las diapositivas, calculada con los mismos datos.»
3. **Perfiles** (1 minuto). Mostrar los dos grupos y el segundo nivel.
   > «Y esta vista muestra los perfiles, con la advertencia que acabamos de discutir: el borde es estable pero geográfico, y la subdivisión del interior es exploratoria.»

**Si falla la conexión.** Seguir con las diapositivas y decir: «El sitio está publicado y el enlace está en el README del repositorio; lo pueden recorrer después.»

**Datos técnicos, solo si preguntan.** Sitio estático (Astro, TypeScript y MapLibre) publicado en Cloudflare, sin servidor ni datos personales; los datos que muestra son agregados y se exportan desde el proyecto con un manifiesto de fuentes, licencias y hashes. Antes de cada publicación pasa 40 pruebas automáticas de funcionamiento y accesibilidad.

---

### Bloque 10 · Recomendaciones — diapositiva `recomendaciones`

**Objetivo.** Traducir el resultado a decisiones.

**Qué decir.**

> «Cuatro recomendaciones.
>
> Uno: priorizar con el historial. El top 10 de barrios por promedio de 12 meses es simple, transparente y ningún modelo probado lo supera de forma relevante. Cubre alrededor del 43 % de los siniestros del mes siguiente.
>
> Dos: elegir el tipo de prevención según el perfil, de forma orientativa: vías rápidas y conductores en el borde; peatones y transporte público en el interior central; motos y bicicletas en el residencial.
>
> Tres: no limitarse al conteo por barrio. Complementarlo con criterios de corredor, como avenidas y vías rápidas, y donde haya medición de tránsito, usar los siniestros por vehículo como señal complementaria, con cautela.
>
> Cuatro: usar el modelo como apoyo, no como reemplazo. Su probabilidad orienta las plazas inciertas del top 10, y los intervalos por barrio ayudan a fijar expectativas y detectar meses atípicos.»

**Transición.** «Y somos igual de explícitos con lo que no se puede afirmar.»

---

### Bloque 11 · Límites y qué haría falta — diapositiva `limites`

**Objetivo.** Cerrar el análisis con honestidad. Un profesor valora más un límite bien dicho que una conclusión inflada.

**Qué decir.**

> «No se puede afirmar nada sobre causas ni sobre el efecto de intervenciones: el diseño es predictivo. No se puede hablar de riesgo por persona o por vehículo en cada barrio, porque no hay exposición. No se pueden fijar prioridades por gravedad, porque faltan ubicaciones de los siniestros graves. Y 2025 podría ser provisorio, aunque usar 2024 como prueba alternativa lleva a la misma conclusión.
>
> ¿Qué haría falta para ir más lejos? Conteos de tránsito con cobertura de toda la ciudad; un historial fechado de obras e intervenciones viales, que permitiría estudiar efectos; la geocodificación completa de los siniestros graves; y la respuesta oficial del Observatorio sobre los datos de 2025 y el cambio de registro de 2019.»

**Cifra de contexto.** Solo el 12,8 % de los siniestros de 2024 ocurre cerca de un sensor de tránsito: por eso la exposición no se puede estimar por barrio.

---

### Bloque 12 · Rigor: qué salió mal y cómo lo corregimos [30'] — oral

**Objetivo.** Mostrar que el proceso detecta sus propios errores. Es un argumento fuerte ante un tribunal académico.

**Qué decir.**

> «No todo salió bien a la primera, y nos parece importante contarlo.
>
> El error más serio fue una fuga de información: en el análisis que supone un mes más de demora en los datos, el entrenamiento incluía una etiqueta que en la realidad todavía no estaría disponible. Nuestra propia revisión no lo detectó; lo encontró una revisión externa. Lo corregimos, agregamos un control automático para que no vuelva a pasar y lo dejamos registrado. El resultado principal no cambió.
>
> También vimos, solo con la validación, que la binomial negativa se volvía inestable en 2022, con pocos meses de entrenamiento. Agregamos una versión regularizada, pero como fue después de ver el test, la marcamos como no confirmatoria; tampoco habría cambiado la elección.
>
> Y al final encargamos una revisión independiente, hecha por un revisor distinto de quien implementó los modelos. Confirmó la conclusión central, la cifra del 92 % y que no hay fugas, y nos obligó a moderar dos conclusiones secundarias: la de exposición pasó a indicativa y la de perfiles se presenta como una división geográfica. Esas correcciones ya están en todo lo que mostramos hoy.
>
> Por último, verificamos la reproducibilidad desde cero: en un entorno limpio, siguiendo solo el README, los datos procesados salen idénticos por hash, las 66 pruebas automáticas pasan, los 8 notebooks corren en orden y las figuras son idénticas píxel a píxel.»

---

### Bloque 13 · Cierre — diapositiva `cierre`

**Objetivo.** Dejar una sola idea y abrir preguntas.

**Qué decir.**

> «Para cerrar, una idea: los siniestros con víctimas se repiten donde ya ocurrieron. Por eso, con estos datos, ningún modelo probado supera al historial para decidir dónde prevenir el mes que viene. Lo valioso del proyecto no es un modelo sofisticado, sino haberlo demostrado con una evaluación honesta, haber identificado qué tipo de prevención sugiere cada perfil y haber señalado dónde el conteo por barrio puede engañar.
>
> Todo está en el repositorio público, con código, notebooks documentados, informes y el sitio web. Muchas gracias; quedamos abiertos a preguntas.»

---

## 3. Hoja de cifras

| Tema | Cifra |
|---|---|
| Datos | 65.818 siniestros con víctimas y 75.197 víctimas, 2019–2025 |
| Por año | ≈ 10.000; 11.752 en 2025 (posiblemente provisorio); 6.061 en 2020 |
| Mortales | 81 % con moto o peatón (moto 42 %, peatón 39 %, 2019–2024) |
| Usuarios | Moto en el 43–46 % de los siniestros; peatón con 10,7 % de graves o mortales |
| Horario | Pico a las 17 h; entre 0 y 5 h, gravedad 2,1 veces mayor |
| Avenidas | 64 % de los siniestros en el 23,5 % de los kilómetros |
| Concentración | 20 % de los barrios reúne el 42 % de los siniestros (32 % por superficie) |
| Persistencia | 68 % del top 10 se repite el mes siguiente; ranking entre años 0,96–0,98 |
| Núcleo | Balvanera, Palermo, Flores, Caballito y Recoleta casi siempre en el top 10; 21 barrios nunca |
| Palermo | 1.º en cantidad, 21.º en siniestros por km² |
| Escala | 48 barrios × mes; 1 % de celdas sin siniestros |
| Modelos | 94 configuraciones: 38 de regresión y 56 de clasificación (más 8 *post hoc* no confirmatorias) |
| Validación | 2022, 2023 y 2024; prueba final 2025 usada una sola vez; 13 controles de fuga |
| Regresión | Poisson regularizado: error 4,07 frente a 4,06 del promedio de 12 meses; −1,0 frente al mes anterior |
| Clasificación | Logística: 81 % de aciertos frente a 79 % (12 meses) y 75 % (mes anterior); 2 aciertos más en 120 |
| Cobertura K = 10 | Azar 20,8 % · historial 42,7 % · modelo 43,1 % · oráculo 44,6 % |
| Ganancia | El historial capta el 92 % de la ganancia posible sobre el azar |
| Perfiles | Borde 9 barrios (35 % de sus siniestros en vías rápidas, frente a 2 %); interior 39 (central 17, residencial 22) |
| Regla del borde | Más del 20 % de los siniestros en autopista o General Paz (coincidencia exacta) |
| Separación | *Silhouette* 0,33 (primer nivel) y 0,195 (segundo nivel; < 0,25 es débil) |
| Exposición | 95 sensores 2024: 43 % cambia de cuartil (44 % en 34 avenidas de mano única); resultado indicativo |
| Equidad | Borde: 16 % de los siniestros, 8–10 % de los lugares del top 10 |
| Reproducibilidad | 66 pruebas; 8 notebooks; figuras idénticas píxel a píxel en sala limpia |

---

## 4. Preguntas probables y cómo responderlas

**1. «Si el modelo no le gana al historial, ¿para qué sirvió el trabajo?»**
> Para demostrar, con una evaluación rigurosa y fuera de muestra, que una regla simple y transparente es prácticamente óptima con estos datos. Eso evita invertir en sistemas complejos que no agregan valor, y además produjo dos aportes propios: los perfiles que orientan el tipo de prevención y la advertencia sobre dónde el conteo por barrio engaña.

**2. «¿No será que los modelos estaban mal ajustados?»**
> Probamos 94 configuraciones de cinco familias con grillas razonables, y la revisión independiente probó además alternativas sencillas propias, como medias de 6 meses o un índice estacional: ninguna superó al promedio de 12 meses. Y entendemos por qué: el 75 % de la decisión del modelo depende del historial del barrio. No queda mucha señal adicional que capturar.

**3. «¿Cómo evitaron la fuga temporal?»**
> Cada variable se calcula solo con datos hasta el mes anterior al pronóstico, y 13 controles automáticos lo verifican como pruebas del código. Validamos en el tiempo, con años posteriores al entrenamiento, y 2025 se usó una sola vez con los modelos congelados. Hubo una fuga en un análisis de sensibilidad, la detectó una revisión externa, la corregimos y agregamos un control específico.

**4. «¿Por qué barrio por mes y no una grilla más fina o por esquina?»**
> Porque a escalas finas hay demasiados ceros y el ranking es inestable, y la gravedad tiene coordenadas faltantes. Lo medimos: la grilla de 1 km tiene 26 % de celdas sin siniestros y un ranking menos estable. La comuna, en cambio, diluye la concentración. El barrio es un punto intermedio, y además es una unidad administrativa en la que se puede actuar.

**5. «¿Por qué no usaron la infraestructura (semáforos, ciclovías)?»**
> Porque los datos disponibles describen solo el estado actual, sin fechas de habilitación. Usarlos para predecir años anteriores sería darle al modelo información del futuro. Quedó registrado como decisión D11; con un historial fechado de obras se podría estudiar.

**6. «¿Un barrio con más siniestros es más peligroso?»**
> No necesariamente. Medimos carga registrada, no riesgo: Palermo es el primero en cantidad y el 21.º por kilómetro cuadrado. Para hablar de riesgo haría falta exposición, como tránsito o viajes, que no existe para toda la ciudad.

**7. «¿Qué tan confiables son los perfiles?»**
> El grupo de borde es estable ante cambios de método, escala y período, pero coincide con una regla simple sobre la proporción de siniestros en vías rápidas, así que lo presentamos como una división geográfica. La subdivisión del interior es débil y solo orientativa.

**8. «¿Y si los datos de 2025 son provisorios?»**
> Lo previmos: repetimos la evaluación usando 2024 como prueba alternativa, y la conclusión es la misma.

**9. «¿Qué significa el 92 %?»**
> No es el porcentaje de siniestros cubiertos. Es la proporción de la mejora posible sobre el azar que el historial ya consigue: el azar cubre el 20,8 %, el oráculo el 44,6 %, y el historial el 42,7 %, que es el 92 % del camino entre ambos.

**10. «¿Esto sirve para decidir intervenciones concretas?»**
> Sirve para decidir dónde mirar primero y qué tipo de prevención considerar. No sirve para estimar el efecto de una intervención: eso requiere un diseño causal y datos de intervenciones fechadas, que no tenemos.

**11. «¿Por qué confiar en las cifras?»**
> Porque todo se reproduce desde las fuentes oficiales siguiendo el README, las cifras clave se verifican automáticamente contra los archivos que las generan, y un revisor independiente reprodujo las principales.

**12. «¿Qué harían con más tiempo?»**
> Enviar la consulta al Observatorio, conseguir datos de tránsito con cobertura completa y un historial de intervenciones, y explorar la extensión prevista sobre lluvia y siniestralidad a corto plazo, con su propia validación.

---

## 5. Cómo decirlo bien

| Evitar | Decir en cambio |
|---|---|
| «El historial es el mejor predictor» | «Ningún modelo probado supera al historial de forma relevante» |
| «Los barrios de borde son más peligrosos» | «Los barrios de borde tienen más siniestros en vías rápidas» |
| «Ajustar por tránsito demuestra que el riesgo es otro» | «Donde hay medición, el orden cambia; es un resultado indicativo» |
| «El modelo descubrió tres tipos de barrio» | «Hay un grupo de borde estable, explicado por el tipo de vía, y una subdivisión débil del interior» |
| «Las motos causan más siniestros» | «Las motos participan en más siniestros registrados; no medimos causas» |
| «Conociendo el futuro se cubriría el 45 %» como meta | «El 45 % es un techo inalcanzable para cualquier pronóstico» |
| «El modelo falló» | «El modelo empata con una referencia simple, y eso es un resultado» |

**Consejos de exposición.**
- Abrí con la respuesta y repetila al cierre: es la idea que tiene que quedar.
- En cada cifra, decí primero la imagen y después el número: «de cada diez barrios elegidos, ocho aciertan».
- Cuando aparezca un límite, decilo con naturalidad y sin disculparte: forma parte del resultado.
- Si te preguntan algo que no se midió, respondé «eso no lo medimos» y explicá qué haría falta.

---

## 6. Antes de presentar

- Las fuentes de las 13 diapositivas ya coinciden con este guion, incluidas las correcciones de la revisión independiente.
- La presentación publicada en claude.ai no se actualiza sola desde `presentation/deck_source`: hay que regenerarla o exportarla a PDF para la entrega (condición P4).
- Probar el sitio web y la conexión en el aula antes de empezar.
