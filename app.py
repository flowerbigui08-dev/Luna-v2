import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN E ID DE CAMBIO (Si no ves '2026', el código no se ha actualizado)
st.set_page_config(page_title="Luna SV 2026", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

# 2. TRUCO DE ESTILO DIRECTO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { text-align: center; color: #FF8C00 !important; font-size: 26px; }
    /* Forzamos el color amarillo en una clase específica */
    .num-dia { color: #FFD700 !important; font-weight: bold; font-size: 16px; text-shadow: 1px 1px 2px #000; }
    .box-info-v3 {
        background: rgba(255, 255, 255, 0.05); 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #FF8C00;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar SV 2026</h1>", unsafe_allow_html=True)

tab_m, tab_a = st.tabs(["📅 Mensual", "🗓️ Anual"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_m:
    c1, c2 = st.columns(2)
    with c1: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="y26")
    with c2: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="m26")

    # Cálculos con la regla de transición de meses
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases = {}
    prox = "---"
    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if yi == 0:
            if t_c.month == mes_id: 
                fases[t_c.day] = [0, "🌑"]
                prox = t_c.strftime('%d/%m/%y %I:%M %p')
            ds = 1 if t_c.hour < 18 else 2
            fc = t_c + timedelta(days=ds)
            if fc.month == mes_id: fases[fc.day] = ["C", "🌘"]
        elif t_c.month == mes_id:
            fases[t_c.day] = [yi, {1:"🌓", 2:"🌕", 3:"🌗"}[yi]]

    # Tabla con IDs de estilo únicos
    filas = ""
    for sem in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for d in sem:
            if d == 0: fila += "<td></td>"
            else:
                bg = "border:1px solid rgba(255,255,255,0.2); background:rgba(255,255,255,0.03);"
                ico = ""
                if d in fases:
                    tipo, dibujo = fases[d]
                    ico = dibujo
                    if tipo == "C": bg = "border:2px solid #FF8C00; background:rgba(255,140,0,0.15);"
                if d == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    bg = "border:2px solid #00FF7F; background:rgba(0,255,127,0.1);"

                fila += f"""<td style='padding:4px;'><div style='{bg} height:70px; border-radius:10px; padding:5px;'>
                    <div style='color:#FFD700 !important; font-weight:bold;'>{d}</div>
                    <div style='text-align:center; font-size:22px;'>{ico}</div>
                </div></td>"""
        filas += fila + "</tr>"

    components.html(f"""<table style='width:100%; table-layout:fixed; color:white; font-family:sans-serif; border-collapse:collapse;'>
        <tr style='color:#FF4B4B; text-align:center;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
        {filas}</table>""", height=450)
    
    st.markdown(f"<div class='box-info-v3'><b>Próxima Luna Nueva:</b> {prox}</div>", unsafe_allow_html=True)

with tab_a:
    anio_a = st.number_input("Seleccionar Año", 2024, 2030, hoy_sv.year, key="ya26")
    # Ajuste de ancho ultra-seguro (90%) para el mordisco
    grid = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; width:90%; margin:auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_a, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_a, m, calendar.monthrange(anio_a, m)[1], 23, 59)))
        t_fa, y_fa = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        cs = []
        for ti, yi in zip(t_fa, y_fa):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                fc = dt + timedelta(days=ds)
                if fc.month == m: cs.append(fc.day)
        
        m_h = f"<div style='background:rgba(255,255,255,0.05); padding:8px; border-radius:10px; border:1px solid rgba(255,255,255,0.1);'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:14px;'>{calendar.month_name[m]}</div>"
        m_h += "<table style='width:100%; font-size:11px; color:white;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_a, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    stil = "color:#FFD700 !important; font-weight:bold;"
                    if d in cs: stil += "border:1px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:4px;"
                    m_h += f"<td><div style='{stil}'>{d}</div></td>"
            m_h += "</tr>"
        m_h += "</table></div>"
        grid += m_h
    components.html(grid + "</div>", height=1000)

# 4. PIE DE PÁGINA (Respaldo NASA)
st.markdown("""
    <div style="text-align: center; border-top: 1px solid #333; margin-top: 20px; padding-top: 20px;">
        <p style="color: #888; font-size: 13px;"><b>Respaldo Científico:</b> Skyfield & NASA Ephemeris.</p>
        <p style="color: #888; font-size: 12px;">Corregido para transiciones astronómicas exactas.</p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; margin-top: 15px;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
