import os
import requests
import streamlit as st

# Configuración visual de la interfaz
st.set_page_config(
    page_title="Panel de Control - Procesamiento CSV", page_icon="📊"
)

st.title("📊 Procesamiento de Datos CSV")
st.markdown(
    "Selecciona los parámetros del lote para ejecutar la automatización en el servidor."
)

st.divider()

# Formulario interactivo
with st.form("pipeline_form"):
    st.subheader("⚙️ Configuración del Lote")

    cantidad_samsung = st.number_input(
        "Cantidad de registros Samsung",
        min_value=1,
        max_value=50000,
        value=100,
        step=50,
    )

    cantidad_generico = st.number_input(
        "Cantidad de registros Genérico",
        min_value=1,
        max_value=50000,
        value=100,
        step=50,
    )

    grupo_nombre = st.text_input(
        "Etiqueta o Nombre del Grupo",
        value="LOTE_DIARIO",
        help="Identificador que se asignará en la columna grupo_nombre",
    )

    submitted = st.form_submit_button(
        "🚀 Disparar Procesamiento", use_container_width=True
    )

# Acción al presionar el botón
if submitted:
    # Obtener variables de entorno (guardadas de forma segura en Streamlit Cloud)
    github_token = os.getenv("GH_PAT")
    repo_owner = os.getenv("GH_OWNER")  # Tu usuario de GitHub
    repo_name = os.getenv("GH_REPO")  # Nombre del repositorio

    if not all([github_token, repo_owner, repo_name]):
        st.error(
            "❌ Faltan credenciales de entorno (GH_PAT, GH_OWNER, GH_REPO)."
        )
    else:
        with st.spinner("Enviando orden a GitHub Actions..."):
            url = f"https://api.github.org/repos/{repo_owner}/{repo_name}/actions/workflows/automatizacion.yml/dispatches"

            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            payload = {
                "ref": "main",
                "inputs": {
                    "cantidad_samsung": str(cantidad_samsung),
                    "cantidad_generico": str(cantidad_generico),
                    "grupo_nombre": grupo_nombre,
                },
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 204:
                st.success(
                    "✅ ¡Proceso iniciado con éxito! El pipeline se está ejecutando en GitHub y subirá los archivos a Google Drive al finalizar."
                )
            else:
                st.error(
                    f"❌ Error al iniciar el flujo. Código HTTP: {response.status_code}"
                )
                st.write(response.text)