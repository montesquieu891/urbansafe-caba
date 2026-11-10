"""Métricas y estimación de incertidumbre compartidas por los Pasos 07, 08 y 10 (protocolo, sección 5)."""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261110


def regression_metrics(y, yhat) -> dict:
    y, yhat = np.asarray(y, float), np.clip(np.asarray(yhat, float), 1e-9, None)
    e = yhat - y
    with np.errstate(divide="ignore", invalid="ignore"):
        dev = 2 * (np.where(y > 0, y * np.log(y / yhat), 0.0) - (y - yhat))
    return {"MAE": float(np.mean(np.abs(e))), "RMSE": float(np.sqrt(np.mean(e ** 2))),
            "devianza_poisson": float(np.mean(dev)), "sesgo": float(np.mean(e)), "n": int(len(y))}


def monthly_series(df: pd.DataFrame, value: str, month_col: str = "mes_objetivo") -> pd.Series:
    """Media mensual de una columna (p. ej., la diferencia de errores absolutos entre modelo y baseline)."""
    return df.groupby(month_col)[value].mean().sort_index()


def topk_coverage(df: pd.DataFrame, score: str, k: int, seed: int = SEED + 1, y: str = "y_target",
                  unit: str = "barrio", month: str = "mes_objetivo") -> pd.Series:
    """Cobertura mensual: proporción de los hechos del mes que ocurren en las k unidades seleccionadas por `score`
    (desempate R0 con `seed`). Es la métrica de utilidad de la priorización (H5)."""
    from src.labels import top_k_labels
    sel = top_k_labels(df, unit, month, k, seed=seed, ycol=score)
    tot = df.groupby(month)[y].sum()
    return (df[y].where(sel, 0).groupby(df[month]).sum() / tot).rename(score)


def block_bootstrap_ci(monthly: pd.Series, block: int = 3, reps: int = 2000, seed: int = SEED, alpha: float = .05) -> dict:
    """Bootstrap por bloques móviles sobre una serie mensual. Devuelve la media observada y el IC (percentil).

    Se remuestrean bloques consecutivos de `block` meses con reposición hasta cubrir la longitud original, lo que
    preserva la dependencia temporal de corto plazo. La incertidumbre entre períodos se mide aparte de la
    sensibilidad al desempate.
    """
    x = np.asarray(monthly, float)
    n = len(x)
    if n < block:
        raise ValueError("Serie más corta que el bloque")
    rng = np.random.default_rng(seed)
    starts = np.arange(n - block + 1)
    nb = int(np.ceil(n / block))
    stats_ = np.empty(reps)
    for r in range(reps):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.choice(starts, nb)])[:n]
        stats_[r] = x[idx].mean()
    return {"media": float(x.mean()), "ic_inf": float(np.quantile(stats_, alpha / 2)),
            "ic_sup": float(np.quantile(stats_, 1 - alpha / 2)), "bloque": block, "reps": reps, "meses": n}
