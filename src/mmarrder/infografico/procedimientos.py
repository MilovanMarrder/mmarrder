from .base import Infografico
from ..utils.transformaciones import normalizar_periodos, filtrar_periodo


class Procedimientos(Infografico):
    """Producción de pacientes nuevos"""

    def produccion_periodo(self, año=None, mes=None,hoja='Procedimientos Quirúrgicos'):
        df = self._leer_tabla_base(
            hoja=hoja,
            valor_final='Totales',
            palabra='ugc'
            )

        columna_id = df.columns[0]  # Especialidad
        df = normalizar_periodos(df, columna_id)
        df = filtrar_periodo(df, año, mes)
        df = df[~df[columna_id].str.contains('brigada', case=False, na=False)]
        df.columns = ['periodo', 'ugc', 'produccion']
        return df
