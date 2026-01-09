import pandas as pd
import numpy as np
import os
import re

# Configuration de ruta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_EXCEL = os.path.join(BASE_DIR, "data", "datos.xlsx")

def obtener_letra_excel(n):
    """Convierte un indice numérico en letra de Excel"""
    letra = ""
    n += 1
    while n > 0:
        n, resto = divmod(n - 1, 26)
        letra = chr(65 + resto) + letra
    return letra

def limpiar_monto(valor):
    """Limpia caracteres de presupuesto (Columnas 7 y 8)"""
    if valor is None or pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace(',', '').strip()
    limpio = re.sub(r'[^0-9.]', '', texto)
    try:
        return float(limpio) if limpio else 0.0
    except:
        return 0.0

def limpiar_beneficiarios(valor):
    """Limpieza para la columna AK (36) - Beneficiarios en Miles"""
    if valor is None or pd.isna(valor): return 0.0
    texto = str(valor).replace(',', '').strip()
    match = re.search(r'(\d+\.?\d*)', texto)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0.0
    return 0.0

def limpiar_porcentaje(valor):
    """Limpia columnas de avance. Si es vacio, devuelve 0.0"""
    if valor is None or pd.isna(valor): 
        return 0.0
    if isinstance(valor, (int, float)): 
        return float(valor)
    
    texto = str(valor).replace('%', '').strip()
    try:
        return float(texto) if texto else 0.0
    except:
        return 0.0

def evaluar_puntos_riesgo(valor):
    """Asigna peso numérico a las categorías de riesgo (Verde=1, Amarillo=2, Rojo=3)"""
    if valor is None or pd.isna(valor): return 0
    v = str(valor).lower().strip()
    if "rojo" in v: return 3
    if "amarillo" in v: return 2
    if "verde" in v: return 1
    return 0

def normalizar_estatus(valor):
    """Estandariza el estado de la obra (Columna 45)"""
    if valor is None or pd.isna(valor):
        return "En Ejecución"
    v = str(valor).lower().strip()
    if "complet" in v or "terminad" in v or "finaliz" in v:
        return "Completo"
    return "En Ejecución"

def categorizar_prioridad(valor):
    """Transforma Col 23 (1-5) en Texto"""
    try:
        v = int(valor)
        if v >= 5: return "CRÍTICA"
        if v == 4: return "ALTA"
        if v == 3: return "MEDIA"
        return "BAJA"
    except:
        return "BAJA"

