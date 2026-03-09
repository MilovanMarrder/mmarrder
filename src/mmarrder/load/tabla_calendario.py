import pandas as pd
import holidays
from datetime import date


class tabla_calendario:
    """
    Clase que genera y encapsula una tabla calendario con información
    temporal y laboral para Honduras.

    Permite construir el calendario por rango de fechas o por mes/año,
    y expone métodos utilitarios sobre el período resultante.

    Parameters
    ----------
    fecha_inicio : str or datetime-like, optional
        Fecha inicial del calendario (formato ISO 'YYYY-MM-DD').
        Se ignora si se especifica `mes`.
    fecha_fin : str or datetime-like, optional
        Fecha final del calendario (formato ISO 'YYYY-MM-DD').
        Se ignora si se especifica `mes`.
    mes : int, optional
        Número de mes (1-12). Si se especifica, el calendario abarca
        todo ese mes. Por defecto usa el mes actual.
    anio : int, optional
        Año del mes. Solo aplica cuando se usa `mes`.
        Por defecto usa el año actual.

    Examples
    --------
    >>> # Por mes (año actual)
    >>> tabla_calendario(mes=7).dias_laborales()
    23

    >>> # Por mes y año específico
    >>> tabla_calendario(mes=8, anio=2027).dias_laborales()

    >>> # Por rango de fechas (comportamiento original)
    >>> tabla_calendario(fecha_inicio="2025-01-01", fecha_fin="2025-03-31").df
    """

    _DIAS_ES = {
        "Mon": "Lun",
        "Tue": "Mar",
        "Wed": "Mié",
        "Thu": "Jue",
        "Fri": "Vie",
        "Sat": "Sáb",
        "Sun": "Dom",
    }

    def __init__(
        self,
        fecha_inicio=None,
        fecha_fin=None,
        mes: int = None,
        anio: int = None,
    ):
        # Resolver rango según parámetros recibidos
        if mes is not None:
            anio_efectivo = anio if anio is not None else date.today().year
            fecha_inicio, fecha_fin = self._rango_mes(mes, anio_efectivo)
        else:
            if fecha_inicio is None:
                fecha_inicio = "2025-01-01"
            if fecha_fin is None:
                fecha_fin = "2026-12-31"

        self._fecha_inicio = pd.to_datetime(fecha_inicio)
        self._fecha_fin = pd.to_datetime(fecha_fin)
        self.df = self._construir()

    # ------------------------------------------------------------------
    # Construcción interna
    # ------------------------------------------------------------------

    @staticmethod
    def _rango_mes(mes: int, anio: int):
        """Devuelve (fecha_inicio, fecha_fin) para el mes/año indicados."""
        inicio = pd.Timestamp(year=anio, month=mes, day=1)
        fin = inicio + pd.offsets.MonthEnd(0)
        return inicio, fin

    def _construir(self) -> pd.DataFrame:
        years = list(range(self._fecha_inicio.year, self._fecha_fin.year + 1))
        hn_holidays = holidays.Honduras(years=years)

        df = pd.DataFrame({
            "fecha": pd.date_range(self._fecha_inicio, self._fecha_fin, freq="D")
        })

        df["dia_semana"] = (
            df["fecha"].dt.day_name().str[:3].map(self._DIAS_ES)
        )
        df["es_fin_semana"] = df["fecha"].dt.weekday >= 5
        df["fecha_date"] = df["fecha"].dt.date
        df["es_feriado"] = df["fecha_date"].isin(hn_holidays)
        df["nombre_feriado"] = df["fecha_date"].map(hn_holidays)
        df["dia_laboral"] = (~df["es_fin_semana"]) & (~df["es_feriado"])

        return df

    # ------------------------------------------------------------------
    # Métodos utilitarios
    # ------------------------------------------------------------------

    def dias_laborales(self) -> int:
        """Cantidad de días laborales en el período."""
        return int(self.df["dia_laboral"].sum())

    def dias_feriados(self) -> int:
        """Cantidad de feriados oficiales en el período."""
        return int(self.df["es_feriado"].sum())

    def dias_fin_semana(self) -> int:
        """Cantidad de días de fin de semana en el período."""
        return int(self.df["es_fin_semana"].sum())

    def total_dias(self) -> int:
        """Total de días en el período."""
        return len(self.df)

    def feriados(self) -> pd.DataFrame:
        """
        Devuelve un DataFrame con solo los feriados del período.

        Returns
        -------
        pd.DataFrame
            Columnas: fecha, dia_semana, nombre_feriado
        """
        return (
            self.df[self.df["es_feriado"]][["fecha", "dia_semana", "nombre_feriado"]]
            .reset_index(drop=True)
        )
    

    def dia_inicio_periodo(self) -> str:
        """Retorna el Día de la semana que inicia el periodo."""
        fecha_min = self.df['fecha'].min()
        dia_semana = fecha_min.strftime('%A')  # Retorna el nombre del día de la semana
        return dia_semana

    def dia_fin_periodo(self) -> str:
        """Retorna el Día de la semana que finaliza el periodo."""
        fecha_max = self.df['fecha'].max()
        dia_semana = fecha_max.strftime('%A')  # Retorna el nombre del día de la semana
        return dia_semana

    def resumen(self) -> pd.Series:
        """
        Devuelve un resumen con los principales conteos del período.

        Returns
        -------
        pd.Series
        """
        return pd.Series({
            "fecha_inicio":    self._fecha_inicio.date(),
            "fecha_fin":       self._fecha_fin.date(),
            "total_dias":      self.total_dias(),
            "dias_laborales":  self.dias_laborales(),
            "fines_de_semana": self.dias_fin_semana(),
            "feriados":        self.dias_feriados(),
            "dia_inicio":      self.dia_inicio_periodo(),
            "dia_fin":         self.dia_fin_periodo(),
        })

    # ------------------------------------------------------------------
    # Representación
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"tabla_calendario("
            f"{self._fecha_inicio.date()} → {self._fecha_fin.date()}, "
            f"{self.total_dias()} días, "
            f"{self.dias_laborales()} laborales)"
        )