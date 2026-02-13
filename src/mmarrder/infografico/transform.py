from __future__ import annotations

import numpy as np
import pandas as pd

from mmarrder.transform.periodos import DICT_MESES


def normalizar_periodos_consulta_externa(df, columna_id):
    df = df.melt(
        id_vars=columna_id,
        var_name='mes',
        value_name='produccion'
    )

    df['año'] = df['mes'].apply(lambda x: np.nan if isinstance(x, str) else str(x))
    df['mes_txt'] = df['mes'].astype(str).str[:3].str.upper()
    df['mes'] = df['mes_txt'].map(DICT_MESES)
    df['año'] = df['año'].bfill()
    df[columna_id[0]] = df[columna_id[0]].ffill()
    df['periodo'] = df['año'] + '-' + df['mes'] + '-01'
    df['periodo'] = pd.to_datetime(df['periodo'], errors='coerce')
    df['produccion'] = pd.to_numeric(df['produccion'], errors='coerce').fillna(0)

    df = (
        df[['periodo', columna_id[0], columna_id[1] ,'produccion']]
        .dropna(subset=['periodo'])
    )

    return df
