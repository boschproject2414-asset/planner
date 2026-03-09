import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api'

export function ProjectHome(){
  const {id}=useParams()
  const [data,setData]=useState({logs:[],risks:[],actions:[]})
  useEffect(()=>{apiFetch(`/v2/projects/${id}/home`).then(r=>r.json()).then(setData)},[id])
  const quick=async(path,method='POST',body)=>{
    const r=await apiFetch(path,{method,headers:{'Content-Type':'application/json'},body: body?JSON.stringify(body):undefined});
    alert(await r.text())
  }
  return <div>
    <h2>Project Home</h2>
    <button onClick={()=>quick('/v2/seed')}>Seed sample data</button>
    <button onClick={()=>quick(`/v2/projects/${id}/recalculate`)}>Recalculate Forecast</button>
    <button onClick={()=>quick(`/v2/projects/${id}/baselines`,'POST',{name:`Baseline-${Date.now()}`})}>Create Baseline</button>
    <h3>Latest Logs</h3><ul>{(data.logs||[]).map((x,i)=><li key={i}>{x}</li>)}</ul>
    <h3>Top Risks</h3><ul>{(data.risks||[]).map((x,i)=><li key={i}>{x}</li>)}</ul>
    <h3>Open Actions</h3><ul>{(data.actions||[]).map((x,i)=><li key={i}>{x}</li>)}</ul>
  </div>
}
