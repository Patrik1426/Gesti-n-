from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime, timedelta

app = FastAPI(title="Data Science Pipeline: Obras Públicas 2025")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS DE ARCHIVOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_EXCEL = os.path.join(BASE_DIR, "data", "datos.xlsx")

# --- CONFIGURACIÓN MAESTRA: ESCALAS (NUEVO) ---
CATALOGO_ESCALAS = {
    # Entrada (Texto -> Numérico)
    "muy bajo": 1, 
    "bajo": 2, 
    "regular": 3, "medio": 3, "media": 3,
    "alto": 4, "alta": 4, 
    "muy alto": 5, "muy alta": 5,
    "critico": 5, "critica": 5, "urgente": 5, "prioritario": 5,
    "rojo": 5, "amarillo": 3, "verde": 1,
    # Salida (Numérico -> Texto Estandarizado)
    1: "1 - Muy Bajo", 2: "2 - Bajo", 3: "3 - Regular", 
    4: "4 - Alto", 5: "5 - Muy Alto"
}

# --- 1. DEFINICIÓN DEL ESQUEMA DE DATOS (MAPPING 0-66) ---
COLUMN_NAMES = {
    0: "id",
    1: "programa",
    2: "area_responsable",
    3: "eje_institucional",
    4: "tipo_recurso",
    5: "concentrado_programas",
    6: "capitulo_gasto",
    7: "presupuesto_modificado",
    8: "anteproyecto_total",
    9: "meta_2025",
    10: "meta_2026",
    11: "unidad_medida",
    12: "costo_unitario",
    13: "proyecto_2025_presupuesto",
    14: "multianualidad",
    15: "tipo_obra",
    16: "alcance_territorial",
    17: "fuente_financiamiento",
    18: "etapa_desarrollo",
    19: "complejidad_tecnica",      # 1-5
    20: "impacto_social",           # 1-5
    21: "alineacion_estrategica",   # 1-5
    22: "impacto_social_nivel",     # 1-5
    23: "urgencia",                 # 1-5
    24: "viabilidad_ejecucion",     # 1-5
    25: "recursos_disponibles",     # 1-5
    26: "riesgo_nivel",             # 1-5
    27: "dependencias_nivel",       # 1-5
    28: "puntuacion_final",
    29: "viabilidad_tecnica_semaforo",
    30: "viabilidad_presupuestal_semaforo",
    31: "viabilidad_juridica_semaforo",
    32: "viabilidad_temporal_semaforo",
    33: "viabilidad_administrativa_semaforo",
    34: "alcaldias",
    35: "ubicacion_especifica",
    36: "beneficiarios_directos",
    37: "poblacion_objetivo_num",
    38: "fecha_inicio_prog",
    39: "fecha_termino_prog",
    40: "duracion_meses",
    41: "fecha_inicio_real",
    42: "fecha_termino_real",
    43: "avance_fisico_pct",
    44: "avance_financiero_pct",
    45: "estatus_general",
    46: "permisos_requeridos",
    47: "estatus_permisos",
    48: "requisitos_especificos",
    49: "responsable_operativo",
    50: "contratista",
    51: "observaciones",
    52: "problemas_identificados",
    53: "acciones_correctivas",
    54: "ultima_actualizacion",
    55: "problema_resuelve",
    56: "solucion_ofrece",
    57: "beneficio_ciudadania",
    58: "dato_destacable",
    59: "alineacion_gobierno",
    60: "poblacion_perfil",
    61: "relevancia_comunicacional",
    62: "hitos_comunicacionales",
    63: "mensajes_clave",
    64: "estrategia_comunicacion",
    65: "control_captura",
    66: "control_notas"
}

# --- 2. FUNCIONES DE LIMPIEZA AVANZADA ---

def clean_money_vectorized(series):
    return series.astype(str).str.replace(r'[$,]', '', regex=True).apply(
        lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0.0
    )

def clean_percentage_vectorized(series):
    return series.astype(str).str.replace('%', '').str.strip().apply(
        lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0.0
    )

# [MEJORA] Función inteligente de escalas
def interpretar_escala_flexible(valor, diccionario=CATALOGO_ESCALAS):
    """Retorna tupla: (Valor Numérico, Texto Formateado)"""
    if pd.isna(valor):
        return (1, diccionario[1]) # Default
    
    val_str = str(valor).strip().lower()
    nivel_detectado = 1 
    encontrado = False

    # 1. Buscar número explícito
    match = re.search(r'\b([1-5])\b', val_str)
    if match:
        nivel_detectado = int(match.group(1))
        encontrado = True
    
    # 2. Buscar palabras clave
    if not encontrado:
        text_keys = sorted([k for k in diccionario.keys() if isinstance(k, str)], key=len, reverse=True)
        for key in text_keys:
            if key in val_str:
                nivel_detectado = diccionario[key]
                encontrado = True
                break
    
    nivel_detectado = max(1, min(5, nivel_detectado))
    return (nivel_detectado, diccionario.get(nivel_detectado, f"{nivel_detectado} - Definido"))

