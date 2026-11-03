# 🚀 Automatización y Procesamiento de Datos CSV con GitHub Actions

Sistema de automatización en Python alojado en GitHub Actions para el procesamiento, segmentación diaria y formateo de grandes volúmenes de datos (~200MB+).

## 🛠️ Tecnologías Utilizadas
* **Python 3.10**: Procesamiento dinámico de datos (`pandas`, `numpy`).
* **Git LFS**: Gestión e integración de archivos CSV de gran tamaño.
* **GitHub Actions**: Pipeline CI/CD para ejecuciones interactivas (`workflow_dispatch`).
* **JSON**: Persistencia de estado e índice de registros entre ejecuciones diarias.

## ⚙️ Arquitectura del Flujo
1. **Script 1 (`script1.py`)**: 
   - Cruce, deduplicación y filtrado de bases de datos de entrada (`BASE VAC 2.csv` y `VAC.csv`).
   - Slicing dinámico según las cantidades solicitadas por el usuario.
   - Guardado de posición y memoria en `estado.json` para garantizar procesamientos secuenciales y sin duplicados entre días.
2. **Script 2 (`script2.py`)**: 
   - Transformación de estructura de columnas según requerimientos de negocio.
   - Asignación dinámica de nombres de grupo (`grupo_nombre`).
   - Exportación de archivos CSV finales listos para entrega.

## 🚀 Ejecución en GitHub Actions
El proyecto se ejecuta de forma interactiva desde la pestaña **Actions** de GitHub introduciendo los parámetros requeridos:
- Cantidad de registros (Samsung / Genérico).
- Etiqueta de grupo diaria.