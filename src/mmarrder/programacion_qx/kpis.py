from __future__ import annotations
import pandas as pd


def horas_por_quirofano(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("quirofano")["duracion_horas"]
        .sum()
        .reset_index()
        .rename(columns={"duracion_horas": "total_horas"})
    )


def horas_por_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["quirofano", "dia_semana"])["duracion_horas"]
        .sum()
        .reset_index()
        .rename(columns={"duracion_horas": "total_horas"})
    )


def horas_por_medico(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("medico")["duracion_horas"]
        .sum()
        .reset_index()
        .rename(columns={"duracion_horas": "total_horas"})
    )


def cirugias_por_dia(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("fecha")
        .size()
        .reset_index(name="cantidad_cirugias")
    )


def duracion_promedio_cirugia(df: pd.DataFrame) -> float:
    return float(df["duracion_horas"].mean())


def ocupacion_por_quirofano(
    df: pd.DataFrame,
    horas_capacidad_diaria: float = 8.0,
) -> pd.DataFrame:
    """
    Calcula ocupación promedio por quirófano.
    Asume capacidad fija diaria.
    """
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    dias = df.groupby("quirofano")["fecha"].nunique().reset_index()
    dias = dias.rename(columns={"fecha": "dias_operativos"})

    horas = horas_por_quirofano(df)

    merged = horas.merge(dias, on="quirofano", how="left")
    merged["capacidad_total"] = merged["dias_operativos"] * horas_capacidad_diaria
    merged["ocupacion_pct"] = (
        merged["total_horas"] / merged["capacidad_total"] * 100
    ).round(1)

    return merged