def clean_text(series):
    return series.astype(str).str.strip().replace('nan', 'No especificado').replace('None', 'No especificado')

def parse_excel_date(val):
    if pd.isna(val): return None
    if isinstance(val, (int, float)):
        try:
            return (datetime(1899, 12, 30) + timedelta(days=val)).strftime('%Y-%m-%d')
        except:
            return None
    val_str = str(val).strip()
    try:
        return pd.to_datetime(val_str).strftime('%Y-%m-%d')
    except:
        return val_str

# --- 3. ENDPOINT DE EXTRACCIÓN Y LIMPIEZA ---

@app.get("/api/data/clean")
async def get_clean_data():
    if not os.path.exists(PATH_EXCEL):
        raise HTTPException(status_code=404, detail="Archivo Excel no encontrado en data/datos.xlsx")
    
    try:
        # A. EXTRACCIÓN (Load)
        df_raw = pd.read_excel(PATH_EXCEL, header=None, engine='openpyxl')
        df = df_raw.iloc[1:].reset_index(drop=True)
        
        df.rename(columns=COLUMN_NAMES, inplace=True)
        
        # Filtrar solo columnas mapeadas existentes
        cols_to_keep = [v for k, v in COLUMN_NAMES.items() if v in df.columns]
        df = df[cols_to_keep]

        # B. LIMPIEZA Y TRANSFORMACIÓN (Transform)
        
        # 1. Numéricos Financieros
        df['presupuesto_modificado'] = clean_money_vectorized(df['presupuesto_modificado'])
        df['anteproyecto_total'] = clean_money_vectorized(df['anteproyecto_total'])
        df['costo_unitario'] = clean_money_vectorized(df['costo_unitario'])
        
        df['presupuesto_final'] = np.where(
            df['presupuesto_modificado'] > 0, 
            df['presupuesto_modificado'], 
            df['anteproyecto_total']
        )

        # 2. Porcentajes
        df['avance_fisico_pct'] = clean_percentage_vectorized(df['avance_fisico_pct'])
        df['avance_financiero_pct'] = clean_percentage_vectorized(df['avance_financiero_pct'])
        
        # 3. Escalas Cualitativas (1-5) [MEJORA]
        # Lista de columnas que son escalas
        escalas = [
            'urgencia', 'impacto_social_nivel', 'viabilidad_ejecucion', 
            'recursos_disponibles', 'riesgo_nivel', 'dependencias_nivel',
            'complejidad_tecnica', 'alineacion_estrategica','impacto_social'
        ]
        
        for col in escalas:
            if col in df.columns:
                # Aplicamos la función inteligente
                resultado = df[col].apply(lambda x: interpretar_escala_flexible(x))
                # Guardamos el numérico en columna auxiliar (para cálculos)
                df[f'{col}_num'] = resultado.apply(lambda x: x[0])
                # Guardamos el texto formateado en la original (para visualización)
                df[col] = resultado.apply(lambda x: x[1])

        # 4. Textos (Limpieza General)
        text_cols = ['programa', 'tipo_obra', 'estatus_general', 'problema_resuelve', 'solucion_ofrece']
        for col in text_cols:
            if col in df.columns:
                df[col] = clean_text(df[col])

        # 5. Fechas
        date_cols = ['fecha_inicio_prog', 'fecha_termino_prog', 'fecha_inicio_real', 'fecha_termino_real']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].apply(parse_excel_date)

        # 6. Feature Engineering
        df['monto_ejecutado'] = df['presupuesto_final'] * (df['avance_financiero_pct'] / 100.0)
        
        # Semaforización automatizada [MEJORA]
        # Usamos las columnas _num porque las originales ahora tienen texto
        conditions = [
            (df.get('riesgo_nivel_num', 0) >= 4) | ((df['avance_fisico_pct'] < 20) & (df.get('viabilidad_ejecucion_num', 0) <= 2)),
            (df.get('riesgo_nivel_num', 0) == 3),
        ]
        choices = ['ROJO', 'AMARILLO']
        df['semaforo'] = np.select(conditions, choices, default='VERDE')

        # C. CARGA / RESPUESTA (Load)
        df_final = df.where(pd.notnull(df), None)
        records = df_final.to_dict(orient='records')
        
        return {
            "metadata": {
                "total_registros": len(df),
                "timestamp": datetime.now().isoformat(),
                "columnas_procesadas": len(df.columns)
            },
            "data": records
        }

    except Exception as e:
        print(f"Error en ETL Pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)