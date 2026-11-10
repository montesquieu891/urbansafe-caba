"""Invariantes del ETL (Paso 04): claves, cardinalidad, recuentos, cobertura y reglas de asignación.

Requiere que existan los datos brutos en data/raw (ver README). La primera prueba de la sesión
ejecuta el ETL completo en un directorio temporal, sin tocar data/processed.
"""
import json

import numpy as np
import pandas as pd
import pytest

from src import data_processing as dp


# ---------------------------------------------------------------- unidades
def test_parse_comuna():
    s = pd.Series(["Comuna 1", "COMUNA 15", "3", "SD", None, "Comuna 99"])
    assert dp.parse_comuna(s).tolist() == [1, 15, 3, pd.NA, pd.NA, pd.NA]


def test_parse_planar_formats():
    s = pd.Series(["POINT (101813.8 95578.5)", "POINT(97439.07 103559.4)", "POINT(100.937.5 96.73300)",
                   "POINT (SD SD)", "POINT(105.15686 103.76)", None])
    xy = dp.parse_planar(s)
    assert xy["x_plana"].iloc[0] == pytest.approx(101813.8) and xy["x_plana"].iloc[1] == pytest.approx(97439.07)
    assert xy.iloc[2:].isna().all().all()


def test_norm_cat():
    out = dp.norm_cat(pd.Series([" auto", "MOTO", "#¡REF!", None, "sd"]))
    assert out.tolist() == ["AUTO", "MOTO", "SD", "SD", "SD"]


def test_flag_meses():
    f = dp.flag_meses(pd.Series(["2019-11", "2020-04", "2021-05", "2021-06", "2025-01"]))
    assert f.tolist() == ["registro", "pandemia", "pandemia", "ninguna", "ninguna"]


# ---------------------------------------------------------------- integración
@pytest.fixture(scope="session")
def outputs(tmp_path_factory):
    out = tmp_path_factory.mktemp("processed")
    qa = dp.run(download=False, accept_new_version=False, out=out)
    read = lambda f: pd.read_csv(out / f, dtype={"mes": str}, low_memory=False)
    return {"qa": qa, "h": read("hechos_clean.csv"), "v": read("victimas_clean.csv"),
            "pb": read("panel_barrio_mes.csv"), "pc": read("panel_comuna_mes.csv"),
            "ex": read("registro_exclusiones.csv"), "dir": out}


def test_fuentes_verificadas(outputs):
    for key in ("hechos", "victimas", "barrios", "comunas"):
        assert outputs["qa"]["fuentes"][key]["estado"] == "verificado"


def test_hechos_sin_perdidas_y_clave_unica(outputs):
    h = outputs["h"]
    assert len(h) == outputs["qa"]["hechos"]["filas_fuente"] == 65818
    assert h["id_siniestro"].is_unique and h["id_siniestro"].notna().all()
    assert set(h["tipo_sumario"]) == {"lesiones", "homicidio"}
    assert ((h["tipo_sumario"] == "homicidio") == (h["gravedad"] == "MORTAL")).all()


def test_fechas_y_particion(outputs):
    h = outputs["h"]
    f = pd.to_datetime(h["fecha"])
    assert f.notna().all() and f.min() >= pd.Timestamp("2019-01-01") and f.max() <= pd.Timestamp("2025-12-31")
    assert (h.loc[h["mes"] >= "2025-01", "particion"] == "test").all()
    assert (h.loc[h["mes"] < "2025-01", "particion"] == "desarrollo").all()


def test_categorias_estandarizadas(outputs):
    h = outputs["h"]
    assert set(h["gravedad"]) == {"LEVE", "GRAVE", "MORTAL"}
    for c in ("modo_victima", "contraparte", "tipo_de_via"):
        vals = h[c].dropna()
        assert (vals == vals.str.upper()).all() and not vals.isin(list(dp.VALORES_INVALIDOS)).any()
    assert h["comuna_fuente"].dropna().between(1, 15).all()


def test_coordenadas_validas(outputs):
    h = outputs["h"]
    has = h["lat"].notna()
    assert (h.loc[has, "lat"].between(-34.71, -34.52) & h.loc[has, "lon"].between(-58.54, -58.33)).all()
    assert (has == h["lon"].notna()).all()


