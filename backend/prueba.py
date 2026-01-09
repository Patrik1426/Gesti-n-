# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import numpy as np
# import os
# import re

# app = FastAPI(title="API Obras Públicas - POA 2025")

# # Habilitar CORS para que el Frontend pueda conectarse
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PATH_EXCEL = os.path.join(BASE_DIR, "data", "datos.xlsx")

# # --- Funciones de Limpieza y Normalización ---
# def limpiar_monto(valor):
#     if valor is None or pd.isna(valor): return 0.0
#     if isinstance(valor, (int, float)): return float(valor)
#     texto = str(valor).replace(',', '').strip()
#     limpio = re.sub(r'[^0-9.]', '', texto)
#     try: return float(limpio) if limpio else 0.0
#     except: return 0.0

# def limpiar_beneficiarios(valor):
#     if valor is None or pd.isna(valor): return 0.0
#     texto = str(valor).replace(',', '').strip()
#     match = re.search(r'(\d+\.?\d*)', texto)
#     if match:
#         try: return float(match.group(1))
#         except: return 0.0
#     return 0.0

# def limpiar_porcentaje(valor):
#     """Limpia columna AR (43). Vacío = 0.0%"""
#     if valor is None or pd.isna(valor): return 0.0
#     if isinstance(valor, (int, float)): return float(valor)
#     texto = str(valor).replace('%', '').strip()
#     try: return float(texto) if texto else 0.0
#     except: return 0.0

# def evaluar_puntos_riesgo(valor):
#     if valor is None or pd.isna(valor): return 0
#     v = str(valor).lower().strip()
#     if "rojo" in v: return 3
#     if "amarillo" in v: return 2
#     if "verde" in v: return 1
#     return 0

# def normalizar_estatus(valor):
#     """Normaliza columna AT (45). Vacío = En Ejecución"""
#     if valor is None or pd.isna(valor): return "En Ejecución"
#     v = str(valor).lower().strip()
#     if "complet" in v or "terminad" in v or "finaliz" in v:
#         return "Completo"
#     return "En Ejecución"

# # --- Endpoint Principal ---
# @app.get("/api/proyectos")

# async def get_proyectos():
#     if not os.path.exists(PATH_EXCEL):
#         raise HTTPException(status_code=404, detail="Archivo Excel no encontrado")
    
#     try:
#         df = pd.read_excel(PATH_EXCEL, engine='openpyxl')
#         proyectos_lista = []

#         # Variables para el resumen (KPIs)
#         total_presupuesto = 0.0
#         total_beneficiarios = 0.0
#         # Agregamos esta variable para sumar el total ejecutado global
#         total_ejecutado = 0.0

        
#         obras_revision = 0
#         obras_viables = 0
#         conteo_completos = 0
#         conteo_ejecucion = 0
#         suma_avances = 0.0

#         for i in range(len(df)):
#             fila = df.iloc[i]
            
#             # 1. Procesar Presupuesto
#             modificado = limpiar_monto(fila.iloc[7])
#             anteproyecto = limpiar_monto(fila.iloc[8])
#             presupuesto_final = modificado if modificado > 0 else anteproyecto
            
#             # 2. Procesar Avance
#             avance_valor = limpiar_porcentaje(fila.iloc[43]) # Ej: 50.0
            
#             # --- CORRECCIÓN IMPORTANTE: CALCULAR MONTO EJECUTADO ---
#             # Si tienes un avance del 50% y 1 millón de presupuesto => Ejecutado = 500k
#             monto_ejecutado = presupuesto_final * (avance_valor / 100.0)
            
#             # 3. Resto de procesamientos
#             puntos_totales = sum([evaluar_puntos_riesgo(fila.iloc[j]) for j in range(29, 34)])
#             estatus_riesgo = "REVISION" if puntos_totales > 5 else "VIABLE"
#             estatus_obra = normalizar_estatus(fila.iloc[45])
#             benef_miles = limpiar_beneficiarios(fila.iloc[36])

#             # Actualizar contadores globales
#             total_presupuesto += presupuesto_final
#             total_ejecutado += monto_ejecutado  # Sumamos al acumulado
#             total_beneficiarios += benef_miles
#             suma_avances += avance_valor
            
#             if estatus_riesgo == "REVISION": obras_revision += 1
#             else: obras_viables += 1
            
#             if estatus_obra == "Completo": conteo_completos += 1
#             else: conteo_ejecucion += 1

