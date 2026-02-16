import pandas as pd
import re
from datetime import datetime
from pathlib import Path
import warnings
warnings.simplefilter("ignore", UserWarning)


def _get_initial_and_final_dates_from_report_name(nombre_archivo):

    # Expresión regular para extraer el rango de fechas (año opcional, separado o pegado al mes)
    match = re.search(
        r"(\d{2})\s+AL\s+(\d{2})\s+DE\s+([A-Z]+)(?:\s+DE\s+(\d{4})|[^\d]*(\d{4}))?",
        nombre_archivo,
        re.IGNORECASE,
    )

    if match:
        dia_inicio, dia_fin, mes, año_separado, año_pegado = match.groups()

        # Si el año está separado, lo usamos directamente
        año = año_separado if año_separado else año_pegado

        # Si no se especifica el año, se usa un valor por defecto
        if año is None:
            año = datetime.now().year  # Puedes cambiar esto según tu lógica

        mes_numero = {
            "ENERO": "01",
            "FEBRERO": "02",
            "MARZO": "03",
            "ABRIL": "04",
            "MAYO": "05",
            "JUNIO": "06",
            "JULIO": "07",
            "AGOSTO": "08",
            "SEPTIEMBRE": "09",
            "OCTUBRE": "10",
            "NOVIEMBRE": "11",
            "DICIEMBRE": "12",
        }.get(mes.upper(), "")

        fecha_inicio = f"{año}-{mes_numero}-{dia_inicio}"
        fecha_fin = f"{año}-{mes_numero}-{dia_fin}"
        print("Fechas identificadas del nombre del reporte:")
        print(f"Fecha de inicio: {fecha_inicio}")
        print(f"Fecha de fin: {fecha_fin}")
        print(60 * "-")
        return fecha_inicio, fecha_fin


def _get_reports_by_date(files_path: str):
    nombre_archivo = Path(files_path).stem
    fechas = _get_initial_and_final_dates_from_report_name(nombre_archivo)
    cant_fechas = len(pd.date_range(start=fechas[0], end=fechas[1]))
    return pd.DataFrame(
        {
            "fecha": pd.date_range(start=fechas[0], end=fechas[1]),
            "nombre_reporte": [nombre_archivo for i in range(cant_fechas)],
            "ruta": [files_path for i in range(cant_fechas)],
        }
    )


def _order_reports_by_dates(folder_files_path: str):

    files_path = Path(folder_files_path)
    files = []

    for i in files_path.iterdir():
        if i.suffix == ".xlsx":
            files.append(i)
    df_reports = pd.DataFrame()
    for file in files:
        df_reports = pd.concat(
            [df_reports, _get_reports_by_date(file)], ignore_index=True
        )

    return df_reports


#################################################
####   Este es el exportable de esta etapa   ####
#################################################


def reports_in_folder(folder: str):
    df_reports = _order_reports_by_dates(folder)

    # Ordenar por Fecha
    df_reports = df_reports.sort_values(by="fecha")
    # Identify duplicated
    fechas_duplicadas = df_reports[df_reports["fecha"].duplicated()]["fecha"].unique()
    # Message in Duplicated Case:
    if len(fechas_duplicadas) > 0:
        print(
            f"Tenemos {len(fechas_duplicadas)} fechas Duplicadas en rango de fechas Extraídas del nombre de los reportes."
        )
        print([fecha.date() for fecha in fechas_duplicadas])
    # DataFrame Final
    return df_reports.reset_index(drop=True)


#############################################################


import pandas as pd
import numpy as np
import re
from datetime import datetime


