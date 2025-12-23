import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

# --- ESTILOS CSS REFORZADOS ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: white; font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .section-label { font-size: 20px; color: #FF8C00; font-weight: bold; text-align: center; display: block; margin-top: 10px; }
    
    /* Selector de Año */
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    
    /* Pestañas de Meses más compactas para Celular */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 40px !important;
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 0px 12px !important;
        color: #bbb;
        font-size: 14px !important;
    }
    .stTabs [aria-selected="true"] { color: #FF8C00 !important; border: 1px solid #FF8C00 !important; }

    /* Estilo de Leyendas */
    .info-card { border: 1px solid #333; border-radius: 12px; background-color: #1a1a1a; padding: 15px; margin: 10px auto; max-width: 400px; }
    .info-item { font-size: 16px; color: #eee; margin-bottom: 8px; display: flex; align-items: center; }
    .emoji-span { font-size: 22px; margin-right: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 2. SELECTORES
anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy_sv.year, label_visibility="collapsed")

st.markdown("<p class='section-label'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Sistema de pestañas para cambiar de mes
tabs = st.tabs(meses_nombres)
mes_id = hoy_sv.month 

for i, tab in enumerate(tabs):
    with tab:
        mes_id = i + 1
        mes_visual = meses_completos[i]

# --- 3. CÁLCULOS (SIN CACHE PARA EVITAR ERRORES) ---
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)))
ultimo_dia = calendar.monthrange(anio, mes_id)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}

t_equi, y_equi = almanac.find_discrete(t0, t1, almanac.seasons(eph))
equi_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_equi, y_equi)}

info_utc, info_sv = "---", "---"
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# --- 4. CONSTRUCCIÓN DEL CALENDARIO ---
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes_id):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: 
            fila += "<td></td>"
        else:
            icons, b_style = "", ""
            # Fases principales
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0: # Luna Nueva
                        t_conj = fases_dict[dia][1]
                        info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p')
                        # Lógica de Celebración
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target = dia + 1 if t_conj < atardecer else dia + 2
                        if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]

            # Estilos y Bordes
            if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                b_style = "style='border: 2px solid #00FF7F; background-color: rgba(0, 255, 127, 0.1);'"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "style='border: 1.5px solid #FF8C00;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            
            fila += f"<td {b_style}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render de la Tabla
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:22px; font-weight:bold; margin-bottom:10px;'>{mes_visual} {anio}</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; font-family: sans-serif; }}
    th {{ color: #FF4B4B; font-size: 14px; padding-bottom: 5px; text-align: center; }}
    td {{ border: 1px solid #333; height: 75px; vertical-align: top; padding: 4px; overflow: hidden; }}
    .n {{ font-size: 16px; font-weight: bold; }}
    .e {{ font-size: 28px; text-align: center; margin-top: 2px; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=500)

# --- 5. LEYENDAS ---
st.markdown(f"""
<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px; text-align:center;">Simbología:</div>
    <div class="info-item"><span style="width:20px; height:20px; border:2px solid #00FF7F; display:inline-block; margin-right:10px;"></span> Día Actual (Hoy)</div>
    <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva</div>
    <div class="info-item"><span class="emoji-span">🌘</span> Día de Celebración</div>
    <div class="info-item"><span class="emoji-span">🌸</span> Equinoccio / Primavera</div>
    <div class="info-item"><span class="emoji-span">🌕</span> Luna Llena</div>
</div>

<div class="info-card">
    <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px; text-align:center;">Datos de la Conjunción:</div>
    <div class="info-item"><span class="emoji-span">🌎</span> {info_utc} (UTC)</div>
    <div class="info-item"><span class="emoji-span">📍</span> {info_sv} (SV)</div>
</div>
""", unsafe_allow_html=True)
