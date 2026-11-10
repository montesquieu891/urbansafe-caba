# UrbanSafe CABA — Informe de robustez y utilidad pública

**Hito:** Paso 10. Integración, robustez y utilidad pública  
**Estado:** borrador para revisión, no cerrado  
**Fecha:** 2026-11-10  
**Evidencia:**
- Notebook: [notebooks/06_integrated_evaluation.ipynb](../notebooks/06_integrated_evaluation.ipynb), ejecutado de punta a punta.
- Tablas: [reports/tables/06_integrated_evaluation/](../reports/tables/06_integrated_evaluation/).
- Figuras: [cobertura_topk.png](../reports/figures/06_integrated_evaluation/cobertura_topk.png), [error_relativo.png](../reports/figures/06_integrated_evaluation/error_relativo.png) y [exposicion_corredores.png](../reports/figures/06_integrated_evaluation/exposicion_corredores.png).
- Insumos: los modelos **congelados** de los Pasos 07 y 08, los perfiles del Paso 09 y el protocolo.

---

## 1. Respuesta a la pregunta del proyecto

**¿Los datos históricos de CABA permiten mejorar la priorización territorial frente a métodos sencillos?** En la práctica, **no**. La priorización por historial ya está muy cerca del máximo alcanzable.

| K barrios priorizados | Azar | **Historial (media de 12 meses)** | Clasificador | Regresión | Oráculo (cota) |
|---|---|---|---|---|---|
| 5 | 10,4 % | **26,4 %** | 26,5 % | 26,5 % | 27,3 % |
| 10 | 20,8 % | **42,7 %** | 43,1 % | 42,8 % | 44,6 % |
| 15 | 31,3 % | **55,7 %** | 55,2 % | 55,7 % | 58,4 % |

*La tabla muestra la cobertura de los hechos del mes siguiente en el test 2025. En la validación 2022–2024 los valores son prácticamente iguales.*

- **El historial capta casi toda la ganancia posible.** Priorizar los 10 barrios con mayor media de 12 meses cubre el **42,7 %** de los siniestros con víctimas del mes siguiente. Conociendo el futuro (oráculo) se cubriría el 44,6 %. Así, el historial capta el **92 %** de la ganancia posible sobre el azar, tanto en el test como en la validación.
- **Los modelos agregan cambios ínfimos.** El clasificador suma **+0,3 pp** con K = 10: es positivo en los 3 *folds*, pero el IC 95 % por bloques en test es [−0,07; +0,80]. Con K = 15 resta 0,4 pp en el test. La regresión agrega entre 0,0 y 0,1 pp.
- **La conclusión es robusta.** Se mantiene ante la definición de empates, la latencia de los datos, la validación retrospectiva V2024 y la escala espacial (§3–§4).

## 2. Cuándo los modelos superan a los baselines y cuándo no

| Comparación | Resultado | Evidencia |
|---|---|---|
| Frente al **azar** | Los modelos y el historial lo superan ampliamente (43 % frente a 21 % de cobertura con K = 10) | §1 |
| Frente a la **persistencia** (mes anterior) | Los modelos son claramente mejores: regresión ΔMAE −1,0; clasificador P@10 0,81 frente a 0,73 | Pasos 07 y 08 |
| Frente a la **media de 12 meses** | **No hay mejora relevante.** Regresión: MAE equivalente. Clasificador: +0,016 de P@10 y +0,3 pp de cobertura, por debajo de los umbrales e incierto entre meses | Pasos 07 y 08; §1 |
| Plazas inciertas del top 10 | El clasificador acierta 3 pp más fuera del núcleo persistente | Paso 08 |
| Meses con cambio de nivel (fin de 2025) | Todos los métodos subestiman; la media de 12 meses reacciona lento | Paso 07 |
| K distinto de 10 | La ventaja del clasificador desaparece con K = 5 y K = 15 | §2 del notebook |
| Con latencia (gap = 1) | La regresión queda peor que el baseline; la ventaja del clasificador es errática | §3 |

## 3. Robustez

| Sensibilidad | Resultado |
|---|---|
| Definición de positivo en empates (R0, R-incl, R-excl-empates) | Ventaja del clasificador idéntica: +0,017 de P@10 en validación |
| Semillas de desempate (500, pareadas) | Amplitud del intervalo ≤ 0,05 pp de cobertura |
| Composición modal (sin estas variables) | El clasificador pierde su ventaja en V2022 y no cambia en V2023 ni V2024 |
| Excluir los meses de pandemia del entrenamiento | Decisivo para la regresión (MAE 3,86 frente a 4,94); menor para la clasificación (0,795 frente a 0,789) |
| Latencia (gap = 1) | Regresión: cociente de MAE de 1,03 en test. Clasificador: Δ entre −0,006 y +0,050 |
| **V2024 como validación retrospectiva** (por si 2025 es provisorio) | Regresión 3,900 frente a 3,901; clasificador 0,786 frente a 0,776. **Misma conclusión** |
| **Escala espacial y temporal (H7)** | Barrio × trimestre es la más estable (persistencia 0,92; P@K 0,84). Barrio × mes es intermedia (0,82; 0,75). Grilla de 1 km (26 % de ceros; 0,66) y comuna (0,66; 0,58) son menos predecibles |

