from datetime import datetime
from pathlib import Path
from enum import Enum

class FormatoFecha(Enum):
    """Opciones de formato de fecha para la nomenclatura de archivos."""
    MES_AÑO = "%Y%m"                        # Ejemplo: 202604 (Útil para reportes mensuales)
    COMPACTO = "%Y%m%d"                     # Ejemplo: 20260406
    COMPACTO_HORA = "%Y%m%d_hr%H%M"         # Ejemplo: 20260406_hr0856
    COMPACTO_HORA_SEGUNDO = "%Y%m%d_hr%H%M%S"   # Ejemplo: 20260406_085614 (Nota: el formato strftime no incluye segundos aquí, revisar si se desea %H%M%S)


def generar_ruta_salida(
    nombre_base: str, 
    extension: str = "xlsx", 
    ruta_directorio: str | Path = r'data/processed', 
    formato: FormatoFecha = FormatoFecha.COMPACTO_HORA,
    fecha_al_inicio: bool = True
) -> Path:
    """
    Genera una ruta de archivo estandarizada, limpia y con marca de tiempo.

    Esta función facilita la exportación de conjuntos de datos y reportes, asegurando 
    que los nombres de los archivos no contengan espacios, estén en minúsculas y 
    mantengan un estándar cronológico para evitar la sobrescritura accidental y 
    mejorar la organización en el sistema de archivos.

    Args:
        nombre_base (str): Nombre descriptivo del archivo. Los espacios se 
            convertirán automáticamente en guiones bajos y el texto a minúsculas.
            Ej: 'Demanda por Periodo' -> 'demanda_por_periodo'.
        extension (str, opcional): Extensión del archivo de salida, con o sin 
            punto inicial. Por defecto es "xlsx".
        ruta_directorio (str | Path, opcional): Directorio donde se guardará 
            el archivo. Por defecto es 'data/processed'.
        formato (FormatoFecha, opcional): Nivel de granularidad para la marca 
            de tiempo, utilizando los valores de la clase FormatoFecha. 
            Por defecto es FormatoFecha.COMPACTO_HORA.
        fecha_al_inicio (bool, opcional): Define la posición de la fecha en el 
            nombre del archivo. Si es True, el formato será 'fecha_nombre.ext'. 
            Si es False, será 'nombre_fecha.ext'. Por defecto es True.

    Returns:
        Path: Un objeto Path absoluto o relativo listo para ser utilizado en 
            funciones de guardado (ej. `df.to_excel(ruta)` o `df.to_csv(ruta)`).

    Examples:
        >>> # Generar ruta para un reporte mensual de demanda
        >>> ruta = generar_ruta_salida(
        ...     nombre_base="Demanda Pacientes", 
        ...     formato=FormatoFecha.MES_AÑO
        ... )
        >>> print(ruta)
        data/processed/202604_demanda_pacientes.xlsx

        >>> # Generar ruta para un extracto de programación de quirófanos
        >>> ruta_q = generar_ruta_salida(
        ...     nombre_base="Programacion Cirugias Etapa 1",
        ...     extension=".csv",
        ...     formato=FormatoFecha.COMPACTO
        ... )
        >>> print(ruta_q)
        data/processed/20260406_programacion_cirugias_etapa_1.csv
    """
    # Aseguramos que la ruta sea un objeto Path
    directorio = Path(ruta_directorio)
    
    # Formateamos la extensión para que siempre tenga un solo punto
    ext = f".{extension.lstrip('.')}"
    
    # Obtenemos el string de la fecha actual según el formato elegido
    fecha_str = datetime.now().strftime(formato.value)
    
    # Limpiamos el nombre base (minúsculas y sin espacios)
    nombre_limpio = nombre_base.strip().lower().replace(" ", "_")
    
    # Construimos el nombre final
    if fecha_al_inicio:
        nombre_final = f"{fecha_str}_{nombre_limpio}{ext}"
    else:
        nombre_final = f"{nombre_limpio}_{fecha_str}{ext}"
        
    return directorio / nombre_final