#             # Construir objeto individual del proyecto
#             proyectos_lista.append({
#                 "id": str(fila.iloc[0]),
#                 "nombre": str(fila.iloc[1]) if not pd.isna(fila.iloc[1]) else "Sin Nombre",
#                 "presupuesto": presupuesto_final,
#                 "ejecutado": monto_ejecutado, 
#                 "beneficiarios": benef_miles,
#                 "avance": avance_valor,
#                 "estatus_obra": estatus_obra,
#                 "puntos_riesgo": puntos_totales,
#                 "estatus_riesgo": estatus_riesgo,
#                 "fuente": "MODIFICADO" if modificado > 0 else "ANTEPROYECTO"
#             })

#         # Cálculo de promedios finales
#         total_obras = len(df)
#         avance_promedio = round(suma_avances / total_obras, 2) if total_obras > 0 else 0

#         return {
#             "detalle": proyectos_lista,
#             "resumen": {
#                 "total_proyectos": total_obras,
#                 "avance_promedio_global": avance_promedio,
#                 "presupuesto_total_mdp": round(total_presupuesto, 2),
#                 "beneficiarios_total_miles": round(total_beneficiarios, 2),
#                 "obras_completas": conteo_completos,
#                 "obras_en_ejecucion": conteo_ejecucion,
#                 "obras_viables": obras_viables,
#                 "obras_revision": obras_revision
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

### Versión Mejorada del Código ###
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import os
# import re

# app = FastAPI(title="API Obras Públicas - POA 2025")

# # Habilitar CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PATH_EXCEL = os.path.join(BASE_DIR, "data", "datos.xlsx")

# # --- Funciones de Limpieza y Normalización ---
# def limpiar_monto(valor):
#     if valor is None or pd.isna(valor):
#         return 0.0
#     if isinstance(valor, (int, float)):
#         return float(valor)
#     texto = str(valor).replace(',', '').strip()
#     limpio = re.sub(r'[^0-9.]', '', texto)
#     try:
#         return float(limpio) if limpio else 0.0
#     except:
#         return 0.0

# def limpiar_beneficiarios(valor):
#     if valor is None or pd.isna(valor):
#         return 0.0
#     texto = str(valor).replace(',', '').strip()
#     match = re.search(r'(\d+\.?\d*)', texto)
#     if match:
#         try:
#             return float(match.group(1))
#         except:
#             return 0.0
#     return 0.0

# def limpiar_porcentaje(valor):
#     if valor is None or pd.isna(valor):
#         return 0.0
#     if isinstance(valor, (int, float)):
#         return float(valor)
#     texto = str(valor).replace('%', '').strip()
#     try:
#         return float(texto) if texto else 0.0
#     except:
#         return 0.0

# def calcular_prioridad(urgencia):
#     """Convierte urgencia (1-5) en texto para el frontend"""
#     try:
#         val = int(urgencia)
#         if val == 5: return "critica"
#         if val == 4: return "alta"
#         if val == 3: return "media"
#         return "baja"
#     except:
#         return "baja"

# def mapear_estatus(texto):
#     """Normaliza el estatus de la obra para el frontend"""
#     if pd.isna(texto):
#         return "planificado"
#     t = str(texto).lower().strip()
#     if "complet" in t or "terminad" in t or "finaliz" in t:
#         return "completado"
#     if "ejecu" in t or "proceso" in t or "construcción" in t:
#         return "en_ejecucion"
#     if "retras" in t:
#         return "retrasado"
#     if "riesgo" in t:
#         return "en_riesgo"
#     return "planificado"

# def evaluar_riesgo_simple(valor_riesgo):
#     """Determina si la obra necesita revisión según nivel de riesgo (col AA)"""
#     riesgo = limpiar_monto(valor_riesgo)
#     return "REVISION" if riesgo >= 4 else "VIABLE"

# # --- Endpoint Principal ---
# @app.get("/api/proyectos")
# async def get_proyectos():
#     if not os.path.exists(PATH_EXCEL):
#         raise HTTPException(status_code=404, detail="Archivo Excel no encontrado")
    
#     try:
#         df = pd.read_excel(PATH_EXCEL, engine='openpyxl')
#         proyectos_lista = []

#         # Variables para KPIs globales
#         total_presupuesto_mdp = 0.0
#         total_ejecutado_mdp = 0.0
#         total_beneficiarios = 0.0
#         suma_avances_fisicos = 0.0

#         conteo_estatus = {
#             "completado": 0, "en_ejecucion": 0, "retrasado": 0,
#             "en_riesgo": 0, "planificado": 0
#         }
#         obras_viables = 0
#         obras_revision = 0

#         for i in range(len(df)):
#             fila = df.iloc[i]