def etl_quirofanos_completo(archivo_excel, nombre_hoja):
    """
    Función ETL mejorada para extraer todos los quirófanos y sus cirugías programadas.
    """

    # Leer todo el archivo sin procesar
    df_raw = pd.read_excel(archivo_excel, sheet_name=nombre_hoja, header=None)

    print(f"Dimensiones del DataFrame: {df_raw.shape}")

    # Buscar todas las filas que contienen "Quirófano No."
    filas_quirofanos = []
    for idx in range(len(df_raw)):
        row_text = " ".join([str(v) for v in df_raw.iloc[idx, :] if pd.notna(v)])
        if "Quirófano No." in row_text:
            filas_quirofanos.append(idx)

    print(f"Quirófanos encontrados en filas: {filas_quirofanos}")

    # Lista para almacenar todos los registros
    todos_registros = []

    # Procesar cada quirófano
    for i, fila_inicio_q in enumerate(filas_quirofanos):
        # Determinar fila final de este quirófano
        if i < len(filas_quirofanos) - 1:
            fila_fin_q = filas_quirofanos[i + 1]
        else:
            # Buscar la siguiente línea con "N.º de Quirófano" o final del archivo
            fila_fin_q = len(df_raw)
            for idx in range(fila_inicio_q + 1, len(df_raw)):
                row_text = " ".join(
                    [str(v) for v in df_raw.iloc[idx, :] if pd.notna(v)]
                )
                if "N.º de Quirófano/Horas disponibles" in row_text:
                    fila_fin_q = idx
                    break

        # Extraer información del quirófano
        quirofano_cell = df_raw.iloc[fila_inicio_q, 1]
        quirofano_str = str(quirofano_cell)

        quirofano_match = re.search(r"Quirófano No\.\s*(\d+)", quirofano_str)
        num_quirofano = quirofano_match.group(1) if quirofano_match else f"Q{i+1}"

        # Extraer especialidad (última línea del cell)
        especialidad = None
        if "\n" in quirofano_str:
            lineas = quirofano_str.split("\n")
            # La especialidad suele estar en las últimas líneas
            for linea in reversed(lineas):
                linea_clean = linea.strip()
                if (
                    linea_clean
                    and "Quirófano" not in linea_clean
                    and "Horas" not in linea_clean
                ):
                    especialidad = linea_clean
                    break

        print(f"\n{'='*60}")
        print(f"Procesando Quirófano {num_quirofano}: {especialidad}")
        print(f"Rango de filas: {fila_inicio_q} a {fila_fin_q}")

        # La fila de días está 2 filas antes del quirófano
        fila_dias = fila_inicio_q - 2
        fila_fechas = fila_inicio_q - 1

        if fila_dias < 0:
            print(f"  ⚠ Fila de días fuera de rango")
            continue

        print(f"  Fila de días: {fila_dias}")
        print(f"  Fila de fechas: {fila_fechas}")

        # Mapear columnas a días y fechas
        # La estructura es: Col2=Hora, Col3=Lunes, Col4=Hora, Col5=Martes, etc.
        fechas_info = {}

        for col in range(2, len(df_raw.columns)):
            # Buscar día en fila_dias
            dia_val = df_raw.iloc[fila_dias, col]

            if pd.notna(dia_val):
                dia_str = str(dia_val).strip()

                # Verificar si es un día de la semana
                for dia in [
                    "Lunes",
                    "Martes",
                    "Miércoles",
                    "Jueves",
                    "Viernes",
                    "Sábado",
                    "Domingo",
                ]:
                    if dia == dia_str:
                        # Buscar fecha en la fila siguiente, misma columna
                        fecha_val = df_raw.iloc[fila_fechas, col]

                        if pd.notna(fecha_val):
                            # Convertir a fecha
                            if isinstance(fecha_val, pd.Timestamp):
                                fecha = fecha_val
                            else:
                                try:
                                    fecha = pd.to_datetime(fecha_val)
                                except:
                                    continue

                            # La columna de hora está en col-1
                            # La columna de datos está en la misma columna (col)
                            col_hora = col - 1
                            col_datos = col

                            fechas_info[col] = {
                                "dia": dia,
                                "fecha": fecha,
                                "col_hora": col_hora,
                                "col_datos": col_datos,
                            }
                            break

        print(f"  Fechas encontradas: {len(fechas_info)}")
        for col, info in fechas_info.items():
            print(
                f"    Col {col} (datos), Col {info['col_hora']} (hora): {info['dia']} {info['fecha'].strftime('%Y-%m-%d')}"
            )

        if not fechas_info:
            print(f"  ⚠ No se encontraron fechas válidas")
            continue

        # Determinar dónde empiezan los datos del quirófano
        fila_inicio_datos = fila_inicio_q

        print(f"  Inicio de datos: fila {fila_inicio_datos}")

        # Procesar las filas de datos
        for fila in range(fila_inicio_datos, fila_fin_q):
            # Verificar si llegamos a una nueva sección
            row_text = " ".join([str(v) for v in df_raw.iloc[fila, :] if pd.notna(v)])
            if "N.º de Quirófano" in row_text and fila > fila_inicio_q:
                break

            # Procesar cada día (columna de datos)
            for col_dato, info_fecha in fechas_info.items():
                col_hora = info_fecha["col_hora"]

                hora_val = df_raw.iloc[fila, col_hora]
                dato_val = df_raw.iloc[fila, col_dato]

                # Verificar si hay datos válidos
                if pd.isna(dato_val):
                    continue

                dato_str = str(dato_val).strip()

                # Filtrar valores no válidos
                if dato_str in [
                    "nan",
                    "",
                    "No. De expediente",
                    "Procedimiento QX",
                    "Médico",
                ]:
                    continue

                # Extraer código de expediente
                codigo_match = re.search(r"(\d{4}-\d{4}-\d{5})", dato_str)
                if not codigo_match:
                    continue

                codigo = codigo_match.group(1)

                # Extraer horas
                hora_str = str(hora_val).strip() if pd.notna(hora_val) else ""
                hora_inicio, hora_fin = extraer_horas(hora_str)

                # Extraer procedimiento y doctor de las siguientes filas
                procedimiento = None
                doctor = None

                # La siguiente fila suele tener el procedimiento
                if fila + 1 < len(df_raw):
                    proc_val = df_raw.iloc[fila + 1, col_dato]
                    if pd.notna(proc_val):
                        procedimiento = str(proc_val).strip()

                # La fila siguiente a esa tiene el doctor
                if fila + 2 < len(df_raw):
                    doc_val = df_raw.iloc[fila + 2, col_dato]
                    if pd.notna(doc_val):
                        doc_str = str(doc_val).strip()
                        if "Dr." in doc_str or "Dra." in doc_str:
                            doctor = doc_str

                # Calcular duración
                duracion = calcular_duracion(hora_inicio, hora_fin)

                # Crear registro
                registro = {
                    "quirofano": f"Quirófano {num_quirofano}",
                    "quirofano_num": int(num_quirofano),
                    "especialidad": especialidad,
                    "fecha": info_fecha["fecha"],
                    "dia_semana": info_fecha["dia"],
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "duracion_horas": duracion,
                    "codigo_expediente": codigo,
                    "procedimiento": procedimiento,
                    "medico": doctor,
                }

                todos_registros.append(registro)

    # Crear DataFrame final
    df_final = pd.DataFrame(todos_registros)

    # Ordenar por quirófano, fecha y hora
    if len(df_final) > 0:
        df_final = df_final.sort_values(
            ["quirofano_num", "fecha", "hora_inicio"]
        ).reset_index(drop=True)

    return df_final


