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

# 2. ESTILOS CSS CON COLORES FIJOS (Independiente del sistema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { text-align: center; color: #FF8C00; font-size: 26px; margin-bottom: 5px; }
    
    /* Cuadros de información con fondo gris oscuro fijo */
    .info-box-fijo {
        background: #1a1c23; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        margin-top: 15px;
        color: white;
    }
    .info-line { color: white; font-size: 15px; margin-bottom: 8px; display: flex; align-items: center; }
    .emoji-size { font-size: 20px; margin-right: 12px; width: 25px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="y_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="m_m")

    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv = "---"
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if yi == 0: 
            if t_c.month == mes_id:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
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
                ico, b_style = "", "border: 1px solid #333; background: #1a1c23;"
                n_color = "#FFD700" # Amarillo oro para números
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    ico = dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: rgba(255,140,0,0.15);"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"

                fila += f"""<td style='padding:4px;'><div style='{b_style} height:72px; border-radius:10px; padding:6px; box-sizing:border-box;'>
                        <div style='color:{n_color}; font-weight:bold; font-size:14px;'>{dia}</div>
                        <div style='text-align:center; font-size:24px; margin-top:2px;'>{ico}</div></div></td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
    <div style='font-family:sans-serif;'>
        <h3 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_id-1]} {anio}</h3>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse; color:white;'>
            <tr style='color:#FF4B4B; text-align:center;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
            {filas_html}
        </table>
    </div>""", height=460)

    # 3. CUADROS DE SIMBOLOGÍA Y PRÓXIMA CONJUNCIÓN (Restaurados)
    st.markdown(f"""
    <div class="info-box-fijo">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:17px;">Simbología:</p>
        <div class="info-line"><span class="emoji-size">✅</span> Hoy (Día actual)</div>
        <div class="info-line"><span class="emoji-size">🌑</span> Conjunción (Luna Nueva)</div>
        <div class="info-line"><span class="emoji-size">🌘</span> Día de Celebración</div>
        <div class="info-line"><span class="emoji-size">🌕</span> Luna Llena</div>
    </div>
    <div class="info-box-fijo">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:8px; font-size:17px;">Próxima Conjunción:</p>
        <p style="margin:0; font-size:15px; color:white;">📍 El Salvador: <b>{info_sv}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Año", 2024, 2030, hoy_sv.year, key="a_f", label_visibility="collapsed")
    # Grid con más espacio y altura (1fr 1fr)
    grid_h = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:12px; width:94%; margin:auto;'>"
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

        m_h = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333;'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:15px; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        m_h += "<table style='width:100%; font-size:12px; text-align:center; color:white;'>"
        m_h += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    style = "color:#FFD700; font-weight:bold;"
                    if d in cs: style += "border:1.5px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:4px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style += "border:1.5px solid #00FF7F; border-radius:4px;"
                    m_h += f"<td><div style='padding:2px; {style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_h += m_h + "</table></div>"
    components.html(grid_h + "</div>", height=1250)

# 4. PIE DE PÁGINA (Respaldo NASA)
st.markdown("""
    <hr style="border:0.1px solid #333; margin-top:30px;">
    <div style="text-align: center; padding-bottom: 20px;">
        <p style="color: #888; font-size: 13px; margin: 0;">
            <b>Respaldo Científico:</b> Cálculos generados en tiempo real utilizando Skyfield y efemérides de la NASA.
        </p>
        <p style="color: #888; font-size: 12px; margin: 5px 0 15px 0;">
            Efemérides NASA | Corregido para transiciones astronómicas exactas.
        </p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;">
            Voz de la Tórtola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
