from django.db import models

class Obra(models.Model):
    # --- Identificadores y Clasificación (Cols 0-6) ---
    id_excel = models.IntegerField(null=True)            # col 0: id
    programa = models.TextField(null=True, blank=True)   # col 1
    area_responsable = models.CharField(max_length=255, null=True, blank=True) # col 2
    eje_institucional = models.CharField(max_length=255, null=True, blank=True) # col 3
    tipo_recurso = models.CharField(max_length=255, null=True, blank=True)      # col 4
    concentrado_programas = models.CharField(max_length=255, null=True, blank=True) # col 5
    capitulo_gasto = models.CharField(max_length=100, null=True, blank=True)    # col 6

    # --- Financieros y Metas (Cols 7-14) ---
    presupuesto_modificado = models.FloatField(default=0)  # col 7
    anteproyecto_total = models.FloatField(default=0)      # col 8
    meta_2025 = models.FloatField(default=0)               # col 9
    meta_2026 = models.FloatField(default=0)               # col 10
    unidad_medida = models.CharField(max_length=100, null=True, blank=True) # col 11
    costo_unitario = models.FloatField(default=0)          # col 12
    proyecto_2025_presupuesto = models.FloatField(null=True, blank=True) # col 13
    multianualidad = models.CharField(max_length=50, null=True, blank=True) # col 14

    # --- Características de la Obra (Cols 15-18) ---
    tipo_obra = models.CharField(max_length=255, null=True, blank=True)          # col 15
    alcance_territorial = models.TextField(null=True, blank=True)                # col 16
    fuente_financiamiento = models.CharField(max_length=255, null=True, blank=True) # col 17
    etapa_desarrollo = models.CharField(max_length=255, null=True, blank=True)   # col 18

    # --- Escalas 1-5 (Cols 19-27) - Guardamos NUMEROS ---
    complejidad_tecnica = models.IntegerField(default=1)    # col 19
    impacto_social = models.IntegerField(default=1)         # col 20
    alineacion_estrategica = models.IntegerField(default=1) # col 21
    impacto_social_nivel = models.IntegerField(default=1)   # col 22
    urgencia = models.IntegerField(default=1)               # col 23
    viabilidad_ejecucion = models.IntegerField(default=1)   # col 24
    recursos_disponibles = models.IntegerField(default=1)   # col 25
    riesgo_nivel = models.IntegerField(default=1)           # col 26
    dependencias_nivel = models.IntegerField(default=1)     # col 27

    # --- Semáforos y Viabilidad (Cols 28-33) ---
    puntuacion_final = models.FloatField(null=True, blank=True) # col 28
    viabilidad_tecnica_semaforo = models.CharField(max_length=50, null=True, blank=True)       # col 29
    viabilidad_presupuestal_semaforo = models.CharField(max_length=50, null=True, blank=True)  # col 30
    viabilidad_juridica_semaforo = models.CharField(max_length=50, null=True, blank=True)      # col 31
    viabilidad_temporal_semaforo = models.CharField(max_length=50, null=True, blank=True)      # col 32
    viabilidad_administrativa_semaforo = models.CharField(max_length=50, null=True, blank=True)# col 33

    # --- Ubicación y Beneficiarios (Cols 34-37) ---
    alcaldias = models.TextField(null=True, blank=True)            # col 34
    ubicacion_especifica = models.TextField(null=True, blank=True) # col 35
    beneficiarios_directos = models.CharField(max_length=255, null=True, blank=True) # col 36
    poblacion_objetivo_num = models.CharField(max_length=255, null=True, blank=True) # col 37

    # --- Fechas (Cols 38-42) ---
    fecha_inicio_prog = models.DateField(null=True, blank=True)   # col 38
    fecha_termino_prog = models.DateField(null=True, blank=True)  # col 39
    duracion_meses = models.CharField(max_length=100, null=True, blank=True) # col 40
    fecha_inicio_real = models.DateField(null=True, blank=True)   # col 41
    fecha_termino_real = models.DateField(null=True, blank=True)  # col 42

    # --- Avances y Estatus (Cols 43-47) ---
    avance_fisico_pct = models.FloatField(default=0)      # col 43
    avance_financiero_pct = models.FloatField(default=0)  # col 44
    estatus_general = models.CharField(max_length=255, null=True, blank=True) # col 45
    permisos_requeridos = models.TextField(null=True, blank=True) # col 46
    estatus_permisos = models.TextField(null=True, blank=True)    # col 47

    # --- Detalles Adicionales (Cols 48-66) ---
    requisitos_especificos = models.TextField(null=True, blank=True) # col 48
    responsable_operativo = models.CharField(max_length=255, null=True, blank=True) # col 49
    contratista = models.CharField(max_length=255, null=True, blank=True) # col 50
    observaciones = models.TextField(null=True, blank=True)       # col 51
    problemas_identificados = models.TextField(null=True, blank=True) # col 52
    acciones_correctivas = models.TextField(null=True, blank=True) # col 53
    ultima_actualizacion = models.DateField(null=True, blank=True) # col 54
    problema_resuelve = models.TextField(null=True, blank=True)   # col 55
    solucion_ofrece = models.TextField(null=True, blank=True)     # col 56
    beneficio_ciudadania = models.TextField(null=True, blank=True) # col 57
    dato_destacable = models.TextField(null=True, blank=True)     # col 58
    alineacion_gobierno = models.TextField(null=True, blank=True) # col 59
    poblacion_perfil = models.TextField(null=True, blank=True)    # col 60
    
    # Comunicacion
    relevancia_comunicacional = models.TextField(null=True, blank=True) # col 61
    hitos_comunicacionales = models.TextField(null=True, blank=True)    # col 62
    mensajes_clave = models.TextField(null=True, blank=True)            # col 63
    estrategia_comunicacion = models.TextField(null=True, blank=True)   # col 64
    control_captura = models.TextField(null=True, blank=True)           # col 65
    control_notas = models.TextField(null=True, blank=True)             # col 66

    def __str__(self):
        return str(self.programa)[:50]