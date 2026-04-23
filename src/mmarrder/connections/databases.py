import pandas as pd
import pymssql
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional


def query_db(
    query: str,
    params: tuple | dict | None = None,
    env_path: Optional[str | Path] = None,
    connection_config: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL en SQL Server y retorna un DataFrame.

    Estrategia híbrida de configuración (en orden de prioridad):
    1. connection_config (override directo)
    2. env_path (cargar .env específico)
    3. .env automático (fallback, comportamiento anterior)

    Esto asegura compatibilidad con proyectos existentes.
    """

    df = None

    # 🔹 1. Carga de entorno (híbrido)
    if connection_config is None:
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            # Fallback automático (compatibilidad con proyectos antiguos)
            load_dotenv()

    # 🔹 2. Obtener configuración
    if connection_config:
        user = connection_config.get("USER")
        password = connection_config.get("PASSWORD")
        database = connection_config.get("DATABASE")
        server = connection_config.get("SERVER")
    else:
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        database = os.getenv("DATABASE")
        server = os.getenv("SERVER")

    # 🔹 3. Validación crítica
    if not all([user, password, database, server]):
        raise ValueError(
            "Variables de entorno no cargadas correctamente. "
            "Verifica .env, env_path o connection_config."
        )

    try:
        # 🔹 4. Conexión
        conn = pymssql.connect(
            server=server,
            user=user,
            password=password,
            database=database
        )

        # 🔹 5. Ejecución
        df = pd.read_sql_query(query, conn, params=params)

    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")

    finally:
        # 🔹 6. Cierre seguro
        if 'conn' in locals() and conn:
            conn.close()

    return df