#             # --- Presupuesto (Col H - índice 7: Modificado o Anteproyecto) ---
#             modificado = limpiar_monto(fila.iloc[7])
#             anteproyecto = limpiar_monto(fila.iloc[8])
#             presupuesto_mdp = modificado if modificado > 0 else anteproyecto
#             presupuesto_pesos = presupuesto_mdp * 1_000_000  # Para frontend

#             # --- Avances ---
#             avance_fisico = limpiar_porcentaje(fila.iloc[43])      # Col AR
#             avance_financiero = limpiar_porcentaje(fila.iloc[44]) # Col AS

#             # --- Monto ejecutado (basado en avance financiero) ---
#             monto_ejecutado_pesos = presupuesto_pesos * (avance_financiero / 100.0)
#             monto_ejecutado_mdp = monto_ejecutado_pesos / 1_000_000

#             # --- Otros campos clave ---
#             estatus_obra = mapear_estatus(fila.iloc[45])           # Col AT
#             prioridad = calcular_prioridad(fila.iloc[23])          # Col X - Urgencia
#             beneficiarios = limpiar_beneficiarios(fila.iloc[36])    # Col AK
#             estatus_riesgo = evaluar_riesgo_simple(fila.iloc[26])  # Col AA

#             # --- Fechas: Real > Programada ---
#             fecha_inicio = str(fila.iloc[41]) if not pd.isna(fila.iloc[41]) else str(fila.iloc[38])
#             fecha_fin = str(fila.iloc[42]) if not pd.isna(fila.iloc[42]) else str(fila.iloc[39])

#             # --- Acumular para KPIs ---
#             total_presupuesto_mdp += presupuesto_mdp
#             total_ejecutado_mdp += monto_ejecutado_mdp
#             total_beneficiarios += beneficiarios
#             suma_avances_fisicos += avance_fisico

#             conteo_estatus[estatus_obra] += 1
#             if estatus_riesgo == "REVISION":
#                 obras_revision += 1
#             else:
#                 obras_viables += 1

#             # --- Construcción del proyecto individual ---
#             proyectos_lista.append({
#                 "id": str(fila.iloc[0]),
#                 "nombre": str(fila.iloc[1]) if not pd.isna(fila.iloc[1]) else "Sin Nombre",
#                 "direccion": str(fila.iloc[2]) if not pd.isna(fila.iloc[2]) else "General",
#                 "responsable": str(fila.iloc[49]) if not pd.isna(fila.iloc[49]) else "No asignado",
#                 "ubicacion": str(fila.iloc[35]) if not pd.isna(fila.iloc[35]) else "Ubicación pendiente",

#                 "presupuesto": presupuesto_pesos,           # En pesos (para gráficos)
#                 "ejecutado": monto_ejecutado_pesos,
#                 "avance": avance_fisico,
#                 "avance_financiero": avance_financiero,

#                 "status": estatus_obra,
#                 "prioridad": prioridad,
#                 "viabilidad": "alta" if estatus_riesgo == "VIABLE" else "baja",

#                 "beneficiarios": beneficiarios,
#                 "fechaInicio": fecha_inicio,
#                 "fechaFin": fecha_fin,

#                 "descripcion": str(fila.iloc[56]) if not pd.isna(fila.iloc[56]) else "Sin descripción detallada.",

#                 "riesgos": [str(fila.iloc[52])] if not pd.isna(fila.iloc[52]) else [],
#                 "objetivos": [str(fila.iloc[57])] if not pd.isna(fila.iloc[57]) else ["Mejorar la infraestructura pública"],
#                 "indicadores": [
#                     {"nombre": "Avance Físico 2025", "actual": avance_fisico, "meta": 100, "unidad": "%"},
#                     {"nombre": "Avance Financiero", "actual": avance_financiero, "meta": 100, "unidad": "%"}
#                 ]
#             })

#         # --- Cálculo final de KPIs ---
#         total_obras = len(df)
#         avance_promedio = round(suma_avances_fisicos / total_obras, 2) if total_obras > 0 else 0

#         return {
#             "detalle": proyectos_lista,
#             "resumen": {
#                 "total_proyectos": total_obras,
#                 "avance_promedio_global": avance_promedio,
#                 "presupuesto_total_mdp": round(total_presupuesto_mdp, 2),
#                 "ejecutado_total_mdp": round(total_ejecutado_mdp, 2),
#                 "beneficiarios_total_miles": round(total_beneficiarios / 1000, 2),
#                 "obras_completas": conteo_estatus["completado"],
#                 "obras_en_ejecucion": conteo_estatus["en_ejecucion"],
#                 "obras_retrasadas": conteo_estatus["retrasado"],
#                 "obras_en_riesgo": conteo_estatus["en_riesgo"],
#                 "obras_planificadas": conteo_estatus["planificado"],
#                 "obras_viables": obras_viables,
#                 "obras_revision": obras_revision
#             }
#         }

