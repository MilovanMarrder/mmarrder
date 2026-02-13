from .base import Infografico
from ..utils.transformaciones import normalizar_periodos, filtrar_periodo



class PacientesNuevos(Infografico):
    """Producción de pacientes nuevos"""

    def produccion_periodo(self, año=None, mes=None, hoja='Pacientes Nuevos'):
        df = self._leer_tabla_base(
            hoja=hoja
            )

        columna_id = df.columns[0]  # Especialidad
        df = normalizar_periodos(df, columna_id)

        return filtrar_periodo(df, año, mes)
