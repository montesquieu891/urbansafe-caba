"""Etiquetado top-K con desempate explícito (decisión D6.1 del informe de viabilidad).

R0: exactamente k positivos por período. El orden es por puntaje descendente; los empates se
resuelven con una clave pseudoaleatoria uniforme generada con
``numpy.random.default_rng([seed, ordinal del período])`` sobre las unidades ordenadas por nombre.
La regla es reproducible, neutral y no usa el historial ni los predictores.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261110


def top_k_labels(df: pd.DataFrame, unit: str, per: str, k: int, seed: int = SEED, ycol: str = "y") -> pd.Series:
    """Devuelve una serie booleana alineada con ``df``: True para las k unidades de mayor ``ycol`` en cada período.

    ``per`` puede contener ``pandas.Period`` o texto 'AAAA-MM'; el ordinal se calcula como período mensual.
    """
    out = pd.Series(False, index=df.index)
    for prd, g in df.groupby(per, sort=False):
        p = prd if isinstance(prd, pd.Period) else pd.Period(str(prd), freq="M")
        g = g.sort_values(unit)
        key = np.random.default_rng([seed, int(p.ordinal)]).random(len(g))
        order = np.lexsort((key, -g[ycol].to_numpy(dtype=float)))
        out.loc[g.index[order[:k]]] = True
    return out


def inclusion_prob(scores, k: int) -> np.ndarray:
    """Probabilidad de que cada unidad quede en el top-k si los empates del corte se resuelven al azar."""
    s = np.asarray(scores, float)
    c = np.sort(s)[::-1][k - 1]
    above, tied = (s > c).sum(), (s == c).sum()
    return np.where(s > c, 1.0, np.where(s == c, (k - above) / tied, 0.0))
