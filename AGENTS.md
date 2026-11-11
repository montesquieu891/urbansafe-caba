# UrbanSafe CABA

Lee [el plan de implementación](UrbanSafe_CABA_Implementation_Plan.md) antes de iniciar un hito. Allí están la consigna académica, los entregables, la estructura prevista y los criterios de aceptación. Comienza por el primer hito pendiente. Cierra cada etapa con evidencia reproducible y registra sus decisiones y limitaciones.

Prioriza el núcleo académico. Define escala, horizonte y objetivo con la auditoría de viabilidad. Compara contra baselines y evalúa fuera de muestra. Distingue concentración, exposición y efectos causales. Mantén la trazabilidad desde las fuentes a las conclusiones.

## Skills por hito

Abre los `SKILL.md` pertinentes en [las skills del proyecto](.agents/skills). Usa las skills generales para ejecutar tareas concretas y las especializadas para las decisiones metodológicas de UrbanSafe.

| Pasos | Skills | Evidencia |
| --- | --- | --- |
| 01–02 | `literature-review` y `urban-data-auditor` desde el 02 | Propuesta, fuentes y cobertura |
| 03–04 | `urban-data-auditor`, `analyze-data-quality`, `jupyter-notebooks` y `geospatial-analysis` en la auditoría del 03 | Viabilidad, panel y ETL verificables |
| 05 | `geospatial-analysis`, `statistical-analysis`, `jupyter-notebooks` y `visualize-data` | AED, patrones y mapas |
| 06–08 | `spatiotemporal-ml`, `jupyter-notebooks` y `ml-scientific-reviewer` al cierre | Protocolo, controles de fuga y evaluación fuera de muestra |
| 09 | `clustering-research`, `jupyter-notebooks` y `ml-scientific-reviewer` al cierre | Perfiles y estabilidad |
| 10 | `geospatial-analysis`, `jupyter-notebooks` y `ml-scientific-reviewer` | Robustez y comparación de priorización |
| 11–12 | `visualize-data` en el 11, `validate-data` y `ml-scientific-reviewer` en la validación final de resultados de modelado | Presentación y entrega reproducible |

`build-dashboard` corresponde a una extensión posterior a la entrega académica, si se solicita. Para mantener las skills usa `$skill-creator`.

### Auditoría de Colabs

Para una revisión integral de un notebook abre primero [colab-reproducibility-audit](.agents/skills/colab-reproducibility-audit/SKILL.md). Añade [colab-data-audit](.agents/skills/colab-data-audit/SKILL.md) si el notebook transforma o explora datos y [colab-ml-validation](.agents/skills/colab-ml-validation/SKILL.md) si genera variables predictoras, entrena modelos, evalúa rankings o produce clusters. 
