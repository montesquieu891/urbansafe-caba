---
name: static-web-release
description: Prepara, verifica y publica con autorización versiones estáticas de la web de UrbanSafe.
---

# Publicación estática

- Compila con dependencias fijadas y un paquete de datos versionado. Publica únicamente el directorio de salida. Revisa el contenido servido para excluir datos crudos, secretos, modelos y artefactos privados.
- Crea una vista previa y verifica enlaces, rutas directas, recarga con filtros, atribución, manifiesto y carga de geometrías y gráficos. Registra el commit, la versión del paquete de datos y el resultado de las pruebas.
- Con autorización expresa, promociona a producción la versión revisada y verifica que la URL pública sirva el manifiesto y las páginas esperadas. Conserva el identificador de la versión anterior para revertir si falla la comprobación.
