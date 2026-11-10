import numpy as np
import pandas as pd

from src import regression as R
from src.evaluation import block_bootstrap_ci, regression_metrics


def test_regression_metrics_basicas():
    m = regression_metrics([0, 2, 4], [1, 2, 3])
    assert np.isclose(m["MAE"], 2 / 3) and np.isclose(m["sesgo"], 0) and m["n"] == 3 and m["devianza_poisson"] > 0


def test_block_bootstrap_reproducible_y_centrado():
    s = pd.Series(np.r_[np.ones(6), -np.ones(6)] * .1 + .5)
    a, b = block_bootstrap_ci(s), block_bootstrap_ci(s)
    assert a == b and a["ic_inf"] <= a["media"] <= a["ic_sup"]


def test_grilla_acotada_por_familia():
    g = R.grid()
    for fam in ("poisson", "negbin", "hgb"):
        assert 0 < sum(k == fam for k, _ in g) <= 30


def test_log_features_sin_ajuste():
    X = pd.DataFrame({c: [0.0, 9.0] for c in R.COUNT_COLS})
    out = R.add_log_features(X)
    assert np.allclose(out["log_y_lag1"], [0, np.log(10)])


def test_negbin_predice_positivo_e_intervalo():
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(400, len(R.FEATURES_COMPACTO))), columns=R.FEATURES_COMPACTO)
    y = rng.negative_binomial(5, 5 / (5 + np.exp(1 + .3 * X.iloc[:, 0])))
    m = R.NegBinNB2().fit(X, y)
    p = m.predict(X)
    lo, hi = m.interval(X, .8)
    assert (p > 0).all() and (lo <= hi).all() and m.alpha_ > 0


def test_topk_coverage_oraculo_y_rango():
    from src.evaluation import topk_coverage
    d = pd.DataFrame({"barrio": list("abcd") * 2, "mes_objetivo": [pd.Period("2024-01", "M")] * 4 + [pd.Period("2024-02", "M")] * 4,
                      "y_target": [5, 3, 1, 1, 0, 2, 2, 6]})
    oracle = topk_coverage(d, "y_target", 1)
    assert np.allclose(oracle.to_numpy(), [0.5, 0.6])
    anti = topk_coverage(d.assign(s=-d["y_target"]), "s", 1)
    assert (anti <= oracle).all() and (anti >= 0).all()
