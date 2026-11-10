---
name: analyze-data-quality
description: Perfila y reconcilia la calidad de tablas, archivos y salidas del ETL de UrbanSafe antes de usarlos como evidencia.
---

# analyze-data-quality

- Define uso, granularidad y clave esperada. Mide cobertura, nulos, duplicados, rangos, categorías e integridad referencial. Desglosa por fuente, período y territorio cuando el agregado oculte faltantes sistemáticos.
- Controla cardinalidad y totales antes y después de joins y filtros. Para fuentes discordantes compara definiciones, ventanas y versiones antes de adjudicar diferencias.
- Reporta impacto sobre el uso previsto, evidencia reproducible y severidad. Convierte en controles automatizados las reglas repetibles. Para viabilidad vial y relación hecho-víctima aplica además la skill específica.

Adaptación local del [SKILL.md de origen](https://github.com/openai/plugins/blob/main/plugins/data-analytics/skills/analyze-data-quality/SKILL.md).
