from __future__ import annotations

import pandas as pd

from mmarrder.analysis import resumen_anual
from .pipeline import get_dataframes


def resumen_infografico_anual(ruta_infografico: str) -> dict[str, pd.Series]:
    """
    Retorna resúmenes anuales por dataset:
      {"Consulta Externa": Serie_por_año, ...}
    """
    dfs = get_dataframes(ruta_infografico)
    return {nombre: resumen_anual(df) for nombre, df in dfs.items()}


def resumen_infografico_anual_tabla(ruta_infografico: str) -> pd.DataFrame:
    """
    Retorna una tabla (DataFrame) con columnas: dataset, anio, produccion
    """
    dfs = get_dataframes(ruta_infografico)

    piezas: list[pd.DataFrame] = []
    for nombre, df in dfs.items():
        s = resumen_anual(df)
        tmp = (
            s.rename("produccion")
            .reset_index()
            .rename(columns={"año": "anio"})
        )
        tmp["dataset"] = nombre
        piezas.append(tmp)

    if not piezas:
        return pd.DataFrame(columns=["dataset", "anio", "produccion"])

    return pd.concat(piezas, ignore_index=True)[["dataset", "anio", "produccion"]]
