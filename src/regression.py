"""Modelos de conteo para el Paso 07 (protocolo, sección 6).

Candidatos:
- ``poisson``: GLM Poisson con penalización L2 (scikit-learn ``PoissonRegressor``).
- ``negbin``: binomial negativa NB2 con α estimado por máxima verosimilitud (statsmodels), sobre el conjunto compacto.
- ``hgb``: *gradient boosting* de histogramas con pérdida Poisson (``HistGradientBoostingRegressor``).

Todo el preprocesamiento se ajusta dentro del Pipeline y, por lo tanto, solo con el entrenamiento del *fold*.
Las transformaciones logarítmicas son deterministas y operan fila por fila, sin ajuste.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy import stats

from src import features as F

SEED = 20261110
COUNT_COLS = ["y_lag1", "y_lag2", "y_lag3", "y_lag12", "y_ma3", "y_ma6", "y_ma12", "densidad_ma12",
              "ciudad_lag1", "ciudad_ma12", "ciudad_lag12", "vecinos_ma3", "area_km2"]
LOG_COLS = [f"log_{c}" for c in COUNT_COLS]
OTHER_MAIN = [c for c in F.FEATURES_MAIN if c not in COUNT_COLS]
FEATURES_GLM_COMPLETO = LOG_COLS + OTHER_MAIN
FEATURES_COMPACTO = ["log_y_ma12", "log_y_ma3", "log_y_lag1", "log_y_lag12", "log_vecinos_ma3",
                     "log_ciudad_lag1", "log_ciudad_ma12", "tendencia_ma3_ma12", "mes_sin", "mes_cos", "n_pandemia_ventana12"]
BASELINES = {"persistencia": "y_lag1", "estacional": "y_lag12", "media12": "y_ma12"}


def add_log_features(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for c in COUNT_COLS:
        X[f"log_{c}"] = np.log1p(X[c])
    return X


# --------------------------------------------------------------------------- modelos
class NegBinNB2:
    """Binomial negativa NB2 (statsmodels) con estandarización ajustada solo en el entrenamiento."""

    def __init__(self, features=None):
        self.features = features or FEATURES_COMPACTO

    def fit(self, X, y):
        import statsmodels.api as sm
        Z = X[self.features].to_numpy(float)
        self.mu_, self.sd_ = Z.mean(0), Z.std(0) + 1e-12
        Zs = sm.add_constant((Z - self.mu_) / self.sd_, has_constant="add")
        self.res_ = sm.NegativeBinomial(np.asarray(y, float), Zs).fit(disp=0, maxiter=500, method="bfgs")
        self.alpha_ = float(self.res_.params[-1])
        return self

    def predict(self, X):
        import statsmodels.api as sm
        Zs = sm.add_constant((X[self.features].to_numpy(float) - self.mu_) / self.sd_, has_constant="add")
        return np.asarray(self.res_.predict(Zs), float)

    def interval(self, X, level=.8):
        """Intervalo de predicción de la NB2 (cuantiles de la distribución, sin incertidumbre de parámetros)."""
        mu = self.predict(X)
        n = 1 / self.alpha_
        p = n / (n + mu)
        a = (1 - level) / 2
        return stats.nbinom.ppf(a, n, p), stats.nbinom.ppf(1 - a, n, p)


class NegBinNB2Reg(NegBinNB2):
    """NB2 con penalización L2 (desviación post hoc registrada en el protocolo, sección 11).

    1. Se ajusta un GLM Poisson con L2 (`lam`) y se estima α por momentos con sus residuos:
       α = Σ((y − μ)² − y) / Σμ², acotado a ≥ 1e-6.
    2. Se ajusta un GLM NB(α) con L2 (`lam`), sin penalizar el intercepto (statsmodels, elastic net con L1_wt = 0).
    Todo se calcula con el entrenamiento del fold.
    """

    def __init__(self, lam: float, features=None):
        super().__init__(features)
        self.lam = lam

    def fit(self, X, y):
        import statsmodels.api as sm
        y = np.asarray(y, float)
        Z = X[self.features].to_numpy(float)
        self.mu_, self.sd_ = Z.mean(0), Z.std(0) + 1e-12
        Zs = sm.add_constant((Z - self.mu_) / self.sd_, has_constant="add")
        pen = np.r_[0.0, np.full(Zs.shape[1] - 1, self.lam)]
        pois = sm.GLM(y, Zs, family=sm.families.Poisson()).fit_regularized(alpha=pen, L1_wt=0.0, maxiter=500)
        mu = np.asarray(pois.predict(Zs))
        self.alpha_ = float(max(((y - mu) ** 2 - y).sum() / (mu ** 2).sum(), 1e-6))
        self.res_ = sm.GLM(y, Zs, family=sm.families.NegativeBinomial(alpha=self.alpha_)).fit_regularized(
            alpha=pen, L1_wt=0.0, maxiter=500)
        return self

    def predict(self, X):
        import statsmodels.api as sm
        Zs = sm.add_constant((X[self.features].to_numpy(float) - self.mu_) / self.sd_, has_constant="add")
        return np.exp(Zs @ np.asarray(self.res_.params))


def grid_posthoc() -> list[tuple[str, dict]]:
    """Grilla añadida después de ver el test (desviación registrada). No es confirmatoria."""
    return [("negbin_reg", {"conjunto": "compacto", "lam": lam, "excluir_pandemia": ex})
            for lam, ex in itertools.product([1e-3, 1e-2, 1e-1, 1.0], [False, True])]


def make_model(kind: str, params: dict):
    if kind == "negbin_reg":
        return NegBinNB2Reg(params["lam"], FEATURES_COMPACTO)
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import PoissonRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    if kind == "poisson":
        feats = FEATURES_GLM_COMPLETO if params["conjunto"] == "completo" else FEATURES_COMPACTO
        cat = ["comuna"] if params["conjunto"] == "completo" else []
        pre = ColumnTransformer([("num", StandardScaler(), feats)] +
                                ([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)] if cat else []))
        return Pipeline([("pre", pre), ("glm", PoissonRegressor(alpha=params["alpha"], max_iter=3000))])
    if kind == "negbin":
        return NegBinNB2(FEATURES_COMPACTO)
    if kind == "hgb":
        feats = F.FEATURES_MAIN + ["comuna"]
        pre = ColumnTransformer([("num", "passthrough", F.FEATURES_MAIN),
                                 ("cat", "passthrough", ["comuna"])])
        return Pipeline([("pre", pre), ("hgb", HistGradientBoostingRegressor(
            loss="poisson", learning_rate=params["learning_rate"], max_leaf_nodes=params["max_leaf_nodes"],
            min_samples_leaf=params["min_samples_leaf"], max_iter=params["max_iter"], l2_regularization=1.0,
            categorical_features=[len(feats) - 1], random_state=SEED))])
    raise ValueError(kind)


def grid() -> list[tuple[str, dict]]:
    """Grillas acotadas (protocolo 4.4: ≤ 30 combinaciones por familia). `excluir_pandemia` es un hiperparámetro."""
    g = []
    for conj, a, ex in itertools.product(["compacto", "completo"], [1e-4, 1e-3, 1e-2, 1e-1, 1.0], [False, True]):
        g.append(("poisson", {"conjunto": conj, "alpha": a, "excluir_pandemia": ex}))
    for ex in [False, True]:
        g.append(("negbin", {"conjunto": "compacto", "excluir_pandemia": ex}))
    for lr, leaves, msl, ex in itertools.product([0.03, 0.1], [7, 15], [20, 60], [False, True]):
        g.append(("hgb", {"learning_rate": lr, "max_leaf_nodes": leaves, "min_samples_leaf": msl,
                          "max_iter": 300 if lr == 0.03 else 120, "excluir_pandemia": ex}))
    return g


def train_mask_excluding_pandemia(X: pd.DataFrame, mask: np.ndarray, excluir: bool) -> np.ndarray:
    if not excluir:
        return mask
    return mask & ~X["mes_objetivo"].isin(F.PANDEMIA).to_numpy()


def config_name(kind: str, params: dict) -> str:
    return kind + "|" + ",".join(f"{k}={v}" for k, v in params.items())
