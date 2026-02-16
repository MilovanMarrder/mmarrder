from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

from mmarrder.io.excel_tables import ExcelTableExportOptions, export_to_excel_with_tables

from .data_loader import (
    get_schedule_from_folder,
    get_schedule_from_file,
    get_all_surgery_info_from_file,
    get_all_surgery_info_from_folder,
)


def _ensure_df(x: Any) -> pd.DataFrame:
    if isinstance(x, pd.DataFrame):
        return x
    raise TypeError(f"Se esperaba DataFrame, recibido: {type(x)}")


def get_dataframes(
    source: str | Path,
    *,
    mode: str = "folder",
) -> dict[str, pd.DataFrame]:
    """
    Devuelve un dict de dataframes normalizado para el ETL programacion_qx.

    Parameters
    ----------
    source:
        Ruta a archivo o carpeta.
    mode:
        "folder" o "file"
    """
    source = str(source)

    if mode not in {"folder", "file"}:
        raise ValueError("mode debe ser 'folder' o 'file'")

    if mode == "folder":
        df_schedule = _ensure_df(get_schedule_from_folder(source))
        df_surgeries = _ensure_df(get_all_surgery_info_from_folder(source))
    else:
        df_schedule = _ensure_df(get_schedule_from_file(source))
        df_surgeries = _ensure_df(get_all_surgery_info_from_file(source))

    return {
        "Schedule": df_schedule,
        "Surgery Info": df_surgeries,
    }


def export_excel(
    source: str | Path,
    output_xlsx: str | Path,
    *,
    mode: str = "folder",
    table_style: str = "TableStyleLight13",
    freeze_panes: str | None = "A2",
    autofit_columns: bool = True,
) -> str:
    """
    Exporta a Excel con tablas estructuradas los dataframes de programacion_qx.
    """
    dfs = get_dataframes(source, mode=mode)

    options = ExcelTableExportOptions(
        table_style=table_style,
        freeze_panes=freeze_panes,
        autofit_columns=autofit_columns,
    )

    return export_to_excel_with_tables(dfs, str(output_xlsx), options=options)
