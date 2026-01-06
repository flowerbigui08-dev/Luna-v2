import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN Y ESTADO DE SESIÓN
st.set_page_config(page_title="Luna SV", layout="wide")

# Inicializar estados para navegación
if 'mes_seleccionado' not in st.session_state:
    st.session_state.mes_seleccionado = datetime.now(pytz.timezone('America/El_Salvador')).month

tz_sv = pytz.timezone('America/El_Salvador')
hoy_sv = datetime.now(tz_sv)

meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ESTILOS CSS REFINADOS
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; margin-bottom: 0px; font-size: 28px; }
    div[data-testid="stNumberInput"] { width: 150px !important; margin: 0 auto !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 14px; font-weight: bold; padding: 10px; }
    
    .info-box { background: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-top: 10px; color: white; }
    .symbol-row { display: flex; align-items: center; border-bottom: 1px solid #222; padding: 8px 0; }
    .symbol-emoji { width: 40px; text-align: center; font-size: 20px; }
    .symbol-divider { width: 1px; height: 25px; background-color: #444; margin: 0 12px; }
    .symbol-text { flex-grow: 1; font-size: 14px; }
    
    .signature-text { text-align: center; color: #FF8C00; font-size: 16px; font-weight: bold; font-style: italic; margin-top: 20px; }
    
    /* Tarjetas de meses en vista anual */
    .month-card { 
        background:#1a1c23; padding:8px; border-radius:10px; border:1px solid #333; color:white; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio, tab_simb = st.tabs(["📅 Mensual", "🗓️ Año", "📖 Info"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

# --- LÓGICA DE CÁLCULO (Igual que antes para precisión técnica) ---
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
    dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
    n13 = dia_1 + timedelta(days=12) 
    if n13.date() < f_eq.date():
        c_luna = lunas_nuevas[1]
        dia_1 = c_luna + timedelta(days=(1 if c_luna.hour < 18 else 2))
        n13 = dia_1 + timedelta(days=12)
    return {"n13": n13, "az_ini": n13 + timedelta(days=2), "az_fin": n13 + timedelta(days=8), "equinoccio": f_eq}

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

# --- PESTAÑA 1: VISTA MENSUAL ---
with tab_mes:
    col_a, col_m = st.columns(2)
    with col_a: anio_m = st.number_input("Año", 2024, 2030, hoy_sv.year)
    with col_m: mes_id = st.number_input("Mes", 1, 12, st.session_state.mes_seleccionado)
    
    st.session_state.mes_seleccionado = mes_id
    esp = obtener_fechas_especiales(anio_m)
    celebs, _ = obtener_celebraciones_mes(anio_m, mes_id)
    
    # Iconos lunares
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
                icons, b_style = "", "border: 1px solid #333; background: #1a1c23; border-radius: 10px;"
                f_actual = tz_sv.localize(datetime(anio_m, mes_id, dia)).date()
                if f_actual == esp["n13"].date(): b_style, icons = "border: 2px solid #FF0000; background: #2c0a0a;", "🍷"
                elif esp["az_ini"].date() <= f_actual <= esp["az_fin"].date(): b_style, icons = "border: 2px solid #FFC0CB; background: #241a1d;", "🫓"
                elif f_actual in celebs: b_style, icons = "border: 2px solid #FF8C00; background: #2c1a0a;", "🌘"
                if f_actual == esp["equinoccio"].date(): icons += "🌸"
                if dia in fases_dict and "🌘" not in icons: icons += iconos_fases[fases_dict[dia]]
                if f_actual == hoy_sv.date(): b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"
                fila += f"<td style='padding:3px;'><div style='{b_style} height: 70px; padding: 5px; box-sizing: border-box; color: white; border-radius: 8px;'><div style='font-weight:bold; font-size:12px;'>{dia}</div><div style='text-align:center; font-size:22px; margin-top:2px;'>{icons}</div></div></td>"
        filas_html += fila + "</tr>"

    st.markdown(f"<h2 style='text-align:center; color:#FF8C00; margin-top:10px; font-size:20px;'>{meses_completos[mes_id-1]} {anio_m}</h2>", unsafe_allow_html=True)
    components.html(f"<style>table{{width:100%; border-collapse:collapse; font-family:sans-serif; table-layout:fixed;}} th{{color:#FF4B4B; text-align:center; font-size:12px;}}</style><table><tr><th>D</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th></tr>{filas_html}</table>", height=420)
    st.markdown("<p class='signature-text'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)

# --- PESTAÑA 2: AÑO COMPLETO ---
with tab_anio:
    anio_full = st.number_input("Año", 2024, 2030, hoy_sv.year, key="anio_f")
    
    # Selector de mes compacto para saltar a la vista mensual
    mes_salto = st.selectbox("Seleccionar mes para ver detalle:", meses_completos, index=st.session_state.mes_seleccionado-1)
    if st.button("Ver Mes Seleccionado", use_container_width=True):
        st.session_state.mes_seleccionado = meses_completos.index(mes_salto) + 1
        st.rerun()

    esp_a = obtener_fechas_especiales(anio_full)
    grid_html = "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px;'>"
    for m in range(1, 13):
        celebs_a, _ = obtener_celebraciones_mes(anio_full, m)
        mes_html = f"<div class='month-card'><div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:12px; margin-bottom:4px;'>{meses_completos[m-1]}</div><table style='width:100%; font-size:9px; text-align:center; border-collapse:collapse;'><tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_full, m):
            mes_html += "<tr>"
            for d in sem:
                if d == 0: mes_html += "<td></td>"
                else:
                    est, f_l = "padding: 1px; color: white;", tz_sv.localize(datetime(anio_full, m, d)).date()
                    if f_l == esp_a["n13"].date(): est += "border: 1px solid #FF0000; background: rgba(255,0,0,0.2);"
                    elif esp_a["az_ini"].date() <= f_l <= esp_a["az_fin"].date(): est += "border: 1px solid #FFC0CB; background: rgba(255,192,203,0.1);"
                    elif f_l in celebs_a: est += "border: 1px solid #FF8C00; background: rgba(255,140,0,0.15);"
                    elif f_l == esp_a["equinoccio"].date(): est += "border: 1px solid #FFD700;"
                    mes_html += f"<td><div style='{est}'>{d}</div></td>"
            mes_html += "</tr>"
        grid_html += mes_html + "</table></div>"
    components.html(grid_html + "</div>", height=1000, scrolling=True)
    st.markdown("<p class='signature-text'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)

# --- PESTAÑA 3: SIMBOLOGÍA ---
with tab_simb:
    st.markdown("<h3 style='color:#FF8C00; text-align:center; font-size:18px;'>Simbología</h3>", unsafe_allow_html=True)
    simbolos = [
        ("🟢", "<b>Día Actual:</b> Fecha de hoy."),
        ("🍷", "<b>13 de Nisán:</b> Cena del Señor."),
        ("🫓", "<b>15-21 Nisán:</b> Panes sin Levadura."),
        ("🌘", "<b>Día 1 (Aviv):</b> Luna de Observación."),
        ("🌸", "<b>Equinoccio:</b> Primavera astronómica."),
        ("🌑", "<b>Conjunción:</b> Luna Nueva exacta."),
        ("🌕", "<b>Luna Llena:</b> Iluminación completa.")
    ]
    html_simb = '<div class="info-box">'
    for emoji, texto in simbolos:
        html_simb += f'<div class="symbol-row"><div class="symbol-emoji">{emoji}</div><div class="symbol-divider"></div><div class="symbol-text">{texto}</div></div>'
    st.markdown(html_simb + '</div>', unsafe_allow_html=True)
    
    # Datos de conjunción simplificados para móvil
    _, conjs_info = obtener_celebraciones_mes(anio_m, mes_id)
    i_sv = conjs_info[0].strftime('%d/%m/%y %I:%M %p') if conjs_info else "---"
    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; font-size:14px;">Próxima Conjunción (ES):</p>
        <p style="font-size:16px; font-weight:bold;">{i_sv}</p>
    </div>
    """, unsafe_allow_html=True)
