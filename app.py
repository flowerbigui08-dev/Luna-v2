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

# INICIALIZAR ESTADO
if 'anio_v' not in st.session_state: st.session_state.anio_v = hoy_sv.year
if 'mes_v' not in st.session_state: st.session_state.mes_v = hoy_sv.month

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# 2. ESTILOS CSS (Para que el diseño no se rompa en móvil)
st.markdown("""
    <style>
    h1 { text-align: center; color: #FF8C00; font-size: 26px; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    
    /* El visor central estilo "cuadro" como tu imagen */
    .visor-estilo-cuadro {
        background: #1a1c23;
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #333;
        font-weight: bold;
        font-size: 16px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Forzar que los botones de Streamlit sean compactos */
    div.stButton > button {
        height: 45px !important;
        width: 100%;
        border-radius: 8px;
    }
    
    .info-box {
        padding: 15px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.3); 
        margin-top: 15px; background: rgba(128,128,128,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Vista Mensual", "🗓️ Año Completo"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    # FILA DE CONTROLES (Año y Mes)
    # Usamos columnas muy pequeñas para las flechas y una más grande para el centro
    
    # CONTROL DE AÑO
    st.write("📅 **Año**")
    ca1, ca2, ca3 = st.columns([1, 2, 1])
    with ca1:
        if st.button("➖", key="a_minus"): st.session_state.anio_v -= 1
    with ca2:
        st.markdown(f"<div class='visor-estilo-cuadro'>{st.session_state.anio_v}</div>", unsafe_allow_html=True)
    with ca3:
        if st.button("➕", key="a_plus"): st.session_state.anio_v += 1
    
    # CONTROL DE MES
    st.write("📆 **Mes**")
    cm1, cm2, cm3 = st.columns([1, 2, 1])
    with cm1:
        if st.button("➖", key="m_minus"):
            st.session_state.mes_v = 12 if st.session_state.mes_v == 1 else st.session_state.mes_v - 1
    with cm2:
        st.markdown(f"<div class='visor-estilo-cuadro'>{meses_completos[st.session_state.mes_v-1]}</div>", unsafe_allow_html=True)
    with cm3:
        if st.button("➕", key="m_plus"):
            st.session_state.mes_v = 1 if st.session_state.mes_v == 12 else st.session_state.mes_v + 1

    anio, mes_id = st.session_state.anio_v, st.session_state.mes_v

    # Cálculos Astronómicos (Igual a tu base)
    t0 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, 1)) - timedelta(days=3))
    t1 = ts.from_datetime(tz_sv.localize(datetime(anio, mes_id, calendar.monthrange(anio, mes_id)[1], 23, 59)))
    t_f, y_f = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    
    fases_dict = {}
    info_sv = "---"
    iconos = {0: "🌑", 1: "🌓", 2: "🌕", 3: "🌗"}

    for ti, yi in zip(t_f, y_f):
        t_c = ti.astimezone(tz_sv)
        if yi == 0: 
            if t_c.month == mes_id:
                info_sv = f"{dias_esp[t_c.weekday()]} {t_c.strftime('%d/%m/%y %I:%M %p')}"
                fases_dict[t_c.day] = [0, "🌑"]
            ds = 1 if t_c.hour < 18 else 2
            fc = t_c + timedelta(days=ds)
            if fc.month == mes_id: fases_dict[fc.day] = ["CELEB", "🌘"]
        elif t_c.month == mes_id:
            fases_dict[t_c.day] = [yi, iconos[yi]]

    # Calendario HTML
    filas_html = ""
    for semana in calendar.Calendar(6).monthdayscalendar(anio, mes_id):
        fila = "<tr>"
        for dia in semana:
            if dia == 0: fila += "<td></td>"
            else:
                ico, b_style = "", "border: 1px solid #333; background: #1a1c23;"
                if dia in fases_dict:
                    tipo, dibujo = fases_dict[dia]
                    ico = dibujo
                    if tipo == "CELEB": b_style = "border: 2px solid #FF8C00; background: #2c1a0a;"
                if dia == hoy_sv.day and mes_id == hoy_sv.month and anio == hoy_sv.year:
                    b_style = "border: 2px solid #00FF7F; background: #0a2c1a;"

                fila += f"""<td style='padding:3px;'><div style='{b_style} height:70px; border-radius:10px; padding:5px; box-sizing:border-box;'>
                        <div style='color:white; font-weight:bold; font-size:14px;'>{dia}</div>
                        <div style='text-align:center; font-size:24px;'>{ico}</div></div></td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
    <div style='font-family:sans-serif;'>
        <h3 style='text-align:center; color:#FF8C00;'>{meses_completos[mes_id-1]} {anio}</h3>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>
            {filas_html}
        </table>
    </div>""", height=460)

    st.markdown(f"""
    <div class="info-box">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:5px;">Próxima Conjunción:</p>
        <p>📍 El Salvador: <b>{info_sv}</b></p>
    </div>""", unsafe_allow_html=True)

with tab_anio:
    st.write("📅 **Seleccione Año**")
    ca_1, ca_2, ca_3 = st.columns([1, 2, 1])
    with ca_1:
        if st.button("➖", key="aa_minus"): st.session_state.anio_v -= 1
    with ca_2:
        st.markdown(f"<div class='visor-estilo-cuadro'>{st.session_state.anio_v}</div>", unsafe_allow_html=True)
    with ca_3:
        if st.button("➕", key="aa_plus"): st.session_state.anio_v += 1
    
    anio_f = st.session_state.anio_v
    grid_h = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:8px; width:92%; margin:auto;'>"
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

        m_h = f"<div style='background:#1a1c23; padding:8px; border-radius:8px; border:1px solid #333;'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:14px; margin-bottom:3px;'>{meses_completos[m-1]}</div>"
        m_h += "<table style='width:100%; font-size:11px; text-align:center; color:white;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    style = "color:white; font-weight:bold;"
                    if d in cs: style += "border:1px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:3px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style += "border:1px solid #00FF7F; border-radius:3px;"
                    m_h += f"<td><div style='{style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_h += m_h + "</table></div>"
    components.html(grid_h + "</div>", height=1050)

st.markdown("""
    <div style="text-align: center; margin-top:20px;">
        <p style="color: #FF8C00; font-size: 18px; font-weight: bold; font-style: italic;">Voz de la Tórtola, Nejapa.</p>
    </div>
    """, unsafe_allow_html=True)
