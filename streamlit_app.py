import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

# -----------------------
# CONFIG GOOGLE SHEETS
# -----------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

SHEET_NAME = st.secrets.get("SHEET_NAME", "Feria_2026")
sheet = client.open(SHEET_NAME).sheet1

# -----------------------
# CONFIG APP
# -----------------------
st.set_page_config(page_title="Registro Feria", page_icon="📋")

st.title("Registro de Interesados")

# -----------------------
# SESSION STATE
# -----------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "data" not in st.session_state:
    st.session_state.data = {}

# -----------------------
# PASO 1: RUBRO
# -----------------------
if st.session_state.step == 1:
    st.subheader("¿Qué rubro le interesó?")

    rubros = [
        "Compactación",
        "Cintas transportadoras",
        "Contenedores",
        "Ruedas",
        "Otro"
    ]

    seleccionados = []
    for r in rubros:
        if st.checkbox(r):
            seleccionados.append(r)

    if st.button("Siguiente"):
        if seleccionados:
            st.session_state.data["rubro"] = ", ".join(seleccionados)
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Seleccioná al menos un rubro")

# -----------------------
# PASO 2: NOMBRE
# -----------------------
elif st.session_state.step == 2:
    nombre = st.text_input("Nombre")

    if st.button("Siguiente"):
        if nombre:
            st.session_state.data["nombre"] = nombre
            st.session_state.step = 3
            st.rerun()
        else:
            st.warning("Ingresá el nombre")

# -----------------------
# PASO 3: EMPRESA
# -----------------------
elif st.session_state.step == 3:
    empresa = st.text_input("Empresa")

    if st.button("Siguiente"):
        if empresa:
            st.session_state.data["empresa"] = empresa
            st.session_state.step = 4
            st.rerun()
        else:
            st.warning("Ingresá la empresa")

# -----------------------
# PASO 4: CONTACTO
# -----------------------
elif st.session_state.step == 4:
    contacto = st.text_input("Contacto (teléfono o email)")

    if st.button("Siguiente"):
        if contacto:
            st.session_state.data["contacto"] = contacto
            st.session_state.step = 5
            st.rerun()
        else:
            st.warning("Ingresá un contacto")

# -----------------------
# PASO 5: COMENTARIOS
# -----------------------
elif st.session_state.step == 5:
    comentarios = st.text_area("Comentarios (opcional)")

    if st.button("Guardar"):
        now = datetime.now(ZoneInfo("America/Montevideo"))

        fila = [
            now.strftime("%Y-%m-%d %H:%M"),
            st.session_state.data.get("rubro", ""),
            st.session_state.data.get("nombre", ""),
            st.session_state.data.get("empresa", ""),
            st.session_state.data.get("contacto", ""),
            comentarios
        ]

        sheet.append_row(fila)

        st.success("Guardado correctamente")

        # RESET TOTAL
        st.session_state.step = 1
        st.session_state.data = {}

        st.rerun()
