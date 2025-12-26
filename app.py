import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { text-align: center; color: white; margin-bottom: 0px; font-size: 28px; }
    .label-naranja { color: #FF8C00; text-align: center; font-weight: bold; font-size: 20px; margin-top: 15px; }
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    input { font-size: 22px !important; text-align: center !important; font-weight: bold !important; }
    
    /* Estilo para las pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1a1a1a; 
        border-radius: 8px; 
        color: white; 
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #FF8C00 !important; color: black !important; font-weight: bold; }

    .info-box {
        background: #1a1a1a; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        margin-top: 15px;
    }
    .info-line { color: white; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-size { font-size: 22px; margin-right: 15px; width: 30px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 2. SELECTORES Y PESTAÑAS
tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

with tab_mes:
    anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy_sv.year, key="anio_m", label_visibility="collapsed")
    mes_id = st.number_input("Mes", min_value=1, max_value=12, value=hoy_sv.month, key="mes_m", label_visibility="collapsed")

    # CÁLCULOS MENSUALES
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))

    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    t_seasons, y_seasons = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    seasons_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_seasons, y_seasons)}

    info_sv, info_utc = "---", "---"
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    filas_html = ""
    cal = calendar.Calendar(firstweekday=6)

    for semana in cal.monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: 
                fila += "<td style='border:none;'></td>"
            else:
                icons = ""
                b_style = "border: 1px solid #333; border-radius: 12px;"
                if mes_id == 3 and dia in seasons_dict and seasons_dict[dia] == 0:
                    icons += "🌸"
                if dia in fases_dict:
                    f_tipo = fases_dict[dia][0]
                    if f_tipo != "CELEB":
                        icons += iconos_fases.get(f_tipo, "")
                        if f_tipo == 0:
                            t_conj = fases_dict[dia][1]
                            info_sv = f"{dias_esp[t_conj.weekday()]} {t_conj.strftime('%d/%m/%y %I:%M %p')}"
                            t_u = t_conj.astimezone(pytz.utc)
                            info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%d/%m/%y %H:%M')}"
                            target = dia + 1 if t_conj.hour < 18 else dia + 2
                            if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 1.5px solid #00FF7F; background: rgba(0,255,127,0.08); border-radius: 12px;"
                elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                    icons += "🌘"
                    b_style = "border: 1.5px solid #FF8C00; background: rgba(255,140,0,0.05); border-radius: 12px;"
                
                fila += f"""<td style='border:none; padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'>
                        <div style='font-weight:bold; font-size:13px; color:#ccc;'>{dia}</div>
                        <div style='font-size:26px; text-align:center; margin-top:2px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:20px; font-size:24px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    html_tabla = f"<table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>"
    components.html(f"<style>table {{ width: 100%; border-collapse: separate; border-spacing: 0px; color: white; font-family: sans-serif; table-layout: fixed; }} th {{ color: #FF4B4B; padding-bottom: 8px; font-size: 15px; text-align: center; font-weight: bold; }}</style>{html_tabla}", height=500)

with tab_anio:
    anio_full = st.number_input("Seleccionar Año", min_value=2024, max_value=2030, value=hoy_sv.year, key="anio_f", label_visibility="collapsed")
    
    # Generar cuadrícula de 12 meses (3 columnas x 4 filas)
    col1, col2 = st.columns(2) # En móvil es mejor 2 columnas o 1
    
    ts = api.load.timescale()
    eph = api.load('de421.bsp')

    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>"
    
    for m in range(1, 13):
        # Calcular conjunciones del mes para marcar celebraciones
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, 1)))
        ultimo_a = calendar.monthrange(anio_full, m)[1]
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, ultimo_a, 23, 59)))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        
        # Guardar días de celebración (día después de Luna Nueva)
        celebraciones = []
        for ti, yi in zip(t_f, y_f):
            if yi == 0: # Luna Nueva
                dt = ti.astimezone(tz_sv)
                target = dt.day + 1 if dt.hour < 18 else dt.day + 2
                if target <= ultimo_a: celebraciones.append(target)

        # Crear HTML de cada mes chiquito
        mes_html = f"<div style='background:#1a1a1a; padding:8px; border-radius:8px; border:1px solid #333;'>"
        mes_html += f"<div style='color:#FF8C00; font-weight:bold; font-size:14px; text-align:center; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        mes_html += "<table style='width:100%; font-size:10px; text-align:center; color:white; border-collapse:collapse;'>"
        mes_html += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        
        for semana in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for dia in semana:
                if dia == 0:
                    mes_html += "<td></td>"
                else:
                    style = ""
                    if dia in celebraciones:
                        style = "border: 1px solid #FF8C00; background: rgba(255,140,0,0.2); border-radius: 3px;"
                    if dia == hoy_sv.day and m == hoy_sv.month and anio_full == hoy_sv.year:
                        style = "border: 1px solid #00FF7F; background: rgba(0,255,127,0.2); border-radius: 3px;"
                    
                    mes_html += f"<td style='padding:2px;'><div style='{style}'>{dia}</div></td>"
            mes_html += "</tr>"
        mes_html += "</table></div>"
        grid_html += mes_html
    
    grid_html += "</div>"
    components.html(f"<style>body{{background:#0e1117;}}</style>{grid_html}", height=800)

# 5. LEYENDA Y DATOS (Se muestran siempre abajo)
st.markdown(f"""
<div class="info-box">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:17px;">Simbología:</p>
    <div class="info-line"><span class="emoji-size">✅</span> Hoy (Día actual)</div>
    <div class="info-line"><span class="emoji-size">🌑</span> Conjunción</div>
    <div class="info-line"><span class="emoji-size">🌘</span> Día de Celebración</div>
    <div class="info-line"><span class="emoji-size">🌸</span> Primavera (Marzo)</div>
    <div class="info-line"><span class="emoji-size">🌕</span> Luna Llena</div>
</div>

<div class="info-box">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:12px; font-size:17px;">Próxima Conjunción:</p>
    <p style="color:#aaa; font-size:14px; margin-bottom:4px;">📍 El Salvador (SV):</p>
    <p style="color:white; font-size:16px; font-weight:bold; margin-bottom:12px;">{info_sv}</p>
    <p style="color:#aaa; font-size:14px; margin-bottom:4px;">🌍 Tiempo Universal (UTC):</p>
    <p style="color:white; font-size:16px; font-weight:bold;">{info_utc}</p>
</div>

<div style="margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center;">
    <p style="color: #666; font-size: 12px; line-height: 1.5;">
        <b>Respaldo Científico:</b><br>
        Los cálculos de este calendario se generan en tiempo real utilizando la biblioteca 
        <b>Skyfield</b> y las efemérides <b>DE421 del Jet Propulsion Laboratory (JPL) de la NASA</b>. 
    </p>
    <p style="color: #888; font-size: 16px; font-style: italic; margin-top: 15px; font-weight: bold;">
        Voz de la Tórtola, Nejapa.
    </p>
</div>
""", unsafe_allow_html=True)
