"""Clasificación y priorización top-K para el Paso 08 (protocolo, secciones 5 y 6).

Objetivo: ``top10_target`` (el barrio está entre los 10 con más hechos del mes T, regla R0).
Candidatos: regresión logística L2, *random forest* y ``HistGradientBoostingClassifier``, con ponderación de clases como
hiperparámetro. SMOTE no se aplica (prevalencia fija del 20,8 %; protocolo, sección 11).
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from src import features as F
from src import regression as R
from src.labels import inclusion_prob, top_k_labels

SEED = 20261110
K = 10
BASELINES = {"persistencia": "y_lag1", "media12": "y_ma12"}
FEATURES_LOGIT = R.FEATURES_GLM_COMPLETO          # versiones log de los conteos más el resto de FEATURES_MAIN
FEATURES_TREE = F.FEATURES_MAIN
FAMILIAS_SHAP = {
    "Historial del barrio": ["y_lag1", "y_lag2", "y_lag3", "y_lag12", "y_ma3", "y_ma6", "y_ma12", "tendencia_ma3_ma12", "densidad_ma12"],
    "Historial relativo (participación, puesto, top 10)": ["share_lag1", "share_ma12", "rank_lag1", "rank_ma12", "top10_freq12"],
    "Nivel de la ciudad": ["ciudad_lag1", "ciudad_ma12", "ciudad_lag12"],
    "Calendario y pandemia": ["mes_sin", "mes_cos", "n_pandemia_ventana12"],
    "Territorio (superficie, comuna)": ["area_km2", "comuna"],
    "Vecindad": ["vecinos_ma3", "vecinos_share_ma12"],
    "Composición modal": [f"comp_{m}_12m" for m in F.MODOS],
}


def familia_de(col: str) -> str:
    base = col[4:] if col.startswith("log_") else col
    base = "comuna" if base.startswith("comuna") else base
    for fam, cols in FAMILIAS_SHAP.items():
        if base in cols:
            return fam
    raise KeyError(col)


# --------------------------------------------------------------------------- modelos
def make_model(kind: str, params: dict):
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    if kind == "logit":
        pre = ColumnTransformer([("num", StandardScaler(), FEATURES_LOGIT),
                                 ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["comuna"])],
                                verbose_feature_names_out=False)
        return Pipeline([("pre", pre), ("clf", LogisticRegression(C=params["C"], class_weight=params["class_weight"],
                                                                  max_iter=5000))])
    if kind == "rf":
        pre = ColumnTransformer([("num", "passthrough", FEATURES_TREE),
                                 ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["comuna"])],
                                verbose_feature_names_out=False)
        return Pipeline([("pre", pre), ("clf", RandomForestClassifier(
            n_estimators=300, max_depth=params["max_depth"], min_samples_leaf=params["min_samples_leaf"],
            class_weight=params["class_weight"], max_features="sqrt", n_jobs=-1, random_state=SEED))])
    if kind == "hgb":
        pre = ColumnTransformer([("num", "passthrough", FEATURES_TREE), ("cat", "passthrough", ["comuna"])],
                                verbose_feature_names_out=False)
        return Pipeline([("pre", pre), ("clf", HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=200, max_leaf_nodes=params["max_leaf_nodes"],
            min_samples_leaf=params["min_samples_leaf"], class_weight=params["class_weight"], l2_regularization=1.0,
            categorical_features=[len(FEATURES_TREE)], random_state=SEED))])
    raise ValueError(kind)


def grid() -> list[tuple[str, dict]]:
    """Grillas acotadas (≤ 30 por familia); `excluir_pandemia` es un hiperparámetro."""
    g = []
    for C, cw, ex in itertools.product([0.01, 0.1, 1.0, 10.0], [None, "balanced"], [False, True]):
        g.append(("logit", {"C": C, "class_weight": cw, "excluir_pandemia": ex}))
    for md, msl, cw, ex in itertools.product([4, 8, None], [5, 20], [None, "balanced_subsample"], [False, True]):
        g.append(("rf", {"max_depth": md, "min_samples_leaf": msl, "class_weight": cw, "excluir_pandemia": ex}))
    for leaves, msl, cw, ex in itertools.product([7, 15], [20, 60], [None, "balanced"], [False, True]):
        g.append(("hgb", {"max_leaf_nodes": leaves, "min_samples_leaf": msl, "class_weight": cw, "excluir_pandemia": ex}))
    return g


def config_name(kind, params):
    return kind + "|" + ",".join(f"{k}={v}" for k, v in params.items())


# --------------------------------------------------------------------------- métricas top-K
def precision_at_k(df: pd.DataFrame, score: str, label: str = "top10_target", k: int = K, seed: int = SEED + 1) -> pd.Series:
    """Precision@k por mes: el top-k por `score` (desempate R0 con `seed`) contra las etiquetas de `label`."""
    sel = top_k_labels(df, "barrio", "mes_objetivo", k, seed=seed, ycol=score)
    return (sel & df[label].astype(bool)).groupby(df["mes_objetivo"]).sum() / k


def expected_precision_at_k(df: pd.DataFrame, score: str, k: int = K, ycol: str = "y_target") -> pd.Series:
    """Precision@k esperada invariante a empates: Σ P(i∈S)·P(i∈P)/k, con los empates de S y de P resueltos al azar."""
    return df.groupby("mes_objetivo").apply(
        lambda g: float((inclusion_prob(g[score], k) * inclusion_prob(g[ycol], k)).sum() / k))


def paired_tie_interval(df: pd.DataFrame, score_a: str, score_b: str, seeds: int = 500, k: int = K, base_seed: int = SEED) -> dict:
    """ΔP@k = P@k(a) − P@k(b) en cada repetición, con las mismas etiquetas (desempate R0 con la semilla de la
    repetición) y los mismos meses para ambos rankings. Devuelve los percentiles 2,5–97,5 (sensibilidad al desempate)."""
    d = np.empty(seeds)
    for s in range(seeds):
        lab = top_k_labels(df, "barrio", "mes_objetivo", k, seed=base_seed + 1000 + s, ycol="y_target")
        tmp = df.assign(_lab=lab.to_numpy())
        pa = precision_at_k(tmp, score_a, "_lab", k, seed=base_seed + 5000 + s)
        pb = precision_at_k(tmp, score_b, "_lab", k, seed=base_seed + 5000 + s)
        d[s] = (pa - pb).mean()
    return {"mediana": float(np.median(d)), "p2.5": float(np.quantile(d, .025)), "p97.5": float(np.quantile(d, .975)),
            "excluye_0": bool(np.quantile(d, .025) > 0 or np.quantile(d, .975) < 0), "semillas": seeds}


def uncertain_slots_precision(df: pd.DataFrame, score: str, core: set, k: int = K, seed: int = SEED + 1) -> dict:
    """Precisión en las plazas inciertas: entre los barrios seleccionados que no pertenecen al núcleo persistente."""
    sel = top_k_labels(df, "barrio", "mes_objetivo", k, seed=seed, ycol=score)
    nc = ~df["barrio"].isin(core)
    s, h = int((sel & nc).sum()), int((sel & nc & df["top10_target"].astype(bool)).sum())
    return {"seleccionados_fuera_del_nucleo": s, "aciertos": h, "precision": h / s if s else float("nan")}


def core_from_training(train: pd.DataFrame, thr: float = .8) -> set:
    """Núcleo persistente: barrios en el top 10 en más del 80 % de los meses objetivo del entrenamiento."""
    f = train.groupby("barrio")["top10_target"].mean()
    return set(f[f > thr].index)
