import base64
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Panel de Control - Procesamiento CSV",
    page_icon="📊",
    layout="centered",
)


# ---------------------------------------------------------
# 2. LOGO SUPERIOR Y ESTILOS LIMPIOS (HEADER OCULTO)
# ---------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


try:
    bin_str = get_base64_of_bin_file("fondo.jpg")
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/jpg;base64,{bin_str}" style="max-width: 240px; height: auto;">
        </div>
        """,
        unsafe_allow_html=True,
    )
except Exception:
    pass

st.markdown(
    """
    <style>
    /* 1. Ocultar la barra superior negra nativa de Streamlit */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: none !important;
    }
    
    /* 2. Fondo general de la página */
    [data-testid="stAppViewContainer"] {
        background-color: #f1f5f9;
    }

    /* 3. Tarjeta central limpia */
    .stMainBlockContainer {
        background-color: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.06);
    }

    /* 4. Textos oscuros de alto contraste */
    h1, h2, h3, .stMarkdown, p, label {
        color: #0f172a !important;
    }

    /* 5. Cajas de entrada de texto e inputs en fondo claro y borde visible */
    input[type="text"], input[type="number"], div[data-baseweb="input"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* 6. Botones principales estilo LAX Tech */
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #e11d48 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
    }

    div.stButton > button *, div.stFormSubmitButton > button * {
        color: #ffffff !important;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #be123c !important;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)
# ---------------------------------------------------------

st.title("👋 Panel de Control")
st.subheader("¡Bienvenido, Data Lovers!")

if st.button("🔊 Activar Saludo de Bienvenida", use_container_width=True):
    audio_js = """
        <script>
            (function() {
                const targetWindow = window.parent || window;
                if ('speechSynthesis' in targetWindow) {
                    targetWindow.speechSynthesis.cancel();
                    const msg = new targetWindow.SpeechSynthesisUtterance("¡Bienvenido, Data Lovers!");
                    msg.lang = 'es-ES';
                    msg.rate = 1.0;
                    targetWindow.speechSynthesis.speak(msg);
                }
            })();
        </script>
    """
    components.html(audio_js, height=0)

st.markdown(
    "Ingresa las cantidades de registros y escribe los filtros de grupo para **Samsung** y **Genérico** antes de iniciar la automatización."
)
st.divider()

# 3. FORMULARIO DE CONFIGURACIÓN
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
            value="ingrese",
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
            value="ingrese",
            help="Escribe el texto exacto con el que deseas filtrar la columna de grupo para Genérico",
        )

    st.divider()

    submitted = st.form_submit_button(
        "🚀 Disparar Procesamiento", use_container_width=True
    )

# 4. LÓGICA DE ENVÍO A GITHUB ACTIONS
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
        st.error(
            "❌ Error: Faltan credenciales. Verifica 'Environment Variables' en Render (GH_PAT, GH_OWNER, GH_REPO)."
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
                    st.success(
                        "✅ ¡Proceso iniciado con éxito! El pipeline se está ejecutando en GitHub Actions."
                    )
                else:
                    st.error(
                        f"❌ Error devuelto por GitHub ({response.status_code}): {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de red al conectar con GitHub API: {e}")