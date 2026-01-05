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
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# 2. ESTILOS CSS REFORZADOS (Evitan desplazamiento lateral)
st.markdown("""
    <style>
    /* Bloquear desplazamiento horizontal */
    .main .block-container { max-width: 100%; overflow-x: hidden; padding-left: 1rem; padding-right: 1rem; }
    
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 26px; }
    div[data-testid="stNumberInput"] { width: 140px !important; margin: 0 auto !important; }
    input { pointer-events: none !important; text-align: center !important; font-weight: bold !important; }
    
    .info-box { background: #1a1c23; padding: 12px; border-radius: 12px; border: 1px solid #333; margin-top: 15px; color: white; overflow: hidden; }
    
    /* Contenedor de Ocaso compatible con móviles estrechos */
    .sunset-container {
        display: flex; flex-wrap: wrap; gap: 8px; justify-content: space-between; margin-top: 5px;
    }
    .sunset-card {
        background: #0e1117; flex: 1 1 calc(50% - 10px); min-width: 100px;
        padding: 8px; border-radius: 8px; border: 1px solid #444; text-align: center;
    }
    .sunset-day { color: #FF8C00; font-size: 10px; font-weight: bold; display: block; }
    .sunset-time { color: white; font-size: 14px; font-weight: bold; }

    .nasa-footer { margin-top: 25px; padding: 15px; border-top: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Mes", "🗓️ Año"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")

    # CÁLCULOS
    fecha_inicio = tz_sv.localize(datetime(anio, mes_id, 1))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t0 = ts.from_datetime(fecha_inicio - timedelta(days=3))
    t1 = ts.from_datetime(fecha_inicio + timedelta(days=ultimo_dia))
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    t_seasons, y_seasons = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    
    fases_dict = {}
    seasons_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_seasons, y_seasons) if ti.astimezone(tz_sv).month == mes_id}
    info_sv, info_utc = "---", "---"

    for ti, yi in zip(t_fases, y_fases):
        t_c = ti.astimezone(tz_sv)
        if yi == 0 and t_c.month == mes_id:
            info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
            info_utc = t_c.astimezone(pytz.utc).strftime(f"{dias_esp[t_c.weekday()]} %d/%m/%y %H:%M")
            
            desplazamiento = 1 if t_c.hour < 18 else 2
            t_celeb = t_c + timedelta(days=desplazamiento)
            fases_dict[t_c.day] = [0, "🌑"]
            if t_celeb.month == mes_id: fases_dict[t_celeb.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, {1:"🌓", 2:"🌕", 3:"🌗"}[yi]]

    # Render Calendario (Ajustado para no desbordar)
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 8px; color: white;"
                if mes_id == 3 and dia in seasons_dict and seasons_dict[dia] == 0: icons += "🌸"
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    icons += dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a;"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"
                
                fila += f"<td style='padding:2px;'><div style='{b_style} height: 65px; padding: 4px;'>"
                fila += f"<div style='font-weight:bold; font-size:12px;'>{dia}</div>"
                fila += f"<div style='text-align:center; font-size:20px;'>{icons}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h3 style='text-align:center; color:#FF8C00; margin-top:10px;'>{meses_completos[mes_id-1]} {anio}</h3>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; table-layout:fixed;}} th{{color:#FF4B4B; font-size:12px; text-align:center; padding-bottom:5px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=380)

    # INFO BOXES
    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:16px;">Simbología:</p>
        <div style="font-size:14px;">✅ Hoy | 🌑 Conjunción | 🌘 Celebración | 🌸 Primavera | 🌕 Luna Llena</div>
    </div>
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:5px; font-size:16px;">Próxima Conjunción:</p>
        <div style="font-size:13px; color:#aaa;">📍 El Salvador (SV):</div>
        <div style="font-size:15px; font-weight:bold; margin-bottom:8px;">{info_sv}</div>
        <div style="font-size:13px; color:#aaa;">🌍 Tiempo Universal (UTC):</div>
        <div style="font-size:15px; font-weight:bold;">{info_utc}</div>
    </div>
    """, unsafe_allow_html=True)

    # OCASO AJUSTADO
    sunset_cards = ""
    puntos_sol = [1, 10, 20, ultimo_dia]
    for d in puntos_sol:
        t_i = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, d, 12, 0)))
        t_f = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, d, 23, 59)))
        t_e, y_e = almanac.find_discrete(t_i, t_f, almanac.sunrise_sunset(eph, loc_sv))
        for ti, yi in zip(t_e, y_e):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                sunset_cards += f"""<div class="sunset-card"><span class="sunset-day">DÍA {d}</span><span class="sunset-time">{dt.strftime('%I:%M %p')}</span></div>"""
    
    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:8px; font-size:16px;">🌅 Ocaso en El Salvador</p>
        <div class="sunset-container">{sunset_cards}</div>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_full = st.number_input("Año Completo", 2024, 2030, hoy_sv.year, key="anio_f")
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;'>"
    for m in range(1, 13):
        f_ini = tz_sv.localize(datetime(anio_full, m, 1))
        t0_a, t1_a = ts.from_datetime(f_ini - timedelta(days=3)), ts.from_datetime(f_ini + timedelta(days=31))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        celebs = []
        for ti, yi in zip(t_f, y_f):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                target = dt + timedelta(days=(1 if dt.hour < 18 else 2))
                if target.month == m: celebs.append(target.day)
        
        mes_h = f"<div style='background:#1a1c23; padding:8px; border-radius:8px; border:1px solid #333;'><div style='color:#FF8C00; font-weight:bold; font-size:12px; text-align:center;'>{meses_completos[m-1][:3]}</div><table style='width:100%; font-size:9px; text-align:center;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_h += "<tr>"
            for d in sem:
                if d == 0: mes_h += "<td></td>"
                else:
                    s = "padding:1px;"
                    if d in celebs: s += "border: 1px solid #FF8C00; border-radius:3px;"
                    if d == hoy_sv.day and m == hoy_sv.month: s += "background:#00FF7F; color:black; border-radius:3px;"
                    mes_h += f"<td><div style='{s}'>{d}</div></td>"
            mes_h += "</tr>"
        grid_html += mes_h + "</table></div>"
    components.html(grid_html + "</div>", height=600, scrolling=True)

st.markdown('<p style="text-align:center; color:#FF8C00; font-weight:bold; font-style:italic; margin-top:20px;">Voz de la Tórtola, Nejapa.</p>', unsafe_allow_html=True)
