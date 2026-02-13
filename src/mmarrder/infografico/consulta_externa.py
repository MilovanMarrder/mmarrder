from .base import Infografico
from mmarrder.transform import normalizar_periodos, recortar_por_ultima_linea, filtrar_periodo
from .transform import normalizar_periodos_consulta_externa




class ConsultaExterna(Infografico):
    """Producción de pacientes nuevos"""

    def produccion_periodo(self, año=None, mes=None,hoja='Consultas Externas'):
        df = self._leer_tabla_base(
            hoja=hoja,
            incluir_valor_final=True,
            valor_final='Maritza Betancourt', 
            columnas_valor_final='Médico'
            )

        columna_id = df.columns[0:2]  # Especialidad, y medicos
        df = normalizar_periodos_consulta_externa(df, columna_id)
        df.columns = ['periodo','especialidad', 'medico', 'produccion']
        return filtrar_periodo(df, año, mes)
    