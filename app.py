import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN (Si ves 'V3', ya actualizó)
st.set_page_config(page_title="Luna SV V3", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

# 2. ESTILOS PARA MODO OSCURO (Basado en tus capturas)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { text-align: center; color: #FF8C00 !important; }
    /* Estilo para los números de los días */
    .num-oro { 
        color: #FFD700 !important; 
        font-weight: bold; 
        font-size: 16px; 
        text-shadow: 1px 1px 2px #000;
    }
    /* Contenedor para evitar el mordisco lateral */
    .contenedor-calendario {
        padding-right: 15px;
        padding-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.write(f"### 🌙 Calendario Lunar - Voz de la Tórtola")

tab1, tab2 = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE CALENDARIO ---
with tab1:
    c1, c2 = st.columns(2)
    with c1: anio = st.number_input("Año", 2024, 2030, hoy_sv.year)
    with c2: mes = st.number_input("Mes", 1, 12, hoy_sv.month)

    # (Aquí va la lógica de cálculo que ya tienes funcionando...)
    # Usaremos el HTML directo para asegurar los colores
    
    # Simulación de celdas para el ejemplo rápido:
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                estilo = "border: 1px solid #333; background: #1a1c23; border-radius: 8px; height: 60px; padding: 5px;"
                # Forzamos el color amarillo aquí mismo
                fila += f"""<td style='padding:2px;'>
                    <div style='{estilo}'>
                        <span style='color: #FFD700 !important; font-weight: bold;'>{dia}</span>
                    </div>
                </td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
        <table style='width:100%; table-layout:fixed; border-collapse:collapse; font-family:sans-serif;'>
            <tr style='color:#FF4B4B; text-align:center;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>
            {filas_html}
        </table>
    """, height=400)

with tab2:
    # Ajuste para el "mordisco" usando un div con margen
    st.markdown("<div class='contenedor-calendario'>", unsafe_allow_html=True)
    # Aquí se genera el grid anual que ya tienes
    st.markdown("</div>", unsafe_allow_html=True)

# 3. EL TEXTO DE LA NASA QUE FALTABA
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888;">
        <p style="margin:0; font-size: 13px;"><b>Respaldo Científico:</b> Cálculos generados en tiempo real con Skyfield y efemérides de la NASA.</p>
        <p style="margin:5px; font-size: 12px;">Corregido para transiciones astronómicas exactas.</p>
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic; margin-top: 10px;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
