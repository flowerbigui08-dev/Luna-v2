import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# 2. ESTILOS CSS (Limpios para no saturar)
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; font-size: 28px; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    .info-box-final {
        padding: 15px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.3); 
        margin-top: 15px; background: rgba(128,128,128,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    c1, c2 = st.columns(2)
    with c1: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="y_fix")
    with c2: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="m_fix")

    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv, info_utc = "---", "---"
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        t_u = ti.astimezone(pytz.utc)
        if yi == 0: 
            if t_c.month == mes_id:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
                info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%d/%m/%y %H:%M')}"
                fases_dict[t_c.day] = [0, "🌑"]
            ds = 1 if t_c.hour < 18 else 2
            fc = t_c + timedelta(days=ds)
            if fc.month == mes_id: fases_dict[fc.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, iconos[yi]]

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                ico, b_style = "", "border: 1px solid #444; background: #1a1c23;"
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    ico = dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a;"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"

                # NÚMEROS GRANDES (22px) FORZADOS AQUÍ
                fila += f"""<td style='padding:4px;'><div style='{b_style} height:80px; border-radius:12px; padding:6px; box-sizing:border-box;'>
                        <div style='color:white; font-weight:bold; font-size:22px !important;'>{dia}</div>
                        <div style='text-align:center; font-size:28px;'>{ico}</div></div></td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
    <div style='font-family:sans-serif;'>
        <h3 style='text-align:center; color:#FF8C00; font-size:22px;'>{meses_completos[mes_id-1]} {anio}</h3>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold; font-size:16px;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>
            {filas_html}
        </table>
    </div>""", height=520)

    # 3. INFORMACIÓN DEBAJO DEL CALENDARIO
    st.markdown(f"""
    <div class="info-box-final">
        <p style="color:#FF8C00; font-weight:bold; font-size:17px; margin-bottom:10px;">Simbología:</p>
        <p style="margin:5px 0;">✅ Hoy | 🌑 Conjunción | 🌘 Celebración | 🌕 Luna Llena</p>
    </div>
    <div class="info-box-final">
        <p style="color:#FF8C00; font-weight:bold; font-size:17px; margin-bottom:8px;">Próxima Conjunción:</p>
        <p style="margin:0; font-size:16px;">📍 El Salvador: <b>{info_sv}</b></p>
        <p style="margin:5px 0 0 0; font-size:15px; opacity:0.8;">🌍 Tiempo UTC: <b>{info_utc}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Año", 2024, 2030, hoy_sv.year, key="a_fix", label_visibility="collapsed")
    # ANCHO 95% Y MARGEN PARA EVITAR MORDISCO
    grid_h = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; width:95%; margin:auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, calendar.monthrange(anio_f, m)[1], 23, 59)))
        t_fa, y_fa = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        cs = []
        for ti, yi in zip(t_fa, y_fa):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                fc = dt + timedelta(days=ds)
                if fc.month == m: cs.append(fc.day)

        m_h = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #444;'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:16px; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        m_h += "<table style='width:100%; font-size:18px !important; text-align:center; color:white; border-collapse:collapse;'>"
        m_h += "<tr style='color:#FF4B4B; font-weight:bold; font-size:14px;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    # NÚMEROS GRANDES (18px) EN ANUAL
                    style = "color:white; font-weight:bold; font-size:18px !important;"
                    if d in cs: style += "border:1.5px solid #FF8C00; background:rgba(255,140,0,0.25); border-radius:5px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style += "border:2px solid #00FF7F; border-radius:5px;"
                    m_h += f"<td><div style='padding:3px; {style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_h += m_h + "</table></div>"
    components.html(grid_h + "</div>", height=1400)

# 4. PIE DE PÁGINA
st.markdown("""
    <hr style="border:0.1px solid rgba(128,128,128,0.2); margin-top:20px;">
    <div style="text-align: center; padding-bottom: 20px;">
        <p style="color: grey; font-size: 13px;">Respaldo Científico: Skyfield & NASA Ephemeris.</p>
        <p style="color: #FF8C00; font-size: 20px; font-weight: bold; font-style: italic;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
