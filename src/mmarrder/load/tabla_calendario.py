import pandas as pd
import holidays


def tabla_calendario(
    fecha_inicio = "2025-01-01",
    fecha_fin = "2026-12-31"
    
):

    """
    Genera una tabla calendario con información temporal y laboral
    para Honduras dentro de un rango de fechas.

    La función crea un DataFrame con un registro por día, incluyendo
    información del día de la semana, identificación de fines de semana,
    feriados oficiales de Honduras y una bandera que indica si el día
    es laboral.

    Parameters
    ----------
    fecha_inicio : str or datetime-like, default='2025-01-01'
        Fecha inicial del calendario. Puede proporcionarse como cadena
        en formato ISO ('YYYY-MM-DD') o como objeto datetime compatible
        con `pandas.to_datetime`.

    fecha_fin : str or datetime-like, default='2026-12-31'
        Fecha final del calendario. Puede proporcionarse como cadena
        en formato ISO ('YYYY-MM-DD') o como objeto datetime compatible
        con `pandas.to_datetime`.

    Returns
    -------
    pandas.DataFrame
        DataFrame con un registro por día en el rango especificado,
        que contiene las siguientes columnas:

        - ``fecha`` : datetime64
            Fecha completa con tipo datetime.
        - ``dia_semana`` : str
            Nombre abreviado del día de la semana en español
            (Lun, Mar, Mié, Jue, Vie, Sáb, Dom).
        - ``es_fin_semana`` : bool
            Indica si la fecha corresponde a sábado o domingo.
        - ``fecha_date`` : date
            Fecha convertida a tipo `date`, útil para comparaciones
            con calendarios externos o librerías de feriados.
        - ``es_feriado`` : bool
            Indica si la fecha corresponde a un feriado oficial
            en Honduras.
        - ``nombre_feriado`` : str or None
            Nombre del feriado si aplica, de lo contrario `None`.
        - ``dia_laboral`` : bool
            Indica si el día es laboral, definido como un día que
            no es fin de semana ni feriado.

    Notes
    -----
    La identificación de feriados se realiza utilizando la librería
    `holidays`, específicamente el calendario oficial de Honduras.

    Examples
    --------
    >>> calendario = tabla_calendario("2026-01-01", "2026-01-10")
    >>> calendario.head()

            fecha dia_semana  es_fin_semana  es_feriado nombre_feriado  dia_laboral
    0 2026-01-01        Jue          False        True      Año Nuevo        False
    1 2026-01-02        Vie          False       False           None         True
    2 2026-01-03        Sáb           True       False           None        False
    """



    # Años contenidos en el rango
    years = list(range(
        pd.to_datetime(fecha_inicio).year,
        pd.to_datetime(fecha_fin).year + 1
    ))

    hn_holidays = holidays.Honduras(years=years)

    calendario = pd.DataFrame({
        "fecha": pd.date_range(fecha_inicio, fecha_fin, freq="D")
    })

    calendario["dia_semana"] = calendario["fecha"].dt.day_name().str[:3]
    
    calendario["dia_semana"] = calendario["dia_semana"].map({
        'Wed':'Mié',
        'Thu':'Jue',
        'Fri':'vie',
        'Sat':'Sáb',
        'Sun':'Dom',
        'Mon':'Lun',
        'Tue':'Mar'
    })

    calendario["es_fin_semana"] = calendario["fecha"].dt.weekday >= 5

    calendario["fecha_date"] = calendario["fecha"].dt.date

    calendario["es_feriado"] = calendario["fecha_date"].isin(hn_holidays)

    calendario["nombre_feriado"] = calendario["fecha_date"].map(hn_holidays)

    calendario["dia_laboral"] = (~calendario["es_fin_semana"]) & (~calendario["es_feriado"])

    return calendario