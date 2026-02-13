from __future__ import annotations

import numpy as np
import pandas as pd

DICT_MESES = {
    "ENE": "01",
    "FEB": "02",
    "MAR": "03",
    "ABR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AGO": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DIC": "12",
}


def recortar_por_ultima_linea(df: pd.DataFrame, valor: str = "TOTAL", col_name: str | None = None) -> pd.DataFrame:
    """
    Recorta el DF hasta la fila donde aparezca 'valor' (incluye la fila del valor si no es TOTAL).
    Si valor == 'TOTAL', corta antes de la fila TOTAL (como tu lógica original).
    """
    if col_name is None:
        serie = df.iloc[:, 0].astype(str).str.upper()
    else:
        serie = df.loc[:, col_name].astype(str).str.upper()

    mask = serie.str.contains(valor, case=False, na=False)

    if not mask.any():
        return df

    idx = mask.idxmax()  # primer match

    if valor.upper() == "TOTAL":
        return df.loc[: idx - 1] if isinstance(idx, int) else df.iloc[: mask.argmax()]

    return df.loc[:idx]


def normalizar_periodos(df: pd.DataFrame, columna_id: str) -> pd.DataFrame:
    """
    Convierte un DF ancho con meses/años en formato largo con:
      [periodo, columna_id, produccion]

    Requiere que las columnas contengan meses tipo 'ENE', 'FEB', etc y/o enteros para años.
    """
    out = df.melt(id_vars=columna_id, var_name="mes", value_name="produccion")

    out["año"] = out["mes"].apply(lambda x: np.nan if isinstance(x, str) else str(x))
    out["mes_txt"] = out["mes"].astype(str).str[:3].str.upper()
    out["mes"] = out["mes_txt"].map(DICT_MESES)
    out["año"] = out["año"].bfill()

    out["periodo"] = out["año"] + "-" + out["mes"] + "-01"
    out["periodo"] = pd.to_datetime(out["periodo"], errors="coerce")
    out["produccion"] = pd.to_numeric(out["produccion"], errors="coerce").fillna(0)

    out = out[[ "periodo", columna_id, "produccion" ]].dropna(subset=["periodo"])
    return out


def filtrar_periodo(df: pd.DataFrame, año: int | None = None, mes: int | None = None, col_periodo: str = "periodo") -> pd.DataFrame:
    """
    Filtra por año/mes sobre una columna datetime (default 'periodo').
    """
    if col_periodo not in df.columns:
        raise KeyError(f"No existe la columna '{col_periodo}' en el DataFrame.")

    if año is not None and mes is not None:
        return df[(df[col_periodo].dt.year == año) & (df[col_periodo].dt.month == mes)]

    if año is not None:
        return df[df[col_periodo].dt.year == año]

    return df
