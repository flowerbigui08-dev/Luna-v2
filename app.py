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

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    .info-box { background: #1a1c23; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-top: 10px; color: white; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 8px 0; }
    .symbol-emoji { width: 50px; text-align: center; font-size: 22px; flex-shrink: 0; }
    .symbol-divider { width: 1px; height: 25px; background-color: #444; margin: 0 15px; }
    .label-conjunction { color: #aaa; font-size: 13px; margin-top: 10px; }
    .data-conjunction { color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px; }
    .signature-text { text-align: center; color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic; margin-top: 20px; }
    .nasa-footer { margin-top: 30px; padding: 20px; text-align: center; color: #888; font-size: 13px; border-top: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

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
    dia_1 = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    if (dia_1 + timedelta(days=12)) < f_eq.date():
        c_luna = lunas_nuevas[1]
        dia_1 = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    return {"n13": dia_1 + timedelta(days=12), "az_ini": dia_1 + timedelta(days=14), "az_fin": dia_1 + timedelta(days=20), "eq": f_eq.date(), "omer": dia_1 + timedelta(days=15)}

def obtener_datos_mes(anio, mes):
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) - timedelta(days=1))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes, 1)) + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fases = {ti.astimezone(tz_sv).day: yi for ti, yi in zip(t_f, y_f) if ti.astimezone(tz_sv).month == mes}
    conjs = [ti for ti, yi in zip(t_f, y_f) if yi == 0]
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
                
                # Omer
                d_o = (f_act - esp["omer"]).days + 1
                if 1 <= d_o <= 50:
                    o_l = f"<div style='position:absolute; top:2px; right:4px; color:#9370DB; font-size:10px; font-weight:bold;'>{d_o}</div>"
                    if d_o == 1: ic = "🌾"
                    elif d_o == 50: ic = "🔥"

                # Marcadores
                if f_act == esp["n13"]: b_s, ic = "border: 2px solid #FF0000; background: #2c0a0a;", "🍷"
                elif esp["az_ini"] <= f_act <= esp["az_fin"]:
                    b_s = "border: 2px solid #FFC0CB; background: #241a1d;"
                    if d_o != 1: ic = "🫓"
                elif f_act in celebs_m: b_s, ic = "border: 2px solid #FF8C00; background: #2c1a0a;", "🌘"
                
                if f_act == esp["eq"]: ic += "🌸"
                if dia in fases_m and not ic: ic += iconos[fases_m[dia]]
                if f_act == hoy_sv.date(): b_s = "border: 2px solid #00FF7F; background: #0a2c1a;"
                
                fila += f"<td style='padding:4px;'><div style='{b_s} height:75px; border-radius:10px; position:relative; padding:6px;'><div style='color:white; font-weight:bold;'>{dia}</div>{o_l}<div style='text-align:center; font-size:24px;'>{ic}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_m-1]} {anio_m}</h2>", unsafe_allow_html=True)
    components.html(f"<table><tr style='color:#FF4B4B;'><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table><style>table{{width:100%; border-collapse:collapse; table-layout:fixed; font-family:sans-serif;}} th{{padding-bottom:5px;}}</style>", height=450)

# --- PESTAÑA 2: AÑO ---
with tab_anio:
    a_f = st.number_input("Año", 2024, 2030, hoy_sv.year, key="af")
    e_a = obtener_fechas_especiales(a_f)
    grid = "<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>"
    for m in range(1, 13):
        f_a, _, c_a = obtener_datos_mes(a_f, m)
        m_h = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333; color:white;'><div style='color:#FF8C00; text-align:center; font-weight:bold;'>{meses_completos[m-1]}</div><table style='width:100%; font-size:11px; text-align:center;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(a_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    fl = tz_sv.localize(datetime(a_f, m, d)).date()
                    st_d, cl = "padding:2px;", "white"
                    if e_a["omer"] <= fl <= (e_a["omer"] + timedelta(days=49)): cl = "#9370DB"
                    if fl == e_a["n13"]: st_d += "border: 1.5px solid #FF0000; border-radius:4px;"
                    elif e_a["az_ini"] <= fl <= e_a["az_fin"]: st_d += "border: 1.5px solid #FFC0CB; border-radius:4px;"
                    elif fl in c_a: st_d += "border: 1.5px solid #FF8C00; border-radius:4px;"
                    m_h += f"<td><div style='{st_d} color:{cl};'>{d}</div></td>"
            m_h += "</tr>"
        grid += m_h + "</table></div>"
    components.html(grid + "</div>", height=1500, scrolling=True)

# --- PESTAÑA 3: SIMBOLOGÍA ---
with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        simbs = [("🟢", "Día Actual"), ("🌾", "Día 1 Omer (Primicia)"), ("🔥", "Día 50 Omer (Shavuot)"), ("🍷", "13 Nisán (Cena)"), ("🫓", "Ázimos"), ("🌘", "Día 1 (Aviv)"), ("🌕", "Luna Llena"), ("🌑", "Conjunción")]
        h_s = '<div class="info-box">'
        for em, tx in simbs:
            h_s += f'<div class="symbol-row"><div class="symbol-emoji">{em}</div><div class="symbol-divider"></div><div class="symbol-text">{tx}</div></div>'
        st.markdown(h_s + '</div>', unsafe_allow_html=True)
    with c2:
        if conjs_m:
            dt = conjs_m[0].astimezone(tz_sv)
            dt_u = conjs_m[0].astimezone(tz_utc)
            d_s, d_u = dias_esp[dt.strftime('%A')], dias_esp[dt_u.strftime('%A')]
            st.markdown(f"""<div class="info-box"><p style="color:#FF8C00; font-weight:bold; font-size:18px;">Datos de Conjunción:</p>
            <div class="label-conjunction">EL SALVADOR (ES)</div><div class="data-conjunction">{d_s} {dt.strftime('%d/%m/%y %I:%M %p')}</div>
            <div class="label-conjunction">TIEMPO UNIVERSAL (UTC)</div><div class="data-conjunction">{d_u} {dt_u.strftime('%d/%m/%y %H:%M UTC')}</div></div>""", unsafe_allow_html=True)

st.markdown("<div class='nasa-footer'><p class='signature-text'>Voz de la Tórtola, Nejapa.</p><b>Respaldo Científico:</b> NASA DE421 / USNO. Calibrado para El Salvador.</div>", unsafe_allow_html=True)
