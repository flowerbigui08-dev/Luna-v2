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
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    
    .conjunction-card { 
        background: #1a1c23; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #333; 
        margin: 20px auto;
        max-width: 500px;
    }
    .label-city { color: #888; font-size: 11px; letter-spacing: 1px; margin-top: 10px; }
    .time-data { color: white; font-size: 18px; font-weight: bold; font-family: monospace; }
    
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; color: white; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 10px 0; }
    .symbol-emoji { width: 40px; text-align: center; font-size: 20px; }
    .symbol-text { flex-grow: 1; font-size: 13px; margin-left: 15px; }
    
    .signature { text-align: center; color: #FF8C00; font-size: 16px; font-weight: bold; font-style: italic; margin-top: 25px; }
    .footer-tech { text-align: center; color: #666; font-size: 11px; margin-top: 10px; line-height: 1.5; border-top: 1px solid #333; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA ---
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
    dia_1_aviv = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    if (dia_1_aviv + timedelta(days=12)) < f_eq.date():
        c_luna = lunas_nuevas[1]
        dia_1_aviv = (c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))).date()
    
    return {
        "n13": dia_1_aviv + timedelta(days=12), 
        "az_ini": dia_1_aviv + timedelta(days=14), 
        "az_fin": dia_1_aviv + timedelta(days=20), 
        "equinoccio": f_eq.date(),
        "omer_ini": dia_1_aviv + timedelta(days=15)
    }