def extraer_horas(hora_str):
    """Extrae hora de inicio y fin del string"""
    if not hora_str or hora_str == "nan":
        return None, None

    hora_inicio, hora_fin = None, None

    # Limpiar el string
    hora_str = hora_str.replace("A.M", "").replace("P.M", "").replace(".", "")

    # Patrón: "07:00 A 08:00" o variaciones
    patron = r"(\d{1,2}):(\d{2})\s*[AaYy]\s*(\d{1,2}):(\d{2})"
    match = re.search(patron, hora_str)

    if match:
        h1 = int(match.group(1))
        m1 = match.group(2)
        h2 = int(match.group(3))
        m2 = match.group(4)

        hora_inicio = f"{h1:02d}:{m1}"
        hora_fin = f"{h2:02d}:{m2}"

    return hora_inicio, hora_fin


def calcular_duracion(hora_inicio, hora_fin):
    """Calcula la duración en horas entre dos horas"""
    if not hora_inicio or not hora_fin:
        return None

    try:
        h_ini = datetime.strptime(hora_inicio, "%H:%M")
        h_fin = datetime.strptime(hora_fin, "%H:%M")

        # Si la hora fin es menor o igual, asumimos siguiente día
        if h_fin <= h_ini:
            from datetime import timedelta

            h_fin = h_fin + timedelta(hours=12)  # Ajuste para PM

        duracion = (h_fin - h_ini).total_seconds() / 3600
        return round(duracion, 2)
    except:
        return None


