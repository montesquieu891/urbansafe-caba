import numpy as np
import pandas as pd
import pytest

from src import profiles as P

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def data():
    h = pd.read_csv(ROOT / "data" / "processed" / "hechos_clean.csv", dtype={"mes": str}, low_memory=False)
    area = pd.read_csv(ROOT / "data" / "processed" / "panel_barrio_mes.csv").groupby("barrio")["area_km2"].first()
    return h, area


def test_ventana_por_defecto_sin_test_ni_anomalias():
    m = P.default_months()
    assert max(m) == "2024-12" and "2019-11" not in m and "2020-04" not in m and len(m) == 55


def test_rechaza_meses_de_test(data):
    h, area = data
    with pytest.raises(ValueError):
        P.build_attributes(h, area, ["2024-12", "2025-01"])


def test_proporciones_suman_uno_y_cubren_48_barrios(data):
    h, area = data
    A = P.build_attributes(h, area, P.default_months())
    assert len(A) == 48
    for grupo in (P.ATTR_HORARIO[:-1], P.ATTR_ESTACION, P.ATTR_MODO):
        assert np.allclose(A[grupo].sum(axis=1), 1.0)


def test_atributos_no_cambian_si_cambia_el_test(data):
    h, area = data
    h2 = h.copy()
    m = h2["mes"] >= "2025-01"
    h2.loc[m, "modo_victima"] = "PEATON"
    h2.loc[m, "hora_entera"] = 3
    a, b = P.build_attributes(h, area, P.default_months()), P.build_attributes(h2, area, P.default_months())
    pd.testing.assert_frame_equal(a, b)
