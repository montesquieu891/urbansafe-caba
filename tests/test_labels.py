import numpy as np
import pandas as pd

from src.labels import inclusion_prob, top_k_labels


def _df():
    # mes 1: empate en el corte (c, d, e = 5) con k = 3; mes 2: sin empate
    return pd.DataFrame({"u": list("abcde") * 2,
                         "mes": ["2020-01"] * 5 + ["2020-02"] * 5,
                         "y": [9, 8, 5, 5, 5, 1, 2, 3, 4, 5]})


def test_exactamente_k_por_periodo_y_reproducible():
    d = _df()
    a, b = top_k_labels(d, "u", "mes", 3), top_k_labels(d, "u", "mes", 3)
    assert (a == b).all()
    assert a.groupby(d["mes"]).sum().tolist() == [3, 3]
    assert a[d["u"].isin(["a", "b"]) & (d["mes"] == "2020-01")].all()      # puestos inequívocos
    assert a[d["mes"] == "2020-02"].tolist() == [False, False, True, True, True]


def test_desempate_no_depende_del_orden_de_filas():
    d = _df()
    shuffled = d.sample(frac=1, random_state=1)
    assert (top_k_labels(d, "u", "mes", 3).sort_index() == top_k_labels(shuffled, "u", "mes", 3).sort_index()).all()


def test_inclusion_prob():
    p = inclusion_prob([9, 8, 5, 5, 5], 3)
    assert np.allclose(p, [1, 1, 1 / 3, 1 / 3, 1 / 3]) and np.isclose(p.sum(), 3)