def test_regla_asignacion_d9(outputs):
    h = outputs["h"]
    assert set(h["metodo_asignacion"]) <= {"within", "nearest_200m", "sin_coordenada"}
    assert (h["en_panel_barrio"] == h["lat"].notna()).all()             # toda coordenada válida se asigna
    assert (h["en_panel_barrio"] == h["barrio"].notna()).all()
    assert h.loc[h["en_panel_barrio"], "comuna"].notna().all()
    solo_comuna = h["en_panel_comuna"] & ~h["en_panel_barrio"]
    assert (h.loc[solo_comuna, "comuna"] == h.loc[solo_comuna, "comuna_fuente"]).all()


def test_conciliacion_hechos_victimas(outputs):
    h, v = outputs["h"], outputs["v"]
    assert len(v) == 75197 and v["id_victima_etl"].is_unique
    vin = v.dropna(subset=["id_siniestro"])
    assert vin["id_siniestro"].isin(h["id_siniestro"]).all()             # sin huérfanos
    assert h["id_siniestro"].isin(vin["id_siniestro"]).all()             # todo hecho tiene víctimas
    filas = vin.groupby("id_siniestro").size().reindex(h["id_siniestro"]).to_numpy()
    assert (h["n_victimas"].to_numpy() == filas).all()
    assert (h["n_victimas"] == h["n_leves"] + h["n_graves"] + h["n_mortales"]).all()


@pytest.mark.parametrize("panel,unit,n_units", [("pb", "barrio", 48), ("pc", "comuna", 15)])
def test_panel_completo(outputs, panel, unit, n_units):
    p = outputs[panel]
    assert len(p) == n_units * 84
    assert p[[unit, "mes"]].drop_duplicates().shape[0] == len(p)
    assert p[unit].nunique() == n_units and p["mes"].nunique() == 84
    counts = [c for c in p.columns if c.startswith(("y_", "hechos_modo_", "n_posible"))]
    assert p[counts].notna().all().all() and (p[counts] >= 0).all().all()
    assert (p["particion"] == np.where(p["mes"] >= "2025-01", "test", "desarrollo")).all()


@pytest.mark.parametrize("panel,unit,flag", [("pb", "barrio", "en_panel_barrio"), ("pc", "comuna", "en_panel_comuna")])
def test_panel_concilia_con_hechos(outputs, panel, unit, flag):
    h, p = outputs["h"], outputs[panel]
    d = h[h[flag]]
    assert p["y_hechos"].sum() == len(d)
    assert p["y_victimas"].sum() == d["n_victimas"].sum()
    assert p["y_ksi"].sum() == d["ksi"].sum()
    modo = [c for c in p.columns if c.startswith("hechos_modo_")]
    assert (p[modo].sum(axis=1) == p["y_hechos"]).all()
    by_month = d.groupby("mes").size().reindex(p["mes"].unique(), fill_value=0)
    assert (p.groupby("mes")["y_hechos"].sum().reindex(by_month.index) == by_month).all()


def test_registro_de_exclusiones_completo(outputs):
    h, v, ex = outputs["h"], outputs["v"], outputs["ex"]
    fuera_barrio = set(h.loc[~h["en_panel_barrio"], "id_siniestro"])
    assert fuera_barrio == set(ex.loc[ex["tabla"] == "hechos", "id"])     # toda exclusión tiene motivo
    assert ex["motivo"].notna().all() and ex["alcance"].notna().all()
    assert set(v.loc[v["sin_id_hecho"], "id_victima_etl"].astype(str)) == set(ex.loc[ex["tabla"] == "victimas", "id"])


def test_valores_auditados_paso03(outputs):
    """Los conteos deben coincidir con la auditoría (feasibility_metrics.json)."""
    qa = outputs["qa"]
    assert qa["hechos"]["metodo_asignacion"] == {"within": 62500, "nearest_200m": 287, "sin_coordenada": 3031}
    assert qa["paneles"]["barrio_mes"]["y_hechos_desarrollo"] == 51688
    assert qa["hechos"]["posible_duplicado"] == 274 and qa["hechos"]["grupos_duplicado"] == 134
    assert qa["hechos"]["comuna_discordante"] == 2329


def test_qa_report_serializable(outputs):
    json.loads((outputs["dir"] / "qa_report.json").read_text(encoding="utf-8"))
