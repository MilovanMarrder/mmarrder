from __future__ import annotations

import numpy as np
import pandas as pd


def detectar_tabla_excel(
    ruta: str,
    hoja: str,
    palabra_inicio: str = "especialidad",
) -> tuple[int, int, int | None]:
    """
    Detecta en qué fila/columna inicia una tabla dentro de una hoja Excel, buscando 'palabra_inicio'.
    Retorna: (fila_inicio, col_inicio, col_final)

    col_final es opcional (None si no se detecta).
    """
    df_temp = pd.read_excel(ruta, sheet_name=hoja, header=None)

    # Quirks específicos del infográfico
    if hoja == "Procedimientos Quirúrgicos":
        if df_temp.shape[0] > 1 and df_temp.shape[1] > 1:
            df_temp.iat[1, 1] = "ugc"
    elif hoja == "Servicios de Apoyo":
        if df_temp.shape[0] > 0 and df_temp.shape[1] > 0:
            df_temp.iat[0, 0] = ""

    mask_inicio = df_temp.astype(str).apply(
        lambda x: x.str.contains(palabra_inicio, case=False, na=False)
    )
    coords = np.where(mask_inicio)

    if coords[0].size == 0:
        raise ValueError(f"No se encontró '{palabra_inicio}' en hoja '{hoja}'.")

    fila_inicio = int(coords[0][0])
    col_inicio = int(coords[1][0])

    df_cols = pd.read_excel(ruta, sheet_name=hoja, header=fila_inicio)
    años = [c for c in df_cols.columns if isinstance(c, int)]
    año_mayor = max(años) if años else None

    col_final = None
    if año_mayor is not None:
        mask_final = df_temp.astype(str).apply(
            lambda x: x.str.contains(str(año_mayor), na=False)
        )
        coords_final = np.where(mask_final)
        if coords_final[1].size > 0:
            col_final = int(coords_final[1][0]) + 1

    return fila_inicio, col_inicio, col_final
