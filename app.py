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
loc_sv = wgs84.latlon(13.689, -89.187) # El Salvador
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    input { pointer-events: none !important; caret-color: transparent !important; text-align: center !important; font-weight: bold !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-top: 15px; color: white; }
    .info-line { color: white; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-size { font-size: 22px; margin-right: 15px; width: 30px; text-align: center; }
    
    .sunset-card {
        background: #0e1117; padding: 12px; border-radius: 10px; border-left: 4px solid #FF8C00; 
        margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
    }

    .nasa-footer { margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# SELECCIÓN GLOBAL DE MES Y AÑO (Para que afecte a Notas y Calendario)
col_a, col_m = st.columns(2)
with col_a: anio_global = st.number_input("Año", 2024, 2030, hoy_sv.year)
with col_m: mes_global = st.number_input("Mes", 1, 12, hoy_sv.month)

# CREACIÓN DE LAS 3 PESTAÑAS
tab_mes, tab_anio, tab_notas = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📝 Notas y Ocaso"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- TAB 1: VISTA MENSUAL ---
with tab_mes:
    fecha_inicio = tz_sv.localize(datetime(anio_global, mes_global, 1))
    t0 = ts.from_datetime(fecha_inicio - timedelta(days=3))
    ultimo_dia = calendar.monthrange(anio_global, mes_global)[1]
    t1 = ts.from_datetime(fecha_inicio + timedelta(days=ultimo_dia))

    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases_dict = {}
    info_sv, info_utc = "---", "---"
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_fases, y_fases):
        t_c = ti.astimezone(tz_sv)
        if yi == 0:
            if t_c.month == mes_global:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
                info_utc = t_c.astimezone(pytz.utc).strftime(f"{dias_esp[t_c.weekday()]} %d/%m/%y %H:%M")
            desplazamiento = 1 if t_c.hour < 18 else 2
            t_celeb = t_c + timedelta(days=desplazamiento)
            if t_c.month == mes_global: fases_dict[t_c.day] = [0, "🌑"]
            if t_celeb.month == mes_global: fases_dict[t_celeb.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_global:
            fases_dict[t_c.day] = [yi, iconos_fases[yi]]

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_global, mes_global):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px; color: white;"
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    icons = dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a;"
                if dia == hoy_sv.day and mes_global == hoy_sv.month and anio_global == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"
                fila += f"<td style='padding:4px;'><div style='{b_style} height: 70px; padding: 6px; box-sizing: border-box;'><div style='font-weight:bold; font-size:13px;'>{dia}</div><div style='text-align:center; font-size:24px; margin-top:2px;'>{icons}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:10px;'>{meses_completos[mes_global-1]} {anio_global}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; table-layout:fixed;}} th{{color:#FF4B4B; padding-bottom:5px; text-align:center; font-weight:bold; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=420)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:17px;">Simbología:</p>
        <div class="info-line"><span class="emoji-size">✅</span> Hoy | <span class="emoji-size">🌑</span> Conjunción | <span class="emoji-size">🌘</span> Celebración | <span class="emoji-size">🌕</span> Luna Llena</div>
    </div>
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:17px;">Próxima Conjunción:</p>
        <p style="color:white; font-size:16px; font-weight:bold; margin-bottom:5px;">{info_sv}</p>
        <p style="color:#aaa; font-size:14px; margin:0;">UTC: {info_utc}</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: AÑO COMPLETO ---
with tab_anio:
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding-bottom: 20px;'>"
    for m in range(1, 13):
        f_ini = tz_sv.localize(datetime(anio_global, m, 1))
        t0_a, t1_a = ts.from_datetime(f_ini - timedelta(days=3)), ts.from_datetime(f_ini + timedelta(days=31))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        celebs = [ (ti.astimezone(tz_sv) + timedelta(days=(1 if ti.astimezone(tz_sv).hour < 18 else 2))).day for ti, yi in zip(t_f, y_f) if yi == 0 and (ti.astimezone(tz_sv) + timedelta(days=(1 if ti.astimezone(tz_sv).hour < 18 else 2))).month == m ]
        
        mes_h = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333;'><div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:5px;'>{meses_completos[m-1]}</div><table style='width:100%; font-size:11px; text-align:center;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_global, m):
            mes_h += "<tr>"
            for d in sem:
                if d == 0: mes_h += "<td></td>"
                else:
                    est = "padding:2px;"
                    if d in celebs: est += "border: 1px solid #FF8C00; background: rgba(255,140,0,0.15); border-radius:4px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_global == hoy_sv.year: est += "border: 1px solid #00FF7F; background: rgba(0,255,127,0.15); border-radius:4px;"
                    mes_h += f"<td><div style='{est}'>{d}</div></td>"
            mes_h += "</tr>"
        grid_html += mes_h + "</table></div>"
    components.html(grid_html + "</div>", height=1100, scrolling=True)

# --- TAB 3: NOTAS Y OCASO ---
with tab_notas:
    st.markdown(f"### ✍️ Notas de {meses_completos[mes_global-1]}")
    # Nota: Los datos de text_area no se guardan permanentemente en Streamlit sin una base de datos, pero sirve para la sesión.
    st.text_area("Escribe tus apuntes aquí:", placeholder="Ej: Observación de la simiente, detalles técnicos...", height=150, key="notas_area")
    
    st.markdown("---")
    st.markdown(f"### 🌅 Puestas de Sol - {meses_completos[mes_global-1]} {anio_global}")
    
    # Cálculo de ocasos para el mes seleccionado (Días 1, 10, 20 y último)
    dias_sol = [1, 10, 20, calendar.monthrange(anio_global, mes_global)[1]]
    for d in dias_sol:
        t_start = ts.from_datetime(tz_sv.localize(datetime(anio_global, mes_global, d, 12, 0)))
        t_end = ts.from_datetime(tz_sv.localize(datetime(anio_global, mes_global, d, 23, 59)))
        t_e, y_e = almanac.find_discrete(t_start, t_end, almanac.sunrise_sunset(eph, loc_sv))
        for ti, yi in zip(t_e, y_e):
            if yi == 0: # Evento de Ocaso
                hora_sol = ti.astimezone(tz_sv).strftime('%I:%M %p')
                st.markdown(f"""
                <div class="sunset-card">
                    <span style="color:#aaa;">Día {d} ({meses_completos[mes_global-1]})</span>
                    <span class="sunset-time">🌅 {hora_sol}</span>
                </div>
                """, unsafe_allow_html=True)

# FOOTER
st.markdown("""
    <div class="nasa-footer">
        <p style="color: #666; font-size: 12px;"><b>Respaldo Científico:</b> NASA JPL / Skyfield</p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic; margin-top: 10px;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
