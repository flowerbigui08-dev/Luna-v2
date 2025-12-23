import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime
import pytz
import calendar

# Configuración inicial
st.set_page_config(page_title="Calendario Lunar SV", page_icon="🌙", layout="wide")

# Datos El Salvador
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main-title { text-align: center; color: white; font-size: 32px; font-weight: bold; margin-bottom: 15px; }
    .section-label { font-size: 22px !important; color: #FF8C00 !important; font-weight: bold !important; text-align: center; display: block; }
    div[data-testid="stNumberInput"] { width: 170px !important; margin: 0 auto !important; }
    
    /* Diseño de botones de Meses */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        background-color: #1a1a1a;
        border-radius: 10px;
        color: #ddd;
        font-size: 16px !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { color: #FF8C00 !important; border: 1px solid #FF8C00 !important; }

    /* Leyendas */
    .info-card { border: 1.5px solid #444; border-radius: 15px; background-color: #1a1a1a; padding: 20px; margin: 15px auto; max-width: 450px; }
    .info-item { font-size: 18px; color: #eee; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-span { font-size: 24px; margin-right: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 1. Selector de Año
anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy_sv.year)

# 2. Selector de Mes (Corregido para que funcione el cambio)
st.markdown("<p class='section-label'>Selecciona el Mes:</p>", unsafe_allow_html=True)
meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Detectar en qué pestaña hace clic el usuario
tabs = st.tabs(meses_nombres)
mes_seleccionado = hoy_sv.month # Por defecto hoy

for i, tab in enumerate(tabs):
    with tab:
        mes_seleccionado = i + 1
        mes_visual = meses_completos[i]

# --- CÁLCULOS ASTRONÓMICOS ---
@st.cache_data # Para que cargue rápido al cambiar meses
def obtener_datos_luna(anio, mes):
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)))
    ultimo = calendar.monthrange(anio, mes)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, ultimo, 23, 59)))
    
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}
    
    t_equi, y_equi = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    equi = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_equi, y_equi)}
    
    return fases, equi, ultimo, ts, eph

fases_dict, equi_dict, ultimo_dia, ts, eph = obtener_datos_luna(anio, mes_seleccionado)

info_utc, info_sv = "---", "---"
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# Construir tabla HTML
header = "<tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>"
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes_seleccionado):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: 
            fila += "<td></td>"
        else:
            icons, b_style = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0: # LUNA NUEVA
                        t_conj = fases_dict[dia][1]
                        info_utc = t_conj.astimezone(pytz.utc).strftime('%d/%m/%y %H:%M')
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p')
                        # Lógica de Atardecer para celebración
                        t_s0 = ts.from_datetime(t_conj.replace(hour=0, minute=0))
                        t_s1 = ts.from_datetime(t_conj.replace(hour=23, minute=59))
                        t_s, y_s = almanac.find_discrete(t_s0, t_s1, almanac.sunrise_sunset(eph, loc_sv))
                        atardecer = next((ti.astimezone(tz_sv) for ti, yi in zip(t_s, y_s) if yi == 0), t_conj.replace(hour=17, minute=45))
                        target = dia + 1 if t_conj < atardecer else dia + 2
                        if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
            
            # Estilos de celda
            if dia == hoy_sv.day and mes_seleccionado == hoy_sv.month and anio == hoy_sv.year:
                b_style = "style='border: 2px solid #00FF7F; background-color: rgba(0, 255, 127, 0.1);'"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"
                b_style = "style='border: 1.5px solid #FF8C00;'"
            
            if dia in equi_dict and equi_dict[dia] == 0: icons += "🌸"
            
            # Se eliminó el onclick para evitar que se quede seleccionado
            fila += f"<td {b_style}><div class='n'>{dia}</div><div class='e'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render
html_final = f"""
<div style='text-align:center; color:#FF8C00; font-size:24px; font-weight:bold; margin-bottom:10px;'>{mes_visual} {anio}</div>
<style>
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; font-family: sans-serif; }}
    th {{ color: #FF4B4B; font-size: 15px; padding-bottom: 8px; }}
    td {{ border: 1px solid #333; height: 80px; vertical-align: top; padding: 5px; }}
    .n {{ font-size: 18px; font-weight: bold; }}
    .e {{ font-size: 30px; text-align: center; margin-top: 5px; }}
</style>
<table>{header}{filas_html}</table>
"""
components.html(html_final, height=520)

# Leyendas
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px;">Simbología:</div>
        <div class="info-item"><span style="width:20px; height:20px; border:2px solid #00FF7F; display:inline-block; margin-right:10px;"></span> Hoy</div>
        <div class="info-item"><span class="emoji-span">🌑</span> Luna Nueva</div>
        <div class="info-item"><span class="emoji-span">🌘</span> Celebración</div>
        <div class="info-item"><span class="emoji-span">🌸</span> Primavera</div>
    </div> """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:18px;">Conjunción:</div>
        <div class="info-item"><span class="emoji-span">🌎</span> {info_utc} (UTC)</div>
        <div class="info-item"><span class="emoji-span">📍</span> {info_sv} (SV)</div>
    </div> """, unsafe_allow_html=True)
