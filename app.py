import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
tz_utc = pytz.utc
hoy_sv = datetime.now(tz_sv)

dias_esp = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}

meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 26px; }
    .conjunction-card { 
        background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; 
        margin: 15px auto; max-width: 450px; text-align: center;
    }
    .label-city { color: #888; font-size: 10px; letter-spacing: 1px; margin-top: 8px; text-transform: uppercase; }
    .time-data { color: #ddd; font-size: 14px; font-weight: 500; font-family: monospace; }
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; color: white; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 8px 0; }
    .symbol-emoji { width: 35px; text-align: center; font-size: 18px; }
    .symbol-text { flex-grow: 1; font-size: 13px; margin-left: 12px; }
    .signature { text-align: center; color: #FF8C00; font-size: 16px; font-weight: bold; font-style: italic; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE CÁLCULO ---
def obtener_fechas_especiales(anio_objetivo):
    # Cálculo de Aviv 1
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 4, 30)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    # Lógica de equinoccio para determinar Aviv
    t_eq_0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t_eq_1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, _ = almanac.find_discrete(t_eq_0, t_eq_1, almanac.seasons(eph))
    f_eq = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))
    
    c_luna_aviv = lunas_nuevas[0]
    dia_1_aviv = (c_luna_aviv + timedelta(days=(1 if c_luna_aviv.hour < 18 else 2))).date()
    if (dia_1_aviv + timedelta(days=12)) < f_eq.date():
        c_luna_aviv = lunas_nuevas[1]
        dia_1_aviv = (c_luna_aviv + timedelta(days=(1 if c_luna_aviv.hour < 18 else 2))).date()
    
    # Cálculo del Mes 7
    t_mes7_0 = ts.from_datetime(tz_sv.localize(datetime.combine(dia_1_aviv + timedelta(days=160), datetime.min.time())))
    t_mes7_1 = ts.from_datetime(tz_sv.localize(datetime.combine(dia_1_aviv + timedelta(days=200), datetime.min.time())))
    t_f7, y_f7 = almanac.find_discrete(t_mes7_0, t_mes7_1, almanac.moon_phases(eph))
    lunas7 = [ti.astimezone(tz_sv) for ti, yi in zip(t_f7, y_f7) if yi == 0]
    
    c_luna7 = lunas7[0]
    dia_1_mes7 = (c_luna7 + timedelta(days=(1 if c_luna7.hour < 18 else 2))).date()

    return {
        "n13": dia_1_aviv + timedelta(days=12), 
        "az_ini": dia_1_aviv + timedelta(days=14), 
        "az_fin": dia_1_aviv + timedelta(days=20), 
        "omer_ini": dia_1_aviv + timedelta(days=15),
        "equinoccio": f_eq.date(),
        "yom_kippur": dia_1_mes7 + timedelta(days=9),
        "sucot_ini": dia_1_mes7 + timedelta(days=14),
        "sucot_fin": dia_1_mes7 + timedelta(days=21)
    }

def obtener_datos_mes(anio, mes):
    # Ampliamos el rango para detectar conjunciones que definen el inicio del mes
    inicio = tz_sv.localize(datetime(anio, mes, 1))
    t0 = ts.from_datetime(inicio - timedelta(days=2))
    t1 = ts.from_datetime(inicio + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    celebs, conjs, fases = [], [], {}
    for ti, yi in zip(t_f, y_f):
        f_dt = ti.astimezone(tz_sv)
        fases[f_dt.day] = yi if f_dt.month == mes else -1
        if yi == 0:
            conjs.append(f_dt)
            # El día de celebración puede caer en el mes actual incluso si la conjunción fue el mes anterior
            dia_celeb = (f_dt + timedelta(days=(1 if f_dt.hour < 18 else 2))).date()
            if dia_celeb.month == mes:
                celebs.append(dia_celeb)
    return celebs, conjs, fases

# --- PESTAÑAS ---
tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

with tab_mes:
    c_a, c_m = st.columns(2)
    with c_a: anio_m = st.number_input("Año", 2024, 2030, 2026 if hoy_sv.year < 2026 else hoy_sv.year)
    with c_m: mes_m = st.number_input("Mes", 1, 12, hoy_sv.month)
    
    esp = obtener_fechas_especiales(anio_m)
    celebs, conjs, fases_mes = obtener_datos_mes(anio_m, mes_m)
    
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
    filas = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_m, mes_m):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                f_act = tz_sv.localize(datetime(anio_m, mes_m, dia)).date()
                bg, border = "#1a1c23", "1px solid #333"
                icons_list = []
                
                # Marcadores de Fiestas
                if f_act == esp["n13"]: bg, border, icons_list = "#2c0a0a", "2px solid #FF0000", ["🍷"]
                elif esp["az_ini"] <= f_act <= esp["az_fin"]: bg, border, icons_list = "#241a1d", "2px solid #FFC0CB", ["🫓"]
                elif f_act == esp["yom_kippur"]: bg, border, icons_list = "#2c0a0a", "2px solid #FF0000", ["🐏"]
                elif esp["sucot_ini"] <= f_act <= esp["sucot_fin"]: bg, border, icons_list = "#0a2c1a", "2px solid #3EB489", ["🌿"]
                elif f_act in celebs: bg, border, icons_list = "#2c1a0a", "2px solid #FF8C00", ["🌘"]
                
                # Fases y Hoy
                if dia in fases_mes and fases_mes[dia] != -1: icons_list.append(iconos_fases[fases_mes[dia]])
                if f_act == hoy_sv.date(): border = "2px solid #00FF7F"

                icon_text = "".join(icons_list)
                fila += f"<td style='padding:3px;'><div style='background:{bg}; border:{border}; height:85px; border-radius:10px; padding:5px; box-sizing:border-box;'><div style='color:white; font-size:12px; font-weight:bold;'>{dia}</div><div style='text-align:center; font-size:22px; margin-top:5px;'>{icon_text}</div></div></td>"
        filas += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_m-1]} {anio_m}</h2>", unsafe_allow_html=True)
    components.html(f"<table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table><style>table{{width:100%; border-collapse:collapse; table-layout:fixed; font-family:sans-serif;}} th{{color:#FF4B4B; padding:5px;}}</style>", height=500)

with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    # Aquí sacrificamos Luna Llena por Conjunción como pediste
    simbs = [
        ("🟢", "Día Actual"), 
        ("🍷", "13 de Nisán (Cena del Señor)"), 
        ("🫓", "15-21 Nisán (Semana de Ázimos)"), 
        ("🐏", "10 del Mes 7 (Expiación / Yom Kippur)"), 
        ("🌿", "15-22 Mes 7 (Cabañas / Sucot)"), 
        ("🌘", "Día 1 (Día de Celebración / Luna de Observación)"),
        ("🌑", "Conjunción (Momento exacto de la Luna Nueva astronómica)")
    ]
    html_s = '<div class="info-box">'
    for e, t in simbs:
        html_s += f'<div class="symbol-row"><div class="symbol-emoji">{e}</div><div class="symbol-text"><b>{t}</b></div></div>'
    st.markdown(html_s + '</div>', unsafe_allow_html=True)

st.markdown("<div class='signature'>Voz de la Tórtola, Nejapa.</div>", unsafe_allow_html=True)
