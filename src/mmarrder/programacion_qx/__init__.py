from .data_loader import (
    get_schedule_from_folder,
    get_schedule_from_file,
    get_all_surgery_info_from_file,
    get_all_surgery_info_from_folder,
)

from .pipeline import (
    get_dataframes,
    export_excel,
)

from ..analysis.resumen import (
    resumen_anual_tabla,
)

__all__ = [
    # API directa (tu lógica existente)
    "get_schedule_from_folder",
    "get_schedule_from_file",
    "get_all_surgery_info_from_file",
    "get_all_surgery_info_from_folder",
    # API nivel pipeline (para UI/export)
    "get_dataframes",
    "export_excel",
    "resumen_anual_tabla",
]

from .kpis import (
    horas_por_quirofano,
    horas_por_dia_semana,
    horas_por_medico,
    cirugias_por_dia,
    duracion_promedio_cirugia,
    ocupacion_por_quirofano,
)

__all__ += [
    "horas_por_quirofano",
    "horas_por_dia_semana",
    "horas_por_medico",
    "cirugias_por_dia",
    "duracion_promedio_cirugia",
    "ocupacion_por_quirofano",
]
