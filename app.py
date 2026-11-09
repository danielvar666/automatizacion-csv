import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.set_page_config(
    page_title="Panel de Control - Procesamiento CSV",
    page_icon="📊",
    layout="centered",
)

st.title("👋 Panel de Control")

# ---------------------------------------------------------
# BOTÓN DE BIENVENIDA QUE DESBLOQUEA EL AUDIO
if "audio_reproducido" not in st.session_state:
    st.session_state.audio_reproducido = False

col_welcome, col_btn = st.columns([3, 1])
with col_welcome:
    st.subheader("¡Bienvenido, Data Lovers!")
with col_btn:
    if st.button("🔊 Activar Saludo", use_container_width=True):
        st.session_state.audio_reproducido = True
        components.html(
            """
            <script>
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance("¡Bienvenido, Data Lovers!");
                    utterance.lang = 'es-ES';
                    utterance.rate = 1.0;
                    window.speechSynthesis.speak(utterance);
                }
            </script>
            """,
            height=0,
        )

st.markdown(
    "Ingresa las cantidades de registros y escribe los filtros de grupo para **Samsung** y **Genérico** antes de iniciar la automatización."
)
# ---------------------------------------------------------

st.divider()

# (Formulario normal de Streamlit abajo)
with st.form("pipeline_form"):
    st.subheader("⚙️ Configuración de Lotes y Filtros")

    st.markdown("### 📱 Lote Samsung")
    col1, col2 = st.columns(2)
    with col1:
        cant_samsung = st.number_input(
            "Cantidad Samsung", min_value=1, max_value=100000, value=100
        )
    with col2:
        filtro_grupo_samsung = st.text_input(
            "Filtro Grupo Samsung", value="VACUNADO"
        )

    st.divider()

    st.markdown("### 🌐 Lote Genérico")
    col3, col4 = st.columns(2)
    with col3:
        cant_generico = st.number_input(
            "Cantidad Genérico", min_value=1, max_value=100000, value=100
        )
    with col4:
        filtro_grupo_generico = st.text_input(
            "Filtro Grupo Genérico", value="GENERICO_LOTE1"
        )

    st.divider()

    submitted = st.form_submit_button(
        "🚀 Disparar Procesamiento", use_container_width=True
    )

if submitted:

    def get_secret(key):
        val = os.getenv(key)
        if val:
            return val
        try:
            return st.secrets.get(key, "")
        except Exception:
            return ""

    github_token = get_secret("GH_PAT").strip()
    repo_owner = get_secret("GH_OWNER").strip()
    repo_name = get_secret("GH_REPO").strip()

    if not github_token or not repo_owner or not repo_name:
        st.error("❌ Error: Faltan credenciales en Render.")
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

        with st.spinner("Enviando orden a GitHub Actions..."):
            try:
                session = requests.Session()
                retries = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504],
                )
                session.mount("https://", HTTPAdapter(max_retries=retries))

                response = session.post(
                    url, json=payload, headers=headers, timeout=15
                )

                if response.status_code == 204:
                    st.success("✅ ¡Proceso iniciado con éxito!")
                else:
                    st.error(f"❌ Error HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión: {e}")