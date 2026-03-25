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

def permisos_etl(ruta_archivo, sheet_name,fecha_corte = "2026-01-31"):
    df = pd.read_excel(ruta_archivo, sheet_name=sheet_name, skiprows=1, dtype={'COD. EMPL':str})
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
        "d"
    ]
    # Trabajaré primero los diarios y luegos los permisos por horas
    df_diarios = df[df['fecha_inicio'].notna()].copy()
    df_diarios['fecha_inicio'] = pd.to_datetime(df_diarios['fecha_inicio'], errors='coerce')
    df_diarios['fecha_fin'] = pd.to_datetime(df_diarios['fecha_fin'], errors='coerce')
    fecha_corte = pd.to_datetime(fecha_corte)
    df_diarios["dias_permiso_hasta_fecha_corte"] = df_diarios.apply(
        lambda fila: len(
            pd.bdate_range(
                start=fila["fecha_inicio"],
                end=fecha_corte if pd.isna(fila["fecha_fin"]) 
                                else min(fila["fecha_fin"], fecha_corte)
            )
        ),
        axis=1
    )

    df_diarios["tipo_inasistencia"] = "permiso diario"
    puestos_seis_horas = [
        "MEDICO ESPECIALISTA",
        "MEDICO ESPECIALISTA EN CUIDADOS INTENSIVOS",
        "CIRUJANO PEDIATRICO",
        "INMUNOLOGIA",
        "NEUROLOGA",
        "MEDICO GENERAL",
    ]
    df_diarios['horas_decimal'] = df_diarios.apply(
        lambda fila: 6*fila['dias_permiso_hasta_fecha_corte'] if fila['puesto'] in puestos_seis_horas else 8*fila['dias_permiso_hasta_fecha_corte'],
        axis=1
    )

    df_horas = df[df['permiso_hora_inicio'].notna()].copy()

    df_horas["inicio_datetime"] = pd.to_datetime(
        df_horas["fecha_permiso"].astype(str) + " " + df_horas["permiso_hora_inicio"].astype(str)
    )

    df_horas["fin_datetime"] = pd.to_datetime(
        df_horas["fecha_permiso"].astype(str) + " " + df_horas["permiso_hora_fin"].astype(str)
    )
    df_horas["horas_decimal"] = (
        (df_horas["fin_datetime"] - df_horas["inicio_datetime"])
        .dt.total_seconds() / 3600
    )


    cols_a_concatenar = [
        "area_gestion",
        "id_empleado",
        "nombre",
        "puesto",
        "fecha_permiso",
        "tipo_permiso",
        "horas_decimal",
    ]
    horas_permiso = pd.concat(
        [df_diarios[cols_a_concatenar], df_horas[cols_a_concatenar]], ignore_index=True
    )
    
    

    return horas_permiso