def analizar_quirofanos(df):
    """Genera estadísticas del DataFrame de quirófanos"""
    if len(df) == 0:
        print("No hay datos para analizar")
        return

    print("=" * 80)
    print("RESUMEN DE CIRUGÍAS PROGRAMADAS")
    print("=" * 80)

    print(f"\nTotal de cirugías programadas: {len(df)}")

    print("\n--- Cirugías por Quirófano ---")
    print(df["quirofano"].value_counts().sort_index())

    print("\n--- Cirugías por Día ---")
    dias_orden = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]
    conteo_dias = df["dia_semana"].value_counts()
    for dia in dias_orden:
        if dia in conteo_dias:
            print(f"{dia:15s}: {conteo_dias[dia]}")

    print("\n--- Cirugías por Especialidad ---")
    print(df["especialidad"].value_counts())

    print("\n--- Top 10 Médicos ---")
    print(df["medico"].value_counts().head(10))

    print("\n--- Duración Promedio por Quirófano (horas) ---")
    duracion_prom = df.groupby("quirofano")["duracion_horas"].mean().round(2)
    print(duracion_prom)

    print("\n--- Procedimientos Más Frecuentes (Top 10) ---")
    print(df["procedimiento"].value_counts().head(10))


# --------Esta es la clave-----------------------#


def get_schedule_from_file(archivo, hoja="A1. CUADRO RESUMEN DE PROD.QX"):

    print("Iniciando ETL...")
    df_quirofanos = etl_quirofanos_completo(archivo, hoja)

    print(f"\n{'='*60}")
    print(f"✓ ETL completado. Total de registros: {len(df_quirofanos)}")
    print(f"{'='*60}")

    if len(df_quirofanos) > 0:

        # Análisis
        analizar_quirofanos(df_quirofanos)

    else:
        print("\n⚠ No se encontraron registros")
    print(f"solo Archivo: {archivo}")

    nombre_archivo = Path(archivo).stem

    df_quirofanos["archivo"] = nombre_archivo

    return df_quirofanos


def get_schedule_from_folder(folder):
    files = [file for file in Path(folder).iterdir() if file.suffix == ".xlsx"]
    df = pd.DataFrame()
    for file in files:
        df = pd.concat([df, get_schedule_from_file(file)], ignore_index=True)
    return df


# ------------------------------
def _get_schedule_table_from_file(file, hoja="A2. CIRUGIA ELECTIVA"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[1]].str.contains("fecha", case=False, na=False)
    ].index[0]

    indice_ultima_fila = df[
        df[df.columns[1]].str.contains("fecha", case=False, na=False)
    ].index[1]

    nrows = (indice_ultima_fila - indice_primera_fila) - 2
    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        nrows=nrows,
        dtype={"Nº del Expediente": str, "Fecha": "datetime64[ns]"},
    )
    df["tipo"] = "Programada Proxima Semana"
    df['ejecutada'] = False
    return df[df["Fecha"].notna()]


def _get_fact_table_from_file(file, hoja="A2. CIRUGIA ELECTIVA"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[1]].str.contains("fecha", case=False, na=False)
    ].index[1]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"Nº del Expediente": str, "Fecha": "datetime64[ns]"},
    )
    df["tipo"] = "Electiva"
    df['ejecutada'] = True
    return df[df["Fecha"].notna()]


def _get_deferred_table_from_file(file, hoja="A3. CIRUGIAS DIFERIDAS"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[1]].str.contains("fecha", case=False, na=False)
    ].index[0]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"Nº del Expediente": str, "Fecha": "datetime64[ns]"},
    )

    df["tipo"] = "Diferida Hospitalización"
    df['ejecutada'] = True
    return df[df["Fecha"].notna()]


def _get_emergencies_table_from_file(file, hoja="A4. CIRUGIAS EMERGENCIA"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[1]].str.contains("fecha", case=False, na=False)
    ].index[0]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"Nº del Expediente": str, "Fecha": "datetime64[ns]"},
    )
    df["tipo"] = "Emergencia"
    df['ejecutada'] = True
    return df[df["Fecha"].notna()]


