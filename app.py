import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# 2. ESTILOS CSS REFORZADOS
st.markdown("""
    <style>
    :root {
        --bg-box: rgba(128, 128, 128, 0.1);
        --border-color: rgba(128, 128, 128, 0.3);
    }
    h1 { text-align: center; margin-bottom: 10px; font-size: 28px; color: #FF8C00; }
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .info-box {
        background: var(--bg-box); 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid var(--border-color); 
        margin-top: 15px;
    }
    /* Clase para asegurar que los números se vean en cualquier modo */
    .num-visible {
        color: #F0F0F0 !important;
        text-shadow: 1px 1px 2px #000;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m", label_visibility="collapsed")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m", label_visibility="collapsed")

    t0_busqueda = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))
    t_fases, y_fases = almanac.find_discrete(t0_busqueda, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv, info_utc = "---", "---"
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_fases, y_fases):
        t_c = ti.astimezone(tz_sv)
        if yi == 0: 
            if t_c.month == mes_id:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
                info_utc = f"{ti.astimezone(pytz.utc).strftime('%H:%M')} (UTC)"
                fases_dict[t_c.day] = [0, t_c]
            d_sum = 1 if t_c.hour < 18 else 2
            f_celeb = t_c + timedelta(days=d_sum)
            if f_celeb.month == mes_id: fases_dict[f_celeb.day] = ["CELEB", None]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, t_c]

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td style='border:none;'></td>"
            else:
                icons, b_style = "", "border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; background: rgba(128,128,128,0.1);"
                if dia in fases_dict:
                    tipo = fases_dict[dia][0]
                    if tipo == "CELEB":
                        icons, b_style = "🌘", "border: 2px solid #FF8C00; background: rgba(255,140,0,0.15); border-radius: 12px;"
                    else: icons = iconos_fases.get(tipo, "")
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1); border-radius: 12px;"
                
                fila += f"""<td style='border:none; padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'>
                        <div class='num-visible' style='font-size:14px;'>{dia}</div>
                        <div style='text-align:center; font-size:26px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; font-size:22px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    components.html(f"""
    <div style='color:white; font-family:sans-serif;'>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
            {filas_html}
        </table>
    </div>""", height=480)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px;">Próxima Conjunción:</p>
        <p style="margin:0; font-size:15px;">📍 El Salvador: <b>{info_sv}</b></p>
        <p style="margin:0; font-size:14px; opacity:0.8;">🌍 Tiempo Universal: {info_utc}</p>
    </div>""", unsafe_allow_html=True)

with tab_anio:
    anio_full = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_f", label_visibility="collapsed")
    # Grid al 95% para evitar el "mordisco" derecho
    grid_html = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; width:95%; margin:auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, calendar.monthrange(anio_full, m)[1], 23, 59)))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        celebs = []
        for ti, yi in zip(t_f, y_f):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                fc = dt + timedelta(days=ds)
                if fc.month == m: celebs.append(fc.day)

        m_h = f"<div style='background:rgba(128,128,128,0.1); padding:8px; border-radius:10px; border:1px solid rgba(128,128,128,0.2);'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:14px;'>{meses_completos[m-1]}</div>"
        m_h += "<table style='width:100%; font-size:11px; text-align:center; border-collapse:collapse;'>"
        m_h += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    style = "color:#F0F0F0; font-weight:bold;"
                    if d in celebs: style += "border:1.5px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:4px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_full == hoy_sv.year: style += "border:1.5px solid #00FF7F; border-radius:4px;"
                    m_h += f"<td><div style='{style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_html += m_h + "</table></div>"
    components.html(grid_html + "</div>", height=1100)

# 4. PIE DE PÁGINA COMPLETO (NASA Y RESPALDO)
st.markdown("""
    <hr style="border:0.5px solid rgba(128,128,128,0.3); margin-top:30px;">
    <div style="text-align: center; padding-bottom: 40px;">
        <p style="color: grey; font-size: 13px; margin: 0;">
            <b>Respaldo Científico:</b> Los cálculos se generan en tiempo real utilizando Skyfield y efemérides de la NASA.
        </p>
        <p style="color: grey; font-size: 12px; margin: 5px 0 15px 0;">
            Efemérides NASA | Corregido para transiciones astronómicas exactas.
        </p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;">
            Voz de la Tórtola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
