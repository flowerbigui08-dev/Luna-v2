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
loc_sv = wgs84.latlon(13.689, -89.187)
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

color_gris = "#2c303c"

# ESTADO PARA NAVEGACIÓN
if 'anio_val' not in st.session_state:
    st.session_state.anio_val = hoy_sv.year
if 'mes_val' not in st.session_state:
    st.session_state.mes_val = hoy_sv.month

# 2. ESTILOS CSS REFORZADOS
st.markdown(f"""
    <style>
    h1 {{ text-align: center; color: #FF8C00; font-size: 26px; margin-bottom: 10px; }}
    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; }}
    
    /* Caja del visor central */
    .visor-central {{
        display: flex;
        align-items: center;
        justify-content: center;
        background: {color_gris};
        color: white;
        font-weight: bold;
        font-size: 18px;
        height: 45px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 10px;
    }}
    
    .label-guia {{
        text-align: center;
        color: #FF8C00;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
    }}

    .info-box-v10 {{
        padding: 15px; border-radius: 12px; 
        border: 1px solid rgba(128, 128, 128, 0.3); 
        margin-top: 15px; 
        background: {color_gris};
        color: white;
    }}
    .linea-simbolo {{ display: flex; align-items: center; margin-bottom: 10px; font-size: 16px; }}
    .emoji-guia {{ width: 35px; font-size: 26px; margin-right: 12px; text-align: center; }}
    
    /* Ajuste de botones Streamlit para que no tengan margen extra */
    div.stButton > button {{
        width: 100%;
        height: 45px;
        font-size: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    # FILA DE CONTROLADORES
    c_izq, c_der = st.columns(2)
    
    with c_izq:
        st.markdown("<div class='label-guia'>Año</div>", unsafe_allow_html=True)
        ba1, ba2, ba3 = st.columns([1,2,1])
        with ba1: 
            if st.button("➖", key="a_menos"): st.session_state.anio_val -= 1
        with ba2:
            st.markdown(f"<div class='visor-central'>{st.session_state.anio_val}</div>", unsafe_allow_html=True)
        with ba3:
            if st.button("➕", key="a_mas"): st.session_state.anio_val += 1
            
    with c_der:
        st.markdown("<div class='label-guia'>Mes</div>", unsafe_allow_html=True)
        bm1, bm2, bm3 = st.columns([1,2,1])
        with bm1:
            if st.button("➖", key="m_menos"):
                if st.session_state.mes_val > 1: st.session_state.mes_val -= 1
        with bm2:
            st.markdown(f"<div class='visor-central'>{meses_completos[st.session_state.mes_val-1]}</div>", unsafe_allow_html=True)
        with bm3:
            if st.button("➕", key="m_mas"):
                if st.session_state.mes_val < 12: st.session_state.mes_val += 1

    anio = st.session_state.anio_val
    mes_id = st.session_state.mes_val

    # Cálculos
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv, info_utc = "---", "---"
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        t_u = ti.astimezone(pytz.utc)
        if yi == 0: 
            if t_c.month == mes_id:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
                info_utc = f"{dias_esp[t_u.weekday()]} {t_u.strftime('%H:%M')} (UTC)"
                fases_dict[t_c.day] = [0, "🌑"]
            ds = 1 if t_c.hour < 18 else 2
            fc = t_c + timedelta(days=ds)
            if fc.month == mes_id: fases_dict[fc.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, iconos[yi]]

    # Tabla
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                ico, b_style = "", f"border: 1px solid #4a4e5a; background: {color_gris};"
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    ico = dibujo
                    if tipo == "CELEB": b_style = f"border: 2px solid #FF8C00; background: #3d2b1f;"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = f"border: 2px solid #00FF7F; background: #243d30;"

                fila += f"""<td style='padding:4px;'><div style='{b_style} height:70px; border-radius:10px; padding:6px; box-sizing:border-box;'>
                        <div style='color:white; font-weight:bold; font-size:14px;'>{dia}</div>
                        <div style='text-align:center; font-size:24px;'>{ico}</div></div></td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
    <div style='font-family:sans-serif;'>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>
            {filas_html}
        </table>
    </div>""", height=460)

    # Info
    st.markdown(f"""
    <div class="info-box-v10">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:12px; font-size:17px;">Simbología:</p>
        <div class="linea-simbolo"><span class="emoji-guia">✅</span> Hoy (Día actual)</div>
        <div class="linea-simbolo"><span class="emoji-guia">🌑</span> Conjunción (Luna Nueva)</div>
        <div class="linea-simbolo"><span class="emoji-guia">🌘</span> Día de Celebración</div>
        <div class="linea-simbolo"><span class="emoji-guia">🌕</span> Luna Llena</div>
    </div>
    <div class="info-box-v10">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:10px; font-size:17px;">Próxima Conjunción:</p>
        <p style="margin:0; font-size:16px;">📍 El Salvador: <b>{info_sv}</b></p>
        <p style="margin:8px 0 0 0; font-size:16px;">🌍 Tiempo Universal: <b>{info_utc}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    st.markdown("<div class='label-guia'>Navegar Año</div>", unsafe_allow_html=True)
    ba1_a, ba2_a, ba3_a = st.columns([1,2,1])
    with ba1_a: 
        if st.button("➖", key="aa_menos"): st.session_state.anio_val -= 1
    with ba2_a:
        st.markdown(f"<div class='visor-central'>{st.session_state.anio_val}</div>", unsafe_allow_html=True)
    with ba3_a:
        if st.button("➕", key="aa_mas"): st.session_state.anio_val += 1
    
    anio_f = st.session_state.anio_val
    grid_h = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:8px; width:94%; margin:auto;'>"
    for m in range(1, 13):
        t0_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, 1)) - timedelta(days=3))
        t1_a = ts.from_datetime(tz_sv.localize(datetime(anio_f, m, calendar.monthrange(anio_f, m)[1], 23, 59)))
        t_fa, y_fa = almanac.find_discrete(t0_a, t1_a, almanac.moon_phases(eph))
        cs = []
        for ti, yi in zip(t_fa, y_fa):
            if yi == 0:
                dt = ti.astimezone(tz_sv)
                ds = 1 if dt.hour < 18 else 2
                fc = dt + timedelta(days=ds)
                if fc.month == m: cs.append(fc.day)

        m_h = f"<div style='background:{color_gris}; padding:8px; border-radius:8px; border:1px solid #4a4e5a;'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:14px; margin-bottom:3px;'>{meses_completos[m-1]}</div>"
        m_h += "<table style='width:100%; font-size:11px; text-align:center; color:white;'>"
        m_h += "<tr style='color:#FF4B4B;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    style = "color:white; font-weight:bold;"
                    if d in cs: style += f"border:1px solid #FF8C00; background:rgba(255,140,0,0.25); border-radius:3px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style += "border:1px solid #00FF7F; border-radius:3px;"
                    m_h += f"<td><div style='{style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_h += m_h + "</table></div>"
    components.html(grid_h + "</div>", height=1050)

st.markdown("""
    <hr style="border:0.1px solid rgba(128,128,128,0.2); margin-top:20px;">
    <div style="text-align: center; padding: 0 10px 30px 10px;">
        <p style="color: grey; font-size: 13px;"><b>Respaldo Científico:</b> Skyfield & JPL/NASA DE421.</p>
        <p style="color: #FF8C00; font-size: 20px; font-weight: bold; font-style: italic;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
