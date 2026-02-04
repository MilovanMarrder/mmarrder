import pandas as pd
import pymssql
import os
from dotenv import load_dotenv


def query_db(
    query : str
):  

    """
    Se agiliza las consultas a base de datos. Requiere tener variables de entorno definidas. 

    
    """

    try:
        
        load_dotenv()

        user = os.getenv('USER')
        password = os.getenv('PASSWORD')
        database = os.getenv('DATABASE')
        server = os.getenv('SERVER')
        
        # Establecer la conexión
        conn = pymssql.connect(server=server, user=user, password=password, database=database)
        
        df = pd.read_sql_query(query,conn)

    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")

    finally:
        # Cerrar la conexión
        if 'conn' in locals():
            conn.close()
    return df