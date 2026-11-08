# 🚀 Automatización y Procesamiento de Datos CSV con GitHub Actions

Sistema de automatización en Python alojado en GitHub Actions para el procesamiento, segmentación diaria, formateo, control de calidad y despliegue automático en Google Drive de grandes volúmenes de datos (~200MB+).

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.10**: Procesamiento dinámico de datos (`pandas`, `numpy`).
- **pytest**: Suite de pruebas unitarias integradas para garantizar el control de calidad en CI/CD.
- **Logging**: Registros de auditoría estructurados para trazabilidad del pipeline.
- **Rclone**: Transferencia automatizada y segura de archivos hacia Google Drive vía OAuth 2.0.
- **Git LFS**: Gestión e integración de archivos CSV de gran tamaño.
- **GitHub Actions**: Pipeline CI/CD con control de calidad y ejecuciones interactivas (`workflow_dispatch`).
- **JSON**: Persistencia del estado e índice de registros (`estado.json`) para garantizar ejecuciones secuenciales sin duplicados.

---

## ⚙️ Arquitectura del Flujo

### 1. Control de Calidad (CI Quality Gate)
- Ejecución automática de pruebas unitarias con `pytest` en la carpeta `tests/`.
- Validación preventiva de lógica de rebanado y manejo de datos vacíos antes de procesar o alterar el almacenamiento.

### 2. Procesamiento de Datos (`script1.py`)
- Cruce, deduplicación y filtrado de bases de datos de entrada (`BASE VAC 2.csv` y `VAC.csv`).
- Rebanado dinámico según las cantidades solicitadas por el usuario.
- Registros detallados con `logging` en lugar de impresiones estándar.
- Actualización del índice de lectura en `estado.json` (`inicio_samsung` e `inicio_generico`) para mantener la trazabilidad de lotes.

### 3. Formateo de Entrega (`script2.py`)
- Transformación de la estructura de columnas según los requerimientos de negocio.
- Asignación dinámica de nombres de grupo (`grupo_nombre`).
- Exportación de los archivos CSV finales generados.

### 4. Subida automática a Google Drive
- Autenticación segura mediante `rclone` utilizando tokens OAuth 2.0 y carpetas parametrizadas por variables de entorno (`GDRIVE_FOLDER_ID`).
- Copia directa de los archivos producidos (`co_mobile_ft_vac_samsung_final.csv` y `co_mobile_ft_vac_generico_final.csv`) a la unidad de almacenamiento.

---

## 🧪 Pruebas Unitarias (Local)

Para ejecutar las pruebas unitarias localmente antes de subir cambios:

```bash
py -m pip install -r requirements.txt
py -m pytest tests/