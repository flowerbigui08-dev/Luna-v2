import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS PARA MODO CLARO/OSCURO Y BLOQUEO DE TECLADO
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    
    /* Centrar selectores y evitar que el teclado salte al tocarlos */
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    input { 
        pointer-events: none !important; 
        caret-color: transparent !important;
        text-align: center !important; 
        font-weight: bold !important; 
    }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    
    /* Cuadros de información con fondo oscuro fijo */
    .info-box {
        background: #1a1c23; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        margin-top: 15px;
        color: white;
    }
    .info-line { color: white; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-size { font-size: 22px; margin-right: 15px; width: 30px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

# Carga de datos astronómicos una sola vez
ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a:
        anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m:
        mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")

    # CÁLCULOS
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))

    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    info_sv, info_utc = "---", "---"
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: 
                fila += "<td></td>"
            else:
                icons = ""
                # FONDO OSCURO FIJO PARA CADA CUADRITO
                b_style = "border: 1px solid #333; background: #1a1c23; border-radius: 10px; color: white;"
                
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0:
                        t_conj = fases_dict[dia][1]
                        info_sv = f"{dias_esp[t_conj.weekday()]} {t_conj.strftime('%d/%m/%y %I:%M %p')}"
                        t_u = t_conj.astimezone(pytz.utc)
                        info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%d/%m/%y %H:%M')}"
                        target = dia + 1 if t_conj.hour < 18 else dia + 2
                        if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a; border-radius: 10px; color: white;"
                elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                    icons += "🌘"
                    b_style = "border: 2px solid #FF8C00; background: #2c1a0a; border-radius: 10px; color: white;"
                
                fila += f"""<td style='padding:4px;'><div style='{b_style} height: 70px; padding: 6px; box-sizing: border-box;'>
                        <div style='font-weight:bold; font-size:13px;'>{dia}</div>
                        <div style='font-size:24px; text-align:center; margin-top:2px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:15px; font-size:22px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    
    components.html(f"""
    <style>
        table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; table-layout: fixed; }}
        th {{ color: #FF4B4B; padding-bottom: 5px; text-align: center; font-weight: bold; font-size: 14px; }}
    </style>
    <table>
        <tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
        {filas_html}
    </table>
    """, height=440)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:17px;">Próxima Conjunción:</p>
        <p style="color:#aaa; font-size:14px; margin:0;">📍 El Salvador (SV):</p>
        <p style="font-size:16px; font-weight:bold; margin-bottom:10px;">{info_sv}</p>
        <p style="color:#aaa; font-size:14px; margin:0;">🌍 Tiempo Universal (UTC):</p>
        <p style="font-size:16px; font-weight:bold;">{info_utc}</p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_full = st.number_input("Año Completo", 2024, 2030, hoy_sv.year, key="anio_f")
    
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, 1)))
        ultimo_a = calendar.monthrange(anio_full, m)[1]
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, ultimo_a, 23, 59)))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        
        celebs = []
        for ti, yi in zip(t_f, y_f):
            if yi == 0: 
                dt = ti.astimezone(tz_sv)
                target = dt.day + 1 if dt.hour < 18 else dt.day + 2
                if target <= ultimo_a: celebs.append(target)

        mes_html = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333; color:white;'>"
        mes_html += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        mes_html += "<table style='width:100%; font-size:11px; text-align:center; border-collapse:collapse;'>"
        mes_html += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        
        for semana in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for dia in semana:
                if dia == 0: mes_html += "<td></td>"
                else:
                    estilo = "padding: 2px;"
                    if dia in celebs: estilo += "border: 1px solid #FF8C00; background: rgba(255,140,0,0.2); border-radius: 4px;"
                    if dia == hoy_sv.day and m == hoy_sv.month and anio_full == hoy_sv.year:
                        estilo += "border: 1px solid #00FF7F; background: rgba(0,255,127,0.2); border-radius: 4px;"
                    mes_html += f"<td><div style='{estilo}'>{dia}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    
    components.html(grid_html + "</div>", height=1000)

# PIE DE PÁGINA
st.markdown("""
    <div style="margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center;">
        <p style="color: #888; font-size: 16px; font-weight: bold; font-style: italic;">
            Voz de la Tórtola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
