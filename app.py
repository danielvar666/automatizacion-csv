import base64
import json
import os
import time
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

# 6. LÓGICA DE ENVÍO A GITHUB ACTIONS (URL CORREGIDA A .COM)
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
            # URL CORREGIDA (.com en lugar de .org)
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

                    #if response.status_code == 204:
                    #    st.success(
                    #        f"✅ ¡Proceso iniciado por el ID `{st.session_state.usuario_id}`! El pipeline se está ejecutando en GitHub Actions."
                    #    )
                    if response.status_code == 204:
                        st.info(
                            f"⏳ Proceso iniciado por **{st.session_state.usuario_nombre}** (ID: `{st.session_state.usuario_id}`). Ejecutando scripts en GitHub Actions..."
                        )

                        # Esperar y verificar que el workflow termine con éxito
                        runs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/automatizacion.yml/runs?per_page=1"
                        time.sleep(5)  # Pausa breve mientras GitHub registra la ejecución

                        with st.spinner("Procesando lotes y subiendo archivos a Google Drive..."):
                            estado_final = None
                            for _ in range(36):  # Monitorea hasta por 3 minutos (36 x 5 seg)
                                run_resp = session.get(runs_url, headers=headers, timeout=15)
                                if run_resp.status_code == 200:
                                    runs = run_resp.json().get("workflow_runs", [])
                                    if runs:
                                        status = runs[0].get("status")          # queued, in_progress, completed
                                        conclusion = runs[0].get("conclusion")  # success, failure, cancelled
                                        if status == "completed":
                                            estado_final = conclusion
                                            break
                                time.sleep(5)

                        if estado_final == "success":
                            st.success(
                                f"✅ Proceso exitoso — Archivos generados y cargados a Google Drive por **{st.session_state.usuario_nombre}**."
                            )
                        elif estado_final is None:
                            st.warning(
                                "⚠️ El proceso sigue ejecutándose en segundo plano. Revisa Google Drive en un minuto."
                            )
                        else:
                            st.error(
                                f"❌ El procesamiento falló en GitHub Actions (estado: {estado_final})."
                            )
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error de red al conectar con GitHub API: {e}")