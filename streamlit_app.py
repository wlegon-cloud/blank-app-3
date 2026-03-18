import streamlit as st
from datetime import datetime
from config import PRODUCTOS, CAMPOS_OBLIGATORIOS
from sheets import get_sheet, ensure_headers, append_lead, check_duplicate

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Registro de Leads",
    page_icon="🎯",
    layout="centered",
)

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0f0f0f; color: #f0ece4; }

.hero {
    background: linear-gradient(135deg, #1a1a1a, #111);
    border: 1px solid #272727;
    border-radius: 14px;
    padding: 2rem 2rem 1.6rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '🎯';
    position: absolute;
    right: 1.5rem; top: 1.2rem;
    font-size: 2.8rem;
    opacity: 0.15;
}
.hero-tag {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #e8c547;
    margin-bottom: 0.4rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f0ece4;
    margin: 0 0 0.3rem;
    line-height: 1.1;
}
.hero-sub { font-size: 0.85rem; color: #555; font-weight: 300; margin: 0; }

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #e8c547;
    margin: 1.6rem 0 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #222;
}

.stTextInput input, .stTextArea textarea {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #e8c547 !important;
    box-shadow: 0 0 0 2px rgba(232,197,71,0.1) !important;
}
.stMultiSelect > div > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}

.stButton > button[kind="primary"] {
    background: #e8c547 !important;
    color: #0f0f0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #888 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
}

.stRadio label { color: #ccc !important; font-size: 0.9rem !important; }

.counter {
    display: inline-block;
    background: #1a1a1a;
    border: 1px solid #272727;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: #666;
    margin-bottom: 1.2rem;
}
.counter span { color: #e8c547; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "leads_session" not in st.session_state:
    st.session_state.leads_session = 0
if "pending_lead" not in st.session_state:
    st.session_state.pending_lead = None
if "success_msg" not in st.session_state:
    st.session_state.success_msg = False


# ── Conexión Sheets ───────────────────────────────────────────────────────────
sheet = get_sheet()
ensure_headers(sheet)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">Stand · Registro</div>
    <div class="hero-title">Registro de Leads</div>
    <p class="hero-sub">Completá los datos del contacto y guardá en Google Sheets</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.leads_session > 0:
    st.markdown(
        f'<div class="counter">Leads cargados esta sesión: '
        f'<span>{st.session_state.leads_session}</span></div>',
        unsafe_allow_html=True,
    )


# ── Mensaje de éxito ──────────────────────────────────────────────────────────
if st.session_state.success_msg:
    st.success("✅ Lead guardado correctamente en Google Sheets.")
    st.session_state.success_msg = False


# ── Confirmación de duplicado ─────────────────────────────────────────────────
if st.session_state.pending_lead is not None:
    datos = st.session_state.pending_lead["datos"]
    dup = st.session_state.pending_lead["duplicado"]

    st.warning(
        f"⚠️ **Posible duplicado detectado**\n\n"
        f"Ya existe un contacto con este email o teléfono:\n\n"
        f"**{dup.get('Nombre', '—')}** · {dup.get('Empresa', '—')} "
        f"· Cargado el {dup.get('Fecha', '—')} a las {dup.get('Hora', '—')}\n\n"
        f"¿Querés guardarlo igual?"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Guardar igual", type="primary"):
            append_lead(sheet, datos)
            st.session_state.leads_session += 1
            st.session_state.pending_lead = None
            st.session_state.form_key += 1
            st.session_state.success_msg = True
            st.rerun()
    with col2:
        if st.button("❌ Cancelar", type="secondary"):
            st.session_state.pending_lead = None
            st.rerun()

    st.stop()


# ── Formulario ────────────────────────────────────────────────────────────────
fk = st.session_state.form_key  # sube con cada lead guardado → resetea campos

st.markdown('<div class="section-title">Datos del contacto</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre *", key=f"nombre_{fk}", placeholder="Juan Pérez")
with col2:
    empresa = st.text_input("Empresa *", key=f"empresa_{fk}", placeholder="Acme S.A.")

col3, col4 = st.columns(2)
with col3:
    cargo = st.text_input("Cargo", key=f"cargo_{fk}", placeholder="Gerente Comercial")
with col4:
    telefono = st.text_input("Teléfono", key=f"telefono_{fk}", placeholder="+598 99 000 000")

email = st.text_input("Email", key=f"email_{fk}", placeholder="juan@empresa.com")

st.markdown('<div class="section-title">Interés comercial</div>', unsafe_allow_html=True)

productos = st.multiselect(
    "Productos de interés",
    options=PRODUCTOS,
    key=f"productos_{fk}",
)

nivel = st.radio(
    "Nivel de interés",
    options=["🔥 Caliente", "🌡️ Tibio", "❄️ Frío"],
    index=1,
    horizontal=True,
    key=f"nivel_{fk}",
)

st.markdown('<div class="section-title">Notas</div>', unsafe_allow_html=True)

notas = st.text_area(
    "Comentarios adicionales",
    key=f"notas_{fk}",
    placeholder="Ej: muy interesado en pricing, vuelve la semana que viene...",
    height=100,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Guardar ───────────────────────────────────────────────────────────────────
if st.button("💾 Guardar lead", type="primary"):

    errores = []
    if not nombre.strip():
        errores.append("**Nombre** es obligatorio.")
    if not empresa.strip():
        errores.append("**Empresa** es obligatoria.")

    if errores:
        for e in errores:
            st.error(f"⚠️ {e}")
    else:
        now = datetime.now()
        row = [
            now.strftime("%d/%m/%Y"),
            now.strftime("%H:%M"),
            nombre.strip(),
            empresa.strip(),
            cargo.strip(),
            telefono.strip(),
            email.strip().lower(),
            ", ".join(productos) if productos else "",
            nivel,
            notas.strip(),
        ]

        duplicado = check_duplicate(sheet, email.strip(), telefono.strip())

        if duplicado:
            st.session_state.pending_lead = {"datos": row, "duplicado": duplicado}
            st.rerun()
        else:
            append_lead(sheet, row)
            st.session_state.leads_session += 1
            st.session_state.form_key += 1
            st.session_state.success_msg = True
            st.rerun()
