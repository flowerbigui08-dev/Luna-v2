import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# 2. ESTILOS CSS REFINADOS (Color de números y corrección de bordes)
st.markdown("""
    <style>
    :root {
        --bg-box: rgba(128, 128, 128, 0.1);
        --border-color: rgba(128, 128, 128, 0.3);
        --num-color: #FFD700; /* Amarillo Oro para que resalte en oscuro y se vea en claro */
    }

    h1 { text-align: center; margin-bottom: 10px; font-size: 28px; }
    
    /* Centrado de inputs */
    div[data-testid="stNumberInput"] { width: 160px !important; margin: 0 auto !important; }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; }

    /* Cuadros de info */
    .info-box {
        background: var(--bg-box); 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid var(--border-color); 
        margin-top: 15px;
    }
    .info-line { font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; }
    .emoji-size { font-size: 22px; margin-right: 15px; width: 30px; text-align: center; }
    
    .mini-leyenda {
        text-align: center;
        background: rgba(255, 140, 0, 0.1);
        border: 1px solid #FF8C00;
        padding: 10px;
        border-radius: 10px;
        margin: 10px auto;
        max-width: 250px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a:
        anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy_sv.year, key="anio_m", label_visibility="collapsed")
    with col_m:
        mes_id = st.number_input("Mes", min_value=1, max_value=12, value=hoy_sv.month, key="mes_m_fix", label_visibility="collapsed")

    # CÁLCULOS
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    t0_busqueda = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    ultimo_dia = calendar.monthrange(anio, mes_id)[1]
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, ultimo_dia, 23, 59)))
    t_fases, y_fases = almanac.find_discrete(t0_busqueda, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv, info_utc = "---", "---"
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_fases, y_fases):
        t_conj = ti.astimezone(tz_sv)
        if yi == 0: 
            if t_conj.month == mes_id:
                t_u = ti.astimezone(pytz.utc)
                info_sv = f"{dias_esp[t_conj.weekday()]} {t_conj.strftime('%d/%m/%y %I:%M %p')}"
                info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%H:%M')} (UTC)"
                fases_dict[t_conj.day] = [0, t_conj]
            dias_a_sumar = 1 if t_conj.hour < 18 else 2
            fecha_celeb = t_conj + timedelta(days=dias_a_sumar)
            if fecha_celeb.month == mes_id:
                fases_dict[fecha_celeb.day] = ["CELEB", None]
        elif t_conj.month == mes_id:
            fases_dict[t_conj.day] = [yi, t_conj]

    # TABLA MENSUAL CON NÚMEROS AMARILLOS Y ANCHO CORREGIDO
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td style='border:none;'></td>"
            else:
                icons = ""
                b_style = "border: 1px solid rgba(128,128,128,0.3); border-radius: 12px; background: rgba(128,128,128,0.05);"
                if dia in fases_dict:
                    tipo = fases_dict[dia][0]
                    if tipo == "CELEB":
                        icons += "🌘"
                        b_style = "border: 2px solid #FF8C00; background: rgba(255,140,0,0.1); border-radius: 12px;"
                    else: icons += iconos_fases.get(tipo, "")
                
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: rgba(0,255,127,0.1); border-radius: 12px;"
                
                # El color #FFD700 asegura que el número se vea siempre
                fila += f"""<td style='border:none; padding:4px;'><div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box;'>
                        <div style='font-weight:bold; font-size:14px; color:#FFD700;'>{dia}</div>
                        <div style='font-size:26px; text-align:center; margin-top:2px;'>{icons}</div></div></td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:20px; font-size:24px;'>{meses_completos[mes_id-1]} {anio}</h2>", unsafe_allow_html=True)
    
    html_tabla = f"""
    <style>
        table {{ width: 98%; border-collapse: separate; border-spacing: 0px; font-family: sans-serif; table-layout: fixed; margin: 0 auto; color: inherit; }}
        th {{ color: #FF4B4B; padding-bottom: 8px; font-size: 15px; text-align: center; font-weight: bold; }}
    </style>
    <table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>
    """
    components.html(html_tabla, height=500)

with tab_anio:
    anio_full = st.number_input("Seleccionar Año", min_value=2024, max_value=2030, value=hoy_sv.year, key="anio_f", label_visibility="collapsed")
    st.markdown("<div class='mini-leyenda'>🟧 Borde Naranja: Día de Celebración</div>", unsafe_allow_html=True)

    # Grid ajustado al 98% para evitar cortes a la derecha
    grid_html = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; width: 98%; margin: 0 auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, 1)) - timedelta(days=3))
        ultimo_a = calendar.monthrange(anio_full, m)[1]
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_full, m, ultimo_a, 23, 59)))
        t_f, y_f = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        celebraciones = []
        for ti, yi in zip(t_f, y_f):
            if yi == 0: 
                dt_conj = ti.astimezone(tz_sv)
                d_sum = 1 if dt_conj.hour < 18 else 2
                f_celeb = dt_conj + timedelta(days=d_sum)
                if f_celeb.month == m: celebraciones.append(f_celeb.day)

        mes_html = f"<div style='background:rgba(128,128,128,0.1); padding:8px; border-radius:10px; border:1px solid rgba(128,128,128,0.2);'>"
        mes_html += f"<div style='color:#FF8C00; font-weight:bold; font-size:16px; text-align:center; margin-bottom:8px;'>{meses_completos[m-1]}</div>"
        mes_html += "<table style='width:100%; font-size:12px; text-align:center; border-collapse:collapse; color:inherit;'>"
        mes_html += "<tr style='color:#FF4B4B; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for semana in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for dia in semana:
                if dia == 0: mes_html += "<td></td>"
                else:
                    inner_style = f"font-size: 13px; font-weight: bold; padding: 3px; color: #FFD700;"
                    if dia in celebraciones:
                        inner_style += "border: 1.5px solid #FF8C00; background: rgba(255,140,0,0.2); border-radius: 4px;"
                    if dia == hoy_sv.day and m == hoy_sv.month and anio_full == hoy_sv.year:
                        inner_style += "border: 1.5px solid #00FF7F; background: rgba(0,255,127,0.15); border-radius: 4px;"
                    mes_html += f"<td><div style='{inner_style}'>{dia}</div></td>"
            mes_html += "</tr>"
        mes_html += "</table></div>"
        grid_html += mes_html
    
    grid_html += "</div>"
    components.html(f"<style>body{{ color: inherit; font-family: sans-serif; }}</style>{grid_html}", height=1400)

# PIE DE PÁGINA
st.markdown("""
    <div style="margin-top: 30px; padding: 15px; border-top: 1px solid rgba(128,128,128,0.2); text-align: center;">
        <p style="color: #FF8C00; font-size: 16px; font-style: italic; font-weight: bold;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