#     except Exception as e:
#         print(f"Error al procesar el Excel: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import re

app = FastAPI(title="API Obras Públicas - POA 2025")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_EXCEL = os.path.join(BASE_DIR, "data", "datos.xlsx")

# --- Funciones de Limpieza y Normalización ---
def limpiar_monto(valor):
    if valor is None or pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).replace(',', '').strip()
    limpio = re.sub(r'[^0-9.]', '', texto)
    try:
        return float(limpio) if limpio else 0.0
    except:
        return 0.0

def limpiar_beneficiarios(valor):
    if valor is None or pd.isna(valor):
        return 0.0
    texto = str(valor).replace(',', '').strip()
    match = re.search(r'(\d+\.?\d*)', texto)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0.0
    return 0.0

def limpiar_porcentaje(valor):
    if valor is None or pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).replace('%', '').strip()
    try:
        return float(texto) if texto else 0.0
    except:
        return 0.0

def calcular_prioridad(urgencia):
    """Convierte urgencia (1-5) en texto para el frontend"""
    try:
        val = int(urgencia)
        if val == 5: return "critica"
        if val == 4: return "alta"
        if val == 3: return "media"
        return "baja"
    except:
        return "baja"

def mapear_estatus(texto):
    """Normaliza el estatus de la obra para el frontend"""
    if pd.isna(texto):
        return "planificado"
    t = str(texto).lower().strip()
    if "complet" in t or "terminad" in t or "finaliz" in t:
        return "completado"
    if "ejecu" in t or "proceso" in t or "construcción" in t:
        return "en_ejecucion"
    if "retras" in t:
        return "retrasado"
    if "riesgo" in t:
        return "en_riesgo"
    return "planificado"

def evaluar_riesgo_simple(valor_riesgo):
    """Determina si la obra necesita revisión según nivel de riesgo (col AA)"""
    riesgo = limpiar_monto(valor_riesgo)
    return "REVISION" if riesgo >= 4 else "VIABLE"

