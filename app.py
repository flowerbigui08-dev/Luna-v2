import streamlit as st
import streamlit.components.v1 as components
from skyfield import api, almanac
from skyfield.api import wgs84
from datetime import datetime, timedelta
import pytz
import calendar

# 1. CONFIGURACIÓN Y ESTADO
st.set_page_config(page_title="Luna SV", layout="wide")
tz_sv = pytz.timezone('America/El_Salvador')
hoy_sv = datetime.now(tz_sv)

dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses_completos = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
color_gris = "#2c303c"

if 'anio_v' not in st.session_state: st.session_state.anio_v = hoy_sv.year
if 'mes_v' not in st.session_state: st.session_state.mes_v = hoy_sv.month

# FUNCIONES DE CAMBIO INSTANTÁNEO
def cambiar_mes(delta):
    nueva_v = st.session_state.mes_v + delta
    if nueva_v > 12:
        st.session_state.mes_v = 1
        st.session_state.anio_v += 1
    elif nueva_v < 1:
        st.session_state.mes_v = 12
        st.session_state.anio_v -= 1
    else:
        st.session_state.mes_v = nueva_v

def cambiar_anio(delta):
    st.session_state.anio_v += delta

# 2. ESTILOS CSS (Ajuste especial para Celular)
st.markdown(f"""
    <style>
    h1 {{ text-align: center; color: #FF8C00; font-size: 24px; margin-bottom: 5px; }}
    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; }}
    
    /* Visor Compacto para Celular */
    .visor-flechas {{
        display: flex;
        align-items: center;
        justify-content: center;
        background: {color_gris};
        color: white;
        font-weight: bold;
        font-size: 14px;
        height: 40px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    
    /* Forzar botones pequeños y pegados */
    div.stButton > button {{
        width: 100% !important;
        padding: 0px !important;
        height: 40px !important;
        font-size: 18px !important;
    }}
    
    .label-mini {{
        text-align: center;
        color: #FF8C00;
        font-size: 11px;
        font-weight: bold;
        margin-bottom: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌙 Calendario Lunar</h1>", unsafe_allow_html=True)

tab_mes, tab_anio = st.tabs(["📅 Mensual", "🗓️ Anual"])

ts = api.load.timescale()
eph = api.load('de421.bsp')

with tab_mes:
    # FILA DE NAVEGACIÓN (Diseño ultra-compacto)
    c_anio, c_mes = st.columns(2)
    
    with c_anio:
        st.markdown("<p class='label-mini'>AÑO</p>", unsafe_allow_html=True)
        ba1, ba2, ba3 = st.columns([1,2,1])
        ba1.button("◀️", key="a1", on_click=cambiar_anio, args=(-1,))
        ba2.markdown(f"<div class='visor-flechas'>{st.session_state.anio_v}</div>", unsafe_allow_html=True)
        ba3.button("▶️", key="a2", on_click=cambiar_anio, args=(1,))
            
    with c_mes:
        st.markdown("<p class='label-mini'>MES</p>", unsafe_allow_html=True)
        bm1, bm2, bm3 = st.columns([1,2,1])
        bm1.button("◀️", key="m1", on_click=cambiar_mes, args=(-1,))
        nombre_mes_vis = meses_completos[st.session_state.mes_v-1][:4] + "." if len(meses_completos[st.session_state.mes_v-1]) > 5 else meses_completos[st.session_state.mes_v-1]
        bm2.markdown(f"<div class='visor-flechas'>{nombre_mes_vis}</div>", unsafe_allow_html=True)
        bm3.button("▶️", key="m2", on_click=cambiar_mes, args=(1,))

    anio, mes_id = st.session_state.anio_v, st.session_state.mes_v

    # Cálculos Astronómicos
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

    # Render del Calendario (Ajustado para que no se desborde)
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

                fila += f"""<td style='padding:2px;'><div style='{b_style} height:60px; border-radius:8px; padding:4px; box-sizing:border-box;'>
                        <div style='color:white; font-weight:bold; font-size:12px;'>{dia}</div>
                        <div style='text-align:center; font-size:20px;'>{ico}</div></div></td>"""
        filas_html += fila + "</tr>"

    components.html(f"""
    <div style='font-family:sans-serif;'>
        <h4 style='text-align:center; color:#FF8C00; margin:5px;'>{meses_completos[mes_id-1]} {anio}</h4>
        <table style='width:100%; table-layout:fixed; border-collapse:collapse;'>
            <tr style='color:#FF4B4B; text-align:center; font-weight:bold; font-size:12px;'><td>D</td><td>L</td><td>M</td><td>M</td><td>J</td><td>V</td><td>S</td></tr>
            {filas_html}
        </table>
    </div>""", height=420)

    # Info Boxes
    st.markdown(f"""
    <div style="padding:12px; border-radius:12px; background:{color_gris}; color:white; border:1px solid rgba(255,255,255,0.1); margin-top:10px;">
        <p style="color:#FF8C00; font-weight:bold; margin-bottom:8px; font-size:15px;">Próxima Conjunción:</p>
        <p style="margin:0; font-size:14px;">📍 El Salvador: <b>{info_sv}</b></p>
        <p style="margin:5px 0 0 0; font-size:14px;">🌍 Tiempo UTC: <b>{info_utc}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab_anio:
    anio_f = st.session_state.anio_v
    st.markdown(f"<h3 style='text-align:center; color:#FF8C00;'>Año {anio_f}</h3>", unsafe_allow_html=True)
    grid_h = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:5px; width:100%;'>"
    for m in range(1, 13):
        # (Cálculos de año completo omitidos por brevedad, se mantienen iguales)
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

        m_h = f"<div style='background:{color_gris}; padding:5px; border-radius:8px; border:1px solid #4a4e5a;'>"
        m_h += f"<div style='color:#FF8C00; font-weight:bold; text-align:center; font-size:12px;'>{meses_completos[m-1][:3]}</div>"
        m_h += "<table style='width:100%; font-size:9px; text-align:center; color:white;'>"
        for sem in calendar.Calendar(6).monthdayscalendar(anio_f, m):
            m_h += "<tr>"
            for d in sem:
                if d == 0: m_h += "<td></td>"
                else:
                    style = ""
                    if d in cs: style = "border:1px solid #FF8C00; background:rgba(255,140,0,0.2); border-radius:2px;"
                    if d == hoy_sv.day and m == hoy_sv.month and anio_f == hoy_sv.year: style = "border:1px solid #00FF7F;"
                    m_h += f"<td><div style='{style}'>{d}</div></td>"
            m_h += "</tr>"
        grid_h += m_h + "</table></div>"
    components.html(grid_h + "</div>", height=850)

st.markdown(f"<p style='text-align:center; color:grey; font-size:11px; margin-top:15px;'>Voz de la Tórtola, Nejapa.</p>", unsafe_allow_html=True)
