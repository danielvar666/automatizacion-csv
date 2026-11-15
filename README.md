# 🚀 Pipeline Automatizado DataOps: Procesamiento CSV, Portal Web y Auditoría

Sistema integral de automatización de datos construido con **Python**, **Streamlit (Render)** y **GitHub Actions** para el procesamiento, segmentación incremental, formateo, entrega en **Google Drive** y trazabilidad en **Google Sheets** de grandes volúmenes de registros (~200MB+).

---

## 🛠️ Stack Tecnológico

- **Python 3.11**: Procesamiento y transformación de datos (`pandas`, `numpy`).
- **Streamlit + Render**: Portal web interactivo desplegado en la nube para operadores, con control de acceso por ID, Modo Demo para visitantes y síntesis de voz nativa (`Web Speech API`).
- **GitHub Actions**: Orquestación CI/CD con disparo remoto vía API (`workflow_dispatch`) y control de concurrencia (`concurrency`) para encolar ejecuciones simultáneas sin colisiones.
- **Google Sheets API (`gspread`)**: Bitácora automática de auditoría que registra operador, fecha/hora, rangos procesados y estado final (`Exitoso` / `Fallido`).
- **Rclone**: Transferencia automatizada y segura hacia Google Drive mediante OAuth 2.0 con nombres de archivo dinámicos por marca de tiempo.
- **Git LFS & JSON**: Gestión de archivos fuente de gran volumen y persistencia transaccional de índices (`estado.json`) para garantizar lotes secuenciales sin duplicados.
- **pytest**: Suite de pruebas unitarias locales para validar la lógica de segmentación y manejo de datos vacíos.

---

## ⚙️ Arquitectura del Flujo

### 1. Portal de Control y Accesibilidad (`app.py` en Render)
- **Control de Acceso:** Autenticación mediante ID de operador vinculado a variables de entorno seguras, más un **Modo Demo** para demostraciones sin afectar índices de producción.
- **Monitoreo en Tiempo Real y Voz:** Consulta el estado de la corrida en GitHub Actions mediante *polling* y emite confirmación visual y auditiva personalizada al finalizar el registro en Google Sheets.

### 2. Control de Concurrencia y Extracción (`script1.py`)
- Cola de ejecución única (`cancel-in-progress: false`) para evitar condiciones de carrera si varios operadores disparan lotes al mismo tiempo.
- Cruce, deduplicación, filtrado dinámico y rebanado incremental leyendo y actualizando `estado.json` (`inicio_samsung` e `inicio_generico`).

### 3. Formateo de Entrega (`script2.py`)
- Estandarización de columnas según reglas de negocio y asignación dinámica de nombres de grupo (`filtro_grupo_samsung`, `filtro_grupo_generico`).

### 4. Despliegue en Google Drive y Auditoría (`auditoria.py`)
- **Almacenamiento Histórico:** Carga automática vía `rclone copyto` generando archivos únicos con sello de tiempo (`_YYYY-MM-DD_HH-MM-SS.csv`) para evitar sobrescrituras.
- **Trazabilidad Completa:** Registro automático en Google Sheets tanto en ejecuciones exitosas (`if: success()`) como ante fallos (`if: failure()`).

---

## 🧪 Pruebas Unitarias (Local)

Para ejecutar las pruebas unitarias localmente antes de subir cambios:

```bash
py -m pip install -r requirements.txt
py -m pytest tests/