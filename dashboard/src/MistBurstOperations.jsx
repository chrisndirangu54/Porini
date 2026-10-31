import React,{useEffect,useState} from 'react';

const API=import.meta.env.VITE_API_URL||'http://localhost:8000';
const KEY=import.meta.env.VITE_API_KEY||'local-dev-key';
const uses=[{value:'hotspot',label:'Active hotspot'},{value:'temporary_vegetation_protection',label:'Temporary fuel protection'},{value:'fireline',label:'Strategic fireline'}];

export default function MistBurstOperations({fireAssessments=[]}){
  const [catalog,setCatalog]=useState([]);
  const [selected,setSelected]=useState('MistBurst-W');
  const [application,setApplication]=useState('hotspot');
  const [checks,setChecks]=useState({product_approved:false,nozzle_compatible:false,environmental_clearance:false,operator_reviewed:false});
  const [weather,setWeather]=useState({wind:'moderate',thermal:'high',vegetation:'dense'});
  const [assessment,setAssessment]=useState(null);
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);
  useEffect(()=>{let alive=true;fetch(API+'/fireshield/mistburst/formulations',{headers:{'X-API-Key':KEY}})
   .then(r=>{if(!r.ok)throw Error('Unable to load MistBurst registry');return r.json()})
   .then(d=>{if(alive)setCatalog(d.formulations||[])})
   .catch(e=>{if(alive)setError(e.message)});return()=>{alive=false}},[]);
  const item=catalog.find(x=>x.id===selected);
  async function review(){
    setLoading(true);setError('');setAssessment(null);
    try{
      const r=await fetch(API+'/fireshield/mistburst/compatibility-review',{method:'POST',
        headers:{'X-API-Key':KEY,'Content-Type':'application/json'},
        body:JSON.stringify({formulation:selected,application,...checks})});
      if(!r.ok)throw Error('Compatibility review failed');
      setAssessment(await r.json());
    }catch(e){setError(e.message)}finally{setLoading(false)}
  }
  const constraints=[
    weather.wind==='strong'?'Strong wind: drift and incomplete coverage likely.':'Wind requires site-specific spray verification.',
    weather.thermal==='high'?'High thermal intensity: rapid evaporation and reignition risk.':'Thermal conditions need verified sensor measurements.',
    weather.vegetation==='dense'?'Dense vegetation: canopy shielding and poor spray penetration possible.':'Vegetation deposition remains unverified.'
  ];
  return <section className="panel" aria-label="MistBurst FireShield operations">
    <div className="eyebrow">FIRESHIELD / ADVISORY SIMULATION</div>
    <h2>MistBurst formulation operations</h2>
    <p className="muted">Compare certified water, water-enhancer gel and long-term retardant modes. No remote release, cartridge switching or flight commands exist. Every scenario below is illustrative—not a calibrated CFD prediction.</p>
    <div className="notice">SIMULATION ONLY · Physical actuation disabled · Qualified fire authority and ecological review required before field use.</div>
    {error&&<p role="alert" className="error">{error}</p>}
    <div className="cards">{catalog.map(f=><button key={f.id} type="button" onClick={()=>{setSelected(f.id);setAssessment(null)}} className="feature" style={{textAlign:'left',cursor:'pointer',outline:selected===f.id?'2px solid #6acba4':'none'}} aria-pressed={selected===f.id}>
      <strong>{f.id}</strong><h3>{f.name}</h3><p>{f.purpose}</p><small>Persistence: {f.persistence}</small>
    </button>)}</div>
    <div className="sectionheading"><h2>Compatibility and application</h2></div>
    <div className="actions" style={{flexWrap:'wrap',gap:12}}>
      <label>Application <select value={application} onChange={e=>{setApplication(e.target.value);setAssessment(null)}}>{uses.map(u=><option value={u.value} key={u.value}>{u.label}</option>)}</select></label>
      <label>Formulation <select value={selected} onChange={e=>{setSelected(e.target.value);setAssessment(null)}}>{catalog.map(f=><option key={f.id}>{f.id}</option>)}</select></label>
    </div>
    {item&&<p className="muted">Nozzle category: {item.nozzle}. Viscosity: {item.viscosity}. {item.notes.join(' ')}</p>}
    <p>These are operator-entered declarations, not independently verified certificates:</p>
    <div className="actions" style={{flexWrap:'wrap',gap:12}}>{Object.keys(checks).map(key=><label key={key}><input type="checkbox" checked={checks[key]} onChange={e=>{setChecks(v=>({...v,[key]:e.target.checked}));setAssessment(null)}}/> {key.replaceAll('_',' ')}</label>)}</div>
    <button className="btn primary" type="button" disabled={loading||!catalog.length} onClick={review}>{loading?'Reviewing…':'Review compatibility'}</button>
    {assessment&&<div className="notice" role="status"><strong>{assessment.advisory_ready?'Declared checks complete — no discharge authorized':'Review incomplete or application mismatch'}</strong><p>{assessment.issues.length?assessment.issues.join(' · '):'All self-declared conditions recorded. Independent validation still required.'}</p><small>Physical actuation enabled: NO · Authorization: NONE</small></div>}
    <div className="sectionheading"><h2>Illustrative field-condition scenario</h2></div>
    <div className="actions" style={{flexWrap:'wrap',gap:12}}>
      {[[ 'wind','Wind',['calm','moderate','strong'] ],['thermal','Thermal intensity',['low','moderate','high']],['vegetation','Fuel density',['sparse','moderate','dense']]].map(([key,label,choices])=>
       <label key={key}>{label} <select value={weather[key]} onChange={e=>setWeather(w=>({...w,[key]:e.target.value}))}>{choices.map(c=><option key={c}>{c}</option>)}</select></label>)}
    </div>
    <p className="muted">LiDAR/infrared observations: {fireAssessments.length} available FireShield assessment records. Weather inputs above are manual illustrative categories, not live sensor data.</p>
    <ul>{constraints.map((c,i)=><li key={i}>{c}</li>)}</ul>
    <p className="muted">Mode transitions require manufacturer-approved line flushing, inspection and verified compatibility. Gel and retardant are kept in separate cartridges; no arbitrary mixing is authorized.</p>
  </section>
}
