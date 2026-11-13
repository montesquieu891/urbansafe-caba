# UrbanSafe CABA — Informe de clustering de perfiles territoriales

**Hito:** Paso 09  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:**
- Notebook: [notebooks/05_clustering.ipynb](../notebooks/05_clustering.ipynb), ejecutado de punta a punta.
- Código: [`src/profiles.py`](../src/profiles.py) y [`tests/test_profiles.py`](../tests/test_profiles.py).
- Tablas: [reports/tables/05_clustering/](../reports/tables/05_clustering/).
- Figuras: [perfiles_mapa.png](../reports/figures/05_clustering/perfiles_mapa.png) y [tipologia_k3.png](../reports/figures/05_clustering/tipologia_k3.png).

**Pregunta.** ¿Qué perfiles de siniestralidad distinguen a los barrios de CABA?

---

## 1. Resumen

| Elemento | Resultado |
|---|---|
| Ventana de atributos | Desarrollo 2019–2024 **sin meses anómalos** (55 meses). **No se usa 2025** |
| Atributos retenidos | 9: modo de la víctima (5), tipo de vía (2), fin de semana y madrugada. Se retuvieron con una regla de señal/ruido fijada antes de agrupar |
| Atributos descartados por ruido | Franjas diurnas, **estacionalidad trimestral** y "otros modos" (cociente señal/ruido < 2) |
| Solución seleccionada (regla a priori) | **K-Means, k = 2**: *silhouette* 0,33, ARI *bootstrap* 0,86 y grupos de 39 y 9 barrios |
| Segundo nivel descriptivo | K-Means, k = 3: **anida** en la anterior. *Silhouette* 0,195 (separación débil) y ARI 0,70 |

**Conclusión (H6).** Se respalda **parcialmente**. Hay un perfil diferenciado, estable y que no depende del volumen: los **barrios de borde sobre la General Paz y las autopistas**. Concentran el 35 % de sus hechos en vías rápidas, tienen más automóvil y moto, y menos peatones y ciclistas. Dentro del resto de la ciudad, la diferencia entre barrios **centrales-densos** (más peatones y transporte público) y **residenciales** (más moto y bicicleta) es reproducible, pero su separación es débil. La estacionalidad y el perfil horario diurno **no distinguen** barrios más allá del ruido de muestreo.

**Acotación tras la revisión independiente (R2).** La partición seleccionada coincide **exactamente** (ARI 1,0) con la regla `pct_autopista_gralpaz > 0,20`; con esa sola variable, la *silhouette* sería 0,81. `pct_avenida` y `pct_autopista_gralpaz` son proporciones complementarias de la misma composición por tipo de vía, así que esa dimensión pesa doble al estandarizar, y las diferencias de modo son en parte mecánicas (en una autopista casi no hay peatones). Núñez (17,5 %) queda justo por debajo del corte. El perfil de borde es estable, pero debe presentarse como una **partición geográfica explicada por una variable**, no como una tipología multivariada de siniestralidad. Sin la familia de vía, la estructura es débil (*silhouette* ≤ 0,23): ese es el resultado multivariado real.

## 2. Diseño

- **Unidades:** 48 barrios. El barrio con menos hechos en la ventana es Coghlan (177), así que no hizo falta excluir barrios por cobertura.
- **Atributos de perfil relativo** (proporciones con denominadores explícitos; `src/profiles.py`):
  - Horario: sobre los hechos con hora. Fin de semana: sobre todos los hechos del barrio (corregido tras la revisión independiente, R10).
  - Estación: sobre todos los hechos.
  - Modo de la víctima: sobre los hechos con modo informado (SD excluido y descrito aparte).
  - Tipo de vía: sobre los hechos de 2020 en adelante con vía informada, porque en 2019 falta en el 95 %.
- **Volumen** (log de hechos por mes y log de densidad): solo en la variante R+V y en la caracterización.
- **Excluidos de los atributos:**
  - gravedad (KSI), por el faltante diferencial (E9);
  - infraestructura vigente (D11). El "tipo de vía" es la vía **registrada en cada hecho**, no la red vial actual;
  - todo dato de 2025.
- **Pruebas:** los atributos no cambian si se alteran los datos de 2025, las proporciones suman 1 y hay 48 barrios (`tests/test_profiles.py`).

**Reglas fijadas antes de ver resultados.** Están en el notebook, en el encabezado y en §1:
1. Cribado de atributos con un cociente señal/ruido ≥ 2.
2. Selección entre K-Means y Ward (k de 2 a 8, escalado estándar) de la solución con mayor *silhouette* entre las que tienen ARI *bootstrap* ≥ 0,60 y grupos de al menos 3 barrios; ante diferencias menores que 0,01, la de menor k.
3. Una *silhouette* menor que 0,25 se considera estructura débil.

