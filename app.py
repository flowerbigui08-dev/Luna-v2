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

st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-top: 15px; color: white; }
    .info-line { color: white; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; }
    .emoji-size { font-size: 20px; margin-right: 12px; width: 25px; text-align: center; }
    .nasa-footer { margin-top: 30px; padding: 15px; border-top: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)
tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

def obtener_fechas_especiales(anio_v):
    # 1. Hallar Equinoccio de Primavera
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_v, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_v, 3, 31)))
    t_equi, y_equi = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    fecha_equinoccio = t_equi[0].astimezone(tz_sv) if len(t_equi) > 0 else tz_sv.localize(datetime(anio_v, 3, 20))

    # 2. Hallar la Luna Nueva (Conjunción) de Marzo
    t_f, y_f = almanac.find_discrete(t0, ts.from_datetime(t1.astimezone(tz_sv) + timedelta(days=30)), almanac.moon_phases(eph))
    
    conjunciones = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    # Primera conjunción de Nisán
    nisan_1 = conjunciones[0]
    nisan_13 = nisan_1 + timedelta(days=13)

    # 3. REGLA: Si el 13 de Nisán es antes del equinoccio, saltar al siguiente mes lunar
    if nisan_13 < fecha_equinoccio:
        nisan_1 = conjunciones[1]
        nisan_13 = nisan_1 + timedelta(days=13)
    
    return nisan_13, fecha_equinoccio

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")

    # Cálculos del mes
    nisan_13_calc, equi_calc = obtener_fechas_especiales(anio)
    
    fecha_inicio = tz_sv.localize(datetime(anio, mes_id, 1))
    t0_m = ts.from_datetime(fecha_inicio - timedelta(days=3))
    t1_m = ts.from_datetime(fecha_inicio + timedelta(days=31))
    t_f, y_f = almanac.find_discrete(t0_m, t1_m, almanac.moon_phases(eph))
    
    fases_dict = {}
    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, {0:"🌑", 1:"🌓", 2:"🌕", 3:"🌗"}[yi]]
            # Marca de celebración (día después de conjunción si es antes de 6pm)
            if yi == 0:
                d_cel = (t_c + timedelta(days=(1 if t_c.hour < 18 else 2)))
                if d_cel.month == mes_id: fases_dict[d_cel.day] = ["CELEB", "🌘"]

    # Render Tabla
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px; color: white;"
                
                # MARCA ESPECIAL 13 DE NISÁN (ROJO)
                if dia == nisan_13_calc.day and mes_id == nisan_13_calc.month:
                    b_style = "border: 2px solid #FF0000; background: #2c0a0a;"
                    icons = "🍷"
                elif dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    icons = dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a;"
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"
                
                fila += f"<td style='padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'><div style='font-weight:bold; font-size:12px;'>{dia}</div><div style='text-align:center; font-size:22px;'>{icons}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h3 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_id-1]} {anio}</h3>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; table-layout:fixed;}} th{{color:#FF4B4B; text-align:center; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=420)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px;">Referencias Teonómicas:</p>
        <div class="info-line"><span class="emoji-size">🍷</span> <b>13 de Nisán:</b> Cena del Señor (Cerca del {nisan_13_calc.strftime('%d/%m')})</div>
        <div class="info-line"><span class="emoji-size">🌸</span> <b>Equinoccio:</b> {equi_calc.strftime('%d de Marzo')}</div>
        <div class="info-line"><span class="emoji-size">✅</span> Hoy | <span class="emoji-size">🌑</span> Conjunción | <span class="emoji-size">🌘</span> Celebración</div>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_f")
    n13, _ = obtener_fechas_especiales(anio_f)
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>"
    for m in range(1, 13):
        # Lógica simplificada para el grid anual
        mes_h = f"<div style='background:#1a1c23; padding:8px; border-radius:10px; border:1px solid #333; color:white;'><div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:12px;'>{meses_completos[m-1]}</div><table style='width:100%; font-size:10px; text-align:center;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            mes_h += "<tr>"
            for d in sem:
                if d == 0: mes_h += "<td></td>"
                else:
                    est = "padding:2px;"
                    if d == n13.day and m == n13.month: est += "border: 1.5px solid #FF0000; border-radius:4px; background:rgba(255,0,0,0.2);"
                    elif d == hoy_sv.day and m == hoy_sv.month: est += "border: 1.5px solid #00FF7F; border-radius:4px;"
                    mes_h += f"<td><div style='{est}'>{d}</div></td>"
            mes_h += "</tr>"
        grid_html += mes_h + "</table></div>"
    components.html(grid_html + "</div>", height=1000, scrolling=True)
