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
hoy_sv = datetime.now(tz_sv)

meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    input { pointer-events: none !important; caret-color: transparent !important; text-align: center !important; font-weight: bold !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; justify-content: center; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    
    .info-box { background: #1a1c23; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-top: 10px; color: white; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 10px 0; }
    .symbol-emoji { width: 50px; text-align: center; font-size: 24px; flex-shrink: 0; }
    .symbol-divider { width: 1px; height: 30px; background-color: #444; margin: 0 15px; flex-shrink: 0; }
    .symbol-text { flex-grow: 1; font-size: 15px; line-height: 1.4; }
    
    .signature-text { text-align: center; color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE FECHAS ---
def obtener_fechas_especiales(anio_objetivo):
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, _ = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    f_eq = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))
    
    tl0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    tl1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 5, 1)))
    t_f, y_f = almanac.find_discrete(tl0, tl1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    c_luna = lunas_nuevas[0]
    desp = 1 if c_luna.hour < 18 else 2
    dia_1_aviv = (c_luna + timedelta(days=desp)).date()
    n13_date = dia_1_aviv + timedelta(days=12)
    
    if n13_date < f_eq.date():
        c_luna = lunas_nuevas[1]
        desp = 1 if c_luna.hour < 18 else 2
        dia_1_aviv = (c_luna + timedelta(days=desp)).date()
        n13_date = dia_1_aviv + timedelta(days=12)
    
    omer_inicio = dia_1_aviv + timedelta(days=15) # 16 de Aviv
    return {
        "n13": n13_date, 
        "az_ini": n13_date + timedelta(days=2), 
        "az_fin": n13_date + timedelta(days=8), 
        "equinoccio": f_eq.date(),
        "omer_ini": omer_inicio
    }

def obtener_celebraciones_mes(anio, mes):
    inicio_busqueda = tz_sv.localize(datetime(anio, mes, 1))
    t0 = ts.from_datetime(inicio_busqueda - timedelta(days=5))
    t1 = ts.from_datetime(inicio_busqueda + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    celebs, conjs = [], []
    for ti, yi in zip(t_f, y_f):
        if yi == 0:
            fecha_c = ti.astimezone(tz_sv)
            conjs.append(fecha_c)
            desp = 1 if fecha_c.hour < 18 else 2
            celebs.append((fecha_c + timedelta(days=desp)).date())
    return celebs, conjs

# --- PESTAÑA 1: MES ---
with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio_m = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_m")
    with col_m: mes_id = st.number_input("Mes", 1, 12, hoy_sv.month, key="mes_m")
    esp = obtener_fechas_especiales(anio_m)
    celebs, _ = obtener_celebraciones_mes(anio_m, mes_id)
    
    t0_f = ts.from_datetime(tz_sv.localize(datetime(anio_m, mes_id, 1)) - timedelta(days=1))
    t1_f = ts.from_datetime(tz_sv.localize(datetime(anio_m, mes_id, 1)) + timedelta(days=31))
    t_f_all, y_f_all = almanac.find_discrete(t0_f, t1_f, almanac.moon_phases(eph))
    fases_dict = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_f_all, y_f_all) if ti.astimezone(tz_sv).month == mes_id}
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_m, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                icons, b_style, omer_label = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px;", ""
                f_actual = tz_sv.localize(datetime(anio_m, mes_id, dia)).date()
                
                # Cálculo de la Cuenta del Omer
                delta_omer = (f_actual - esp["omer_ini"]).days + 1
                if 1 <= delta_omer <= 50:
                    omer_label = f"<div style='position:absolute; top:2px; right:4px; color:#9370DB; font-size:10px; font-weight:bold;'>{delta_omer}</div>"
                    if delta_omer == 1: icons = "🌾"
                    elif delta_omer == 50: icons = "🔥"
                
                # Prioridad de Eventos
                if f_actual == esp["n13"]: b_style, icons = "border: 2px solid #FF0000; background: #2c0a0a; border-radius: 10px;", "🍷"
                elif esp["az_ini"] <= f_actual <= esp["az_fin"]: b_style, icons = "border: 2px solid #FFC0CB; background: #241a1d; border-radius: 10px;", "🫓"
                elif f_actual in celebs: b_style, icons = "border: 2px solid #FF8C00; background: #2c1a0a; border-radius: 10px;", "🌘"
                
                if f_actual == esp["equinoccio"]: icons += "🌸"
                if dia in fases_dict and not icons: icons += iconos_fases[fases_dict[dia]]
                if f_actual == hoy_sv.date(): b_style = "border: 2px solid #00FF7F; background: #0a2c1a; border-radius: 10px;"
                
                fila += f"""
                <td style='padding:4px;'>
                    <div style='{b_style} height: 75px; padding: 6px; box-sizing: border-box; position: relative;'>
                        <div style='font-weight:bold; font-size:13px; color:white; text-align:left;'>{dia}</div>
                        {omer_label}
                        <div style='text-align:center; font-size:24px; margin-top:2px;'>{icons}</div>
                    </div>
                </td>"""
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:15px; font-size:22px;'>{meses_completos[mes_id-1]} {anio_m}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; font-family:sans-serif; table-layout:fixed;}} th{{color:#FF4B4B; padding-bottom:5px; text-align:center; font-weight:bold; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=440)
    st.markdown("<p class='signature-text'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)

# --- PESTAÑA 3: SIMBOLOGÍA ---
with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        simbolos = [
            ("🌾", "<b>Día 1 del Omer:</b> Ofrenda de la Primicia (16 de Aviv)."),
            ("🔥", "<b>Día 50 del Omer:</b> Fiesta de Shavuot (Pentecostés)."),
            ("<span style='color:#9370DB; font-weight:bold; font-size:20px;'>1-50</span>", "<b>Contador Morado:</b> Indica el número del día en la cuenta del Omer."),
            ("🍷", "<b>13 de Nisán:</b> Cena del Señor."),
            ("🫓", "<b>15-21 de Nisán:</b> Semana de los Ázimos."),
            ("🌸", "<b>Equinoccio:</b> Primavera astronómica.")
        ]
        html_simb = '<div class="info-box">'
        for emoji, texto in simbolos:
            html_simb += f'<div class="symbol-row"><div class="symbol-emoji">{emoji}</div><div class="symbol-divider"></div><div class="symbol-text">{texto}</div></div>'
        st.markdown(html_simb + '</div>', unsafe_allow_html=True)
    
    with c2:
        _, conjs_info = obtener_celebraciones_mes(anio_m, mes_id)
        i_sv = conjs_info[0].strftime('%A %d/%m/%y %I:%M %p') if conjs_info else "---"
        st.markdown(f"""
        <div class="info-box">
            <p style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:18px;">Datos de Conjunción:</p>
            <div style="color:white; font-size:18px; font-weight:bold;">{i_sv}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<p class='signature-text'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)
