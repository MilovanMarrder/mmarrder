import pandas as pd
import pymssql
import os
from dotenv import load_dotenv
from pathlib import Path

def query_db(query: str, params: tuple | dict | None = None, ) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL en la base de datos y retorna los resultados en un DataFrame.

    Esta función gestiona automáticamente la carga de credenciales desde el archivo .env,
    establece la conexión con SQL Server mediante pymssql y asegura el cierre de la 
    conexión tras la ejecución, incluso si ocurre un error.

    Args:
        query (str): Sentencia SQL a ejecutar. Debe usar marcadores de parámetros 
            tipo '%s' para tuplas o '%(key)s' para diccionarios para evitar 
            inyección SQL.
        params (tuple o dict, opcional): Valores a inyectar en la consulta. 
            Si es una tupla, el orden debe coincidir con los '%s'. 
            Si es un dict, las llaves deben coincidir con '%(key)s'. 
            Por defecto es None.

    Returns:
        pd.DataFrame: Un objeto DataFrame con los resultados de la consulta. 
            Retorna None (o un DataFrame vacío dependiendo del error) si la 
            conexión o ejecución fallan.

    Example:
        >>> # Ejemplo 1: Sin parámetros
        >>> df = query_db("SELECT TOP 10 * FROM tuTabla")
        
        >>> # Ejemplo 2: Con parámetros (Tupla)
        >>> sql = "SELECT * FROM Ventas WHERE Anio = %s"
        >>> df = query_db(sql, params=(2024,))
        >>> print(df.head())
        
        >>> # Ejemplo 3: Con diccionario (Recomendado)
        >>> sql = "SELECT * FROM Vista WHERE año > %(anio)s AND sala = %(sala)s"
        >>> data = {'anio': 2023, 'sala': 'Quirofano 1'}
        >>> df = query_db(sql, params=data)
    """
    df = None  # Inicializamos df para evitar errores si falla el try
    # Definir ruta explícita al .env (raíz del proyecto)
    BASE_DIR = Path(__file__).resolve().parents[2]
    env_path = BASE_DIR / ".env"

    load_dotenv(dotenv_path=env_path)

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    database = os.getenv('DATABASE')
    server = os.getenv('SERVER')

    # Validación crítica (esto te ahorra horas de debugging)
    if not all([user, password, database, server]):
        raise ValueError("Variables de entorno no cargadas correctamente")
        
    try:
        # Establecer la conexión
        conn = pymssql.connect(server=server, user=user, password=password, database=database)
        
        # Pasamos el argumento 'params' directamente a pandas
        df = pd.read_sql_query(query, conn, params=params)

    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")

    finally:
        # Cerrar la conexión de forma segura
        if 'conn' in locals() and conn:
            conn.close()
            
    return df