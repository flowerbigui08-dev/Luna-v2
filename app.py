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
meses_hebreos = ["Aviv", "Ziv", "Siván", "Tamuz", "Av", "Elul", "Etanim", "Bul", "Quisleu", "Tebet", "Sabat", "Adar", "Adar II"]

# ESTILOS CSS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 26px; }
    div[data-testid="stNumberInput"] { width: 140px !important; margin: 0 auto !important; }
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
    .signature { text-align: center; color: #FF8C00; font-size: 20px; font-weight: bold; font-style: italic; margin-top: 30px; }
    .footer-tech { text-align: center; color: #666; font-size: 11px; margin-top: 10px; border-top: 1px solid #333; padding-top: 10px; line-height: 1.6; }
    .sub-title-heb { text-align: center; color: #888; font-size: 16px; margin-top: -15px; margin-bottom: 15px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE CÁLCULO ---
def obtener_fechas_especiales(anio_objetivo):
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 4, 30)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    lunas_nuevas = [ti.astimezone(tz_sv) for ti, yi in zip(t_f, y_f) if yi == 0]
    
    t_eq_0 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 1)))
    t_eq_1 = ts.from_datetime(tz_sv.localize(datetime(anio_objetivo, 3, 31)))
    t_eq, _ = almanac.find_discrete(t_eq_0, t_eq_1, almanac.seasons(eph))
    
    # Guardamos el datetime completo para mostrar la hora después
    f_eq_dt = t_eq[0].astimezone(tz_sv) if len(t_eq) > 0 else tz_sv.localize(datetime(anio_objetivo, 3, 20))
    f_eq_date = f_eq_dt.date()
    
    c_luna_aviv = lunas_nuevas[0]
    dia_1_aviv = (c_luna_aviv + timedelta(days=(1 if c_luna_aviv.hour < 18 else 2))).date()
    if (dia_1_aviv + timedelta(days=12)) < f_eq_date:
        c_luna_aviv = lunas_nuevas[1]
        dia_1_aviv = (c_luna_aviv + timedelta(days=(1 if c_luna_aviv.hour < 18 else 2))).date()
    
    t_mes7_0 = ts.from_datetime(tz_sv.localize(datetime.combine(dia_1_aviv + timedelta(days=160), datetime.min.time())))
    t_mes7_1 = ts.from_datetime(tz_sv.localize(datetime.combine(dia_1_aviv + timedelta(days=200), datetime.min.time())))
    t_f7, y_f7 = almanac.find_discrete(t_mes7_0, t_mes7_1, almanac.moon_phases(eph))
    lunas7 = [ti.astimezone(tz_sv) for ti, yi in zip(t_f7, y_f7) if yi == 0]
    dia_1_mes7 = (lunas7[0] + timedelta(days=(1 if lunas7[0].hour < 18 else 2))).date()

    return {
        "aviv_1": dia_1_aviv,
        "n13": dia_1_aviv + timedelta(days=12), 
        "az_ini": dia_1_aviv + timedelta(days=14), "az_fin": dia_1_aviv + timedelta(days=20), 
        "omer_ini": dia_1_aviv + timedelta(days=15), 
        "equinoccio_dt": f_eq_dt,
        "equinoccio_date": f_eq_date,
        "yom_kippur": dia_1_mes7 + timedelta(days=9),
        "sucot_ini": dia_1_mes7 + timedelta(days=14), "sucot_fin": dia_1_mes7 + timedelta(days=21)
    }

def obtener_datos_mes(anio, mes):
    inicio = tz_sv.localize(datetime(anio, mes, 1))
    t0 = ts.from_datetime(inicio - timedelta(days=3))
    t1 = ts.from_datetime(inicio + timedelta(days=32))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    celebs, conjs, fases = [], [], {}
    esp = obtener_fechas_especiales(anio)
    
    for ti, yi in zip(t_f, y_f):
        f_dt = ti.astimezone(tz_sv)
        if yi == 0:
            conjs.append(f_dt)
            dia_c = (f_dt + timedelta(days=(1 if f_dt.hour < 18 else 2))).date()
            if dia_c.month == mes and dia_c.year == anio:
                diff_days = (dia_c - esp["aviv_1"]).days
                num_mes_heb = round(diff_days / 29.5) % 12
                nombre_heb = meses_hebreos[num_mes_heb]
                celebs.append((dia_c, nombre_heb))
        if f_dt.month == mes: fases[f_dt.day] = yi
    return celebs, conjs, fases

