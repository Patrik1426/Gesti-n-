from rest_framework import serializers
from .models import Obra

class ObraSerializer(serializers.ModelSerializer):
    # Campos calculados
    semaforo = serializers.SerializerMethodField()
    presupuesto_final = serializers.SerializerMethodField()
    monto_ejecutado = serializers.SerializerMethodField()

    # Campos de Texto para Escalas (Sobreescribimos para mostrar texto en lugar de num)
    urgencia = serializers.SerializerMethodField()
    impacto_social = serializers.SerializerMethodField()
    alineacion_estrategica = serializers.SerializerMethodField()
    complejidad_tecnica = serializers.SerializerMethodField()
    riesgo_nivel = serializers.SerializerMethodField()
    # ... puedes agregar aquí los demás si quieres texto en todos

    # Agregamos los _num para tener el dato numérico crudo también
    urgencia_num = serializers.IntegerField(source='urgencia', read_only=True)
    riesgo_nivel_num = serializers.IntegerField(source='riesgo_nivel', read_only=True)
    # Django permite renombrar campos con 'source'

    class Meta:
        model = Obra
        fields = '__all__'

    # --- Lógica de Negocio ---
    def get_presupuesto_final(self, obj):
        return obj.presupuesto_modificado if obj.presupuesto_modificado > 0 else obj.anteproyecto_total

    def get_monto_ejecutado(self, obj):
        presupuesto = self.get_presupuesto_final(obj)
        return presupuesto * (obj.avance_financiero_pct / 100.0)

    def get_semaforo(self, obj):
        if obj.riesgo_nivel >= 4: return "ROJO"
        if obj.avance_fisico_pct < 20 and obj.urgencia >= 4: return "ROJO"
        if obj.riesgo_nivel == 3: return "AMARILLO"
        return "VERDE"

    # --- Traducción Escalas (Num -> Texto) ---
    def _to_text(self, valor):
        textos = {1: "1 - Muy Bajo", 2: "2 - Bajo", 3: "3 - Regular", 4: "4 - Alto", 5: "5 - Muy Alto"}
        return textos.get(valor, f"{valor} - Definido")

    def get_urgencia(self, obj): return self._to_text(obj.urgencia)
    def get_impacto_social(self, obj): return self._to_text(obj.impacto_social)
    def get_alineacion_estrategica(self, obj): return self._to_text(obj.alineacion_estrategica)
    def get_complejidad_tecnica(self, obj): return self._to_text(obj.complejidad_tecnica)
    def get_riesgo_nivel(self, obj): return self._to_text(obj.riesgo_nivel)