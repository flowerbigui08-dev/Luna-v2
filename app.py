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
    h1 { text-align: center; color: #FF8C00; }
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    
    /* Contenedor principal para evitar cortes laterales */
    .main-container {
        padding: 10px;
        max-width: 100%;
        overflow-x: hidden;
    }

    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    
    .info-box {
        background: rgba(128, 128, 128, 0.1); 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid rgba(128, 128, 128, 0.3);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="m1")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="m2")

    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
    info_sv = "---"

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if yi == 0:
            if t_c.month == mes_id: 
                fases_dict[t_c.day] = [0, "🌑"]
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
            d_sum = 1 if t_c.hour < 18 else 2
            f_celeb = t_c + timedelta(days=d_sum)
            if f_celeb.month == mes_id: fases_dict[f_celeb.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, iconos[yi]]

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td style='border:none;'></td>"
            else:
                b_style = "border: 1px solid rgba(128,128,128,0.4); border-radius: 12px; background: rgba(128,128,128,0.05);"
                content = ""
                if dia in fases_dict:
                    tipo, ico = fases_dict[dia]
                    content = ico
                    if tipo == "CELEB":
                        b_style = "border: 2px solid #FF8C00; background: rgba(255,140,0,0.15); border-radius: 12px;"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1); border-radius: 12px;"

                fila += f"""
                <td style='padding:5px; border:none;'>
                    <div style='{b_style} height:80px; padding:8px; box-sizing:border-box;'>
                        <div style='color:#FFD700 !important; font-weight:bold; font-size:16px;'>{dia}</div>
                        <div style='text-align:center; font-size:28px; margin-top:2px;'>{content}</div>
                    </div>
                </td>"""
        filas_html += fila + "</tr>"

    html_mensual = f"""
    <div style='max-width:98%; margin:auto; font-family:sans-serif;'>
        <h2 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_id-1]} {anio}</h2>
        <table style='width:100%; border-collapse:collapse; table-layout:fixed;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold; font-size:16px;'>
                <td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td>
            </tr>
            {filas_html}
        </table>
    </div>
    """
    components.html(html_mensual, height=550)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; font-size:18px; margin-bottom:10px;">Próxima Conjunción:</p>
        <p style="font-size:16px; margin:0;">📍 El Salvador: <b>{info_sv}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Año", 2024, 2030, hoy_sv.year, key="a1")
    # Grid con margen de seguridad (padding-right) para evitar el "mordisco"
    grid = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:15px; width:96%; margin:auto; padding-right:10px;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, calendar.monthrange(anio_f, m)[1], 23, 59)))
        t_fa, y_fa = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        celebs = []
        for ti, yi in zip(t_fa, y_fa):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                f_c = dt + timedelta(days=ds)
                if f_c.month == m: celebs.append(f_c.day)
        
        m_html = f"<div style='background:rgba(128,128,128,0.1); padding:10px; border-radius:12px; border:1px solid rgba(128,128,128,0.2);'>"
        m_html += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:8px;'>{meses_completos[m-1]}</div>"
        m_html += "<table style='width:100%; font-size:13px; text-align:center; color:white;'>"
        m_html += "<tr style='color:#FF4B4B; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_html += "<tr>"
            for d in sem:
                if d == 0: m_html += "<td></td>"
                else:
                    style = "color:#FFD700 !important; font-weight:bold; padding:4px;"
                    if d in celebs: style += "border:1.5px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:6px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style += "border:1.5px solid #00FF7F; border-radius:6px;"
                    m_html += f"<td><div style='{style}'>{d}</div></td>"
            m_html += "</tr>"
        m_html += "</table></div>"
        grid += m_html
    grid += "</div>"
    components.html(grid, height=1300)

# 3. PIE DE PÁGINA (Respaldo Científico completo)
st.markdown("""
    <hr style="border:0.5px solid rgba(128,128,128,0.3);">
    <div style="text-align: center; padding: 10px;">
        <p style="color: grey; font-size: 13px; margin-bottom: 5px;">
            <b>Respaldo Científico:</b> Los cálculos se generan en tiempo real utilizando Skyfield y efemérides de la NASA.
        </p>
        <p style="color: grey; font-size: 12px; margin-bottom: 15px;">
            Efemérides NASA | Corregido para transiciones.
        </p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;">
            Voz de la Tórtola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
