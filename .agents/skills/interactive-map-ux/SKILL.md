---
name: interactive-map-ux
description: Implementa y revisa la interacción sincronizada entre mapa, ficha de barrio y simulador retrospectivo de UrbanSafe.
---

# Interacción cartográfica de UrbanSafe

- Mantén el mes, barrio, métrica, estrategia y K en un estado compartido. Refleja los filtros relevantes en la URL. El mapa, la ficha y el ranking deben mostrar el mismo corte y responder juntos al cambiar un filtro.
- En el atlas, indica unidad, período y fuente. Distingue conteo de densidad por superficie. Usa escalas comparables entre meses de una misma métrica y separa visualmente cero de sin datos.
- En el simulador, muestra qué información estaba disponible al corte, la selección y la cobertura observada en 2025. Distingue los barrios compartidos y exclusivos de cada estrategia mediante texto o contorno además del color.
- Da acceso equivalente a las selecciones con una lista navegable por teclado. Conserva foco visible, etiquetas legibles y una ficha que funcione en móvil. Aclara el carácter exploratorio de la subdivisión del interior.
