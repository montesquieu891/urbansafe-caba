export type View = 'atlas' | 'simulador' | 'perfiles';
export type Strategy = 'clasificador' | 'regresion' | 'historial_media12' | 'historial_persistencia' | 'oraculo';
export type ExplorerState = {month:string;id:number;metric:'hechos'|'densidad';query:string;view:View;strategy:Strategy;k:number;level:number};
export type Forecast = {id_barrio:number;mes_objetivo:string;mes_observable:string;horizonte_meses:number;gap_meses:number;puntajes:Record<string,number>;resultado_posterior:{hechos:{valor:number};puntaje_oraculo:number};selecciones:Record<Strategy,Record<string,boolean>>};
export type Profile = {id_barrio:number;grupo:number;k3:number;perfil_k3:string};
type Monthly = {mes_objetivo:string;estrategia:string;K:number;cobertura:number;hechos_cubiertos:number;hechos_totales:number;ids_seleccionados:number[]};
export type Coverage = {mensual:Monthly[];anual:{estrategia:string;K:number;media_coberturas_mensuales:number}[];diferencias_vs_historial:{estrategia:string;K:number;d_test:number;ic_bloques_inf:number;ic_bloques_sup:number}[];fraccion_ganancia_sobre_azar_K10:number};
const $ = <T extends HTMLElement>(id:string)=>document.getElementById(id) as T;
const labels:Record<Strategy,string>={clasificador:'Modelo de clasificación',regresion:'Modelo de regresión',historial_media12:'Historial del último año',historial_persistencia:'Solo el último mes',oraculo:'Oráculo'};
// Sujeto en minúscula para las frases de lectura («En marzo de 2025, el modelo de clasificación eligió…»).
const subjects:Record<Strategy,string>={clasificador:'el modelo de clasificación',regresion:'el modelo de regresión',historial_media12:'el historial del último año',historial_persistencia:'la regla del último mes',oraculo:'el oráculo'};
// Formato fijo «43,05 %» (espacio no separable), independiente de la versión de ICU del navegador.
const percent=(n:number)=>`${new Intl.NumberFormat('es-AR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n*100)} %`;
const points=(n:number)=>new Intl.NumberFormat('es-AR',{minimumFractionDigits:2,maximumFractionDigits:2,signDisplay:'exceptZero'}).format(n*100);
const monthLabel=(m:string)=>new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(`${m}-01T12:00:00Z`));
const number=(n:number)=>new Intl.NumberFormat('es-AR',{maximumFractionDigits:2}).format(n);
const percent1=(n:number)=>`${new Intl.NumberFormat('es-AR',{minimumFractionDigits:1,maximumFractionDigits:1}).format(n*100)} %`;
// Descripciones cualitativas del Paso 09, docs/clustering_report.md §5.
const profileDescriptions = {
 borde: {title:'Borde · General Paz y autopistas',color:'#bd884c',meaning:'Son los barrios con más del 20 % de sus hechos registrados en autopista o General Paz. En parte por eso, también tienen más automóvil y moto, y menos peatones y bicicletas que el interior.',question:'Pregunta para explorar: ¿qué papel tienen las vías rápidas y sus accesos en los hechos del barrio?'},
 interior: {title:'Interior',color:'#84a992',meaning:'Es el conjunto más amplio y heterogéneo. Las vías rápidas tienen menor peso en sus registros. Dentro de él hay diferencias de composición, pero no una frontera clara entre dos tipos.',question:'Pregunta para explorar: ¿qué modos y tipos de vía aparecen en los registros de cada barrio?'},
 residencial: {title:'Interior residencial',color:'#a4c7ab',meaning:'Dentro del interior, este subgrupo presenta relativamente más moto y bicicleta que el central-denso. El nombre resume su perfil; no es una clasificación oficial del uso del suelo.',question:'Pregunta para explorar: ¿dónde se concentran los hechos que involucran moto y bicicleta?'},
 central: {title:'Interior central-denso',color:'#6d8fb8',meaning:'Dentro del interior, este subgrupo presenta relativamente más peatones y transporte público que el residencial. No implica que cada barrio tenga el mismo patrón.',question:'Pregunta para explorar: ¿cómo se distribuyen los hechos vinculados a peatones y transporte público?'}
};
export function parseFeatures(q:URLSearchParams):Pick<ExplorerState,'view'|'strategy'|'k'|'level'> {
 const s=q.get('estrategia')||'';
 return {view:q.get('vista')==='simulador'?'simulador':q.get('vista')==='perfiles'?'perfiles':'atlas',strategy:Object.hasOwn(labels,s)?s as Strategy:'clasificador',k:[5,10,15].includes(Number(q.get('k')))?Number(q.get('k')):10,level:q.get('nivel')==='3'?3:2};
}
export function createFeatures(forecasts:Forecast[],profiles:Profile[],coverage:Coverage,getState:()=>ExplorerState,update:(patch:Partial<ExplorerState>,push?:boolean)=>void){
 const predictions=new Map(forecasts.map(r=>[`${r.id_barrio}:${r.mes_objetivo}`,r]));
 const groups=new Map(profiles.map(r=>[r.id_barrio,r]));
 const count=(test:(p:Profile)=>boolean)=>profiles.filter(test).length;
 // K=3 debe anidar el grupo de borde de K=2 (contrato del Paso 09).
 if(profiles.some(p=>(p.grupo===1)!==(p.k3===1)))throw new Error('Perfiles K=3 no anidados en K=2');
 if(predictions.size!==576||groups.size!==48)throw new Error('Claves inválidas en simulador o perfiles');
 const months=Array.from({length:12},(_,i)=>`2025-${String(i+1).padStart(2,'0')}`);
 // Comprobar las selecciones públicas contra su cobertura, sin resolver empates en JS.
 for(const month of months)for(const k of [5,10,15])for(const strategy of Object.keys(labels) as Strategy[]){
  const rows=forecasts.filter(r=>r.mes_objetivo===month),selected=rows.filter(r=>r.selecciones[strategy][String(k)]);
  const ref=coverage.mensual.find(r=>r.mes_objetivo===month&&r.K===k&&r.estrategia===strategy);
  const captured=selected.reduce((n,r)=>n+r.resultado_posterior.hechos.valor,0),total=rows.reduce((n,r)=>n+r.resultado_posterior.hechos.valor,0);
  if(rows.length!==48||selected.length!==k||!ref||captured!==ref.hechos_cubiertos||total!==ref.hechos_totales||Math.abs(captured/total-ref.cobertura)>1e-12||selected.some(r=>!ref.ids_seleccionados.includes(r.id_barrio)))throw new Error('Selecciones públicas no reconcilian');
 }
 const annualOf=(strategy:string,k:number)=>coverage.anual.find(r=>r.estrategia===strategy&&r.K===k)!.media_coberturas_mensuales;
 // Respuesta principal del simulador: 10 barrios, modelo de clasificación frente al historial (Paso 10).
 {
  const ci=coverage.diferencias_vs_historial.find(r=>r.K===10&&r.estrategia==='clasificador')!;
  const tie=ci.ic_bloques_inf<=0&&ci.ic_bloques_sup>=0;
  $('headline-answer').textContent=tie?'Prácticamente empatados':ci.ic_bloques_inf>0?'El modelo apuntó mejor':'El historial apuntó mejor';
  $('headline-detail').textContent=`Atendiendo 10 de los 48 barrios, el historial del último año reunió en promedio el ${percent1(annualOf('historial_media12',10))} de los siniestros con víctimas de cada mes, y el modelo de clasificación, el ${percent1(annualOf('clasificador',10))}. ${tie?'La diferencia es demasiado chica para afirmar que el modelo sea mejor.':ci.ic_bloques_inf>0?'El modelo reunió más siniestros, aunque es una sola temporada de prueba.':'El historial reunió más siniestros en 2025.'}${coverage.fraccion_ganancia_sobre_azar_K10>=0.85?' Mirar el último año ya consigue casi toda la ventaja posible frente a elegir barrios al azar.':''}`;
 }
 let timer:ReturnType<typeof setInterval>|undefined;
 function stop(){if(timer!==undefined)clearInterval(timer);timer=undefined;$('play-months').textContent='Reproducir meses';}
 function move(delta:number){const i=months.indexOf(getState().month);update({month:months[Math.max(0,Math.min(11,i+delta))]});}
 document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(button=>button.addEventListener('click',()=>{stop();const view=button.dataset.view as View;const s=getState();update({view,...(view==='simulador'&&!months.includes(s.month)?{month:'2025-01'}:{})});}));
 $<HTMLSelectElement>('strategy').addEventListener('change',e=>{stop();update({strategy:(e.target as HTMLSelectElement).value as Strategy});});
 $<HTMLSelectElement>('k').addEventListener('change',e=>{stop();update({k:Number((e.target as HTMLSelectElement).value)});});
 $<HTMLSelectElement>('profile-level').addEventListener('change',e=>update({level:Number((e.target as HTMLSelectElement).value)}));
 $('previous-month').addEventListener('click',()=>{stop();move(-1);});$('next-month').addEventListener('click',()=>{stop();move(1);});
 $('play-months').addEventListener('click',()=>{if(timer!==undefined){stop();return;}if(getState().month==='2025-12')update({month:'2025-01'});$('play-months').textContent='Pausar reproducción';timer=setInterval(()=>{const i=months.indexOf(getState().month);if(i<0||i>=11||getState().view!=='simulador'){stop();return;}update({month:months[i+1]},false);if(i+1===11)stop();},1800);});
 window.addEventListener('popstate',stop);window.addEventListener('pagehide',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});$('month').addEventListener('change',stop);
 const prediction=(id:number)=>predictions.get(`${id}:${getState().month}`);
 function flags(id:number){const s=getState(),r=prediction(id);return {strategy:!!r?.selecciones[s.strategy][String(s.k)],baseline:!!r?.selecciones.historial_media12[String(s.k)]};}
 function category(id:number){if(!prediction(id))return 'Sin datos';const f=flags(id);return f.strategy&&f.baseline?'Elegido por los dos':f.strategy?'Solo por el método':f.baseline?'Solo por el historial':'No elegido';}
 function profileLabel(id:number){const p=groups.get(id)!;return getState().level===2?(p.grupo===1?'Borde · General Paz/autopistas':'Interior'):p.perfil_k3;}
 function mapStyle(id:number){const s=getState();if(s.view==='atlas')return {};if(s.view==='perfiles'){const p=groups.get(id)!;return {color:s.level===2?(p.grupo===1?'#bd884c':'#84a992'):['#a4c7ab','#bd884c','#6d8fb8'][p.k3],strategy:0,baseline:0};}const f=flags(id);return {color:!prediction(id)?'#b2b9b9':f.strategy&&f.baseline?'#416d65':f.strategy?'#9dbbde':f.baseline?'#e1bf83':'#e3e7dd',strategy:Number(f.strategy),baseline:Number(f.baseline)};}
 function decorateList(){const s=getState();const list=$('neighborhood-list');for(const button of list.querySelectorAll<HTMLButtonElement>('button[data-id]')){button.querySelector('.badge')?.remove();delete button.dataset.selectedStrategy;delete button.dataset.selectedBaseline;if(s.view==='atlas')continue;const id=Number(button.dataset.id),badge=document.createElement('small');badge.className='badge';button.querySelector('span')!.append(' ');badge.textContent=s.view==='simulador'?category(id):profileLabel(id);button.querySelector('span')!.append(badge);if(s.view==='simulador'){const f=flags(id);button.dataset.selectedStrategy=String(f.strategy);button.dataset.selectedBaseline=String(f.baseline);}}
  if(s.view!=='atlas')$('ranking-info').textContent+=s.view==='simulador'?' · Siniestros registrados en el mes; quién eligió cada barrio se indica con texto y bordes.':' · Perfiles históricos fijos; valores del mes observado.';
 }
 function render(){const s=getState(),sim=s.view==='simulador',profile=s.view==='perfiles';$('simulation').hidden=!sim;$('profiles-panel').hidden=!profile;$('feature-detail').hidden=s.view==='atlas';document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===s.view)));$<HTMLSelectElement>('strategy').value=s.strategy;$<HTMLSelectElement>('k').value=String(s.k);$<HTMLSelectElement>('profile-level').value=String(s.level);
 // En el simulador el mes elegido es el objetivo del pronóstico; el observable se muestra en el corte.
 $('month-label').textContent=sim?'01 / MES A ANTICIPAR':'01 / PERÍODO';$('month').setAttribute('aria-label',sim?'Mes a anticipar':'Mes observado');
 $('sim-month-slot').hidden=!sim;
 const controls=$('controls');if(sim){$('sim-month-slot').append(controls);}else{$('atlas-controls-slot').after(controls);}
 $('metric-label').textContent=s.view==='atlas'?'02 / MIRADA':'02 / DATO DEL BARRIO';
 $('observed-caption').hidden=s.view==='atlas';$('map-reading').hidden=s.view==='atlas';
 $('map-reading').textContent=sim?'Cómo leer el mapa: verde, barrios elegidos por los dos métodos; azul, solo por el método elegido; ocre, solo por el historial; gris claro, no elegidos. El color indica quién eligió el barrio, no cuántos siniestros tuvo. Tocá un barrio para ver el detalle.':'Leé el mapa como grupos de semejanza. Un color identifica un perfil histórico; no significa mayor o menor peligrosidad. La cifra de la ficha pertenece al mes elegido, no es el criterio de agrupación.';
 $('view-title').innerHTML=sim?'Elegir dónde actuar.<br/><em>Y comprobarlo con 2025.</em>':profile?'Barrios diferentes.<br/><em>Patrones en común.</em>':'Una ciudad.<br/><em>48 historias viales.</em>';
 $('view-lead').textContent=sim?'Un simulador para decidir qué barrios priorizar cada mes y comprobar, con lo que realmente pasó, si la elección apuntó bien.':profile?'Explorá qué rasgos de los siniestros comparten los barrios, más allá de cuántos hechos registran.':'Explorá dónde se concentran los siniestros con víctimas. Siete años de registros, barrio por barrio.';
 $('view-context').textContent=sim?'PRUEBA CON DATOS DE 2025':profile?'SEMEJANZA HISTÓRICA':'OBSERVACIÓN HISTÓRICA';
 $('view-context-description').textContent=sim?'Mide dónde se concentraron los siniestros, no el efecto de una intervención.':profile?'Los grupos describen la composición de los registros, no niveles de riesgo.':'La carga registrada cuenta una parte de la historia. No mide el riesgo individual ni la exposición al tránsito.';
 $('map-heading').textContent=sim?'BARRIOS ELEGIDOS PARA ESE MES':profile?'PERFILES HISTÓRICOS':'CONCENTRACIÓN TERRITORIAL';
 $('legend-note').textContent=sim?'Contorno azul: método elegido · contorno ocre punteado: historial · contorno negro: barrio en foco':profile?'Grupos históricos fijos · contorno negro: barrio en foco':'Escala fija para todos los meses · contorno negro: barrio seleccionado';
 if(profile){
 $('profile-summary').textContent=s.level===2?`${count(p=>p.grupo===0)} barrios de interior · ${count(p=>p.grupo===1)} barrios de borde.`:`${count(p=>p.k3===0)} residenciales · ${count(p=>p.k3===2)} centrales-densos · ${count(p=>p.k3===1)} de borde.`;
 const cards=s.level===2?[['interior',count(p=>p.grupo===0)],['borde',count(p=>p.grupo===1)]]:[['residencial',count(p=>p.k3===0)],['central',count(p=>p.k3===2)],['borde',count(p=>p.k3===1)]];
 $('profile-cards').innerHTML=cards.map(([key,n])=>{const d=profileDescriptions[key as keyof typeof profileDescriptions];return `<article class="profile-card" style="--profile-color:${d.color}"><strong>${n} barrios · ${s.level===3&&key!=='borde'?'subgrupo exploratorio':'grupo principal'}</strong><h3>${d.title}</h3><p>${d.meaning}</p><p class="question">${d.question}</p></article>`;}).join('');
 $('profile-warning').textContent=s.level===2?'Qué sabemos con más confianza: el grupo de borde aparece de forma estable, pero coincide con una regla simple (más del 20 % de los hechos en autopista o General Paz). Es una división geográfica, no un tipo de barrio descubierto por el algoritmo. Núñez queda justo por debajo del corte.':'Lectura exploratoria: la separación entre los dos subgrupos del interior es débil. Sus rasgos se superponen; sirven para formular preguntas, no para asignar políticas automáticamente.';
 const p=groups.get(s.id)!;const d=p.grupo===1?profileDescriptions.borde:s.level===2?profileDescriptions.interior:p.k3===0?profileDescriptions.residencial:profileDescriptions.central;
 $('feature-detail').innerHTML=`<strong>Perfil histórico: ${profileLabel(s.id)}</strong><p class="profile-meaning">${d.meaning}</p><p>${d.question}</p><small>Rasgos del grupo, no una explicación causal de este barrio. ${s.level===3?'Subdivisión exploratoria; separación interior débil.':''}</small>`;
 }

 if(sim){
  const available=months.includes(s.month),r=prediction(s.id);
  $('simulation-results').hidden=!available;
  for(const id of ['previous-month','next-month','play-months'])$<HTMLButtonElement>(id).disabled=!available;
  $<HTMLButtonElement>('previous-month').disabled=!available||s.month==='2025-01';
  $<HTMLButtonElement>('next-month').disabled=!available||s.month==='2025-12';
  // Supuesto h=1/gap=0 del protocolo, dicho en lenguaje llano.
  $('cutoff').textContent=r?`Elección hecha con datos hasta ${monthLabel(r.mes_observable)} para anticipar ${monthLabel(s.month)}. Supone que esos datos estaban completos a tiempo; eso no está verificado.`:'El simulador cubre los meses de 2025. Elegí uno para ver la comparación.';
  const how:Record<Strategy,string>={
   clasificador:'Cómo elige: un modelo estima, para cada barrio, la probabilidad de quedar entre los 10 con más siniestros del mes y toma los de mayor probabilidad. No es la probabilidad de sufrir un siniestro.',
   regresion:'Cómo elige: un modelo estima cuántos siniestros tendrá cada barrio en el mes y toma los de mayor estimación.',
   historial_media12:'Cómo elige: promedia los siniestros de cada barrio en los 12 meses anteriores y toma los de mayor promedio. Es la referencia contra la que se compara todo.',
   historial_persistencia:'Cómo elige: toma los barrios con más siniestros en el último mes. Sirve para ver si una memoria corta funciona mejor que el promedio del año.',
   oraculo:'El oráculo hace trampa a propósito: elige después de conocer los resultados del mes. No sirve para planificar; muestra el máximo que se podía reunir.'};
  $('strategy-explanation').textContent=how[s.strategy];
  if(r){
   const score=s.strategy==='oraculo'?r.resultado_posterior.puntaje_oraculo:r.puntajes[s.strategy];
   const scoreText:Record<Strategy,string>={clasificador:`Probabilidad estimada de estar entre los 10 con más siniestros: ${percent(score)}`,regresion:`Siniestros estimados para el mes: ${number(score)}`,historial_media12:`Promedio de los 12 meses anteriores: ${number(score)} siniestros`,historial_persistencia:`Siniestros del mes anterior: ${number(score)}`,oraculo:`Siniestros del mes, ya conocidos por el oráculo: ${number(score)}`};
   $('feature-detail').innerHTML=`<strong>${category(s.id)}</strong><p>Método: ${labels[s.strategy]} · ${s.k} barrios a atender</p><p>${scoreText[s.strategy]}</p><p>Ese mes se registraron ${r.resultado_posterior.hechos.valor} siniestros con víctimas en el barrio.</p>`;
  }else $('feature-detail').textContent='Elegí un mes de 2025 para ver la comparación.';
  if(available){
   const monthly=(strategy:string)=>coverage.mensual.find(r=>r.mes_objetivo===s.month&&r.estrategia===strategy&&r.K===s.k)!;
   const a=monthly(s.strategy),b=monthly('historial_media12'),isBaseline=s.strategy==='historial_media12';
   const delta=annualOf(s.strategy,s.k)-annualOf('historial_media12',s.k);
   $('strategy-name').textContent=labels[s.strategy];
   $('monthly-coverage').textContent=percent(a.cobertura);
   $('monthly-counts').textContent=`${a.hechos_cubiertos} de ${a.hechos_totales} siniestros del mes ocurrieron en estos ${s.k} barrios`;
   $('baseline-coverage').textContent=percent(b.cobertura);
   $('baseline-counts').textContent=`${b.hechos_cubiertos} de ${b.hechos_totales} siniestros del mes ocurrieron en estos ${s.k} barrios`;
   $('annual-strategy').textContent=percent(annualOf(s.strategy,s.k));
   $('annual-baseline').textContent=percent(annualOf('historial_media12',s.k));
   $('annual-difference').textContent=`Diferencia con el historial: ${points(delta)} puntos.`;
   const ci=coverage.diferencias_vs_historial.find(r=>r.K===s.k&&r.estrategia===s.strategy);
   $('annual-ci').textContent=ci?`Margen de incertidumbre: entre ${points(ci.ic_bloques_inf)} y ${points(ci.ic_bloques_sup)} puntos. ${ci.ic_bloques_inf<=0&&ci.ic_bloques_sup>=0?'Como incluye el cero, no se puede afirmar que uno sea mejor.':ci.ic_bloques_sup<0?'Todo el margen queda por debajo de cero: en 2025 este método reunió menos siniestros que el historial.':'Todo el margen queda por encima de cero en 2025, aunque es una sola temporada de prueba.'}`:isBaseline?'Es el método de referencia.':'No hay un margen de incertidumbre publicado para este método.';
   const gap=Math.abs(a.hechos_cubiertos-b.hechos_cubiertos);
   const comparison=isBaseline?'Es el método de referencia.':`Con la misma cantidad de barrios, el historial reunió ${b.hechos_cubiertos}. ${a.hechos_cubiertos===b.hechos_cubiertos?'Ese mes, los dos eligieron igual de bien.':`Es decir, ${gap} ${gap===1?'siniestro':'siniestros'} ${a.hechos_cubiertos>b.hechos_cubiertos?'más':'menos'} que el historial.`}`;
   $('monthly-reading').textContent=`En ${monthLabel(s.month)}, ${subjects[s.strategy]} eligió ${s.k} de los 48 barrios. Allí ocurrió el ${percent(a.cobertura)} de los siniestros con víctimas del mes (${a.hechos_cubiertos} de ${a.hechos_totales}). ${comparison} Esto muestra dónde se concentraron los siniestros, no cuántos se habrían evitado.`;
   const common=a.ids_seleccionados.filter(id=>b.ids_seleccionados.includes(id)).length,differ=s.k-common;
   $('selection-summary').textContent=isBaseline?'':`Los dos métodos coinciden en ${common} de los ${s.k} barrios; cada uno eligió ${differ} ${differ===1?'barrio distinto':'barrios distintos'}.`;
   $('random-reference').textContent=`Referencias para ${s.k} barrios en 2025: elegirlos al azar reuniría en promedio el ${percent(annualOf('azar_esperado',s.k))} de los siniestros; el oráculo, el ${percent(annualOf('oraculo',s.k))}.`;
   $('gain-reference').textContent=`Para 10 barrios, el historial consigue aproximadamente el ${Math.round(100*coverage.fraccion_ganancia_sobre_azar_K10)} % de la ganancia sobre el azar alcanzable por el oráculo. No es el porcentaje de siniestros reunidos.`;
  }
 }
 if(s.view!=='atlas'){$('legend-title').textContent=sim?`Quién eligió cada barrio · ${s.k} de 48`:s.level===2?'Dos grupos principales':'Tres perfiles · exploratorio';const entries=sim?[['#416d65','Elegido por los dos'],['#9dbbde','Solo por el método'],['#e1bf83','Solo por el historial'],['#e3e7dd','No elegido'],['#b2b9b9','Sin datos']]:s.level===2?[['#84a992','Interior'],['#bd884c','Borde']]:[['#a4c7ab','Interior residencial'],['#6d8fb8','Interior central-denso'],['#bd884c','Borde']];$('legend-items').innerHTML=entries.map(([c,t])=>`<span><i class="swatch" style="background:${c}"></i>${t}</span>`).join('');}
 decorateList();
 }
 return {render,decorateList,mapStyle};
}
