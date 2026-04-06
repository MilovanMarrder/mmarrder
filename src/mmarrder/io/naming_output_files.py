from datetime import datetime
from pathlib import Path
from typing import Literal

def generar_ruta_salida(
    nombre_base: str, 
    extension: str = "xlsx", 
    ruta_directorio: str | Path = r'data/processed', 
    formato: Literal["mes_año", "compacto", "hora", "segundo"] = "hora",
    fecha_al_inicio: bool = True,
    notificar: bool = True
) -> Path:
    """
    Genera una ruta de archivo estandarizada con marca de tiempo y la imprime en consola.

    Args:
        nombre_base (str): Nombre descriptivo del archivo. Se limpia automáticamente 
            (minúsculas y guiones bajos).
        extension (str, opcional): Extensión del archivo. Por defecto "xlsx".
        ruta_directorio (str | Path, opcional): Carpeta destino. Por defecto 'data/processed'.
        formato (Literal, opcional): Estilo de la fecha:
            - "mes_año": AAAAMM
            - "compacto": AAAAMMDD
            - "hora": AAAAMMDD_hrHHMM
            - "segundo": AAAAMMDD_HHMMSS
            Por defecto es "hora".
        fecha_al_inicio (bool, opcional): Si la fecha va al principio o al final. 
            Por defecto es True.
        notificar (bool, opcional): Si es True, imprime la ruta generada en la terminal. 
            Por defecto es True.

    Returns:
        Path: Objeto Path con la ruta completa del archivo.

    Example:
        >>> ruta = generar_ruta_salida("Demanda Lece", formato="compacto")
        Ruta generada: data/processed/20260406_demanda_lece.xlsx
    """
    
    # Diccionario interno de formatos
    formatos = {
        "mes_año": "%Y%m",
        "compacto": "%Y%m%d",
        "hora": "%Y%m%d_hr%H%M",
        "segundo": "%Y%m%d_%H%M%S"
    }

    # Validación de formato (por si se pasa un string no contemplado)
    fmt_string = formatos.get(formato, formatos["hora"])
    
    directorio = Path(ruta_directorio)
    ext = f".{extension.lstrip('.')}"
    fecha_str = datetime.now().strftime(fmt_string)
    nombre_limpio = nombre_base.strip().lower().replace(" ", "_")
    
    if fecha_al_inicio:
        nombre_final = f"{fecha_str}_{nombre_limpio}{ext}"
    else:
        nombre_final = f"{nombre_limpio}_{fecha_str}{ext}"
        
    ruta_final = directorio / nombre_final

    if notificar:
        print(f"Ruta generada para <<{nombre_base}>>: {ruta_final}")
        
    return ruta_final