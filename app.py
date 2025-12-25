import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y PÁGINA ---
st.set_page_config(
    page_title="Luna SV", 
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# PARCHE PARA OCULTAR LA BARRA SUPERIOR (FORK, GITHUB Y MENÚ)
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}
    
    .main { background-color: #0e1117; }
    h1 { text-align: center; color: white; margin-bottom: 20px; font-size: 28px; }
    .label-naranja { color: #FF8C00; text-align: center; font-weight: bold; font-size: 22px; margin-top: 10px; margin-bottom: 0px; }
    
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { pointer-events: none; text-align: center !important; font-size: 20px !important; font-weight: bold !important; }
    
    .info-box {
        background: #1a1a1a; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #333; 
        margin-top: 15px;
    }
    .info-line { 
        color: white; 
        font-size: 18px; 
        margin-bottom: 15px; 
        display: flex; 
        align-items: center; 
    }
    .emoji-size { 
        font-size: 28px; 
        margin-right: 15px; 
        width: 35px; 
        text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. RESTO DEL CÓDIGO ---
tz_sv = pytz.timezone('America/El_Salvador')
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

st.markdown("<p class='label-naranja'>Año</p>", unsafe_allow_html=True)
anio = st.number_input("Año selector", min_value=2024, max_value=2030, value=hoy_sv.year, label_visibility="collapsed")

st.markdown("<p class='label-naranja'>Mes</p>", unsafe_allow_html=True)
mes_id = st.number_input("Mes selector", min_value=1, max_value=12, value=hoy_sv.month, label_visibility="collapsed")

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
                        info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%H:%M')}"
                        target = dia + 1 if t_conj.hour < 18 else dia + 2
                        if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
            if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.08); border-radius: 12px;"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "border: 2px solid #FF8C00; background: rgba(255,140,0,0.05); border-radius: 12px;"
            
            fila += f"""
            <td style='border:none; padding:4px;'>
                <div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'>
                    <div style='font-weight:bold; font-size:13px; color:#ccc;'>{dia}</div>
                    <div style='font-size:26px; text-align:center; margin-top:2px;'>{icons}</div>
                </div>
            </td>"""
    filas_html += fila + "</tr>"

st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:25px; font-size:26px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)

html_tabla = f"""
<style>
    table {{ width: 100%; border-collapse: separate; border-spacing: 0px; color: white; font-family: sans-serif; table-layout: fixed; }}
    th {{ padding-bottom: 8px; font-size: 15px; text-align: center; font-weight: bold; }}
</style>
<table>
    <tr><th style='color:#FF4B4B;'>D</th><th style='color:#FF4B4B;'>L</th><th style='color:#FF4B4B;'>M</th><th style='color:#FF4B4B;'>M</th><th style='color:#FF4B4B;'>J</th><th style='color:#FF4B4B;'>V</th><th style='color:#FF4B4B;'>S</th></tr>
    {filas_html}
</table>
"""
components.html(html_tabla, height=480)

st.markdown(f"""
<div class="info-box">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:20px; font-size:20px;">Simbología:</p>
    <div class="info-line"><span class="emoji-size">✅</span> Hoy (Día actual)</div>
    <div class="info-line"><span class="emoji-size">🌑</span> Luna Nueva</div>
    <div class="info-line"><span class="emoji-size">🌘</span> Día de Celebración</div>
    <div class="info-line"><span class="emoji-size">🌸</span> Primavera (Marzo)</div>
    <div class="info-line"><span class="emoji-size">🌕</span> Luna Llena</div>
</div>

<div class="info-box">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:12px; font-size:20px;">Próxima Conjunción:</p>
    <p style="color:#aaa; font-size:15px; margin-bottom:4px;">📍 El Salvador (SV):</p>
    <p style="color:white; font-size:18px; font-weight:bold; margin-bottom:12px;">{info_sv}</p>
    <p style="color:#aaa; font-size:15px; margin-bottom:4px;">🌍 Tiempo Universal (UTC):</p>
    <p style="color:white; font-size:18px; font-weight:bold;">{info_utc}</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div style="margin-top: 30px; padding: 20px; border-top: 1px solid #333; text-align: center;">
        <p style="color: #666; font-size: 12px; line-height: 1.6;">
            <b>Respaldo Científico:</b><br>
            Los cálculos de este calendario se generan en tiempo real utilizando la biblioteca 
            <b>Skyfield</b> y las efemérides <b>DE421 de la NASA (JPL)</b>.<br>
            Ajustado para el huso horario de El Salvador (GMT-6).
        </p>
        <p style="color: #888; font-size: 16px; font-style: italic; margin-top: 15px; font-weight: bold;">
            Voz de la Tortola, Nejapa.
        </p>
    </div>
    """, unsafe_allow_html=True)
