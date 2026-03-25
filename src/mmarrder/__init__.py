"""
mmarrder: librería personal para Data Analysis, ETL y Reporting.

Estructura recomendada:
- mmarrder.io        -> IO genérico (Excel, archivos, etc.)
- mmarrder.transform -> transformaciones genéricas (fechas, periodos, etc.)
- mmarrder.analysis  -> resúmenes, agregaciones
- mmarrder.infografico -> lógica específica del ETL "Infográfico"
- mmarrder.etl      -> lógica específica del ETL "General"
"""

__all__ = ["__version__"]

__version__ = "0.1.7"
