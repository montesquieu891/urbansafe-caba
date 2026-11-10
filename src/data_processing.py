"""ETL de UrbanSafe CABA (Paso 04).

Reconstruye los datos procesados a partir de las fuentes oficiales:

1. **Adquisición.** Descarga, si se pide, los archivos del manifiesto y verifica su SHA-256 frente a la versión
   auditada en los Pasos 02 y 03.
2. **Hechos.** Estandariza fechas, horas y categorías; valida coordenadas; parsea la coordenada plana;
   marca posibles duplicados y meses anómalos; asigna barrio y comuna con la regla D9 del informe
   de viabilidad.
3. **Víctimas.** Estandariza categorías y edad y concilia la relación 1:N con los hechos.
4. **Paneles completos.** Construye barrio × mes (principal) y comuna × mes (robustez) para 2019-01 a 2025-12,
   con ceros explícitos.
5. **Trazabilidad.** Escribe el registro de exclusiones y el informe de control de calidad.

No elimina registros de las tablas limpias: las exclusiones afectan solo a los paneles, se registran
por motivo y se conservan en los totales de la ciudad.

Uso (desde la raíz del proyecto):
    python -m src.data_processing [--download] [--accept-new-version]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CDN = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/"
USER_AGENT = "urbansafe-research-client"

# CRS plano de la fuente: Gauss-Krüger BA, datum Campo Inchauspe (identificado en el Paso 03)
CRS_CABA = ("+proj=tmerc +lat_0=-34.6297166 +lon_0=-58.4627 +k=1 +x_0=100000 +y_0=100000 "
            "+ellps=intl +towgs84=-148,136,90,0,0,0,0 +units=m +no_defs")
CRS_WGS84 = "EPSG:4326"

PERIOD_START, PERIOD_END = "2019-01", "2025-12"
TEST_START = "2025-01"                      # test provisorio (D3)
NEAREST_MAX_M = 200                         # D9: asignación por cercanía
PLANAR_DISCREPANCY_M = 500                  # umbral de discrepancia lat/lon frente a la coordenada plana
MESES_REGISTRO = ["2019-11", "2019-12"]     # D3: caída de registro en toda la ciudad
MESES_PANDEMIA = [str(p) for p in pd.period_range("2020-03", "2021-05", freq="M")]

# Categorías de modo de la víctima (hecho) agregadas para el panel
MODOS_PANEL = {"MOTO": "moto", "PEATON": "peaton", "BICICLETA": "bicicleta", "AUTO": "auto",
               "TRANSPORTE PUBLICO": "transporte_publico", "SD": "sd"}
VALORES_INVALIDOS = {"#¡REF!", "#REF!", "#�REF!", "NAN", ""}


@dataclass(frozen=True)
class SourceFile:
    key: str
    relpath: str        # ruta bajo data/raw
    url_path: str       # ruta bajo el CDN
    sha256: str         # hash de la versión auditada (docs/evidence/paso02/sha256.txt)
    required: bool = True


MANIFEST = [
    SourceFile("hechos", "siniestros/siniestros_viales_hechos.csv",
               "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_hechos.csv",
               "e1d232514458c110b5daee5350042e2d8d4b666f6caf4bce4d8675a1b8b93be5"),
    SourceFile("victimas", "siniestros/siniestros_viales_victimas.csv",
               "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_victimas.csv",
               "2d878e6123dda2b3b070c4eb9633a56ddda2548b8d190a800b511bdbae593e4e"),
    SourceFile("notas", "siniestros/NOTAS_SINIESTROS_VIALES_2019-2025.pdf",
               "transporte-y-obras-publicas/victimas-siniestros-viales/NOTAS_SINIESTROS_VIALES_2019-2025.pdf",
               "47b6e32bf27bf92b071445a02dfcc4ec11294ee5a95d36acd343c5b174bac424", required=False),
    SourceFile("barrios", "limites/barrios.geojson",
               "innovacion-transformacion-digital/barrios/barrios.geojson",
               "c24fabd01c61b889388f0a8cfd9ca4757c1f57583c0ffd1b4ed3b96d768bb655"),
    SourceFile("comunas", "limites/comunas.geojson",
               "innovacion-transformacion-digital/comunas/comunas.geojson",
               "a4a7be8222a6a5c4a5a28c5e6e1b5ff5b0f6ba25f2788250f0ab3f9d6d59959f"),
    SourceFile("callejero", "red_vial/callejero.geojson",
               "jefatura-de-gabinete-de-ministros/calles/callejero.geojson",
               "8f398258b9957effa5613423db83c94e3f9e1e04ecb6dc358db54872ae427211", required=False),
    SourceFile("cruces", "red_vial/cruces-semaforizados.csv",
               "transporte-y-obras-publicas/cruces-semaforizados/cruces-semaforizados.csv",
               "1283d338319a3706e045a02e96231572db92a8ffdbe5a57f1a0a187579eba527", required=False),
    SourceFile("conteo_2024", "exposicion/conteo_vehicular_2024.xlsx",
               "transporte-y-obras-publicas/volumen_vehicular/conteo_vehicular_2024.xlsx",
               "7fa2ae07e3e9339b4a1d0772b298c9380d7f370989fec66af5a5e847df3f488b", required=False),
    SourceFile("ubicaciones", "exposicion/ubicaciones.xlsx",
               "transporte-y-obras-publicas/volumen_vehicular/ubicaciones.xlsx",
               "596043f726cb401124ede25fc0d32cbb4e2be281e3d3de9483b6c9d14804c063", required=False),
    SourceFile("diccionario_conteo", "exposicion/diccionario_conteo_vehicular.xlsx",
               "transporte-y-obras-publicas/volumen_vehicular/diccionario_conteo_vehicular.xlsx",
               "5b5cc956fb04487d97d4e11ef16a125cef6b93520ceccb345ddb54847485c621", required=False),
]


# ---------------------------------------------------------------------------
# 1. Adquisición y verificación
# ---------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def acquire(download: bool, accept_new_version: bool, raw: Path = RAW) -> dict:
    """Descarga los archivos faltantes (si download) y verifica sus hashes."""
    status = {}
    for sf in MANIFEST:
        dest = raw / sf.relpath
        if not dest.exists() and download:
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(CDN + sf.url_path, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=600) as resp:
                dest.write_bytes(resp.read())
        if not dest.exists():
            if sf.required:
                raise FileNotFoundError(f"Falta {dest}. Ejecute con --download o copie el archivo (ver README).")
            status[sf.key] = {"estado": "ausente (opcional)"}
            continue
        actual = sha256(dest)
        ok = actual == sf.sha256
        if not ok and sf.required and not accept_new_version:
            raise ValueError(
                f"El hash de {sf.relpath} no coincide con la versión auditada.\n  esperado {sf.sha256}\n  obtenido {actual}\n"
                "La fuente pudo actualizarse. Use --accept-new-version para procesarla igual; quedará registrado.")
        status[sf.key] = {"estado": "verificado" if ok else "VERSION_NUEVA", "sha256": actual}
    return status


# ---------------------------------------------------------------------------
# 2. Utilidades de estandarización
# ---------------------------------------------------------------------------
def read_source_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False, na_values=[""])


def norm_cat(s: pd.Series, missing: str = "SD") -> pd.Series:
    """Mayúsculas, sin espacios extremos; vacíos y valores de error de planilla pasan a `missing`."""
    out = s.astype("string").str.strip().str.upper()
    out = out.mask(out.isna() | out.isin(VALORES_INVALIDOS), missing)
    return out


def parse_comuna(s: pd.Series) -> pd.Series:
    """'Comuna 1', 'COMUNA 1', '1' -> 1; 'SD' o vacío -> <NA>. Valores fuera de 1–15 -> <NA>."""
    n = pd.to_numeric(s.astype("string").str.extract(r"(\d+)")[0], errors="coerce").astype("Int64")
    return n.where(n.between(1, 15))


def parse_planar(s: pd.Series) -> pd.DataFrame:
    """Extrae x e y de 'POINT (x y)' o 'POINT(x y)'. Los valores mal formados quedan en NaN."""
    xy = s.astype("string").str.extract(r"^POINT ?\((-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)\)$")
    xy = xy.astype(float)
    xy.columns = ["x_plana", "y_plana"]
    # Valores con otra escala (p. ej. 105.15686), observados en 2024: no comparables
    xy[xy["x_plana"] < 1000] = np.nan
    return xy


def flag_meses(mes: pd.Series) -> pd.Series:
    m = mes.astype(str)
    return pd.Series(np.select([m.isin(MESES_REGISTRO), m.isin(MESES_PANDEMIA)], ["registro", "pandemia"], "ninguna"),
                     index=mes.index)


# ---------------------------------------------------------------------------
# 3. Hechos
# ---------------------------------------------------------------------------
def clean_hechos(raw: pd.DataFrame) -> pd.DataFrame:
    h = pd.DataFrame({"id_siniestro": raw["id_siniestro"].str.strip()})
    h["tipo_sumario"] = h["id_siniestro"].str[:2].map({"LC": "lesiones", "HC": "homicidio"})
    h["fecha"] = pd.to_datetime(raw["fecha_siniestro"], format="mixed", errors="coerce")
    hora = pd.to_datetime(raw["hora_siniestro"], format="%H:%M:%S", errors="coerce")
    h["hora"] = hora.dt.strftime("%H:%M:%S")
    h["hora_entera"] = hora.dt.hour.astype("Int64")
    h["mes"] = h["fecha"].dt.to_period("M").astype(str)
    h["anio"] = h["fecha"].dt.year.astype("Int64")
    h["dia_semana"] = h["fecha"].dt.day_of_week.astype("Int64")   # 0 = lunes
    for src, dst in [("numero_victimas_leve_siniestro", "n_leves"), ("numero_victimas_grave_siniestro", "n_graves"),
                     ("numero_victimas_mortal_siniestro", "n_mortales")]:
        h[dst] = pd.to_numeric(raw[src], errors="coerce").astype("Int64")
    h["n_victimas"] = (h["n_leves"] + h["n_graves"] + h["n_mortales"]).astype("Int64")
    h["gravedad"] = norm_cat(raw["gravedad_siniestro"])
    h["ksi"] = h["gravedad"].isin(["GRAVE", "MORTAL"])
    h["tipo_de_via"] = norm_cat(raw["tipo_de_via_siniestro"])
    h["modo_victima"] = norm_cat(raw["modo_desplazamiento_victima"])
    h["contraparte"] = norm_cat(raw["contraparte_siniestro"])
    h["participantes"] = norm_cat(raw["participantes_siniestro"])
    h["direccion_normalizada"] = raw["direccion_normalizada_siniestro"].astype("string").str.strip()
    h["comuna_fuente"] = parse_comuna(raw["comuna_siniestro"])
    lat = pd.to_numeric(raw["latitud_siniestro"], errors="coerce")
    lon = pd.to_numeric(raw["longitud_siniestro"], errors="coerce")
    valid = lat.between(-35, -34) & lon.between(-59, -58)
    h["lat"] = lat.where(valid)
    h["lon"] = lon.where(valid)
    h = pd.concat([h, parse_planar(raw["geocodificacion_plana"])], axis=1)
    h["anomalia_mes"] = flag_meses(h["mes"])
    h["particion"] = np.where(h["mes"] >= TEST_START, "test", "desarrollo")
    # Posibles duplicados: misma fecha, hora y lugar (aprox. 1 m) con distinto id (D10)
    key = pd.DataFrame({"f": h["fecha"].dt.strftime("%Y-%m-%d"), "h": h["hora"],
                        "la": h["lat"].round(5), "lo": h["lon"].round(5)})
    has = key.notna().all(axis=1)
    grp_size = key[has].groupby(["f", "h", "la", "lo"])["f"].transform("size")
    gid = key[has].groupby(["f", "h", "la", "lo"]).ngroup()
    h["dup_grupo"] = pd.Series(pd.NA, index=h.index, dtype="Int64")
    h.loc[grp_size[grp_size > 1].index, "dup_grupo"] = gid[grp_size > 1].astype("Int64")
    h["posible_duplicado"] = h["dup_grupo"].notna()
    return h


def assign_zones(h: pd.DataFrame, barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    """Regla D9: within -> barrio más cercano (≤ 200 m) -> comuna de la fuente -> exclusión del panel."""
    h = h.copy()
    pts = gpd.GeoDataFrame(h.loc[h["lat"].notna(), ["id_siniestro"]],
                           geometry=gpd.points_from_xy(h.loc[h["lat"].notna(), "lon"], h.loc[h["lat"].notna(), "lat"]),
                           crs=CRS_WGS84)
    bar = barrios[["barrio", "comuna", "geometry"]]
    j = gpd.sjoin(pts, bar, how="left", predicate="within")
    if j.index.duplicated().any():
        raise AssertionError("Un punto coincide con más de un barrio")
    miss = j["barrio"].isna()
    near = gpd.sjoin_nearest(pts.loc[miss].to_crs(CRS_CABA), bar.to_crs(CRS_CABA), how="left",
                             max_distance=NEAREST_MAX_M, distance_col="dist_m")
    near = near[~near.index.duplicated()]
    j.loc[near.index, ["barrio", "comuna"]] = near[["barrio", "comuna"]].values
    h["barrio"] = j["barrio"].reindex(h.index).astype("string")
    h["comuna_geo"] = pd.to_numeric(j["comuna"].reindex(h.index), errors="coerce").astype("Int64")
    metodo = pd.Series("sin_coordenada", index=h.index, dtype="string")
    metodo.loc[j.index[~miss]] = "within"
    metodo.loc[near.index[near["barrio"].notna()]] = "nearest_200m"
    metodo.loc[j.index[j["barrio"].isna()]] = "fuera_de_CABA"
    h["metodo_asignacion"] = metodo
    h["comuna"] = h["comuna_geo"].fillna(h["comuna_fuente"]).astype("Int64")
    h["comuna_discordante"] = h["comuna_geo"].notna() & h["comuna_fuente"].notna() & (h["comuna_geo"] != h["comuna_fuente"])
    # Discrepancia entre lat/lon y la coordenada plana
    ok = h["lat"].notna() & h["x_plana"].notna()
    geo = gpd.GeoSeries(gpd.points_from_xy(h.loc[ok, "lon"], h.loc[ok, "lat"]), crs=CRS_WGS84, index=h.index[ok]).to_crs(CRS_CABA)
    plana = gpd.GeoSeries(gpd.points_from_xy(h.loc[ok, "x_plana"], h.loc[ok, "y_plana"]), crs=CRS_CABA, index=h.index[ok])
    h["dist_plana_m"] = plana.distance(geo).reindex(h.index).round(2)
    h["discrepancia_plana"] = h["dist_plana_m"] > PLANAR_DISCREPANCY_M
    # Alcance en los paneles
    h["en_panel_barrio"] = h["barrio"].notna()
    h["en_panel_comuna"] = h["comuna"].notna()
    return h


# ---------------------------------------------------------------------------
# 4. Víctimas
# ---------------------------------------------------------------------------
def clean_victimas(raw: pd.DataFrame) -> pd.DataFrame:
    v = pd.DataFrame({"id_siniestro": raw["id_siniestro"].astype("string").str.strip()})
    v.insert(0, "id_victima_etl", range(1, len(v) + 1))      # id técnico: la fuente no tiene id de víctima
    v["fecha"] = pd.to_datetime(raw["fecha_siniestro"], format="mixed", errors="coerce")
    v["modo_victima"] = norm_cat(raw["modo_desplazamiento_victima"])
    v["sexo"] = norm_cat(raw["sexo_victima"])
    edad = pd.to_numeric(raw["edad_victima"], errors="coerce")
    v["edad"] = edad.astype("Int64")
    v["edad_fuera_de_rango"] = edad > 105
    v["gravedad"] = norm_cat(raw["GRAVEdad_victima"])
    v["rol"] = norm_cat(raw["rol_victima"])
    v["fecha_fallecimiento"] = pd.to_datetime(raw["fecha_fallecimiento_victima"], format="mixed", errors="coerce")
    v["fila_identica_en_fuente"] = raw.duplicated(keep=False)
    v["sin_id_hecho"] = v["id_siniestro"].isna()
    return v


# ---------------------------------------------------------------------------
# 5. Paneles
# ---------------------------------------------------------------------------
def build_panel(h: pd.DataFrame, unit: str, units: list, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    meses = [str(p) for p in pd.period_range(PERIOD_START, PERIOD_END, freq="M")]
    d = h[h[f"en_panel_{unit}"]].copy()
    d["modo_panel"] = d["modo_victima"].map(MODOS_PANEL).fillna("otros")
    agg = d.groupby([unit, "mes"]).agg(
        y_hechos=("id_siniestro", "size"), y_victimas=("n_victimas", "sum"), y_ksi=("ksi", "sum"),
        y_graves=("gravedad", lambda s: (s == "GRAVE").sum()), y_mortales=("gravedad", lambda s: (s == "MORTAL").sum()),
        n_posible_duplicado=("posible_duplicado", "sum"))
    comp = pd.crosstab([d[unit], d["mes"]], d["modo_panel"]).add_prefix("hechos_modo_")
    for c in [f"hechos_modo_{m}" for m in list(MODOS_PANEL.values()) + ["otros"]]:
        if c not in comp.columns:
            comp[c] = 0
    idx = pd.MultiIndex.from_product([units, meses], names=[unit, "mes"])
    p = agg.join(comp).reindex(idx, fill_value=0).reset_index()
    count_cols = [c for c in p.columns if c not in (unit, "mes")]
    p[count_cols] = p[count_cols].astype("int64")
    p["anio"] = p["mes"].str[:4].astype(int)
    p["mes_calendario"] = p["mes"].str[5:7].astype(int)
    p["anomalia_mes"] = flag_meses(p["mes"])
    p["particion"] = np.where(p["mes"] >= TEST_START, "test", "desarrollo")
    if extra is not None:
        p = p.merge(extra, on=unit, how="left")
    return p


# ---------------------------------------------------------------------------
# 6. Orquestación
# ---------------------------------------------------------------------------
def exclusion_log(h: pd.DataFrame, v: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sin_coord_ni_comuna = h[~h["en_panel_comuna"]]
    rows.append(pd.DataFrame({"tabla": "hechos", "id": sin_coord_ni_comuna["id_siniestro"],
                              "motivo": "sin coordenada válida ni comuna", "alcance": "excluido de paneles barrio y comuna"}))
    solo_comuna = h[h["en_panel_comuna"] & ~h["en_panel_barrio"]]
    rows.append(pd.DataFrame({"tabla": "hechos", "id": solo_comuna["id_siniestro"],
                              "motivo": "sin coordenada válida; comuna informada por la fuente",
                              "alcance": "excluido del panel barrio; incluido en panel comuna"}))
    sin_id = v[v["sin_id_hecho"]]
    rows.append(pd.DataFrame({"tabla": "victimas", "id": sin_id["id_victima_etl"].astype(str),
                              "motivo": "fila de víctima sin id_siniestro", "alcance": "no vinculable a un hecho"}))
    return pd.concat(rows, ignore_index=True)


def run(download: bool = False, accept_new_version: bool = False, raw: Path = RAW, out: Path = PROCESSED) -> dict:
    status = acquire(download, accept_new_version, raw)
    out.mkdir(parents=True, exist_ok=True)

    hechos_raw = read_source_csv(raw / "siniestros" / "siniestros_viales_hechos.csv")
    victimas_raw = read_source_csv(raw / "siniestros" / "siniestros_viales_victimas.csv")
    barrios = gpd.read_file(raw / "limites" / "barrios.geojson").to_crs(CRS_WGS84).rename(columns={"nombre": "barrio"})
    barrios["barrio"] = barrios["barrio"].astype("string")
    comunas = gpd.read_file(raw / "limites" / "comunas.geojson").to_crs(CRS_WGS84)

    h = assign_zones(clean_hechos(hechos_raw), barrios)
    v = clean_victimas(victimas_raw)

    # Atributos territoriales de la unidad (límites oficiales; no son infraestructura vial, ver D11)
    bar_attr = barrios.to_crs(CRS_CABA).assign(area_km2=lambda d: (d.area / 1e6).round(4),
                                                id_barrio=lambda d: d["id"].astype(int),
                                                comuna_barrio=lambda d: d["comuna"].astype(int))[["barrio", "id_barrio", "comuna_barrio", "area_km2"]]
    com_attr = comunas.to_crs(CRS_CABA).assign(comuna=lambda d: d["comuna"].astype(int),
                                                area_km2=lambda d: (d.area / 1e6).round(4))[["comuna", "area_km2"]]
    panel_b = build_panel(h, "barrio", sorted(barrios["barrio"].tolist()), pd.DataFrame(bar_attr))
    panel_c = build_panel(h, "comuna", list(range(1, 16)), pd.DataFrame(com_attr))
    excl = exclusion_log(h, v)

    # Escritura
    h.assign(fecha=h["fecha"].dt.strftime("%Y-%m-%d")).to_csv(out / "hechos_clean.csv", index=False)
    v.assign(fecha=v["fecha"].dt.strftime("%Y-%m-%d"),
             fecha_fallecimiento=v["fecha_fallecimiento"].dt.strftime("%Y-%m-%d")).to_csv(out / "victimas_clean.csv", index=False)
    panel_b.to_csv(out / "panel_barrio_mes.csv", index=False)
    panel_c.to_csv(out / "panel_comuna_mes.csv", index=False)
    excl.to_csv(out / "registro_exclusiones.csv", index=False)

    vict_por_hecho = v.dropna(subset=["id_siniestro"]).groupby("id_siniestro").size()
    qa = {
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuentes": status,
        "hechos": {"filas_fuente": len(hechos_raw), "filas_limpias": len(h), "id_unico": bool(h["id_siniestro"].is_unique),
                   "fechas_no_parseables": int(h["fecha"].isna().sum()), "sin_coordenada_valida": int(h["lat"].isna().sum()),
                   "metodo_asignacion": h["metodo_asignacion"].value_counts().to_dict(),
                   "en_panel_barrio": int(h["en_panel_barrio"].sum()), "en_panel_comuna": int(h["en_panel_comuna"].sum()),
                   "comuna_discordante": int(h["comuna_discordante"].sum()),
                   "posible_duplicado": int(h["posible_duplicado"].sum()), "grupos_duplicado": int(h["dup_grupo"].nunique()),
                   "discrepancia_plana_500m": int(h["discrepancia_plana"].sum())},
        "victimas": {"filas_fuente": len(victimas_raw), "filas_limpias": len(v), "sin_id_hecho": int(v["sin_id_hecho"].sum()),
                     "huerfanas": int((~v["id_siniestro"].dropna().isin(h["id_siniestro"])).sum()),
                     "conteo_hecho_igual_filas": bool((h.set_index("id_siniestro")["n_victimas"] == vict_por_hecho.reindex(h["id_siniestro"]).values).all())},
        "paneles": {"barrio_mes": {"filas": len(panel_b), "unidades": int(panel_b["barrio"].nunique()), "meses": int(panel_b["mes"].nunique()),
                                   "y_hechos_total": int(panel_b["y_hechos"].sum()),
                                   "y_hechos_desarrollo": int(panel_b.loc[panel_b["particion"] == "desarrollo", "y_hechos"].sum())},
                    "comuna_mes": {"filas": len(panel_c), "unidades": int(panel_c["comuna"].nunique()), "meses": int(panel_c["mes"].nunique()),
                                   "y_hechos_total": int(panel_c["y_hechos"].sum())}},
        "exclusiones_por_motivo": excl.groupby(["tabla", "motivo"]).size().rename("n").reset_index().to_dict(orient="records"),
    }
    (out / "qa_report.json").write_text(json.dumps(qa, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return qa


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--download", action="store_true", help="descarga los archivos faltantes desde el CDN oficial")
    ap.add_argument("--accept-new-version", action="store_true",
                    help="procesa aunque el hash difiera de la versión auditada (queda registrado en qa_report.json)")
    args = ap.parse_args(argv)
    qa = run(download=args.download, accept_new_version=args.accept_new_version)
    print(json.dumps({k: qa[k] for k in ("hechos", "victimas", "paneles")}, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    sys.exit(main())
