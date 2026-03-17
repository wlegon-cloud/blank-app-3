import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import io

st.set_page_config(page_title="Registro Feria", layout="centered")

st.title("Registro rápido - Feria")

# Estilo botones grandes
st.markdown("""
    <style>
    div.stButton > button {
        height: 80px;
        width: 100%;
        font-size: 18px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

FILE_NAME = "contactos.csv"

# Crear archivo si no existe
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=[
        "Fecha", "Rubro", "Nombre", "Empresa", "Contacto", "Comentarios"
    ])
    df.to_csv(FILE_NAME, index=False)

# -------------------------
# RUBROS (BOTONES CUADRADOS)
# -------------------------
rubros = [
    "Logística",
    "Industria",
    "Retail",
    "Construcción",
    "Agro",
    "Otro"
]

st.subheader("¿Qué rubro le interesa?")

if "rubro" not in st.session_state:
    st.session_state.rubro = None

cols = st.columns(3)

for i, r in enumerate(rubros):
    if cols[i % 3].button(r):
        st.session_state.rubro = r

# Mostrar selección
if st.session_state.rubro:
    st.success(f"Rubro seleccionado: {st.session_state.rubro}")
else:
    st.warning("Seleccioná un rubro")

# -------------------------
# FORMULARIO
# -------------------------
nombre = st.text_input("Nombre")
empresa = st.text_input("Empresa")
contacto = st.text_input("Teléfono o Email")

comentarios = st.text_area(
    "Comentarios (opcional)",
    placeholder="Ej: necesita cotización / llamar la semana que viene",
    height=80
)

# -------------------------
# GUARDAR
# -------------------------
if st.button("Guardar"):
    if st.session_state.rubro and nombre and contacto:
        nuevo = pd.DataFrame([{
            "Fecha": datetime.now(ZoneInfo("America/Montevideo")).strftime("%Y-%m-%d %H:%M"),),
            "Rubro": st.session_state.rubro,
            "Nombre": nombre,
            "Empresa": empresa,
            "Contacto": contacto,
            "Comentarios": comentarios
        }])

        nuevo.to_csv(FILE_NAME, mode='a', header=False, index=False)

        st.success("Contacto guardado ✅")

        # Resetear
        st.session_state.rubro = None
        st.rerun()
    else:
        st.error("Completá rubro, nombre y contacto")

# -------------------------
# DESCARGAR EXCEL
# -------------------------
st.divider()
st.subheader("Descargar datos")

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Contactos')

    buffer.seek(0)

    st.download_button(
        label="Descargar Excel",
        data=buffer,
        file_name="contactos_feria.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No hay datos aún")
