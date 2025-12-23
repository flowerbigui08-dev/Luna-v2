import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

# Configuración de pantalla
st.set_page_config(page_title="Luna SV", layout="wide")

# ESTILO OSCURO PROFESIONAL (Basado en tus fotos)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { text-align: center; color: white; font-size: 26px; margin-bottom: 0px; }
    .orange-text { color: #FF8C00; text-align: center; font-weight: bold; margin: 5px 0; }
    
    /* Botones en horizontal para celular */
    div.stButton > button {
        width: 100%;
        background-color: #1a1a1a !important;
        color: #ccc !important;
        border: 1px solid #333 !important;
        padding: 5px 2px !important;
        font-size: 13px !important;
    }
    
    /* Calendario */
    .cal-table { width: 100%; border-collapse: collapse; color: white; }
    .cal-table td { border: 1px solid #333; height: 65px; vertical-align: top; padding: 4px; width: 14%; }
    .dia-num { font-weight: bold; font-size: 14px; }
    .luna-icon { text-align: center; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# Lógica de tiempo
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)
if 'm_id' not in st.session_state: st.session_state.m_id = hoy.month

# Selector de Año
st.markdown("<p class='orange-text'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=2025, label_visibility="collapsed")

# Selector de Mes (4 columnas para que quepan en el cel)
st.markdown("<p class='orange-text'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
cols = st.columns(4)
for i, m in enumerate(meses_n):
    with cols[i % 4]:
        if st.button(m, key=f"m{i}"):
            st.session_state.m_id = i + 1
            st.rerun()

m_sel = st.session_state.m_id
nombres_largos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin:10px 0;'>{nombres_largos[m_sel-1]} {anio}</h2>", unsafe_allow_html=True)

# Cálculo de Luna
d_inicio = datetime(anio, m_sel, 1)
nm = ephem.next_new_moon(d_inicio).datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
fm = ephem.next_full_moon(d_inicio).datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)

# Calendario HTML
cal = calendar.Calendar(firstweekday=6)
filas = ""
for semana in cal.monthdayscalendar(anio, m_sel):
    fila = "<tr>"
    for d in semana:
        if d == 0: fila += "<td></td>"
        else:
            txt, estilo = "", ""
            # Luna Nueva
            if d == nm.day and m_sel == nm.month:
                txt = "🌑"
                celeb = d + 1 if nm.hour < 18 else d + 2
                st.session_state.c = celeb
            # Luna Llena
            if d == fm.day and m_sel == fm.month: txt = "🌕"
            # Día actual
            if d == hoy.day and m_sel == hoy.month and anio == hoy.year:
                estilo = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"
            # Celebración
            elif 'c' in st.session_state and d == st.session_state.c:
                txt = "🌘"; estilo = "border: 2px solid #FF8C00;"
            
            fila += f"<td style='{estilo}'><span class='dia-num'>{d}</span><div class='luna-icon'>{txt}</div></td>"
    filas += fila + "</tr>"

st.markdown(f"<table class='cal-table'><tr style='color:#FF4B4B;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table>", unsafe_allow_html=True)

# SIMBOLOGÍA (Exactamente como tu foto)
st.markdown(f"""
<div style="background:#1a1a1a; padding:15px; border-radius:12px; border:1px solid #333; margin-top:20px;">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px;">Simbología:</p>
    <p style="color:white; font-size:14px;"><span style="color:#00FF7F;">□</span> Día Actual (Hoy)</p>
    <p style="color:white; font-size:14px;">🌑 Luna Nueva</p>
    <p style="color:white; font-size:14px;">🌘 Día de Celebración</p>
    <p style="color:white; font-size:14px;">🌕 Luna Llena</p>
</div>
""", unsafe_allow_html=True)
