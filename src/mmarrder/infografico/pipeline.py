from __future__ import annotations

from pathlib import Path

from mmarrder.io.excel_tables import ExcelTableExportOptions, export_to_excel_with_tables

# Imports relativos dentro del paquete infografico
from .hospitalizacion import Hospitalizacion
from .servicios_apoyo import ServiciosApoyo
from .consulta_externa import ConsultaExterna
from .pacientes_nuevos import PacientesNuevos
from .procedimientos import Procedimientos


def _get_dataframes_dict(ruta_infografico: str | Path):
    ruta = str(ruta_infografico)

    df_hosp = Hospitalizacion(ruta).produccion_periodo()
    df_apoyo = ServiciosApoyo(ruta).produccion_periodo()
    df_ce = ConsultaExterna(ruta).produccion_periodo()
    df_nuevos = PacientesNuevos(ruta).produccion_periodo()
    df_qx = Procedimientos(ruta).produccion_periodo()

    return {
        "Pacientes Nuevos": df_nuevos,
        "Consulta Externa": df_ce,
        "Servicios de Apoyo": df_apoyo,
        "Procedimientos": df_qx,
        "Hospitalizacion": df_hosp,
    }


def from_path_to_excel_with_tables(
    ruta_infografico: str | Path,
    nombre_archivo_exportado: str | Path,
    *,
    table_style: str = "TableStyleLight13",
    freeze_panes: str | None = "A2",
    autofit_columns: bool = True,
) -> str:
    """
    Ejecuta el pipeline del infográfico y exporta a Excel con tablas estructuradas.
    Retorna la ruta del archivo generado.
    """
    options = ExcelTableExportOptions(
        table_style=table_style,
        freeze_panes=freeze_panes,
        autofit_columns=autofit_columns,
    )

    return export_to_excel_with_tables(
        _get_dataframes_dict(ruta_infografico),
        str(nombre_archivo_exportado),
        options=options,
    )
