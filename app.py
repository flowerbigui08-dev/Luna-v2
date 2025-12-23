import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)

if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month

st.markdown("<h1 style='text-align:center;'>🌙 Luna SV</h1>", unsafe_allow_html=True)

# Selector de Mes sencillo
meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
cols = st.columns(4)
for i, m in enumerate(meses):
    with cols[i % 4]:
        if st.button(m, key=f"m{i}"):
            st.session_state.m_id = i + 1
            st.rerun()

m_sel = st.session_state.m_id
anio = 2025

# Lógica
d_inicio = datetime(anio, m_sel, 1)
n_m = ephem.next_new_moon(d_inicio)
dt_nm = n_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)

# Calendario HTML
cal = calendar.Calendar(firstweekday=6)
filas = ""
for semana in cal.monthdayscalendar(anio, m_sel):
    fila = "<tr>"
    for d in semana:
        if d == 0: fila += "<td></td>"
        else:
            txt, estilo = "", "border: 1px solid #444;"
            if d == dt_nm.day and dt_nm.month == m_sel:
                txt = "🌑"
                # Marcamos celebración el día siguiente por defecto para esta prueba
                st.session_state.celeb = d + 1
            if 'celeb' in st.session_state and d == st.session_state.celeb:
                txt = "🌘"
                estilo = "border: 2px solid #FF8C00;"
            if d == hoy.day and m_sel == hoy.month:
                estilo = "border: 2px solid #00FF7F;"
            fila += f"<td style='{estilo} height:60px; vertical-align:top;'><b>{d}</b><br><center>{txt}</center></td>"
    filas += fila + "</tr>"

html = f"<table style='width:100%; border-collapse:collapse; color:white;'>{filas}</table>"
components.html(html, height=400)
st.write(f"🌑 Luna Nueva: {dt_nm.strftime('%d/%m %I:%M %p')}")
