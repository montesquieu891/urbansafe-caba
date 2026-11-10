import { createFeatures, parseFeatures, type ExplorerState, type Forecast, type Profile, type Coverage } from './explorer-features';
// MapLibre (~1 MB) se carga de forma diferida: filtros, ficha y lista quedan operativos antes que el mapa.
import type { GeoJSONSource, Map as MapLibreMap } from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import type { FeatureCollection, Geometry } from 'geojson';

type Observation = { valor: number | null; estado: 'observado' | 'sin_datos' };
type Row = { id_barrio: number; mes: string; hechos: Observation; area_km2: number; hechos_por_km2: number | null; composicion_modo: Record<string, Observation>; anomalia_mes: string };
type Properties = { id_barrio: number; nombre: string; comuna: number; valor?: number | null; color?: string };
type Metric = 'hechos' | 'densidad';
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const monthInput = $<HTMLSelectElement>('month'), metricInput = $<HTMLSelectElement>('metric'), search = $<HTMLInputElement>('search');
const nf = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 1 });
const monthName = (m: string) => new Intl.DateTimeFormat('es-AR', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${m}-01T12:00:00Z`));
const esc = (s: string) => s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
const norm = (s: string) => s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
const colors = ['#d5e4ac','#a3c785','#6d9d64','#397449','#174a36'];
const breaks: Record<Metric, number[]> = { hechos: [10, 25, 50, 75], densidad: [5, 10, 20, 30] };
const unit = (metric: Metric) => metric === 'hechos' ? 'hechos registrados con víctimas' : 'hechos por km²';
const readValue = (row: Row | undefined, metric: Metric) => !row || row.hechos.estado !== 'observado' || row.hechos.valor === null ? null : metric === 'hechos' ? row.hechos.valor : row.hechos_por_km2;
const format = (v: number | null) => v === null ? 'Sin datos' : nf.format(v);
const fill = (value: number | null, metric: Metric) => value === null ? '#b2b9b9' : value === 0 ? '#fffef9' : colors[breaks[metric].filter(n => value >= n).length];
async function get<T>(name: string): Promise<T> { const response = await fetch(`/data/v1/${name}`); if (!response.ok) throw new Error(`No se pudo cargar ${name}`); return response.json(); }

async function start() {
 const [geo, panel, manifest, forecasts, profiles, coverage] = await Promise.all([get<FeatureCollection<Geometry,Properties>>('barrios.geojson'),get<Row[]>('panel-mensual.json'),get<{schema_version:string;data_version:string;fecha_corte:string}>('manifest.json'),get<Forecast[]>('priorizacion-2025.json'),get<Profile[]>('perfiles.json'),get<Coverage>('cobertura.json')]);
 if (manifest.schema_version !== '1.0.0' || geo.features.length !== 48 || panel.length !== 4032) throw new Error('El paquete no coincide con el contrato del atlas.');
 const months = [...new Set(panel.map(r => r.mes))].sort();
 const byKey = new Map(panel.map(r => [`${r.id_barrio}:${r.mes}`, r]));
 const neighborhoods = geo.features.map(f => f.properties);
 if (byKey.size !== panel.length) throw new Error('El panel tiene claves duplicadas.');
 let state: ExplorerState;
 const features = createFeatures(forecasts, profiles, coverage, ()=>state, update);
 let map: MapLibreMap | undefined;
 let ready = false;
 function fromURL() {
  const q = new URLSearchParams(location.search), rawMonth = q.get('mes');
  // Una fecha válida fuera de cobertura permanece explícitamente sin datos.
  const month = rawMonth && /^\d{4}-(0[1-9]|1[0-2])$/.test(rawMonth) && Number(rawMonth.slice(0,4)) >= 1900 && Number(rawMonth.slice(0,4)) <= 2100 ? rawMonth : '2025-12';
  const id = Number(q.get('barrio'));
  state = {month, id: neighborhoods.some(n => n.id_barrio === id) ? id : 21, metric: q.get('metrica') === 'densidad' ? 'densidad' : 'hechos', query: q.get('buscar') || '', ...parseFeatures(q)};
 }
 function url(push = true) {
  const q = new URLSearchParams({mes:state.month,barrio:String(state.id),metrica:state.metric});
  if (state.query) q.set('buscar',state.query);
  if(state.view!=='atlas')q.set('vista',state.view);
  q.set('estrategia',state.strategy);q.set('k',String(state.k));q.set('nivel',String(state.level));
  history[push ? 'pushState' : 'replaceState'](null,'',`${location.pathname}?${q}`);
 }
 function update(patch: Partial<typeof state>, push = true) { state = {...state,...patch}; url(push); render(); }
 function drawMap() {
  if (!map || !ready) return;
  const data: FeatureCollection<Geometry,Properties> = {...geo,features:geo.features.map(f => {const value=readValue(byKey.get(`${f.properties.id_barrio}:${state.month}`),state.metric);return {...f,properties:{...f.properties,valor:value,color:fill(value,state.metric),...features.mapStyle(f.properties.id_barrio)}};})};
  (map.getSource('barrios') as GeoJSONSource).setData(data);
  map.setFilter('selection',['==',['get','id_barrio'],state.id]);
  map.setLayoutProperty('strategy-outline','visibility',state.view==='simulador'?'visible':'none');
  map.setLayoutProperty('baseline-outline','visibility',state.view==='simulador'?'visible':'none');
  $('map').dataset.view=state.view;
  $('map').dataset.month=state.month; $('map').dataset.metric=state.metric; $('map').dataset.selected=String(state.id);
 }
 function render() {
  const row = byKey.get(`${state.id}:${state.month}`), value = readValue(row,state.metric);
  const neighborhood=neighborhoods.find(n => n.id_barrio === state.id)!;
  const options = months.includes(state.month) ? months : [...months,state.month].sort();
  monthInput.innerHTML=options.map(m=>`<option value="${m}">${monthName(m)}${months.includes(m)?'':' · sin datos'}</option>`).join('');
  monthInput.value=state.month;metricInput.value=state.metric;search.value=state.query;
  $('period-label').textContent=monthName(state.month);
  const rows=panel.filter(r=>r.mes===state.month), available=rows.filter(r=>r.hechos.estado==='observado' && r.hechos.valor!==null);
  $('total').textContent=available.length === 48 ? nf.format(available.reduce((n,r)=>n+r.hechos.valor!,0)) : 'Sin datos';
  $('neighborhood').textContent=neighborhood.nombre;
  const area = row?.area_km2 ?? panel.find(r=>r.id_barrio===state.id)?.area_km2;
  $('neighborhood-meta').textContent=`Comuna ${neighborhood.comuna} · ${nf.format(area!)} km² · ${monthName(state.month)}`;
  $('value').textContent=format(value); $('unit').textContent=unit(state.metric);
  $('observation-note').textContent=value===null?'Sin datos para este período.':value===0?'Cero hechos registrados en este mes.':row?.anomalia_mes==='registro'?'Mes con anomalía de registro: interpretar con cautela.':row?.anomalia_mes==='pandemia'?'Mes afectado por la pandemia: contexto de movilidad excepcional.':'Observación histórica · hechos asignados al barrio.';
  $('legend-title').textContent=state.metric==='hechos'?'Hechos registrados con víctimas':'Densidad · hechos por km²';
  const b=breaks[state.metric], ranges=[`> 0–< ${b[0]}`,...b.slice(0,-1).map((v,i)=>`${v}–< ${b[i+1]}`),`≥ ${b.at(-1)}`];
  $('legend-items').innerHTML=[['#fffef9','0 observado'],...colors.map((c,i)=>[c,ranges[i]]),['#b2b9b9','Sin datos']].map(([color,label])=>`<span><i class="swatch" style="background:${color}"></i>${esc(label)}</span>`).join('');
  const historyRows=months.map(m=>byKey.get(`${state.id}:${m}`));
  const vals=historyRows.map(r=>readValue(r,state.metric));
  const max=Math.max(1,...vals.filter((v):v is number=>v!==null));
  const x=(i:number)=>5+i*350/(months.length-1), y=(v:number)=>95-v/max*85;
  let path='', previous=false;
  vals.forEach((v,i)=>{if(v===null){previous=false;return;}path+=`${previous?'L':'M'}${x(i).toFixed(2)},${y(v).toFixed(2)} `;previous=true;});
  const index=months.indexOf(state.month);
  $('series').innerHTML=`<title>${esc(neighborhood.nombre)}: ${unit(state.metric)}, 2019–2025</title><line x1="5" x2="355" y1="95" y2="95" stroke="#b9c4b1"/><text x="5" y="9" fill="#586b65" font-size="9">${nf.format(max)}</text><path d="${path}" fill="none" stroke="#397449" stroke-width="2"/>${index>=0&&value!==null?`<line x1="${x(index)}" x2="${x(index)}" y1="12" y2="98" stroke="#a14a13" stroke-dasharray="3 3"/><circle cx="${x(index)}" cy="${y(value)}" r="4" fill="#a14a13"/>`:''}`;
  $('series').setAttribute('aria-label',`${neighborhood.nombre}: serie mensual en ${unit(state.metric)}. Mes seleccionado: ${state.month}, ${format(value)}.`);
  $('series-caption').textContent=`${neighborhood.nombre} · ${unit(state.metric)}`;
  $('series-values').innerHTML=months.map((m,i)=>`<tr${m===state.month?' aria-current="true"':''}><td>${m}</td><td>${format(vals[i])}</td></tr>`).join('');
  const labels:Record<string,string>={auto:'Automóvil',bicicleta:'Bicicleta',moto:'Moto',otros:'Otros',peaton:'Peatón',sd:'Sin informar',transporte_publico:'Transporte público'};
  $('modes').innerHTML=Object.entries(labels).map(([key,label])=>{const o=row?.composicion_modo[key];const n=o?.estado==='observado'?o.valor:null;return `<li><span>${label}</span><span class="bar" aria-hidden="true"><span style="width:${n!==null&&row?.hechos.valor?100*n/row.hechos.valor:0}%"></span></span><b>${format(n)}</b></li>`}).join('');
  renderList(); features.render(); drawMap();
  $('status').textContent=`${monthName(state.month)} · ${neighborhood.nombre} · ${format(value)} ${value!==null?unit(state.metric):''}`;
 }
 function renderList() {
  const visible=neighborhoods.filter(n=>norm(n.nombre).includes(norm(state.query))).map(n=>({...n,value:readValue(byKey.get(`${n.id_barrio}:${state.month}`),state.metric)})).sort((a,b)=>(b.value??-1)-(a.value??-1)||a.nombre.localeCompare(b.nombre,'es'));
  $('neighborhood-list').innerHTML=visible.map(n=>`<button type="button" data-id="${n.id_barrio}" aria-pressed="${n.id_barrio===state.id}"><span><span class="sr-only">Seleccionar </span>${esc(n.nombre)}</span> <b>${format(n.value)}</b></button>`).join('');
  $('ranking-info').textContent=`${visible.length} de 48 barrios · ${monthName(state.month)} · ${unit(state.metric)} · mayor a menor`;
  $('empty-search').hidden=visible.length>0;
 }
 fromURL();url(false);render();
 monthInput.disabled=metricInput.disabled=search.disabled=false;
 monthInput.addEventListener('change',()=>update({month:monthInput.value}));
 metricInput.addEventListener('change',()=>update({metric:metricInput.value as Metric}));
 search.addEventListener('input',()=>{state.query=search.value;url(false);renderList();features.decorateList();});
 $('neighborhood-list').addEventListener('click',event=>{const button=(event.target as HTMLElement).closest<HTMLButtonElement>('button[data-id]');if(button){const id=Number(button.dataset.id);update({id});document.querySelector<HTMLButtonElement>(`button[data-id="${id}"]`)?.focus({preventScroll:true});}});
 window.addEventListener('popstate',()=>{fromURL();render();});
 $('version').textContent=`Corte: ${manifest.fecha_corte} · Versión: ${manifest.data_version}`;
 try {
  $('map').dataset.loading='true';
  const [maplibregl] = await Promise.all([import('maplibre-gl'), import('maplibre-gl/dist/maplibre-gl.css')]);
  maplibregl.setWorkerUrl(workerUrl);
  delete $('map').dataset.loading;
  map=new maplibregl.Map({container:'map',style:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#e9ede3'}}]},bounds:[[-58.54,-34.71],[-58.32,-34.52]],fitBoundsOptions:{padding:25},attributionControl:false,dragRotate:false,pitchWithRotate:false});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}),'bottom-right');
  map.addControl(new maplibregl.AttributionControl({compact:true,customAttribution:'Buenos Aires Data · CC-BY-2.5-AR'}));
  map.on('load',()=>{map!.addSource('barrios',{type:'geojson',data:geo});map!.addLayer({id:'fills',type:'fill',source:'barrios',paint:{'fill-color':['coalesce',['get','color'],'#d5e4ac'],'fill-opacity':1}});map!.addLayer({id:'borders',type:'line',source:'barrios',paint:{'line-color':'#f4f3ed','line-width':1}});map!.addLayer({id:'strategy-outline',type:'line',source:'barrios',filter:['==',['get','strategy'],1],paint:{'line-color':'#3b76b1','line-width':3}});map!.addLayer({id:'baseline-outline',type:'line',source:'barrios',filter:['==',['get','baseline'],1],paint:{'line-color':'#a86e28','line-width':2,'line-dasharray':[2,2]}});map!.addLayer({id:'selection',type:'line',source:'barrios',paint:{'line-color':'#152e29','line-width':3}});ready=true;drawMap();});
  map.on('idle',()=>{if(ready){const ids=new Set(map!.queryRenderedFeatures({layers:['fills']}).map(f=>f.properties.id_barrio));$('map').dataset.rendered=String(ids.size);$('map').dataset.ready=String(ids.size===48);}});
  map.on('click','fills',event=>{const id=Number(event.features?.[0].properties.id_barrio);if(id)update({id});});
  map.on('mouseenter','fills',()=>{map!.getCanvas().style.cursor='pointer';});map.on('mouseleave','fills',()=>{map!.getCanvas().style.cursor='';});
  map.on('error',()=>{$('map-fallback').hidden=false;});
  $('reset-map').addEventListener('click',()=>map!.fitBounds([[-58.54,-34.71],[-58.32,-34.52]],{padding:25,duration:0}));
 } catch { delete $('map').dataset.loading;$('map-fallback').hidden=false;$<HTMLButtonElement>('reset-map').disabled=true; }
}
start().catch(error=>{$('status').textContent=`No pudimos cargar el atlas. ${error.message}. Recargá la página para volver a intentar.`; $('status').setAttribute('role','alert');});

