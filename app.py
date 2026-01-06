# ... (Partes anteriores del código se mantienen igual) ...

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
                # CÁLCULO MEJORADO PARA ADAR II
                diff_days = (dia_c - esp["aviv_1"]).days
                num_mes_heb = round(diff_days / 29.5)
                
                if num_mes_heb < 0: # Meses antes de Aviv (final del año anterior)
                    nombre_heb = "Adar II" if num_mes_heb == -1 else "Mes anterior"
                elif num_mes_heb >= 12: # El mes 13 después de Aviv
                    nombre_heb = "Adar II"
                else:
                    nombre_heb = meses_hebreos[num_mes_heb]
                
                celebs.append((dia_c, nombre_heb))
        if f_dt.month == mes: fases[f_dt.day] = yi
    return celebs, conjs, fases

# ... (El resto del código del calendario se mantiene igual) ...
