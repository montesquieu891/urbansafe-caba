import numpy as np
import pandas as pd

from src import classification as Cl


def _toy(months=6, n=20, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for m in pd.period_range("2022-01", periods=months, freq="M"):
        y = rng.permutation(n) + 5            # conteos sin empates: el ranking correcto es inequívoco
        rank = (-y).argsort().argsort()
        for i in range(n):
            rows.append({"barrio": f"b{i:02d}", "mes_objetivo": m, "y_target": y[i], "top10_target": rank[i] < 10,
                         "perfecto": y[i] + rng.random() * .01, "malo": -y[i]})
    return pd.DataFrame(rows)


def test_precision_at_k_extremos():
    d = _toy()
    assert np.isclose(Cl.precision_at_k(d, "perfecto").mean(), 1.0)
    assert Cl.precision_at_k(d, "malo").mean() < .5


def test_expected_precision_y_pareado():
    d = _toy()
    assert np.isclose(Cl.expected_precision_at_k(d, "y_target").mean(), 1.0)
    r = Cl.paired_tie_interval(d, "perfecto", "malo", seeds=20)
    assert r["p2.5"] > 0 and r["excluye_0"]
    z = Cl.paired_tie_interval(d, "perfecto", "perfecto", seeds=10)
    assert z["p2.5"] == z["p97.5"] == 0


def test_familias_cubren_todas_las_variables():
    for c in Cl.FEATURES_LOGIT + Cl.FEATURES_TREE + ["comuna_3"]:
        Cl.familia_de(c)


def test_grilla_acotada():
    g = Cl.grid()
    for fam in ("logit", "rf", "hgb"):
        assert 0 < sum(k == fam for k, _ in g) <= 30
