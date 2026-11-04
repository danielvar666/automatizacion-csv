# 🚀 Automatización y Procesamiento de Datos CSV con GitHub Actions

Sistema de automatización en Python alojado en GitHub Actions para el procesamiento, segmentación diaria, formateo y despliegue automático en Google Drive de grandes volúmenes de datos (~200MB+).

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.10**: Procesamiento dinámico de datos (`pandas`, `numpy`).
- **Rclone**: Transferencia automatizada y segura de archivos hacia Google Drive vía OAuth 2.0.
- **Git LFS**: Gestión e integración de archivos CSV de gran tamaño.
- **GitHub Actions**: Pipeline CI/CD para ejecuciones interactivas (`workflow_dispatch`).
- **JSON**: Persistencia del estado e índice de registros (`estado.json`) para garantizar ejecuciones secuenciales sin duplicados.

---

## ⚙️ Arquitectura del Flujo

1. **Script 1 (`script1.py`)**:
   - Cruce, deduplicación y filtrado de bases de datos de entrada (`BASE VAC 2.csv` y `VAC.csv`).
   - Rebanado dinámico según las cantidades solicitadas por el usuario.
   - Actualización del índice de lectura en `estado.json` (`inicio_samsung` e `inicio_generico`) para mantener la trazabilidad de lotes.

2. **Script 2 (`script2.py`)**:
   - Transformación de la estructura de columnas según los requerimientos de negocio.
   - Asignación dinámica de nombres de grupo (`grupo_nombre`).
   - Exportación de los archivos CSV finales generados.

3. **Subida Automática a Google Drive**:
   - Autenticación segura mediante `rclone` utilizando tokens OAuth 2.0 y carpetas parametrizadas por variables de entorno (`GDRIVE_FOLDER_ID`).
   - Copia directa de los archivos producidos (`co_mobile_ft_vac_samsung_final.csv` y `co_mobile_ft_vac_generico_final.csv`) a la unidad de almacenamiento.

---

## 🚀 Ejecución en GitHub Actions

El proyecto se ejecuta de forma interactiva desde la pestaña **Actions** de GitHub mediante el evento `workflow_dispatch`:

1. Selecciona el workflow en la pestaña **Actions**.
2. Introduce los parámetros requeridos:
   - **Cantidad de registros** (Samsung / Genérico).
   - **Etiqueta de grupo diaria**.
3. Haz clic en **Run workflow**.

El pipeline procesará la información, actualizará los estados y dejará los archivos disponibles inmediatamente en tu carpeta de Google Drive.