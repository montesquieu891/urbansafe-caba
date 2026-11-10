---
name: dashboard-e2e
description: Verifica en navegador los recorridos, estados y cifras del atlas y simulador de UrbanSafe con Playwright.
---

# Pruebas de extremo a extremo

- Ejecuta las pruebas sobre una compilación local con datos fijos y versionados. Usa expectativas de referencia derivadas de los artefactos de Python, independientes de la implementación del frontend.
- Verifica el recorrido de seleccionar un barrio, cambiar de mes y cambiar de métrica. Comprueba que mapa, ficha, serie y leyenda reflejen el mismo estado. Incluye un cero observado, un caso sin datos y una URL con filtros que sobreviva a una recarga.
- Para 2025 y K = 10, valida las coberturas anuales publicadas de 42,73 % para el historial de 12 meses y 43,05 % para el clasificador. Prueba el recuento de K selecciones, el empate y la cobertura en al menos un mes de referencia.
- Repite los recorridos principales en escritorio y móvil, con al menos una ruta por teclado. Usa aserciones sobre nombres accesibles y valores visibles. Guarda evidencia de fallos en el entorno de pruebas.