## 4. Incertidumbre y sesgos territoriales

- **Incertidumbre.**
  - Los IC por bloques (3 meses) del test 2025 son amplios: ±0,4–0,5 pp de cobertura y ±0,14 de MAE.
  - Con solo 12 meses de test, la potencia es baja.
  - La binomial negativa regularizada da intervalos por barrio con buena cobertura en 2025 (Paso 07, post hoc).
- **Error relativo.** Es mayor en los barrios de bajo volumen (MAE/media de 0,34 frente a 0,19 en el tercil alto). Lo mismo le pasa al baseline: es ruido de conteo, no un sesgo del modelo.
- **Representación de perfiles en el top 10.** El **perfil de borde** (General Paz y autopistas) aporta el 16,2 % de los hechos, pero solo el 8–10 % de las selecciones: su carga se reparte entre barrios de volumen medio. **Priorizar por conteo de barrio subrepresenta las vías rápidas del borde.** Es un efecto del criterio, no del modelo.
- **Calibración por perfil.** El clasificador sobreestima en el borde (0,15 frente a 0,10 observado) y está bien calibrado en el interior.

## 5. Exposición por corredor (H8, extensión condicionada)

Alrededor de los 95 sensores de 2024, el conteo de hechos **no se asocia con el volumen** (Spearman 0,03). El orden por **tasa** (hechos por millón de vehículos-día) difiere del orden por conteo:
- Spearman de 0,68 entre ambos órdenes;
- 43 % de los sensores cambia de cuartil;
- 4 de 10 coincidencias en el top 10.

Las tasas medianas son mayores en los carriles exclusivos (5,4) que en calles y avenidas (1,9) y en autopistas (1,3). **H8 se respalda solo dentro de los corredores medidos.** Las limitaciones son un solo año, un día por semana y un radio de 150 m. **No se extrapola** a barrios ni a otros años (D8).

## 6. Veredicto sobre las hipótesis

| Hipótesis | Veredicto | Evidencia principal |
|---|---|---|
| **H1.** Concentración y persistencia | **Respaldada** | El 20 % de los barrios concentra el 42 % de los hechos (frente al 32 % por superficie). La persistencia de rangos es de 0,96–0,98 entre años y 0,82 entre meses (E6) |
| **H2.** Predictibilidad sobre la persistencia | **Respaldada frente a la persistencia y al estacional; no frente a la media de 12 meses** | ΔMAE −1,0 (IC < 0) frente a la persistencia; ΔMAE +0,009 (IC [−0,13; 0,14]) frente a la media de 12 meses |
| **H3.** Aporte de la infraestructura | **No contrastable** (D11) | No hay infraestructura con vigencia verificable. Solo hay asociación descriptiva (E10) |
| **H4.** Detección de concentración | **No respaldada frente al mejor baseline** (mejora pequeña, no relevante) | ΔP@10 +0,016 en validación (umbral 0,02) y +0,017 en test (IC [−0,02; 0,06]) |
| **H5.** Valor para la priorización | **No respaldada** | Cobertura +0,3 pp con K = 10; ventaja nula o negativa con otros K. El historial capta el 92 % de la ganancia posible |
| **H6.** Perfiles territoriales | **Parcialmente respaldada** | Un perfil de borde robusto; subdivisión del interior débil (Paso 09) |
| **H7.** Dependencia de la escala | **Parcialmente respaldada** | Las unidades finas tienen más ceros y menos estabilidad; la relación no es monótona (la comuna también es menos predecible) |
| **H8.** Exposición | **Respaldada en corredores con sensor (2024)** | Cambio sustancial del orden al ajustar por volumen. No es generalizable |

## 7. Qué decisiones puede informar razonablemente

**Puede informar:**
1. **Priorización mensual por historial.** Elegir los 10 barrios con mayor media de 12 meses cubre alrededor del 43 % de los siniestros con víctimas del mes siguiente. Es simple, transparente y prácticamente óptimo con estos datos. **Es la recomendación operativa.**
2. **Probabilidad calibrada de entrar al top 10.** El clasificador sirve como apoyo para las plazas inciertas, es decir, para decidir entre los barrios que no son fijos. Su ganancia es marginal.
3. **Intervalos de conteo por barrio** con la binomial negativa regularizada, para fijar expectativas y detectar meses atípicos.
4. **Tipo de prevención según el perfil** (Paso 09):
   - barrios de borde: vías rápidas, autos y motos;
   - interior central-denso: peatones y transporte público en avenidas;
   - interior residencial: motociclistas y ciclistas.
