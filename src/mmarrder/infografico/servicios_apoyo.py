from .base import Infografico
from mmarrder.transform import normalizar_periodos, recortar_por_ultima_linea, filtrar_periodo




class ServiciosApoyo(Infografico):
    """Producción de pacientes nuevos"""

    def produccion_periodo(self, año=None, mes=None,hoja='Servicios de Apoyo'):
        df = self._leer_tabla_base(
            palabra="Servicios", 
            hoja=hoja
            )

        columna_id = df.columns[0]  # columna inicial
        df = normalizar_periodos(df, columna_id)
        df = df[df['Servicios']!='Holter']
        return filtrar_periodo(df, año, mes)
