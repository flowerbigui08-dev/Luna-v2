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

# Estilos para que se vea oscuro y pro
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { text-align: center; color: white; margin-bottom: 0px; }
    .label-naranja { color: #FF8C00; text-align: center; font-weight: bold; font-size: 20px; margin-top: 15px; }
    div[data-testid="stNumberInput"] { width: 180px !important; margin: 0 auto !important; }
    input { font-size: 22px !important; text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

# 2. SELECTORES DE (+) Y (-)
# Selector de Año
st.markdown("<p class='label-naranja'>Año:</p>", unsafe_allow_html=True)
anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy_sv.year, label_visibility="collapsed")

# Selector de Mes (Ahora con botones + y -)
st.markdown("<p class='label-naranja'>Mes (1 al 12):</p>", unsafe_allow_html=True)
mes_id = st.number_input("Mes", min_value=1, max_value=12, value=hoy_sv.month, label_visibility="collapsed")

meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_visual = meses_completos[mes_id - 1]

# 3. CÁLCULOS ASTRONÓMICOS (Sin trabas)
ts = api.load.timescale()
eph = api.load('de421.bsp')
t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)))
ultimo_dia = calendar.monthrange(anio, mes_id)[1]
t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))

t_fases, y_fases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
fases_dict = {ti.astimezone(tz_sv).day: [yi, ti.astimezone(tz_sv)] for ti, yi in zip(t_fases, y_fases)}

info_sv = "---"
iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

# 4. TABLA DEL CALENDARIO
filas_html = ""
cal = calendar.Calendar(firstweekday=6)

for semana in cal.monthdayscalendar(anio, mes_id):
    fila = "<tr>"
    for dia in semana:
        if dia == 0: fila += "<td></td>"
        else:
            icons, b_style = "", ""
            if dia in fases_dict:
                f_tipo = fases_dict[dia][0]
                if f_tipo != "CELEB":
                    icons += iconos_fases.get(f_tipo, "")
                    if f_tipo == 0: # Luna Nueva
                        t_conj = fases_dict[dia][1]
                        info_sv = t_conj.strftime('%d/%m/%y %I:%M %p')
                        # Lógica Celebración
                        target = dia + 1 if t_conj.hour < 18 else dia + 2
                        if target <= ultimo_dia: fases_dict[target] = ["CELEB", None]
            
            # Colores de bordes
            if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1);"
            elif dia in fases_dict and fases_dict[dia][0] == "CELEB":
                icons += "🌘"; b_style = "border: 1.5px solid #FF8C00;"
            
            fila += f"<td style='{b_style}'><div style='font-weight:bold;'>{dia}</div><div style='font-size:28px; text-align:center;'>{icons}</div></td>"
    filas_html += fila + "</tr>"

# Render final del calendario
st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>{mes_visual} {anio}</h2>", unsafe_allow_html=True)
html_tabla = f"""
<style>
    table {{ width: 100%; border-collapse: collapse; color: white; font-family: sans-serif; }}
    th {{ color: #FF4B4B; padding-bottom: 5px; }}
    td {{ border: 1px solid #333; height: 70px; vertical-align: top; padding: 5px; width: 14%; }}
</style>
<table>
    <tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
    {filas_html}
</table>
"""
components.html(html_tabla, height=450)

# 5. SIMBOLOGÍA
st.markdown(f"""
<div style="background:#1a1a1a; padding:15px; border-radius:12px; border:1px solid #333; margin-top:10px;">
    <p style="color:#FF8C00; font-weight:bold; margin-bottom:8px;">Simbología:</p>
    <p style="color:white; font-size:14px;"><span style="color:#00FF7F;">□</span> Hoy</p>
    <p style="color:white; font-size:14px;">🌑 Luna Nueva | 🌕 Luna Llena</p>
    <p style="color:white; font-size:14px;">🌘 Día de Celebración</p>
    <hr style="border:0.5px solid #333;">
    <p style="color:#aaa; font-size:13px;">Próxima Conjunción (SV):<br><b>{info_sv}</b></p>
</div>
""", unsafe_allow_html=True)