def obtener_datos_mes(anio, mes):
    inicio = tz_sv.localize(datetime(anio, mes, 1))
    t0 = ts.from_datetime(inicio - timedelta(days=5))
    t1 = ts.from_datetime(inicio + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    celebs, conjs, fases = [], [], {}
    for ti, yi in zip(t_f, y_f):
        f_dt = ti.astimezone(tz_sv)
        if f_dt.month == mes:
            fases[f_dt.day] = yi
            if yi == 0:
                conjs.append(f_dt)
                celebs.append((f_dt + timedelta(days=(1 if f_dt.hour < 18 else 2))).date())
    return celebs, conjs, fases

# --- PESTAÑAS ---
tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

with tab_mes:
    c_a, c_m = st.columns(2)
    with c_a: anio_m = st.number_input("Año", 2024, 2030, hoy_sv.year, key="n_anio")
    with c_m: mes_m = st.number_input("Mes", 1, 12, hoy_sv.month, key="n_mes")
    
    esp = obtener_fechas_especiales(anio_m)
    celebs, conjs, fases_mes = obtener_datos_mes(anio_m, mes_m)
    
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
    filas = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_m, mes_m):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                f_act = tz_sv.localize(datetime(anio_m, mes_m, dia)).date()
                bg, border, icon_text, omer_txt = "#1a1c23", "1px solid #333", "", ""
                d_omer = (f_act - esp["omer_ini"]).days + 1
                if 1 <= d_omer <= 50:
                    omer_txt = f"<div style='position:absolute; top:2px; right:4px; color:#9370DB; font-size:10px; font-weight:bold;'>{d_omer}</div>"
                    if d_omer == 1: icon_text = "🌾"
                    elif d_omer == 50: icon_text = "🔥"
                if f_act == esp["n13"]: bg, border, icon_text = "#2c0a0a", "2px solid #FF0000", "🍷"
                elif esp["az_ini"] <= f_act <= esp["az_fin"]: 
                    bg, border = "#241a1d", "2px solid #FFC0CB"
                    if d_omer != 1: icon_text = "🫓"
                elif f_act in celebs: bg, border, icon_text = "#2c1a0a", "2px solid #FF8C00", "🌘"
                if f_act == esp["equinoccio"]: icon_text += "🌸"
                if dia in fases_mes:
                    if fases_mes[dia] == 2: icon_text += "🌕"
                    elif not icon_text: icon_text = iconos[fases_mes[dia]]
                if f_act == hoy_sv.date(): border = "2px solid #00FF7F"
                fila += f"<td style='padding:3px;'><div style='background:{bg}; border:{border}; height:85px; border-radius:10px; position:relative; padding:5px; box-sizing:border-box;'><div style='color:white; font-size:12px; font-weight:bold;'>{dia}</div>{omer_txt}<div style='text-align:center; font-size:24px; margin-top:5px;'>{icon_text}</div></div></td>"
        filas += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_m-1]} {anio_m}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; table-layout:fixed; font-family:sans-serif;}} th{{color:#FF4B4B; padding:5px; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table>", height=550)

    if conjs:
        c_sv = conjs[0].astimezone(tz_sv)
        c_utc = conjs[0].astimezone(tz_utc)
        st.markdown(f"""
        <div class="conjunction-card">
            <p style="color:#FF8C00; font-weight:bold; font-size:18px; margin:0; text-align:center;">Próxima Conjunción ({meses_completos[mes_m-1]}):</p>
            <div class="label-city">📍 EL SALVADOR (SV)</div>
            <div class="time-data">{dias_esp[c_sv.strftime('%A')]} {c_sv.strftime('%d/%m/%y %I:%M %p')}</div>
            <div style="height:1px; background:#333; margin:15px 0;"></div>
            <div class="label-city">🌍 TIEMPO UNIVERSAL (UTC)</div>
            <div class="time-data">{dias_esp[c_utc.strftime('%A')]} {c_utc.strftime('%d/%m/%y')} {c_utc.strftime('%H:%M')} UTC</div>
        </div>
        """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Seleccionar Año", 2024, 2030, anio_m, key="input_anio_full")
    esp_a = obtener_fechas_especiales(anio_f)
    grid_html = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; padding: 10px;'>"
    for m in range(1, 13):
        celebs_a, _, _ = obtener_datos_mes(anio_f, m)
        mes_html = f"<div style='background:#1a1c23; padding:10px; border-radius:10px; border:1px solid #333; color:white;'><div style='color:#FF8C00; font-weight:bold; text-align:center; margin-bottom:8px;'>{meses_completos[m-1]}</div><table style='width:100%; font-size:12px; text-align:center; border-collapse:collapse;'><tr style='color:#FF4B4B; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            mes_html += "<tr>"
            for d in sem:
                if d == 0: mes_html += "<td></td>"
                else:
                    f_l = tz_sv.localize(datetime(anio_f, m, d)).date()
                    est, n_cl = "padding: 3px;", "white"
                    if esp_a["omer_ini"] <= f_l <= (esp_a["omer_ini"] + timedelta(days=49)): n_cl = "#9370DB"
                    if f_l == esp_a["n13"]: est += "border: 1.5px solid #FF0000; border-radius: 5px; background: #2c0a0a;"
                    elif esp_a["az_ini"] <= f_l <= esp_a["az_fin"]: est += "border: 1.5px solid #FFC0CB; border-radius: 5px; background: #241a1d;"
                    elif f_l in celebs_a: est += "border: 1.5px solid #FF8C00; border-radius: 5px; background: #2c1a0a;"
                    mes_html += f"<td><div style='{est} color:{n_cl}; font-weight:bold;'>{d}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    components.html(grid_html + "</div>", height=1000, scrolling=True)

with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    simbs = [("🟢", "Día Actual"), ("🌾", "Día 1 del Omer"), ("🔥", "Día 50 del Omer"), ("🍷", "13 de Nisán"), ("🫓", "Ázimos"), ("🌘", "Día 1 (Mes)"), ("🌕", "Luna Llena"), ("🌑", "Conjunción"), ("🌸", "Equinoccio")]
    html_s = '<div class="info-box">'
    for e, t in simbs:
        html_s += f'<div class="symbol-row"><div class="symbol-emoji">{e}</div><div class="symbol-text"><b>{t}</b></div></div>'
    st.markdown(html_s + '</div>', unsafe_allow_html=True)

st.markdown("<div class='signature'>Voz de la Tórtola, Nejapa.</div><div class='footer-tech'><b>Respaldo Científico:</b> NASA DE421 / Algoritmos USNO.</div>", unsafe_allow_html=True)
