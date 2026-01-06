import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
tz_utc = pytz.utc
hoy_sv = datetime.now(tz_sv)

st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; font-size: 28px; margin-bottom: 0; }
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; color: white; margin-bottom: 10px; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 8px 0; }
    .symbol-emoji { width: 45px; text-align: center; font-size: 20px; }
    .symbol-text { flex-grow: 1; font-size: 14px; margin-left: 10px; }
    .signature-text { text-align: center; color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic; margin-top: 15px; }
    .nasa-footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #333; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE CÁLCULO ---
def obtener_datos(anio, mes):
    # Equinoccio y Aviv 1
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, 4, 30)))
    t_eq, _ = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    f_eq = t_eq[0].astimezone(tz_sv).date() if t_eq else datetime(anio, 3, 20).date()
    
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    c_luna = lunas_nuevas[0]
    dia_1_aviv = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    if (dia_1_aviv + timedelta(days=12)) < f_eq:
        c_luna = lunas_nuevas[1]
        dia_1_aviv = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    
    omer_ini = dia_1_aviv + timedelta(days=15) # 16 de Aviv
    
    # Conjunciones del mes actual
    tm0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) - timedelta(days=2))
    tm1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) + timedelta(days=32))
    t_fm, y_fm = almanac.find_discrete(tm0, tm1, almanac.moon_phases(eph))
    
    conjs_list = [ti for ti, yi in zip(t_fm, y_fm) if yi == 0]
    fechas_celebs = [(ti.astimezone(tz_sv) + timedelta(days=(1 if ti.astimezone(tz_sv).hour < 18 else 2))).date() for ti in conjs_list]
    
    return {
        "n13": dia_1_aviv + timedelta(days=12),
        "az_ini": dia_1_aviv + timedelta(days=14),
        "az_fin": dia_1_aviv + timedelta(days=20),
        "omer_ini": omer_ini,
        "equinoccio": f_eq,
        "celebs": fechas_celebs,
        "conjs_data": conjs_list
    }

# --- PESTAÑA 1: MES ---
with tab_mes:
    col1, col2 = st.columns(2)
    anio_m = col1.number_input("Año", 2024, 2030, hoy_sv.year)
    mes_m = col2.number_input("Mes", 1, 12, hoy_sv.month)
    
    d = obtener_datos(anio_m, mes_m)
    
    filas = ""
    for sem in calendar.Calendar(6).monthdayscalendar(anio_m, mes_m):
        fila = "<tr>"
        for dia in sem:
            if dia == 0: fila += "<td></td>"
            else:
                f_act = datetime(anio_m, mes_m, dia).date()
                icons, omer_num, style = "", "", "border: 1px solid #333; background: #1a1c23;"
                
                # Omer Logic
                diff = (f_act - d["omer_ini"]).days + 1
                if 1 <= diff <= 50:
                    omer_num = f"<div style='position:absolute; top:2px; right:4px; color:#9370DB; font-size:10px; font-weight:bold;'>{diff}</div>"
                    if diff == 1: icons = "🌾"
                    elif diff == 50: icons = "🔥"
                
                # Fiestas y Emojis
                if f_act == d["n13"]: style, icons = "border: 2px solid #FF0000; background: #2c0a0a;", "🍷"
                elif d["az_ini"] <= f_act <= d["az_fin"]: style, icons = "border: 2px solid #FFC0CB; background: #241a1d;", "🫓"
                elif f_act in d["celebs"]: style, icons = "border: 2px solid #FF8C00; background: #2c1a0a;", "🌘"
                
                if f_act == d["equinoccio"]: icons += "🌸"
                if f_act == hoy_sv.date(): style = "border: 2px solid #00FF7F; background: #0a2c1a;"
                
                fila += f"<td style='padding:2px;'><div style='{style} height:70px; position:relative; border-radius:8px; padding:5px;'><div style='color:white; font-size:12px;'>{dia}</div>{omer_num}<div style='text-align:center; font-size:22px;'>{icons}</div></div></td>"
        filas += fila + "</tr>"

    st.markdown(f"<h3 style='text-align:center; color:#FF8C00;'>{calendar.month_name[mes_m]} {anio_m}</h3>", unsafe_allow_html=True)
    components.html(f"<table><tr style='color:#FF4B4B; font-family:sans-serif;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table><style>table{{width:100%; table-layout:fixed; border-collapse:collapse;}} th{{padding-bottom:5px;}}</style>", height=420)

# --- PESTAÑA 3: SIMBOLOGÍA Y CONJUNCIÓN ---
with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        simbs = [("🌾", "<b>Día 1 del Omer:</b> Primicia de la Cebada (16 de Aviv)."), 
                  ("🔥", "<b>Día 50:</b> Shavuot / Pentecostés."),
                  ("<span style='color:#9370DB; font-weight:bold;'>1-50</span>", "<b>Contador Morado:</b> Día actual de la cuenta."),
                  ("🍷", "<b>13 de Nisán:</b> Cena del Señor."),
                  ("🫓", "<b>15-21 de Nisán:</b> Ázimos."),
                  ("🌘", "<b>Día 1:</b> Luna de observación."),
                  ("🌸", "<b>Equinoccio:</b> Primavera astronómica.")]
        html = '<div class="info-box">'
        for em, txt in simbs:
            html += f'<div class="symbol-row"><div class="symbol-emoji">{em}</div><div class="symbol-text">{txt}</div></div>'
        st.markdown(html + '</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="info-box"><p style="color:#FF8C00; font-weight:bold; margin-bottom:10px;">Datos de Conjunción:</p>', unsafe_allow_html=True)
        if d["conjs_data"]:
            conj = d["conjs_data"][0]
            st.write(f"**EL SALVADOR (ES):**")
            st.code(conj.astimezone(tz_sv).strftime('%A %d/%m/%y %I:%M %p'))
            st.write(f"**TIEMPO UNIVERSAL (UTC):**")
            st.code(conj.astimezone(tz_utc).strftime('%A %d/%m/%y %H:%M UTC'))
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p class='signature-text'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)
st.markdown("<div class='nasa-footer'>Respaldo Científico: Efemérides NASA DE421 y algoritmos del USNO. Calibrado para El Salvador.</div>", unsafe_allow_html=True)
