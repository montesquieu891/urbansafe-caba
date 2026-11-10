"""Controles de publicación: errores de fuentes deben impedir generar un paquete."""
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from scripts.export_web_data import INPUTS, ROOT, build, observation, sha


@pytest.fixture(scope='module')
def package():
    return build()


def test_public_package_reconciles(package):
    payload, manifest = package
    assert set(payload) == {'barrios.geojson', 'panel-mensual.json', 'priorizacion-2025.json',
                            'perfiles.json', 'cobertura.json', 'manifest.json'}
    for name, info in manifest['archivos'].items():
        assert hashlib.sha256(payload[name]).hexdigest() == info['sha256']
    panel = json.loads(payload['panel-mensual.json'])
    forecasts = json.loads(payload['priorizacion-2025.json'])
    assert len({(r['id_barrio'], r['mes']) for r in panel}) == 4032
    assert len({(r['id_barrio'], r['mes_objetivo']) for r in forecasts}) == 576
    assert sum(r['hechos'] == observation(0) for r in panel) == 45
    assert all(r['mes_observable'] < r['mes_objetivo'] for r in forecasts)
    assert manifest['validacion']['discrepancias_pendientes'] == []
    # Lista cerrada de campos públicos: ningún identificador o ubicación individual.
    assert set(panel[0]) == {'id_barrio', 'mes', 'hechos', 'area_km2', 'hechos_por_km2',
                             'composicion_modo', 'anomalia_mes'}
    assert set(forecasts[0]) == {'id_barrio', 'mes_objetivo', 'mes_observable', 'horizonte_meses',
                                 'gap_meses', 'puntajes', 'resultado_posterior', 'selecciones'}


def test_zero_and_missing_remain_distinct():
    assert observation(0) == {'valor': 0, 'estado': 'observado'}
    assert observation(None) == observation(float('nan')) == {'valor': None, 'estado': 'sin_datos'}
    for value in (-1, 0.5, float('inf')):
        with pytest.raises(ValueError):
            observation(value)


def test_reproducible_bytes(package):
    assert build()[0] == package[0]


@pytest.mark.parametrize('fault', ['duplicate_panel', 'missing_panel', 'unknown_name',
                                    'duplicate_geometry', 'changed_target', 'changed_coverage',
                                    'missing_observation'])
def test_inconsistent_inputs_rejected(tmp_path, fault):
    for relative in INPUTS.values():
        dest = tmp_path / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, dest)
    if fault == 'duplicate_geometry':
        dest = tmp_path / INPUTS['geometria']
        data = json.loads(dest.read_text(encoding='utf-8-sig'))
        data['features'][1] = data['features'][0]
        dest.write_text(json.dumps(data), encoding='utf8')
    else:
        key = {'unknown_name': 'perfiles', 'changed_target': 'clasificacion',
               'changed_coverage': 'cobertura'}.get(fault, 'panel')
        dest = tmp_path / INPUTS[key]
        data = pd.read_csv(dest)
        if fault == 'duplicate_panel':
            data.iloc[1] = data.iloc[0]
        elif fault == 'missing_panel':
            data = data.iloc[1:]
        elif fault == 'unknown_name':
            data.loc[0, 'barrio'] = 'No existe'
        elif fault == 'changed_target':
            data.loc[0, 'y_target'] += 1
        elif fault == 'changed_coverage':
            data.loc[data.conjunto.eq('TEST2025'), 'cobertura'] += .01
        else:
            data.loc[0, 'y_hechos'] = float('nan')
        data.to_csv(dest, index=False)
    with pytest.raises(ValueError):
        build(tmp_path)
    assert not (tmp_path / 'web').exists()


def test_provenance_hash_ignores_line_endings(tmp_path):
    # Una copia con CRLF (Windows) y otra con LF (clon nuevo) deben registrar la misma procedencia.
    lf, crlf, binary = tmp_path / 'a.py', tmp_path / 'b.py', tmp_path / 'c.bin'
    lf.write_bytes(b'x = 1\ny = 2\n')
    crlf.write_bytes(b'x = 1\r\ny = 2\r\n')
    binary.write_bytes(b'x = 1\r\ny = 2\r\n')
    assert sha(lf) == sha(crlf)
    assert sha(binary) != sha(lf)
