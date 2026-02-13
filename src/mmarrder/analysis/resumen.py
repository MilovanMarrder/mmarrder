from __future__ import annotations

import pandas as pd


def resumen_anual(df: pd.DataFrame, col_fecha: str = "periodo", col_produccion: str = "produccion") -> pd.Series:
    """
    Agrupa por año y suma producción.
    Devuelve una Serie indexada por año.
    """
    out = df.copy()
    out[col_fecha] = pd.to_datetime(out[col_fecha], errors="coerce")
    out = out.dropna(subset=[col_fecha])

    out["año"] = out[col_fecha].dt.year
    return out.groupby("año")[col_produccion].sum()
