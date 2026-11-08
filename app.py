import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Panel de Control - Procesamiento CSV", page_icon="📊"
)

st.title("📊 Procesamiento de Datos CSV")
st.markdown(
    "Ingresa las cantidades de registros y escribe los filtros de grupo para Samsung y Genérico antes de iniciar la automatización."
)

st.divider()

with st.form("pipeline_form"):
    st.subheader("⚙️ Configuración de Lotes y Filtros")

    # --- SECCIÓN SAMSUNG ---
    st.markdown("### 📱 Lote Samsung")
    col1, col2 = st.columns(2)
    with col1:
        cant_samsung = st.number_input(
            "Cantidad Samsung",
            min_value=1,
            max_value=100000,
            value=100,
            step=50,
        )
    with col2:
        filtro_grupo_samsung = st.text_input(
            "Filtro Grupo Samsung",
            value="VACUNADO",
            help="Escribe el texto exacto con el que deseas filtrar la columna de grupo para Samsung",
        )

    st.divider()

    # --- SECCIÓN GENÉRICO ---
    st.markdown("### 🌐 Lote Genérico")
    col3, col4 = st.columns(2)
    with col3:
        cant_generico = st.number_input(
            "Cantidad Genérico",
            min_value=1,
            max_value=100000,
            value=100,
            step=50,
        )
    with col4:
        filtro_grupo_generico = st.text_input(
            "Filtro Grupo Genérico",
            value="GENERICO_LOTE1",
            help="Escribe el texto exacto con el que deseas filtrar la columna de grupo para Genérico",
        )

    st.divider()

    submitted = st.form_submit_button(
        "🚀 Disparar Procesamiento", use_container_width=True
    )

if submitted:
    # 1. Obtención prioritaria desde st.secrets
    github_token = st.secrets.get("GH_PAT", os.getenv("GH_PAT", "")).strip()
    repo_owner = st.secrets.get("GH_OWNER", os.getenv("GH_OWNER", "")).strip()
    repo_name = st.secrets.get("GH_REPO", os.getenv("GH_REPO", "")).strip()

    # 2. Control de errores ante variables vacías
    if not github_token or not repo_owner or not repo_name:
        st.error(
            "❌ Error: Faltan secretos en Streamlit Cloud. Asegúrate de guardar GH_PAT, GH_OWNER y GH_REPO en 'Configuración avanzada > Misterios'."
        )
    else:
        url = f"https://api.github.org/repos/{repo_owner}/{repo_name}/actions/workflows/automatizacion.yml/dispatches"

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        payload = {
            "ref": "main",
            "inputs": {
                "cantidad_samsung": str(cant_samsung),
                "filtro_grupo_samsung": filtro_grupo_samsung,
                "cantidad_generico": str(cant_generico),
                "filtro_grupo_generico": filtro_grupo_generico,
            },
        }

        with st.spinner("Enviando parámetros a GitHub Actions..."):
            try:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=10
                )

                if response.status_code == 204:
                    st.success(
                        "✅ ¡Proceso iniciado con éxito! El pipeline se está ejecutando en GitHub Actions."
                    )
                else:
                    st.error(
                        f"❌ Error devuelto por GitHub ({response.status_code}): {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                st.error(
                    f"❌ Error de red al intentar conectar a la API ({url}): {e}"
                )