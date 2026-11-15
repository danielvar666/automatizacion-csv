import base64
from datetime import datetime
import json
import os
import time
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
import gspread
import requests
from requests.adapters import HTTPAdapter
import streamlit as st
import streamlit.components.v1 as components
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
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: none !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #f1f5f9;
    }
    .stMainBlockContainer {
        background-color: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.06);
    }
    h1, h2, h3, .stMarkdown, p, label {
        color: #0f172a !important;
    }
    input[type="text"], input[type="password"], input[type="number"], div[data-baseweb="input"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
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
    /* 7. Texto legible dentro de alertas de estado y éxito */
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] code {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Función para leer variables de entorno de Render o secrets
def get_secret(key):
    val = os.getenv(key)
    if val:
        return val
    try:
        return st.secrets.get(key, "")
    except Exception:
        return ""

def obtener_indices_github(repo_owner, repo_name, headers):
    url_estado = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/estado.json"
    try:
        resp = requests.get(url_estado, headers=headers, timeout=10)
        if resp.status_code == 200:
            contenido_b64 = resp.json().get("content", "")
            datos = json.loads(base64.b64decode(contenido_b64).decode("utf-8"))
            return datos.get("inicio_samsung", 0), datos.get("inicio_generico", 0)
    except Exception:
        pass
    return None, None

def registrar_auditoria(
    usuario_id,
    usuario_nombre,
    cant_samsung,
    rango_samsung,
    filtro_samsung,
    cant_generico,
    rango_generico,
    filtro_generico,
    estado,
):
    creds_raw = get_secret("GCP_SERVICE_ACCOUNT")
    sheet_id = get_secret("GOOGLE_SHEET_ID").strip()

    if not creds_raw or not sheet_id:
        return False, "Faltan credenciales de Google Sheets en Render."

    try:
        creds_dict = json.loads(creds_raw)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1

        ahora_col = datetime.now(ZoneInfo("America/Bogota"))
        fecha_str = ahora_col.strftime("%Y-%m-%d")
        hora_str = ahora_col.strftime("%H:%M:%S")

        fila = [
            fecha_str,
            hora_str,
            str(usuario_id),
            str(usuario_nombre),
            int(cant_samsung),
            str(rango_samsung),
            str(filtro_samsung),
            int(cant_generico),
            str(rango_generico),
            str(filtro_generico),
            str(estado),
        ]
        sheet.append_row(fila)
        return True, "Registro guardado en bitácora."
    except Exception as e:
        return False, f"No se pudo escribir en Google Sheets: {e}"

# ---------------------------------------------------------
# 3. PANTALLA DE SOLICITUD DE ID CON ASOCIACIÓN DE NOMBRE
# ---------------------------------------------------------
if "acceso_autorizado" not in st.session_state:
    st.session_state.acceso_autorizado = False
    st.session_state.usuario_id = ""
    st.session_state.usuario_nombre = ""

if not st.session_state.acceso_autorizado:
    st.title("🔐 Control de Acceso")
    st.markdown(
        "Ingresa tu **número de identificación** para acceder al panel o entra en modo visitante."
    )

    id_ingresado = st.text_input(
        "ID de Acceso", type="password", placeholder="Escribe tu cédula aquí..."
    )

    col_ingresar, col_demo = st.columns(2)
    with col_ingresar:
        if st.button("✅ Ingresar con mi ID", use_container_width=True):
            operadores_raw = get_secret("OPERADORES_JSON")
            try:
                # Convierte el texto JSON de Render en un diccionario de Python
                operadores = (
                    json.loads(operadores_raw)
                    if operadores_raw
                    else {"lax2026": "Administrador"}
                )
            except json.JSONDecodeError:
                operadores = {"lax2026": "Administrador"}

            id_limpio = id_ingresado.strip()

            if id_limpio in operadores:
                st.session_state.acceso_autorizado = True
                st.session_state.usuario_id = id_limpio
                st.session_state.usuario_nombre = operadores[id_limpio]
                st.rerun()
            else:
                st.error("❌ ID no autorizado. Verifica tu número.")

    with col_demo:
        if st.button("👀 Modo Demo (Visitantes)", use_container_width=True):
            st.session_state.acceso_autorizado = True
            st.session_state.usuario_id = "DEMO"
            st.session_state.usuario_nombre = "Visitante Portafolio"
            st.rerun()

    st.stop()
# ---------------------------------------------------------
# 4. TU INTERFAZ PRINCIPAL (SOLO VISIBLE TRAS VALIDAR ID)
# ---------------------------------------------------------
col_tit, col_salir = st.columns([4, 1])
with col_tit:
    st.title("👋 Panel de Control")
with col_salir:
    st.write("")
    if st.button("🔒 Salir"):
        st.session_state.acceso_autorizado = False
        st.session_state.usuario_id = ""
        st.rerun()

#st.subheader(
#    f"¡Bienvenido, Data Lovers! (ID: {st.session_state.usuario_id})"
#)

st.subheader(f"¡Bienvenido, Data Lovers! {st.session_state.usuario_nombre}")

if st.button("🔊 Activar Saludo de Bienvenida", use_container_width=True):
    nombre_limpio = st.session_state.usuario_nombre.replace('"', '').replace("'", "")
    audio_js = f"""
        <script>
            (function() {{
                const targetWindow = window.parent || window;
                if ('speechSynthesis' in targetWindow) {{
                    targetWindow.speechSynthesis.cancel();
                    const msg = new targetWindow.SpeechSynthesisUtterance("¡Bienvenido, Data Lovers, {nombre_limpio}!");
                    msg.lang = 'es-ES';
                    msg.rate = 1.0;
                    targetWindow.speechSynthesis.speak(msg);
                }}
            }})();
        </script>
    """
    components.html(audio_js, height=0)

st.markdown(
    "Ingresa las cantidades de registros y escribe los filtros de grupo para **Samsung** y **Genérico** antes de iniciar la automatización."
)
st.divider()

# 5. FORMULARIO DE CONFIGURACIÓN
with st.form("pipeline_form"):
    st.subheader("⚙️ Configuración de Lotes y Filtros")

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

# 6. LÓGICA DE ENVÍO A GITHUB ACTIONS
if submitted:
    if st.session_state.usuario_id == "DEMO":
        with st.spinner("Simulando ejecución en Modo Demo..."):
            time.sleep(1.5)
        st.success(
            f"✅ [MODO DEMO] Simulación exitosa: {cant_samsung} Samsung y {cant_generico} Genérico."
        )
    else:
        github_token = get_secret("GH_PAT").strip()
        repo_owner = get_secret("GH_OWNER").strip()
        repo_name = get_secret("GH_REPO").strip()

        if not github_token or not repo_owner or not repo_name:
            st.error(
                "❌ Error: Faltan credenciales. Verifica 'Environment Variables' en Render (GH_PAT, GH_OWNER, GH_REPO)."
            )
        else:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/automatizacion.yml/dispatches"

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
                    "usuario_id": str(st.session_state.usuario_id),
                    "usuario_nombre": str(st.session_state.usuario_nombre),
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
                            f"✅ Orden enviada por **{st.session_state.usuario_nombre}** (ID: `{st.session_state.usuario_id}`). "
                            "Los archivos se subirán a Google Drive y quedarán registrados automáticamente en la bitácora en ~45 segundos."
                        )
                    else:
                        st.error(
                            f"❌ Error al disparar el pipeline (HTTP {response.status_code}): {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error de red al conectar con GitHub API: {e}")