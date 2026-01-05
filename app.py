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

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    input { pointer-events: none !important; caret-color: transparent !important; text-align: center !important; font-weight: bold !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-top: 15px; color: white; }
    .info-line { color: white; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-size { font-size: 22px; margin-right: 15px; width: 30px; text-align: center; }
    
    .nasa-footer { margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA TÉCNICA DE NISÁN ---
def obtener_fechas_nisan(anio_objetivo):
    # 1. Buscar Equinoccio
    t_equi_0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t_equi_1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, y_eq = almanac.find_discrete(t_equi_0, t_equi_1, almanac.seasons(eph))
    f_equinoccio = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))

    # 2. Buscar Conjunciones
    t_luna_0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t_luna_1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 5, 1)))
    t_f, y_f = almanac.find_discrete(t_luna_0, t_luna_1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    c_luna = lunas_nuevas[0]
    dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
    n13 = dia_1 + timedelta(days=12) 
    
    # Regla del embolismo
    if n13.date() < f_equinoccio.date():
        c_luna = lunas_nuevas[1]
        dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
        n13 = dia_1 + timedelta(days=12)
    
    # Rango de Ázimos: Inicia el día 15 de Nisán (Día 1 + 14 días)
    az_inicio = dia_1 + timedelta(days=14)
    az_fin = dia_1 + timedelta(days=20) # Día 21 de Nisán
    
    return n13, az_inicio, az_fin

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")

    f_n13, f_az_ini, f_az_fin = obtener_fechas_nisan(anio)

    # CÁLCULOS FASES
    fecha_inicio = tz_sv.localize(datetime(anio, mes_id, 1))
    t0 = ts.from_datetime(fecha_inicio - timedelta(days=3))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t1 = ts.from_datetime(fecha_inicio + timedelta(days=ultimo_dia))
    t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    t_seasons, y_seasons = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    
    fases_dict = {}
    seasons_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_seasons, y_seasons) if ti.astimezone(tz_sv).month == mes_id}
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_fases, y_fases):
        t_c = ti.astimezone(tz_sv)
        if yi == 0:
            desp = 1 if t_c.hour < 18 else 2
            t_celeb = t_c + timedelta(days=desp)
            if t_c.month == mes_id: fases_dict[t_c.day] = [0, "🌑"]
            if t_celeb.month == mes_id: fases_dict[t_celeb.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, iconos_fases[yi]]

    # RENDER MENSUAL
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px; color: white;"
                f_actual = tz_sv.localize(datetime(anio, mes_id, dia))
                
                # REGLAS DE PRIORIDAD
                # 1. Cena del Señor (13 Nisán)
                if dia == f_n13.day and mes_id == f_n13.month:
                    b_style = "border: 2px solid #FF0000; background: #2c0a0a; border-radius: 10px;"
                    icons = "🍷"
                # 2. Ázimos (15-21 Nisán) - Rosa Pálido
                elif f_az_ini <= f_actual <= f_az_fin:
                    b_style = "border: 2px solid #FFC0CB; background: #241a1d; border-radius: 10px;"
                    icons = "🫓"
                else:
                    if mes_id == 3 and dia in seasons_dict and seasons_dict[dia] == 0:
                        icons += "🌸"
                    if dia in fases_dict:
                        tipo, dibujo = fases_dict[dia]
                        icons += dibujo
                        if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a; border-radius: 10px;"
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a; border-radius: 10px;"
                
                fila += f"""<td style='padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'>
                        <div style='font-weight:bold; font-size:13px;'>{dia}</div>
                        <div style='text-align:center; font-size:24px; margin-top:2px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:15px; font-size:22px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; font-family:sans-serif; table-layout:fixed;}} th{{color:#FF4B4B; padding-bottom:5px; text-align:center; font-weight:bold; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=440)

    # LEYENDA
    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:17px;">Simbología:</p>
        <div class="info-line"><span class="emoji-size">🍷</span> 13 de Nisán (Cena del Señor)</div>
        <div class="info-line"><span class="emoji-size">🫓</span> 15-21 de Nisán (Ázimos)</div>
        <div class="info-line"><span class="emoji-size">🌘</span> Día 1 de Aviv (Celebración)</div>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_full = st.number_input("Año Completo", 2024, 2030, hoy_sv.year, key="anio_f")
    fn13_a, fazi_a, fazf_a = obtener_fechas_nisan(anio_full)
    
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding-bottom: 20px;'>"
    for m in range(1, 13):
        mes_html = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333; color:white;'>"
        mes_html += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        mes_html += "<table style='width:100%; font-size:11px; text-align:center; border-collapse:collapse;'>"
        mes_html += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for d in sem:
                if d == 0: mes_html += "<td></td>"
                else:
                    est = "padding: 2px;"
                    f_loop = tz_sv.localize(datetime(anio_full, m, d))
                    if d == fn13_a.day and m == fn13_a.month:
                        est += "border: 1.5px solid #FF0000; background: rgba(255,0,0,0.3); border-radius: 4px;"
                    elif fazi_a <= f_loop <= fazf_a:
                        est += "border: 1.5px solid #FFC0CB; background: rgba(255,192,203,0.15); border-radius: 4px;"
                    mes_html += f"<td><div style='{est}'>{d}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    components.html(grid_html + "</div>", height=1150, scrolling=True)

st.markdown("<div class='nasa-footer'><p style='color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;'>Voz de la Tórtola, Nejapa.</p></div>", unsafe_allow_html=True)
