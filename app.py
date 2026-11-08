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
    github_token = os.getenv("GH_PAT")
    repo_owner = os.getenv("GH_OWNER")
    repo_name = os.getenv("GH_REPO")

    if not all([github_token, repo_owner, repo_name]):
        st.error(
            "❌ Faltan las variables secretas en Streamlit (GH_PAT, GH_OWNER, GH_REPO)."
        )
    else:
        with st.spinner("Enviando parámetros a GitHub Actions..."):
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

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 204:
                st.success(
                    "✅ ¡Proceso iniciado con éxito! El pipeline se ejecutará con los filtros de texto ingresados."
                )
            else:
                st.error(
                    f"❌ Error al iniciar. Código HTTP: {response.status_code}"
                )
                st.write(response.text)