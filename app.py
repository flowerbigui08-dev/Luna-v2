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

# 2. ESTILOS CSS REFORZADOS (Para que se vea bien en el cel)
st.markdown("""
    <style>
    /* Evita que se corte a los lados en pantallas pequeñas */
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 1rem !important;
    }
    
    h1 { text-align: center; color: #FF8C00; font-size: 24px; }
    
    .box-info-v2 {
        background: rgba(255, 255, 255, 0.05); 
        padding: 12px; 
        border-radius: 10px; 
        border: 1px solid rgba(255, 140, 0, 0.3);
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="y_mes")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="m_mes")

    # Cálculos
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_data = {}
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
    prox_conj = "---"

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if yi == 0:
            if t_c.month == mes_id: 
                fases_data[t_c.day] = [0, "🌑"]
                prox_conj = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
            d_sum = 1 if t_c.hour < 18 else 2
            f_celeb = t_c + timedelta(days=d_sum)
            if f_celeb.month == mes_id: fases_data[f_celeb.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_data[t_c.day] = [yi, iconos[yi]]

    # Tabla Mensual
    filas = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td style='border:none;'></td>"
            else:
                # Fondo y borde dinámico
                estilo_celda = "border: 1px solid rgba(128,128,128,0.3); border-radius: 8px; background: rgba(128,128,128,0.1);"
                dibujo = ""
                if dia in fases_data:
                    tipo, ico = fases_data[dia]
                    dibujo = ico
                    if tipo == "CELEB": estilo_celda = "border: 2px solid #FF8C00; background: rgba(255,140,0,0.1); border-radius: 8px;"
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    estilo_celda = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1); border-radius: 8px;"

                fila += f"""
                <td style='padding:3px; border:none;'>
                    <div style='{estilo_celda} height:70px; padding:5px; box-sizing:border-box;'>
                        <div style='color:#FFD700 !important; font-weight:bold; font-size:15px; text-shadow: 1px 1px 1px black;'>{dia}</div>
                        <div style='text-align:center; font-size:22px;'>{dibujo}</div>
                    </div>
                </td>"""
        filas += fila + "</tr>"

    html_m = f"""
    <div style='width:100%; font-family:sans-serif;'>
        <h3 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_id-1]} {anio}</h3>
        <table style='width:100%; border-collapse:separate; border-spacing:2px; table-layout:fixed;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold; font-size:14px;'>
                <td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td>
            </tr>
            {filas}
        </table>
    </div>
    """
    components.html(html_m, height=480)
    st.markdown(f"<div class='box-info-v2'><b>Próxima Conjunción:</b><br>📍 El Salvador: {prox_conj}</div>", unsafe_allow_html=True)

with tab_anio:
    anio_a = st.number_input("Año Seleccionado", 2024, 2030, hoy_sv.year, key="y_anio")
    # Reducción de ancho al 92% para asegurar que no haya "mordisco" en el cel
    grid_html = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; width:92%; margin:0 auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_a, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_a, m, calendar.monthrange(anio_a, m)[1], 23, 59)))
        t_fa, y_fa = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        dias_c = []
        for ti, yi in zip(t_fa, y_fa):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                fc = dt + timedelta(days=ds)
                if fc.month == m: dias_c.append(fc.day)
        
        m_html = f"<div style='background:rgba(255,255,255,0.05); padding:8px; border-radius:10px; border:1px solid rgba(128,128,128,0.2);'>"
        m_html += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:14px; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        m_html += "<table style='width:100%; font-size:11px; text-align:center;'>"
        m_html += "<tr style='color:#FF4B4B; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_a, m):
            m_html += "<tr>"
            for d in sem:
                if d == 0: m_html += "<td></td>"
                else:
                    s_d = "color:#FFD700 !important; font-weight:bold; text-shadow: 1px 1px 1px black;"
                    if d in dias_c: s_d += "border:1px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:4px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_a == hoy_sv.year: s_d += "border:1px solid #00FF7F; border-radius:4px;"
                    m_html += f"<td><div style='{s_d}'>{d}</div></td>"
            m_html += "</tr>"
        m_html += "</table></div>"
        grid_html += m_html
    grid_html += "</div>"
    components.html(grid_html, height=1100)

# 3. RESPALDO CIENTÍFICO Y PIE DE PÁGINA
st.markdown("""
    <hr style="border:0.1px solid rgba(128,128,128,0.2); margin-top:30px;">
    <div style="text-align: center;">
        <p style="color: #888; font-size: 13px; margin: 0;">
            <b>Respaldo Científico:</b> Cálculos generados con Skyfield y efemérides NASA.
        </p>
        <p style="color: #888; font-size: 12px; margin: 5px 0 15px 0;">
            Corregido para transiciones astronómicas exactas.
        </p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;">
            Voz de la Tórtola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
