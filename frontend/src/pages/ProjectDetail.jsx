import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function ProjectDetail(){
  const {id}=useParams()
  const [tab,setTab]=useState('Plan')
  const [result,setResult]=useState('')

  const call=async(path,method='GET',body)=>{
    const r=await apiFetch(path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined})
    const data=await r.json();
    setResult(JSON.stringify(data,null,2))
  }

  return <div>
    <h2>Project {id}</h2>
    <div style={{display:'flex',gap:8,marginBottom:8}}>{['Plan','Do','Investigate','Materials'].map(t=><button key={t} onClick={()=>setTab(t)}>{t}</button>)}</div>
    {tab==='Plan' && <div>
      <button onClick={()=>call(`/projects/${id}/recalculate_schedule`,'POST')}>Recalculate Schedule</button>
      <button onClick={()=>call(`/projects/${id}/simulate_schedule_risk`,'POST')}>Simulate Risk</button>
      <button onClick={()=>call(`/projects/${id}/gates/G2/approve`,'POST',{actor_user_id:1,comment:'ready'})}>Approve G2</button>
    </div>}
    {tab==='Do' && <div>
      <button onClick={()=>call('/daily_logs','POST',{project_id:Number(id),trolley_id:1,log_date:new Date().toISOString().slice(0,10),shift:'day',created_by:1,summary:'Work done',blockers:'none',next_plan:'continue'})}>Create EOD</button>
      <button onClick={()=>call('/project_activities/1/start','POST',{actor_user_id:1,actual_start:new Date().toISOString().slice(0,10)})}>Start Activity #1</button>
    </div>}
    {tab==='Investigate' && <div>
      <button onClick={()=>call(`/projects/${id}/detect_anomalies`,'POST')}>Detect Anomalies</button>
    </div>}
    {tab==='Materials' && <div>
      <button onClick={()=>call(`/projects/${id}/material_risks`)}>Material Risks</button>
    </div>}
    <pre>{result}</pre>
  </div>
}
