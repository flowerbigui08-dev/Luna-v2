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

dias_esp = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS OPTIMIZADOS PARA MÓVIL
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 5px; font-size: 24px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-top: 5px; color: white; }
    .label-conjunction { color: #aaa; font-size: 12px; margin-top: 8px; }
    .data-conjunction { color: white; font-size: 15px; font-weight: bold; margin-bottom: 5px; }
    .signature-text { text-align: center; color: #FF8C00; font-size: 16px; font-weight: bold; font-style: italic; margin-top: 10px; }
    .nasa-footer { margin-top: 20px; padding: 15px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio, tab_simb = st.tabs(["📅 Mensual", "🗓️ Anual", "📖 Info"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

def obtener_fechas_especiales(anio_objetivo):
    # Cálculo simplificado para lógica de Aviv/Nisán
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, _ = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    f_eq = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))
    
    tl0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    tl1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 5, 1)))
    t_f, y_f = almanac.find_discrete(tl0, tl1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    c_luna = lunas_nuevas[0]
    dia_1 = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    if (dia_1 + timedelta(days=12)) < f_eq.date():
        c_luna = lunas_nuevas[1]
        dia_1 = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
        
    return {"n13": dia_1 + timedelta(days=12), "az_ini": dia_1 + timedelta(days=14), "az_fin": dia_1 + timedelta(days=20), "eq": f_eq.date(), "omer": dia_1 + timedelta(days=15)}

def obtener_datos_mes(anio, mes):
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) - timedelta(days=2))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) + timedelta(days=33))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_f, y_f) if ti.astimezone(tz_sv).month == mes}
    conjs = [ti for ti, yi in zip(t_f, y_f) if yi == 0 and ti.astimezone(tz_sv).month == mes]
    celebs = [(ti.astimezone(tz_sv) + timedelta(days=(1 if ti.astimezone(tz_sv).hour < 18 else 2))).date() for ti in conjs]
    return fases, conjs, celebs

# --- PESTAÑA 1: MES ---
with tab_mes:
    c_a, c_m = st.columns(2)
    anio_m = c_a.number_input("Año", 2024, 2030, hoy_sv.year)
    mes_m = c_m.number_input("Mes", 1, 12, hoy_sv.month)
    
    esp = obtener_fechas_especiales(anio_m)
    fases_m, conjs_m, celebs_m = obtener_datos_mes(anio_m, mes_m)
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_m, mes_m):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                f_act = tz_sv.localize(datetime(anio_m, mes_m, dia)).date()
                b_s, ic, o_l = "border: 1px solid #333; background: #1a1c23;", "", ""
                
                # Lógica de Emojis
                emoji_lista = []
                
                # 1. Omer (Número)
                d_o = (f_act - esp["omer"]).days + 1
                if 1 <= d_o <= 50:
                    o_l = f"<div style='position:absolute; top:2px; right:3px; color:#9370DB; font-size:9px; font-weight:bold;'>{d_o}</div>"
                    if d_o == 1: emoji_lista.append("🌾")
                    elif d_o == 50: emoji_lista.append("🔥")

                # 2. Festividades
                if f_act == esp["n13"]: 
                    b_s, ic_fest = "border: 2px solid #FF0000; background: #2c0a0a;", "🍷"
                    emoji_lista.append(ic_fest)
                elif esp["az_ini"] <= f_act <= esp["az_fin"]:
                    b_s = "border: 1px solid #FFC0CB; background: #241a1d;"
                    if d_o != 1: emoji_lista.append("🫓")
                elif f_act in celebs_m: 
                    b_s, ic_fest = "border: 2px solid #FF8C00; background: #2c1a0a;", "🌘"
                    emoji_lista.append(ic_fest)
                
                # 3. Luna (Siempre presente si es fase)
                if dia in fases_m:
                    emoji_lista.append(iconos[fases_m[dia]])
                
                # 4. Equinoccio
                if f_act == esp["eq"]: emoji_lista.append("🌸")
                
                # Bordes especiales
                if f_act == hoy_sv.date(): b_s = "border: 2px solid #00FF7F; background: #0a2c1a;"
                
                # Mostrar máximo 2 emojis para no desbordar
                ic_final = "".join(emoji_lista[:2])
                
                fila += f"<td style='padding:2px;'><div style='{b_s} height:65px; border-radius:8px; position:relative; padding:4px;'><div style='color:white; font-size:12px; font-weight:bold;'>{dia}</div>{o_l}<div style='text-align:center; font-size:20px; margin-top:5px;'>{ic_final}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h3 style='text-align:center; color:#FF8C00; margin: 10px 0;'>{meses_completos[mes_m-1]} {anio_m}</h3>", unsafe_allow_html=True)
    components.html(f"<table><tr style='color:#FF4B4B; font-size:12px;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table><style>table{{width:100%; border-collapse:collapse; table-layout:fixed; font-family:sans-serif;}} th{{padding-bottom:5px;}}</style>", height=420)

# --- PESTAÑA 3: SIMBOLOGÍA ---
with tab_simb:
    if conjs_m:
        dt = conjs_m[0].astimezone(tz_sv)
        dt_u = conjs_m[0].astimezone(tz_utc)
        d_s, d_u = dias_esp[dt.strftime('%A')], dias_esp[dt_u.strftime('%A')]
        st.markdown(f"""<div class="info-box"><p style="color:#FF8C00; font-weight:bold; font-size:16px; margin-bottom:5px;">Próxima Conjunción:</p>
        <div class="label-conjunction">EL SALVADOR (ES)</div><div class="data-conjunction">{d_s} {dt.strftime('%d/%m/%y %I:%M %p')}</div>
        <div class="label-conjunction">TIEMPO UNIVERSAL (UTC)</div><div class="data-conjunction">{d_u} {dt_u.strftime('%d/%m/%y %H:%M UTC')}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="info-box" style="font-size:13px;">
    <b>Simbología:</b><br>
    🟢 Día Actual | 🌕 Luna Llena | 🌑 Conjunción<br>
    🍷 13 Nisán | 🫓 Ázimos | 🌘 Día 1 (Mes)<br>
    🌾 Primicia (Omer 1) | 🔥 Shavuot (Omer 50)
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='nasa-footer'><p class='signature-text'>Voz de la Tórtola, Nejapa.</p><b>Respaldo:</b> NASA DE421 / USNO.</div>", unsafe_allow_html=True)