5. **En corredores con medición**, revisar la priorización por tasa de exposición, que cambia el orden.

**No debería informar:**
- Efectos causales de intervenciones ni de la infraestructura (diseño predictivo, D4 y D11).
- Riesgo por usuario o por vehículo a escala barrial (sin exposición, D8).
- Priorización de gravedad por barrio (KSI con faltante diferencial, E9).
- Decisiones con escalas más finas que el barrio sin una nueva validación (H7).
- Generalización a otras ciudades.

## 8. Reproducibilidad

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 06_integrated_evaluation.ipynb
```

La ejecución tarda menos de 1 minuto. Hay 55 pruebas automatizadas y todas pasan.

---

## 9. Dictamen científico del Paso 10 (autoauditoría)

**Tipo de revisión.** **Autoauditoría** con las skills `ml-scientific-reviewer`, `colab-ml-validation` y `geospatial-analysis`. El revisor es el mismo agente que implementó. **Se recomienda una revisión independiente antes de la entrega (Paso 12).** En este proyecto, una revisión externa ya detectó una fuga de etiquetas que la autoauditoría del Paso 06 había omitido.

**Comprobaciones ejecutadas.**
1. **Reajuste por *fold*.** Con las configuraciones congeladas, reproduce exactamente la P@10 esperada guardada en el Paso 08 (0,7694, 0,8292 y 0,7861). Está verificado con un `assert` en el notebook.
2. **Cobertura recalculada desde `predicciones_test.csv` con `nlargest`,** sin las funciones del proyecto: clasificador 0,4305, oráculo 0,4462 y media de 12 meses 0,4273. Coinciden.
3. **No se volvió a seleccionar ningún modelo.** Las sensibilidades usan solo la validación; el test se usa únicamente con modelos y predicciones congelados.

| # | Hallazgo | Severidad | Tratamiento | Condición |
|---|---|---|---|---|
| I1 | La cobertura en test reutiliza 2025, que ya se evaluó en los Pasos 07 y 08 | Baja | Está prevista por el protocolo (test usado en los Pasos 07, 08 y 10). No hubo nuevas decisiones; las sensibilidades están en validación | ✔ |
| I2 | Baja potencia del test (12 meses) | Media, inherente | IC por bloques informados; conclusiones formuladas como "no hay mejora demostrable" | ✔ |
| I3 | El análisis de escala (H7) usa rankings sin ajuste, no modelos reentrenados por escala | Media | Se declara. Mide la señal disponible, no el desempeño de modelos en cada escala | ✔ Declarado |
| I4 | H8 usa un radio de 150 m alrededor de sensores ubicados en corredores | Media | Resultado limitado a los corredores; sin extrapolación | ✔ |
| I5 | El perfil de borde está subrepresentado por el criterio de conteo | Media (equidad territorial) | Se informa como efecto del criterio de priorización, con una alternativa sugerida | ✔ |
| I6 | El test 2025 podría ser provisorio | Media | V2024 retrospectiva da la misma conclusión | ✔ |

**Dictamen: aprobado.** El sistema se evaluó como herramienta de priorización frente al historial, con incertidumbre y sesgos territoriales. Queda documentado cuándo supera a los baselines (persistencia y azar), cuándo no (media de 12 meses) y qué decisiones puede informar. El resultado central es negativo pero sólido: con estos datos, **la mejor priorización mensual es el historial simple**.

## 10. Verificación del criterio de aceptación del Paso 10

Criterio del plan: *"documentar cuándo supera baselines, cuándo no y qué decisiones puede informar razonablemente"*.

| Requisito | Estado | Evidencia |
|---|---|---|
| Priorización de los modelos frente al historial | ✔ | §1 y §2 |
| Cobertura de siniestros futuros en las K zonas | ✔ | §1 (K = 5, 10 y 15; validación y test) |
| Sensibilidad a períodos, granularidad espacial y variables | ✔ | §3 (V2024, pandemia, latencia, escala, composición, empates) |
| Incertidumbre y sesgos territoriales | ✔ | §4 |
| Análisis separado de exposición por corredor, sin extrapolar | ✔ | §5 |
| Cuándo supera, cuándo no, qué decisiones informa | ✔ | §2, §6 y §7 |
| `notebooks/06_integrated_evaluation.ipynb` e informe de robustez | ✔ | Este documento |
| Dictamen científico registrado | ✔ | §9 |
