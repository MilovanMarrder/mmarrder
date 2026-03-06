import unicodedata
import re
import pandas as pd

def normalizar_texto(texto: str, estilo_texto = 'UPPER') -> str:
    """
    Normaliza un texto eliminando tildes, reduciendo espacios en blanco
    repetidos y aplicando un estilo de capitalización especificado.

    La función convierte el texto a uno de los siguientes estilos:
    ``'upper'``, ``'lower'`` o ``'title'``. Luego elimina diacríticos
    (acentos y otros signos), normaliza espacios múltiples a un solo
    espacio y retorna el resultado final.

    Parameters
    ----------
    texto : str
        Texto de entrada que se desea normalizar. Si el valor es nulo
        (`NaN`), la función retorna una cadena vacía.
    estilo_texto : str, default='UPPER'
        Estilo de transformación del texto antes de normalizarlo.
        Valores permitidos:
        - ``'upper'``: convierte todo a mayúsculas.
        - ``'lower'``: convierte todo a minúsculas.
        - ``'title'``: convierte a formato título.

    Returns
    -------
    str
        Texto normalizado, sin tildes, con espacios simplificados y con
        el estilo de capitalización solicitado.

    Raises
    ------
    ValueError
        Si `estilo_texto` no es uno de los valores permitidos:
        ``'upper'``, ``'lower'`` o ``'title'``.

    Examples
    --------
    >>> normalizar_texto("  José   Martínez ", "upper")
    'JOSE MARTINEZ'

    >>> normalizar_texto("área de trabajo", "title")
    'Area De Trabajo'
    """
    if pd.isna(texto):
        return ""
    match estilo_texto.lower():
        case 'upper':
            texto = str(texto).upper().strip()
        case 'title':
            texto = str(texto).title().strip()
        case 'lower':
            texto = str(texto).lower().strip()
        case _:
            raise ValueError(f"Estilo de texto no válido: {estilo_texto}")
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto)
    return texto

