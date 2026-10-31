import React,{useState} from 'react';
import {MapContainer,TileLayer,CircleMarker,Popup} from 'react-leaflet';
import {Radio,Camera,Flame,Activity,RefreshCw} from 'lucide-react';

export default function SentinelOperations({towers,incidents,fireAssessments,onRefresh}){
 const [selected,setSelected]=useState(null);
 const [filter,setFilter]=useState('all');
 const fireIds=new Set(fireAssessments.map(x=>x.incident_id));
 const relevant=incidents.filter(x=>fireIds.has(x.id)||x.source_ids.some(s=>s.startsWith('tower:')));
 const filtered=relevant.filter(x=>filter==='all'||(filter==='fire'?fireIds.has(x.id):x.source_ids.some(s=>s.startsWith('tower:'))));
 return <div className="sentinel">
  <div className="sectionheading"><h2>Sentinel Tower Operations</h2><button className="btn" onClick={onRefresh}><RefreshCw size={15}/> Refresh</button></div>
  <div className="notice">PROTOTYPE — Tower coordinates are approximate observation origins, not localized threat positions. Sensors and suppression hardware are not connected automatically. All detections require human review.</div>
  <div className="stats">
   <div className="metric"><span>REGISTERED TOWERS</span><b>{towers.length}</b><small>Registry entries</small></div>
   <div className="metric"><span>REPORTING ONLINE</span><b>{towers.filter(t=>t.health?.online===true).length}</b><small>Last reported; may be stale</small></div>
   <div className="metric"><span>TOWER INCIDENTS</span><b>{relevant.filter(x=>x.source_ids.some(s=>s.startsWith('tower:'))).length}</b><small>Unverified observations</small></div>
   <div className="metric"><span>FIRE ASSESSMENTS</span><b>{fireAssessments.length}</b><small>Advisory only</small></div>
  </div>
  <div className="sectionheading"><h2>Monitoring locations</h2><span>Field coverage has not been validated</span></div>
  <div className="mapbox"><MapContainer center={towers.length?[towers[0].latitude,towers[0].longitude]:[-1.15,37]} zoom={towers.length?10:8} className="map" scrollWheelZoom={false}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors"/>
  {towers.map(t=><CircleMarker key={t.id} center={[t.latitude,t.longitude]} radius={9} pathOptions={{color:'#64b6e9',fillOpacity:.8}}><Popup><strong>{t.name}</strong><br/>Tower height: {t.height_m}m<br/>Last status: {t.health?(t.health.online?'Reported online':'Reported offline'):'Unknown'}</Popup></CircleMarker>)}
  </MapContainer></div>
  <div className="sectionheading"><h2>Tower inventory</h2><span>No live stream or device commands</span></div>
  <div className="cards">{towers.length?towers.map(t=><div className="feature" key={t.id}><Radio size={25}/><h2>{t.name}</h2><p>{t.height_m}m tower · {t.power_type} · {t.connectivity_type}</p><small>Last report: {t.health?.observed_at?new Date(t.health.observed_at).toLocaleString():'No telemetry'}</small><p>Battery: {t.health?.battery_percent??'Unknown'}{t.health?.battery_percent!=null?'%':''}</p></div>):<div className="panel"><h2>No towers registered</h2><p>Register a prototype tower through the protected /towers API. Live hardware is not connected.</p></div>}</div>
  <div className="sectionheading"><h2>Multimodal alert review</h2><div className="actions"><button className="btn" onClick={()=>setFilter('all')}>All</button><button className="btn" onClick={()=>setFilter('fire')}><Flame size={14}/> Fire</button><button className="btn" onClick={()=>setFilter('tower')}><Camera size={14}/> Towers</button></div></div>
  <div className="tablewrap"><table><thead><tr><th>OBSERVATION</th><th>PRIORITY</th><th>CONFIDENCE</th><th>UNCERTAINTY</th><th>STATUS</th><th>REVIEW</th></tr></thead><tbody>{filtered.length?filtered.map(i=><tr key={i.id}><td><strong>{i.event_type.replaceAll('_',' ')}</strong><small>{i.synthetic?'Synthetic · ':''}{i.modalities.join(', ')}</small></td><td>{i.priority}</td><td>{Math.round(i.confidence*100)}%</td><td>±{i.uncertainty_m} m</td><td>{i.status}</td><td><button className="view" onClick={()=>setSelected(i)}>Inspect</button></td></tr>):<tr><td colSpan="6" className="empty">No matching detections.</td></tr>}</tbody></table></div>
  {selected&&<div className="panel"><h2>Review: {selected.event_type.replaceAll('_',' ')}</h2><p>Potential observation only. Review corroborating evidence with a trained ranger or authorized responder.</p><p>Modalities: {selected.modalities.join(', ')} · {selected.synthetic?'Synthetic sample':'Submitted field observation'}</p><p>Confidence is not proof of illegal conduct or a verified fire.</p><button className="btn" onClick={()=>setSelected(null)}>Close review</button></div>}
 </div>
}
