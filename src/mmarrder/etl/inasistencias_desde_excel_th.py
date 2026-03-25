import pandas as pd
from mmarrder.load import tabla_calendario


def _etl_vacaciones_por_tipo(
    ruta_archivo: str,
    nombre_hoja: str,
    fecha_minima: str = "2025-01-01",
    fecha_maxima: str = "2100-01-01",
    vacaciones_profilacticas: bool = False
) -> pd.DataFrame:
    """
    Realiza el proceso de ETL para el DataFrame de vacaciones ordinarias.
    Desde el archivo de Excel.
    """
    if not vacaciones_profilacticas:
        
        df = pd.read_excel(
            ruta_archivo,
            sheet_name=nombre_hoja,
            skiprows=5,
            usecols=[0, 1, 2, 5, 6, 7, 8],
            dtype={"cod": str},
        )
        df['tipo_vacaciones'] = 'ordinarias'
    else:
        df = pd.read_excel(
            ruta_archivo,
            sheet_name=nombre_hoja,
            skiprows=5,
            usecols=[0, 1, 2, 5, 10, 11, 12],
            dtype={"cod": str},
        )
        df['tipo_vacaciones'] = 'profilacticas'
        
    df.columns = [
        "id_empleado",
        "nombre",
        "depto",
        "fecha",
        "fecha_inicio",
        "fecha_fin",
        "dias_vacaciones",
        "tipo_vacaciones"
    ]
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df = df[
        (df["fecha_inicio"].notna())
        & (df["fecha_inicio"] >= fecha_minima)
        & (df["fecha_inicio"] <= fecha_maxima)
    ]
    
    
    return df


def vacaciones_etl(
    ruta_archivo: str,
    nombre_hoja: str,
    fecha_minima: str = "2025-01-01",
    fecha_maxima: str = "2100-01-01",
) -> pd.DataFrame:
    """
    Realiza el proceso de ETL para el DataFrame de vacaciones ordinarias y profilácticas.
    Desde el archivo de Excel.
    """
    df_ordinarias = _etl_vacaciones_por_tipo(
        ruta_archivo, nombre_hoja, fecha_minima, fecha_maxima, vacaciones_profilacticas=False
    )
    
    df_profilacticas = _etl_vacaciones_por_tipo(
        ruta_archivo, nombre_hoja, fecha_minima, fecha_maxima, vacaciones_profilacticas=True
    )
    
    df_final = pd.concat([df_ordinarias, df_profilacticas], ignore_index=True)
    
    df_final["fecha_fin_dentro_periodo"] = df_final.apply(
        lambda row: fecha_maxima if row["fecha_fin"] > fecha_maxima else row["fecha_fin"],
        axis=1,
        )

    df_final["dias_inasistencia_en_periodo"] = df_final.apply(
            lambda row: tabla_calendario(fecha_inicio=row["fecha_inicio"], fecha_fin=row["fecha_fin_dentro_periodo"]).dias_laborales(),
            axis=1,
        )
    
    df_final["dias_inasistencia_en_periodo"] = df_final.apply(
        lambda row: row['dias_inasistencia_en_periodo'] if row['dias_vacaciones'] >= 1 else row['dias_vacaciones'],
        axis=1
    )
    df_final.drop(columns=['dias_vacaciones'], inplace=True)
    return df_final

def permisos_etl(
    ruta_archivo_permiso,
    sheet_name_permisos,
    fecha_minima="2026-01-01",
    fecha_maxima="2100-12-31",
):
    df = pd.read_excel(
        ruta_archivo_permiso,
        sheet_name=sheet_name_permisos,
        skiprows=1,
        dtype={"COD. EMPL": str},
    )
    # renombro columnas para estandarizar con el proceso de vacaciones
    df.columns = [
        "area_gestion",
        "id_empleado",
        "nombre",
        "puesto",
        "fecha_permiso",
        "fecha_inicio",
        "fecha_fin",
        "dias_permiso",
        "permiso_hora_inicio",
        "permiso_hora_fin",
        "horas_permiso",
        "tipo_permiso",
        "observaciones",
        "a",
        "b",
        "c",
        "d",
    ]
    # Filtrar solo los permisos que tengan fecha de inicio dentro del periodo
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df = df[
        (df["fecha_inicio"].notna())
        & (df["fecha_inicio"] >= fecha_minima)
        & (df["fecha_inicio"] <= fecha_maxima)
    ]

    df["fecha_inicio"] = pd.to_datetime(
        df["fecha_inicio"], errors="coerce"
    )
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")
    
    df["fecha_fin_dentro_periodo"] = df.apply(
        lambda row: (
            fecha_maxima if row["fecha_fin"] > fecha_maxima else row["fecha_fin"]
        ),
        axis=1,
    )

    df["dias_inasistencia_en_periodo"] = df.apply(
        lambda row: tabla_calendario(
            fecha_inicio=row["fecha_inicio"], fecha_fin=row["fecha_fin_dentro_periodo"]
        ).dias_laborales(),
        axis=1,
    )

    df["dias_inasistencia_en_periodo"] = df.apply(
        lambda row: (
            row["dias_inasistencia_en_periodo"]
            if (row["dias_permiso"] >= 1) or (pd.isna(row["dias_permiso"]))
            else row["dias_permiso"]
        ),
        axis=1,
    )
    df["inicio_datetime"] = pd.to_datetime(
        df["fecha_permiso"].astype(str)
        + " "
        + df["permiso_hora_inicio"].astype(str),
        errors="coerce",
    )

    df["fin_datetime"] = pd.to_datetime(
        df["fecha_permiso"].astype(str)
        + " "
        + df["permiso_hora_fin"].astype(str),
        errors="coerce",
    )
    df["horas_decimal"] = (
        df["fin_datetime"] - df["inicio_datetime"]
    ).dt.total_seconds() / 3600
    df["dias_inasistencia_en_periodo"] = df.apply(
        lambda row: (
            row["horas_decimal"] / 8
            if (row["dias_inasistencia_en_periodo"] == 1)
            and (pd.notna(row["permiso_hora_inicio"]))
            else row["dias_inasistencia_en_periodo"]
        ),
        axis=1,
    )
    df = df[
        [
            "area_gestion",
            "id_empleado",
            "nombre",
            "puesto",
            "fecha_permiso",
            "fecha_inicio",
            "fecha_fin",
            "fecha_fin_dentro_periodo",
            "tipo_permiso",
            "dias_inasistencia_en_periodo",
        ]
    ]

    return df