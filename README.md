# UrbanSafe CABA

Proyecto académico de ciencia de datos sobre siniestralidad vial en la Ciudad Autónoma de Buenos Aires. Analiza la frecuencia y la concentración territorial de los siniestros con víctimas, evalúa fuera de muestra si se puede anticipar su concentración por barrio en el mes siguiente y compara esa priorización con una estrategia basada solo en el historial.

- Propuesta y preguntas: [docs/research_proposal.md](docs/research_proposal.md)
- Fuentes: [docs/data_inventory.md](docs/data_inventory.md) y [docs/source_register.csv](docs/source_register.csv)
- Viabilidad y decisiones D1–D11: [docs/feasibility_report.md](docs/feasibility_report.md)
- Diccionario de datos procesados: [docs/data_dictionary.md](docs/data_dictionary.md)
- **Informe final:** [docs/final_report.md](docs/final_report.md)
- Plan y estado de los hitos: [UrbanSafe_CABA_Implementation_Plan.md](UrbanSafe_CABA_Implementation_Plan.md)

## Estructura

```
data/raw/            Fuentes oficiales tal como se descargan (no versionado)
data/processed/      Salidas del ETL (no versionado; se reconstruye)
docs/                Propuesta, inventario, viabilidad, diccionario y evidencia por paso
notebooks/           00_data_audit (03), 01_EDA (05), 02_feature_engineering (06), 03_regression (07), 04_classification (08), 05_clustering (09), 06_integrated_evaluation (10), 07_storytelling (11)
reports/             Tablas y figuras generadas por los notebooks
models/              Modelos finales congelados (.joblib) y metadatos (Paso 12)
presentation/        Fuentes de la presentación (Paso 11)
scripts/             Relevamiento (Paso 02), exportación de modelos y trazabilidad (Paso 12)
src/                 data_processing.py (ETL), labels.py (etiquetado top-K, regla R0), features.py (variables y particiones), regression.py y evaluation.py (Paso 07), classification.py (Paso 08), profiles.py (Paso 09)
tests/               Invariantes del ETL (pytest)
```

## Reproducir los datos procesados

Se requiere Python 3.13 (verificado con 3.13.7) y acceso a internet para la descarga.

**1. Crear el entorno.**

```bash
python -m venv .venv
```

Activarlo con `source .venv/bin/activate` (Linux o macOS) o `.venv\Scripts\activate` (Windows). Luego:

```bash
pip install -r requirements.txt
```

Si el proyecto está en una carpeta sincronizada (OneDrive, Dropbox), conviene crear el entorno fuera de ella, por ejemplo en `~/.venvs/urbansafe`.

**2. Descargar las fuentes y ejecutar el ETL.** Desde la raíz del proyecto:

```bash
python -m src.data_processing --download
```

El comando descarga en `data/raw/` los archivos oficiales de BA Data y verifica su **SHA-256** frente a la versión auditada. Después escribe en `data/processed/` las tablas limpias, los paneles barrio × mes y comuna × mes, el registro de exclusiones y `qa_report.json`. La ejecución tarda unos segundos, sin contar la descarga, que ronda los 71 MB.

**2b. Construir las variables del modelado** (Paso 06; protocolo en [docs/experimental_protocol.md](docs/experimental_protocol.md)):

```bash
python -m src.features
```

**3. Verificar las invariantes.**

```bash
python -m pytest -q tests
```

Son 55 pruebas. Las del ETL verifican clave única, ausencia de huérfanos, conciliación entre hechos y víctimas, paneles completos, totales conciliados, exclusiones con motivo y valores de la auditoría. Las de etiquetado verifican la regla R0. Las de variables son controles de fuga temporal.

**4. Comprobar que las salidas son idénticas a las de referencia.** Compare los hashes de `data/processed/` con [docs/evidence/paso04/processed_sha256.txt](docs/evidence/paso04/processed_sha256.txt):

```bash
cd data/processed && sha256sum -c ../../docs/evidence/paso04/processed_sha256.txt
```

**Si la fuente se actualizó.** El portal publica actualizaciones anuales. Si un hash no coincide, el ETL se detiene e informa el cambio. Para procesar la nueva versión de todos modos, use `--accept-new-version`. El cambio queda registrado en `qa_report.json`, pero los resultados ya no serán comparables con los de referencia.

**5. Reproducir todos los notebooks en orden** (unos 15 minutos):

```bash
cd notebooks && for nb in 00_data_audit 01_EDA 02_feature_engineering 03_regression 04_classification 05_clustering 06_integrated_evaluation 07_storytelling; do python -m nbconvert --to notebook --execute --inplace $nb.ipynb; done
```

**6. Exportar los modelos finales y verificar la trazabilidad:**

```bash
python scripts/export_models.py
```

```bash
python scripts/check_traceability.py
```

El primer comando reajusta las configuraciones congeladas y comprueba que sus predicciones de 2025 coincidan con las de los notebooks. El segundo verifica los enlaces de los documentos y las cifras clave del informe final.

**Notebook de auditoría por separado (opcional).**

```bash
cd notebooks && python -m nbconvert --to notebook --execute --inplace 00_data_audit.ipynb
```

## Fuentes y licencias

| Fuente | Organismo | Licencia |
|---|---|---|
| Siniestros viales: hechos, víctimas y notas metodológicas 2019–2025 | Observatorio de Movilidad y Seguridad Vial, GCBA | Creative Commons Attribution |
| Barrios y comunas | DG Gobernanza de Datos Abiertos, GCBA | CC-BY-2.5-AR |
| Callejero y cruces semaforizados (uso descriptivo) | GCBA | CC-BY-2.5-AR |
| Volumen vehicular 2024 (extensión condicionada) | Observatorio de Movilidad y Seguridad Vial, GCBA | Creative Commons Attribution |

Las URL exactas, los hashes y las limitaciones de cada fuente están en el [registro de fuentes](docs/source_register.csv). Fuente de los datos: Buenos Aires Data, Gobierno de la Ciudad de Buenos Aires.

## Alcance e interpretación

- Los conteos son **carga registrada** de siniestros con víctimas (fuente policial). No representan riesgo ajustado por exposición.
- El proyecto es **predictivo**: la importancia de las variables no implica causalidad.
- La infraestructura vial disponible refleja solo el estado actual, por lo que se excluye de la evaluación predictiva principal (D11).

## Estado

| Paso | Estado |
|---|---|
| 01 Delimitación científica | Completado |
| 02 Relevamiento de fuentes | Completado (consulta institucional en borrador, no enviada) |
| 03 Auditoría de viabilidad | Completado |
| 04 Repositorio, entorno y ETL | Completado |
| 05 AED y análisis territorial | Completado |
| 06 Feature engineering y diseño experimental | Completado |
| 07 Regresión supervisada | Completado |
| 08 Clasificación supervisada | Completado |
| 09 Clustering no supervisado | Completado |
| 10 Integración y robustez | Completado |
| 11 Storytelling y presentación | Completado |
| 12 Validación final y entrega | Completado: [docs/final_validation.md](docs/final_validation.md) |