def _get_cancelled_table_from_file(file, hoja="A5. CIRUGIAS CANCELADAS"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[1]].str.contains("nombre", case=False, na=False)
    ].index[0]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"N° de Expediente": str},
    )
    df["tipo"] = "Cancelada"
    df['ejecutada'] = False
    return df[df["N° de Expediente"].notna()]


def _get_added_table_from_file(file, hoja="A6. CIRUGIAS SUSTI Y AGREG"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila
    indice_primera_fila = df[
        df[df.columns[3]].str.contains("nombre del paciente sus", case=False, na=False)
    ].index[0]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"Nº del Expediente.1": str},
    )
    df["tipo"] = "Agregada Durante la Semana"
    df['ejecutada'] = True
    df = df[df["Nombre del paciente sustituto o agregado"].notna()]
    return df[df[df.columns[2]].isna()]


def _get_substituted_table_from_file(file, hoja="A6. CIRUGIAS SUSTI Y AGREG"):

    # importar para leer
    df = pd.read_excel(file, sheet_name=hoja)
    # Encontrar primera fila

    indice_primera_fila = df[
        df[df.columns[3]].str.contains("nombre del paciente sus", case=False, na=False)
    ].index[0]

    df = pd.read_excel(
        file,
        sheet_name=hoja,
        skiprows=indice_primera_fila + 1,
        dtype={"Nº del Expediente": str},
    )

    df["tipo"] = "Sustitución de Paciente Cancelado"
    df['ejecutada'] = True
    df = df[df["Nombre del paciente sustituto o agregado"].notna()]
    
    return df[df[df.columns[2]].notna()]


### Esta será la que extrae todo
def get_all_surgery_info_from_file(file_path: str):

    df_agregados_sustituidos = pd.concat(
        [
            _get_substituted_table_from_file(file_path),
            _get_added_table_from_file(file_path),
        ],
        ignore_index=True,
    )

    df_agregados_sustituidos.drop(
        columns={"Nombre del Paciente programado", "Nº del Expediente"}, inplace=True
    )
 

    df_agregados_sustituidos.columns = [
        "Nº",
        "Paciente",
        "Expediente",
        "Procedimiento",
        "EN LEQ",
        "EN MORA",
        "NO MORA",
        "Servicio",
        "tipo",
        "ejecutada"
    ]

    df_cancelados = _get_cancelled_table_from_file(file_path)

    df_cancelados.drop(columns={"Observaciones"}, inplace=True)

    df_cancelados.columns = [
        "Nº",
        "Paciente",
        "Expediente",
        "Procedimiento",
        "Servicio",
        "Motivo de cancelación",
        "EN LEQ",
        "EN MORA",
        "NO MORA",
        "Observaciones",
        "Imputable",
        "tipo",
        "ejecutada"
    ]

    # unificando los parecidos:

    df_generales = pd.concat(
        [
            _get_fact_table_from_file(file_path),
            _get_schedule_table_from_file(file_path),
            _get_deferred_table_from_file(file_path),
            _get_emergencies_table_from_file(file_path),
        ],
        ignore_index=True,
    )

    df_generales.columns = [
        "Nº",
        "Fecha",
        "Paciente",
        "Expediente",
        "Procedimiento",
        "Servicio",
        "EN LEQ",
        "EN MORA",
        "NO MORA",
        "Medico",
        "tipo",
        "ejecutada"
    ]

    df_unificado_total = pd.concat(
        [
            df_generales,
            df_agregados_sustituidos,
            df_cancelados,
        ],
        ignore_index=True,
    )

    df_unificado_total.drop(columns={"Nº"}, inplace=True)

    df_unificado_total["archivo"] = Path(file_path).stem
    return df_unificado_total


def get_all_surgery_info_from_folder(folder):
    files = [file for file in Path(folder).iterdir() if file.suffix == ".xlsx"]
    df = pd.DataFrame()
    for file in files:
        df = pd.concat([df, get_all_surgery_info_from_file(file)], ignore_index=True)
    return df
