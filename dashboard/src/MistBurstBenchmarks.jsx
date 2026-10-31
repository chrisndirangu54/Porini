import React,{useState} from 'react';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const KEY=import.meta.env.VITE_API_KEY||'local-dev-key';
const fields=[['discharged_liters','Discharged (L)'],['deposited_liters','Deposited (L)'],['electrical_energy_wh','Electricity (Wh)'],['gas_recharge_energy_wh','Gas compression/recharge (Wh)'],['mass_kg','System mass (kg)'],['coverage_m2','Covered area (m²)'],['droplet_dv50_microns','Measured droplet Dv50 (µm; optional)'],['spray_uniformity_cv','Measured spray CV (optional)']];
export default function MistBurstBenchmarks(){
 const [data,setData]=useState({test_id:'bench-001',propulsion:'mechanical_pump',formulation:'MistBurst-W',discharged_liters:'',deposited_liters:'',electrical_energy_wh:'',gas_recharge_energy_wh:'',mass_kg:'',coverage_m2:'',droplet_dv50_microns:'',spray_uniformity_cv:''});
 const [results,setResults]=useState([]),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 function set(k,v){setData(d=>({...d,[k]:v}));}
 async function calculate(e){e.preventDefault();setBusy(true);setError('');
  try{const trial={...data};for(const [k] of fields)trial[k]=data[k]===''?null:Number(data[k]);
    const r=await fetch(API+'/fireshield/mistburst/benchmarks/compare',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':KEY},body:JSON.stringify({trials:[trial]})});
    if(!r.ok){const body=await r.json();throw Error(JSON.stringify(body.detail||'Validation failed'))}
    setResults(v=>[...(v),...(await r.json()).results]);
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 return <div className="panel"><h2>Atomization benchmark lab</h2><p className="muted">Enter measured bench-test results for pump, compressed air or nitrogen. No manufactured performance figures, physical pressure controls or chemical gas-generation tests.</p>
 <form onSubmit={calculate}><div className="actions" style={{flexWrap:'wrap',gap:12}}>
  <label>Test ID <input required value={data.test_id} onChange={e=>set('test_id',e.target.value)}/></label>
  <label>Propulsion <select value={data.propulsion} onChange={e=>set('propulsion',e.target.value)}>{['mechanical_pump','compressed_air','compressed_nitrogen'].map(x=><option key={x}>{x}</option>)}</select></label>
  <label>Formulation <select value={data.formulation} onChange={e=>set('formulation',e.target.value)}>{['MistBurst-W','MistBurst-G','MistBurst-R'].map(x=><option key={x}>{x}</option>)}</select></label>
  {fields.map(([key,label])=><label key={key}>{label} <input type="number" min="0" step="any" required={!['droplet_dv50_microns','spray_uniformity_cv'].includes(key)} value={data[key]} onChange={e=>set(key,e.target.value)}/></label>)}
 </div><button className="btn primary" disabled={busy} type="submit">Calculate measured metrics</button></form>
 {error&&<div className="error" role="alert">{error}</div>}
 {results.length>0&&<div className="tablewrap"><table><thead><tr><th>Test</th><th>Propulsion</th><th>Energy Wh/L</th><th>Deposited fraction</th><th>Coverage m²/L</th><th>Mass kg</th><th>Spray CV</th></tr></thead><tbody>{results.map((r,i)=><tr key={i}><td>{r.test_id}</td><td>{r.propulsion}</td><td>{r.energy_wh_per_liter}</td><td>{r.deposition_fraction}</td><td>{r.coverage_m2_per_liter}</td><td>{r.hardware_mass_kg}</td><td>{r.spray_uniformity_cv??'Not measured'}</td></tr>)}</tbody></table></div>}
 <p className="muted">Results are unverified inputs, not controlled head-to-head rankings. Compare only matching wind, nozzle, formulation, target and measurement protocols. Include energy consumed to recharge compressed-gas vessels.</p>
 </div>
}
