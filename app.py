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
    
    .label-conjunction { color: #aaa; font-size: 14px; margin-bottom: 2px; margin-top: 8px; }
    .data-conjunction { color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    
    .nasa-footer { margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center; color: #888; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE NISÁN Y CELEBRACIONES ---
def obtener_fechas_especiales(anio_objetivo, mes_objetivo=None):
    # Equinoccio
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, y_eq = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    f_eq = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))

    # Nisán
    tl0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    tl1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 5, 1)))
    t_f, y_f = almanac.find_discrete(tl0, tl1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    c_luna = lunas_nuevas[0]
    dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
    n13 = dia_1 + timedelta(days=12) 
    
    if n13.date() < f_eq.date():
        c_luna = lunas_nuevas[1]
        dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
        n13 = dia_1 + timedelta(days=12)
    
    return {
        "n13": n13,
        "az_ini": n13 + timedelta(days=2),
        "az_fin": n13 + timedelta(days=8),
        "equinoccio": f_eq
    }

def obtener_celebraciones_mes(anio, mes):
    # Buscar conjunción para este mes específico
    inicio_busqueda = tz_sv.localize(datetime(anio, mes, 1))
    t0 = ts.from_datetime(inicio_busqueda - timedelta(days=5))
    t1 = ts.from_datetime(inicio_busqueda + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    celebraciones = []
    conjunciones = []
    for ti, yi in zip(t_f, y_f):
        if yi == 0: # Luna Nueva
            fecha_c = ti.astimezone(tz_sv)
            conjunciones.append(fecha_c)
            desp = 1 if fecha_c.hour < 18 else 2
            celebraciones.append((fecha_c + timedelta(days=desp)).date())
    return celebraciones, conjunciones

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")

    especiales = obtener_fechas_especiales(anio)
    celebs_mes, conjs_mes = obtener_celebraciones_mes(anio, mes_id)

    # Datos para la caja de conjunción
    info_sv = conjs_mes[0].strftime('%A %d/%m/%y %I:%M %p') if conjs_mes else "---"
    info_utc = conjs_mes[0].astimezone(pytz.utc).strftime('%A %d/%m/%y %H:%M') if conjs_mes else "---"

    # Fases generales
    t0_f = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=1))
    t1_f = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) + timedelta(days=31))
    t_f_all, y_f_all = almanac.find_discrete(t0_f, t1_f, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_f_all, y_f_all) if ti.astimezone(tz_sv).month == mes_id}
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px;"
                f_actual = tz_sv.localize(datetime(anio, mes_id, dia)).date()
                
                # REGLAS DE MARCADO
                if f_actual == especiales["n13"].date():
                    b_style = "border: 2px solid #FF0000; background: #2c0a0a; border-radius: 10px;"
                    icons = "🍷"
                elif especiales["az_ini"].date() <= f_actual <= especiales["az_fin"].date():
                    b_style = "border: 2px solid #FFC0CB; background: #241a1d; border-radius: 10px;"
                    icons = "🫓"
                elif f_actual in celebs_mes:
                    b_style = "border: 2px solid #FF8C00; background: #2c1a0a; border-radius: 10px;"
                    icons = "🌘"
                
                if f_actual == especiales["equinoccio"].date(): icons += "🌸"
                if dia in fases_dict and "🌘" not in icons: icons += iconos_fases[fases_dict[dia]]
                
                if f_actual == hoy_sv.date():
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a; border-radius: 10px;"
                
                fila += f"""<td style='padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box; color: white;'>
                        <div style='font-weight:bold; font-size:13px;'>{dia}</div>
                        <div style='text-align:center; font-size:24px; margin-top:2px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:15px; font-size:22px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; font-family:sans-serif; table-layout:fixed;}} th{{color:#FF4B4B; padding-bottom:5px; text-align:center; font-weight:bold; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=440)

    # LEYENDA COMPLETA
    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:17px;">Simbología:</p>
        <div class="info-line"><span class="emoji-size">🟢</span> Hoy (Día actual)</div>
        <div class="info-line"><span class="emoji-size">🍷</span> 13 de Nisán (Cena del Señor)</div>
        <div class="info-line"><span class="emoji-size">🫓</span> 15-21 de Nisán (Ázimos)</div>
        <div class="info-line"><span class="emoji-size">🌸</span> Equinoccio de Primavera</div>
        <div class="info-line"><span class="emoji-size">🌘</span> Día 1 (Luna de Observación / Celebración)</div>
        <div class="info-line"><span class="emoji-size">🌑</span> Conjunción Astronómica</div>
    </div>
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:5px; font-size:17px;">Próxima Conjunción:</p>
        <div class="label-conjunction">EL SALVADOR (ES)</div>
        <div class="data-conjunction">{info_sv}</div>
        <div class="label-conjunction">TIEMPO UNIVERSAL (UTC)</div>
        <div class="data-conjunction">{info_utc}</div>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_full = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_f")
    esp_a = obtener_fechas_especiales(anio_full)
    
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding-bottom: 20px;'>"
    for m in range(1, 13):
        celebs_a, _ = obtener_celebraciones_mes(anio_full, m)
        mes_html = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333; color:white;'>"
        mes_html += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:5px;'>{meses_completos[m-1]}</div>"
        mes_html += "<table style='width:100%; font-size:11px; text-align:center; border-collapse:collapse;'>"
        mes_html += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for d in sem:
                if d == 0: mes_html += "<td></td>"
                else:
                    est = "padding: 2px; color: white;"
                    f_l = tz_sv.localize(datetime(anio_full, m, d)).date()
                    if f_l == esp_a["n13"].date():
                        est += "border: 1.5px solid #FF0000; background: rgba(255,0,0,0.3); border-radius: 4px;"
                    elif esp_a["az_ini"].date() <= f_l <= esp_a["az_fin"].date():
                        est += "border: 1.5px solid #FFC0CB; background: rgba(255,192,203,0.15); border-radius: 4px;"
                    elif f_l in celebs_a: # BORDES NARANJA EN VISTA ANUAL
                        est += "border: 1.5px solid #FF8C00; background: rgba(255,140,0,0.2); border-radius: 4px;"
                    elif f_l == esp_a["equinoccio"].date():
                        est += "border: 1px solid #FFD700;"
                    mes_html += f"<td><div style='{est}'>{d}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    components.html(grid_html + "</div>", height=1150, scrolling=True)

st.markdown("""
    <div class='nasa-footer'>
        <p style='color: #FF8C00; font-size: 16px; font-weight: bold; font-style: italic; margin-bottom: 8px;'>Voz de la Tórtola, Nejapa.</p>
        Los datos astronómicos de este calendario, incluyendo fases lunares y equinoccios,<br>
        están basados en las efemérides DE421 de la NASA y cálculos del Observatorio Naval de EE. UU. (USNO).
    </div>
    """, unsafe_allow_html=True)
