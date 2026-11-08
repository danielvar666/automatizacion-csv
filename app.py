import os
import requests
import streamlit as st

# (Tu código de configuración y formulario va aquí arriba...)

if submitted:
    # Función auxiliar para leer variables sin romper la ejecución
    def get_secret(key):
        # 1. Intentar obtener desde variables de entorno del sistema (Render, local, etc.)
        val = os.getenv(key)
        if val:
            return val
        # 2. Si no existe en el sistema, buscar en st.secrets (Streamlit Cloud)
        try:
            return st.secrets.get(key, "")
        except Exception:
            return ""

    github_token = get_secret("GH_PAT").strip()
    repo_owner = get_secret("GH_OWNER").strip()
    repo_name = get_secret("GH_REPO").strip()

    if not github_token or not repo_owner or not repo_name:
        st.error(
            "❌ Error: Faltan credenciales. Revisa la sección 'Environment Variables' en Render."
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
                    url, json=payload, headers=headers, timeout=15
                )

                if response.status_code == 204:
                    st.success(
                        "✅ ¡Proceso iniciado con éxito en GitHub Actions!"
                    )
                else:
                    st.error(
                        f"❌ Error devuelto por GitHub ({response.status_code}): {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión al intentar contactar la API: {e}")