# --- PESTAÑAS ---
tab_mes, tab_anio, tab_simb = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo", "📖 Simbología"])

with tab_mes:
    c_a, c_m = st.columns(2)
    with c_a: anio_m = st.number_input("Año", 2024, 2035, hoy_sv.year)
    with c_m: mes_m = st.number_input("Mes", 1, 12, hoy_sv.month)
    
    esp = obtener_fechas_especiales(anio_m)
    celebs, conjs, fases_mes = obtener_datos_mes(anio_m, mes_m)
    
    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-bottom:5px;'>{meses_completos[mes_m-1]} {anio_m}</h2>", unsafe_allow_html=True)
    
    if celebs:
        dia_heb, nombre_heb = celebs[0]
        st.markdown(f"<div class='sub-title-heb'>{dia_heb.day} de {meses_completos[mes_m-1]}, 1 de {nombre_heb}</div>", unsafe_allow_html=True)
    
    iconos_fases = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}
    filas = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio_m, mes_m):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                f_act = tz_sv.localize(datetime(anio_m, mes_m, dia)).date()
                bg, border, omer_txt = "#1a1c23", "1px solid #333", ""
                icons_list = []
                
                if any(dia == c[0].day for c in celebs):
                    bg, border = "#2c1a0a", "2px solid #FF8C00"
                    icons_list.append("🌘")

                d_omer = (f_act - esp["omer_ini"]).days + 1
                if 1 <= d_omer <= 50:
                    omer_txt = f"<div style='position:absolute; top:2px; right:4px; color:#9370DB; font-size:10px; font-weight:bold;'>{d_omer}</div>"
                    if d_omer == 1: icons_list.append("🌾")
                    elif d_omer == 50: icons_list.append("🔥")

                if f_act == esp["n13"]: bg, border = "#2c0a0a", "2px solid #FF0000"; icons_list.append("🍷")
                elif esp["az_ini"] <= f_act <= esp["az_fin"]: bg, border = "#241a1d", "2px solid #FFC0CB"; icons_list.append("🫓")
                elif f_act == esp["yom_kippur"]: bg, border = "#2c0a0a", "2px solid #FF0000"; icons_list.append("🐏")
                elif esp["sucot_ini"] <= f_act <= esp["sucot_fin"]: bg, border = "#0a2c1a", "2px solid #3EB489"; icons_list.append("🌿")
                
                if f_act == esp["equinoccio_date"]: icons_list.append("🌸")
                if dia in fases_mes: icons_list.append(iconos_fases[fases_mes[dia]])
                if f_act == hoy_sv.date(): border = "2px solid #00FF7F"

                icon_text = "".join(icons_list)
                fila += f"<td style='padding:3px;'><div style='background:{bg}; border:{border}; height:85px; border-radius:10px; position:relative; padding:5px; box-sizing:border-box;'><div style='color:white; font-size:12px; font-weight:bold;'>{dia}</div>{omer_txt}<div style='text-align:center; font-size:22px; margin-top:5px; line-height:1.1;'>{icon_text}</div></div></td>"
        filas += fila + "</tr>"

    components.html(f"<style>table{{width:100%; border-collapse:collapse; table-layout:fixed; font-family:sans-serif;}} th{{color:#FF4B4B; padding:5px; font-size:14px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas}</table>", height=550)

    if conjs:
        c_sv = conjs[0].astimezone(tz_sv)
        c_utc = conjs[0].astimezone(tz_utc)
        eq_sv = esp["equinoccio_dt"]
        
        st.markdown(f"""
        <div class="conjunction-card">
            <p style="color:#FF8C00; font-weight:bold; font-size:15px; margin-bottom:5px;">Próxima Conjunción ({meses_completos[mes_m-1]}):</p>
            <div class="label-city">📍 El Salvador (SV)</div>
            <div class="time-data">{dias_esp[c_sv.strftime('%A')]} {c_sv.strftime('%d/%m/%y %I:%M %p')}</div>
            <div class="label-city">🌍 Tiempo Universal (UTC)</div>
            <div class="time-data">{dias_esp[c_utc.strftime('%A')]} {c_utc.strftime('%d/%m/%y')} {c_utc.strftime('%H:%M')} UTC</div>
            <hr style="border: 0; border-top: 1px solid #333; margin: 10px 0;">
            <p style="color:#3EB489; font-weight:bold; font-size:14px; margin-bottom:5px;">🌸 Equinoccio de Primavera {anio_m}:</p>
            <div class="time-data">{dias_esp[eq_sv.strftime('%A')]} {eq_sv.strftime('%d')} de {meses_completos[eq_sv.month-1]} - {eq_sv.strftime('%I:%M %p')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.number_input("Seleccionar Año", 2024, 2035, anio_m, key="input_anio_full")
    esp_a = obtener_fechas_especiales(anio_f)
    grid_html = "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 10px;'><style>@media (max-width: 800px) { div { grid-template-columns: repeat(2, 1fr) !important; } } @media (max-width: 500px) { div { grid-template-columns: 1fr !important; } } .mes-box { background:#1a1c23; padding:8px; border-radius:10px; border:1px solid #333; color:white; } .mes-title { color:#FF8C00; font-weight:bold; text-align:center; font-size:13px; margin-bottom:5px; } .mes-table { width:100%; font-size:10px; text-align:center; border-collapse:collapse; }</style>"
    for m in range(1, 13):
        celebs_a, _, _ = obtener_datos_mes(anio_f, m)
        mes_html = f"<div class='mes-box'><div class='mes-title'>{meses_completos[m-1]}</div><table class='mes-table'><tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            mes_html += "<tr>"
            for d in sem:
                if d == 0: mes_html += "<td></td>"
                else:
                    f_l = tz_sv.localize(datetime(anio_f, m, d)).date()
                    est, n_cl = "", "white"
                    if esp_a["omer_ini"] <= f_l <= (esp_a["omer_ini"] + timedelta(days=49)): n_cl = "#9370DB"
                    if f_l == esp_a["n13"] or f_l == esp_a["yom_kippur"]: est = "border: 1px solid #FF0000; border-radius: 3px; background: #2c0a0a;"
                    elif esp_a["az_ini"] <= f_l <= esp_a["az_fin"]: est = "border: 1px solid #FFC0CB; border-radius: 3px; background: #241a1d;"
                    elif esp_a["sucot_ini"] <= f_l <= esp_a["sucot_fin"]: est = "border: 1px solid #3EB489; border-radius: 3px; background: #0a2c1a;"
                    elif any(f_l == c[0] for c in celebs_a): est = "border: 1px solid #FF8C00; border-radius: 3px; background: #2c1a0a;"
                    mes_html += f"<td><div style='{est} color:{n_cl}; font-weight:bold;'>{d}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    components.html(grid_html + "</div>", height=900, scrolling=True)

with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center;'>Guía de Marcadores</h3>", unsafe_allow_html=True)
    simbs = [
        ("🟢", "Día Actual"), 
        ("🍷", "13 de Nisán (Cena del Señor)"), 
        ("🫓", "15-21 Nisán (Ázimos)"), 
        ("🌾", "Primicia (Omer 1)"), 
        ("🐏", "10 Mes 7 (Expiación / Yom Kippur)"), 
        ("🌿", "15-22 Mes 7 (Cabañas / Sucot)"), 
        ("🔥", "Omer 50 (Shavuot)"), 
        ("🌸", "Equinoccio de Primavera (Referencia Solar)"),
        ("🌘", "Día 1 (Celebración / Observación)"), 
        ("🌑", "Conjunción (Luna Nueva Astronómica)")
    ]
    html_s = '<div class="info-box">'
    for e, t in simbs:
        html_s += f'<div class="symbol-row"><div class="symbol-emoji">{e}</div><div class="symbol-text"><b>{t}</b></div></div>'
    st.markdown(html_s + '</div>', unsafe_allow_html=True)

st.markdown("<div class='signature'>Voz de la Tórtola, Nejapa.</div>", unsafe_allow_html=True)
st.markdown("<div class='footer-tech'><b>Respaldo Científico:</b> NASA DE421 / USNO.</div>", unsafe_allow_html=True)
