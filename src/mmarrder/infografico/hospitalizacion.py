from .base import Infografico
from ..utils.transformaciones import normalizar_periodos, filtrar_periodo



class Hospitalizacion(Infografico):
    """Producción de pacientes nuevos"""

    def produccion_periodo(self, año=None, mes=None,hoja='Hospitalización'):
        df = self._leer_tabla_base(
            hoja=hoja,
            palabra="Hospitalización Total",
            valor_final='Días Paciente',
            incluir_valor_final = True,
            columnas_valor_final = 'Hospitalización Total'
            )

        columna_id = df.columns[0]  # columna inicial
        df = normalizar_periodos(df, columna_id)
        return filtrar_periodo(df, año, mes)