## 3. Alternativas comparadas

| Método (conjunto R, escalado estándar) | Mejor *silhouette* (k) | ARI *bootstrap* en ese k | Observación |
|---|---|---|---|
| **K-Means** | **0,330 (k = 2)** | **0,86** | Elegida. Con k ≥ 3, la *silhouette* queda por debajo de 0,25 |
| Ward | 0,330 (k = 2) | 0,82 | La misma partición que K-Means con k = 2 |
| Jerárquico *average* | 0,444 (k = 2) | 0,57 | No elegible: separa **un solo barrio** (tamaños 47/1; con k = 3, 39/8/1), así que no cumple el mínimo de 3 barrios por grupo, y además es inestable. Su *silhouette* alta refleja un caso aislado, no perfiles |
| HDBSCAN (tamaño mínimo 3 a 6) | 0,26 sin contar el ruido (tamaño 3) | — | **62,5 % de ruido** con tamaño 3 y **100 %** con 4 a 6: no hay estructura de densidad |
| Variante R+V (con volumen) | 0,278 (Ward, k = 2) | — | Con K-Means k = 2 da casi la misma partición que R (ARI 0,91) |

Las tablas completas están en [comparacion_metodos.csv](../reports/tables/05_clustering/comparacion_metodos.csv) (3 conjuntos de escalado × 3 métodos × k de 2 a 8, con Calinski-Harabasz y Davies-Bouldin) y en [hdbscan.csv](../reports/tables/05_clustering/hdbscan.csv).

## 4. Robustez de la solución seleccionada

| Prueba | ARI frente a la solución seleccionada |
|---|---|
| Escalado robusto y min-max | 1,00 y 1,00 |
| Subventana hasta 2022-12 / 2023–2024 / entre ambas | 1,00 / 1,00 / 1,00 |
| Sin la familia de horario / sin la de modo | 1,00 / 1,00 |
| **Sin la familia de tipo de vía** | **0,28** |
| Semillas (30, con `n_init` = 1) | 0,65 de media. Con `n_init` = 50, la solución es estable |
| *Bootstrap* de barrios (200 réplicas; en la práctica, submuestreo de barrios únicos, alrededor del 63 %, porque `bootstrap_ari` descarta las repeticiones) | Media 0,86; percentil 10: 0,20 (K-Means). Para Ward con k = 2, percentil 10: 0,54 |
| Dependencia del volumen | η² = 0,001 (nivel) y 0,03 (densidad) |

**Lectura.** La partición **no es un artefacto del volumen, del escalado ni del período**, pero **depende de la familia "tipo de vía"**. Refleja una condición geográfica estructural: tener la General Paz o las autopistas dentro del barrio. El percentil 10 del ARI *bootstrap* de K-Means (0,20) muestra que algunas réplicas reorganizan los grupos. Por eso se considera robusta la **existencia** del grupo de borde, no la asignación exacta de cada barrio cercano a la frontera entre perfiles. Esa existencia es, en esencia, la de un umbral sobre la proporción de hechos en autopista o General Paz (R2).

## 5. Perfiles

| Perfil | n | Barrios | Moto | Peatón | Bicicleta | Auto | TP | Avenida | Autopista/Gral. Paz | KSI* | Top 10* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Borde (Gral. Paz/autopistas)** | 9 | Liniers, Mataderos, Saavedra, Versalles, Villa Devoto, Villa Lugano, Villa Pueyrredón, Villa Real, Villa Riachuelo | 49 % | 12 % | 8 % | 19 % | 6 % | 35 % | **35 %** | 5,0 % | 17 % |
| Interior central-denso (segundo nivel) | 17 | Entre ellos, Balvanera, Constitución, Flores, Monserrat, Palermo y Recoleta | 41 % | **20 %** | 11 % | 14 % | **8,5 %** | 66 % | 2 % | 5,3 % | 30 % |
| Interior residencial (segundo nivel) | 22 | Entre ellos, Almagro, Belgrano, Caballito, Coghlan y Núñez | **47 %** | 16 % | **15 %** | 11 % | 5,5 % | 61 % | 2 % | 4,7 % | 16 % |

*Descriptivos, no usados para agrupar. KSI: proporción de hechos graves o mortales, afectada por el faltante diferencial de coordenadas. Top 10: frecuencia media en el top 10 mensual. Las listas completas están en [perfiles_k3.csv](../reports/tables/05_clustering/perfiles_k3.csv) y [asignacion_barrios.csv](../reports/tables/05_clustering/asignacion_barrios.csv).

**Uso posible (orientativo, no causal).**
- Barrios de borde: prevención orientada a **vías rápidas y conductores** (auto y moto). Esta orientación se deduce casi directamente de la variable que define el grupo.
- Interior central-denso: **usuarios vulnerables en avenidas** (peatones y transporte público).
- Interior residencial: **motociclistas y ciclistas**.

