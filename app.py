import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import calendar
import ephem

# 1. CONFIGURACIÓN Y ESTILO OSCURO
st.set_page_config(page_title="Calendario Lunar SV", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro general */
    .main { background-color: #0e1117; }
    
    /* Título y etiquetas en naranja */
    h1 { text-align: center; color: #FF8C00; font-size: 28px !important; margin-bottom: 0px; }
    .label-naranja { color: #FF8C00; text-align: center; font-weight: bold; font-size: 20px; margin-top: 10px; }
    
    /* Botones de meses pequeños para que quepan en el celular */
    div.stButton > button {
        width: 100%;
        padding: 5px 2px !important;
        background-color: #262730 !important;
        color: #eee !important;
        border: 1px solid #444 !important;
        font-size: 14px !important;
        border-radius: 8px;
    }
    div.stButton > button:hover { border-color: #FF8C00 !important; color: #FF8C00 !important; }
    
    /* Ajuste del selector de año */
    div[data-testid="stNumberInput"] label { display: none; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    
    /* Estilo de la tabla del calendario */
    .cal-table { width: 100%; border-collapse: collapse; color: white; background: #1a1a1a; }
    .cal-table th { color: #FF4B4B; padding: 10px 0; font-size: 16px; }
    .cal-table td { border: 1px solid #333; height: 75px; vertical-align: top; padding: 5px; width: 14.2%; }
    .dia-n { font-size: 16px; font-weight: bold; }
    .luna-img { text-align: center; font-size: 28px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE TIEMPO
tz_sv = pytz.timezone('America/El_Salvador')
hoy = datetime.now(tz_sv)

if 'm_id' not in st.session_state:
    st.session_state.m_id = hoy.month

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 3. SELECTORES (Año y Mes)
st.markdown("<p class='label-naranja'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("", min_value=2024, max_value=2030, value=2025)

st.markdown("<p class='label-naranja'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_f = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Usamos 4 columnas para que quepan 3 meses por fila en el celular
cols = st.columns(4)
for i, m in enumerate(meses_n):
    with cols[i % 4]:
        if st.button(m, key=f"m{i}"):
            st.session_state.m_id = i + 1
            st.rerun()

m_sel = st.session_state.m_id

# 4. CÁLCULO LUNAR
d_inicio = datetime(anio, m_sel, 1)
n_m = ephem.next_new_moon(d_inicio)
dt_nm = n_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)
f_m = ephem.next_full_moon(d_inicio)
dt_fm = f_m.datetime().replace(tzinfo=pytz.utc).astimezone(tz_sv)

# 5. CONSTRUCCIÓN DEL CALENDARIO
st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>{meses_f[m_sel-1]} {anio}</h2>", unsafe_allow_html=True)

filas_html = ""
for semana in calendar.Calendar(firstweekday=6).monthdayscalendar(anio, m_sel):
    fila = "<tr>"
    for d in semana:
        if d == 0:
            fila += "<td></td>"
        else:
            txt, b_s = "", ""
            # Luna Nueva
            if d == dt_nm.day and dt_nm.month == m_sel:
                txt = "🌑"
                # Día de celebración
                c_d = d + 1 if dt_nm.hour < 18 else d + 2
                st.session_state.c_d = c_d
            
            # Luna Llena
            if d == dt_fm.day and dt_fm.month == m_sel:
                txt = "🌕"

            # Bordes especiales
            if d == hoy.day and m_sel == hoy.month and anio == hoy.year:
                b_s = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"
            elif 'c_d' in st.session_state and d == st.session_state.c_d:
                txt = "🌘"
                b_s = "border: 2px solid #FF8C00;"

            fila += f"<td style='{b_s}'><div class='dia-n'>{d}</div><div class='luna-img'>{txt}</div></td>"
    filas_html += fila + "</tr>"

html_tabla = f"""
<table class='cal-table'>
    <tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
    {filas_html}
</table>
"""
components.html(html_tabla, height=480)

# 6. SIMBOLOGÍA (Igual a tus fotos)
st.markdown(f"""
<div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-top:10px;">
    <p style="color:#FF8C00; font-weight:bold; font-size:20px; margin-bottom:10px;">Simbología:</p>
    <p style="color:white; margin:5px 0;"><span style="color:#00FF7F; font-size:20px;">□</span> Día Actual (Hoy)</p>
    <p style="color:white; margin:5px 0;">🌑 Luna Nueva</p>
    <p style="color:white; margin:5px 0;">🌘 Día de Celebración</p>
    <p style="color:white; margin:5px 0;">🌕 Luna Llena</p>
    <hr style="border:0.5px solid #333;">
    <p style="color:#aaa; font-size:14px;">Próxima Luna Nueva (SV):<br><b>{dt_nm.strftime('%d/%m/%Y %I:%M %p')}</b></p>
</div>
""", unsafe_allow_html=True)
