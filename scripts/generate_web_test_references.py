"""Referencias E2E independientes del frontend y del paquete JSON público."""
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.labels import top_k_labels
rpath=ROOT/'reports/tables/03_regression/predicciones_test.csv'
cpath=ROOT/'reports/tables/04_classification/predicciones_test.csv'
r=pd.read_csv(rpath);c=pd.read_csv(cpath)
config=json.loads((cpath.parent/'seleccion_congelada.json').read_text(encoding='utf8'))
regconfig=json.loads((rpath.parent/'seleccion_congelada.json').read_text(encoding='utf8'))
d=r.merge(c[['barrio','mes_objetivo',config['modelo_seleccionado']]],on=['barrio','mes_objetivo'],validate='one_to_one')
p=pd.read_csv(ROOT/'data/processed/panel_barrio_mes.csv')
ids=p[['barrio','id_barrio']].drop_duplicates().set_index('barrio').id_barrio.to_dict()
references=[]
for k in (5,10,15):
 for strategy,col in [('clasificador',config['modelo_seleccionado']),('historial_media12','y_ma12'),('regresion',regconfig['modelo_seleccionado']),('oraculo','y_target'),('historial_persistencia','y_lag1')]:
  selected=top_k_labels(d,'barrio','mes_objetivo',k,seed=20261111,ycol=col)
  for month,g in d.groupby('mes_objetivo'):
   chosen=g[selected.loc[g.index]]
   cutoff=chosen[col].min()
   references.append({'month':month,'k':k,'strategy':strategy,'ids':sorted(ids[n] for n in chosen.barrio),'captured':int(chosen.y_target.sum()),'total':int(g.y_target.sum()),'boundary_tie':bool((g[col]==cutoff).sum()>1)})
out=ROOT/'web/tests/fixtures/simulation.json';out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps({'inputs':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [rpath,cpath]},'references':references},indent=2)+'\n',encoding='utf8')
print('Referencias:',len(references),'empates:',sum(r['boundary_tie'] for r in references))