Los perfiles describen la composición de la **carga registrada**, no el riesgo por usuario: no hay exposición (D8).

## 6. Reproducibilidad

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 05_clustering.ipynb
```

La ejecución tarda unos 5 minutos, por los *bootstrap*. Hay 54 pruebas automatizadas y todas pasan.

---

## 7. Dictamen científico del Paso 09 (autoauditoría)

**Tipo de revisión.** **Autoauditoría** con las skills `ml-scientific-reviewer` y `colab-ml-validation` (sección de clustering). El revisor es el mismo agente que implementó. No hubo un revisor independiente.

**Comprobaciones ejecutadas.**
1. **Reproducción independiente.** A partir de `atributos_barrio.csv` se reajustaron el escalado y K-Means con k = 2. La partición coincide con `asignacion_barrios.csv` (ARI 1,0) y la *silhouette* es 0,330.
2. **Atributos recalculados desde `hechos_clean.csv` sin `src/profiles.py`.** Autopista o General Paz en Villa Lugano: 0,2039. Peatón en Balvanera: 0,2399. Ambos coinciden. El último mes usado es 2024-12.
3. **Ventana sin resultados futuros.** Hay un test que perturba 2025 y verifica que los atributos no cambien.

| # | Hallazgo | Evidencia | Severidad | Tratamiento | Condición |
|---|---|---|---|---|---|
| K1 | La partición elegida depende de una sola familia de atributos (tipo de vía) | ARI 0,28 sin ella | Media | Se informa como perfil **geográfico-estructural**. Sin vía, la estructura es débil (*silhouette* ≤ 0,23) | ✔ Declarado |
| K2 | Inestabilidad parcial por *bootstrap* en K-Means (percentil 10 de ARI = 0,20) | §4 | Media | Se afirma la existencia del grupo de borde, no la asignación de los barrios fronterizos. Ward da la misma partición con un percentil 10 de 0,54 | ✔ Redacción acotada |
| K3 | El segundo nivel (k = 3) tiene separación débil | *Silhouette* 0,195 | Media | Se presenta como descriptivo y orientativo, no como la selección | ✔ |
| K4 | El cribado descartó la estacionalidad y las franjas horarias | Cociente señal/ruido < 2 | Baja | La regla se fijó antes de agrupar y evita perfiles construidos sobre ruido; queda documentado | ✔ |
| K5 | El tipo de vía se calcula solo desde 2020 (en 2019 falta en el 95 %) | `src/profiles.py` | Baja | Denominador explícito; las subventanas dan ARI 1,0 | ✔ |
| K6 | KSI y top 10 por grupo se describen con el faltante diferencial de los graves | E9 | Baja | No se usan para agrupar; se marcan como descriptivos | ✔ |
| K7 | La métrica de estabilidad por semilla con `n_init` = 1 subestima la estabilidad de la solución usada (`n_init` = 50) | §4 | Baja | Se informan ambas | ✔ |

**Dictamen: aprobado.** No hay hallazgos que invaliden el resultado. Se compararon alternativas (K-Means, Ward, *average*, HDBSCAN; variantes de escalado, de atributos y de volumen). La selección siguió una regla fijada a priori. Los grupos están caracterizados en unidades originales. Las limitaciones (K1–K3) acotan la afirmación: hay **un** perfil robusto y una subdivisión débil.

**Revisión independiente posterior (2026-11-13; [dictamen](independent_model_review.md)).** Confirmó la reproducción (ARI 1,0, *silhouette* 0,33) y que los atributos excluyen 2025. Acotó la interpretación: el perfil de borde equivale a la regla `pct_autopista_gralpaz > 0,20` (R2), y corrigió dos descripciones de método (R10). Ambas correcciones están aplicadas arriba.

## 8. Verificación del criterio de aceptación del Paso 09

Criterio del plan: *"grupos caracterizados, alternativas comparadas y selección argumentada"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Atributos históricos de frecuencia, estacionalidad, distribución horaria y composición | ✔ | §2. La estacionalidad y las franjas diurnas se evaluaron y se descartaron por ruido (K4); el volumen está en la variante R+V |
| K-Means y jerárquico; DBSCAN o HDBSCAN si los datos lo justifican | ✔ | §3. HDBSCAN se evaluó y no encontró estructura |
| *Silhouette*, estabilidad, separación, sensibilidad al escalado e interpretabilidad | ✔ | §3–§5 |
| Sin resultados futuros en los atributos | ✔ | Ventana ≤ 2024-12 y test de perturbación |
| Grupos caracterizados | ✔ | §5 |
| Alternativas comparadas y selección argumentada | ✔ | §3 y §2 (regla a priori) |
| Dictamen científico registrado | ✔ | §7 |
