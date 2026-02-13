from .excel_reader import detectar_tabla_excel
from mmarrder.transform import normalizar_periodos, recortar_por_ultima_linea, filtrar_periodo
from .transform import normalizar_periodos_consulta_externa



import pandas as pd


class Infografico:

    def __init__(self, ruta):
        self.ruta = ruta

    def _leer_tabla_base(
        self,
        hoja,
        palabra="especialidad",
        valor_final="",
        incluir_valor_final=False,
        columnas_valor_final="",
    ):
        fila, col_ini, col_fin = detectar_tabla_excel(self.ruta, hoja, palabra)

        df = pd.read_excel(self.ruta, sheet_name=hoja, header=fila)

        df = df.iloc[:, col_ini:col_fin]
        if incluir_valor_final:
            df = recortar_por_ultima_linea(
                df, valor=valor_final, col_name=columnas_valor_final
            )
            return df
        else:
            df = recortar_por_ultima_linea(df)

        return df

    def pacientes_nuevos(
        self, año=None, mes=None, hoja="Pacientes Nuevos", incluir_sin_produccion=True
    ):
        df = self._leer_tabla_base(hoja=hoja)

        columna_id = df.columns[0]  # Especialidad
        df = normalizar_periodos(df, columna_id)
        df = filtrar_periodo(df, año, mes)
        df.columns = ["periodo", "especialidad", "produccion"]
        if incluir_sin_produccion:
            return df
        else:
            return df[df["produccion"] > 0]

    def consulta_externa(
        self, año=None, mes=None, hoja="Consultas Externas", incluir_sin_produccion=True
    ):
        df = self._leer_tabla_base(
            hoja=hoja,
            incluir_valor_final=True,
            valor_final="Maritza Betancourt",
            columnas_valor_final="Médico",
        )

        columna_id = df.columns[0:2]  # Especialidad, y medicos
        df = normalizar_periodos_consulta_externa(df, columna_id)
        df.columns = ["periodo", "especialidad", "medico", "produccion"]
        df = filtrar_periodo(df, año, mes)
        if incluir_sin_produccion:
            return df
        else:
            return df[df["produccion"] > 0]

    def hospitalizacion(
        self,
        año=None,
        mes=None,
        hoja="Hospitalización",
        incluir_sin_produccion=True,
        palabra="Hospitalización Total",
        detalle_sala=False,
    ):

        if detalle_sala:
            salas = [
                "Sala Misceláneos",
                "Sala Nefrología",
                "Unidad de Cuidados Intermedios",
                "UME",
            ]
            df = pd.DataFrame()

            for sala in salas:
                prod_sala = self.hospitalizacion(palabra=sala)
                prod_sala["sala"] = sala
                df = pd.concat([df, prod_sala], ignore_index=True)
                return df
        else:

            df = self._leer_tabla_base(
                hoja=hoja,
                palabra=palabra,
                valor_final="Días Paciente",
                incluir_valor_final=True,
                columnas_valor_final=palabra,
            )

            columna_id = df.columns[0]  # columna inicial
            df = normalizar_periodos(df, columna_id)
            df = filtrar_periodo(df, año, mes)
            df.columns = ["periodo", "metrica", "produccion"]
            if incluir_sin_produccion:
                return df
            else:
                return df[df["produccion"] > 0]

    def procedimientos(
        self,
        año=None,
        mes=None,
        hoja="Procedimientos Quirúrgicos",
        incluir_sin_produccion=True,
    ):
        df = self._leer_tabla_base(hoja=hoja, valor_final="Totales", palabra="ugc")

        columna_id = df.columns[0]  # Especialidad
        df = normalizar_periodos(df, columna_id)
        df = filtrar_periodo(df, año, mes)
        df = df[~df[columna_id].str.contains("brigada", case=False, na=False)]
        df.columns = ["periodo", "ugc", "produccion"]
        df = filtrar_periodo(df, año, mes)
        if incluir_sin_produccion:
            return df
        else:
            return df[df["produccion"] > 0]

    def servicios_apoyo(
        self, año=None, mes=None, hoja="Servicios de Apoyo", incluir_sin_produccion=True
    ):
        df = self._leer_tabla_base(palabra="Servicios", hoja=hoja)

        columna_id = df.columns[0]  # columna inicial
        df = normalizar_periodos(df, columna_id)
        df = df[df["Servicios"] != "Holter"]
        df = filtrar_periodo(df, año, mes)
        if incluir_sin_produccion:
            return df
        else:
            return df[df["produccion"] > 0]
