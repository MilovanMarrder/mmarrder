from pathlib import Path
from typing import Any, Union
from functools import lru_cache
import json
import yaml

_MISSING = object()

_LOADERS: dict[str, tuple[str, Any]] = {
    ".json": ("r", json.load),
    ".yaml": ("r", lambda f: yaml.safe_load(f) or {}),
    ".yml":  ("r", lambda f: yaml.safe_load(f) or {}),
}


@lru_cache(maxsize=16)
def _leer_archivo(path: Path) -> Any:           # ✅ Any, no dict
    ext = path.suffix.lower()
    if ext not in _LOADERS:
        raise ValueError(
            f"Formato no soportado: '{ext}'. "
            f"Formatos válidos: {list(_LOADERS)}"
        )
    modo, loader = _LOADERS[ext]
    with path.open(modo, encoding="utf-8") as f:  # ✅ path.open()
        return loader(f)


def cargar_config(
    archivo: str = "config.json",
    *keys: Union[str, int],                       # ✅ str | int
    default: Any = _MISSING,
    reload: bool = True,                         # ✅ parámetro reload
) -> Any:
    """
    Carga un archivo de configuración JSON o YAML y navega su estructura
    anidada mediante una secuencia de claves o índices.

    El archivo se lee una sola vez por sesión gracias a un caché interno
    (``lru_cache``). Las llamadas posteriores con el mismo archivo no
    generan I/O adicional, salvo que se indique ``reload=True``.

    La detección de formato es automática según la extensión del archivo:

    +------------+------------------+
    | Extensión  | Formato          |
    +============+==================+
    | ``.json``  | JSON             |
    +------------+------------------+
    | ``.yaml``  | YAML             |
    +------------+------------------+
    | ``.yml``   | YAML (alias)     |
    +------------+------------------+

    Parameters
    ----------
    archivo : str, optional
        Ruta al archivo de configuración, relativa o absoluta.
        Por defecto ``"config.json"`` en el directorio de trabajo actual.
    *keys : str or int
        Secuencia de claves (``str``) o índices (``int``) para navegar
        la estructura cargada. Se aplican en orden, soportando
        diccionarios y listas anidados en cualquier combinación.
        Si no se pasan claves, se retorna la estructura completa.
    default : Any, optional
        Valor devuelto cuando la ruta de claves no existe.
        Acepta cualquier valor, **incluido** ``None``.
        Si se omite y la ruta no existe, se lanza ``KeyError``.
    reload : bool, optional
        Si es ``True``, invalida el caché antes de leer el archivo,
        forzando una relectura desde disco. Útil en notebooks o
        pipelines donde el archivo puede cambiar entre llamadas.
        Por defecto ``True``.

    Returns
    -------
    Any
        - La estructura completa si no se pasan ``keys``.
        - El valor encontrado en la ruta ``keys[0] → keys[1] → …``
        - ``default`` si la ruta no existe y se proporcionó.

    Raises
    ------
    FileNotFoundError
        Si el archivo indicado no existe en el sistema de archivos.
    ValueError
        Si la extensión del archivo no corresponde a ningún formato
        soportado.
    KeyError
        Si una clave ``str`` no existe en el diccionario actual y no
        se definió ``default``.
    TypeError
        Si se intenta navegar con una clave ``str`` sobre una lista
        (se requiere índice ``int``), o si el valor actual no es
        navegable (no es ``dict`` ni ``list``).
    IndexError
        Si un índice ``int`` está fuera del rango de la lista.

    Notes
    -----
    - El caché opera sobre la ruta resuelta (``Path.resolve()``), por lo
      que rutas relativas y absolutas equivalentes comparten entrada.
    - Con ``reload=True`` se limpia **todo** el caché, no solo la entrada
      del archivo indicado (limitación de ``lru_cache``).
    - Los archivos YAML vacíos retornan ``{}`` en lugar de ``None``.
    - Las raíces JSON/YAML que sean listas en lugar de diccionarios
      son válidas; usa índices ``int`` como primeras claves.

    Examples
    --------
    Dado el archivo ``config.yaml``:

    .. code-block:: yaml

        base_de_datos:
          host: localhost
          puerto: 5432
          replicas:
            - host: replica-1
              puerto: 5433
            - host: replica-2
              puerto: 5434

        app:
          debug: true

    Cargar la estructura completa:

    >>> cargar_config("config.yaml")
    {'base_de_datos': {...}, 'app': {...}}

    Acceder a un valor simple:

    >>> cargar_config("config.yaml", "base_de_datos", "host")
    'localhost'

    Navegar una lista con índice entero:

    >>> cargar_config("config.yaml", "base_de_datos", "replicas", 0, "host")
    'replica-1'

    Usar ``default`` cuando la clave puede no existir:

    >>> cargar_config("config.yaml", "app", "timeout", default=30)
    30

    Usar ``None`` explícitamente como valor por defecto:

    >>> cargar_config("config.yaml", "app", "sentry_dsn", default=None)
    None

    Forzar relectura tras modificar el archivo en disco:

    >>> cargar_config("config.yaml", "app", "debug", reload=True)
    True
    """
    path = Path(archivo).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: '{archivo}'")

    if reload:
        _leer_archivo.cache_clear()

    config = _leer_archivo(path)

    if not keys:
        return config

    valor = config

    for key in keys:
        # ✅ Navegación explícita con errores descriptivos
        if isinstance(valor, dict):
            if key not in valor:
                if default is not _MISSING:
                    return default
                ruta = " -> ".join(map(str, keys))
                raise KeyError(
                    f"Clave '{key}' no encontrada "
                    f"(ruta: '{ruta}' en '{archivo}')"
                )
            valor = valor[key]

        elif isinstance(valor, list):
            if not isinstance(key, int):
                raise TypeError(
                    f"Se esperaba índice 'int' para navegar una lista, "
                    f"se recibió '{type(key).__name__}': {key!r}"
                )
            try:
                valor = valor[key]
            except IndexError:
                if default is not _MISSING:
                    return default
                raise IndexError(
                    f"Índice {key} fuera de rango "
                    f"(lista de {len(valor)} elementos en '{archivo}')"
                )
        else:
            raise TypeError(
                f"No se puede navegar la clave {key!r} "
                f"porque el valor actual es de tipo "
                f"'{type(valor).__name__}', no es un dict ni una lista"
            )

    return valor