# --- Endpoint Principal ---
@app.get("/api/proyectos")
async def get_proyectos():
    if not os.path.exists(PATH_EXCEL):
        raise HTTPException(status_code=404, detail="Archivo Excel no encontrado")
    
    try:
        df = pd.read_excel(PATH_EXCEL, engine='openpyxl')
        proyectos_lista = []

        # Variables para KPIs globales
        total_presupuesto_mdp = 0.0
        total_ejecutado_mdp = 0.0
        total_beneficiarios = 0.0
        suma_avances_fisicos = 0.0

        conteo_estatus = {
            "completado": 0, "en_ejecucion": 0, "retrasado": 0,
            "en_riesgo": 0, "planificado": 0
        }
        obras_viables = 0
        obras_revision = 0

        for i in range(len(df)):
            fila = df.iloc[i]

            # --- Presupuesto (Col H - índice 7: Modificado o Anteproyecto) ---
            modificado = limpiar_monto(fila.iloc[7])
            anteproyecto = limpiar_monto(fila.iloc[8])
            presupuesto_mdp = modificado if modificado > 0 else anteproyecto
            presupuesto_pesos = presupuesto_mdp * 1_000_000  # Para frontend

            # --- Avances ---
            avance_fisico = limpiar_porcentaje(fila.iloc[43])      # Col AR
            avance_financiero = limpiar_porcentaje(fila.iloc[44]) # Col AS

            # --- Monto ejecutado (basado en avance financiero) ---
            monto_ejecutado_pesos = presupuesto_pesos * (avance_financiero / 100.0)
            monto_ejecutado_mdp = monto_ejecutado_pesos / 1_000_000

            # --- Otros campos clave ---
            estatus_obra = mapear_estatus(fila.iloc[45])           # Col AT
            prioridad = calcular_prioridad(fila.iloc[23])          # Col X - Urgencia
            beneficiarios = limpiar_beneficiarios(fila.iloc[36])    # Col AK
            estatus_riesgo = evaluar_riesgo_simple(fila.iloc[26])  # Col AA

            # --- Fechas: Real > Programada ---
            fecha_inicio = str(fila.iloc[41]) if not pd.isna(fila.iloc[41]) else str(fila.iloc[38])
            fecha_fin = str(fila.iloc[42]) if not pd.isna(fila.iloc[42]) else str(fila.iloc[39])

            # ============================================================
            # === NUEVOS CAMPOS SOLICITADOS EN EL PASO 1 ===
            # ============================================================
            nivel_riesgo = limpiar_monto(fila.iloc[26])      # Col AA (1-5)
            nivel_impacto = limpiar_monto(fila.iloc[22])     # Col W (1-5)
            nivel_viabilidad = limpiar_monto(fila.iloc[24])  # Col Y (1-5)

            problema_txt = str(fila.iloc[52]) if not pd.isna(fila.iloc[52]) else ""
            accion_txt = str(fila.iloc[53]) if not pd.isna(fila.iloc[53]) else ""

            es_retrasado = "retras" in str(fila.iloc[45]).lower()
            es_riesgo_alto = nivel_riesgo >= 4
            es_baja_viabilidad = nivel_viabilidad > 0 and nivel_viabilidad <= 2
            # ============================================================

            # --- Acumular para KPIs ---
            total_presupuesto_mdp += presupuesto_mdp
            total_ejecutado_mdp += monto_ejecutado_mdp
            total_beneficiarios += beneficiarios
            suma_avances_fisicos += avance_fisico

            conteo_estatus[estatus_obra] += 1
            if estatus_riesgo == "REVISION":
                obras_revision += 1
            else:
                obras_viables += 1

            # --- Construcción del proyecto individual ---
            proyectos_lista.append({
                "id": str(fila.iloc[0]),
                "nombre": str(fila.iloc[1]) if not pd.isna(fila.iloc[1]) else "Sin Nombre",
                "direccion": str(fila.iloc[2]) if not pd.isna(fila.iloc[2]) else "General",
                "responsable": str(fila.iloc[49]) if not pd.isna(fila.iloc[49]) else "No asignado",
                "ubicacion": str(fila.iloc[35]) if not pd.isna(fila.iloc[35]) else "Ubicación pendiente",

                "presupuesto": presupuesto_pesos,           # En pesos (para gráficos)
                "ejecutado": monto_ejecutado_pesos,
                "avance": avance_fisico,
                "avance_financiero": avance_financiero,

                "status": estatus_obra,
                "prioridad": prioridad,
                "viabilidad": "alta" if estatus_riesgo == "VIABLE" else "baja",

                "beneficiarios": beneficiarios,
                "fechaInicio": fecha_inicio,
                "fechaFin": fecha_fin,

                "descripcion": str(fila.iloc[56]) if not pd.isna(fila.iloc[56]) else "Sin descripción detallada.",

                "riesgos": [str(fila.iloc[52])] if not pd.isna(fila.iloc[52]) else [],
                "objetivos": [str(fila.iloc[57])] if not pd.isna(fila.iloc[57]) else ["Mejorar la infraestructura pública"],
                "indicadores": [
                    {"nombre": "Avance Físico 2025", "actual": avance_fisico, "meta": 100, "unidad": "%"},
                    {"nombre": "Avance Financiero", "actual": avance_financiero, "meta": 100, "unidad": "%"}
                ],

                # === NUEVOS CAMPOS AÑADIDOS ===
                "riesgo_nivel": nivel_riesgo,             # 1-5
                "impacto_social": nivel_impacto,          # 1-5
                "viabilidad_nivel": nivel_viabilidad,     # 1-5
                "problema_identificado": problema_txt,
                "accion_correctiva": accion_txt,
                "es_retrasado": es_retrasado,
                "es_riesgo_alto": es_riesgo_alto,
                "es_baja_viabilidad": es_baja_viabilidad
            })

        # --- Cálculo final de KPIs ---
        total_obras = len(df)
        avance_promedio = round(suma_avances_fisicos / total_obras, 2) if total_obras > 0 else 0

        return {
            "detalle": proyectos_lista,
            "resumen": {
                "total_proyectos": total_obras,
                "avance_promedio_global": avance_promedio,
                "presupuesto_total_mdp": round(total_presupuesto_mdp, 2),
                "ejecutado_total_mdp": round(total_ejecutado_mdp, 2),
                "beneficiarios_total_miles": round(total_beneficiarios / 1000, 2),
                "obras_completas": conteo_estatus["completado"],
                "obras_en_ejecucion": conteo_estatus["en_ejecucion"],
                "obras_retrasadas": conteo_estatus["retrasado"],
                "obras_en_riesgo": conteo_estatus["en_riesgo"],
                "obras_planificadas": conteo_estatus["planificado"],
                "obras_viables": obras_viables,
                "obras_revision": obras_revision
            }
        }

    except Exception as e:
        print(f"Error al procesar el Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)