def ejecutar_reporte_completo():
    if not os.path.exists(PATH_EXCEL):
        print(f"Error: No se encontró el archivo en: {PATH_EXCEL}")
        return

    try:
        df = pd.read_excel(PATH_EXCEL, engine='openpyxl')
        
        # 1. Mapa de Columnas (Opcional, para auditoría)
        print("\n" + "=" * 160)
        print(" MAPA DE COLUMNAS DETECTADAS")
        print("=" * 160)
        columnas = df.columns.tolist()
        for idx in range(len(columnas)):
            print(f"[{idx:2}] Col {obtener_letra_excel(idx):<3} : {str(columnas[idx])[:38]}")

        print("-" * 160)
        print(" DETALLE INTEGRAL DE PROYECTOS")
        print("-" * 160)

        # Variables de control
        total_obras = 0
        total_presupuesto_mdp = 0.0
        total_beneficiarios_miles = 0.0
        obras_viables = 0
        obras_en_revision = 0
        conteo_completos = 0
        conteo_ejecucion = 0
        suma_avances_fisicos = 0.0
        suma_avances_mixtos = 0.0

        # Header alineado (185 caracteres)
        header = f"{'Fila':<5} | {'ID (A)':<8} | {'Nombre del Proyecto (B)':<35} | {'Prio (X)':<10} | {'Monto MDP':<12} | {'Benef (k)':<10} | {'Av. Mix %':<10} | {'Estatus (AT)':<15} | {'Puntos':<8} | {'Situación'}"
        print(header)
        print("-" * 160)

        for i in range(len(df)):
            fila = df.iloc[i]
            
            # Limpieza de Identificación y Nombres (Protección contra saltos de línea)
            id_obra = str(fila.iloc[0]).strip()
            nombre_raw = str(fila.iloc[1]) if not pd.isna(fila.iloc[1]) else "SIN NOMBRE"
            nombre_proyecto = nombre_raw.replace('\n', ' ').replace('\r', ' ').strip()[:33]
            
            # Prioridad, Presupuesto y Beneficiarios
            prioridad_txt = categorizar_prioridad(fila.iloc[23])
            m_mod = limpiar_monto(fila.iloc[7])
            m_ant = limpiar_monto(fila.iloc[8])
            presupuesto_final = m_mod if m_mod > 0 else m_ant
            benef_miles = limpiar_beneficiarios(fila.iloc[36])
            
            # Avances (Físico AR / Financiero AS)
            av_fisico = limpiar_porcentaje(fila.iloc[43])
            av_financiero = limpiar_porcentaje(fila.iloc[44])
            avance_mixto = (av_fisico + av_financiero) / 2
            
            # Estatus y Riesgo
            estatus_raw = str(fila.iloc[45]) if not pd.isna(fila.iloc[45]) else "En Ejecución"
            estatus_obra = normalizar_estatus(estatus_raw.replace('\n', '').strip())
            
            puntos_totales = sum([evaluar_puntos_riesgo(fila.iloc[j]) for j in range(29, 34)])
            
            # Clasificación de Situación
            if puntos_totales > 5:
                estatus_critico = "REVISION"
                obras_en_revision += 1
            else:
                estatus_critico = "VIABLE"
                obras_viables += 1

            if estatus_obra == "Completo": 
                conteo_completos += 1
            else: 
                conteo_ejecucion += 1
            
            # Acumuladores
            total_obras += 1
            total_presupuesto_mdp += presupuesto_final
            total_beneficiarios_miles += benef_miles
            suma_avances_fisicos += av_fisico
            suma_avances_mixtos += avance_mixto

            # Impresión de fila alineada
            print(f"{i+2:<5} | {id_obra:<8} | {nombre_proyecto:<35} | {prioridad_txt:<10} | {presupuesto_final:<12,.2f} | {benef_miles:<10,.2f} | {avance_mixto:<10.1f}% | {estatus_obra:<15} | {puntos_totales:<8} | {estatus_critico}")

        # Cálculos de Promedio
        av_fisico_global = suma_avances_fisicos / total_obras if total_obras > 0 else 0
        av_mixto_global = suma_avances_mixtos / total_obras if total_obras > 0 else 0

        # --- RESUMEN FINAL MEZCLADO (TU FORMATO FAVORITO) ---
        print("=" * 160)
        print(" RESUMEN CONSOLIDADO DEL PLAN OPERATIVO")
        print("-" * 160)
        print(f" TOTAL DE PROYECTOS PROCESADOS : {total_obras}")
        print(f" AVANCE FÍSICO PROMEDIO GLOBAL : {av_fisico_global:.2f}%")
        print(f" AVANCE MIXTO PROMEDIO (F+F)   : {av_mixto_global:.2f}%")
        print(f" PROYECTOS COMPLETADOS (AT)    : {conteo_completos}")
        print(f" PROYECTOS EN EJECUCIÓN (AT)   : {conteo_ejecucion}")
        print(f" PROYECTOS VIABLES (<= 5 pts)  : {obras_viables}")
        print(f" PROYECTOS EN REVISION CRÍTICA (> 5 pts): {obras_en_revision}")
        print(f" TOTAL BENEFICIARIOS IMPACTADOS: {total_beneficiarios_miles:,.2f} MILES")
        print(f" INVERSION TOTAL PROGRAMADA    : {total_presupuesto_mdp:,.2f} MDP")
        print("=" * 160 + "\n")

    except Exception as e:
        print(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    ejecutar_reporte_completo()